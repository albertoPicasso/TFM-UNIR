from interfaces.splitter import Splitter
from langchain.schema import Document
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextSplitter(Splitter):
    def __init__(self, chunk_size=1500, chunk_overlap=500):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n\n", "\n\n", "\n", ". ", " "]
        )

    def split(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of documents into smaller chunks of text for easier processing or retrieval.

        Parameters:
            documents (List[Document]): A list of Document objects to be split.
                                        Each document contains text content and optional metadata.

        Returns:
            List[Document]: A list of new Document objects, where each contains a chunk of the original content
                            and preserves the associated metadata.

        Description:
            - Iterates through the input documents.
            - Splits each document's content into smaller pieces using a text splitter.
            - Wraps each chunk into a new Document while maintaining the original metadata.
        """
        chunked_docs = []
        for doc in documents:
            chunks = self.splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunked_docs.append(Document(page_content=chunk, metadata=doc.metadata))

        return chunked_docs
