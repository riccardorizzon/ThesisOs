class ConversationNotFoundError(Exception):
    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        super().__init__(f"Conversation not found: {conversation_id}")
