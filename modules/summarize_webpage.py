from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

summarize_webpage_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        Summarize the content which is related to mentioned queries
        """,
        ),
        MessagesPlaceholder("messages"),
    ]
)
