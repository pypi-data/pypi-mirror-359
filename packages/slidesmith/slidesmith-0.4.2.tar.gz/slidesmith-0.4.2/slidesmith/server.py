"""
FastMCP server implementation for Slidesmith.

This module creates and configures the MCP server with all tools and resources.
"""

from typing import Any

from fastmcp import FastMCP

from . import __version__
from .tools import register_all_tools


def create_server() -> FastMCP:
    """
    Create and configure the Slidesmith MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Create FastMCP instance
    mcp = FastMCP(
        name="slidesmith",
        version=__version__,
    )
    
    # Register all tools
    register_all_tools(mcp)
    
    # TODO: Register template resources when FastMCP resource API is clarified
    # FastMCP 2.9.2 has a different resource registration API than expected
    # Will revisit this in a future phase
    
    return mcp


def run_server(
    server: FastMCP,
    transport: str = "stdio",
    host: str = "localhost",
    port: int = 5858,
) -> None:
    """
    Run the MCP server with specified transport.
    
    Args:
        server: FastMCP server instance
        transport: Transport mode ("stdio" or "http")
        host: Host for HTTP transport
        port: Port for HTTP transport
    """
    if transport == "stdio":
        server.run()
    else:
        server.run(transport="http", host=host, port=port)