from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain.schema import Document
from typing import List
from interfaces.splitter import Splitter


class HtmlSplitter(Splitter):

    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=[
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3")
            ]
        )

    def split(self, documents: List[Document]) -> List[Document]:
        chunked_docs = []
        for doc in documents:
            chunks = self.splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunked_docs.append(chunk)
        return chunked_docs
