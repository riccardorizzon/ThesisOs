COMPANION_OPEN_MARKER = "__companion_open__"
COMPANION_OPEN_UTTERANCE = "Continuiamo da ieri"


def is_companion_open(text: str | None) -> bool:
    return bool(text and text.strip() == COMPANION_OPEN_MARKER)
