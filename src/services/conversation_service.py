import asyncio
import time

import streamlit as st


class ConversationService:
    def __init__(self, client):
        self.client = client

    def handle_ai_thinking(self):
        """
        Handle AI thinking state - simple version.
        """
        if st.session_state.get("ai_thinking", False):
            try:
                user_message = st.session_state.messages[-1]["content"]
                
                # Get response
                response = self._get_response(user_message)
                
                # Add response and clear thinking state
                st.session_state.messages.append({"role": "ai", "content": response})
                st.session_state.ai_thinking = False
                
                self.limit_messages()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.ai_thinking = False
                st.rerun()

    def _get_response(self, user_message):
        """
        Get complete response from client.
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def collect_response():
                chunks = []
                async for chunk in self.client.generate(user_message):
                    chunks.append(chunk)
                return ''.join(chunks)
            
            response = loop.run_until_complete(collect_response())
            loop.close()
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"

    def should_start_ai_thinking(self):
        """
        Check if AI thinking should be started.
        """
        return (
            len(st.session_state.messages) > 0
            and st.session_state.messages[-1]["role"] == "user"
            and not st.session_state.get("ai_thinking", False)
        )

    def limit_messages(self, max_messages=10):
        """
        Limit the number of messages in session state.
        """
        if len(st.session_state.messages) > max_messages:
            st.session_state.messages = st.session_state.messages[-max_messages:]
