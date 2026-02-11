"""
Tests for thread safety in Runtime class.

These tests verify that the Runtime class properly handles concurrent access
using threading.Lock to prevent race conditions in multi-threaded deployments.
"""

import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest

from framework.runtime.core import Runtime


@pytest.fixture
def runtime():
    """Create a Runtime instance with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Runtime(tmpdir)


def test_concurrent_start_and_end_run(runtime):
    """
    Test that multiple threads calling start_run and end_run concurrently
    do not raise exceptions or corrupt state.
    """
    def start_and_end_run(thread_id):
        run_id = runtime.start_run(
            goal_id=f"goal_{thread_id}",
            goal_description=f"Test goal {thread_id}"
        )
        # Verify run was started
        assert run_id.startswith("run_")
        # End the run
        runtime.end_run(success=True, narrative=f"Completed thread {thread_id}")
        return run_id

    # Run multiple threads concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(start_and_end_run, i) for i in range(10)]
        results = [f.result() for f in futures]

    # Verify all runs completed
    assert len(results) == 10
    assert all(r.startswith("run_") for r in results)


def test_concurrent_decide_unique_ids(runtime):
    """
    Test that concurrent calls to decide() generate unique decision IDs.
    This verifies the UUID-based ID generation prevents duplicate IDs.
    """
    # Start a run
    runtime.start_run(goal_id="test_goal", goal_description="Test concurrent decisions")

    decision_ids = []
    lock = threading.Lock()

    def make_decision(thread_id):
        decision_id = runtime.decide(
            intent=f"Decision from thread {thread_id}",
            options=[
                {"id": "option_a", "description": "Option A"},
                {"id": "option_b", "description": "Option B"},
            ],
            chosen="option_a",
            reasoning=f"Reason from thread {thread_id}"
        )
        with lock:
            decision_ids.append(decision_id)
        return decision_id

    # Run multiple threads concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_decision, i) for i in range(10)]
        results = [f.result() for f in futures]

    # Verify all decision IDs are unique
    assert len(decision_ids) == 10
    assert len(set(decision_ids)) == 10, "Decision IDs must be unique"
    assert all(d.startswith("dec_") for d in decision_ids)

    runtime.end_run(success=True)


def test_concurrent_decide_and_record_outcome(runtime):
    """
    Test that multiple threads calling decide() and record_outcome()
    concurrently do not corrupt the run's decision list.
    """
    runtime.start_run(goal_id="test_goal", goal_description="Test concurrent operations")

    def decide_and_record(thread_id):
        decision_id = runtime.decide(
            intent=f"Intent {thread_id}",
            options=[{"id": "opt1", "description": "Option 1"}],
            chosen="opt1",
            reasoning=f"Reasoning {thread_id}"
        )
        # Record outcome
        runtime.record_outcome(
            decision_id=decision_id,
            success=True,
            result=f"Result {thread_id}",
            summary=f"Summary {thread_id}"
        )
        return decision_id

    # Run multiple threads concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(decide_and_record, i) for i in range(10)]
        results = [f.result() for f in futures]

    # Verify all decisions were recorded
    assert len(results) == 10
    assert len(set(results)) == 10

    # Verify run has all decisions
    current_run = runtime.current_run
    assert current_run is not None
    assert len(current_run.decisions) == 10

    runtime.end_run(success=True)


def test_decide_without_run_logs_error(runtime):
    """
    Test that calling decide() without an active run logs an error (not warning)
    and returns an empty string.
    """
    with patch("framework.runtime.core.logger") as mock_logger:
        decision_id = runtime.decide(
            intent="Test intent",
            options=[{"id": "opt1", "description": "Option 1"}],
            chosen="opt1",
            reasoning="Test reasoning"
        )

        # Verify empty string returned
        assert decision_id == ""

        # Verify logger.error was called (not warning)
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "decide called but no run in progress" in call_args


def test_record_outcome_without_run_logs_error(runtime):
    """
    Test that calling record_outcome() without an active run logs an error
    (not warning).
    """
    with patch("framework.runtime.core.logger") as mock_logger:
        runtime.record_outcome(
            decision_id="dec_12345678",
            success=True,
            result="test result"
        )

        # Verify logger.error was called (not warning)
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "record_outcome called but no run in progress" in call_args
        assert "dec_12345678" in call_args


def test_report_problem_without_run_logs_error(runtime):
    """
    Test that calling report_problem() without an active run logs an error
    (not warning) and returns an empty string.
    """
    with patch("framework.runtime.core.logger") as mock_logger:
        problem_id = runtime.report_problem(
            severity="critical",
            description="Test problem"
        )

        # Verify empty string returned
        assert problem_id == ""

        # Verify logger.error was called (not warning)
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "report_problem called but no run in progress" in call_args
        assert "critical" in call_args
        assert "Test problem" in call_args


def test_set_node_thread_safety(runtime):
    """
    Test that multiple threads calling set_node() concurrently
    do not corrupt state.
    """
    runtime.start_run(goal_id="test_goal")

    def set_node(node_id):
        runtime.set_node(node_id)
        # Give other threads a chance to interleave
        import time
        time.sleep(0.001)

    # Run multiple threads setting different nodes
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(set_node, f"node_{i}") for i in range(10)]
        for f in futures:
            f.result()

    # The final node should be one of the values set
    # We can't predict which one due to concurrency, but it should be valid
    assert runtime._current_node.startswith("node_")

    runtime.end_run(success=True)


def test_current_run_property_thread_safety(runtime):
    """
    Test that the current_run property is thread-safe when accessed concurrently.
    """
    runtime.start_run(goal_id="test_goal")

    results = []
    lock = threading.Lock()

    def read_current_run(thread_id):
        run = runtime.current_run
        with lock:
            results.append(run is not None)
        return run

    # Read current_run from multiple threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(read_current_run, i) for i in range(10)]
        for f in futures:
            f.result()

    # All threads should have seen the run
    assert all(results)

    runtime.end_run(success=True)

    # After ending, all threads should see None
    results.clear()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(read_current_run, i) for i in range(10)]
        for f in futures:
            f.result()

    # All threads should see None after run ended
    assert not any(results)


def test_decide_and_execute_does_not_deadlock(runtime):
    """
    Test that decide_and_execute() does not hold the lock while executing,
    which would cause deadlocks if executor() calls back into runtime.
    """
    runtime.start_run(goal_id="test_goal")

    # Executor that tries to access runtime (should not deadlock)
    def executor():
        # This accesses the lock via current_run property
        run = runtime.current_run
        assert run is not None
        return "success"

    decision_id, result = runtime.decide_and_execute(
        intent="Test intent",
        options=[{"id": "opt1", "description": "Option 1"}],
        chosen="opt1",
        reasoning="Test reasoning",
        executor=executor
    )

    assert decision_id.startswith("dec_")
    assert result == "success"

    runtime.end_run(success=True)
