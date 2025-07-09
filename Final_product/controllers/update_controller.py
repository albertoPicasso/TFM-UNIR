from pathlib import Path
import shutil
from services.update_services.regular_update_service import RegularUpdateService
from services.update_services.practise_update_service import PractiseUpdateService
import logging

class UpdateController():

    def __init__(self, content_path: str,
                 database_path: str,
                 embedding_model_name:str,
                 summary_model_name:str,
                 summary_model_type:str,
                 summary_api_key:str,
                 summary_temperature:float,
                 summary_max_tokens:int,
                 summary_top_k:float,
                 DL_recursive_mode:bool = False,
                 DL_extract_images:bool = True,
                 database_type = "FAISS"
                 ):
            """
            Initializes the application by validating the given content path.

            This constructor checks that the specified content path exists and that it
            contains the required directory structure:
            - teoria/
            - info/
            - practica

            :param content_path: The base directory path to validate.
            :raises ValueError: If the path does not exist or the structure is invalid.
            """
            path = Path(content_path)
            if not path.exists():
                raise ValueError(f"Document path does not exist: {content_path}")

            if not self._structure_is_valid(content_path):
                raise ValueError(f"Estructura inválida en: {content_path}")

            self.CONTEN_PATH = content_path

            path = Path(database_path)
            if not path.exists():
                raise ValueError(f"Document path does not exist: {database_path}")

            if not self._structure_is_valid(database_path):
                raise ValueError(f"Estructura inválida en: {database_path}")

            self.DATABASE_PATH = database_path

            teoria_content_path = str(Path(content_path) / "teoria")

            self.update_theory_service = RegularUpdateService(database_path=database_path,
                                                             context_path = teoria_content_path,
                                                             embedding_model_name= embedding_model_name,
                                                             DL_extract_images= DL_extract_images,
                                                             DL_recursive_mode=DL_recursive_mode,
                                                             database_type=database_type,
                                                             database_name = "teoria/")

            info_content_path = str(Path(content_path) / "info")
            self.update_info_service = RegularUpdateService(database_path=database_path,
                                                             context_path = info_content_path,
                                                             embedding_model_name= embedding_model_name,
                                                             DL_extract_images= DL_extract_images,
                                                             DL_recursive_mode=DL_recursive_mode,
                                                             database_type=database_type,
                                                             database_name = "info/")

            lab_content_path = str(Path(content_path) / "practica")
            self.update_practise_service = PractiseUpdateService(database_path=database_path,
                                                             context_path = lab_content_path,
                                                             summary_model_type =  summary_model_type,
                                                             summary_model_name =  summary_model_name,
                                                             summary_api_key = summary_api_key,
                                                             summary_temperature = summary_temperature,
                                                             summary_top_k = summary_top_k,
                                                             summary_max_tokens = summary_max_tokens,
                                                             DL_extract_images= DL_extract_images,
                                                             DL_recursive_mode= True,)           ##Always set at true

            self.logger = logging.getLogger(__name__)





    def _structure_is_valid(self, content_path: str) -> bool:
        base = Path(content_path)

        required_dirs = ["teoria", "info", "practica"]
        practica_subdirs = [] # ["examenes", "ejercicios"]

        for d in required_dirs:
            if not (base / d).is_dir():
                return False

        for sub in practica_subdirs:
            if not (base / "practica" / sub).is_dir():
                return False

        return True


    def _clear_structure_content(self, content_path: str) -> None:
        """
        Removes all files and subdirectories inside the required folders,
        while keeping the main structure intact.

        :param content_path: Base path where the structure exists.
        """
        base = Path(content_path)
        target_dirs = ["teoria", "info", "practica"]

        for rel_path in target_dirs:
            dir_path = base / rel_path
            if dir_path.is_dir():
                for item in dir_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)


    def launch(self):
        """
        Executes the update process for all knowledge bases by clearing existing content
        and triggering updates for theory, information, and practical data sources.

        Description:
            - Clears the content of the current database directory.
            - Launches the update services for:
                - Theory content
                - Informational content
                - Practical exercises or files
        """
        try:
            self._clear_structure_content(self.DATABASE_PATH)
            self.update_theory_service.launch()
            self.update_info_service.launch()
            self.update_practise_service.launch()
        except Exception as e:
            self.logger.error(f"Error crítico durante el proceso de actualización: {e}", exc_info=True)
            raise
