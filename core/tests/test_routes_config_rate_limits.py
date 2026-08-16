"""HTTP tests for PUT /api/config/rate-limits.

Regression coverage: the handler's own docstring says values are
"clamped to the hard ceiling", but it previously only appended a
warning and persisted the raw, uncapped value to configuration.json —
which SocialRateLimiter._resolve_limit() would then honor uncapped,
letting social-automation actions past the documented hard ceiling.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

import framework.config as config_mod
import framework.server.routes_config as routes_config_mod

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    cfg_file = tmp_path / "configuration.json"
    monkeypatch.setattr(config_mod, "HIVE_CONFIG_FILE", cfg_file)
    monkeypatch.setattr(routes_config_mod, "HIVE_CONFIG_FILE", cfg_file)
    return cfg_file


def _build_app() -> web.Application:
    app = web.Application()
    routes_config_mod.register_routes(app)
    return app


@pytest_asyncio.fixture
async def client():
    tc = TestClient(TestServer(_build_app()))
    await tc.start_server()
    yield tc
    await tc.close()


async def test_value_within_ceiling_is_persisted_unchanged(client: TestClient):
    resp = await client.put("/api/config/rate-limits", json={"limits": {"linkedin.invite.daily": 40}})
    body = await resp.json()
    assert resp.status == 200
    assert "warnings" not in body

    row = next(r for r in body["limits"] if r["platform"] == "linkedin" and r["action_type"] == "invite")
    assert row["daily"] == 40


async def test_value_above_ceiling_is_clamped_not_persisted_raw(client: TestClient, _isolated_config: Path):
    resp = await client.put("/api/config/rate-limits", json={"limits": {"linkedin.invite.daily": 999999}})
    body = await resp.json()
    assert resp.status == 200
    assert body.get("warnings"), "expected a warning about exceeding the hard max"

    row = next(r for r in body["limits"] if r["platform"] == "linkedin" and r["action_type"] == "invite")
    assert row["daily"] == 125  # daily_max ceiling — not 999999

    import json as _json

    on_disk = _json.loads(_isolated_config.read_text(encoding="utf-8"))
    assert on_disk["rate_limits"]["linkedin.invite.daily"] == 125, (
        "the clamped value must be what's persisted to configuration.json, "
        "not the raw uncapped input"
    )


async def test_value_below_one_is_floored(client: TestClient):
    resp = await client.put("/api/config/rate-limits", json={"limits": {"linkedin.invite.daily": 0}})
    body = await resp.json()
    assert resp.status == 200

    row = next(r for r in body["limits"] if r["platform"] == "linkedin" and r["action_type"] == "invite")
    assert row["daily"] == 1
