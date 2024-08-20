import os

import groq


os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Meesho Chatbot"
os.environ["USER_AGENT"] = "Mozilla/5.0"

os.environ["TAVILY_API_KEY"] = "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"

from groq import Groq

os.environ["GROQ_API_KEY"] = "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"


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



groq_llm = load_groq()
llm = groq_llm

groq_client = load_groq_client()
