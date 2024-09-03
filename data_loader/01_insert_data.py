#!/usr/bin/env python
# coding: utf-8

# In[2]:

import re
import os
import pandas as pd
from langchain_core.documents import Document
import psycopg
from utils import get_postgres_vector_store

# In[1]: Check the data is not already insserted

query = """
SELECT EXISTS (
SELECT FROM pg_tables
WHERE  schemaname = 'public'
AND    tablename  = 'langchain_pg_embedding'
);
 """

with psycopg.connect("dbname=postgres user=postgres password=mysecretpassword host=postgresql") as conn:
    with conn.cursor() as cur:
        table_exists,  = cur.execute(query).fetchone() # type: ignore

        # If the embedings are up to date
        if table_exists:
            exit(0)



# In[2]:


df: pd.DataFrame = pd.read_csv(
    filepath_or_buffer = "listings.csv",
    usecols= ["description","beds","bathrooms_text","bathrooms","accommodates","price"],
    nrows = 100 #just for testing
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


df["price_float"] = df["price"].str.replace('$','').str.replace(',','').astype(float)
df["bathrooms_float"] = (
    df["bathrooms_text"]
        .apply(lambda row: float(extract_number_with_decimal(str(row))))
)

df["description_lower"] = df["description"].str.lower()

df = df[["price_float","bathrooms_float","description_lower"]]
df = df.dropna(subset = ["description_lower"])

df.reset_index(drop = True)
df = df.fillna('null')


# In[7]:
vector_store = get_postgres_vector_store()


# In[8]:


documents = []

for index, row in df.iterrows():
    doc = Document(
        page_content= row["description_lower"],
        metadata={"price": row["price_float"], "bathrooms": row["bathrooms_float"]},
    )

    documents.append(doc)

    if  bool(index % 10**3 == 0): # type: ignore
        vector_store.add_documents(documents)
        documents = []

#The final docs
vector_store.add_documents(documents)
# %%
