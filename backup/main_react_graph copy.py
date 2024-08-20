from importlib import metadata
from load_llm import llm, groq_client
from io import BytesIO

import streamlit as st
import time
import json
from utils import *

from langchain_core.messages import *

from st_utils.audio import record_audio, translate_audio, check_for_processed_audio
from st_utils.helpers import *
import audio_recorder_streamlit as audio_recorder

st.set_page_config(
    page_title="Meesho Chatbot",
    page_icon="https://assets-global.website-files.com/65b8f370a600366bc7cf9b20/660e66b997dc8488ed5ac43a_meta.png",
    layout="wide",  # Optional: 'centered' or 'wide'
)


@st.cache_resource
def get_graph():
    from chat_graph import graph

    return graph


graph = get_graph()

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


translated_text = ""
chats = []


with st.sidebar:

    # audio_bytes = record_audio()

    audio_bytes = audio_recorder(
        text="", neutral_color="#CCCCCC", recording_color="red", icon_size="2x", pause_threshold=2.0, key="record_audio"
    )
    check_for_processed_audio(audio_bytes)

    chat_ids = get_chats()

    st.markdown("## Meesho ChatBot")
    st.write("")
    new_chat = st.button("New chat")

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


if new_session:
    audio_bytes = None

new_session = False

if audio_bytes:
    translated_text = translate_audio(BytesIO(audio_bytes))

prompt = st.chat_input("Hi")

if translated_text and translated_text != st.session_state.get("translated_text", ""):
    prompt = translated_text
    st.session_state["translated_text"] = translated_text


config = {"configurable": {"thread_id": st.query_params["id"]}}
states = graph.get_state_history(config)
for state in states:
    messages = state.values["messages"]
    display_messages(messages)
    break


if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

if prompt:
    with st.chat_message("assistant"):

        response = graph.invoke({"messages": [("user", prompt)]}, config)

        state = graph.get_state(config)
        actions = [action.content for action in state.values["actions"]]
        metadata = "\n\n".join(actions)

        with st.container(border=True):
            st.write(metadata)

        response = st.write(parse_output(response["messages"][-1].content))
