from DocumentLoaders.universal_document_loader import Universal_document_loader
from configs.model_config import Model_config
from DatabaseManager.chroma_database_manager import Chroma_database_manager
from DatabaseManager.faiss_database_manager import Faiss_database_manager
from configs.data_config import Data_config
from LLM_handler.LLM_handler import LLMHandler
from questionGenerator.questionGeneratorr import QuestionGenerator
import logging
import os

class Testing_pipeline():

    def __init__(self):

        self.data_config = Data_config("LLM_testing/configs/data_config.json")
        self.database_manager = Faiss_database_manager(work_directory=self.data_config.databases_path,
                                                        model_name=self.data_config.embedding_model_name)

        #self.model_config = Model_config(
        #    "LLM_testing/configs/__model_config.json")

        '''
        self.llm = LLMHandler(model_name=self.model_config.model_name,
                              model_type=self.model_config.model_type,
                              api_key=self.model_config.api_key,
                              max_tokens = self.model_config.max_tokens
                              )
        '''

        logging.basicConfig(filename='LLM_testing/app.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)


    def start(self):
        database_name = "Faiss.db"

        print ("Encendido")
        self.logger.info("Sistema encendido")

        dl = Universal_document_loader(path=self.data_config.docs_path, recursive_mode=self.data_config.recursive_mode, process_images=self.data_config.process_images)
        docs = dl.load_documents()
        print (docs)
        """
        self.logger.info(f"Documentos Cargados desde {self.data_config.docs_path}")
        print ("Extraccion terminada")

        try:
            self.database_manager.create_and_save_embeddings(
                documents=docs, database_name=database_name)
            self.logger.info(f"BBDD creada ")
        except Exception as e:
            self.logger.info(f"Ha ocurrico un error {e}")

        self.logger.info(f"BBDD creada{self.data_config.databases_path}")


        qg = QuestionGenerator()
        question = qg.get_question()

        while (not question == None):
            context = self.database_manager.get_context_with_stats(database_name= database_name, query_text=question)
            response = self.llm.query_with_stats(context = context, question = question, save_path="LLM_testing/Times/generation/gemma-2-9b-it-free-extended-tokens.csv")
            print (response)
            question = qg.get_question()

            """








    def show_data_config(self):
        print(self.data_config.docs_path)
        print(self.data_config.process_images)
        print(self.data_config.recursive_mode)






tp = Testing_pipeline()
tp.start()
