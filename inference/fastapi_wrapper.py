"""
FastApi class
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from recommendation_llm import RecommendationApp

class UserQuery(BaseModel):
    """
    request body
    """
    query: str

# pylint: disable=too-few-public-methods
class FastAPIApp:
    """
    autoexplicative
    """
    def __init__(self, recommendation_app: RecommendationApp):
        self.app = FastAPI()
        self.templates = Jinja2Templates(directory="templates")
        self.recommendation_app = recommendation_app
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def setup_routes(self):
        """
        autoexplicative
        """
        @self.app.post("/intermediate/")
        async def intermediate_responses(query: UserQuery) -> dict:
            return self.recommendation_app.handle_user_query(query.query)

        @self.app.post("/chatbot/")
        async def get_final_response(query: UserQuery) -> dict:
            return self.recommendation_app.handle_user_query(query.query)

        @self.app.get("/webpage")
        async def read_root(request: Request) -> HTMLResponse:
            return self.templates.TemplateResponse("index.html", {"request": request})
