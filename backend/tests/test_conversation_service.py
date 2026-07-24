import app.services.conversation.service as conversation_service
from app.db import models
from app.services.conversation.locks import ConversationLocks


async def test_lock_rejects_second_active_run():
    locks = ConversationLocks()
    assert locks.try_acquire("c1") is True
    assert locks.try_acquire("c1") is False   # already active -> caller returns 409
    locks.release("c1")
    assert locks.try_acquire("c1") is True


def test_conversation_title_from_message_collapses_and_truncates():
    message = "  Una   domanda\nmolto lunga " + ("sulla metodologia " * 10)

    title = conversation_service.conversation_title_from_message(message)

    assert "\n" not in title
    assert "  " not in title
    assert len(title) <= 72
    assert title.endswith("…")


def test_conversation_title_from_short_message():
    assert (
        conversation_service.conversation_title_from_message(
            "  Revisione del capitolo tre  "
        )
        == "Revisione del capitolo tre"
    )


def test_conversation_title_from_blank_message_keeps_placeholder():
    assert (
        conversation_service.conversation_title_from_message("   \n ")
        == "Nuova conversazione"
    )


async def test_list_backfills_legacy_placeholder_from_first_user_message(
    db_session,
):
    conversation = models.Conversation(
        project_id="thesis-agent",
        title="New Conversation",
    )
    db_session.add(conversation)
    await db_session.flush()
    db_session.add(
        models.Message(
            conversation_id=conversation.id,
            role="user",
            content="  Analisi   delle\nfonti primarie  ",
        )
    )
    await db_session.commit()

    result = await conversation_service.ConversationService().list_conversations(
        "thesis-agent"
    )

    item = next(entry for entry in result.items if entry.id == conversation.id)
    assert item.title == "Analisi delle fonti primarie"
