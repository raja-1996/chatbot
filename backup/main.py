from load_llm import llm


import streamlit as st
import time
import json
from utils import *
from langgraph.prebuilt import ToolNode

from langchain_core.messages import *

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_utils import get_session_history
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent




from chatbot_tools import search_web
tools = [search_web]
# tools = []

# llm = llm.bind_tools(tools)
# tool_node = ToolNode(tools=tools)


# Set the page configuration
st.set_page_config(
    page_title="Meesho Chatbot",
    page_icon="https://assets-global.website-files.com/65b8f370a600366bc7cf9b20/660e66b997dc8488ed5ac43a_meta.png",  # Replace with the path to your icon image
    layout="centered",  # Optional: 'centered' or 'wide'
)


def get_role(message):
    if isinstance(message, HumanMessage):
        return 'user'

    if isinstance(message, AIMessage):
        return 'assistant'
    
    return 'other'

chats =[]
with st.sidebar:
    chat_ids = get_chats()
    st.markdown("## Meesho ChatBot")
    st.write("")
    new_chat = st.button("New chat")
    
    last_chat_id = None
    for chat_id, message in chat_ids:
        if chat_id == last_chat_id:
            continue
        last_chat_id = chat_id
        message = json.loads(message)['data']['content']
        # st.link_button(label=chat_id, url=f"http://www.google.com")
        # st.link_button(str(chat_id), f"?id={chat_id}")
        prefix = ' '.join(message.split()[:3])

        st.markdown(f'''
        <a href="/?id={chat_id}" target="_self" style="
        text-decoration: none;
        color: #ffffff;
        ">{prefix} </a>
        ''', unsafe_allow_html=True)



if new_chat:
    del st.query_params["id"]

if "id" not in st.query_params:
    st.query_params["id"] = int(time.time())


# Avoid using tools for basic queries or when a straightforward answer or explanation suffices.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful assistant. Use tools if required. Provide detailed answer
            """,
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# llm = prompt | llm



agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

runnable_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    output_messages_key='output',
    history_messages_key="history",
)

def display_messages(messages):
    for message in messages:
        role = get_role(message)
        if role == 'other':
            continue

        with st.chat_message(role):
            st.markdown(message.content)

messages = get_session_history(st.query_params["id"]).get_messages()
display_messages(messages)
print("Displayed message")

if prompt := st.chat_input("Hi"):
    with st.chat_message("user"):
        st.markdown(prompt)
print("prompt message")

if prompt:
    print("running assistane")
    with st.chat_message("assistant"):
        stream =  runnable_with_history.invoke(
                {"input": prompt},
                config={"configurable": {"session_id": st.query_params["id"]}},
            )


        response = st.write(stream['output'])
        
        
        # response = st.write_stream(stream)


