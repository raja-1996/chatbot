from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent


from langchain_core.messages import *
from langchain import hub
from langchain_core.prompts import PromptTemplate


def get_react_agent(prompt_template, tools, llm):
    prompt = PromptTemplate.from_template(template=prompt_template)

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=False, handle_parsing_errors=True, return_intermediate_steps=True
    )

    def react_agent_node(state):

        chat_history = state["messages"]
        plan = state["steps"]
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        print(plan_str)

        response = agent_executor.invoke(
            {"input": chat_history[-1].content, "chat_history": chat_history[:-1], "plan_str": plan_str}
        )

        actions = [
            f"Tool: {action[0].tool} \n\n Input: {action[0].tool_input}" for action in response["intermediate_steps"]
        ]

        message = AIMessage(content=response["output"])
        return {"messages": [message], "actions": actions}

    return react_agent_node
