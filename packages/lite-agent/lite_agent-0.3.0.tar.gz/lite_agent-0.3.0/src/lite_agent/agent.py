from collections.abc import AsyncGenerator, Callable, Sequence
from pathlib import Path
from typing import Any, Optional

from funcall import Funcall
from jinja2 import Environment, FileSystemLoader
from litellm import CustomStreamWrapper
from pydantic import BaseModel

from lite_agent.client import BaseLLMClient, LiteLLMClient
from lite_agent.loggers import logger
from lite_agent.stream_handlers import litellm_stream_handler
from lite_agent.types import AgentChunk, AgentSystemMessage, RunnerMessages, ToolCall, ToolCallChunk, ToolCallResultChunk

TEMPLATES_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

HANDOFFS_SOURCE_INSTRUCTIONS_TEMPLATE = jinja_env.get_template("handoffs_source_instructions.xml.j2")
HANDOFFS_TARGET_INSTRUCTIONS_TEMPLATE = jinja_env.get_template("handoffs_target_instructions.xml.j2")
WAIT_FOR_USER_INSTRUCTIONS_TEMPLATE = jinja_env.get_template("wait_for_user_instructions.xml.j2")


class Agent:
    def __init__(  # noqa: PLR0913
        self,
        *,
        model: str | BaseLLMClient,
        name: str,
        instructions: str,
        tools: list[Callable] | None = None,
        handoffs: list["Agent"] | None = None,
        message_transfer: Callable[[RunnerMessages], RunnerMessages] | None = None,
        completion_condition: str = "stop",
    ) -> None:
        self.name = name
        self.instructions = instructions
        if isinstance(model, BaseLLMClient):
            # If model is a BaseLLMClient instance, use it directly
            self.client = model
        else:
            # Otherwise, create a LitellmClient instance
            self.client = LiteLLMClient(model=model)
        self.completion_condition = completion_condition
        self.handoffs = handoffs if handoffs else []
        self._parent: Agent | None = None
        self.message_transfer = message_transfer
        # Initialize Funcall with regular tools
        self.fc = Funcall(tools)

        # Add wait_for_user tool if completion condition is "call"
        if completion_condition == "call":
            self._add_wait_for_user_tool()

        # Set parent for handoff agents
        if handoffs:
            for handoff_agent in handoffs:
                handoff_agent.parent = self
            self._add_transfer_tools(handoffs)

        # Add transfer_to_parent tool if this agent has a parent (for cases where parent is set externally)
        if self.parent is not None:
            self.add_transfer_to_parent_tool()

    @property
    def parent(self) -> Optional["Agent"]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Agent"]) -> None:
        self._parent = value
        if value is not None:
            self.add_transfer_to_parent_tool()

    def _add_transfer_tools(self, handoffs: list["Agent"]) -> None:
        """Add transfer function for handoff agents using dynamic tools.

        Creates a single 'transfer_to_agent' function that accepts a 'name' parameter
        to specify which agent to transfer the conversation to.

        Args:
            handoffs: List of Agent objects that can be transferred to
        """
        # Collect all agent names for validation
        agent_names = [agent.name for agent in handoffs]

        def transfer_handler(name: str) -> str:
            """Handler for transfer_to_agent function."""
            if name in agent_names:
                return f"Transferring to agent: {name}"

            available_agents = ", ".join(agent_names)
            return f"Agent '{name}' not found. Available agents: {available_agents}"

        # Add single dynamic tool for all transfers
        self.fc.add_dynamic_tool(
            name="transfer_to_agent",
            description="Transfer conversation to another agent.",
            parameters={
                "name": {
                    "type": "string",
                    "description": "The name of the agent to transfer to",
                    "enum": agent_names,
                },
            },
            required=["name"],
            handler=transfer_handler,
        )

    def add_transfer_to_parent_tool(self) -> None:
        """Add transfer_to_parent function for agents that have a parent.

        This tool allows the agent to transfer back to its parent when:
        - The current task is completed
        - The agent cannot solve the current problem
        - Escalation to a higher level is needed
        """

        def transfer_to_parent_handler() -> str:
            """Handler for transfer_to_parent function."""
            if self.parent:
                return f"Transferring back to parent agent: {self.parent.name}"
            return "No parent agent found"

        # Add dynamic tool for parent transfer
        self.fc.add_dynamic_tool(
            name="transfer_to_parent",
            description="Transfer conversation back to parent agent when current task is completed or cannot be solved by current agent",
            parameters={},
            required=[],
            handler=transfer_to_parent_handler,
        )

    def add_handoff(self, agent: "Agent") -> None:
        """Add a handoff agent after initialization.

        This method allows adding handoff agents dynamically after the agent
        has been constructed. It properly sets up parent-child relationships
        and updates the transfer tools.

        Args:
            agent: The agent to add as a handoff target
        """
        # Add to handoffs list if not already present
        if agent not in self.handoffs:
            self.handoffs.append(agent)

            # Set parent relationship
            agent.parent = self

            # Add transfer_to_parent tool to the handoff agent
            agent.add_transfer_to_parent_tool()

            # Remove existing transfer tool if it exists and recreate with all agents
            try:
                # Try to remove the existing transfer tool
                if hasattr(self.fc, "remove_dynamic_tool"):
                    self.fc.remove_dynamic_tool("transfer_to_agent")
            except Exception as e:
                # If removal fails, log and continue anyway
                logger.debug(f"Failed to remove existing transfer tool: {e}")

            # Regenerate transfer tools to include the new agent
            self._add_transfer_tools(self.handoffs)

    def prepare_completion_messages(self, messages: RunnerMessages) -> list[dict[str, str]]:
        # Convert from responses format to completions format
        converted_messages = self._convert_responses_to_completions_format(messages)

        # Prepare instructions with handoff-specific additions
        instructions = self.instructions

        # Add source instructions if this agent can handoff to others
        if self.handoffs:
            instructions = HANDOFFS_SOURCE_INSTRUCTIONS_TEMPLATE.render(extra_instructions=None) + "\n\n" + instructions

        # Add target instructions if this agent can be handed off to (has a parent)
        if self.parent:
            instructions = HANDOFFS_TARGET_INSTRUCTIONS_TEMPLATE.render(extra_instructions=None) + "\n\n" + instructions

        # Add wait_for_user instructions if completion condition is "call"
        if self.completion_condition == "call":
            instructions = WAIT_FOR_USER_INSTRUCTIONS_TEMPLATE.render(extra_instructions=None) + "\n\n" + instructions

        return [
            AgentSystemMessage(
                role="system",
                content=f"You are {self.name}. {instructions}",
            ).model_dump(),
            *converted_messages,
        ]

    async def completion(self, messages: RunnerMessages, record_to_file: Path | None = None) -> AsyncGenerator[AgentChunk, None]:
        # Apply message transfer callback if provided
        processed_messages = messages
        if self.message_transfer:
            logger.debug(f"Applying message transfer callback for agent {self.name}")
            processed_messages = self.message_transfer(messages)

        self.message_histories = self.prepare_completion_messages(processed_messages)
        tools = self.fc.get_tools(target="completion")
        resp = await self.client.completion(
            messages=self.message_histories,
            tools=tools,
            tool_choice="auto",  # TODO: make this configurable
        )

        # Ensure resp is a CustomStreamWrapper
        if isinstance(resp, CustomStreamWrapper):
            return litellm_stream_handler(resp, record_to=record_to_file)
        msg = "Response is not a CustomStreamWrapper, cannot stream chunks."
        raise TypeError(msg)

    async def list_require_confirm_tools(self, tool_calls: Sequence[ToolCall] | None) -> Sequence[ToolCall]:
        if not tool_calls:
            return []
        results = []
        for tool_call in tool_calls:
            tool_func = self.fc.function_registry.get(tool_call.function.name)
            if not tool_func:
                logger.warning("Tool function %s not found in registry", tool_call.function.name)
                continue
            tool_meta = self.fc.get_tool_meta(tool_call.function.name)
            if tool_meta["require_confirm"]:
                logger.debug('Tool call "%s" requires confirmation', tool_call.id)
                results.append(tool_call)
        return results

    async def handle_tool_calls(self, tool_calls: Sequence[ToolCall] | None, context: Any | None = None) -> AsyncGenerator[ToolCallChunk | ToolCallResultChunk, None]:  # noqa: ANN401
        if not tool_calls:
            return
        if tool_calls:
            for tool_call in tool_calls:
                tool_func = self.fc.function_registry.get(tool_call.function.name)
                if not tool_func:
                    logger.warning("Tool function %s not found in registry", tool_call.function.name)
                    continue

            for tool_call in tool_calls:
                try:
                    yield ToolCallChunk(
                        type="tool_call",
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments or "",
                    )
                    content = await self.fc.call_function_async(tool_call.function.name, tool_call.function.arguments or "", context)
                    yield ToolCallResultChunk(
                        type="tool_call_result",
                        tool_call_id=tool_call.id,
                        name=tool_call.function.name,
                        content=str(content),
                    )
                except Exception as e:  # noqa: PERF203
                    logger.exception("Tool call %s failed", tool_call.id)
                    yield ToolCallResultChunk(
                        type="tool_call_result",
                        tool_call_id=tool_call.id,
                        name=tool_call.function.name,
                        content=str(e),
                    )

    def _convert_responses_to_completions_format(self, messages: RunnerMessages) -> list[dict]:
        """Convert messages from responses API format to completions API format."""
        converted_messages = []
        i = 0

        while i < len(messages):
            message = messages[i]
            message_dict = message.model_dump() if isinstance(message, BaseModel) else message

            message_type = message_dict.get("type")
            role = message_dict.get("role")

            if role == "assistant":
                # Look ahead for function_call messages
                tool_calls = []
                j = i + 1

                while j < len(messages):
                    next_message = messages[j]
                    next_dict = next_message.model_dump() if isinstance(next_message, BaseModel) else next_message

                    if next_dict.get("type") == "function_call":
                        tool_call = {
                            "id": next_dict["function_call_id"],  # type: ignore
                            "type": "function",
                            "function": {
                                "name": next_dict["name"],  # type: ignore
                                "arguments": next_dict["arguments"],  # type: ignore
                            },
                            "index": len(tool_calls),
                        }
                        tool_calls.append(tool_call)
                        j += 1
                    else:
                        break

                # Create assistant message with tool_calls if any
                assistant_msg = message_dict.copy()
                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls  # type: ignore

                converted_messages.append(assistant_msg)
                i = j  # Skip the function_call messages we've processed

            elif message_type == "function_call_output":
                # Convert to tool message
                converted_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": message_dict["call_id"],  # type: ignore
                        "content": message_dict["output"],  # type: ignore
                    },
                )
                i += 1

            elif message_type == "function_call":
                # This should have been processed with the assistant message
                # Skip it if we encounter it standalone
                i += 1

            else:
                # Regular message (user, system)
                converted_msg = message_dict.copy()

                # Handle new Response API format for user messages
                content = message_dict.get("content")
                if role == "user" and isinstance(content, list):
                    converted_msg["content"] = self._convert_user_content_to_completions_format(content)  # type: ignore

                converted_messages.append(converted_msg)
                i += 1

        return converted_messages

    def _convert_user_content_to_completions_format(self, content: list) -> list:
        """Convert user message content from Response API format to Completion API format."""
        # Handle the case where content might not actually be a list due to test mocking
        if type(content) is not list:  # Use type() instead of isinstance() to avoid test mocking issues
            return content

        converted_content = []
        for item in content:
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "input_text":
                    # Convert ResponseInputText to completion API format
                    converted_content.append(
                        {
                            "type": "text",
                            "text": item["text"],
                        },
                    )
                elif item_type == "input_image":
                    # Convert ResponseInputImage to completion API format
                    if item.get("file_id"):
                        msg = "File ID input is not supported for Completion API. Please use image_url instead of file_id for image input."
                        raise ValueError(msg)

                    if not item.get("image_url"):
                        msg = "ResponseInputImage must have either file_id or image_url, but image_url is required for Completion API."
                        raise ValueError(msg)

                    # Build image_url object with detail inside
                    image_data = {"url": item["image_url"]}
                    detail = item.get("detail", "auto")
                    if detail:  # Include detail if provided
                        image_data["detail"] = detail

                    converted_content.append(
                        {
                            "type": "image_url",
                            "image_url": image_data,
                        },
                    )
                else:
                    # Keep existing format (text, image_url)
                    converted_content.append(item)
            else:
                # Handle non-dict items (shouldn't happen, but just in case)
                converted_content.append(item)

        return converted_content

    def set_message_transfer(self, message_transfer: Callable[[RunnerMessages], RunnerMessages] | None) -> None:
        """Set or update the message transfer callback function.

        Args:
            message_transfer: A callback function that takes RunnerMessages as input
                             and returns RunnerMessages as output. This function will be
                             called before making API calls to allow preprocessing of messages.
        """
        self.message_transfer = message_transfer

    def _add_wait_for_user_tool(self) -> None:
        """Add wait_for_user tool for agents with completion_condition='call'.

        This tool allows the agent to signal when it has completed its task.
        """

        def wait_for_user_handler() -> str:
            """Handler for wait_for_user function."""
            return "Waiting for user input."

        # Add dynamic tool for task completion
        self.fc.add_dynamic_tool(
            name="wait_for_user",
            description="Call this function when you have completed your assigned task or need more information from the user.",
            parameters={},
            required=[],
            handler=wait_for_user_handler,
        )
