import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.services.conversation_service import ConversationService


class MockStreamlitSessionState:
    """Mock Streamlit session state for testing"""
    
    def __init__(self):
        self._state = {}
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __contains__(self, key):
        return key in self._state
    
    def __getattr__(self, name):
        return self._state.get(name)
    
    def __setattr__(self, name, value):
        if name == '_state':
            super().__setattr__(name, value)
        else:
            self._state[name] = value
    
    def __delitem__(self, key):
        if key in self._state:
            del self._state[key]


class TestConversationService:
    """Test suite for ConversationService"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing"""
        client = Mock()
        
        async def mock_generate(prompt, model=None):
            # Mock streaming response
            test_response = "Test response"
            for char in test_response:
                yield char
        
        client.generate = mock_generate
        return client
    
    @pytest.fixture
    def mock_st(self):
        """Mock streamlit module"""
        with patch('src.services.conversation_service.st') as mock_st:
            mock_st.session_state = MockStreamlitSessionState()
            mock_st.rerun = Mock()
            yield mock_st
    
    @pytest.fixture
    def conversation_service(self, mock_client, mock_st):
        """Create ConversationService instance for testing"""
        return ConversationService(mock_client)
    
    def test_init(self, mock_client):
        """Test ConversationService initialization"""
        service = ConversationService(mock_client)
        assert service.client == mock_client
    
    def test_should_start_ai_thinking_empty_messages(self, conversation_service, mock_st):
        """Test should_start_ai_thinking with empty messages"""
        mock_st.session_state.messages = []
        result = conversation_service.should_start_ai_thinking()
        assert result is False
    
    def test_should_start_ai_thinking_no_user_message(self, conversation_service, mock_st):
        """Test should_start_ai_thinking with no user message"""
        mock_st.session_state.messages = [{"role": "ai", "content": "Hello"}]
        result = conversation_service.should_start_ai_thinking()
        assert result is False
    
    def test_should_start_ai_thinking_already_thinking(self, conversation_service, mock_st):
        """Test should_start_ai_thinking when already thinking"""
        mock_st.session_state.messages = [{"role": "user", "content": "Hello"}]
        mock_st.session_state["ai_thinking"] = True
        result = conversation_service.should_start_ai_thinking()
        assert result is False
    
    def test_should_start_ai_thinking_valid(self, conversation_service, mock_st):
        """Test should_start_ai_thinking with valid conditions"""
        mock_st.session_state.messages = [{"role": "user", "content": "Hello"}]
        mock_st.session_state["ai_thinking"] = False
        result = conversation_service.should_start_ai_thinking()
        assert result is True
    
    def test_limit_messages_under_limit(self, conversation_service, mock_st):
        """Test limit_messages when under limit"""
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(5)]
        mock_st.session_state.messages = messages
        conversation_service.limit_messages(max_messages=10)
        assert len(mock_st.session_state.messages) == 5
    
    def test_limit_messages_over_limit(self, conversation_service, mock_st):
        """Test limit_messages when over limit"""
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(15)]
        mock_st.session_state.messages = messages
        conversation_service.limit_messages(max_messages=10)
        assert len(mock_st.session_state.messages) == 10
        # Check that it kept the last 10 messages
        assert mock_st.session_state.messages[0]["content"] == "Message 5"
        assert mock_st.session_state.messages[-1]["content"] == "Message 14"
    
    def test_handle_ai_thinking_not_thinking(self, conversation_service, mock_st):
        """Test handle_ai_thinking when not in thinking state"""
        mock_st.session_state["ai_thinking"] = False
        conversation_service.handle_ai_thinking()
        # Should not modify state
        assert not mock_st.session_state.get("streaming_started", False)
    
    def test_handle_ai_thinking_success(self, conversation_service, mock_st):
        """Test handle_ai_thinking successful execution"""
        mock_st.session_state.messages = [{"role": "user", "content": "Test message"}]
        mock_st.session_state["ai_thinking"] = True
        
        with patch.object(conversation_service, '_get_response', return_value="Test response") as mock_get_response, \
             patch.object(conversation_service, 'limit_messages') as mock_limit:
            
            conversation_service.handle_ai_thinking()
            
            # Check that response was processed correctly
            mock_get_response.assert_called_once_with("Test message")
            assert len(mock_st.session_state.messages) == 2
            assert mock_st.session_state.messages[-1]["role"] == "ai"
            assert mock_st.session_state.messages[-1]["content"] == "Test response"
            assert mock_st.session_state.get("ai_thinking") is False
            mock_limit.assert_called_once()
            mock_st.rerun.assert_called_once()
    
    def test_handle_ai_thinking_error(self, conversation_service, mock_st):
        """Test handle_ai_thinking with error"""
        mock_st.session_state.messages = [{"role": "user", "content": "Test message"}]
        mock_st.session_state["ai_thinking"] = True
        
        with patch.object(conversation_service, '_get_response', side_effect=Exception("Test error")):
            conversation_service.handle_ai_thinking()
            
            # Check that error was handled properly
            assert mock_st.session_state.get("ai_thinking") is False
            mock_st.rerun.assert_called_once()
    
    def test_get_response_success(self, conversation_service, mock_client):
        """Test _get_response successful execution"""
        user_message = "Test message"
        expected_response = "Test response"
        
        # Mock asyncio components
        with patch('asyncio.new_event_loop') as mock_new_loop, \
             patch('asyncio.set_event_loop') as mock_set_loop:
            
            mock_loop = Mock()
            mock_new_loop.return_value = mock_loop
            mock_loop.run_until_complete.return_value = expected_response
            
            result = conversation_service._get_response(user_message)
            
            assert result == expected_response
            mock_loop.close.assert_called_once()
    
    def test_get_response_error(self, conversation_service, mock_client):
        """Test _get_response with error"""
        user_message = "Test message"
        
        with patch('asyncio.new_event_loop', side_effect=Exception("Test error")):
            result = conversation_service._get_response(user_message)
            
            assert result == "Error: Test error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])