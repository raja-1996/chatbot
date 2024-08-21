import operator
from typing import *
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages: Annotated[list, add_messages]
    steps: Annotated[list, operator.add]
    agent: str
    actions: Annotated[list, operator.add]
