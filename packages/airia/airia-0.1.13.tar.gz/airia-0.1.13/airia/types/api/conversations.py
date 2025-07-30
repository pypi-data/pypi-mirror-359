"""
Pydantic models for conversation management API responses.

This module defines data structures for conversation operations including
creation, retrieval, and message management within the Airia platform.
"""
from typing import Optional, List, Dict
from datetime import datetime

from pydantic import BaseModel, Field


class PolicyRedaction(BaseModel):
    """
    Information about content that was redacted due to policy violations.
    
    When content in a conversation violates platform policies, this model
    tracks what was redacted and where it occurred.
    """
    violating_text: str = Field(alias="violatingText")
    violating_message_index: int = Field(alias="violatingMessageIndex")


class ConversationMessage(BaseModel):
    """
    Individual message within a conversation.
    
    Represents a single message exchange in a conversation, which can be
    from a user, assistant, or system. Messages may include text content
    and optional image attachments.
    """
    id: str
    conversation_id: str = Field(alias="conversationId")
    message: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    role: str
    images: Optional[List[str]] = None


class GetConversationResponse(BaseModel):
    """
    Complete conversation data including messages and metadata.
    
    This response contains all information about a conversation including
    its message history, associated files, execution status, and any
    content moderation actions that have been applied.
    """
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    messages: List[ConversationMessage]
    title: Optional[str] = None
    websocket_url: Optional[str] = Field(None, alias="websocketUrl")
    deployment_id: Optional[str] = Field(None, alias="deploymentId")
    data_source_files: Dict[str, List[str]] = Field(alias="dataSourceFiles")
    is_bookmarked: bool = Field(alias="isBookmarked")
    policy_redactions: Optional[Dict[str, PolicyRedaction]] = Field(
        None, alias="policyRedactions"
    )
    last_execution_status: Optional[str] = Field(None, alias="lastExecutionStatus")
    last_execution_id: Optional[str] = Field(None, alias="lastExecutionId")


class CreateConversationResponse(BaseModel):
    """
    Response data for newly created conversations.
    
    Contains the essential information needed to begin interacting with
    a new conversation, including connection details and visual metadata.
    """
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    websocket_url: str = Field(alias="websocketUrl")
    deployment_id: str = Field(alias="deploymentId")
    icon_id: Optional[str] = Field(None, alias="iconId")
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    description: Optional[str] = None
    space_name: Optional[str] = Field(None, alias="spaceName")
