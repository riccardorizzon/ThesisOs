"""RetrievalService domain errors (M4)."""


class RetrievalServiceError(Exception):
    """Base retrieval error."""


class DocumentNotIndexedError(RetrievalServiceError):
    def __init__(self, document_id: str):
        super().__init__(f"document {document_id} is not indexed")
        self.document_id = document_id


class EmbedFailedError(RetrievalServiceError):
    def __init__(self, message: str):
        super().__init__(message)


class SearchError(RetrievalServiceError):
    pass
