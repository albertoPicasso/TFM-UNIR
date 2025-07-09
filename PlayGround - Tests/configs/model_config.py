import json


class Model_config:
    def __init__(self, config_path: str):
        """
        Loads configuration from a JSON file.

        :param config_path: Path to the JSON configuration file.
        """
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, "r") as file:
                config = json.load(file)
                self.model_name = config.get("model_name", "gpt-4o-mini-2024-07-18")
                self.model_type = config.get("model_type", "openai")
                self.api_key = config.get("api_key", None)
                self.temperature = config.get("temperature", 1.0)
                self.max_tokens = config.get("max_tokens", 512)
                self.top_p = config.get("top_p", 1.0)
                self.together_api_key = config.get("together_api_key", None)
        except FileNotFoundError:
            raise ValueError(
                f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {self.config_path}")

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "together_api_key": self.together_api_key
        }
