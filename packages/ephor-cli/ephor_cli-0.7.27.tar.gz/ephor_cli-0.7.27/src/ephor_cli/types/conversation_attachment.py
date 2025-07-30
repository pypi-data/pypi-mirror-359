from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
import uuid


class AttachmentSource(BaseModel):
    """Model for attachment source information."""
    model_config = ConfigDict(populate_by_name=True)
    
    type: Literal['local', 'drive' , 'notion']
    file_id: Optional[str] = Field(None, alias='fileId')  # Only present when type is 'drive' | 'notion'


class ConversationAttachment(BaseModel):
    """Model for a conversation attachment."""
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    project_id: str
    conversation_id: str
    space_id: Optional[str] = None  # New field for space ID
    s3_key: str
    file_name: str
    file_type: str
    file_size: int
    is_indexed: bool = False  # Tracks whether the attachment has been indexed
    scope: Literal['space', 'project', 'global'] = 'project'  # NEW FIELD - Default: 'project'
    source: AttachmentSource  # NEW FIELD - Required
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateConversationAttachmentRequest(BaseModel):
    """Request model for creating a conversation attachment."""
    model_config = ConfigDict(populate_by_name=True)
    
    user_id: str
    project_id: str
    conversation_id: str
    space_id: Optional[str] = None  # New field for space ID
    s3_key: str
    file_name: str
    file_type: str
    file_size: int
    scope: Optional[Literal['space', 'project', 'global']] = 'project'  # NEW FIELD - Default: 'project'
    source: AttachmentSource  # NEW FIELD - Required


class CreateConversationAttachmentResponse(BaseModel):
    """Response model for creating a conversation attachment."""
    result: ConversationAttachment


class ListConversationAttachmentRequest(BaseModel):
    """Request model for listing conversation attachments."""
    user_id: str
    project_id: str
    conversation_id: str


class ListConversationAttachmentResponse(BaseModel):
    """Response model for listing conversation attachments."""
    result: List[ConversationAttachment]


class DeleteConversationAttachmentRequest(BaseModel):
    """Request model for deleting a conversation attachment."""
    user_id: str
    project_id: str
    conversation_id: str
    attachment_id: str


class DeleteConversationAttachmentResponse(BaseModel):
    """Response model for deleting a conversation attachment."""
    success: bool


class UpdateConversationAttachmentRequest(BaseModel):
    """Request model for updating a conversation attachment."""
    model_config = ConfigDict(populate_by_name=True)
    
    user_id: str
    project_id: str
    conversation_id: str
    attachment_id: str
    scope: Literal['space', 'project', 'global']  # Updated to use scope instead of isProjectScope


class UpdateConversationAttachmentResponse(BaseModel):
    """Response model for updating a conversation attachment."""
    result: ConversationAttachment


# JSON-RPC wrapper models
class ConversationAttachmentRPCRequest(BaseModel):
    """JSON-RPC request wrapper for conversation attachment operations."""
    jsonrpc: str = "2.0"
    method: str  # "create", "list", "delete", or "update"
    params: Union[CreateConversationAttachmentRequest, ListConversationAttachmentRequest, DeleteConversationAttachmentRequest, UpdateConversationAttachmentRequest]
    id: Optional[Union[str, int]] = None


class ConversationAttachmentRPCResponse(BaseModel):
    """JSON-RPC response wrapper for conversation attachment operations."""
    jsonrpc: str = "2.0"
    result: Union[ConversationAttachment, List[ConversationAttachment], bool] = None
    error: Optional[dict] = None
    id: Optional[Union[str, int]] = None 