"""
Here is the main business logic
"""

from recommender import LlmRecomender
from processor import DocumentProcessor



class RecommendationApp:
    """
    App definition
    """
    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        document_processor : DocumentProcessor,
        llm_recomender: LlmRecomender
    ):
        self.document_processor = document_processor
        self.llm_recomender = llm_recomender

    def handle_user_query(self, user_query: str):
        """
        some
        """
        documents_and_filters = self.document_processor.process_user_query(user_query)
        response = (
            self
            .llm_recomender
            .recomend(user_query, documents_and_filters["ranked_documents"])
        )

        documents_and_filters["ranked_documents"] = (
            documents_and_filters["ranked_documents"].to_html()
        )

        return documents_and_filters | response
