from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent


from langchain_core.messages import *
from langchain import hub
from langchain_core.prompts import PromptTemplate

from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st


from langchain.agents.format_scratchpad.tools import (
    format_to_tool_messages,
)


def get_tool_agent(prompt, tools, llm):

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=False, handle_parsing_errors=False, return_intermediate_steps=True
    )

    def tool_agent_node(state, config):

        chat_history = state["messages"]

        plan = state["steps"]
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))

        response = agent_executor.invoke(
            {"input": chat_history[-1].content, "chat_history": chat_history[:-1], "plan_str": plan_str}
        )

        actions = [
            f"Tool: {action[0].tool} \n\n Input: {action[0].tool_input}" for action in response["intermediate_steps"]
        ]

        tool_messages = format_to_tool_messages(response["intermediate_steps"])
        message = AIMessage(content=response["output"])
        return {"messages": tool_messages + [message], "actions": actions}

    return tool_agent_node
