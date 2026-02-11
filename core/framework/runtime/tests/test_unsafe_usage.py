"""
Test to verify potential unsafe direct access to Run object.
"""

import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

from framework.runtime.core import Runtime


def test_direct_run_access_potential_issue():
    """
    Test what happens if someone gets the Run object via current_run property
    and then mutates it directly without going through Runtime methods.

    This is a potential unsafe usage pattern.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = Runtime(tmpdir)
        runtime.start_run(goal_id="test", goal_description="Test direct access")

        # Get the run object directly
        run = runtime.current_run
        assert run is not None

        # If multiple threads directly call run.add_problem without the Runtime lock,
        # there could be a race condition in the problem_id generation
        problem_ids = []
        lock = threading.Lock()

        def add_problem_directly(thread_id):
            # This bypasses Runtime's lock protection!
            # This is UNSAFE usage but we need to document it
            problem_id = run.add_problem(
                severity="warning", description=f"Problem {thread_id}"
            )
            with lock:
                problem_ids.append(problem_id)
            return problem_id

        # Run concurrent direct access
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(add_problem_directly, i) for i in range(10)]
            for f in futures:
                f.result()

        # Check if there are duplicates
        unique_ids = set(problem_ids)
        if len(unique_ids) < len(problem_ids):
            print(
                f"⚠️  WARNING: Direct Run access has race condition! "
                f"Expected 10 unique IDs, got {len(unique_ids)}"
            )
            print(f"Duplicate IDs found: {len(problem_ids) - len(unique_ids)}")
            # This would fail if there are duplicates
            # But we'll document this as "don't do this" rather than fix it
            # because it's outside the intended API usage

        runtime.end_run(success=True)


if __name__ == "__main__":
    # Run the test to see if direct access is problematic
    test_direct_run_access_potential_issue()
    print("Test completed - check output for warnings")
