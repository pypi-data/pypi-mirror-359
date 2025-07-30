import pytest
from petal.src.core.utils import is_dag, topological_sort


# -------------------------------
# DAG VALIDATION TESTS
# -------------------------------

def test_is_dag_simple_linear():
    # A -> B -> C forms a simple valid DAG
    edges = {("A", "B"), ("B", "C")}
    assert is_dag(edges) is True


def test_is_dag_branch_and_merge():
    # A branches to B and C, which both lead to D
    # A -> B -> D
    # A -> C -> D
    edges = {("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")}
    assert is_dag(edges) is True


def test_is_dag_disconnected_components():
    # Two independent chains: A -> B and X -> Y -> Z
    edges = {("A", "B"), ("X", "Y"), ("Y", "Z")}
    assert is_dag(edges) is True


def test_is_dag_with_cycle():
    # A cycle exists: A -> B -> C -> A
    edges = {("A", "B"), ("B", "C"), ("C", "A")}
    assert is_dag(edges) is False


def test_is_dag_with_self_loop():
    # A self-loop: X -> X
    edges = {("X", "X")}
    assert is_dag(edges) is False


def test_is_dag_with_subgraph_cycle():
    # One component has a cycle: A -> B -> C -> A
    # D -> E is valid but doesn't negate the cycle
    edges = {("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")}
    assert is_dag(edges) is False


# -------------------------------
# TOPOLOGICAL SORT TESTS
# -------------------------------

def test_topological_sort_linear_chain():
    # A -> B -> C → should be ordered as A, B, C
    edges = {("A", "B"), ("B", "C")}
    assert topological_sort(edges) == ["A", "B", "C"]


def test_topological_sort_branch_and_merge():
    # A → B, A → C, B → D, C → D
    # Valid order: A must come before B and C; D must come last
    edges = {("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")}
    result = topological_sort(edges)
    assert result.index("A") < result.index("B")
    assert result.index("A") < result.index("C")
    assert result.index("B") < result.index("D")
    assert result.index("C") < result.index("D")


def test_topological_sort_disconnected_components():
    # Two independent DAGs: A → B and X → Y → Z
    edges = {("A", "B"), ("X", "Y"), ("Y", "Z")}
    result = topological_sort(edges)
    # Ensure A comes before B, and Y comes before Z
    assert result.index("A") < result.index("B")
    assert result.index("Y") < result.index("Z")
    assert result.index("X") < result.index("Y")


def test_topological_sort_multiple_valid_orders():
    # A → C, B → C — A and B are independent
    edges = {("A", "C"), ("B", "C")}
    result = topological_sort(edges)
    # Both A and B must come before C
    assert result.index("A") < result.index("C")
    assert result.index("B") < result.index("C")


def test_topological_sort_raises_on_cycle():
    # Cycle: A → B → C → A
    edges = {("A", "B"), ("B", "C"), ("C", "A")}
    with pytest.raises(ValueError, match="cycle"):
        topological_sort(edges)


def test_topological_sort_raises_on_self_loop():
    # Self-loop should raise an error
    edges = {("X", "X")}
    with pytest.raises(ValueError, match="cycle"):
        topological_sort(edges)


# -------------------------------
# Empty/degenerate cases
# -------------------------------

def test_topological_sort_empty():
    # Empty graph should return an empty order
    edges = set()
    assert topological_sort(edges) == []


def test_is_dag_empty():
    # An empty graph is trivially a DAG
    assert is_dag(set()) is True
