import json
from collections.abc import AsyncGenerator, Sequence
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

from lite_agent.agent import Agent
from lite_agent.loggers import logger
from lite_agent.types import (
    AgentAssistantMessage,
    AgentChunk,
    AgentChunkType,
    AgentFunctionCallOutput,
    AgentFunctionToolCallMessage,
    AgentSystemMessage,
    AgentUserMessage,
    FlexibleRunnerMessage,
    MessageDict,
    RunnerMessage,
    ToolCall,
    ToolCallFunction,
    UserInput,
)

if TYPE_CHECKING:
    from lite_agent.types import AssistantMessage

DEFAULT_INCLUDES: tuple[AgentChunkType, ...] = (
    "completion_raw",
    "usage",
    "final_message",
    "tool_call",
    "tool_call_result",
    "content_delta",
    "tool_call_delta",
)


class Runner:
    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.messages: list[RunnerMessage] = []

    def _normalize_includes(self, includes: Sequence[AgentChunkType] | None) -> Sequence[AgentChunkType]:
        """Normalize includes parameter to default if None."""
        return includes if includes is not None else DEFAULT_INCLUDES

    def _normalize_record_path(self, record_to: PathLike | str | None) -> Path | None:
        """Normalize record_to parameter to Path object if provided."""
        return Path(record_to) if record_to else None

    async def _handle_tool_calls(self, tool_calls: "Sequence[ToolCall] | None", includes: Sequence[AgentChunkType], context: "Any | None" = None) -> AsyncGenerator[AgentChunk, None]:  # noqa: ANN401, C901, PLR0912
        """Handle tool calls and yield appropriate chunks."""
        if not tool_calls:
            return

        # Check for transfer_to_agent calls first
        transfer_calls = [tc for tc in tool_calls if tc.function.name == "transfer_to_agent"]
        if transfer_calls:
            # Handle all transfer calls but only execute the first one
            for i, tool_call in enumerate(transfer_calls):
                if i == 0:
                    # Execute the first transfer
                    await self._handle_agent_transfer(tool_call, includes)
                else:
                    # Add response for additional transfer calls without executing them
                    self.messages.append(
                        AgentFunctionCallOutput(
                            type="function_call_output",
                            call_id=tool_call.id,
                            output="Transfer already executed by previous call",
                        ),
                    )
            return  # Stop processing other tool calls after transfer

        return_parent_calls = [tc for tc in tool_calls if tc.function.name == "transfer_to_parent"]
        if return_parent_calls:
            # Handle multiple transfer_to_parent calls (only execute the first one)
            for i, tool_call in enumerate(return_parent_calls):
                if i == 0:
                    # Execute the first transfer
                    await self._handle_parent_transfer(tool_call, includes)
                else:
                    # Add response for additional transfer calls without executing them
                    self.messages.append(
                        AgentFunctionCallOutput(
                            type="function_call_output",
                            call_id=tool_call.id,
                            output="Transfer already executed by previous call",
                        ),
                    )
            return  # Stop processing other tool calls after transfer

        async for tool_call_chunk in self.agent.handle_tool_calls(tool_calls, context=context):
            if tool_call_chunk.type == "tool_call" and tool_call_chunk.type in includes:
                yield tool_call_chunk
            if tool_call_chunk.type == "tool_call_result":
                if tool_call_chunk.type in includes:
                    yield tool_call_chunk
                # Create function call output in responses format
                self.messages.append(
                    AgentFunctionCallOutput(
                        type="function_call_output",
                        call_id=tool_call_chunk.tool_call_id,
                        output=tool_call_chunk.content,
                    ),
                )

    async def _collect_all_chunks(self, stream: AsyncGenerator[AgentChunk, None]) -> list[AgentChunk]:
        """Collect all chunks from an async generator into a list."""
        return [chunk async for chunk in stream]

    def run(
        self,
        user_input: UserInput,
        max_steps: int = 20,
        includes: Sequence[AgentChunkType] | None = None,
        context: "Any | None" = None,  # noqa: ANN401
        record_to: PathLike | str | None = None,
    ) -> AsyncGenerator[AgentChunk, None]:
        """Run the agent and return a RunResponse object that can be asynchronously iterated for each chunk."""
        includes = self._normalize_includes(includes)
        if isinstance(user_input, str):
            self.messages.append(AgentUserMessage(role="user", content=user_input))
        elif isinstance(user_input, (list, tuple)):
            # Handle sequence of messages
            for message in user_input:
                self.append_message(message)
        else:
            # Handle single message (BaseModel, TypedDict, or dict)
            # Type assertion needed due to the complex union type
            self.append_message(user_input)  # type: ignore[arg-type]
        return self._run(max_steps, includes, self._normalize_record_path(record_to), context=context)

    async def _run(self, max_steps: int, includes: Sequence[AgentChunkType], record_to: Path | None = None, context: "Any | None" = None) -> AsyncGenerator[AgentChunk, None]:  # noqa: ANN401, C901
        """Run the agent and return a RunResponse object that can be asynchronously iterated for each chunk."""
        logger.debug(f"Running agent with messages: {self.messages}")
        steps = 0
        finish_reason = None

        # Determine completion condition based on agent configuration
        completion_condition = getattr(self.agent, "completion_condition", "stop")

        def is_finish() -> bool:
            if completion_condition == "call":
                function_calls = self._find_pending_function_calls()
                return any(getattr(fc, "name", None) == "wait_for_user" for fc in function_calls)
            return finish_reason == "stop"

        while not is_finish() and steps < max_steps:
            resp = await self.agent.completion(self.messages, record_to_file=record_to)
            async for chunk in resp:
                if chunk.type in includes:
                    yield chunk

                if chunk.type == "final_message":
                    message = chunk.message
                    # Convert to responses format and add to messages
                    await self._convert_final_message_to_responses_format(message)
                    finish_reason = chunk.finish_reason
                    if finish_reason == "tool_calls":
                        # Find pending function calls in responses format
                        pending_function_calls = self._find_pending_function_calls()
                        if pending_function_calls:
                            # Convert to ToolCall format for existing handler
                            tool_calls = self._convert_function_calls_to_tool_calls(pending_function_calls)
                            require_confirm_tools = await self.agent.list_require_confirm_tools(tool_calls)
                            if require_confirm_tools:
                                return
                            async for tool_chunk in self._handle_tool_calls(tool_calls, includes, context=context):
                                yield tool_chunk
            steps += 1

    async def run_continue_until_complete(
        self,
        max_steps: int = 20,
        includes: list[AgentChunkType] | None = None,
        record_to: PathLike | str | None = None,
    ) -> list[AgentChunk]:
        resp = self.run_continue_stream(max_steps, includes, record_to=record_to)
        return await self._collect_all_chunks(resp)

    def run_continue_stream(
        self,
        max_steps: int = 20,
        includes: list[AgentChunkType] | None = None,
        record_to: PathLike | str | None = None,
        context: "Any | None" = None,  # noqa: ANN401
    ) -> AsyncGenerator[AgentChunk, None]:
        return self._run_continue_stream(max_steps, includes, record_to=record_to, context=context)

    async def _run_continue_stream(
        self,
        max_steps: int = 20,
        includes: Sequence[AgentChunkType] | None = None,
        record_to: PathLike | str | None = None,
        context: "Any | None" = None,  # noqa: ANN401
    ) -> AsyncGenerator[AgentChunk, None]:
        """Continue running the agent and return a RunResponse object that can be asynchronously iterated for each chunk."""
        includes = self._normalize_includes(includes)

        # Find pending function calls in responses format
        pending_function_calls = self._find_pending_function_calls()
        if pending_function_calls:
            # Convert to ToolCall format for existing handler
            tool_calls = self._convert_function_calls_to_tool_calls(pending_function_calls)
            async for tool_chunk in self._handle_tool_calls(tool_calls, includes, context=context):
                yield tool_chunk
            async for chunk in self._run(max_steps, includes, self._normalize_record_path(record_to)):
                if chunk.type in includes:
                    yield chunk
        else:
            # Check if there are any messages and what the last message is
            if not self.messages:
                msg = "Cannot continue running without a valid last message from the assistant."
                raise ValueError(msg)

            last_message = self.messages[-1]
            if not (isinstance(last_message, AgentAssistantMessage) or (hasattr(last_message, "role") and getattr(last_message, "role", None) == "assistant")):
                msg = "Cannot continue running without a valid last message from the assistant."
                raise ValueError(msg)

            resp = self._run(max_steps=max_steps, includes=includes, record_to=self._normalize_record_path(record_to), context=context)
            async for chunk in resp:
                yield chunk

    async def run_until_complete(
        self,
        user_input: UserInput,
        max_steps: int = 20,
        includes: list[AgentChunkType] | None = None,
        record_to: PathLike | str | None = None,
    ) -> list[AgentChunk]:
        """Run the agent until it completes and return the final message."""
        resp = self.run(user_input, max_steps, includes, record_to=record_to)
        return await self._collect_all_chunks(resp)

    async def _convert_final_message_to_responses_format(self, message: "AssistantMessage") -> None:
        """Convert a completions format final message to responses format messages."""
        # The final message from the stream handler might still contain tool_calls
        # We need to convert it to responses format
        if hasattr(message, "tool_calls") and message.tool_calls:
            if message.content:
                # Add the assistant message without tool_calls
                assistant_msg = AgentAssistantMessage(
                    role="assistant",
                    content=message.content,
                )
                self.messages.append(assistant_msg)

            # Add function call messages
            for tool_call in message.tool_calls:
                function_call_msg = AgentFunctionToolCallMessage(
                    type="function_call",
                    function_call_id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments or "",
                    content="",
                )
                self.messages.append(function_call_msg)
        else:
            # Regular assistant message without tool calls
            assistant_msg = AgentAssistantMessage(
                role="assistant",
                content=message.content,
            )
            self.messages.append(assistant_msg)

    def _find_pending_function_calls(self) -> list:
        """Find function call messages that don't have corresponding outputs yet."""
        function_calls: list[AgentFunctionToolCallMessage] = []
        function_call_ids = set()

        # Collect all function call messages
        for msg in reversed(self.messages):
            if isinstance(msg, AgentFunctionToolCallMessage):
                function_calls.append(msg)
                function_call_ids.add(msg.function_call_id)
            elif isinstance(msg, AgentFunctionCallOutput):
                # Remove the corresponding function call from our list
                function_call_ids.discard(msg.call_id)
            elif isinstance(msg, AgentAssistantMessage):
                # Stop when we hit the assistant message that initiated these calls
                break

        # Return only function calls that don't have outputs yet
        return [fc for fc in function_calls if fc.function_call_id in function_call_ids]

    def _convert_function_calls_to_tool_calls(self, function_calls: list[AgentFunctionToolCallMessage]) -> list[ToolCall]:
        """Convert function call messages to ToolCall objects for compatibility."""

        tool_calls = []
        for fc in function_calls:
            tool_call = ToolCall(
                id=fc.function_call_id,
                type="function",
                function=ToolCallFunction(
                    name=fc.name,
                    arguments=fc.arguments,
                ),
                index=len(tool_calls),
            )
            tool_calls.append(tool_call)
        return tool_calls

    def set_chat_history(self, messages: Sequence[FlexibleRunnerMessage], root_agent: Agent | None = None) -> None:
        """Set the entire chat history and track the current agent based on function calls.

        This method analyzes the message history to determine which agent should be active
        based on transfer_to_agent and transfer_to_parent function calls.

        Args:
            messages: List of messages to set as the chat history
            root_agent: The root agent to use if no transfers are found. If None, uses self.agent
        """
        # Clear current messages
        self.messages.clear()

        # Set initial agent
        current_agent = root_agent if root_agent is not None else self.agent

        # Add each message and track agent transfers
        for message in messages:
            self.append_message(message)
            current_agent = self._track_agent_transfer_in_message(message, current_agent)

        # Set the current agent based on the tracked transfers
        self.agent = current_agent
        logger.info(f"Chat history set with {len(self.messages)} messages. Current agent: {self.agent.name}")

    def get_messages_dict(self) -> list[dict[str, Any]]:
        """Get the messages in JSONL format."""
        return [msg.model_dump(mode="json") for msg in self.messages]

    def _track_agent_transfer_in_message(self, message: FlexibleRunnerMessage, current_agent: Agent) -> Agent:
        """Track agent transfers in a single message.

        Args:
            message: The message to analyze for transfers
            current_agent: The currently active agent

        Returns:
            The agent that should be active after processing this message
        """
        if isinstance(message, dict):
            return self._track_transfer_from_dict_message(message, current_agent)

        if isinstance(message, AgentFunctionToolCallMessage):
            return self._track_transfer_from_function_call_message(message, current_agent)

        return current_agent

    def _track_transfer_from_dict_message(self, message: dict[str, Any] | MessageDict, current_agent: Agent) -> Agent:
        """Track transfers from dictionary-format messages."""
        message_type = message.get("type")
        if message_type != "function_call":
            return current_agent

        function_name = message.get("name", "")
        if function_name == "transfer_to_agent":
            return self._handle_transfer_to_agent_tracking(message.get("arguments", ""), current_agent)

        if function_name == "transfer_to_parent":
            return self._handle_transfer_to_parent_tracking(current_agent)

        return current_agent

    def _track_transfer_from_function_call_message(self, message: AgentFunctionToolCallMessage, current_agent: Agent) -> Agent:
        """Track transfers from AgentFunctionToolCallMessage objects."""
        if message.name == "transfer_to_agent":
            return self._handle_transfer_to_agent_tracking(message.arguments, current_agent)

        if message.name == "transfer_to_parent":
            return self._handle_transfer_to_parent_tracking(current_agent)

        return current_agent

    def _handle_transfer_to_agent_tracking(self, arguments: str | dict, current_agent: Agent) -> Agent:
        """Handle transfer_to_agent function call tracking."""
        try:
            args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments

            target_agent_name = args_dict.get("name")
            if target_agent_name:
                target_agent = self._find_agent_by_name(current_agent, target_agent_name)
                if target_agent:
                    logger.debug(f"History tracking: Transferring from {current_agent.name} to {target_agent_name}")
                    return target_agent

                logger.warning(f"Target agent '{target_agent_name}' not found in handoffs during history setup")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse transfer_to_agent arguments during history setup: {e}")

        return current_agent

    def _handle_transfer_to_parent_tracking(self, current_agent: Agent) -> Agent:
        """Handle transfer_to_parent function call tracking."""
        if current_agent.parent:
            logger.debug(f"History tracking: Transferring from {current_agent.name} back to parent {current_agent.parent.name}")
            return current_agent.parent

        logger.warning(f"Agent {current_agent.name} has no parent to transfer back to during history setup")
        return current_agent

    def _find_agent_by_name(self, root_agent: Agent, target_name: str) -> Agent | None:
        """Find an agent by name in the handoffs tree starting from root_agent.

        Args:
            root_agent: The root agent to start searching from
            target_name: The name of the agent to find

        Returns:
            The agent if found, None otherwise
        """
        # Check direct handoffs from current agent
        if root_agent.handoffs:
            for agent in root_agent.handoffs:
                if agent.name == target_name:
                    return agent

        # If not found in direct handoffs, check if we need to look in parent's handoffs
        # This handles cases where agents can transfer to siblings
        current = root_agent
        while current.parent is not None:
            current = current.parent
            if current.handoffs:
                for agent in current.handoffs:
                    if agent.name == target_name:
                        return agent

        return None

    def append_message(self, message: FlexibleRunnerMessage) -> None:
        if isinstance(message, RunnerMessage):
            self.messages.append(message)
        elif isinstance(message, dict):
            # Handle different message types
            message_type = message.get("type")
            role = message.get("role")

            if message_type == "function_call":
                # Function call message
                self.messages.append(AgentFunctionToolCallMessage.model_validate(message))
            elif message_type == "function_call_output":
                # Function call output message
                self.messages.append(AgentFunctionCallOutput.model_validate(message))
            elif role == "assistant" and "tool_calls" in message:
                # Legacy assistant message with tool_calls - convert to responses format
                # Add assistant message without tool_calls
                assistant_msg = AgentAssistantMessage(
                    role="assistant",
                    content=message.get("content", ""),
                )
                self.messages.append(assistant_msg)

                # Convert tool_calls to function call messages
                for tool_call in message.get("tool_calls", []):
                    function_call_msg = AgentFunctionToolCallMessage(
                        type="function_call",
                        function_call_id=tool_call["id"],
                        name=tool_call["function"]["name"],
                        arguments=tool_call["function"]["arguments"],
                        content="",
                    )
                    self.messages.append(function_call_msg)
            elif role:
                # Regular role-based message
                role_to_message_class = {
                    "user": AgentUserMessage,
                    "assistant": AgentAssistantMessage,
                    "system": AgentSystemMessage,
                }

                message_class = role_to_message_class.get(role)
                if message_class:
                    self.messages.append(message_class.model_validate(message))
                else:
                    msg = f"Unsupported message role: {role}"
                    raise ValueError(msg)
            else:
                msg = "Message must have a 'role' or 'type' field."
                raise ValueError(msg)

    async def _handle_agent_transfer(self, tool_call: ToolCall, _includes: Sequence[AgentChunkType]) -> None:
        """Handle agent transfer when transfer_to_agent tool is called.

        Args:
            tool_call: The transfer_to_agent tool call
            _includes: The types of chunks to include in output (unused)
        """

        # Parse the arguments to get the target agent name
        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
            target_agent_name = arguments.get("name")
        except (json.JSONDecodeError, KeyError):
            logger.error("Failed to parse transfer_to_agent arguments: %s", tool_call.function.arguments)
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output="Failed to parse transfer arguments",
                ),
            )
            return

        if not target_agent_name:
            logger.error("No target agent name provided in transfer_to_agent call")
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output="No target agent name provided",
                ),
            )
            return

        # Find the target agent in handoffs
        if not self.agent.handoffs:
            logger.error("Current agent has no handoffs configured")
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output="Current agent has no handoffs configured",
                ),
            )
            return

        target_agent = None
        for agent in self.agent.handoffs:
            if agent.name == target_agent_name:
                target_agent = agent
                break

        if not target_agent:
            logger.error("Target agent '%s' not found in handoffs", target_agent_name)
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output=f"Target agent '{target_agent_name}' not found in handoffs",
                ),
            )
            return

        # Execute the transfer tool call to get the result
        try:
            result = await self.agent.fc.call_function_async(
                tool_call.function.name,
                tool_call.function.arguments or "",
            )

            # Add the tool call result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output=str(result),
                ),
            )

            # Switch to the target agent
            logger.info("Transferring conversation from %s to %s", self.agent.name, target_agent_name)
            self.agent = target_agent

        except Exception as e:
            logger.exception("Failed to execute transfer_to_agent tool call")
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output=f"Transfer failed: {e!s}",
                ),
            )

    async def _handle_parent_transfer(self, tool_call: ToolCall, _includes: Sequence[AgentChunkType]) -> None:
        """Handle parent transfer when transfer_to_parent tool is called.

        Args:
            tool_call: The transfer_to_parent tool call
            _includes: The types of chunks to include in output (unused)
        """

        # Check if current agent has a parent
        if not self.agent.parent:
            logger.error("Current agent has no parent to transfer back to.")
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output="Current agent has no parent to transfer back to",
                ),
            )
            return

        # Execute the transfer tool call to get the result
        try:
            result = await self.agent.fc.call_function_async(
                tool_call.function.name,
                tool_call.function.arguments or "",
            )

            # Add the tool call result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output=str(result),
                ),
            )

            # Switch to the parent agent
            logger.info("Transferring conversation from %s back to parent %s", self.agent.name, self.agent.parent.name)
            self.agent = self.agent.parent

        except Exception as e:
            logger.exception("Failed to execute transfer_to_parent tool call")
            # Add error result to messages
            self.messages.append(
                AgentFunctionCallOutput(
                    type="function_call_output",
                    call_id=tool_call.id,
                    output=f"Transfer to parent failed: {e!s}",
                ),
            )
