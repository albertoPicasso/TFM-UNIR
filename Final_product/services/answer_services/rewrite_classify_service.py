from tools.LLM_tool import LLMTool
from services.answer_services.utils_prompts import UtilsPrompts
import json
import logging

class RewriteClassifyService ():

    def __init__(self,
                 classifier_model_name:str,
                 classifier_model_type:str,
                 classifier_api_key:str,
                 classifier_temperature:float,
                 classifier_max_tokens:int,
                 classifier_top_k:float):

        self.LLM = LLMTool(
                    model_type=classifier_model_type,
                    model_name=classifier_model_name,
                    api_key=classifier_api_key,
                    temperature=classifier_temperature,
                    top_p=classifier_top_k,
                    max_tokens=classifier_max_tokens)

        self.logger = logging.getLogger(__name__)




    def classify_rewrite(self, history):
        """
        Classifies the input question into a specific category and rewrites it for clarity or consistency.

        Parameters:
            history (str): The original user input or conversation history.

        Returns:
            tuple: A tuple containing:
                - category (str): The classified category of the question (e.g., "teoria", "informacion", etc.).
                - question (str): The rewritten version of the input question.

        Description:
            - Constructs a classification prompt from the input text.
            - Queries a language model (LLM) with the prompt.
            - Parses the JSON response to extract the category and rewritten question.
        """

        try:
            prompt = UtilsPrompts.get_classification_prompt_from_text(raw_input=history)
            result = self.LLM.query(prompt=prompt)
            response_json = json.loads(result)

            category = response_json['category']
            question = response_json['rewrite_question']

            return category, question

        except json.JSONDecodeError as e:
            msg = f"Error decodificando JSON en classify_rewrite: {e}"
            self.logger.error(msg)
            raise Exception(msg) from e

        except KeyError as e:
            msg = f"Clave faltante en la respuesta JSON en classify_rewrite: {e}"
            self.logger.error(msg)
            raise Exception(msg) from e

        except Exception as e:
            msg = f"Error inesperado en classify_rewrite: {e}"
            self.logger.error(msg, exc_info=True)
            raise Exception(msg) from e
