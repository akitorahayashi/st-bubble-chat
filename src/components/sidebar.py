import streamlit as st


def render_sidebar():
    """Render sidebar with chat controls"""
    with st.sidebar:
        # Create a custom styled button with columns for spacing
        col1, col2, col3 = st.columns([1, 10, 1])
        
        with col2:
            if st.button("⟲ New Chat", help="Clear history and start a new chat", key="new_chat_btn", use_container_width=True):
                st.session_state.messages.clear()
                if "ai_thinking" in st.session_state:
                    del st.session_state.ai_thinking
                st.rerun()