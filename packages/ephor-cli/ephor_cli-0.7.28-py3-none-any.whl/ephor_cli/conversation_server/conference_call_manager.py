import asyncio
import uuid
import os
import requests
from typing import Dict

from langchain_core.messages import HumanMessage
from langchain_core.messages.utils import messages_from_dict
from langchain_core.messages.base import messages_to_dict

from ephor_cli.utils.orchestrator_agent_config import generate_final_response
from ephor_cli.conversation_server.host_manager import ADKHostManager
from ephor_cli.services.agent import AgentService
from ephor_cli.services.message import MessageService
from ephor_cli.services.task import TaskService
from ephor_cli.types.message import (
    SendMessageParams,
    ConferenceCallTaskRequest,
    ConferenceCallTaskResponse,
    SendMessageRequest,
    SendMessageResponse,
    MessageInfo,
)
from ephor_cli.types.task import Task
from ephor_cli.utils.attachments import (
    process_attachments,
    cleanup_text_content_for_storage,
)
from ephor_cli.services.s3 import S3Service
from ephor_cli.constant import EPHOR_SERVER_URL


class ConferenceCallManager:
    def __init__(self):
        self.agent_service = AgentService()
        self.message_service = MessageService()
        self.task_service = TaskService()
        self.s3_service = S3Service()
        self.active_managers: Dict[str, ADKHostManager] = {}
        self.managers_lock = asyncio.Lock()

    async def _send_message_orchestrator_internal(
        self, request_data: SendMessageRequest
    ):
        print(f"Orchestrator: Received message: {request_data.params.message}")

        # Format the message to match LangChain's expected format
        formatted_message = {
            "type": "human",
            "data": {
                "content": request_data.params.message.get("data", {}).get(
                    "content", ""
                ),
                "additional_kwargs": request_data.params.message.get(
                    "additional_kwargs", {}
                ),
            },
        }

        message = messages_from_dict([formatted_message])[0]
        print(f"Orchestrator: Message: {message}")
        message.id = str(uuid.uuid4())

        # Process attachments if any, including conversation-level attachments
        # Use direct function call internally (no HTTP deadlock)
        # Extract space_id from message if available
        space_id = message.additional_kwargs.get("space_id")
        message = process_attachments(
            message,
            self.s3_service,
            user_id=request_data.params.user_id,
            project_id=request_data.params.project_id,
            conversation_id=request_data.params.conversation_id,
            space_id=space_id,
        )

        message = cleanup_text_content_for_storage(message)

        # Create and manage ADKHostManager instance locally for this orchestration
        orchestrator_manager = ADKHostManager(
            request_data.params.user_id,
            request_data.params.project_id,
            request_data.params.conversation_id,
            request_data.params.context,
            None,
        )

        async with self.managers_lock:
            print(f"Orchestrator: Active manager for message {message.id} set")
            self.active_managers[message.id] = orchestrator_manager

        message = orchestrator_manager.sanitize_message(message)
        self.message_service.add_message(
            request_data.params.user_id,
            request_data.params.project_id,
            request_data.params.conversation_id,
            message,
        )
        print(
            f"Orchestrator: Stored message: {self.message_service.get_message(request_data.params.user_id, request_data.params.project_id, request_data.params.conversation_id, message.id)}"
        )
        message_id = message.id

        try:
            await orchestrator_manager.process_message(message)
        finally:
            # Clean up the active manager when done
            async with self.managers_lock:
                if message_id in self.active_managers:
                    del self.active_managers[message_id]

        return SendMessageResponse(
            result=MessageInfo(
                message_id=message_id,
                conversation_id=request_data.params.conversation_id,
                project_id=request_data.params.project_id,
                user_id=request_data.params.user_id,
            )
        )

    async def handle_conference_call_task(
        self, request_data: ConferenceCallTaskRequest
    ):
        """Handle conference call"""

        try:
            params = request_data.params
            user_email = params.user_id
            conversation_id = params.conversation_id
            project_id = params.project_id
            primary_conversation_id = params.primary_conversation_id
            space_id = params.space_id
            summary = params.summary
            transcript = params.transcript

            asyncio.create_task(
                self.run_conference_call_task(
                    user_email,
                    project_id,
                    conversation_id,
                    primary_conversation_id,
                    space_id,
                    summary,
                    transcript,
                )
            )

            return ConferenceCallTaskResponse(
                user_id=user_email,
                project_id=project_id,
                conversation_id=conversation_id,
                primary_conversation_id=primary_conversation_id,
                result="success",
            )
        except Exception as e:
            return ConferenceCallTaskResponse(
                user_id=user_email,
                project_id=project_id,
                conversation_id=conversation_id,
                primary_conversation_id=primary_conversation_id,
                result=f"Error: {e}",
            )

    async def run_conference_call_task(
        self,
        user_email,
        project_id,
        conversation_id,
        primary_conversation_id,
        space_id,
        summary,
        transcript,
    ):
        agents = self.agent_service.list_agents(
            user_email, project_id, primary_conversation_id
        )

        for agent in agents:
            self.agent_service.register_agent(
                user_email, project_id, conversation_id, agent.url
            )

        print(f"Agents for {primary_conversation_id}: {agents}")

        try:
            print(
                f"Starting background processing for conference call: {conversation_id}"
            )

            context = f"Transcript: {transcript}\\nCallSummary: {summary}"
            message_content = "Refer to the transcript and call summary given to you, understand the task assigned. You should get this task done without asking any follow up questions as you cannot interact with the user directly. Your job is to get the task done by delegating it to agents."
            message = HumanMessage(content=message_content)
            message.additional_kwargs["space_id"] = space_id

            await self._send_message_orchestrator_internal(
                SendMessageRequest(
                    params=SendMessageParams(
                        user_id=user_email,
                        project_id=project_id,
                        conversation_id=conversation_id,
                        message=messages_to_dict([message])[0],
                        context=context,
                    )
                )
            )

            messages = self.message_service.list_messages(
                user_email, project_id, conversation_id
            )

            tasks = self.task_service.list_tasks(
                user_email, project_id, conversation_id, fetch_history=True
            )

            for task in tasks:
                if isinstance(task, Task):
                    history = task.history
                    for message in history:
                        messages.append(message)

            print("Conference call task processing completed.")

            final_response = generate_final_response(
                call_summary=summary,
                call_transcript=transcript,
                conversation_history=messages,
            )

            # Make HTTP call to the completion endpoint
            headers = {
                "Content-Type": "application/json",
                "x-api-key": os.environ.get("EPHOR_API_KEY", ""),
            }

            # Prepare the request payload
            payload = {
                "user_id": user_email,
                "project_id": project_id,
                "conversation_id": conversation_id,
                "primary_conversation_id": primary_conversation_id,
                "result": final_response,
            }

            # Send the request to the completion endpoint
            response = requests.post(
                f"{EPHOR_SERVER_URL}/projects/{project_id}/conversations/{conversation_id}/on-background-task-complete",
                json=payload,
                headers=headers,
                timeout=30,  # 30 second timeout
            )

            # Handle the response
            if response.status_code == 200:
                print(
                    f"Successfully notified completion for conversation {conversation_id}"
                )
            else:
                print(
                    f"Failed to notify completion for conversation {conversation_id}. Status: {response.status_code}, Response: {response.text}"
                )

        except Exception as e:
            print(
                f"Error in background processing for conference call {conversation_id}: {e}"
            )
