"""
Stress tests for Runtime thread safety.

These tests use higher concurrency and more aggressive timing
to expose any remaining race conditions.
"""

import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from framework.runtime.core import Runtime


@pytest.fixture
def runtime():
    """Create a Runtime instance with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Runtime(tmpdir)


def test_stress_concurrent_decisions_high_volume(runtime):
    """
    Stress test with high volume of concurrent decisions.
    This should expose any remaining race conditions in decision recording.
    """
    runtime.start_run(goal_id="stress_test", goal_description="High volume stress test")

    num_threads = 50
    decisions_per_thread = 20
    all_decision_ids = []
    lock = threading.Lock()

    def make_many_decisions(thread_id):
        thread_decisions = []
        for i in range(decisions_per_thread):
            decision_id = runtime.decide(
                intent=f"Thread {thread_id} decision {i}",
                options=[
                    {"id": "opt1", "description": "Option 1"},
                    {"id": "opt2", "description": "Option 2"},
                ],
                chosen="opt1",
                reasoning=f"Reason {i}",
            )
            thread_decisions.append(decision_id)
            # Minimal delay to increase contention
            time.sleep(0.0001)

        with lock:
            all_decision_ids.extend(thread_decisions)
        return thread_decisions

    # Run high volume concurrent decisions
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(make_many_decisions, i) for i in range(num_threads)]
        for f in futures:
            f.result()

    # Verify all decision IDs are unique
    expected_total = num_threads * decisions_per_thread
    assert len(all_decision_ids) == expected_total, f"Expected {expected_total} decisions"
    assert len(set(all_decision_ids)) == expected_total, (
        f"Found duplicate IDs: {expected_total - len(set(all_decision_ids))} duplicates"
    )

    # Verify all are in the run
    current_run = runtime.current_run
    assert current_run is not None
    assert len(current_run.decisions) == expected_total

    runtime.end_run(success=True)


def test_stress_concurrent_problems_high_volume(runtime):
    """
    Stress test problem recording with high concurrency.
    This verifies that problem_id generation doesn't have race conditions.
    """
    runtime.start_run(goal_id="stress_test", goal_description="Problem stress test")

    num_threads = 30
    problems_per_thread = 10
    all_problem_ids = []
    lock = threading.Lock()

    def report_many_problems(thread_id):
        thread_problems = []
        for i in range(problems_per_thread):
            problem_id = runtime.report_problem(
                severity="warning",
                description=f"Problem from thread {thread_id}, iteration {i}",
            )
            thread_problems.append(problem_id)
            # Minimal delay to increase contention
            time.sleep(0.0001)

        with lock:
            all_problem_ids.extend(thread_problems)
        return thread_problems

    # Run high volume concurrent problem reporting
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(report_many_problems, i) for i in range(num_threads)]
        for f in futures:
            f.result()

    # Verify all problem IDs are unique
    expected_total = num_threads * problems_per_thread
    assert len(all_problem_ids) == expected_total
    assert len(set(all_problem_ids)) == expected_total, (
        f"Found duplicate problem IDs: {expected_total - len(set(all_problem_ids))} duplicates"
    )

    # Verify all are in the run
    current_run = runtime.current_run
    assert current_run is not None
    assert len(current_run.problems) == expected_total

    runtime.end_run(success=True)


def test_stress_mixed_operations(runtime):
    """
    Stress test with mixed operations: decisions, outcomes, problems.
    This simulates realistic multi-threaded usage.
    """
    runtime.start_run(goal_id="stress_test", goal_description="Mixed operations stress test")

    num_threads = 20
    operations_per_thread = 15

    def mixed_operations(thread_id):
        for i in range(operations_per_thread):
            # Make a decision
            decision_id = runtime.decide(
                intent=f"Mixed op {thread_id}-{i}",
                options=[{"id": "opt", "description": "Option"}],
                chosen="opt",
                reasoning="Reasoning",
            )

            # Record outcome
            runtime.record_outcome(decision_id=decision_id, success=True, result=f"Result {i}")

            # Sometimes report a problem
            if i % 3 == 0:
                runtime.report_problem(severity="minor", description=f"Minor issue {i}")

            # Minimal delay
            time.sleep(0.0001)

    # Run mixed operations concurrently
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(mixed_operations, i) for i in range(num_threads)]
        for f in futures:
            f.result()

    # Verify run integrity
    current_run = runtime.current_run
    assert current_run is not None
    assert len(current_run.decisions) == num_threads * operations_per_thread
    assert current_run.metrics.total_decisions == num_threads * operations_per_thread
    assert current_run.metrics.successful_decisions == num_threads * operations_per_thread

    runtime.end_run(success=True)


def test_stress_rapid_start_end_cycles(runtime):
    """
    Stress test rapid start/end cycles to verify no state corruption.
    """
    num_cycles = 100

    def run_cycle(i):
        run_id = runtime.start_run(goal_id=f"cycle_{i}", goal_description="Rapid cycle")
        # Quick decision
        decision_id = runtime.decide(
            intent="Quick decision",
            options=[{"id": "opt", "description": "Option"}],
            chosen="opt",
            reasoning="Quick",
        )
        runtime.record_outcome(decision_id=decision_id, success=True)
        runtime.end_run(success=True)
        return run_id

    # Run cycles sequentially (can't have multiple active runs in same Runtime)
    for i in range(num_cycles):
        run_cycle(i)

    # Verify runtime is clean
    assert runtime.current_run is None


def test_stress_concurrent_node_switching(runtime):
    """
    Stress test concurrent node switching to verify set_node thread safety.
    """
    runtime.start_run(goal_id="stress_test", goal_description="Node switching stress test")

    num_threads = 30
    switches_per_thread = 20

    def switch_nodes(thread_id):
        for i in range(switches_per_thread):
            runtime.set_node(f"node_{thread_id}_{i}")
            time.sleep(0.0001)

    # Run concurrent node switches
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(switch_nodes, i) for i in range(num_threads)]
        for f in futures:
            f.result()

    # Current node should be one of the values set (we can't predict which due to race)
    assert runtime._current_node.startswith("node_")

    runtime.end_run(success=True)


def test_stress_outcome_recording_ordering(runtime):
    """
    Verify that outcomes are correctly associated with decisions
    even under high concurrency.
    """
    runtime.start_run(goal_id="stress_test", goal_description="Outcome ordering test")

    num_threads = 20

    def decide_and_record(thread_id):
        # Each thread makes a decision and records its outcome
        decision_id = runtime.decide(
            intent=f"Decision {thread_id}",
            options=[{"id": "opt", "description": "Option"}],
            chosen="opt",
            reasoning=f"Reasoning {thread_id}",
        )

        # Add some delay to increase race window
        time.sleep(0.001)

        # Record outcome with thread-specific result
        runtime.record_outcome(
            decision_id=decision_id, success=True, result=f"Result from thread {thread_id}"
        )

        return (decision_id, thread_id)

    # Run concurrent decide+record operations
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(decide_and_record, i) for i in range(num_threads)]
        for f in futures:
            f.result()

    # Verify all decisions have their correct outcomes
    current_run = runtime.current_run
    assert current_run is not None
    assert len(current_run.decisions) == num_threads

    # Check each decision has an outcome
    for decision in current_run.decisions:
        assert decision.outcome is not None
        assert decision.outcome.success is True

    runtime.end_run(success=True)
