## E2E Chatbot Implementation using LangChain, Docker and FastApi

To run locally, rename `.env.example` to `.env` and add your ChatGPT API key.

### What this repository does:

1. Creates a vector database using PostgreSQL.
2. Downloads Airbnb data from Buenos Aires City.
3. Creates pre-filters using the OpenAI API.
4. Performs RAG (Retrieval-Augmented Generation) with the filtered data.
5. Do post filtering 
5. Perform reranking based in user custom weights
6. Responds to user queries.


### Testing: 

1. Perform unit testing over the promps using Langsmith, only the promp that extract filters is being tested with one example case for now. More examples and more promps will be added in the future

### Next Planned Steps:

1. Abstract classes to handle multiple LLMs.
2. Add memory to the chats using LangChain's built-in features.
3. Expand CI and implement CD.
4. Create a Flask UI to get the responses the all the intermediate steps


## Make inference
Do a post request to this endpoint
`http://localhost:8000/chatbot/`

with a body like this

`
{
    "query": "I want an department in Argentina"
}
`

Or you can use the web interface in 
`http://localhost:8000/webpage/`
where you can check all the intermediate results