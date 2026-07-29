from app.runtime.action_loop.registry import ToolRegistry


def test_registry_execute():
    reg = ToolRegistry()

    def echo_query(query: str) -> dict:
        """Echo a query."""
        return {"query": query}

    reg.register(echo_query)
    assert reg.execute("echo_query", {"query": "x"}) == {"query": "x"}
    schemas = reg.schemas()
    assert schemas[0]["function"]["name"] == "echo_query"
