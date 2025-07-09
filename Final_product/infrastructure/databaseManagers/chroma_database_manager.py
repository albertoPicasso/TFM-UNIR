from interfaces.databaseManager import Database_manager
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
import time
import pandas as pd
import os
import csv

class Chroma_database_manager(Database_manager):
    """
    Manages document embedding storage and retrieval using a vector database.

    This class provides functionality to generate, store, and retrieve document embeddings
    using a Chroma-based vector database. It allows for efficient similarity searches and
    ensures proper preprocessing of documents before indexing.

    Key Features:
    - Converts documents into embeddings and stores them in a vector database.
    - Prevents overwriting existing databases to ensure data integrity.
    - Supports similarity-based retrieval of documents for contextual search.
    - Implements reranking for improved result relevance.
    """


    def __init__(self, model_name: str, work_directory:str):
        super().__init__(work_directory, model_name)



    def create (self, documents: list[list[Document]], database_name:str) -> None:
        """
        Generate and store document embeddings in a vector database.

        This method processes a list of documents, converts them into embeddings, and
        stores them in a Chroma vector database. If a database with the given name already
        exists, an exception is raised to prevent overwriting.

        :param documents: A nested list where each sublist contains pages of a document.
        :type documents: list[list[Document]]
        :param database_name: Name of the database to be created, defaults to "test1.db".
        :type database_name: str, optional
        :raises FileExistsError: If a database with the specified name already exists.
        """

        database_path = self.work_directory + database_name

        path = Path(database_path)
        if path.exists() and any(path.iterdir()):
            raise FileExistsError("The database already exists in current workspace (folder is not empty).")

        else:
            docs = []

            for i, doc in enumerate(documents):
                for j, page in enumerate(doc):
                    docs.append(self._preprocess_document(page, num_doc=i, num_page=j ))


            Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_model,
                persist_directory = database_path)



    def get_context(self, database_name:str, query_text: str, k: int = 5) -> list:
        """
        Retrieve the top K most relevant documents from the vector database.

        This method performs a similarity search on the specified database to find
        documents that are semantically similar to the given query. The results are
        then reranked for improved relevance.

        :param database_name: Name of the database to search in.
        :type database_name: str
        :param query_text: The input query used for similarity search.
        :type query_text: str
        :param k: Number of top relevant documents to retrieve, defaults to 5.
        :type k: int, optional
        :return: A list of tuples containing the retrieved documents and their similarity scores.
        :rtype: list
        :raises FileExistsError: If the specified database does not exist.
        """

        database_path = self.work_directory + database_name
        path = Path(database_path)

        if not path.exists() or not any(path.iterdir()):
            raise FileExistsError("The database doesn't exist or the directory is empty in the current workspace.")

        vector_store= Chroma(persist_directory=database_path, embedding_function=self.embedding_model)
        results = vector_store.similarity_search_with_score(query_text,k=k)
        results = self._rerank_documents(results)
        return results


    def _rerank_documents(self, context:list, distance_threshold:float = 6.5) -> list:

        """
        Rerank context retrieved using L2 distance given by database

        Return an Ordered and filtered context tuple(score, document) by distance and threshold
        """

        sorted_results = sorted(context, key=lambda x: x[1], reverse=True)
        filtered_results = list(filter(lambda x: x[1] <= distance_threshold, sorted_results))
        return filtered_results
        """
        for res, score in results:
            print(f"* [Distance = {score:3f}] {res.page_content} [{res.metadata}]")
        """




    def _preprocess_document(self, doc: Document, num_doc:int, num_page:int) -> Document:

        """
            Clean unnecessary metadata and assing an unique ID
            ID = Document * 10000 + page number = Document 3 page number 5 = 30005
                                                  Document 0 page 0 = 0
        """

        metadata = {}
        source_file = doc.metadata['source'].split('\\')[-1]
        page_label = doc.metadata['page_label']

        metadata['title'] = source_file
        metadata['page_label'] = page_label

        doc.metadata = metadata
        doc.id = str((num_doc*10000) + num_page)
        return doc
