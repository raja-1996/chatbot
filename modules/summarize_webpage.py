from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

summarize_webpage_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        Summarize the following content
        """,
        ),
        MessagesPlaceholder("messages"),
    ]
)


