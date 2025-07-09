from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from interfaces.documentsLoader import DocumentsLoader
import re
import time
import pandas as pd
from pathlib import Path

class Universal_documents_loader(DocumentsLoader):

    """
    This class extracts information from files based on a given system path.
    It supports multiple formats, depending on the `documentLoaders` loaded from LangChain.

    Features:
    - Can process files recursively within the specified path or only in the given directory.
    - Allows extracting text from images if enabled.
    - Returns a list where each position contains a list of LangChain `Document` objects, organized by page.
    """


    def __init__(self, path:str , process_images:bool, recursive_mode:bool):
        """
        Path:
            The folder path where the document loader will search for files. It works recursively,
            gathering all files in the specified path, including files in child directories.

        Formats:
            A list of file formats supported by this Document Loader for extracting information.
            Currently, only the PDF loader is supported, but it's easy to implement support for
            additional formats. For more details on extending the loader, refer to:
            https://python.langchain.com/api_reference/community/document_loaders.html
        """
        super().__init__(path, process_images, recursive_mode)
        self.allowed_formats = [".pdf", ".txt", ".url", ".py"]



    def load_documents(self) -> list[list[Document]]:
        """
        Loads and processes documents from the specified directory.

        This method retrieves all available files, applies necessary preprocessing,
        and extracts relevant information to structure them as a list of documents.

        Returns:
            list[list[Document]]: A nested list where each sublist represents a document
            containing its extracted pages.
        """
        docs = []
        files = self._get_all_files()
        self._clean_files(files)

        for file in files:
            try:
                doc = self._extract_document_info(file)
            except Exception as e:
                self.logger.warning(f"Error procesando {file}: {e}", exc_info=True)

            docs.append (doc)
        return docs

    def load_document(self, file_name:str) -> list[Document]:
        path = self.path / Path(file_name)
        try:
            doc = self._extract_document_info(path)
        except Exception as e:
            # Registra el problema y continúa con el siguiente archivo
            self.logger.warning(f"Error procesando {path}: {e}", exc_info=True)

        return doc



    def load_documents_with_timer(self) -> list[list[Document]]:
        docs = []
        times = []
        i = -1
        files = self._get_all_files()
        self._clean_files(files)

        for _ in range(50):
            i += 1
            print ("S" + str(i)  )
            for file in files:
                start_time = time.time()
                docs.append (self._extract_document_info(file))
                end_time = time.time()
                times.append(end_time - start_time)


        df = pd.DataFrame({"Documento": range(1, len(times) + 1), "Tiempo (s)": times})
        save_path = "LLM_testing/times/documen_loader/PyPDFtiempos_sin_images.csv"
        df.to_csv(save_path, index=False)

        return docs



    def _get_all_files(self)-> list[str]:
        """
        Retrieves all files from the specified path (recursively or not).

        Returns:
            files (list[str]): A list of file paths as strings.
        """
        files:list[str] = []
        if (self.recursive_mode):
            for file in self.path.rglob('*'):
                if file.is_file():
                    files.append(file)
            return files

        else:
            for file in self.path.iterdir():
                if file.is_file():
                    files.append(file)

            return files


    def _clean_files(self, files:list[str]) -> list[str]:
        """
        Removes files from the provided list that do not match the allowed formats.

        Args:
            files (list[str]): A list of file paths as strings.

        Returns:
            None: The function modifies the files in place by deleting non-matching ones.
        """
        non_allowed_files = filter(lambda file: file.suffix.lower() not in self.allowed_formats, files)
        for file in non_allowed_files:
            file.unlink()



    def _extract_document_info(self, file:str) -> Document:
        """
        Extracts and processes the content of a document file.

        This method uses a loader to retrieve the document content, then applies
        necessary formatting changes (e.g., replacing OCR-related formatting)
        for each page in the document.

        Args:
            file (str): The path to the document file to be processed.

        Returns:
            list[Document]: A list of Document objects containing the processed content
            of each page in the input file.
        """
        doc = []
        loader  = self._get_loader(file)
        # Get document
        try:
            doc = loader.load()
        except Exception as e:

            if self.process_images:
                try:
                    self.process_images = True
                    loader  = self._get_loader(file)
                    doc = loader.load()
                except Exception as inner_e:
                    self.process_images = False
                    raise RuntimeError(f"Loader failed even after disabling image processing: {inner_e}") from inner_e
                finally:
                    self.process_images = True
            else:
                raise RuntimeError(f"Loader failed: {file}")

        for i in range(len(doc)):
            doc[i].page_content = self._replace_ocr_format(doc[i].page_content)
        return  doc





    def _replace_ocr_format(self, text: str) -> str:
        """
        Replaces markdown image format from ![text] to OCR_figure ![text].

        Args:
            text (str): The input text containing OCR image references.

        Returns:
            str: The modified text with OCR_figure prefix.
        """
        return re.sub(r'(!\[[^\]]*\])', r'texto Figure = \1', text)


    def _get_loader(self, file:str) :
        """
        Determines and returns the appropriate document loader based on file type.

        This method selects a suitable loader for processing documents, currently
        supporting only PDF files. If the file format is not recognized, it raises an
        exception.

        Args:
            file (str): The path to the file to be loaded.

        Returns:
            A document loader instance for handling the specified file type.

        Raises:
            ValueError: If the file format is not supported.
        """

        match (file.suffix.lower()):
            case ".pdf":
                loader = PyPDFLoader(
                    file_path = file,
                    extract_images= self.process_images,
                    images_inner_format="markdown-img"
                    )
                return loader

            case ".txt":
                loader = TextLoader(
                    file_path=file,
                    encoding="utf-8"
                )
                return loader

            case ".url":

                file_path = file
                try:

                    with open(file_path, "r", encoding="utf-8") as f:
                        url = f.read().strip()


                except FileNotFoundError:
                    raise FileNotFoundError(f"El archivo '{file_path}' no fue encontrado.")
                except PermissionError:
                    raise PermissionError(f"No tienes permiso para leer el archivo '{file_path}'.")
                except UnicodeDecodeError:
                    raise UnicodeDecodeError("utf-8", b"", 0, 1, f"No se pudo decodificar el archivo '{file_path}'.")
                except Exception as e:
                    raise Exception(f"Error inesperado al leer el archivo '{file_path}': {e}")

                loader = WebPageLoader(url)
                return loader

            case ".py":
                #Works pretty well with a regular text loader :)
                loader = TextLoader(
                    file_path=file,
                    encoding="utf-8"
                )
                return loader

            case _:
                raise ValueError("File format not supported")




from typing import List
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
import requests
from bs4 import BeautifulSoup
class WebPageLoader(BaseLoader):
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        # Descargar el contenido de la web
        response = requests.get(self.url)
        response.raise_for_status()
        html = response.text

        # Extraer texto visible usando BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=' ', strip=True)
        # Crear un Document con metadata
        docs = [Document(page_content=text, metadata={"source": self.url})]
        return docs
