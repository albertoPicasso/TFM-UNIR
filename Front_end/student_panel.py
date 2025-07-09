import streamlit as st
from rag_services import query_rag_system
from program_data_manager import get_programs, get_courses_by_program

def render_student_panel():
    """Render el componente de la interfaz de usuario del panel de estudiante"""
    st.title("Chat con el Asistente RAG")
    
    # Obtener programas
    programs = get_programs()
    if not programs:
        st.warning("No programs found.")
        return

    # program_dict = {name: id for id, name in programs}
    
    # Estado de sesión para el programa y curso seleccionados
    # if 'selected_program_name' not in st.session_state:
    #     st.session_state.selected_program_name = list(program_dict.keys())[0]
    
    # selected_program_name = st.selectbox(
    #     "Select a program:",
    #     list(program_dict.keys()),
    #     key='selected_program_name'
    # )
    # selected_program_id = program_dict[selected_program_name]

    # Obtener cursos para el programa seleccionado
    # courses = get_courses_by_program(selected_program_id)
    # if not courses:
    #     st.warning("No courses found for this program.")
    #     # Restablecer la selección de curso si el programa cambia y no tiene cursos
    #     st.session_state.selected_course_name = None
    #     st.session_state.messages = []
    # else:
    #     course_dict = {name: id for id, name in courses}

    #     # Estado de sesión para el curso seleccionado
    #     if 'selected_course_name' not in st.session_state or st.session_state.selected_course_name not in course_dict:
    #          st.session_state.selected_course_name = list(course_dict.keys())[0]

    #     selected_course_name = st.selectbox(
    #         "Select a course:",
    #         list(course_dict.keys()),
    #         key='selected_course_name'
    #     )
    #     selected_course_id = course_dict[selected_course_name]

    # Mostrar mensajes de chat usando los componentes nativos de Streamlit
    for i, (msg, is_user) in enumerate(st.session_state.get('messages', [])):
        if is_user:
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)
    
    # Usar el input de chat nativo de Streamlit
    if prompt := st.chat_input("Escribe tu mensaje:"):
        # Añadir el mensaje del usuario al chat
        st.session_state.setdefault('messages', []).append((prompt, True))
        # Obtener el historial de conversación anterior para el contexto
        # Obtener mensajes del usuario (True)
        user_messages = [msg for msg, is_user in st.session_state.messages if is_user]

        # Obtener respuestas del asistente (False)  
        assistant_responses = [msg for msg, is_user in st.session_state.messages if not is_user]

        # Emparejarlos correctamente (últimos 10 mensajes, que es el contexto definido en el proyecto)
        history = list(zip(user_messages, assistant_responses))[-10:]

        # Mostrar el estado de carga
        with st.spinner("Obteniendo respuesta del sistema RAG..."):
            # Consultar el sistema RAG con el contexto del programa
            response = query_rag_system(
                prompt, 
                history, 
            )
        
        # Añadir la respuesta de la IA al chat
        st.session_state.messages.append((response, False))
        st.rerun() 