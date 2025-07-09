import os
import streamlit as st
from typing import Optional

class ConfigManager:
    """Manages configuration settings for the Streamlit app"""
    
    @staticmethod
    def get_rag_endpoint() -> str:
        """Get the RAG system endpoint URL"""
        # First check if it's set in session state (user configured)
        if 'rag_endpoint_url' in st.session_state:
            return st.session_state.rag_endpoint_url
        
        # Then check environment variable
        env_url = os.getenv("RAG_API_URL")
        if env_url:
            return env_url
        
        # Default fallback
        return "http://localhost:8000/tfm/service/getAnswer"
    
    @staticmethod
    def set_rag_endpoint(url: str):
        """Set the RAG system endpoint URL in session state"""
        st.session_state.rag_endpoint_url = url.rstrip('/')
    
    @staticmethod
    def get_api_timeout() -> int:
        """Get API timeout in seconds"""
        return int(os.getenv("API_TIMEOUT", "30"))
    
    @staticmethod
    def get_max_retries() -> int:
        """Get maximum number of retries for API calls"""
        return int(os.getenv("API_MAX_RETRIES", "3"))

def render_config_panel():
    """Render the configuration panel in the sidebar"""
    st.sidebar.header("🔧 Configuration")
    
    # RAG Endpoint Configuration
    st.sidebar.subheader("RAG System Endpoint")
    
    current_endpoint = ConfigManager.get_rag_endpoint()
    new_endpoint = st.sidebar.text_input(
        "RAG API Base URL:",
        value=current_endpoint,
        help="Enter the base URL for your RAG system API (e.g., http://localhost:8000 or https://your-api.com)"
    )
    
    if st.sidebar.button("Update Endpoint"):
        if new_endpoint:
            ConfigManager.set_rag_endpoint(new_endpoint)
            st.sidebar.success("Endpoint updated successfully!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a valid URL")
    
    # Show current configuration
    st.sidebar.info(f"**Current endpoint:** {ConfigManager.get_rag_endpoint()}")
    
    # Test connection button
    if st.sidebar.button("Test Connection"):
        # test_connection()
        pass