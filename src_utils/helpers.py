from langchain_core.messages import *
import streamlit as st


def parse_output(text):
    text = text.replace("$", "\$")
    return text


def get_role(message):
    if message.type == "human":
        return "user"

    if message.type == "ai":
        return "assistant"

    return "other"


def display_messages(messages: list[BaseMessage]):
    for message in messages:
        role = get_role(message)
        if role == "other":
            continue

        content = (message.content).strip()
        if len(content):
            with st.chat_message(role):
                st.markdown(parse_output(message.content))
