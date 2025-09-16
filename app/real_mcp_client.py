"""
Real MCP Client that connects to the CrystalDBA Postgres MCP Server
This provides the actual MCP integration that mimics Claude desktop behavior
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid
import os

@dataclass
class MCPToolCall:
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class RealMCPClient:
    """
    Real MCP Client that connects to the CrystalDBA Postgres MCP Server
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.mcp_process = None
        self.available_tools = {}
        self.available_resources = {}
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        self.request_id = 0
    
    async def initialize(self) -> bool:
        """Initialize the MCP client and connect to the real MCP server"""
        try:
            # Start the real MCP server process
            self.mcp_process = await asyncio.create_subprocess_exec(
                'postgres-mcp',
                self.database_url,
                '--access-mode=restricted',  # Use restricted mode for safety
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
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
            
            # Send request and get response
            response = await self._send_request(init_request)
            if response.get("error"):
                self.logger.error(f"MCP initialization failed: {response['error']}")
                return False
            
            # Get available tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "tools/list",
                "params": {}
            }
            
            tools_response = await self._send_request(tools_request)
            if tools_response.get("result", {}).get("tools"):
                for tool in tools_response["result"]["tools"]:
                    self.available_tools[tool["name"]] = tool
            
            # Get available resources
            resources_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "resources/list",
                "params": {}
            }
            
            resources_response = await self._send_request(resources_request)
            if resources_response.get("result", {}).get("resources"):
                for resource in resources_response["result"]["resources"]:
                    self.available_resources[resource["uri"]] = resource
            
            self.initialized = True
            self.logger.info(f"Real MCP client initialized with {len(self.available_tools)} tools and {len(self.available_resources)} resources")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize real MCP client: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolCall:
        """Call a tool on the real MCP server"""
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
                "id": self._get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await self._send_request(request)
            
            if response.get("error"):
                return MCPToolCall(
                    name=tool_name,
                    arguments=arguments,
                    error=response["error"]["message"]
                )
            
            # Parse the result
            result_content = response.get("result", {}).get("content", [])
            if result_content and result_content[0].get("type") == "text":
                try:
                    result_data = json.loads(result_content[0]["text"])
                except json.JSONDecodeError:
                    result_data = {"text": result_content[0]["text"]}
                
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
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        if not self.mcp_process:
            raise Exception("MCP server not running")
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.mcp_process.stdin.write(request_json.encode())
        await self.mcp_process.stdin.drain()
        
        # Read response
        response_line = await self.mcp_process.stdout.readline()
        if not response_line:
            raise Exception("No response from MCP server")
        
        response = json.loads(response_line.decode().strip())
        return response
    
    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
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
            "initialized": self.initialized,
            "server_type": "CrystalDBA Postgres MCP Pro"
        }
    
    async def close(self):
        """Close the MCP client and server"""
        if self.mcp_process:
            self.mcp_process.terminate()
            await self.mcp_process.wait()
            self.mcp_process = None
        self.initialized = False

