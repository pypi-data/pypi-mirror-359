import os
import requests
from typing import List
import asyncio

from ephor_cli.clients.ddb.message import MessageDDBClient
from ephor_cli.constant import DYNAMODB_TABLE_NAME, API_SERVER_URL
from langchain_core.messages import BaseMessage
from langchain_core.messages.base import messages_to_dict


class MessageService:
    """Service for high-level message operations.

    This service uses the MessageDDBClient for low-level DynamoDB operations.
    """

    def __init__(
        self,
        table_name: str = DYNAMODB_TABLE_NAME,
        region: str = "us-east-1",
        trigger_update_threshold: int = 10,
    ):
        """Initialize the Message Service.

        Args:
            table_name: The name of the DynamoDB table
            region: AWS region for the DynamoDB table
        """
        self.client = MessageDDBClient(table_name, region)
        self.trigger_update_threshold = trigger_update_threshold

    def add_message(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        message: BaseMessage,
        task_id: str | None = None,
    ) -> bool:
        """Create a new message.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation the message belongs to
            message: The message data to store

        Returns:
            True if the message was created successfully, False otherwise
        """

        result = self.client.store_message(
            user_id, project_id, conversation_id, message, task_id
        )

        asyncio.create_task(
            self.handle_summary_update(user_id, project_id, conversation_id, task_id)
        )

        return result

    async def handle_summary_update(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        task_id: str | None = None,
    ):
        messages = self.get_unsummarized_messages(
            user_id, project_id, conversation_id, task_id
        )

        if len(messages) >= self.trigger_update_threshold:
            self.trigger_update_summary(
                user_id,
                project_id,
                conversation_id,
                task_id,
            )

    def list_messages(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        task_id: str | None = None,
    ) -> List[BaseMessage]:
        """Get all messages for a conversation, sorted by last_message_id chain."""
        messages = self.client.list_messages(
            user_id, project_id, conversation_id, task_id
        )
        if not messages:
            return []
        # Build id -> message and last_message_id -> message mappings
        last_id_to_msg = {}
        for m in messages:
            last_id = m.additional_kwargs.get("last_message_id")
            last_id_to_msg[last_id] = m
        # Find the head (message whose last_message_id is None or not present)
        head = None
        for m in messages:
            if m.additional_kwargs.get("last_message_id") is None:
                head = m
                break
        if head is None:
            # fallback: just return unsorted if no head found
            return messages
        # Reconstruct the chain
        ordered = [head]
        current = head
        while True:
            next_msg = last_id_to_msg.get(current.id)
            if not next_msg:
                break
            ordered.append(next_msg)
            current = next_msg
        return ordered

    def delete_message(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        message_id: str,
        task_id: str | None = None,
    ) -> bool:
        """Delete a message.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation the message belongs to
            message_id: The ID of the message to delete

        Returns:
            True if the message was deleted successfully, False otherwise
        """
        return self.client.delete_message(
            user_id, project_id, conversation_id, message_id, task_id
        )

    def delete_messages(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        task_id: str | None = None,
    ) -> bool:
        """Delete all messages for a conversation.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation to delete messages for

        Returns:
            True if all messages were deleted successfully, False otherwise
        """
        messages = self.list_messages(user_id, project_id, conversation_id, task_id)
        for message in messages:
            self.delete_message(
                user_id, project_id, conversation_id, message.id, task_id
            )
        return True

    def get_message(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        message_id: str,
        task_id: str | None = None,
    ) -> BaseMessage:
        """Get a message.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation the message belongs to
            message_id: The ID of the message to get

        Returns:
            The message
        """
        return self.client.get_message(
            user_id, project_id, conversation_id, message_id, task_id
        )

    def trigger_update_summary(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        task_id: str | None = None,
    ) -> bool:
        """Trigger an update summary by sending the last 10 messages to the summarization endpoint.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation to summarize
            task_id: Optional task ID if messages are scoped to a specific task

        Returns:
            True if the summary request was sent successfully, False otherwise
        """
        try:
            messages = self.get_unsummarized_messages(
                user_id, project_id, conversation_id, task_id
            )

            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "x-api-key": os.environ.get("EPHOR_API_KEY", ""),
            }

            # Prepare the request payload
            payload = {
                "messages": messages_to_dict(messages),  # list[dict]
            }

            # Send the request to the summarization endpoint using the space ID
            response = requests.post(
                f"{API_SERVER_URL}/projects/{project_id}/conversations/{conversation_id}/trigger-update-summary",
                json=payload,
                headers=headers,
                timeout=30,  # 30 second timeout
            )

            if response.status_code in [200, 201, 202]:
                print(
                    f"Summary update triggered successfully for conversation {conversation_id}"
                )
                for m in messages:
                    m.additional_kwargs["summarized"] = True
                    self.client.store_message(
                        user_id, project_id, conversation_id, m, task_id
                    )
                return True
            else:
                print(
                    f"Failed to trigger summary update: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            print(f"Error triggering summary update: {e}")
            return False

    def get_unsummarized_messages(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        task_id: str | None = None,
    ) -> List[BaseMessage]:
        """Get all messages for a conversation that have not been summarized."""
        messages = self.list_messages(user_id, project_id, conversation_id, task_id)
        return [m for m in messages if not m.additional_kwargs.get("summarized")]
