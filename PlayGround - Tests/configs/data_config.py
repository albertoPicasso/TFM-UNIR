import json
from pathlib import Path

class Data_config:
    def __init__(self, json_path: str):
        """
        Loads configuration from a JSON file.

        :param json_path: Path to the JSON configuration file.
        """
        self.config_path = json_path
        self.load_config()

    def load_config(self):
        """Loads and validates the configuration from the JSON file."""
        try:
            with open(self.config_path, "r") as file:
                conf = json.load(file)

                self.docs_path = conf.get("docs_path")
                if not self._path_exists(self.docs_path):
                    raise ValueError(f"Document path does not exist: {self.docs_path}")

                self.process_images = conf.get("process_images", "true").lower() == "true"
                self.recursive_mode = conf.get("recursive_mode", "false").lower() == "true"

                self.databases_path = conf.get("databases_path")
                if not self._path_exists(self.databases_path):
                    raise ValueError(f"Databases path does not exist: {self.databases_path}")

                self.embedding_model_name = conf.get("embedding_model_name")

        except FileNotFoundError:
            raise ValueError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {self.config_path}")

    def _path_exists(self, path: str) -> bool:
        """Checks if a given path exists."""
        return Path(path).exists()

    def to_dict(self):
        """Returns the configuration as a dictionary."""
        return {
            "docs_path": self.docs_path,
            "process_images": self.process_images,
            "recursive_mode": self.recursive_mode,
            "databases_path": self.databases_path,
            "embedding_model_name": self.embedding_model_name,
        }

