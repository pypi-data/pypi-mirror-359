"""
Wraps one to many MCP servers around a langchain BaseChatModel
"""
import asyncio
import logging
from typing import List, Dict, Optional, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools.base import BaseTool
from langchain_core.messages.tool import ToolCall, ToolMessage
from langchain_core.messages.base import BaseMessage
from langchain_core.messages.ai import AIMessage

from mcpwrap.server_stub import ServerSession, McpTool
from mcpwrap.llm_integration import convert_tool_to_langchain_tool


logger = logging.getLogger(__name__)


class MultiMcpModel:
    
    def __init__(
        self, 
        base_model: BaseChatModel,
        mcp_servers: List[ServerSession]
    ):
        self.chat_model: BaseChatModel = base_model
        self.tool_enable_chat_model: Optional[BaseChatModel] = None
        
        self.mcp_servers: List[ServerSession] = mcp_servers
        self.tool_name_server_mapping: Dict[str, ServerSession] = {}
        
        
        if len(mcp_servers) == 0:
            raise ValueError("Please supply at least one MCP ServerSession")
    
    async def initialize(self):
        all_mcp_tools: List[McpTool] = []
        
        for srv in self.mcp_servers:
            srv_tools = await srv.list_tools()
            
            for tool in srv_tools:
                existing_server_with_tool = self.tool_name_server_mapping.get(tool.name, None)
                if existing_server_with_tool is not None:
                    raise ValueError(
                        f"Duplicate definition for tool '{tool.name}'. Server '{existing_server_with_tool.name}' defined the tool and server '{srv.name}' tried to define it again."
                    )
                self.tool_name_server_mapping[tool.name] = srv
                all_mcp_tools.append(tool)
        
        all_langchain_tools = [convert_tool_to_langchain_tool(t) for t in all_mcp_tools]
        
        self.tool_enable_chat_model = self.chat_model.bind_tools(all_langchain_tools)

    async def process_tool_call(self, tool_call: ToolCall) -> List[ToolMessage]:
        """
        Method to process tool calls and return the messages produced by the tool
        """
        tool_name = tool_call["name"]
        
        mcp_server = self.tool_name_server_mapping.get(tool_name, None)
        
        if mcp_server is None:
            raise ValueError(f"Could not find tool '{tool_name}' in my records")
        
        return await mcp_server.process_langchain_tool_call(tool_call)

    async def process_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolMessage]:
        """
        Method to process a batch of tool calls
        """
        all_calls = [self.process_tool_call(tc) for tc in tool_calls]
        
        tool_messages_bundle = await asyncio.gather(*all_calls)
        
        compiled_list = []
        
        for tool_messages in tool_messages_bundle:
            compiled_list += tool_messages
        
        return compiled_list

    async def ainvoke(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Takes in a Chat history in the langchain format and produces one to many new messages
        using the underlying model and optionally MCP tools
        """
        all_results = []
        
        result = await self.tool_enable_chat_model.ainvoke(messages)
        
        all_results.append(result)
        
        if type(result) == AIMessage:
            additional_messages = await self.process_tool_calls(result.tool_calls)
            all_results += additional_messages
        
        return all_results
