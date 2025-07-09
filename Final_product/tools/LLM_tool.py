
from factories.LLMFactory import LLMFactory
class LLMTool():
    def __init__(
        self,
        model_name: str,
        model_type: str = "openai",
        api_key: str = None,
        temperature: float = 1,
        max_tokens: int = 512,
        top_p: float = 1.0
    ):
        """
        Initializes the query handler with a language model.

        :param model_name: Name of the language model (e.g., 'gpt-4' for OpenAI or 'bigscience/bloom' for Hugging Face).
        :param model_type: Type of model ('openai' or 'huggingface').
        :param api_key: API key for authentication.
        :param temperature: Controls randomness (0 = deterministic, 1 = very random).
        :param max_tokens: Maximum number of tokens to generate.
        :param top_p: Controls nucleus sampling (0-1, lower = more focused responses).
        """
        self.model_type = model_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

        self.llm = LLMFactory.create_llm(
            model_type=model_type,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )

    def query(self, prompt: str):
        """
        Performs a query using the provided prompt.

        :param prompt: The full prompt to send to the model.

        :return: The model-generated response.
        """

        response = self.llm.invoke(prompt)
        return response.content
