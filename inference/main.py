import os
from pydantic import BaseModel
from fastapi import FastAPI
import pandas as pd
import openai
from langchain_openai import ChatOpenAI
from utils import get_postgres_vector_store
from langchain_core.messages import HumanMessage, SystemMessage

model = ChatOpenAI(model="gpt-3.5-turbo")
api_key = os.environ.get('OPENAI_API_KEY')

def handle_db_result(search_results):

    df = pd.DataFrame()
    for doc in search_results:
    
        df_insert = pd.DataFrame({
        "description": [doc.page_content],
        "price": [doc.metadata["price"]], 
        "bathrooms": [doc.metadata["bathrooms"]]
        })
    
        df = pd.concat([df, df_insert])
    
    # index 1,2,3 .... N
    df.reset_index(drop = True)

    return df

def extract_prefilter(query: str) -> dict[str, str | None]:
    promp = f"""
    Given the user query inside <>
    Check if there is a strict constraint in bathrooms and price and extract the maximum price then respond in this JSON format
    {{"bathroms": 2,"price": 20}}
    
    If one the the two constraint is not present just write null
    
    Example 1:
    User Query: 'I want to rent an aparment in Palermo that have at least 2 bathrooms and a price bellow than $20 the night'
    Response: {{"bathroms": 2,"price": 20}}
    
    Example 2:
    User Query: 'I want to rent an apartment in Buenos Aires'
    Response: {{"bathroms": None,"price": None}}
    
    Example 3:
    User Query: 'How much costs a flat in New York with just one bath'
    Response: {{"bathroms": 1,"price": None}}
    
    Do not respond anything different from the desired JSON

    Query: <{query}> "
    """

    response = model.invoke([
        SystemMessage(content = "You need to extract features from an user question, you are going to respond a JSON, and you are using None for not found values"),
        HumanMessage(content=promp)
    ]).content

    # Any  other than a response than string raise an error
    assert type(response) == str
    
    return response
    

def handle_user_query(query):

    vector_store = get_postgres_vector_store()
    condition = eval(extract_prefilter(query))
    pre_filter = {"price": {"$lte":condition["price"]}} if condition["price"] else {}

    search_results = vector_store.similarity_search(
        query,
        k=3,
        filter= pre_filter
    )

    search_results_df =  handle_db_result(search_results)

    response = model.invoke([
        SystemMessage(content = "You are a airbnb recommendation system."),
        HumanMessage(content= f"Answer this user query: {query} with the following context:\n{search_results_df}")
    ]).content

    return {"response": response}


class UserQuery(BaseModel):
    query: str


app = FastAPI()


@app.post("/chatbot/")
async def create_item(query: UserQuery):
    return handle_user_query(query.query)