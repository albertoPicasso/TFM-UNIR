from langchain.prompts import PromptTemplate
from .LLMFactory import LLMFactory
import pandas as pd
import time
import csv
import os


class LLMHandler:
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

    def query(self, context, question: str):
        """
        Performs a query using the provided context and question.

        :param context: The context for the query.
        :param question: The question to ask the model.

        :return: The model-generated response.
        """
        context = self._format_context(context)
        context_prompt_template = self._get_promt_template()

        generation_AIMessage = (context_prompt_template | self.llm).invoke({
            "context": context,
            "question": question
        })

        generation = generation_AIMessage  # .content

        return generation


    def query_with_stats(self, context, question: str, save_path:str):
        """
        Performs a query using the provided context and question.

        :param context: The context for the query.
        :param question: The question to ask the model.

        :return: The model-generated response.
        """
        times = None


        context = self._format_context(context)
        context_prompt_template = self._get_promt_template()

        start_time = time.time()
        generation_AIMessage = (context_prompt_template | self.llm).invoke({
            "context": context,
            "question": question
        })
        end_time = time.time()

        times = (end_time - start_time)
        if hasattr(generation_AIMessage, 'content'):
            response = generation_AIMessage.content.replace('\n', ' ')
            input_tokens = generation_AIMessage.usage_metadata['input_tokens']
            output_tokens = generation_AIMessage.usage_metadata['output_tokens']
            total_tokens = generation_AIMessage.usage_metadata['total_tokens']

        else:
            response = generation_AIMessage.replace('\n', ' ')
            input_tokens = pd.NA
            output_tokens = pd.NA
            total_tokens = pd.NA


        file_exists = os.path.isfile(save_path)
        with open(save_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Escribe encabezados solo si el archivo no existía
            if not file_exists:
                writer.writerow(["time(s)", "question", "response", "input_Tokens", "output_Tokens", "Total_Tokens"])

            # Escribe una nueva fila con los resultados
            writer.writerow([times, question, response ,input_tokens, output_tokens, total_tokens])

        if hasattr(generation_AIMessage, 'content'):
            generation = generation_AIMessage.content  # .content
        else:
            generation = generation_AIMessage

        return generation

    def _get_promt_template(self):

        return PromptTemplate(
            template="""
            Contesta a la pregunta en base al contexto proporcionado y el historial de la conversación.

            Contexto relevante:
            ```
            {context}
            ```

            Pregunta: {question}

            Al citar, incluye el título y la página de los mensajes de los que obtuviste la información.
            Si no es necesario citar, puedes omitirlo. Evita parafrasear de manera que se pierda la flexibilidad del texto original.
            Traduce el contexto si es necesario antes de leerlo.
            """,
            input_variables=["context", "question"],
        )

    def _format_context(self, context):
        if context == None:
            return " "

        formatted_context = []
        for response, score in context:

            page_content = response.page_content
            file_name = response.metadata['title']
            page_number = response.metadata['page_label']

            formatted_context.append(
                f"Archivo: {file_name} (Página {page_number})\n{page_content}")

        return "\n\n".join(formatted_context)
