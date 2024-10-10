"""
This module contains the database definitions
"""

import pandas as pd
from models import Documents
from filter_extractor import FilterExtractor
from database import Db

class MockDf():
    """
    Mocks a dataframe object
    This should me moved to a models file
    """
    def __init__(self, message):
        self.message = message

    def to_html(self):
        """
        To mimic pandas .html method
        """
        return self.message

    def __bool__(self):
        return False

    def _str__(self):
        return "no context provided"

    def __getitem__(self, item):
        return self

class DocumentProcessor:
    """
    some
    """
    def __init__(
        self,
        db: Db,
        filter_extractor: FilterExtractor,
        ):
        """
        some
        """
        self.db = db
        self.filter_extractor = filter_extractor

    def extract_documents(self, user_query: str, extracted_filters: dict) -> Documents:
        """
        some
        """
        print("Extracting documments")
        documents = self.db.extract_documents(
            user_query,
            extracted_filters,
        )
        return documents


    def handle_db_result(self, documents: Documents) -> pd.DataFrame:
        """
        Convert the documents to a parsed dataframe
        """
        df = pd.DataFrame()
        for doc in documents:

            df_insert = pd.DataFrame(
                {
                    "description": [doc.page_content],
                    "price": [doc.metadata["price"]],
                    "name": [doc.metadata["name"]],
                    "bathrooms": [doc.metadata["bathrooms"]],
                    "review_scores_rating": [doc.metadata["review_scores_rating"]],
                    "review_scores_accuracy": [doc.metadata["review_scores_accuracy"]],
                    "review_scores_cleanliness": [doc.metadata["review_scores_cleanliness"]],
                    "review_scores_checkin": [doc.metadata["review_scores_checkin"]],
                    "review_scores_communication": [doc.metadata["review_scores_communication"]],
                    "review_scores_location": [doc.metadata["review_scores_location"]],
                    "review_scores_value": [doc.metadata["review_scores_value"]],
                }
            )

            df = pd.concat([df, df_insert])

        # index 1,2,3 .... N
        df.reset_index(drop=True)

        return df

    def postfilter_documents(self, documents: pd.DataFrame) -> pd.DataFrame:
        """
        This are the same cols that are being used to do reranking
        This is not necesarly true but it works for now
        """

        print("posfiltering docs")

        non_nullable_cols = [
            'review_scores_rating',
            'review_scores_accuracy',
            'review_scores_cleanliness',
            'review_scores_checkin',
            'review_scores_communication',
            'review_scores_location',
            'review_scores_value',
        ]

        documents =  documents.dropna(subset = non_nullable_cols)

        return documents

    def get_rank_score(self, df_row: pd.Series) -> float:
        """
        Random generated weights
        To be able to create experiments this should me moved
        to a config file or similar
        """

        rank_weights = {
            'review_scores_rating': 0.24,
            'review_scores_accuracy': 0.11,
            'review_scores_cleanliness': 0.02,
            'review_scores_checkin': 0.57,
            'review_scores_communication': 0.75,
            'review_scores_location': 0.65,
            'review_scores_value': 0.33
        }

        field_weight = [value * df_row[key] for key, value in rank_weights.items()]
        total_row_weight = sum(field_weight)
        return total_row_weight

    def rank_documents(self, documents: pd.DataFrame) -> pd.DataFrame:
        """
        Ranking documments based is custom rules
        """
        print("ranking docs")
        # Apply ranking to documents
        df = documents.copy()
        df["ranking_score"] = df.apply(self.get_rank_score, axis = 1)
        df = df.sort_values(by = "ranking_score").head(1)
        del df["ranking_score"]

        return df

    def process_user_query(self, user_query: str) -> dict:
        """
        some
        """
        print("Starting to process user query...")

        extracted_filters = self.filter_extractor.extract_filter(user_query)
        parsed_filters = self.filter_extractor.parse_filters(extracted_filters)
        extracted_documents = self.extract_documents(user_query, parsed_filters)

        # If the database doesn't contain any document
        # That satisfy the filters
        if len(extracted_documents) == 0:
            mocked_extracted_documents_as_df: MockDf = MockDf("No results from db")
            mocked_postfiltered_documents: MockDf = MockDf("No results after postfilter")
            mocked_ranked_documents: MockDf = MockDf("No results after rerank")

            return {
                "extracted_filters": extracted_filters,
                "extracted_documents" : mocked_extracted_documents_as_df.to_html(),
                "postfiltered_documents": mocked_postfiltered_documents.to_html(),
                "ranked_documents": mocked_ranked_documents # Not a bug
            }


        extracted_documents_as_df: pd.DataFrame = self.handle_db_result(extracted_documents)
        postfiltered_documents: pd.DataFrame = self.postfilter_documents(extracted_documents_as_df)
        ranked_documents: pd.DataFrame = self.rank_documents(postfiltered_documents)

        return {
            "extracted_filters": extracted_filters,
            "extracted_documents" : extracted_documents_as_df.to_html(),
            "postfiltered_documents": postfiltered_documents.to_html(),
            "ranked_documents": ranked_documents # Not a bug
        }
