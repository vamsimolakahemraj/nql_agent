"""
MCP Client for integrating with MCP servers
This provides the interface between the agentic engine and MCP servers
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid

@dataclass
class MCPToolCall:
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPClient:
    """
    MCP Client that can discover and use tools from MCP servers
    """
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.available_tools = {}
        self.available_resources = {}
        self.logger = logging.getLogger(__name__)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the MCP client and discover available tools"""
        try:
            # Initialize the MCP server
            init_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "clientInfo": {
                        "name": "nql-agentic-engine",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Get available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list",
                "params": {}
            }
            
            # Get available resources
            resources_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "resources/list",
                "params": {}
            }
            
            # Process requests
            init_response = await self.mcp_server.handle_request(init_request)
            tools_response = await self.mcp_server.handle_request(tools_request)
            resources_response = await self.mcp_server.handle_request(resources_request)
            
            if init_response.get("error"):
                self.logger.error(f"MCP initialization failed: {init_response['error']}")
                return False
            
            # Store available tools and resources
            if tools_response.get("result", {}).get("tools"):
                for tool in tools_response["result"]["tools"]:
                    self.available_tools[tool["name"]] = tool
            
            if resources_response.get("result", {}).get("resources"):
                for resource in resources_response["result"]["resources"]:
                    self.available_resources[resource["uri"]] = resource
            
            self.initialized = True
            self.logger.info(f"MCP client initialized with {len(self.available_tools)} tools and {len(self.available_resources)} resources")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolCall:
        """Call a tool on the MCP server"""
        if not self.initialized:
            await self.initialize()
        
        if tool_name not in self.available_tools:
            return MCPToolCall(
                name=tool_name,
                arguments=arguments,
                error=f"Tool '{tool_name}' not available"
            )
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self.mcp_server.handle_request(request)
            
            if response.get("error"):
                return MCPToolCall(
                    name=tool_name,
                    arguments=arguments,
                    error=response["error"]["message"]
                )
            
            # Parse the result
            result_content = response.get("result", {}).get("content", [])
            if result_content and result_content[0].get("type") == "text":
                result_data = json.loads(result_content[0]["text"])
                return MCPToolCall(
                    name=tool_name,
                    arguments=arguments,
                    result=result_data
                )
            else:
                return MCPToolCall(
                    name=tool_name,
                    arguments=arguments,
                    result=response.get("result", {})
                )
                
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            return MCPToolCall(
                name=tool_name,
                arguments=arguments,
                error=str(e)
            )
    
    async def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Read a resource from the MCP server"""
        if not self.initialized:
            await self.initialize()
        
        if uri not in self.available_resources:
            self.logger.warning(f"Resource '{uri}' not available")
            return None
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "resources/read",
                "params": {
                    "uri": uri
                }
            }
            
            response = await self.mcp_server.handle_request(request)
            
            if response.get("error"):
                self.logger.error(f"Error reading resource {uri}: {response['error']}")
                return None
            
            # Parse the result
            contents = response.get("result", {}).get("contents", [])
            if contents and contents[0].get("mimeType") == "application/json":
                return json.loads(contents[0]["text"])
            else:
                return contents[0] if contents else None
                
        except Exception as e:
            self.logger.error(f"Error reading resource {uri}: {e}")
            return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.available_tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        return self.available_tools.get(tool_name)
    
    def get_available_resources(self) -> List[str]:
        """Get list of available resource URIs"""
        return list(self.available_resources.keys())
    
    def get_resource_info(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific resource"""
        return self.available_resources.get(uri)
    
    async def discover_capabilities(self) -> Dict[str, Any]:
        """Discover all capabilities of the MCP server"""
        if not self.initialized:
            await self.initialize()
        
        return {
            "tools": {
                "count": len(self.available_tools),
                "names": list(self.available_tools.keys()),
                "details": self.available_tools
            },
            "resources": {
                "count": len(self.available_resources),
                "uris": list(self.available_resources.keys()),
                "details": self.available_resources
            },
            "initialized": self.initialized
        }

