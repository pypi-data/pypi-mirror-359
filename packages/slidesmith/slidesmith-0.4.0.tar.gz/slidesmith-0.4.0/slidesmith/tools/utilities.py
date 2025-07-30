"""
Utility tools: get_component_doc, svg_icon, get_version.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..models import ComponentDocIn, MarkdownOut, PathOut, SvgIconIn

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_utility_tools(mcp: "FastMCP") -> None:
    """Register utility tools with the MCP server."""
    
    @mcp.tool()
    def get_version() -> dict:
        """Get the current version of Slidesmith MCP server."""
        from .. import __version__
        return {
            "version": __version__,
            "name": "slidesmith",
            "description": "MCP server for creating pixel-perfect slide decks from Markdown"
        }
    
    @mcp.tool()
    def get_component_doc(params: Union[ComponentDocIn, str, dict]) -> MarkdownOut:
        """Get documentation for a component (delegates to component_discovery module)."""
        # Import the enhanced version from component_discovery
        from .component_discovery import get_component_doc as enhanced_get_component_doc
        
        # Delegate to the enhanced implementation
        return enhanced_get_component_doc(params)
    
    @mcp.tool()
    def svg_icon(params: Union[SvgIconIn, str, dict]) -> PathOut:
        """Get SVG icon from offline collection."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = SvgIconIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = SvgIconIn(**params)
        elif not isinstance(params, SvgIconIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Load icon map and SVG paths
        # Try multiple paths to support both development and installed package
        possible_template_paths = [
            Path(__file__).parent.parent.parent / "templates" / "markov-pro",  # Development
            Path.home() / ".slidesmith" / "templates" / "markov-pro",  # Installed
        ]
        
        icon_map_path = None
        svg_paths_file = None
        for path in possible_template_paths:
            test_icon_map = path / "assets" / "icons" / "icon-map.json"
            test_svg_paths = path / "assets" / "icons" / "svg-paths.json"
            if test_icon_map.exists():
                icon_map_path = test_icon_map
                svg_paths_file = test_svg_paths
                break
        
        # Default color from params or icon map
        default_color = "#374151"
        
        # Try to find the icon
        icon_key = None
        svg_data = None
        
        # Load icon map to find the icon key
        if icon_map_path and icon_map_path.exists():
            icon_map = json.loads(icon_map_path.read_text())
            default_color = icon_map.get("colors", {}).get("default", default_color)
            
            # Try to find icon by FontAwesome class name
            fa_class = f"fas fa-{params.name}"
            if params.style == "regular":
                fa_class = f"far fa-{params.name}"
            elif params.style == "brands":
                fa_class = f"fab fa-{params.name}"
            
            icon_key = icon_map.get("icons", {}).get(fa_class)
            
            # If not found, try direct key match
            if not icon_key:
                icon_key = f"{params.name}-{params.style}"
        
        # Load SVG paths
        if icon_key and svg_paths_file.exists():
            svg_paths = json.loads(svg_paths_file.read_text())
            svg_data = svg_paths.get(icon_key)
        
        # Generate SVG content
        if svg_data:
            color = params.color or default_color
            size = params.size or 24
            viewBox = svg_data.get("viewBox", "0 0 512 512")
            path = svg_data.get("path", "")
            
            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{viewBox}" fill="{color}">
  <path d="{path}"/>
</svg>"""
        else:
            # Fallback: Create a placeholder icon
            color = params.color or default_color
            size = params.size or 24
            
            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}">
  <circle cx="12" cy="12" r="10" fill="none" stroke="{color}" stroke-width="2"/>
  <text x="12" y="17" text-anchor="middle" font-size="14" fill="{color}">?</text>
</svg>"""
        
        # Save to temp location with cache-friendly name
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "slidesmith_icons"
        temp_dir.mkdir(exist_ok=True)
        
        # Create filename based on icon parameters
        safe_name = params.name.replace("/", "_")
        safe_color = (params.color or default_color).replace("#", "")
        svg_filename = f"{safe_name}_{params.style}_{params.size}_{safe_color}.svg"
        svg_path = temp_dir / svg_filename
        
        # Only write if file doesn't exist (simple caching)
        if not svg_path.exists():
            svg_path.write_text(svg_content)
        
        return PathOut(
            path=str(svg_path),
            size_bytes=len(svg_content.encode()),
        )