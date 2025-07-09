from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFacePipeline
from langchain_together import Together
from transformers import pipeline
from typing import Dict, Any, Optional


class LLMFactory:
    @staticmethod
    def create_llm(
        model_type: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
        **kwargs
    ):
        """Factory method to create LLM instances based on provider type."""

        if model_type == "openai":
            return ChatOpenAI(
                model=model_name or "gpt-4o-mini-2024-07-18",
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )

        elif model_type == "huggingface":
            # Create a config dict instead of modifying os.environ
            hf_config = {}
            if api_key:
                hf_config["token"] = api_key

            hf_pipeline = pipeline(
                "text-generation",
                model=model_name,
                temperature=temperature,
                max_length=max_tokens,
                top_p=top_p,
                **hf_config
            )
            return HuggingFacePipeline(pipeline=hf_pipeline)

        elif model_type == "together":


            return Together(
                model=model_name,
                together_api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )

        else:
            supported = ["openai", "huggingface", "together"]
            raise ValueError(
                f"Unsupported model type: '{model_type}'. Supported types: {supported}")
