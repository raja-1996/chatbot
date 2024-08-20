import requests
from langchain_community.document_loaders import WebBaseLoader
import nest_asyncio

nest_asyncio.apply()

from modules.newsloader import NewsLoader
from modules.summarize_webpage import summarize_webpage_prompt

from langchain_community.document_loaders import PyMuPDFLoader

from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.retrievers import TavilySearchAPIRetriever


search_engine = DuckDuckGoSearchAPIWrapper()
tavily_retriever = TavilySearchAPIRetriever(k=2)

from load_llm import llm
from langchain_core.tools import tool

import re


def clean_text(text):
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def remove_white_spaces(text):
    text = re.sub(r"\s+", " ", text)
    return text


def summarize_urls(docs):

    if isinstance(docs, str):
        docs = [docs]

    llm_chain = summarize_webpage_prompt | llm

    batch_input = [{"messages": [("human", f"{doc.page_content}")]} for doc in docs]
    webpage_summaries = llm_chain.batch(batch_input, config={"max_concurrency": 10})
    return webpage_summaries


def get_results_from_duckduckgo(search_query):
    return search_engine._ddgs_text(search_query, max_results=2)


def get_results_from_tavily(search_queries):
    queries_docs = tavily_retriever.batch(search_queries)
    docs = [{"href": doc.metadata["source"], "content": doc.page_content} for docs in queries_docs for doc in docs]
    return docs


@tool
def search_web(search_queries: str, explanation: str) -> str:
    """The search_web tool allows to augment knowledge and retrieve the latest information on a topic by searching the web using provided comma-separated search queries max queries 2. This tool returns a summary of the key points from all retrieved web pages, enabling me to provide more accurate and up-to-date information.

    Args:
        search_queries (str): comma seperated search queries without quotes, related to the topic, max queries 3
        explanation (str): give a reason for choosing this tool

    Returns:
        str: summary of all web pages retrieved for a search query
    """

    search_queries = search_queries.split(",")
    search_queries = [clean_text(query) for query in search_queries]

    urls = []
    results = get_results_from_tavily(search_queries)
    urls += [item["href"] for item in results]

    print("****   WEB SEARCH  *****")
    print(search_queries)
    for url in urls:
        print(url)

    summaries = "\n\n".join([f"\n\nContent: {remove_white_spaces(doc['content'])}" for idx, doc in enumerate(results)])
    return summaries

    # urls = []
    # for search_query in search_queries:
    #     results = get_results_from_duckduckgo(search_query)
    #     urls += [item["href"] for item in results]

    urls = []
    results = get_results_from_tavily(search_queries)
    urls += [item["href"] for item in results]

    print("****   WEB SEARCH  *****")
    print(search_queries)
    for url in urls:
        print(url)

    loader = NewsLoader(urls, requests_per_second=10)
    loader.requests_kwargs = {"verify": False}

    docs = loader.aload()

    # summaries = summarize_urls(docs)
    # summaries = "\n\n".join([f"\nSource: {urls[idx]} \n\nContent: {doc.content}" for idx, doc in enumerate(summaries)])

    summaries = "\n\n".join([f"\n\nContent: {remove_white_spaces(doc.page_content)}" for idx, doc in enumerate(docs)])

    return summaries


def read_pdf(url: str) -> list[str]:
    """Read PDF and convert it to list of pages
    use this tool, for urls/file which has .pdf extension

    Args:
        url (str): pdf url

    Returns:
        List[str]: list of pages
    """

    print(f"Reading PDF {url}")
    loader = PyMuPDFLoader(url)
    docs = loader.load()
    docs = [f" \n Page {i+1} \n\n Content: {doc.page_content}" for i, doc in enumerate(docs)]
    docs = "\n\n".join(docs)

    return docs


@tool
def scrape_content_from_webpage(url: str, explanation: str) -> str:
    """scrape text content from webpage

    Args:
        url (str): webpage to scrape
        explanation (str): give a reason for choosing this tool

    Returns:
        str: content from web page
    """

    response = requests.get(url)

    if response.headers["Content-Type"] == "application/pdf":
        return read_pdf(url)

    loader = NewsLoader([url], requests_per_second=10)
    docs = loader.aload()

    summaries = "\n\n".join([doc.page_content for doc in docs])
    return summaries
