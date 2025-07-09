from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document

class Splitter(ABC):
    @abstractmethod
    def split(self, documents: List[Document]) -> List[Document]:
        """
        Recibe una lista de documentos y devuelve otra lista con los documentos divididos en chunks.

        :param documents: Lista de documentos originales.
        :return: Lista de documentos chunked.
        """
        pass
