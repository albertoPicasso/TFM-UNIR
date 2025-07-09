from pathlib import Path
from infrastructure.documentLoaders.universal_documents_loader import Universal_documents_loader
from infrastructure.databaseManagers.practise_database_manager import PractiseDatabaseManager
from services.update_services.utils_practise import UtilsPractise
from tools.LLM_tool import LLMTool
import logging


class PractiseUpdateService():

    def __init__(self,
                 database_path:str,
                 context_path:str,
                 summary_model_name:str,
                 summary_model_type:str,
                 summary_api_key:str,
                 summary_temperature:float,
                 summary_max_tokens:int,
                 summary_top_k:float,
                 DL_recursive_mode:bool = True,
                 DL_extract_images:bool = True):

        ##La base de datos ahora va a ser un json

        path =  Path(database_path)
        if not path.exists():
            raise ValueError(f"Document path does not exist: {database_path}")

        path =  Path(context_path)
        if not path.exists():
            raise ValueError(f"Document path does not exist: {context_path}")


        self.DATABASE_PATH = database_path
        self.CONTEXT_PATH = context_path
        self.DL_RECURSIVE_MODE = DL_recursive_mode
        self.DL_EXTRACT_IMAGES = DL_extract_images
        self.utils = UtilsPractise()
        self.LLM = LLMTool(
                    model_type=summary_model_type,
                    model_name=summary_model_name,
                    api_key=summary_api_key,
                    temperature=summary_temperature,
                    top_p=summary_top_k,
                    max_tokens=summary_max_tokens)
        self.db_manager = PractiseDatabaseManager(work_directory=database_path, LLM=self.LLM)

        self.logger = logging.getLogger(__name__)


    def launch(self):
        """
        Loads and processes practical documents, builds a directory tree structure,
        and creates a structured database for LLM-based answering.

        Description:
            - Initializes a universal document loader with recursive search enabled.
            - Loads documents from the configured context path.
            - Merges document pages into a format suitable for LLM consumption.
            - Builds a JSON representation of the folder tree structure.
            - Creates a practical database using the processed documents and the folder tree,
            saving it under 'practica/summary_tree.json'.
        """
        try:
            documentLoader = Universal_documents_loader(
                path=self.CONTEXT_PATH,
                recursive_mode=True,
                process_images=self.DL_EXTRACT_IMAGES
            )

            docs = documentLoader.load_documents()
            docs4LLM = self.utils.merged_pages(docs)
            tree = self.utils.build_tree_json(self.CONTEXT_PATH)
            name = Path("practica") / Path("summary_tree.json")

            self.db_manager.create(docs4LLM, database_name=name, tree=tree)

        except Exception as e:
            self.logger.error(f"Error al construir y almacenar la base de datos de práctica: {e}", exc_info=True)
            raise
