from importlib import metadata
from load_llm import llm, groq_client
from io import BytesIO

import streamlit as st
import time
import json
from utils import *

from langchain_core.messages import *


from audio_recorder_streamlit import audio_recorder
from src_utils.helpers import *
from src_utils.audio import translate_audio, check_for_processed_audio

from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st


@st.cache_resource
def get_graph():
    from chat_graph import graph

    return graph


import streamlit as st

st.set_page_config(
    page_title="Chatbot",
    page_icon="src_utils/logo.png",
    layout="wide",  # Optional: 'centered' or 'wide'
)

st.markdown(
    """
<style>
p, li, a {
    font-size:19px !important;
    
            
}
</style>
""",
    unsafe_allow_html=True,
)

# color: #CCCCCC;
# neutral_color="#CCCCCC",

graph = get_graph()


translated_text = ""
with st.sidebar:

    # audio input

    audio_bytes = audio_recorder(
        text="", recording_color="red", icon_size="2x", pause_threshold=2.0, key="record_audio"
    )
    audio_bytes = check_for_processed_audio(audio_bytes)

    if "chats" not in st.session_state:
        chat_ids = get_chats()
        st.session_state["chats"] = chat_ids
    else:
        chat_ids = st.session_state["chats"]

    st.markdown("## Meesho ChatBot")
    st.write("")
    new_chat = st.button("New chat")

    for chat_id, message in chat_ids:

        prefix = " ".join(message.split()[:3])

        st.markdown(
            f"""
        <a href="/?id={chat_id}" target="_self" style="
        text-decoration: none;
        ">{'`' + prefix + '`'}</a>
        """,
            unsafe_allow_html=True,
        )


if new_chat:
    del st.query_params["id"]

if "id" not in st.query_params:
    st.query_params["id"] = int(time.time())

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

        # st_callback = StreamlitCallbackHandler(st.container())
        # config["callbacks"] = [st_callback]
        retries = 2
        while retries:
            try:
                response = graph.invoke({"messages": [("user", prompt)]}, config)
                retries = 0

                state = graph.get_state(config)
                actions = [action for action in state.values["actions"]]

                if len(actions):
                    metadata = "\n\n".join(actions)
                    with st.expander(label="Actions"):
                        st.write(metadata)

                response = st.write(parse_output(response["messages"][-1].content))
                break

            except Exception as e:
                print("Retrying", e)
                retries -= 1
