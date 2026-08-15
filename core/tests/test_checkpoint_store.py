"""Tests for CheckpointStore corruption handling.

Regression for silent data loss: a checkpoint file corrupted by a crash
mid-write, disk error, or manual edit used to be indistinguishable from
"no checkpoint ever existed" — load_checkpoint just logged and returned
None, so the orchestrator's resume path silently restarted the session
from scratch instead of surfacing the corruption. The corrupted file was
also left in place, so every subsequent resume attempt failed the same way.
"""

import pytest

from framework.schemas.checkpoint import Checkpoint
from framework.storage.checkpoint_store import CheckpointCorruptionError, CheckpointStore

pytestmark = pytest.mark.asyncio


def _make_checkpoint() -> Checkpoint:
    return Checkpoint.create(
        checkpoint_type="node_start",
        session_id="sess_1",
        run_id="run_1",
        current_node="n1",
        execution_path=["n1"],
        data_buffer={"key": "value"},
    )


async def test_load_checkpoint_returns_none_for_missing_file(tmp_path):
    """A checkpoint that was never written is a normal, expected None."""
    store = CheckpointStore(tmp_path)
    result = await store.load_checkpoint("cp_never_existed")
    assert result is None
    assert not store._corrupted_dir.exists()


async def test_load_checkpoint_raises_and_quarantines_corrupted_file(tmp_path):
    """A corrupted checkpoint must raise (not silently return None) and be
    moved out of checkpoints/ so it stops blocking every future load."""
    store = CheckpointStore(tmp_path)
    store.checkpoints_dir.mkdir(parents=True)
    checkpoint_path = store.checkpoints_dir / "cp_bad.json"
    checkpoint_path.write_text('{"checkpoint_id": "cp_bad", "state":', encoding="utf-8")

    with pytest.raises(CheckpointCorruptionError):
        await store.load_checkpoint("cp_bad")

    assert not checkpoint_path.exists()
    quarantined = list(store._corrupted_dir.glob("cp_bad_*.json"))
    assert len(quarantined) == 1


async def test_load_index_returns_none_and_quarantines_corrupted_index(tmp_path):
    """Unlike checkpoints, a corrupted index must NOT raise — internal
    self-healing (_update_index_add) treats a missing index as "start a
    fresh one", and that path must keep working even after corruption."""
    store = CheckpointStore(tmp_path)
    store.checkpoints_dir.mkdir(parents=True)
    store.index_path.write_text("not valid json{{{", encoding="utf-8")

    result = await store.load_index()

    assert result is None
    assert not store.index_path.exists()
    quarantined = list(store._corrupted_dir.glob("index_*.json"))
    assert len(quarantined) == 1


async def test_save_checkpoint_recovers_from_corrupted_index(tmp_path):
    """Saving a new checkpoint must still succeed after a prior index got
    corrupted — the corrupted index is quarantined, not fatal."""
    store = CheckpointStore(tmp_path)
    store.checkpoints_dir.mkdir(parents=True)
    store.index_path.write_text("{ corrupted", encoding="utf-8")

    checkpoint = _make_checkpoint()
    await store.save_checkpoint(checkpoint)

    index = await store.load_index()
    assert index is not None
    assert index.latest_checkpoint_id == checkpoint.checkpoint_id

    loaded = await store.load_checkpoint(checkpoint.checkpoint_id)
    assert loaded is not None
    assert loaded.checkpoint_id == checkpoint.checkpoint_id
