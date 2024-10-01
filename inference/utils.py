import os
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage


POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
openai_api_key  = os.environ.get("OPENAI_API_KEY")
collection_name = os.environ.get("EMBEDING_COLLECTION_NAME") or ''

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

    extract_prefilter_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    promp = f"""
    Given the user query inside <>
    Check if there is a strict constraint in bathrooms and price and extract the maximum price then respond a pytho dictionary with this format
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
    
    Do not respond anything different from the desired python dictionary

    Query: <{query}> "
    """

    response = extract_prefilter_model.invoke([
        SystemMessage(content = "You need to extract features from an user question, you are going to respond a python dict with two keys \"bathroms\" and \"price\", and you are using None for not found values"),
        HumanMessage(content=promp)
    ]).content

    # Any  other than a response than string raise an error
    assert type(response) == str
    return response


def parse_filters(json_filter):
    dict_operator = {"price": "$lte", "bathrooms": "$eq"}
    base_dict = dict()
    for amenity, operator in dict_operator.items():
        add_dict = {amenity: {operator: json_filter[amenity]}} if json_filter[amenity] else {}
        base_dict = base_dict | add_dict

    return base_dict


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

    create_recomendation_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    response = create_recomendation_model.invoke([
        SystemMessage(content = "You are a airbnb recommendation system."),
        HumanMessage(content= f"Answer this user query: {query} with the following context:\n{search_results_df}")
    ]).content

    return {"response": response}


def get_postgres_vector_store():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key = openai_api_key
    )


    connection = f"postgresql+psycopg://postgres:{POSTGRES_PASSWORD}@postgresql/{POSTGRES_DATABASE}"  # Uses psycopg3!

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    return vector_store