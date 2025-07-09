from fastapi import FastAPI, Response, status
from API.models.replace_content_input_payload import ReplaceContentInputPayload
from API.models.get_answer_input_payload import GetAnswerInputPayload, Message
from configs.main_config import Main_config
from pathlib import Path
from controllers.answer_controller import AnswerController
import logging

app = FastAPI()
logger = logging.getLogger(__name__)
main_config = Main_config(Path("Final_product") / "configs" / "config.json")

answer_handler = AnswerController(
                                                    database_path = main_config.DATABASE_PATH,
                                                    embedding_model_name = main_config.EMBEDDING_MODEL_NAME,

                                                    classifier_model_type = main_config.CLASSIFIER_MODEL_TYPE,   ##Lo ideal sería usar una clase para encapsular estos datos
                                                    classifier_model_name =  main_config.CLASSIFIER_MODEL_NAME,  ##Pero no se donde ponerla en la arquitectura
                                                    classifier_api_key =  main_config.CLASSIFIER_API_KEY,
                                                    classifier_temperature =  main_config.CLASSIFIER_TEMPERATURE,
                                                    classifier_top_k =  main_config.CLASSIFIER_TOP_P,
                                                    classifier_max_tokens =  main_config.CLASSIFIER_MAX_TOKENS,

                                                    answer_model_type =  main_config.ANSWER_MODEL_TYPE,   ##Lo ideal sería usar una clase para encapsular estos datos
                                                    answer_model_name =  main_config.ANSWER_MODEL_NAME,  ##Pero no se donde ponerla en la arquitectura
                                                    answer_api_key =  main_config.ANSWER_API_KEY,
                                                    answer_temperature =  main_config.ANSWER_TEMPERATURE,
                                                    answer_top_k =  main_config.ANSWER_TOP_P,
                                                    answer_max_tokens =  main_config.ANSWER_MAX_TOKENS,

                                                    content_path= main_config.CONTENT_PATH
                                    )


@app.post("/tfm/service/replaceContent")
def ReplaceContent(payload: ReplaceContentInputPayload) -> Response:
    logger.info("Reemplazando contenido")
    input = payload.root
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/tfm/service/getAnswer")
def GetAnswer(payload: GetAnswerInputPayload) -> Message:
    logger.info(
        "Solicitando respuesta para el historial con %d mensajes ",
        len(payload.messages)
    )
    try:
        response = answer_handler.launch(history=payload.model_dump())
        return Message(role = "assistant", content = response)
    except Exception as e:
        logger.error(f"Error al lanzar answer_handler: {e}", exc_info=True)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
