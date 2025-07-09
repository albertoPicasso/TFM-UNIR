from abc import ABC, abstractmethod
from langchain_core.documents import Document
from pathlib import Path
import logging

class DocumentsLoader(ABC):

    """
    Interface for document loaders.
    Defines the required methods for any document loader implementation.
    """


    def __init__(self, path:str , process_images:bool = False, recursive_mode:bool = False):
        self.path = Path(path)
        self.allowed_formats = []
        self.process_images = process_images
        self.recursive_mode = recursive_mode
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def load_documents(self) -> list[list[Document]]:
        """
        Extracts documents from the specified path.

        Returns:
            list of extracted documents
        """
        pass
