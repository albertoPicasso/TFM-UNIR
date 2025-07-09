from DocumentLoaders.universal_document_loader import Universal_document_loader
from configs.model_config import Model_config
from DatabaseManager.chroma_database_manager import Chroma_database_manager
from DatabaseManager.faiss_database_manager import Faiss_database_manager
from configs.data_config import Data_config
from LLM_handler.LLM_handler import LLMHandler
from questionGenerator.questionGeneratorr import QuestionGenerator
import logging
import os

from utils.ragas_helpers import process_qa_folder, iterate_qa_entries, get_entries_by_file, read_qa_file, parse_llm_response, save_evaluation_data_to_json
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness, answer_relevancy, context_recall, context_precision
from datasets import Dataset


class Testing_pipeline():

    def __init__(self):

        self.data_config = Data_config("LLM_testing/configs/data_config.json")
        # self.database_manager = Chroma_database_manager(work_directory=self.data_config.databases_path,
        #                                                 model_name=self.data_config.embedding_model_name)
        self.database_manager = Faiss_database_manager(work_directory=self.data_config.databases_path,
                                                       model_name=self.data_config.embedding_model_name)

        self.model_config = Model_config(
            "LLM_testing/configs/__model_config.json")

        self.llm = LLMHandler(model_name=self.model_config.model_name,
                              model_type=self.model_config.model_type,
                              api_key=self.model_config.api_key
                              )

        logging.basicConfig(filename='LLM_testing/app.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def start(self):
        database_name = "ragas.db"

        self.logger.info("Document loader init")
        dl = Universal_document_loader(
            path=self.data_config.docs_path, recursive_mode=self.data_config.recursive_mode, process_images=self.data_config.process_images)

        docs = dl.load_documents()

        print(f"Documentos Cargados {docs}")
        print(f"Documentos Cargados desde: {self.data_config.docs_path}")
        self.logger.info(
            f"Documentos Cargados desde {self.data_config.docs_path}")

        try:
            self.database_manager.create_and_save_embeddings(
                documents=docs, database_name=database_name)
            self.logger.info(f"BBDD creada")
        except Exception as e:
            print(f"Ha ocurrico un error {e}")
            self.logger.info(f"Ha ocurrico un error {e}")

        # self.logger.info(f"BBDD creada{self.data_config.databases_path}")

        print('lets read the questions')
        folder_questions = 'LLM_testing/questionGenerator/sets'

        questions = process_qa_folder(folder_questions)
        qs = []
        answers = []
        contexts = []
        ground_truth = []
        for question in questions:
            context = self.database_manager.get_context(
                database_name=database_name, query_text=question['question'])
            first_result = context[0]
            first_document = first_result[0]
            question_context = first_document.page_content

            response = self.llm.query(context, question)

            qs.append(question['question'])
            ground_truth.append(question['answer'])
            contexts.append([question_context])
            answers.append(response.content)

        data_to_evaluate = {
            'question': qs,
            'answer': answers,
            'contexts': contexts,
            'ground_truth': ground_truth
        }

        save_evaluation_data_to_json(
            data_to_evaluate=data_to_evaluate,
            output_dir='evaluation_data',
            filename='evaluatingdata.json'
        )

        dataset = Dataset.from_dict(data_to_evaluate)

        score = evaluate(dataset, metrics=[
                         faithfulness, answer_correctness, answer_relevancy, context_recall, context_precision])

        '''
            Explanation from https://medium.com/data-science/evaluating-rag-applications-with-ragas-81d67b0ee31a
            context_relevancy (signal-to-noise ratio of the retrieved context): While the LLM judges all of the context as relevant for the last question, it also judges that most of the retrieved context for the second question is irrelevant. Depending on this metric, you could experiment with different numbers of retrieved contexts to reduce the noise.
            context_recall (if all the relevant information required to answer the question was retrieved): The LLMs evaluate that the retrieved contexts contain the relevant information required to answer the questions correctly.
            faithfulness (factual accuracy of the generated answer): While the LLM judges that the first and last questions are answered correctly, the answer to the second question, which wrongly states that the president did not mention Intel’s CEO, is judged with a faithfulness of 0.5.
            answer_relevancy (how relevant is the generated answer to the question): All of the generated answers are judged as fairly relevant to the questions.
        '''

        df = score.to_pandas()
        df.to_csv('score.csv', index=False)

    def show_data_config(self):
        print(self.data_config.docs_path)
        print(self.data_config.process_images)
        print(self.data_config.recursive_mode)


tp = Testing_pipeline()
tp.start()
