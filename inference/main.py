import os
from pydantic import BaseModel
from fastapi import FastAPI
import pandas as pd
import openai
from utils import get_postgres_vector_store


api_key = os.environ.get('OPENAI_API_KEY')


client = openai.Client(api_key = api_key)
vector_store = get_postgres_vector_store()

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
    {str({"bathroms": 2,"price": 20})}
    
    If one the the two constraint is not present just write null
    
    Example 1:
    User Query: 'I want to rent an aparment in Palermo that have at least 2 bathrooms and a price bellow than $20 the night'
    Response: {str({"bathroms": 2,"price": 20})}
    
    Example 2:
    User Query: 'I want to rent an apartment in Buenos Aires'
    Response: {str({"bathroms": None,"price": None})}
    
    Example 3:
    User Query: 'How much costs a flat in New York with just one bath'
    Response: {str({"bathroms": 1,"price": None})}
    
    Query: <{query}> "
    """

    completion = client.chat.completions.create(
        temperature= 0,
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system", 
                "content": "You need to extract features from an user question"},
            {
                "role": "user", 
                "content": promp
            }
        ]
    )

    response = completion.choices[0].message.content

    # Any  other than a response than string raise an error
    assert type(response) == str
    
    return eval(response)
    

def handle_user_query(query):

    condition = extract_prefilter(query)
    pre_filter = {"price": {"$lte":condition["price"]}} if condition["price"] else {}

    search_results = vector_store.similarity_search(
        query,
        k=3,
        filter= pre_filter
    )

    search_results_df =  handle_db_result(search_results)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system", 
                "content": "You are a airbnb listing recommendation system."},
            {
                "role": "user", 
                "content": f"Answer this user query: {query} with the following context:\n{search_results_df}"
            }
        ]
    )

    return {"response": completion.choices[0].message.content}


class UserQuery(BaseModel):
    query: str


app = FastAPI()


@app.post("/chatbot/")
async def create_item(query: UserQuery):
    return handle_user_query(query.query)