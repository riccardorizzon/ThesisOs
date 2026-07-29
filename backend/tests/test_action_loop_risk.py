from app.runtime.action_loop.risk import RiskClass, classify, is_consequential


def test_builtin_read_tools():
    assert classify("search_corpus") is RiskClass.READ
    assert classify("get_selection_context") is RiskClass.READ


def test_unknown_tool_is_read_by_default():
    assert classify("unknown_tool") is RiskClass.READ


def test_consequential_excludes_read():
    assert is_consequential(RiskClass.READ) is False
    assert is_consequential(RiskClass.WRITE_LOCAL) is True
