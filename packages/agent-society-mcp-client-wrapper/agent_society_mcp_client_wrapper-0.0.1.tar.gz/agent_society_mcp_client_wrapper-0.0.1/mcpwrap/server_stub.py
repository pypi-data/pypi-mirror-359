from typing import Any, List, Dict, Optional

import asyncio
import logging
from contextlib import AsyncExitStack
from datetime import timedelta

from mcp import ClientSession
from mcp.types import Tool as McpTool, CallToolResult as McpCallToolResult, TextContent as McpTextContent
from mcp.client.sse import sse_client

from langchain_core.messages.tool import ToolCall as LangChainToolCall, ToolMessage as LangChainToolMessage


logger = logging.getLogger(__name__)

class ServerSession:
    """Represents a connection to an MCP server"""
    
    def __init__(self, name: str, url: str):
        self.exit_stack = AsyncExitStack()
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.url = url
        self.client_session: ClientSession
        self.name = name

    async def initialize(self):
        try:
            read_stream, write_stream = await self.exit_stack.enter_async_context(
                sse_client(self.url)
            )
            logger.info(f"Connected to server {self.url}")
            self.client_session = await self.exit_stack.enter_async_context(
                ClientSession(
                    read_stream=read_stream, write_stream=write_stream,
                    read_timeout_seconds=timedelta(minutes=10)
                )
            )
            logger.info("Initializing client session")
            
            await self.client_session.initialize()
            logger.info("Session initialized")
        except Exception as e:
            logger.error(f"Exception duing intialization: {e}")
            self.cleanup()
            raise e

    async def cleanup(self):
        async with self._cleanup_lock:
            await self.exit_stack.aclose()
            self.client_session = None
    
    async def list_tools(self) -> List[McpTool]:
        """List available tools from the server.

        Returns:
            A list of available tools.

        Raises:
            RuntimeError: If the server is not initialized.
        """
        if not self.client_session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.client_session.list_tools()
        
        return tools_response.tools
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        retries: int = 2,
        delay: float = 1.0,
    ) -> McpCallToolResult:
        """Execute a tool with retry mechanism.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            retries: Number of retry attempts.
            delay: Delay between retries in seconds.

        Returns:
            Tool execution result.

        Raises:
            RuntimeError: If server is not initialized.
            Exception: If tool execution fails after all retries.
        """
        if not self.client_session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                result = await self.client_session.call_tool(tool_name, arguments)

                return result

            except Exception as e:
                attempt += 1
                logging.warning(
                    f"Error executing tool: {e}. Attempt {attempt} of {retries}."
                )
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise

    async def process_langchain_tool_call(self, tool_call: LangChainToolCall) -> List[LangChainToolMessage]:
        """
        Abstraction to enable easy langchain integration
        """
        tool_name: str = tool_call["name"]
        tool_args: Dict[str, Any] = tool_call["args"]
        tool_call_id: Optional[str] = tool_call.get("id", None)
        
        result = await self.execute_tool(
            tool_name=tool_name,
            arguments=tool_args
        )
        
        result_content = result.content
        
        result_list = []
        
        message_status = "success" if not result.isError else "error"
        
        for content in result_content:
            if type(content) != McpTextContent:
                result_list.append(LangChainToolMessage(f"<WARNING> The tool returned content of type `{str(type(content))}` which is currently not supported by this library."))
            else:
                result_list.append(LangChainToolMessage(content.text, status=message_status, tool_call_id=tool_call_id))
        
        return result_list
