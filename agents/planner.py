from load_llm import openai_llm, groq_llm
from langchain_core.prompts import ChatPromptTemplate

from typing import *
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import *


class SystemPrompt(BaseModel):
    """generate prompt for better answer the query"""

    prompt: str = Field(..., description="""prompt""")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in answering queries and breaking down complex tasks. Your role is to outline a clear and step-by-step approach to answer the user's question. However, do not execute the steps yourself. Another agent LLM will handle the execution based on your guidance. Your task is to ensure that your steps are detailed, logical, and easy to follow, providing the necessary framework for the other agent to generate the final response. Begin by analyzing the query and then list the steps required to address it comprehensively.

Previous conversation history:
{chat_history}
            """,
        ),
        ("human", "{query}"),
    ]
)

# structured_llm = groq_llm.with_structured_output(SystemPrompt)

structured_llm = prompt | groq_llm


def planner(state):

    chat_history = state["messages"]
    history = [
        message for message in chat_history[:-1] if isinstance(message, HumanMessage) or isinstance(message, AIMessage)
    ]

    response = structured_llm.invoke({"query": chat_history[-1].content, "chat_history": history})
    # steps = [response.prompt]

    steps = [response.content]
    plan_str = "\n\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

    print("***** Planner *****")
    print(plan_str)

    actions = [f"Planner:\n\n{plan_str}"]

    return {"steps": steps, "actions": actions}
