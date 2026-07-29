import pytest


@pytest.mark.asyncio
async def test_litellm_client_acompletion_with_tools(monkeypatch):
    class FakeMsg:
        content = None
        tool_calls = [{"id": "t1", "function": {"name": "search_corpus", "arguments": '{"query":"x"}'}}]

    class FakeChoice:
        message = FakeMsg()
        finish_reason = "tool_calls"

    class FakeResp:
        choices = [FakeChoice()]

    async def fake_acompletion(**kwargs):
        assert "tools" in kwargs
        return FakeResp()

    monkeypatch.setattr("app.llm.litellm_client.litellm.acompletion", fake_acompletion)
    from app.llm.litellm_client import LiteLLMClient

    client = LiteLLMClient(project="p", location="europe-west1", model="gemini-2.0-flash")
    turn = await client.acompletion_with_tools(
        [{"role": "user", "content": "hi"}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "search_corpus",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
    )
    assert turn.tool_calls[0].name == "search_corpus"
