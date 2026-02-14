"""Tests for circular dependency detection in Plan."""

import json

import pytest

from framework.graph.plan import (
    ActionSpec,
    ActionType,
    CircularDependencyError,
    Plan,
    PlanStep,
    StepStatus,
)


class TestCircularDependencyError:
    """Tests for CircularDependencyError exception class."""

    def test_circular_dependency_error_message(self):
        """CircularDependencyError has correct message format."""
        cycle = ["step_a", "step_b", "step_c", "step_a"]
        error = CircularDependencyError(cycle)
        assert "Circular dependency detected" in str(error)
        assert "step_a -> step_b -> step_c -> step_a" in str(error)

    def test_circular_dependency_error_has_cycle_attribute(self):
        """CircularDependencyError stores the cycle."""
        cycle = ["step_1", "step_2", "step_1"]
        error = CircularDependencyError(cycle)
        assert error.cycle == cycle

    def test_circular_dependency_error_is_value_error(self):
        """CircularDependencyError is a ValueError subclass."""
        cycle = ["step_a", "step_b", "step_a"]
        error = CircularDependencyError(cycle)
        assert isinstance(error, ValueError)


class TestValidateDependencies:
    """Tests for Plan.validate_dependencies() method."""

    def test_valid_plan_no_cycle(self):
        """Valid plan with no cycles passes validation."""
        steps = [
            PlanStep(
                id="step_1",
                description="First step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
            PlanStep(
                id="step_2",
                description="Second step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_1"],
            ),
            PlanStep(
                id="step_3",
                description="Third step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_2"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan",
            steps=steps,
        )
        # Should not raise
        plan.validate_dependencies()

    def test_direct_cycle_two_steps(self):
        """Direct cycle between two steps raises CircularDependencyError."""
        steps = [
            PlanStep(
                id="step_a",
                description="Step A",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_b"],
            ),
            PlanStep(
                id="step_b",
                description="Step B",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_a"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with cycle",
            steps=steps,
        )

        with pytest.raises(CircularDependencyError) as exc_info:
            plan.validate_dependencies()

        # Verify cycle contains both steps
        cycle = exc_info.value.cycle
        assert "step_a" in cycle
        assert "step_b" in cycle

    def test_indirect_cycle_three_steps(self):
        """Indirect/transitive cycle (A->B->C->A) raises CircularDependencyError."""
        steps = [
            PlanStep(
                id="step_a",
                description="Step A",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_c"],
            ),
            PlanStep(
                id="step_b",
                description="Step B",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_a"],
            ),
            PlanStep(
                id="step_c",
                description="Step C",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_b"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with transitive cycle",
            steps=steps,
        )

        with pytest.raises(CircularDependencyError) as exc_info:
            plan.validate_dependencies()

        # Verify cycle contains all three steps
        cycle = exc_info.value.cycle
        assert "step_a" in cycle
        assert "step_b" in cycle
        assert "step_c" in cycle

    def test_self_dependency(self):
        """Step depending on itself raises CircularDependencyError."""
        steps = [
            PlanStep(
                id="step_1",
                description="Self-dependent step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_1"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with self-dependency",
            steps=steps,
        )

        with pytest.raises(CircularDependencyError) as exc_info:
            plan.validate_dependencies()

        cycle = exc_info.value.cycle
        assert "step_1" in cycle

    def test_complex_dag_no_false_positive(self):
        """Complex DAG with diamond pattern doesn't trigger false positive."""
        # Diamond pattern: step_1 -> step_2, step_3; step_2, step_3 -> step_4
        steps = [
            PlanStep(
                id="step_1",
                description="Root",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
            PlanStep(
                id="step_2",
                description="Branch 1",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_1"],
            ),
            PlanStep(
                id="step_3",
                description="Branch 2",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_1"],
            ),
            PlanStep(
                id="step_4",
                description="Merge",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_2", "step_3"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with diamond pattern",
            steps=steps,
        )

        # Should not raise
        plan.validate_dependencies()

    def test_unknown_dependency_raises_value_error(self):
        """Step depending on non-existent step raises ValueError."""
        steps = [
            PlanStep(
                id="step_1",
                description="Step 1",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["nonexistent_step"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with unknown dependency",
            steps=steps,
        )

        with pytest.raises(ValueError) as exc_info:
            plan.validate_dependencies()

        assert "unknown step" in str(exc_info.value).lower()
        assert "nonexistent_step" in str(exc_info.value)

    def test_empty_plan_passes_validation(self):
        """Empty plan with no steps passes validation."""
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Empty plan",
            steps=[],
        )

        # Should not raise
        plan.validate_dependencies()

    def test_single_step_no_deps_passes_validation(self):
        """Single step with no dependencies passes validation."""
        steps = [
            PlanStep(
                id="step_1",
                description="Solo step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Single step plan",
            steps=steps,
        )

        # Should not raise
        plan.validate_dependencies()

    def test_multiple_independent_steps_pass_validation(self):
        """Multiple independent steps (no dependencies) pass validation."""
        steps = [
            PlanStep(
                id="step_1",
                description="Independent 1",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
            PlanStep(
                id="step_2",
                description="Independent 2",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
            PlanStep(
                id="step_3",
                description="Independent 3",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Multiple independent steps",
            steps=steps,
        )

        # Should not raise
        plan.validate_dependencies()

    def test_cycle_in_subset_of_steps(self):
        """Cycle in subset of steps is detected even with valid steps present."""
        steps = [
            PlanStep(
                id="step_1",
                description="Valid step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
            ),
            PlanStep(
                id="step_a",
                description="Cyclic A",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_b"],
            ),
            PlanStep(
                id="step_b",
                description="Cyclic B",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_a"],
            ),
            PlanStep(
                id="step_2",
                description="Another valid step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_1"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Mixed valid and cyclic steps",
            steps=steps,
        )

        with pytest.raises(CircularDependencyError):
            plan.validate_dependencies()


class TestFromJsonWithCycleDetection:
    """Tests that Plan.from_json() validates dependencies."""

    def test_from_json_valid_plan(self):
        """Valid plan JSON loads successfully."""
        plan_data = {
            "id": "test_plan",
            "goal_id": "test_goal",
            "description": "Test plan",
            "steps": [
                {
                    "id": "step_1",
                    "description": "First step",
                    "action": {"action_type": "function"},
                    "dependencies": [],
                },
                {
                    "id": "step_2",
                    "description": "Second step",
                    "action": {"action_type": "function"},
                    "dependencies": ["step_1"],
                },
            ],
        }

        # Should not raise
        plan = Plan.from_json(plan_data)
        assert plan.id == "test_plan"
        assert len(plan.steps) == 2

    def test_from_json_with_cycle_raises_error(self):
        """Plan JSON with circular dependencies raises CircularDependencyError."""
        plan_data = {
            "id": "test_plan",
            "goal_id": "test_goal",
            "description": "Test plan with cycle",
            "steps": [
                {
                    "id": "step_a",
                    "description": "Step A",
                    "action": {"action_type": "function"},
                    "dependencies": ["step_b"],
                },
                {
                    "id": "step_b",
                    "description": "Step B",
                    "action": {"action_type": "function"},
                    "dependencies": ["step_a"],
                },
            ],
        }

        with pytest.raises(CircularDependencyError):
            Plan.from_json(plan_data)

    def test_from_json_string_with_cycle_raises_error(self):
        """Plan JSON string with circular dependencies raises CircularDependencyError."""
        plan_data = {
            "id": "test_plan",
            "goal_id": "test_goal",
            "description": "Test plan with cycle",
            "steps": [
                {
                    "id": "step_a",
                    "description": "Step A",
                    "action": {"action_type": "function"},
                    "dependencies": ["step_b"],
                },
                {
                    "id": "step_b",
                    "description": "Step B",
                    "action": {"action_type": "function"},
                    "dependencies": ["step_a"],
                },
            ],
        }
        plan_json = json.dumps(plan_data)

        with pytest.raises(CircularDependencyError):
            Plan.from_json(plan_json)

    def test_from_json_with_unknown_dependency_raises_error(self):
        """Plan JSON with unknown dependency raises ValueError."""
        plan_data = {
            "id": "test_plan",
            "goal_id": "test_goal",
            "description": "Test plan with unknown dep",
            "steps": [
                {
                    "id": "step_1",
                    "description": "Step 1",
                    "action": {"action_type": "function"},
                    "dependencies": ["missing_step"],
                },
            ],
        }

        with pytest.raises(ValueError) as exc_info:
            Plan.from_json(plan_data)

        assert "unknown step" in str(exc_info.value).lower()


class TestGetReadyStepsWithCycles:
    """Tests for get_ready_steps() behavior when cycles exist."""

    def test_get_ready_steps_with_cycle_returns_empty(self):
        """When a cycle exists, no steps are ready (all pending on each other)."""
        # Create plan with cycle without going through from_json
        steps = [
            PlanStep(
                id="step_a",
                description="Step A",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_b"],
                status=StepStatus.PENDING,
            ),
            PlanStep(
                id="step_b",
                description="Step B",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_a"],
                status=StepStatus.PENDING,
            ),
        ]
        # Bypass from_json validation by using model_construct
        plan = Plan.model_construct(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with cycle",
            steps=steps,
            context={},
            revision=1,
        )

        # No steps should be ready
        ready = plan.get_ready_steps()
        assert len(ready) == 0

    def test_get_ready_steps_with_partial_cycle(self):
        """Steps outside cycle can still be ready."""
        steps = [
            PlanStep(
                id="step_1",
                description="Independent step",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=[],
                status=StepStatus.PENDING,
            ),
            PlanStep(
                id="step_a",
                description="Cyclic A",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_b"],
                status=StepStatus.PENDING,
            ),
            PlanStep(
                id="step_b",
                description="Cyclic B",
                action=ActionSpec(action_type=ActionType.FUNCTION),
                dependencies=["step_a"],
                status=StepStatus.PENDING,
            ),
        ]
        # Bypass validation using model_construct
        plan = Plan.model_construct(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan",
            steps=steps,
            context={},
            revision=1,
        )

        ready = plan.get_ready_steps()
        # Only step_1 should be ready
        assert len(ready) == 1
        assert ready[0].id == "step_1"


class TestExecutorIntegration:
    """Tests for executor integration with circular dependency detection."""

    @pytest.mark.asyncio
    async def test_executor_rejects_circular_dependencies(self, tmp_path):
        """FlexibleGraphExecutor validates plan and fails fast on circular deps."""
        from framework.graph.flexible_executor import FlexibleGraphExecutor
        from framework.graph.goal import Goal
        from framework.runtime.core import Runtime

        # Create plan with circular dependencies
        steps = [
            PlanStep(
                id="step_a",
                description="Step A",
                action=ActionSpec(action_type=ActionType.FUNCTION, function_name="dummy"),
                dependencies=["step_b"],
            ),
            PlanStep(
                id="step_b",
                description="Step B",
                action=ActionSpec(action_type=ActionType.FUNCTION, function_name="dummy"),
                dependencies=["step_a"],
            ),
        ]
        # Bypass from_json validation to test executor validation using model_construct
        plan = Plan.model_construct(
            id="test_plan",
            goal_id="test_goal",
            description="Test plan with cycle",
            steps=steps,
            context={},
            revision=1,
        )

        goal = Goal(
            id="test_goal",
            name="Test Goal",
            description="Test goal",
            success_criteria=[],
            constraints=[],
        )

        runtime = Runtime(storage_path=tmp_path / "runtime")
        executor = FlexibleGraphExecutor(runtime=runtime)

        # Execute should fail fast with CircularDependencyError
        result = await executor.execute_plan(plan, goal)

        # Should return FAILED status with error about circular dependency
        assert result.status.value == "failed"
        assert result.error is not None
        assert "circular dependency" in result.error.lower()

    @pytest.mark.asyncio
    async def test_executor_accepts_valid_plan(self, tmp_path):
        """FlexibleGraphExecutor accepts valid plan without circular deps."""
        from framework.graph.flexible_executor import FlexibleGraphExecutor
        from framework.graph.goal import Goal
        from framework.runtime.core import Runtime

        steps = [
            PlanStep(
                id="step_1",
                description="First step",
                action=ActionSpec(action_type=ActionType.FUNCTION, function_name="dummy"),
                dependencies=[],
            ),
            PlanStep(
                id="step_2",
                description="Second step",
                action=ActionSpec(action_type=ActionType.FUNCTION, function_name="dummy"),
                dependencies=["step_1"],
            ),
        ]
        plan = Plan(
            id="test_plan",
            goal_id="test_goal",
            description="Valid plan",
            steps=steps,
        )

        goal = Goal(
            id="test_goal",
            name="Test Goal",
            description="Test goal",
            success_criteria=[],
            constraints=[],
        )

        runtime = Runtime(storage_path=tmp_path / "runtime")
        executor = FlexibleGraphExecutor(runtime=runtime)

        # Register a dummy function
        def dummy_func():
            return {"result": "success"}

        executor.register_function("dummy", dummy_func)

        # Should not raise during validation
        # (Will complete or fail for other reasons, but not circular dependency)
        result = await executor.execute_plan(plan, goal)

        # Status should not be FAILED due to circular dependency
        # (Could be COMPLETED or other status depending on execution)
        if result.status.value == "failed":
            # If failed, error should not be about circular dependencies
            assert result.error is None or "circular dependency" not in result.error.lower()
