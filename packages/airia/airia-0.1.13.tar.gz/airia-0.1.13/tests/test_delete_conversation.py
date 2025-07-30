import pytest
from unittest.mock import Mock, patch
from airia.client.sync_client import AiriaClient
from airia.client.async_client import AiriaAsyncClient
from airia.exceptions import AiriaAPIError


class TestDeleteConversation:
    """Test suite for conversation deletion functionality."""

    def test_delete_conversation_success(self):
        """Test successful conversation deletion."""
        client = AiriaClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            # Should not raise an exception
            client.delete_conversation("test_conversation_id")
            
            # Verify the request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "DELETE"
            
            # Verify the URL is correct
            request_data = call_args[0][1]
            assert "/v1/Conversations/test_conversation_id" in request_data.url

    def test_delete_conversation_with_correlation_id(self):
        """Test conversation deletion with correlation ID."""
        client = AiriaClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            client.delete_conversation("test_conversation_id", correlation_id="test_correlation")
            
            # Verify correlation ID is included in headers
            request_data = mock_request.call_args[0][1]
            assert request_data.headers["X-Correlation-ID"] == "test_correlation"

    def test_delete_conversation_not_found(self):
        """Test handling of non-existent conversation."""
        client = AiriaClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = AiriaAPIError(404, "Conversation not found")
            
            with pytest.raises(AiriaAPIError) as exc_info:
                client.delete_conversation("nonexistent_id")
            
            assert exc_info.value.status_code == 404

    def test_delete_conversation_bearer_token(self):
        """Test conversation deletion with bearer token authentication."""
        client = AiriaClient(bearer_token="test_bearer_token")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            client.delete_conversation("test_conversation_id")
            
            # Verify bearer token is used in authorization header
            request_data = mock_request.call_args[0][1]
            assert request_data.headers["Authorization"] == "Bearer test_bearer_token"
            assert "X-API-KEY" not in request_data.headers


class TestDeleteConversationAsync:
    """Test suite for async conversation deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_conversation_success_async(self):
        """Test successful async conversation deletion."""
        client = AiriaAsyncClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            # Should not raise an exception
            await client.delete_conversation("test_conversation_id")
            
            # Verify the request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "DELETE"
            
            # Verify the URL is correct
            request_data = call_args[0][1]
            assert "/v1/Conversations/test_conversation_id" in request_data.url

    @pytest.mark.asyncio
    async def test_delete_conversation_with_correlation_id_async(self):
        """Test async conversation deletion with correlation ID."""
        client = AiriaAsyncClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            await client.delete_conversation("test_conversation_id", correlation_id="test_correlation")
            
            # Verify correlation ID is included in headers
            request_data = mock_request.call_args[0][1]
            assert request_data.headers["X-Correlation-ID"] == "test_correlation"

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found_async(self):
        """Test handling of non-existent conversation in async client."""
        client = AiriaAsyncClient(api_key="test_key")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = AiriaAPIError(404, "Conversation not found")
            
            with pytest.raises(AiriaAPIError) as exc_info:
                await client.delete_conversation("nonexistent_id")
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_conversation_bearer_token_async(self):
        """Test async conversation deletion with bearer token authentication."""
        client = AiriaAsyncClient(bearer_token="test_bearer_token")
        
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = None
            
            await client.delete_conversation("test_conversation_id")
            
            # Verify bearer token is used in authorization header
            request_data = mock_request.call_args[0][1]
            assert request_data.headers["Authorization"] == "Bearer test_bearer_token"
            assert "X-API-KEY" not in request_data.headers