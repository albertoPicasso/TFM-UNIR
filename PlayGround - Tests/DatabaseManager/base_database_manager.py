from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

class Base_database_manager():
    """
    Abstract base class for managing vector database operations.

    This class defines a common interface for database managers that handle document
    embedding storage and retrieval. It ensures consistency across different implementations
    while allowing flexibility in the choice of vector database and embedding model.

    Key Features:
    - Initializes an embedding model for document processing.
    - Defines abstract methods for storing and retrieving embeddings.
    - Requires concrete implementations to specify how embeddings are created and queried.
    """


    def __init__(self, work_directory:str, model_name:str):
        self.work_directory = work_directory
        model_kwargs = {'trust_remote_code': 'True'}
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name, model_kwargs= model_kwargs)

    @abstractmethod
    def create_and_save_embeddings (self, text:str) -> None:
        pass

    @abstractmethod
    def get_context(self, database_name: str, query_text: str, k: int = 5) -> list:
        pass
