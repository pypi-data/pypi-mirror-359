import pytest
import pytest_asyncio
from dotenv import load_dotenv

from airia import AiriaAsyncClient, AiriaClient
from airia.types.api import GetConversationResponse
from airia.exceptions import AiriaAPIError

load_dotenv(override=True)

# Test constants
TEST_USER_ID = "00996c45-1515-48cf-90e9-af54c23dc301"
INVALID_CONVERSATION_ID = "00000000-0000-0000-0000-000000000000"


# Fixtures for the sync client
@pytest.fixture
def sync_client():
    """Create a sync client with test API key."""
    return AiriaClient(log_requests=True)


# Fixtures for the async client
@pytest_asyncio.fixture
async def async_client():
    """Create an async client with test API key."""
    return AiriaAsyncClient(log_requests=True)


class TestSyncGetConversation:
    """Tests for synchronous get_conversation method."""

    def test_get_conversation_basic(self, sync_client: AiriaClient):
        """Test get_conversation with valid conversation ID."""
        convo_id = sync_client.create_conversation(user_id=TEST_USER_ID)
        response = sync_client.get_conversation(conversation_id=convo_id.conversation_id)

        # Verify response type
        assert isinstance(response, GetConversationResponse)

        # Verify required fields are present
        assert response.user_id is not None
        assert response.conversation_id == convo_id.conversation_id
        assert response.messages is not None
        assert isinstance(response.messages, list)
        assert response.data_source_files is not None
        assert isinstance(response.is_bookmarked, bool)

        sync_client.delete_conversation(convo_id.conversation_id)

    def test_get_conversation_invalid_id(self, sync_client: AiriaClient):
        """Test get_conversation with invalid conversation ID."""
        with pytest.raises(AiriaAPIError) as exc_info:
            sync_client.get_conversation(conversation_id=INVALID_CONVERSATION_ID)

        # Verify that it's a 404 error for non-existent conversation
        assert exc_info.value.status_code == 404


class TestAsyncGetConversation:
    """Tests for asynchronous get_conversation method."""

    @pytest.mark.asyncio
    async def test_get_conversation_basic(self, async_client: AiriaAsyncClient):
        """Test async get_conversation with valid conversation ID."""
        convo_id = await async_client.create_conversation(user_id=TEST_USER_ID)
        response = await async_client.get_conversation(
            conversation_id=convo_id.conversation_id
        )

        # Verify response type
        assert isinstance(response, GetConversationResponse)

        # Verify required fields are present
        assert response.user_id is not None
        assert response.conversation_id == convo_id.conversation_id
        assert response.messages is not None
        assert isinstance(response.messages, list)
        assert response.data_source_files is not None
        assert isinstance(response.is_bookmarked, bool)

        await async_client.delete_conversation(convo_id.conversation_id)

    @pytest.mark.asyncio
    async def test_get_conversation_invalid_id(self, async_client: AiriaAsyncClient):
        """Test async get_conversation with invalid conversation ID."""
        with pytest.raises(AiriaAPIError) as exc_info:
            await async_client.get_conversation(conversation_id=INVALID_CONVERSATION_ID)

        # Verify that it's a 404 error for non-existent conversation
        assert exc_info.value.status_code == 404
