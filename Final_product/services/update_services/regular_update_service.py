from pathlib import Path
from infrastructure.documentLoaders.universal_documents_loader import Universal_documents_loader
from infrastructure.Splitters.text_splitter import TextSplitter
from infrastructure.databaseManagers.chroma_database_manager import Chroma_database_manager
from infrastructure.databaseManagers.faiss_database_manager import Faiss_database_manager
import logging

class RegularUpdateService():

    def __init__(self,
                 database_path:str,
                 context_path:str,
                 database_name:str,
                 embedding_model_name: str,
                 DL_recursive_mode:bool = False,
                 DL_extract_images:bool = True,
                 database_type:str = "faiss"
                 ):


        path =  Path(database_path)
        if not path.exists():
            raise ValueError(f"Document path does not exist: {database_path}")

        path =  Path(context_path)
        if not path.exists():
            raise ValueError(f"Document path does not exist: {context_path}")


        self.DATABASE_PATH = database_path
        self.CONTEXT_PATH = context_path
        self.EMBEDDING_MODEL = embedding_model_name
        self.DL_RECURSIVE_MODE = DL_recursive_mode
        self.DL_EXTRACT_IMAGES = DL_extract_images
        self.DATABASE_NAME = database_name

        if (database_type == "faiss"):
            self.database_manager = Faiss_database_manager(model_name=self.EMBEDDING_MODEL,
                                                            work_directory=self.DATABASE_PATH)
        elif (database_type == "chroma"):
            self.database_manager = Chroma_database_manager(model_name=self.EMBEDDING_MODEL,
                                                            work_directory=self.DATABASE_PATH)
        else:
            raise ValueError ("Database selected is not implemented")

        self.logger = logging.getLogger(__name__)



    def launch(self):
        """
        Loads documents from a specified directory, splits them into chunks, and creates a database for future retrieval.

        Description:
            - Initializes a document loader with configured settings such as recursive loading and image processing.
            - Loads all documents from the context path.
            - Splits each document into smaller text chunks using a text splitter.
            - Stores the resulting chunks into a database using the database manager.

        Notes:
            - The documents are prepared for efficient retrieval and question-answering tasks.
            - The database is created or overwritten with the specified name.
        """
        try:
            documentLoader = Universal_documents_loader(
                path=self.CONTEXT_PATH,
                recursive_mode=self.DL_RECURSIVE_MODE,
                process_images=self.DL_EXTRACT_IMAGES
            )

            docs = documentLoader.load_documents()

            text_splitter = TextSplitter()
            chunks_docs = []

            for doc in docs:
                chunks_docs.append(text_splitter.split(doc))

            self.database_manager.create(documents=chunks_docs, database_name=self.DATABASE_NAME)

        except Exception as e:
            self.logger.error(f"Error al preparar y almacenar los documentos: {e}", exc_info=True)
            raise
