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
        """Get documentation for a component."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ComponentDocIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ComponentDocIn(**params)
        elif not isinstance(params, ComponentDocIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Look for component documentation
        # Try multiple paths to support both development and installed package
        possible_paths = [
            Path(__file__).parent.parent.parent / "templates" / params.template,  # Development
            Path.home() / ".slidesmith" / "templates" / params.template,  # Installed
        ]
        
        component_file = None
        templates_dir = None
        for path in possible_paths:
            test_file = path / "components" / f"{params.component}.jsx"
            if test_file.exists():
                component_file = test_file
                templates_dir = path
                break
        
        if not component_file:
            return MarkdownOut(
                content=f"# {params.component}\n\nComponent not found in {params.template} template.",
                title=params.component,
                examples=[],
            )
        
        content = component_file.read_text()
        
        # Extract JSDoc comment if present
        import re
        doc_match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
        
        # Parse JSDoc content
        doc_sections = {
            'description': [],
            'params': [],
            'returns': None,
            'example': []
        }
        
        if doc_match:
            doc_text = doc_match.group(1)
            lines = [line.strip().lstrip('* ') for line in doc_text.split('\n')]
            
            current_section = 'description'
            for line in lines:
                if line.startswith('@param'):
                    current_section = 'params'
                    param_match = re.match(r'@param\s+{([^}]+)}\s+(\S+)\s*-?\s*(.*)', line)
                    if param_match:
                        param_type, param_name, param_desc = param_match.groups()
                        doc_sections['params'].append({
                            'name': param_name,
                            'type': param_type,
                            'description': param_desc
                        })
                elif line.startswith('@returns') or line.startswith('@return'):
                    current_section = 'returns'
                    doc_sections['returns'] = line.replace('@returns', '').replace('@return', '').strip()
                elif line.startswith('@example'):
                    current_section = 'example'
                elif line and current_section == 'description':
                    doc_sections['description'].append(line)
                elif line and current_section == 'example':
                    doc_sections['example'].append(line)
        
        # Build markdown documentation
        md_parts = [f"# {params.component}"]
        
        if doc_sections['description']:
            md_parts.append('\n'.join(doc_sections['description']))
        
        if doc_sections['params']:
            md_parts.append("\n## Props")
            md_parts.append("| Prop | Type | Description |")
            md_parts.append("|------|------|-------------|")
            for param in doc_sections['params']:
                md_parts.append(f"| `{param['name']}` | `{param['type']}` | {param['description']} |")
        
        # Look for example files
        examples_dir = templates_dir / "examples"
        example_files = []
        if examples_dir.exists():
            # Find examples that use this component
            for example_file in examples_dir.glob("*.mdx"):
                example_content = example_file.read_text()
                if params.component in example_content:
                    example_files.append(example_file.name)
        
        if example_files or doc_sections['example']:
            md_parts.append("\n## Examples")
            
            if doc_sections['example']:
                md_parts.append("\n### Basic Usage")
                md_parts.append("```jsx")
                md_parts.extend(doc_sections['example'])
                md_parts.append("```")
            
            if example_files:
                md_parts.append(f"\n### Example Files")
                for file in example_files[:3]:  # Limit to first 3 examples
                    md_parts.append(f"- `{file}`")
        
        # Add component source
        md_parts.append("\n## Component Source")
        md_parts.append("```jsx")
        md_parts.append(content)
        md_parts.append("```")
        
        return MarkdownOut(
            content='\n'.join(md_parts),
            title=params.component,
            examples=example_files[:3] if example_files else [],
        )
    
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