"""
This is the application
"""


from database import Db
from recommender import LlmRecomender
from filter_extractor import FilterExtractor
from processor import DocumentProcessor
from recommendation_llm import RecommendationApp
from fastapi_wrapper import FastAPIApp


db_instance = Db()
recommender_instance = LlmRecomender()
filter_extractor_instance = FilterExtractor()
document_processer_instance = DocumentProcessor(db_instance, filter_extractor_instance)
app_instance = RecommendationApp(document_processer_instance, recommender_instance)
fast_api_app = FastAPIApp(app_instance)

db_instance.init_db()
fast_api_app.setup_routes()
app = fast_api_app.app
