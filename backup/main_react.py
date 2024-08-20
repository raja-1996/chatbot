from io import BytesIO
from load_llm import llm, groq_client


import streamlit as st
import time
import json
from utils import *
from langgraph.prebuilt import ToolNode

from langchain_core.messages import *

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_utils import get_session_history
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from audio_recorder_streamlit import audio_recorder


st.set_page_config(
    page_title="Meesho Chatbot",
    page_icon="https://assets-global.website-files.com/65b8f370a600366bc7cf9b20/660e66b997dc8488ed5ac43a_meta.png",
    layout="wide",  # Optional: 'centered' or 'wide'
)


st.markdown(
    """
<style>
p, li, a {
    font-size:18px !important;
    color: #CCCCCC;
            
}
</style>
""",
    unsafe_allow_html=True,
)


def get_role(message):
    if isinstance(message, HumanMessage):
        return "user"

    if isinstance(message, AIMessage):
        return "assistant"

    return "other"


def save_wav_file(filename, audio_bytes):
    with open(filename, mode="wb") as f:
        f.write(audio_bytes)


def audio_to_text(audio_bytes):
    translation = groq_client.audio.translations.create(
        file=("aa.wav", audio_bytes),
        model="whisper-large-v3",
    )
    return translation.text


def get_translated_text(audio_bytes):
    translation_text = audio_to_text(audio_bytes)
    return translation_text


translated_text = ""
chats = []
with st.sidebar:

    audio_bytes = audio_recorder(
        text="", neutral_color="#CCCCCC", recording_color="red", icon_size="2x", pause_threshold=2.0, key="record_audio"
    )

    print("audio bytes")
    if st.session_state.get("audio_bytes", "") == audio_bytes:
        print("Already processed audio")
        audio_bytes = None
    else:
        st.session_state["audio_bytes"] = audio_bytes

    chat_ids = get_chats()

    st.markdown("## Meesho ChatBot")
    st.write("")
    new_chat = st.button("New chat")

    last_chat_id = None
    for chat_id, message in chat_ids:

        prefix = " ".join(message.split()[:3])

        st.markdown(
            f"""
        <a href="/?id={chat_id}" target="_self" style="
        text-decoration: none;
        color: #ffffff;
        ">{prefix} </a>
        """,
            unsafe_allow_html=True,
        )


if new_chat:
    del st.query_params["id"]

new_session = False
if "id" not in st.query_params:
    st.query_params["id"] = int(time.time())
    new_session = True


from chatbot_tools import search_web, scrape_content_from_webpage

tools = [search_web, scrape_content_from_webpage]


from langchain import hub
from langchain_core.prompts import PromptTemplate

prompt_template = """Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

Expectations:

Provide detailed and thorough responses: Ensure that answers are comprehensive and cover all aspects of the question or task.
Break down complex ideas: Explain each concept clearly, using lists, examples, or analogies where necessary to enhance understanding.
Include relevant context and background: Offer additional information that could be helpful for the user’s understanding or future reference.
Expand on implications or related topics: If applicable, suggest related ideas, concepts, or questions that the user might be interested in exploring.


TOOLS:

------

Assistant has access to the following tools:

{tools}

To use a tool, please use the following format:

```

Thought: Do I need to use a tool? Yes [explain why?]

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```

Thought: Do I need to use a tool? No [explain why?]

Final Answer: [generate the response step by step]

```

Begin!

Previous conversation history:

{chat_history}

New input: {input}

{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(template=prompt_template)


agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

runnable_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    output_messages_key="output",
    history_messages_key="chat_history",
)


def parse_output(text):
    text = text.replace("$", "\$")
    return text


def display_messages(messages):
    for message in messages:
        role = get_role(message)
        if role == "other":
            continue

        with st.chat_message(role):
            st.markdown(parse_output(message.content))


if new_session:
    audio_bytes = None

new_session = False


messages = get_session_history(st.query_params["id"]).get_messages()
display_messages(messages)


if audio_bytes:
    translated_text = get_translated_text(BytesIO(audio_bytes))

prompt = st.chat_input("Hi")

if translated_text and translated_text != st.session_state.get("translated_text", ""):
    prompt = translated_text
    st.session_state["translated_text"] = translated_text

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

if prompt:
    with st.chat_message("assistant"):
        stream = runnable_with_history.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": st.query_params["id"]}},
        )

        response = st.write(parse_output(stream["output"]))
