"""
MCP tools for Slidesmith.

This package contains all the tool implementations for the MCP server.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

# Import all tool registration functions
from .deck_management import register_deck_management_tools
from .slide_management import register_slide_management_tools
from .component_discovery import register_component_discovery_tools
from .template_config import register_template_config_tools
from .dynamic_content import register_dynamic_content_tools
from .theming import register_theming_tools
from .build import register_build_tools
from .quality import register_quality_tools
from .export import register_export_tools
from .utilities import register_utility_tools


def register_all_tools(mcp: "FastMCP") -> None:
    """
    Register all Slidesmith tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance
    """
    # Register tools by category
    register_deck_management_tools(mcp)
    register_slide_management_tools(mcp)
    register_component_discovery_tools(mcp)
    register_template_config_tools(mcp)
    register_dynamic_content_tools(mcp)
    register_theming_tools(mcp)
    register_build_tools(mcp)
    register_quality_tools(mcp)
    register_export_tools(mcp)
    register_utility_tools(mcp)


__all__ = [
    "register_all_tools",
    "register_deck_management_tools",
    "register_slide_management_tools",
    "register_component_discovery_tools",
    "register_template_config_tools",
    "register_dynamic_content_tools",
    "register_theming_tools",
    "register_build_tools",
    "register_quality_tools",
    "register_export_tools",
    "register_utility_tools",
]