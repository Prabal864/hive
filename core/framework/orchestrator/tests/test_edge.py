"""Tests for ``GraphSpec.validate()`` — the pre-execution structural checks.

Focused on the ``entry_points`` mapping: named alternate entry points used by
pause/resume flows. Before this test, ``validate()`` checked the main entry
node, terminal nodes, and edge references, but never checked that an
``entry_points`` target actually names a node in the graph. A dangling entry
point would pass validation and only surface later, at resume time, via
``get_entry_point()`` handing back a node id that doesn't exist.
"""

from framework.orchestrator.edge import GraphSpec
from framework.orchestrator.node import NodeSpec


def _node(node_id: str) -> NodeSpec:
    return NodeSpec(id=node_id, name=node_id, description=f"node {node_id}")


def _graph(**overrides) -> GraphSpec:
    defaults = {
        "id": "g",
        "goal_id": "goal",
        "entry_node": "start",
        "nodes": [_node("start")],
        "terminal_nodes": ["start"],
    }
    defaults.update(overrides)
    return GraphSpec(**defaults)


def test_validate_passes_with_no_entry_points():
    # Preserve existing behavior: a graph with no named entry points at all
    # shouldn't trip the new check.
    result = _graph()
    assert result.validate()["errors"] == []


def test_validate_accepts_entry_point_targeting_real_node():
    graph = _graph(nodes=[_node("start"), _node("resume_node")], entry_points={"resume": "resume_node"})
    errors = graph.validate()["errors"]
    assert not any("Entry point" in e for e in errors)


def test_validate_flags_entry_point_targeting_missing_node():
    graph = _graph(entry_points={"resume": "missing_node"})
    errors = graph.validate()["errors"]
    assert "Entry point 'resume' references missing node 'missing_node'" in errors


def test_validate_flags_only_the_invalid_entry_point_among_several():
    graph = _graph(
        nodes=[_node("start"), _node("resume_node")],
        entry_points={"good": "resume_node", "bad": "missing_node"},
    )
    errors = graph.validate()["errors"]
    assert "Entry point 'bad' references missing node 'missing_node'" in errors
    assert not any("'good'" in e for e in errors)
