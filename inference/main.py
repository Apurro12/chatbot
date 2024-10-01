import os
from pydantic import BaseModel
from fastapi import FastAPI
from utils import handle_user_query

class UserQuery(BaseModel):
    query: str

app = FastAPI()


@app.post("/chatbot/")
async def create_item(query: UserQuery):
    return handle_user_query(query.query)