#!/usr/bin/env python
# coding: utf-8

# In[1]:

import re
import pandas as pd
from langchain_core.documents import Document

import os
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
collection_name = os.environ.get("EMBEDING_COLLECTION_NAME")
openai_api_key = os.environ.get("OPENAI_API_KEY")


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key = openai_api_key
)

# In[2]:

# This is a copy-paste of the other one bacause
# In build is using socket insted of TCP, so I need to edit this fn
# To be able to use in both places (build and runtime) 
# Maybe get and environment to check if is build or runtime
def get_postgres_vector_store():
    #Because this is being done on build, it is connecting using the unix socket
    connection = f"postgresql+psycopg://postgres:{POSTGRES_PASSWORD}@:5432/{POSTGRES_DATABASE}"  # Uses psycopg3!

    return_vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    return return_vector_store


# In[2]:

metadata_cols = [
    "beds",
    "bathrooms_text",
    "bathrooms",
    "accommodates",
    "price",
    "review_scores_rating",
    "review_scores_accuracy",
    "review_scores_cleanliness",
    "review_scores_checkin",
    "review_scores_communication",
    "review_scores_location",
    "review_scores_value",
    "name"
]

usecols = ["description"] + metadata_cols


df: pd.DataFrame = pd.read_csv(
    filepath_or_buffer = "listings.csv",
    usecols= usecols,
    # nrows = 100 #just for testing
)

# In[4]:

#ChatGPT generated
def extract_number_with_decimal(text: str):
    """
    extract non numeric values from string
    """
    # Use a regex pattern to match numbers with optional decimal points
    number = re.findall(r'\d+\.?\d*', text)
    # Join all found numbers into a single string (if there are any)
    return ''.join(number) if number else 'nan'


# In[5]:


df["price"] = df["price"].str.replace('$','').str.replace(',','').astype(float)
df["bathrooms"] = (
    df["bathrooms"]
        .apply(lambda row: float(extract_number_with_decimal(str(row))))
)

df["description"] = df["description"].str.lower()
df = df.dropna(subset = ["description"])

df.reset_index(drop = True)
df = df.fillna('null')


# In[7]:
vector_store = get_postgres_vector_store()


# In[8]:


documents = []

for index, row in df.iterrows():
    doc = Document(
        page_content= row["description"],
        metadata= {key: row[key] for key in metadata_cols}
    )

    documents.append(doc)

    if  bool(index % 10**3 == 0): # type: ignore
        vector_store.add_documents(documents)
        documents = []

#The final docs
if len(documents):
    vector_store.add_documents(documents)
