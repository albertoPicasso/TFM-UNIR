from interfaces.databaseManager import Database_manager
from langchain_core.documents import Document
from services.update_services.utils_practise import UtilsPractise
from tools.LLM_tool import LLMTool
from pathlib import Path
import json

class PractiseDatabaseManager(Database_manager):

    def __init__(self, work_directory:str, LLM:LLMTool):
        self.WORK_DIRECTOY = work_directory
        self.LLM = LLM
        self.utils = UtilsPractise()

    def create (self, documents: list[list[Document]], database_name:str, tree ) -> None:

        for doc in documents :
            prompt = self.utils.get_summary_prompt_from_document(doc)
            summary = self.LLM.query(prompt=prompt)
            self.utils.write_response_tree(doc_path = doc.metadata["source"],
                                     tree = tree,
                                     message = summary)

        output_path = Path(self.WORK_DIRECTOY) / Path(database_name)

        output_path.write_text(
            json.dumps(tree, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def get_context(self, path:str):
        """
        Lee un archivo JSON desde el path proporcionado y devuelve su contenido como objeto Python.

        :param path: Ruta al archivo JSON (str o Path).
        :return: Contenido del JSON como dict o list.
        :raises FileNotFoundError: Si el archivo no existe.
        :raises json.JSONDecodeError: Si el contenido no es JSON válido.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"El archivo no existe: {path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Error al decodificar JSON en {path}: {e.msg}", e.doc, e.pos
            )
