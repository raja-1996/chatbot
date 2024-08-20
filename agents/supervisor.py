from load_llm import openai_llm, groq_llm
from langchain_core.prompts import ChatPromptTemplate

from typing import *
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import *


class Supervisor(BaseModel):
    """select agent and explantion for selecting the agent"""

    agent: Literal["ai_expert", "stock_trader", "generic"] = Field(
        ...,
        description="""select following agents based user question agents: ai_expert, stock_trader, generic""",
    )

    explanation: str = Field(description="explain the reason for selecting specific agent")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
As a supervisor, select the appropriate agent based on the query:

AI Expert: Specialized in AI and Data Science, focusing on developing new models, algorithms, and analyzing complex data.
Stock Trader: Specializes in stock market analysis and trading, with expertise in financial markets and trading strategies.
Generic Agent: Handles general topics not covered by the other agents.
Specify the reason for your selection.

            Previous conversation history:

            {chat_history}
            """,
        ),
        ("human", "{query}"),
    ]
)

structured_llm = groq_llm.with_structured_output(Supervisor)

structured_llm = prompt | structured_llm


def supervisor(state):

    chat_history = state["messages"]
    history = [message for message in chat_history[:-1] if isinstance(message, HumanMessage)]
    response = structured_llm.invoke({"query": chat_history[-1].content, "chat_history": history})
    agent = response.agent
    return {"agent": agent, "actions": [f"Agent: {agent} \n\n Explantion: {response.explanation}"]}
