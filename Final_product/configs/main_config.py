import json
from pathlib import Path

class Main_config():
    def __init__(self, json_path: str):
        """
        Initializes the class by validating and ensuring the required folder structure.

        :param content_path: Path where the content folders should reside.
        :raises ValueError: If the base path does not exist or structure is invalid.
        """
        self._json_path = json_path
        self.load_config()


    def load_config(self):

        try:

            with open(self._json_path, "r") as file:
                conf = json.load(file)
                ##Ingest configs

                self.CONTENT_PATH = conf.get("content_path")
                if not self._path_exists(self.CONTENT_PATH):
                    raise ValueError(f"Document path does not exist: {self.CONTENT_PATH}")

                self.DATABASE_PATH = conf.get("databases")
                if not self._path_exists(self.DATABASE_PATH):
                    raise ValueError(f"Document path does not exist: {self.DATABASE_PATH}")

                self.EMBEDDING_MODEL_NAME = conf.get("embedding_model")

                self.DL_RECURSIVE_MODE = conf.get("DL_recursive_mode", "true").lower() == "true"
                self.DL_EXTRACT_IMAGES = conf.get("DL_extract_images", "false").lower() == "true"

                self.SUMMARY_MODEL_NAME = conf.get("summary_model_name")
                self.SUMMARY_MODEL_TYPE = conf.get("summary_model_type")
                self.SUMMARY_API_KEY = conf.get("summary_api_key")
                self.SUMMARY_TEMPERATURE = conf.get("summary_temperature")
                self.SUMMARY_MAX_TOKENS = conf.get("summary_max_tokens")
                self.SUMMARY_TOP_P = conf.get("summary_top_p")

                self.CLASSIFIER_MODEL_NAME = conf.get("classifier_model_name")
                self.CLASSIFIER_MODEL_TYPE = conf.get("classifier_model_type")
                self.CLASSIFIER_API_KEY = conf.get("classifier_api_key")
                self.CLASSIFIER_TEMPERATURE = conf.get("classifier_temperature")
                self.CLASSIFIER_MAX_TOKENS = conf.get("classifier_max_tokens")
                self.CLASSIFIER_TOP_P = conf.get("classifier_top_p")

                self.ANSWER_MODEL_NAME = conf.get("answer_model_name")
                self.ANSWER_MODEL_TYPE = conf.get("answer_model_type")
                self.ANSWER_API_KEY = conf.get("answer_api_key")
                self.ANSWER_TEMPERATURE = conf.get("answer_temperature")
                self.ANSWER_MAX_TOKENS = conf.get("answer_max_tokens")
                self.ANSWER_TOP_P = conf.get("answer_top_p")

                self.DATABASE_TYPE = conf.get("database_type")




        except FileNotFoundError:
            raise ValueError(f"Configuration file not found: {self._json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {self._json_path}")


    def _path_exists(self, path: str) -> bool:
        """Checks if a given path exists."""
        return Path(path).exists()

    def to_dict(self):
        """Returns the configuration as a dictionary."""
        return {
            "docs_path": self.CONTENT_PATH,
            "databases": self.DATABASE_PATH,
            "embedding_model_name": self.EMBEDDING_MODEL_NAME
        }
