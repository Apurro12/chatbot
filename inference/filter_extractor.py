"""
Some general class
"""
from ast import literal_eval
from typing import Callable
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)

def default_promp(query: str) -> str:
    """
    get the default promp,
    IDK if this should be moved to a config file
    """

    promp = f"""
    Given the user query inside <>
    Check if there is a strict constraint in bathrooms and price and extract the maximum price then respond a pytho dictionary with this format
    {{"bathrooms": 2,"price": 20}}
    
    If one the the two constraint is not present just write null
    
    Example 1:
    User Query: 'I want to rent an aparment in Palermo that have at least 2 bathrooms and a price bellow than $20 the night'
    Response: {{"bathrooms": 2,"price": 20}}
    
    Example 2:
    User Query: 'I want to rent an apartment in Buenos Aires'
    Response: {{"bathrooms": None,"price": None}}
    
    Example 3:
    User Query: 'How much costs a flat in New York with just one bath'
    Response: {{"bathrooms": 1,"price": None}}
    
    Do not respond anything different from the desired python dictionary

    Query: <{query}> "
    """

    return promp

# pylint: disable=line-too-long
default_system_message: str = 'You need to extract features from an user question, you are going to respond a python dict with two keys "bathroms" and "price", and you are using None for not found values'

class FilterExtractor:
    """
    some
    """
    def __init__(
        self,
        llm_filter: BaseChatModel = ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        system_message: str = default_system_message,
        filter_promp: Callable[[str], str] = default_promp,
        ):
        self.llm_filter = llm_filter
        self.filter_promp = filter_promp
        self.system_message = system_message


    def extract_filter(self, user_query: str) -> dict[str, str]:
        """
        some docstring
        """
        response = self.llm_filter.invoke(
            [
                SystemMessage(content=self.system_message),
                HumanMessage(content=self.filter_promp(user_query)),
            ]
        ).content

        # Any  other than a response than string raise an error
        assert isinstance(response, str)
        filter_dict = literal_eval(response)
        assert isinstance(filter_dict, dict)
        print("extracted filters:", filter_dict)
        return filter_dict

    def parse_filters(self, filter_dict: dict):
        """
        Parse the python dict style filter
        To mongo aggregation style
        """
        dict_operator = {"price": "$lte", "bathrooms": "$eq"}
        base_dict: dict = {}
        for amenity, operator in dict_operator.items():
            add_dict = (
                {amenity: {operator: filter_dict[amenity]}} if filter_dict[amenity] else {}
            )
            base_dict = base_dict | add_dict

        print("Parsed filters:", base_dict)
        return base_dict
