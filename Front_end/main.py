import streamlit as st
import pandas as pd
from streamlit_chat import message
import sqlite3
import hashlib
from typing import List, Dict, Any, Tuple

from document_manager import get_subjects, get_categories, render_document_manager, get_documents_dataframe
from program_data_manager import get_programs, get_courses_by_program, get_subjects_by_course
from database_manager import setup_database
from admin_panel import render_admin_panel
from student_panel import render_student_panel
from rag_services import index_document_in_rag, remove_document_from_rag, query_rag_system
from config_manager import render_config_panel

def authenticate(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", 
                  (username, hashed_password))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True, result[0], result[1]
    else:
        return False, None, None

# Document management functions
# def get_documents():
#     conn = sqlite3.connect('users.db')
#     df = pd.read_sql_query("SELECT id, title, created_at, indexed FROM documents", conn)
#     conn.close()
#     return df

def add_document(title, content):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (title, content, indexed) VALUES (?, ?, 0)", (title, content))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Send document to RAG system for indexing
    index_document_in_rag(doc_id, title, content)
    return doc_id

def delete_document(doc_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    # Remove document from RAG system
    remove_document_from_rag(doc_id)

def update_document(doc_id, title, content):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET title = ?, content = ?, indexed = 0 WHERE id = ?", (title, content, doc_id))
    conn.commit()
    conn.close()
    
    # Update document in RAG system
    index_document_in_rag(doc_id, title, content)

def get_document(doc_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, content FROM documents WHERE id = ?", (doc_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)

# Set up the database
setup_database()

# Streamlit app
st.set_page_config(
    page_title="Student RAG Assistant",
    page_icon="",
    layout="wide"
)

# Add configuration panel to sidebar
# render_config_panel()  # Commented out - can be uncommented when needed

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Login page
if not st.session_state.authenticated:
    st.title("Login")
    
    username = st.text_input("Username", value="student")
    password = st.text_input("Password", type="password", value="student123")
    
    if st.button("Login"):
        success, user_id, role = authenticate(username, password)
        if success:
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    # Main application
    st.sidebar.title(f"Welcome, {st.session_state.role}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.role = None
        st.session_state.messages = []
        st.rerun()
    
    # Admin panel
    if st.session_state.role == "admin":
        render_admin_panel()
    else:
        # Student view - only chat
        render_student_panel()
