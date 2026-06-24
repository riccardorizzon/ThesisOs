from app.schemas.run_context import RunContext
from app.schemas.graph_state import GraphState


def test_run_context_fields_and_disjoint_from_graphstate():
    rc = RunContext(conversation_id="c1", agent_run_id="r1", trace_id="t1", request_id="q1")
    assert rc.user_id is None
    assert rc.metadata == {}
    # execution fields must NOT leak into the domain GraphState contract
    assert "conversation_id" not in GraphState.model_fields
    assert "trace_id" not in GraphState.model_fields
