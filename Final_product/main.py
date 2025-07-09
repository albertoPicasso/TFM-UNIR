from __future__ import annotations
import argparse
from dataclasses import dataclass
from controllers.update_controller import UpdateController
from controllers.answer_controller import AnswerController
# from Final_product.API.api import API
from configs.main_config import Main_config
import json
from pathlib import Path
import uvicorn
import logging



logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),                   # Consola
        logging.FileHandler("app.log", encoding="utf-8")  # Archivo
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Configura las opciones disponibles para la aplicación."""
    update: bool = False
    answer: bool = False


class Application:
    """Clase principal que encapsula la lógica de la aplicación."""
    def __init__(self, config: AppConfig) -> None:
        self.argsconfig = config

        try:

            #Lectura del archivo de configuracion
            self.main_config = Main_config(Path("Final_product") / "configs" / "config.json")

            self.update_handler = UpdateController(content_path = self.main_config.CONTENT_PATH,
                                                database_path = self.main_config.DATABASE_PATH,
                                                embedding_model_name = self.main_config.EMBEDDING_MODEL_NAME,
                                                DL_recursive_mode = self.main_config.DL_RECURSIVE_MODE,
                                                DL_extract_images = self.main_config.DL_EXTRACT_IMAGES,

                                                summary_model_type = self.main_config.SUMMARY_MODEL_TYPE,   ##Lo ideal sería usar una clase para encapsular estos datos
                                                summary_model_name = self.main_config.SUMMARY_MODEL_NAME,  ##Pero no se donde ponerla en la arquitectura
                                                summary_api_key = self.main_config.SUMMARY_API_KEY,
                                                summary_temperature = self.main_config.SUMMARY_TEMPERATURE,
                                                summary_top_k = self.main_config.SUMMARY_TOP_P,
                                                summary_max_tokens = self.main_config.SUMMARY_MAX_TOKENS,

                                                database_type = self.main_config.DATABASE_TYPE
                                                )
            logger.info("UpdateController instanciado")
            self.answer_handler = AnswerController(
                                                    database_path = self.main_config.DATABASE_PATH,
                                                    embedding_model_name = self.main_config.EMBEDDING_MODEL_NAME,

                                                    classifier_model_type = self.main_config.CLASSIFIER_MODEL_TYPE,   ##Lo ideal sería usar una clase para encapsular estos datos
                                                    classifier_model_name = self.main_config.CLASSIFIER_MODEL_NAME,  ##Pero no se donde ponerla en la arquitectura
                                                    classifier_api_key = self.main_config.CLASSIFIER_API_KEY,
                                                    classifier_temperature = self.main_config.CLASSIFIER_TEMPERATURE,
                                                    classifier_top_k = self.main_config.CLASSIFIER_TOP_P,
                                                    classifier_max_tokens = self.main_config.CLASSIFIER_MAX_TOKENS,

                                                    answer_model_type = self.main_config.ANSWER_MODEL_TYPE,   ##Lo ideal sería usar una clase para encapsular estos datos
                                                    answer_model_name = self.main_config.ANSWER_MODEL_NAME,  ##Pero no se donde ponerla en la arquitectura
                                                    answer_api_key = self.main_config.ANSWER_API_KEY,
                                                    answer_temperature = self.main_config.ANSWER_TEMPERATURE,
                                                    answer_top_k = self.main_config.ANSWER_TOP_P,
                                                    answer_max_tokens = self.main_config.ANSWER_MAX_TOKENS,

                                                    content_path=self.main_config.CONTENT_PATH)
            logger.info("AnswerController instanciado")


        except FileNotFoundError:
            raise ValueError(f"Archivo de configuración del main no encontrado:")
        except json.JSONDecodeError:
            raise ValueError(f"Formato JSON inválido en configuracion de main")
        except Exception as e:
            raise ValueError(f"Error inesperado al cargar la configuración del main: {e}")



    # Métodos públicos -----------------------------------------------------
    def run(self) -> None:

        """Ejecuta la acción seleccionada en función de los argumentos."""
        if self.argsconfig.update:
            self._update_content()
        elif self.argsconfig.answer:
            self._simulate_answer()
        else:
            self._launch_server()

    # Métodos privados -----------------------------------------------------
    def _update_content(self) -> None:
        logger.info("Actualizando contenido ... ")
        try:
            self.update_handler.launch()
        except Exception as e:
            logger.critical(f"Error crítico en la secuencia de actualización: {e}", exc_info=True)

        logger.info("Contenido actualizado.")
        try:
            self._launch_server()
        except Exception as e:
            logger.critical(f"Error crítico en el sistema: {e}", exc_info=True)



    def _launch_server(self) -> None:
        logger.info("Lanzando Servidor ... ")
        uvicorn.run("API.api:app", host="127.0.0.1", port=8000, reload=True)


    def _simulate_answer(self):
        #Simulation of entry json
        history = {"messages": [
                        {"role": "user", "content": "Que dia es el examen de programacion II"},
                        {"role": "assistant", "content": "El 5 de junio a las 9 am "},
                        {"role": "user", "content": "Como puedo sacar los primos del 1 al 100"}]}

        answer=self.answer_handler.launch(history)
        print (answer)


# Funciones auxiliares ------------------------------------------------------

def _parse_arguments() -> AppConfig:
    """Analiza los argumentos de línea de comandos y devuelve un AppConfig."""
    parser = argparse.ArgumentParser(
        description="Plataforma final TFM Chatbot en las aulas "
                    "argumentos -u/--update y -t/--test."
    )

    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Actualiza el contenido"
    )

    parser.add_argument(
        "-a",
        "--answer",
        action="store_true",
        help="Simula una pregunta"
    )

    args = parser.parse_args()
    return AppConfig(update=args.update, answer = args.answer)


def main() -> None:
    """Punto de entrada principal."""
    config = _parse_arguments()
    app = Application(config)
    app.run()


if __name__ == "__main__":
    main()
