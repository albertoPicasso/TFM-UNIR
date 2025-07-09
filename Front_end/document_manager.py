import os
import pandas as pd
from datetime import datetime
import streamlit as st
import shutil
import sqlite3

def get_subjects():
    """Get list of subjects from the cursos folder"""
    base_path = "cursos"
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    subjects = [d for d in os.listdir(base_path) 
                if os.path.isdir(os.path.join(base_path, d))]
    return subjects

def get_categories():
    """Get the standard categories for each subject"""
    return ["ejercicios", "examenes", "informacion", "temas"]

def ensure_subject_structure(subject):
    """Ensure the folder structure exists for a subject"""
    base_path = os.path.join("cursos", subject)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    for category in get_categories():
        category_path = os.path.join(base_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

def create_subject(subject_name):
    """Create a new subject with the standard folder structure"""
    if not subject_name:
        return False, "Subject name cannot be empty"
    
    base_path = os.path.join("cursos", subject_name)
    if os.path.exists(base_path):
        return False, f"Subject '{subject_name}' already exists"
    
    ensure_subject_structure(subject_name)
    return True, f"Subject '{subject_name}' created successfully"

def delete_subject(subject_name):
    """Delete a subject and all its contents"""
    base_path = os.path.join("cursos", subject_name)
    if not os.path.exists(base_path):
        return False, f"Subject '{subject_name}' does not exist"
    
    try:
        shutil.rmtree(base_path)
        return True, f"Subject '{subject_name}' deleted successfully"
    except Exception as e:
        return False, f"Error deleting subject: {str(e)}"

def get_files(subject, category):
    """Get list of files in a specific subject category"""
    path = os.path.join("cursos", subject, category)
    if not os.path.exists(path):
        ensure_subject_structure(subject)
        return pd.DataFrame(columns=['id', 'filename', 'created_at', 'indexed'])
    
    files = []
    for i, filename in enumerate(os.listdir(path)):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            # Get file creation time
            created_time = os.path.getctime(file_path)
            created_at = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if file has been indexed (this is a mock - you'd need to track this separately)
            # For now, we'll assume files with .txt extension are indexed
            indexed = filename.endswith('.txt')
            
            files.append({
                'id': i + 1,
                'filename': filename,
                'created_at': created_at,
                'indexed': indexed
            })
    
    return pd.DataFrame(files)

def get_file_content(subject, category, filename):
    """Get the content of a specific file"""
    file_path = os.path.join("cursos", subject, category, filename)
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def save_file(subject, category, filename, content):
    """Save content to a file in the specified location"""
    ensure_subject_structure(subject)
    file_path = os.path.join("cursos", subject, category, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f"File '{filename}' saved successfully"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"

def delete_file(subject, category, filename):
    """Delete a specific file"""
    file_path = os.path.join("cursos", subject, category, filename)
    if not os.path.exists(file_path):
        return False, f"File '{filename}' does not exist"
    
    try:
        os.remove(file_path)
        return True, f"File '{filename}' deleted successfully"
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"

def render_document_manager():
    """Render the document manager UI component"""
    st.header("Document Management")
    
    # Get list of subjects
    subjects = get_subjects()
    
    # Create new subject input
    with st.expander("Create New Subject"):
        new_subject = st.text_input("Subject Name")
        if st.button("Create Subject"):
            success, message = create_subject(new_subject)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    if not subjects:
        st.info("No subjects found. Create a subject to get started.")
        return
    
    # Subject selection
    selected_subject = st.selectbox("Selecckonar asignatura", subjects)
    
    # Category tabs
    categories = get_categories()
    selected_category = st.radio("Category", categories, horizontal=True)
    
    # Display files in the selected category
    st.subheader(f"Files in {selected_subject}/{selected_category}")
    
    # Get files in the selected category
    files_df = get_files(selected_subject, selected_category)
    
    if files_df.empty:
        st.info(f"No files found in {selected_subject}/{selected_category}")
    else:
        # Display files
        st.dataframe(files_df, index=False)
        
        # File operations
        col1, col2 = st.columns(2)
        
        with col1:
            if not files_df.empty:
                selected_file = st.selectbox("Select File", files_df['filename'].tolist())
                
                if st.button("View File"):
                    content = get_file_content(selected_subject, selected_category, selected_file)
                    if content is not None:
                        st.text_area("File Content", value=content, height=300, key="view_content")
                
                if st.button("Delete File"):
                    success, message = delete_file(selected_subject, selected_category, selected_file)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with col2:
            st.subheader("Add/Edit File")
            new_filename = st.text_input("Filename")
            new_content = st.text_area("Content", height=200)
            
            if st.button("Save File"):
                if new_filename:
                    success, message = save_file(selected_subject, selected_category, new_filename, new_content)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Filename cannot be empty")
    
    # Option to delete the subject
    if st.button("Delete Subject", type="primary", help="This will delete the subject and all its contents"):
        success, message = delete_subject(selected_subject)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

def get_documents_dataframe(course_id):
    """
    Get documents as a DataFrame for integration with existing code.
    This function can be called from your main application.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Query to get documents with their categories
    query = """
    SELECT d.id, d.title, d.created_at, d.indexed, c.name as category
    FROM documents d
    JOIN categories c ON d.category_id = c.id
    WHERE c.course_id = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(course_id,))
    conn.close()
    
    if not df.empty:
        df.set_index('id', inplace=True)
    
    return df

def mark_document_as_indexed(doc_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET indexed = 1 WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
