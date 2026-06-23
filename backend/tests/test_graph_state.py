from app.schemas.graph_state import GraphState


def test_graph_state_defaults():
    s = GraphState(messages=[])
    assert s.plan is None
    assert s.retrieved_context == []
    assert s.errors == []


def test_graph_state_roundtrip():
    s = GraphState(messages=[], route="writer", draft="hello")
    assert GraphState.model_validate_json(s.model_dump_json()).route == "writer"
