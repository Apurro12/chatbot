"""
Here is where the llm model create the recommendation
"""

from typing import Callable
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from models import Documents

def default_promp(query: str, context: Documents) -> str:
    """
    get the default promp,
    IDK if this should be moved to a config file
    """

    promp =f"""
    Answer this user query: {query} using the context between <>. \n
    Always the name of the property and any other necesarly information. \n
    If not context is provided say that the user must adjust the filters. \n

    context: <\n{context} \n >"""

    return promp

default_system_message: str = "You are a airbnb recommendation system."

class LlmRecomender:
    """
    some
    """
    # pylint: disable=too-few-public-methods
    def __init__(
        self,
        # Where should I put this default args?
        # In a config file or similar? To be defined later
        llm_recommender: BaseChatModel = ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        system_message: str = default_system_message,
        promp: Callable[[str, Documents], str] = default_promp,
        ):
        self.promp = promp
        self.llm_recommender = llm_recommender
        self.system_message = system_message

    def recomend(self, user_query: str, processed_documents: Documents) -> dict[str, str]:
        """
        some
        """
        response = self.llm_recommender.invoke(
            [
                SystemMessage(content=self.system_message),
                HumanMessage(
                    content= self.promp(user_query, processed_documents)
                ),
            ]
        ).content

        assert isinstance(response, str)
        return {
            "response": response, 
            "promp": self.promp(user_query, processed_documents)
        }
