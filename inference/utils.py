import os
from ast import literal_eval
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage


POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
openai_api_key = os.environ.get("OPENAI_API_KEY")
collection_name = os.environ.get("EMBEDING_COLLECTION_NAME") or "vector_collection"


class MockDf():
    def __init__(self, message):
        self.message = message

    def to_html(self):
        return self.message

    def __bool__(self):
        return False

    def _str__(self):
        return "no context provided"

    def __getitem__(self, item):
        return self

def handle_db_result(search_results):

    df = pd.DataFrame()
    for doc in search_results:

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

    # pylint: disable=line-too-long
    system_message = 'You need to extract features from an user question, you are going to respond a python dict with two keys "bathroms" and "price", and you are using None for not found values'
    response = extract_prefilter_model.invoke(
        [
            SystemMessage(content=system_message),
            HumanMessage(content=promp),
        ]
    ).content

    # Any  other than a response than string raise an error
    assert isinstance(response, str)
    return response


def parse_filters(json_filter):
    dict_operator = {"price": "$lte", "bathrooms": "$eq"}
    base_dict = {}
    for amenity, operator in dict_operator.items():
        add_dict = (
            {amenity: {operator: json_filter[amenity]}} if json_filter[amenity] else {}
        )
        base_dict = base_dict | add_dict

    return base_dict



def get_rank_score(df_row):

    # Random generated weights
    # To be able to create experiments this should me moved
    # to a config file or similar
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


def postfilter(df):
    # This are the same cols that are being used to do reranking
    # This is not necesarly true but it works for now
    non_nullable_cols = [
        'review_scores_rating',
         'review_scores_accuracy',
         'review_scores_cleanliness',
         'review_scores_checkin',
         'review_scores_communication',
         'review_scores_location',
         'review_scores_value',
    ]

    df =  df.dropna(subset = non_nullable_cols)

    return df

def rerank(df):

    df = df.copy()
    df["ranking_score"] = df.apply(get_rank_score, axis = 1)
    df = df.sort_values(by = "ranking_score").head(1)
    del df["ranking_score"]

    return df

def handle_intermediate_steps(query):

    vector_store = get_postgres_vector_store()
    condition = literal_eval(extract_prefilter(query))
    pre_filter = parse_filters(condition)

    search_results = vector_store.similarity_search(query, k=3, filter=pre_filter)

    if search_results:
        raw_search_results_df = handle_db_result(search_results)
    else:
        raw_search_results_df = MockDf("No results from db")

    # Do postfilter based on some criteria
    if isinstance(raw_search_results_df, pd.DataFrame):
        postfilter_search_results_df = postfilter(raw_search_results_df)
    else:
        postfilter_search_results_df = MockDf("No results after postfilter")

    # Rank result based on certain criteria
    # This is just an example
    if isinstance(postfilter_search_results_df, pd.DataFrame):
        rerank_search_results = rerank(postfilter_search_results_df)
    else:
        rerank_search_results = MockDf("No results after rerank")


    create_recomendation_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    promp =f"""
    Answer this user query: {query} using the context between <>. \n
    Always the name of the property and any other necesarly information. \n
    If not context is provided say that the user must adjust the filters. \n

    context: <\n{rerank_search_results} \n >"""
    response = create_recomendation_model.invoke(
        [
            SystemMessage(content="You are a airbnb recommendation system."),
            HumanMessage(
                # pylint: disable=line-too-long
                content= promp
            ),
        ]
    ).content

    return {
        "condition": condition,
        "pre_filter": pre_filter,
        # pylint: disable=line-too-long
        "raw_search_results": raw_search_results_df[["name","description","price","bathrooms"]].to_html(),
        # pylint: disable=line-too-long
        "postfilter_search_results": postfilter_search_results_df[["name","description","price","bathrooms"]].to_html(),
        # pylint: disable=line-too-long
        "rerank_search_results": rerank_search_results[["name","description","price","bathrooms"]].to_html(),
        "promp": promp,
        "response": response
        }

def handle_user_query(query):
    return handle_intermediate_steps(query)["response"]


def get_postgres_vector_store():

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=openai_api_key
    )

    # pylint: disable=line-too-long
    connection = f"postgresql+psycopg://postgres:{POSTGRES_PASSWORD}@postgresql/{POSTGRES_DATABASE}"  # Uses psycopg3!
    #connection = "postgresql+psycopg://localhost/vectordb?user=camilo_amadio&password=mysecretpassword"

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    return vector_store
