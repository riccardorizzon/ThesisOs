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


def test_registry_coerces_string_int_arguments():
    reg = ToolRegistry()

    def search(query: str, limit: int = 10) -> dict:
        """Search with a limit."""
        return {"query": query, "limit": limit, "limit_type": type(limit).__name__}

    reg.register(search)
    result = reg.execute("search", {"query": "craft", "limit": "5"})
    assert result["limit"] == 5
    assert result["limit_type"] == "int"
