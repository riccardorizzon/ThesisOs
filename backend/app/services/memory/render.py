from app.schemas.memory import PromptContext


def render_prompt_context(ctx: PromptContext) -> str:
    """Render PromptContext to LLM wire text. Kept separate from load_prompt_context."""
    sections: list[str] = []

    if ctx.editable:
        body = "\n\n".join(_item_text(m) for m in ctx.editable)
        sections.append(f"[EDITABLE MEMORY]\n{body}")

    if ctx.user:
        body = "\n\n".join(_item_text(m) for m in ctx.user)
        sections.append(f"[USER PREFERENCES]\n{body}")

    if ctx.thesis:
        body = "\n\n".join(_item_text(m) for m in ctx.thesis)
        sections.append(f"[THESIS CONTEXT]\n{body}")

    if not sections:
        return ""

    header = "You are assisting with a thesis. The following persistent memory applies:\n\n"
    return header + "\n\n".join(sections)


def _item_text(item) -> str:
    if item.title:
        return f"## {item.title}\n{item.content}"
    return item.content
