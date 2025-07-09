from langchain.prompts import PromptTemplate
from typing import Union, List, Tuple
from langchain.docstore.document import Document
import json


class UtilsPrompts():

    @staticmethod
    def get_classification_prompt_from_text(raw_input: Union[str, dict]) -> str:
        """
        Crea un prompt para clasificar una entrada académica y reformular la última pregunta del usuario,
        utilizando los mensajes anteriores como contexto.

        :param raw_input: JSON que contiene una conversación (str o dict).
        :return: Cadena con el prompt completo listo para enviar al modelo.
        """
        if isinstance(raw_input, str):
            try:
                raw_input = json.loads(raw_input)
            except json.JSONDecodeError:
                raise ValueError("El raw_input no es un JSON válido.")

        # Si es un dict con 'messages', extraerlos
        if isinstance(raw_input, dict) and "messages" in raw_input:
            messages = raw_input["messages"]
        elif isinstance(raw_input, list):
            messages = raw_input
        else:
            raise ValueError("El formato de entrada no es válido. Esperado: dict con 'messages' o lista de mensajes.")

        # Extraer los mensajes del usuario
        user_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]

        if not user_messages:
            raise ValueError("No se encontraron mensajes del usuario.")

        # Último mensaje es la pregunta, el resto es contexto
        question = user_messages[-1].strip()
        context = "\n".join(user_messages[:-1]).strip()

        template = """
            Eres un asistente académico experto en clasificación de contenidos educativos y formulación clara de preguntas.

            Contexto:
            {contexto}

            Pregunta del usuario:
            {pregunta}

            Tu tarea es analizar la pregunta del usuario teniendo en cuenta que el último mensaje del chat es la pregunta principal
            y los mensajes anteriores son el contexto necesario para entenderla completamente. Devuelve un JSON con dos claves:

            - "category": Clasifica el contenido en una de estas cuatro opciones (usa solo una):
                - "teoria": si el texto trata sobre explicaciones conceptuales o marcos teóricos.
                - "informacion": si se refiere a organización de la materia, fechas, reglas, bibliografía, etc.
                - "practica": si el contenido es un ejercicio, problema, pregunta de examen o algo que requiere resolución.
                - "irrelevante": si el contenido no tiene que ver con un aspecto académico relacionado con la programación informática o es ofensivo. Devuelve la misma palabra como pregunta reformulada.

            - "rewrite_question": Reformula la última pregunta del chat añadiendo la información necesaria para que sea respondida. Este información debes tomarla de la historia de la conversación.

            Instrucciones adicionales para la reformulación:
            - No añadas información que no esté explícitamente en el texto.
            - Si la última pregunta es ambigua o depende del contexto anterior, intégrala con ese contexto para que tenga sentido por sí sola.
            - Ejemplo: Si el texto es:
                “¿Cuándo es el examen? El día 5. ¿Qué entra?”
                Deberás reformular la última pregunta como:
                “¿Qué contenidos entran en el examen del día 5?”

            - Usa un lenguaje claro, formal y directo.

            Salida esperada (en formato JSON):
            {{
            "category": "...",
            "rewrite_question": "..."
            }}

            Devuelve solo texto plano, no ```json ni nada por el estilo
        """.strip()

        return template.format(contexto=context, pregunta=question)



    @staticmethod
    def get_answering_prompt_from_question_and_context(
        question: str,
        context: List[Tuple[Document, float]]
    ) -> str:
        """
        Crea un prompt para responder a una pregunta académica usando un contexto proporcionado.

        :param question: Pregunta del usuario (str).
        :param context: Lista de tuplas (Document, score), donde Document tiene .page_content.
        :return: Prompt en formato string para enviar al modelo.
        """
        if not question.strip():
            raise ValueError("La pregunta no puede estar vacía.")

        if not context:
            context_text = "No se proporcionó contexto documental."
        else:
            # Extraer el contenido de cada documento, eliminar duplicados y juntar el texto
            context_text = "\n\n".join(set(doc.page_content.strip() for doc, _ in context if doc.page_content))

        prompt_template = """
            Eres un asistente académico experto. Se te hará una pregunta, y tienes a tu disposición un conjunto de fragmentos de documentos como contexto.

            Tu tarea es:
            1. Analizar el contexto documental proporcionado.
            2. Determinar si el contexto es suficiente y adecuado para responder.
            3. Si es suficiente, responde **solo en base a ese contexto**.
            4. Si no es suficiente pero conoces la respuesta por conocimiento general, respóndela con claridad.
            5. Si no puedes responder con seguridad, indícalo de forma clara.

            Requisitos:
            - Si usas el contexto, cita brevemente el contenido relevante sin inventar.
            - No inventes datos que no estén ni en el contexto ni en tu conocimiento general.
            - Responde con un tono académico, claro y preciso.

            Pregunta:
            {question}


            Contexto:
            {context}

            Respuesta:
            """.strip()

        return prompt_template.format(question=question.strip(), context=context_text.strip())


    @staticmethod
    def get_relevant_files_prompt_from_query_and_summaries(query: str, summaries: Union[str, dict]) -> str:
        """
        Crea un prompt para seleccionar los archivos relevantes (con su ruta completa) para responder a una consulta del usuario.

        :param query: Pregunta o consulta del usuario.
        :param summaries: Diccionario (o JSON serializado) con resúmenes de archivos disponibles (puede tener múltiples niveles).
        :return: Cadena con el prompt completo listo para enviar al modelo.
        """
        import json
        from textwrap import indent

        def flatten_summaries(data, path=""):
            flat = {}
            for key, value in data.items():
                new_path = f"{path}/{key}" if path else key
                if isinstance(value, dict):
                    flat.update(flatten_summaries(value, new_path))
                else:
                    flat[new_path] = value
            return flat

        if isinstance(summaries, str):
            try:
                summaries = json.loads(summaries)
            except json.JSONDecodeError:
                raise ValueError("El parámetro 'summaries' no es un JSON válido.")

        # Aplanar estructura anidada
        flat_summaries = flatten_summaries(summaries)

        # Construir texto de resúmenes
        summaries_text = ""
        for full_path, resumen in flat_summaries.items():
            summaries_text += f"\nArchivo: {full_path}\n{indent(resumen.strip(), '    ')}\n"

        # Template del prompt
        template = f"""
        Eres un asistente académico encargado de identificar qué archivos son relevantes para responder a una consulta realizada por un estudiante.

        Tienes a tu disposición un conjunto de archivos con sus resúmenes. Cada archivo tiene una **ruta completa** con el formato "carpeta/subcarpeta/.../nombre_de_archivo".

        Tu tarea consiste en devolver una lista que contenga únicamente los nombres completos de los archivos (incluyendo la ruta completa), que puedan contener información útil y pertinente para construir una respuesta basada en contexto.

        Reglas:
        - No asumas ni inventes contenido que no esté explícitamente en los resúmenes.
        - Si consideras que ningún archivo es útil para la consulta, devuelve una lista vacía.
        - No justifiques tu respuesta, solo devuelve la lista.

        Formato de salida esperado:

        ["carpeta/archivo1", "carpeta/subcarpeta/archivo2", ...]


        Consulta del usuario:
        \"\"\"
        {query.strip()}
        \"\"\"

        Resúmenes disponibles:
        {summaries_text.strip()}

        Recuerda responder solo con los que estés seguro de contienen información relevante.
        """

        return template.strip()

    @staticmethod
    def get_answering_prompt_pratise(query: str, context: List[List[Document]]) -> str:
        """
        Crea un prompt que instruye al modelo a generar una respuesta académica basada en un conjunto de documentos contextuales,
        siguiendo buenas prácticas de programación y manteniendo un estilo académico riguroso.

        :param query: Pregunta o consulta del usuario.
        :param context: Lista de listas de Document (estructura típica en LangChain).
        :return: Cadena con el prompt completo listo para enviar al modelo.
        """
        from textwrap import indent

        # Aplanar la lista de listas
        flattened_docs = [doc for sublist in context for doc in sublist]

        # Construir texto del contexto
        context_text = ""
        for idx, doc in enumerate(flattened_docs, 1):
            content = doc.page_content.strip()
            metadata = doc.metadata.get("source", f"Documento_{idx}")
            context_text += f"\nFuente: {metadata}\n{indent(content, '    ')}\n"

        # Plantilla del prompt
        template = f"""
        Eres un asistente académico con conocimientos avanzados en programación y buenas prácticas de desarrollo de software.

        Tienes acceso a una colección de fuentes documentales académicas. Tu tarea es generar una respuesta clara, precisa y de alta calidad
        a una consulta del usuario, usando exclusivamente la información provista en los documentos de contexto.

        Reglas:
        - Utiliza únicamente el contenido disponible en los documentos para construir tu respuesta.
        - Adopta un tono académico, técnico y profesional.
        - Aplica principios de diseño limpio y buenas prácticas de programación cuando sea relevante.
        - No inventes información ni asumas detalles no explícitos en el contexto.
        - Si la consulta no puede ser respondida con el contexto, indícalo explícitamente.

        Consulta del usuario:
        \"\"\"
        {query.strip()}
        \"\"\"

        Contexto disponible:
        {context_text.strip()}

        Escribe una respuesta detallada y precisa utilizando el estilo académico y técnico apropiado.
        """

        return template.strip()
