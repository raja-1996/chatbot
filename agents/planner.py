from load_llm import openai_llm, groq_llm
from langchain_core.prompts import ChatPromptTemplate

from typing import *
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import *


class Planner(BaseModel):
    """list of steps to answer the query"""

    steps: List[str] = Field(
        ...,
        description="""list of steps to answer the query""",
    )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
As a planner, list all the steps required to answer the query. Remeber dont answer answer, Your role is to list the steps
            Previous conversation history:

            {chat_history}
            """,
        ),
        ("human", "{query}"),
    ]
)

structured_llm = groq_llm.with_structured_output(Planner)

structured_llm = prompt | structured_llm


def planner(state):

    chat_history = state["messages"]
    history = chat_history[:-1]

    response = structured_llm.invoke({"query": chat_history[-1].content, "chat_history": history})
    steps = response.steps
    plan_str = "\n\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

    actions = [f"Planner:\n\n{plan_str}"]

    return {"steps": steps, "actions": actions}
