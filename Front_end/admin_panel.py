import streamlit as st
import pandas as pd
from streamlit_chat import message
from document_manager import get_documents_dataframe
from program_data_manager import get_programs, get_courses_by_program, get_subjects_by_course
from rag_services import query_rag_system, index_document_in_rag
import sqlite3
import json
import os
import base64

def save_document_to_db(title, content, category_id, metadata):
    """Save document to database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO documents (title, content, category_id, metadata)
            VALUES (?, ?, ?, ?)
        """, (title, content, category_id, json.dumps(metadata)))
        
        doc_id = cursor.lastrowid
        conn.commit()
        
        # Index the document in RAG system
        index_document_in_rag(doc_id, title, content, metadata)
        
        return True, doc_id
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def render_admin_panel():
    """Render the admin panel UI component"""
    st.sidebar.header("Admin Panel")
    admin_option = st.sidebar.selectbox("Select Option", ["Manage Documents", "Chat"])
    
    if admin_option == "Manage Documents":
        render_document_management()
    else:
        render_chat_interface()

def render_document_management():
    """Render the document management interface"""
    st.title("Document Management")
    
    tab1, = st.tabs(["View Documents"])
    
    with tab1:
        # Get programs
        programs = get_programs()
        if programs:
            # Convert to dictionary for easier selection
            program_dict = {name: id for id, name in programs}
            selected_program = st.selectbox("Seleccionar programa:", list(program_dict.keys()))
            
            # Get courses for selected program
            courses = get_courses_by_program(program_dict[selected_program])
            if courses:
                course_dict = {name: id for id, name in courses}
                selected_course = st.selectbox("Seleccionar curso:", list(course_dict.keys()))
                
                # Get categories for the selected course
                categories = get_subjects_by_course(course_dict[selected_course])
                if categories:
                    category_dict = {name: id for id, name in categories}
                    
                    # File upload section
                    st.header("Upload Document")
                    
                    # Category selection moved outside the file upload block
                    selected_category = st.selectbox("Select Category:", list(category_dict.keys()))
                    
                    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'doc', 'docx', 'md'])
                    
                    if uploaded_file is not None:
                        # Get file name without extension
                        file_name = uploaded_file.name
                        file_extension = file_name.split('.')[-1].lower()
                        
                        # Create metadata JSON
                        metadata = {
                            "subject_id": course_dict[selected_course],
                            "category_id": category_dict[selected_category],
                            "program_id": program_dict[selected_program]
                        }
                        
                        if st.button("Upload"):
                            try:
                                # Read file content based on file type
                                if file_extension in ['pdf', 'doc', 'docx']:
                                    # For binary files, store the raw bytes
                                    content = uploaded_file.getvalue()
                                    # Convert to base64 for storage
                                    content = base64.b64encode(content).decode('utf-8')
                                else:
                                    # For text files, decode as UTF-8
                                    content = uploaded_file.getvalue().decode('utf-8')
                                
                                # Save to database
                                print('# Save to database')
                                success, result = save_document_to_db(
                                    title=file_name,
                                    content=content,
                                    category_id=category_dict[selected_category],
                                    metadata=metadata
                                )
                                
                                if success:
                                    st.success(f"File {file_name} uploaded and indexed successfully!")
                                    st.rerun()  # Refresh the page to show the new document
                                else:
                                    st.error(f"Error saving document: {result}")
                            except Exception as e:
                                st.error(f"Error processing file: {str(e)}")
                
                st.header("All Documents")
                
                # Get all documents for the selected course
                docs_df = get_documents_dataframe(course_dict[selected_course])
                st.write(docs_df)
            else:
                st.info("No courses found for this program.")
        else:
            st.info("No programs found. Please add programs first.")

def render_chat_interface():
    """Render the chat interface"""
    st.title("Chat with RAG Assistant")
    
    # Display chat messages
    for i, (msg, is_user) in enumerate(st.session_state.messages):
        if is_user:
            message(msg, is_user=True, key=f"msg_{i}_user")
        else:
            message(msg, is_user=False, key=f"msg_{i}_ai")
    
    # Chat input
    user_input = st.text_input("Type your message:", key="user_input")
    
    if st.button("Send") and user_input:
        # Add user message to chat
        st.session_state.messages.append((user_input, True))
        
        # Get previous conversation history for context
        history = [(msg, resp) for msg, is_user in st.session_state.messages[:-1:2] 
                   for resp, _ in st.session_state.messages[1::2]]
        
        # Query the RAG system
        response = query_rag_system(user_input, history)
        
        # Add AI response to chat
        st.session_state.messages.append((response, False))
        st.rerun()
