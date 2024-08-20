from typing import List

from langchain_core.documents import Document

from langchain_community.document_loaders.web_base import *
from newspaper import Article


class NewsLoader(WebBaseLoader):
    """Load `IMSDb` webpages."""

    def scrape_all(self, urls: List[str], parser: Union[str, None] = None) -> List[Any]:
        """Fetch all urls, then return soups for all results."""
        from bs4 import BeautifulSoup

        results = asyncio.run(self.fetch_all(urls))
        final_results = []
        for i, result in enumerate(results):
            url = urls[i]
            if parser is None:
                if url.endswith(".xml"):
                    parser = "xml"
                else:
                    parser = self.default_parser
                self._check_parser(parser)
            final_results.append(result)

        return final_results

    def aload(self) -> List[Document]:  # type: ignore
        """Load text from the urls in web_path async into Documents."""

        results = self.scrape_all(self.web_paths)

        docs = []
        for path, input_html in zip(self.web_paths, results):

            article = Article(path)
            article.download(input_html=input_html)
            article.parse()
            text = article.text
            metadata = {
                "title": getattr(article, "title", ""),
                "link": getattr(article, "url", getattr(article, "canonical_link", "")),
                "authors": getattr(article, "authors", []),
                "language": getattr(article, "meta_lang", ""),
                "description": getattr(article, "meta_description", ""),
                "publish_date": getattr(article, "publish_date", ""),
            }
            docs.append(Document(page_content=text, metadata=metadata))

        return docs
