from typing import List, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages.base import BaseMessage
from langchain_core.tools.base import BaseTool
from langchain_core.runnables import Runnable


def invoke_with_tools(model: BaseChatModel, input_messages: Sequence[BaseMessage], tools: List[BaseTool]) -> BaseMessage:
    model_with_tools: Runnable[Sequence[BaseMessage], BaseMessage] = model.bind_tools(tools)
    
    return model_with_tools.invoke(input=input_messages)
