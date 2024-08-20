import os

import groq
from groq import Groq


def load_groq_client():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return client


def load_groq():
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        # model="llama-3.1-70b-versatile",
        # model="llama-3.1-8b-instant",
        model="llama3-groq-70b-8192-tool-use-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    return llm


def load_openai():
    import os
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        azure_deployment=os.environ["azure_deployment"],
        api_version=os.environ["api_version"],
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    return llm


groq_llm = load_groq()
openai_llm = load_openai()
llm = groq_llm

groq_client = load_groq_client()
