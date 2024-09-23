## E2E Chatbot Implementation using LangChain, Docker and FastApi

To run locally, rename `.env.example` to `.env` and add your ChatGPT API key.

### What this repository does:

1. Creates a vector database using PostgreSQL.
2. Downloads Airbnb data from Buenos Aires City.
3. Creates pre-filters using the OpenAI API.
4. Performs RAG (Retrieval-Augmented Generation) with the filtered data.
5. Responds to user queries.


### Testing.
1) Perform unit testing over the promps using Langsmith, only the promp that extract filters is being tested with one example case for now. More examples and more promps will be added in the future

### Next Planned Steps:

1. Abstract classes to handle multiple LLMs.
2. Add memory to the chats using LangChain's built-in features.
3. Expand CI and implement CD.


## Make inference
Do a post request to this endpoint
`http://localhost:8000/chatbot/`

with a body like this

`
{
    "query": "I want an department in Argentina"
}
`