## E2E Chatbot Implementation using LangChain and Docker

To run locally, rename `.env.example` to `.env` and add your ChatGPT API key.

### What this repository does:

1. Creates a vector database using PostgreSQL.
2. Downloads Airbnb data from Buenos Aires City.
3. Creates pre-filters using the OpenAI API.
4. Performs RAG (Retrieval-Augmented Generation) with the filtered data.
5. Responds to user queries.

### Next Planned Steps:

1. Abstract classes to handle multiple LLMs.
2. Add memory to the chats using LangChain's built-in features.
3. Implement CI/CD and testing.
