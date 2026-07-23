class ConversationNotFoundError(Exception):
    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        super().__init__(f"Conversation not found: {conversation_id}")


class ConversationProjectMismatchError(Exception):
    def __init__(
        self,
        conversation_id: str,
        *,
        expected_project_id: str,
        requested_project_id: str,
    ) -> None:
        self.conversation_id = conversation_id
        self.expected_project_id = expected_project_id
        self.requested_project_id = requested_project_id
        super().__init__(
            f"Conversation {conversation_id} belongs to {expected_project_id}, "
            f"not {requested_project_id}"
        )
