"""
This module contains the database definitions
"""

import os
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import VectorStore
from models import Documents

POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE") or ''
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or ''
POSTGRES_USERNAME = os.environ.get('POSTGRES_USERNAME') or ''
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or ''
collection_name = os.environ.get("EMBEDING_COLLECTION_NAME") or 'vector_collection'

class DatabaseNotInitializedError(Exception):
    """Exception raised when attempting to use the database before it has been initialized."""
    def __init__(self, message="Please initialize the database before extracting documents."):
        self.message = message
        super().__init__(self.message)

class Db:
    """
    some docstring
    """
    def __init__(self):
        self.db: VectorStore | None = None

    def __str__(self) -> str:
        return "database"

    def init_db(self) -> None:
        """
        some
        """
        print("initializing database")

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=OPENAI_API_KEY # type: ignore
        )

        # This should be load as env variable "connection_string" or similar
        # pylint: disable=line-too-long
        connection = f"postgresql+psycopg://postgres:{POSTGRES_PASSWORD}@postgresql/{POSTGRES_DATABASE}"
        print(connection)

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection,
            use_jsonb=True,
        )

        self.db = vector_store


    def close_db(self) -> None:
        """
        some
        """
        print("closing database")
        self.db = None

    def extract_documents(self,user_query: str, filter_condition: dict) -> Documents:
        """
        some
        """
        if not self.db:
            raise DatabaseNotInitializedError()

        print(f"extracting docs using filter {filter_condition}")
        search_results = self.db.similarity_search(user_query, k = 3, filter= filter_condition)
        return search_results
