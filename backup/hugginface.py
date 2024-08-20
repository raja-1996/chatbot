import streamlit as st
import time
from utils import *


# Set the page configuration
st.set_page_config(
    page_title="Meta Llama 3",
    page_icon="https://assets-global.website-files.com/65b8f370a600366bc7cf9b20/660e66b997dc8488ed5ac43a_meta.png",  # Replace with the path to your icon image
    layout="centered",  # Optional: 'centered' or 'wide'
)

chats =[]
with st.sidebar:
    chat_ids = get_chats()

    new_chat = st.button("New chat")
    

    for chat_id, message in chat_ids:
        # st.link_button(label=chat_id, url=f"http://www.google.com")
        # st.link_button(str(chat_id), f"?id={chat_id}")
        st.markdown(f'<a href="/?id={chat_id}" target="_self" style="text-decoration: none">{message[:20]} </a>',unsafe_allow_html=True)


if new_chat:
    del st.query_params["id"]

if "id" not in st.query_params:
    st.query_params["id"] = int(time.time())

messages = parse_messages(get_messages(st.query_params["id"]))
# print(messages)
st.session_state.messages = messages



from huggingface_hub import InferenceClient

client = InferenceClient(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    token="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",
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hi"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    insert_message(st.query_params["id"],  'user', prompt,  len(st.session_state.messages))
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

def parse_output(stream):
    for token in stream:
        yield token.choices[0].delta.content

# print("assistant")
# print(st.session_state.messages)
if prompt:
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            messages=st.session_state.messages,
            stream=True,
            max_tokens=1024,
        )

        response = st.write_stream(parse_output(stream))


        st.session_state.messages.append({"role": "assistant", "content": response})
        insert_message(st.query_params["id"], 'assistant', response, len(st.session_state.messages))
