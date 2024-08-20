from io import BytesIO
from load_llm import groq_client
import streamlit as st

import audio_recorder_streamlit as audio_recorder


def record_audio_widget():

    audio_bytes = audio_recorder(
        text="", neutral_color="#CCCCCC", recording_color="red", icon_size="2x", pause_threshold=2.0, key="record_audio"
    )
    return audio_bytes


def translate_audio(audio_bytes):
    translation = groq_client.audio.translations.create(
        file=("aa.wav", audio_bytes),
        model="whisper-large-v3",
    )
    return translation.text


def check_for_processed_audio(audio_bytes):

    if (
        audio_bytes
        and st.session_state.get("audio_bytes", None)
        and st.session_state.get("audio_bytes", "")[:100] == audio_bytes[:100]
    ):
        audio_bytes = None
    else:
        st.session_state["audio_bytes"] = audio_bytes

    return audio_bytes
