"""MCP (Model Context Protocol) server management"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server"""
    name: str
    type: str = "builtin"  # builtin, custom, remote
    url: Optional[str] = None
    api_key: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MCPManager:
    """Manages MCP server connections"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".mission_control" / "mcp_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.servers: Dict[str, MCPServerConfig] = {}
        self.connected_servers: Dict[str, Any] = {}
        
        # Load existing configuration
        self._load_config()
        
        # Initialize builtin servers
        self._init_builtin_servers()
    
    def _init_builtin_servers(self):
        """Initialize builtin MCP servers"""
        builtin_servers = [
            MCPServerConfig(
                name="github",
                type="builtin",
                capabilities=["repository", "issues", "pull_requests"],
                metadata={"description": "GitHub integration for repository management"}
            ),
            MCPServerConfig(
                name="filesystem",
                type="builtin",
                capabilities=["read", "write", "search"],
                metadata={"description": "Local filesystem access"}
            ),
            MCPServerConfig(
                name="web",
                type="builtin",
                capabilities=["browse", "search", "scrape"],
                metadata={"description": "Web browsing and search capabilities"}
            ),
            MCPServerConfig(
                name="database",
                type="builtin",
                capabilities=["query", "schema", "migrate"],
                metadata={"description": "Database operations"}
            ),
            MCPServerConfig(
                name="docker",
                type="builtin",
                capabilities=["containers", "images", "compose"],
                metadata={"description": "Docker container management"}
            ),
            MCPServerConfig(
                name="kubernetes",
                type="builtin",
                capabilities=["pods", "services", "deployments"],
                metadata={"description": "Kubernetes cluster management"}
            )
        ]
        
        for server in builtin_servers:
            if server.name not in self.servers:
                self.servers[server.name] = server
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                    for name, config in data.get("servers", {}).items():
                        self.servers[name] = MCPServerConfig(**config)
                    
                    # Load connection state
                    for name in data.get("connected", []):
                        if name in self.servers:
                            self.connected_servers[name] = {"status": "loaded"}
                            
                logger.info(f"Loaded MCP configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load MCP config: {str(e)}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            data = {
                "servers": {
                    name: server.model_dump()
                    for name, server in self.servers.items()
                    if server.type != "builtin"
                },
                "connected": list(self.connected_servers.keys())
            }
            
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved MCP configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save MCP config: {str(e)}")
    
    def list_available_servers(self) -> List[Dict[str, Any]]:
        """List all available MCP servers"""
        servers = []
        
        for name, config in self.servers.items():
            servers.append({
                "name": name,
                "type": config.type,
                "description": config.metadata.get("description", ""),
                "capabilities": config.capabilities,
                "connected": name in self.connected_servers
            })
        
        return sorted(servers, key=lambda x: (x["type"], x["name"]))
    
    def connect_server(self, server_name: str, config_file: Optional[Path] = None):
        """Connect to an MCP server"""
        if server_name in self.connected_servers:
            raise ValueError(f"Server {server_name} is already connected")
        
        # Handle custom server with config file
        if config_file and config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)
                server_config = MCPServerConfig(
                    name=server_name,
                    type="custom",
                    **config_data
                )
                self.servers[server_name] = server_config
        
        if server_name not in self.servers:
            raise ValueError(f"Unknown server: {server_name}")
        
        server_config = self.servers[server_name]
        
        # Simulate connection (in real implementation, this would establish actual connection)
        logger.info(f"Connecting to MCP server: {server_name}")
        
        # For builtin servers, we can directly "connect"
        if server_config.type == "builtin":
            self.connected_servers[server_name] = {
                "status": "connected",
                "capabilities": server_config.capabilities
            }
        else:
            # For custom/remote servers, would need actual connection logic
            # This is a placeholder
            self.connected_servers[server_name] = {
                "status": "connected",
                "capabilities": server_config.capabilities,
                "url": server_config.url
            }
        
        self._save_config()
        logger.info(f"Successfully connected to {server_name}")
    
    def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name not in self.connected_servers:
            raise ValueError(f"Server {server_name} is not connected")
        
        logger.info(f"Disconnecting from MCP server: {server_name}")
        
        # Remove from connected servers
        del self.connected_servers[server_name]
        
        # Remove custom servers from config
        if server_name in self.servers and self.servers[server_name].type == "custom":
            del self.servers[server_name]
        
        self._save_config()
        logger.info(f"Successfully disconnected from {server_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current MCP connection status"""
        return {
            "connected_count": len(self.connected_servers),
            "total_count": len(self.servers),
            "connected_servers": list(self.connected_servers.keys()),
            "available_servers": list(self.servers.keys())
        }
    
    def get_server_capabilities(self, server_name: str) -> List[str]:
        """Get capabilities of a specific server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown server: {server_name}")
        
        return self.servers[server_name].capabilities
    
    def is_connected(self, server_name: str) -> bool:
        """Check if a server is connected"""
        return server_name in self.connected_servers
    
    def get_connected_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all connected servers with their info"""
        result = {}
        
        for name, connection in self.connected_servers.items():
            if name in self.servers:
                result[name] = {
                    "config": self.servers[name].model_dump(),
                    "connection": connection
                }
        
        return result