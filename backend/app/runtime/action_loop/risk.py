from enum import Enum

BUILTIN_READ_TOOLS = frozenset({"search_corpus", "get_selection_context"})


class RiskClass(str, Enum):
    READ = "read"
    WRITE_LOCAL = "write_local"
    EXEC = "exec"
    EXTERNAL = "external"


def classify(tool_name: str) -> RiskClass:
    if tool_name in BUILTIN_READ_TOOLS:
        return RiskClass.READ
    return RiskClass.READ


def is_consequential(risk: RiskClass) -> bool:
    return risk is not RiskClass.READ
