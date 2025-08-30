import streamlit as st
import time


class ConversationService:
    def __init__(self, client):
        self.client = client
    
    def process_ai_response(self, user_message):
        """
        Process AI response using the provided client.
        
        Args:
            user_message: The user's input message
            
        Returns:
            AI response string or fallback message
        """
        try:
            response = self.client.generate(user_message)
            
            if response:
                return response
            else:
                # Fallback for API failure
                time.sleep(1)
                return "Sorry, I can't connect to the AI service right now. Please try again later."
                
        except Exception as e:
            st.error("Failed to generate response. Please try again later.")
            # Fallback response
            return f"An error occurred. Message: {user_message}"

    def handle_ai_thinking(self):
        """
        Handle AI thinking state and process responses.
        """
        if st.session_state.get("ai_thinking", False):
            try:
                ai_response = self.process_ai_response(st.session_state.messages[-1]['content'])
                if ai_response:
                    st.session_state.messages.append({"role": "ai", "content": ai_response})
                
                st.session_state.ai_thinking = False
                
                # Limit message count
                self.limit_messages()
                st.rerun()
                
            except Exception as e:
                st.error("Failed to generate response. Please try again later.")
                st.session_state.ai_thinking = False
                st.rerun()

    def should_start_ai_thinking(self):
        """
        Check if AI thinking should be started.
        
        Returns:
            True if AI should start processing, False otherwise
        """
        return (len(st.session_state.messages) > 0 and 
                st.session_state.messages[-1]["role"] == "user" and
                not st.session_state.get("ai_thinking", False))

    def limit_messages(self, max_messages=10):
        """
        Limit the number of messages in session state.
        
        Args:
            max_messages: Maximum number of messages to keep
        """
        if len(st.session_state.messages) > max_messages:
            st.session_state.messages = st.session_state.messages[-max_messages:]