import os
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
openai_api_key  = os.environ.get("OPENAI_API_KEY")
collection_name = os.environ.get("EMBEDING_COLLECTION_NAME") or ''


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key = openai_api_key
)

def get_postgres_vector_store():
    connection = f"postgresql+psycopg://postgres:{POSTGRES_PASSWORD}@postgresql/{POSTGRES_DATABASE}"  # Uses psycopg3!

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

    return vector_store