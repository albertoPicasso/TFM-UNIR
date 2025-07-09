import os
import json
import requests
from typing import List, Tuple
import streamlit as st
from document_manager import mark_document_as_indexed
from config_manager import ConfigManager

# Integración con el sistema RAG
def index_document_in_rag(doc_id, title, content, metadata: dict = None):
    """Enviar un documento al sistema RAG para indexar"""
    try:
        rag_api_url = f"{ConfigManager.get_rag_endpoint()}/index"
        
        payload = {
            "document_id": doc_id,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = requests.post(
            rag_api_url, 
            json=payload,
            timeout=ConfigManager.get_api_timeout()
        )
        
        if response.status_code == 200:
            mark_document_as_indexed(doc_id)
            return True
        else:
            st.error(f"Failed to index document: {response.text}")
            return False
    except requests.exceptions.Timeout:
        st.error("Tiempo de espera agotado. Por favor, verifique la configuración de su endpoint.")
        return False
    except Exception as e:
        st.error(f"Error al indexar el documento: {str(e)}")
        return False

def remove_document_from_rag(doc_id):
    """Eliminar un documento del sistema RAG"""
    try:
        rag_api_url = f"{ConfigManager.get_rag_endpoint()}/remove"
        
        payload = {
            "document_id": doc_id
        }
        
        response = requests.post(
            rag_api_url, 
            json=payload,
            timeout=ConfigManager.get_api_timeout()
        )
        
        if response.status_code != 200:
            st.error(f"Error al eliminar el documento del índice: {response.text}")
    except requests.exceptions.Timeout:
        st.error("Tiempo de espera agotado. Por favor, verifique la configuración de su endpoint.")
    except Exception as e:
        st.error(f"Error removing document from index: {str(e)}")

def query_rag_system(query: str, history: List[Tuple[str, str]], program_id: int = None, course_id: int = None) -> str:
    """Consultar el sistema RAG con la pregunta del usuario"""
    try:
        rag_api_url = ConfigManager.get_rag_endpoint()

        formatted_history = []
        
        # Se añaden los mensajes anteriores si los hay
        for user_msg, ai_msg in history:
            formatted_history.append({"role": "user", "content": user_msg})
            formatted_history.append({"role": "assistant", "content": ai_msg})
        
        # Agregar el mensaje que acaba de escribir el usuario
        formatted_history.append({"role": "user", "content": query})
        
        payload = {
            "messages": formatted_history
        }
        
        response = requests.post(
            rag_api_url, 
            json=payload,
            timeout=ConfigManager.get_api_timeout()
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, dict):
                # Se comprueba si el resultado tiene las propiedades role y content
                if "role" in result and "content" in result:
                    return result["content"]
                
                # Si no se encuentra ninguna de las propiedades esperadas, se devuelve un mensaje de error
                else:
                    return f"Unexpected response format. Available keys: {list(result.keys())}"
            
            # Si la respuesta es una cadena, se devuelve directamente
            elif isinstance(result, str):
                return result
            
            # Si la respuesta es una lista, se busca el primer mensaje con las propiedades role y content
            elif isinstance(result, list) and len(result) > 0:
                for item in result:
                    if isinstance(item, dict) and "role" in item and "content" in item:
                        if item["role"] == "assistant":
                            return item["content"]
                return "No assistant message found in response list"
            
            else:
                return f"Unexpected response type: {type(result)}"
        else:
            return f"Error al consultar el sistema RAG: HTTP {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return "Tiempo de espera agotado. Por favor, verifique la configuración de su endpoint."
    except requests.exceptions.ConnectionError:
        return "No se puede conectar al sistema RAG. Por favor, verifique la URL de su endpoint y asegúrese de que el servicio esté funcionando."
    except Exception as e:
        return f"Error: {str(e)}"

def test_rag_connection() -> bool:
    """Probar la conexión al sistema RAG"""
    try:
        rag_api_url = f"{ConfigManager.get_rag_endpoint()}/health"
        
        response = requests.get(
            rag_api_url,
            timeout=ConfigManager.get_api_timeout()
        )
        
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False