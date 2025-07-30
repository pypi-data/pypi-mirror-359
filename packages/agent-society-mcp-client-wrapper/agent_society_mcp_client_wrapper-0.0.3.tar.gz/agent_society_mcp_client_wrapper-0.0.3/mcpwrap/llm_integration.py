from typing import Dict, Any, Union, List, Type, Set
from dataclasses import dataclass

from pydantic import BaseModel as PydanticBaseModel, create_model, Field
from mcp.types import Tool as McpTool
from langchain_core.tools import BaseTool as LangchainTool, StructuredTool

import jsonref


def convert_tool_to_langchain_tool(
    mcp_tool: McpTool
) -> LangchainTool:
    pd_rep = convert_input_schema_to_pydantic(mcp_tool.inputSchema)
    
    return StructuredTool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema=pd_rep
    )


def convert_input_schema_to_pydantic(
    input_schema: Dict[str, Any]
) -> PydanticBaseModel:
    norm_schema = normalize_schema(input_schema)
    
    return convert_json_tree(norm_schema)


def normalize_schema(json_schema: Dict[str, Any]) -> Dict[str, Any]:
    normalized_schema = jsonref.replace_refs(json_schema, merge_props=True, lazy_load=False)

    return normalized_schema


@dataclass
class StructField:
    key: str
    type: Type

# TODO: Adopt for DRAFT7
PRIMITIVES = {
    "null": None, 
    "boolean": bool, 
    "number": float, 
    "string": str, 
    "integer": int
}

TYPE_DEFAULT = {
    None: None,
    bool: False,
    float: 0.0,
    str: "",
    int: 0
}

def _is_primitive(obj_type: str) -> bool:
    return obj_type in PRIMITIVES


def convert_json_tree(schema_node: Dict[str, Any]) -> PydanticBaseModel:
    attributes: Dict[str, Any] = {}
    
    prop_node: Dict[str, Any] = schema_node["properties"]
    required_fields: Set[str] = set(schema_node["required"])
    title: str = schema_node["title"]

    for name, specs in prop_node.items():
        specs: Dict[str, Any]
        
        prop_type = specs["type"]
        is_required = name in required_fields
        
        description_val = specs.get("description", None)

        if _is_primitive(prop_type):
            datatype: Type = PRIMITIVES[prop_type]
            default_value = TYPE_DEFAULT[datatype]
            
            default_val: Any = ... if is_required else default_value
            
            attributes[name] = (
                datatype,
                Field(default=default_val, description=description_val)
            )
        else:
            if prop_type == "object":
                nested_pd = convert_json_tree(specs)
                
                if is_required:
                    field_descriptor = Field(default=..., description=description_val)
                else:
                    field_descriptor = Field(default_factory=nested_pd, description=description_val)
                
                attributes[name] = (
                    nested_pd,
                    field_descriptor
                )
            elif prop_type == "array":
                item_node = specs["items"]
                item_type = item_node["type"]
                
                if _is_primitive(item_type):
                    attributes[name] = (
                        List[PRIMITIVES[item_type]],
                        Field(default_factory=list)
                    )
                else:
                    repeated_type = convert_json_tree(item_node)
                    
                    if is_required:
                        field_descriptor = Field(default=..., description=description_val)
                    else:
                        field_descriptor = Field(default_factory=repeated_type, description=description_val)
                    
                    attributes[name] = (
                        List[repeated_type],
                        field_descriptor
                    )
    
    return create_model(
        title,
        **attributes
    )
