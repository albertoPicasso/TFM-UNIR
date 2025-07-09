from pathlib import Path
from langchain.schema import Document
from langchain.prompts import PromptTemplate

class UtilsPractise:

    def build_tree_json(self, path:str):
        """
        Recursively builds a JSON-like dictionary representing the directory structure
        starting from the given path.

        Parameters:
            path (str): The root directory path to scan.

        Returns:
            dict: A nested dictionary representing the folder and file structure.
                Directories are represented as nested dictionaries, and files as None.
                If access to a directory is denied, returns {"error": "Permission denied"}.

        Description:
            - Converts the input path to a Path object.
            - Iterates through all entries in the directory, sorted by name.
            - If an entry is a subdirectory, recursively builds its tree.
            - If an entry is a file, assigns None as its value in the tree.
        """
        path = Path(path)

        tree = {}
        try:
            entries = sorted(path.iterdir(), key=lambda p: p.name)
        except PermissionError:
            return {"error": "Permission denied"}

        for entry in entries:
            if entry.is_dir():
                tree[entry.name] = self.build_tree_json(entry)
            else:
                tree[entry.name] = None
        return tree


    def get_parts_after_keyword(self, path: str, keyword='practica') -> tuple:
        """this is a split but compatible with all OSs and get left elements from kw"""
        parts = Path(path).parts
        keyword_lower = keyword.lower()

        for i, part in enumerate(parts):
            if part.lower() == keyword_lower:
                return parts[i + 1:]

        raise ValueError(f"Ruta inválida: no se encontró el directorio '{keyword}' en '{path}'")

    def write_value(self, data: dict, keys: list, message:str):
        current = data
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = message

    def write_response_tree(self, doc_path:str, tree:dict, message: str):
        spltitted_selected_path = self.get_parts_after_keyword(doc_path)
        self.write_value(data=tree, keys= spltitted_selected_path, message= message)


    def merged_pages(self, docs):

        merged_docs = []
        for pages in docs:
            if not pages:
                # Documento vacío: contenido vacío y metadata vacía
                merged_docs.append(Document(page_content="", metadata={}))
                continue

            combined_content = "".join(page.page_content for page in pages)
            first_metadata = pages[0].metadata or {}

            merged_docs.append(Document(page_content=combined_content, metadata=first_metadata))

        return merged_docs


    def get_promt_template(self):

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


    def get_summary_prompt_from_document(self, doc: Document) -> str:
        """
        Crea un prompt para pedir un resumen basado en un objeto Document de LangChain.

        :param doc: Objeto Document con el contenido a resumir.
        :return: Cadena con el prompt completo listo para enviar al modelo.
        """
        template = PromptTemplate(
            template="""
            Actúa como un experto en comprensión de textos técnicos y pedagógicos. Tu tarea es analizar y resumir el siguiente documento para que un modelo educativo pueda responder con precisión a preguntas sobre su contenido. El documento puede contener teoría, ejercicios, soluciones, o fragmentos de código.

            Realiza un resumen estructurado que cumpla con los siguientes objetivos:

            1. **Propósito del documento**: Describe de forma general de qué trata el texto (tema principal, área del conocimiento, nivel académico si se deduce).
            2. **Enunciados de ejercicios (si los hay)**:
            - Indica cuántos ejercicios contiene.
            - Resume brevemente cada enunciado: tema tratado, tipo de pregunta (teórica, práctica, aplicada), y objetivo evaluativo.
            3. **Soluciones (si están presentes)**:
            - Explica de forma concisa cómo se resuelven.
            - Menciona qué conceptos o técnicas se aplican.
            4. **Contenido de programación (si aplica)**:
            - Detecta si hay código fuente o pseudocódigo.
            - Describe de qué trata el código: por ejemplo, si implementa listas, funciones, clases, recursividad, estructuras de control, etc.
            - Intenta inferir el objetivo del ejercicio/programa.
            5. **Observaciones pedagógicas (opcional)**:
            - Si hay patrones recurrentes, estilos de pregunta o temas frecuentes, menciónalos.

            🔒 No inventes contenido. Si algún fragmento no es claro, indícalo como "no interpretable".
            🧠 Resume de forma precisa, organizada y orientada a uso por un modelo que debe comprender el texto para asistir a estudiantes o generar respuestas educativas.

            ---

            📄 Documento a resumir:

            ```
            {document}
            ```

            El resumen debe ser claro, coherente y fiel al contenido original.
            No añadas información inventada ni opiniones. Si hay partes que no se entienden, indícalo.
            """,
            input_variables=["document"],
        )

        return template.format(document=doc)

    def get_dummy_promt(self):
        return PromptTemplate(
            template="""
            Solo di hola para mi
            """
        )
