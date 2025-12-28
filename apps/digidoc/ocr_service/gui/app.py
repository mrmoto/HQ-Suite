"""
Streamlit Main Application

Main entry point for the DigiDoc Streamlit GUI.
Provides multi-page navigation for queue viewing and visual matching.
"""

import streamlit as st
from ..config import get_config

# Page configuration
st.set_page_config(
    page_title="DigiDoc - OCR Review",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'config' not in st.session_state:
    try:
        st.session_state.config = get_config()
        st.session_state.config_loaded = True
    except Exception as e:
        st.session_state.config = None
        st.session_state.config_loaded = False
        st.session_state.config_error = str(e)

# Sidebar navigation
st.sidebar.title("📄 DigiDoc")
st.sidebar.markdown("---")

# Navigation - check if queue item is selected
if 'selected_queue_item_id' in st.session_state and st.session_state.selected_queue_item_id:
    # Auto-navigate to Visual Match if item is selected
    page = "Visual Match"
else:
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Queue View", "Visual Match"],
        index=0
    )

# Display config status
if not st.session_state.config_loaded:
    st.sidebar.error("⚠️ Configuration Error")
    st.sidebar.error(st.session_state.config_error)
    st.error("Failed to load configuration. Please check your `digidoc_config.yaml` file.")
    st.stop()

# Main content area
if page == "Queue View":
    from .pages import queue_view
    queue_view.render()
elif page == "Visual Match":
    from .pages import visual_match
    visual_match.render()
