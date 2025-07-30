"""
Component discovery tools: list_components, enhanced get_component_doc, preview_component.
Empowers Claude to systematically discover and use all available components.
"""

import json
import re
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Union, List, Dict, Any, Optional

from ..models import ComponentDocIn, MarkdownOut, StatusOut
from ..components import ComponentRegistry, Component
from ..config import WORKSPACES_DIR
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


# New models for component discovery
class ComponentInfo(BaseModel):
    """Information about a single component."""
    name: str = Field(..., description="Component name (e.g., 'card', 'columns')")
    category: str = Field(..., description="Component category (e.g., 'layout', 'content', 'data')")
    description: str = Field(..., description="Brief description of what the component does")
    props: List[Dict[str, str]] = Field(default_factory=list, description="List of component properties")
    usage_example: str = Field(..., description="Basic usage example in Markdown syntax")


class ListComponentsOut(BaseModel):
    """Output for list_components."""
    total_components: int
    components: List[ComponentInfo]


class PreviewComponentIn(BaseModel):
    """Input for preview_component."""
    component: str = Field(..., description="Component name to preview")
    props: Dict[str, Any] = Field(default_factory=dict, description="Component properties")
    template: str = Field("markov-pro", description="Template context for styling")


class PreviewComponentOut(BaseModel):
    """Output for preview_component."""
    success: bool
    html: str = Field(..., description="Rendered HTML of the component")
    css_classes: List[str] = Field(default_factory=list, description="CSS classes used")
    

def register_component_discovery_tools(mcp: "FastMCP") -> None:
    """Register component discovery tools with the MCP server."""
    
    @mcp.tool()
    def list_components(params: Union[dict, str] = None) -> ListComponentsOut:
        """List all available components with descriptions and usage examples."""
        registry = ComponentRegistry()
        
        # Define component metadata
        component_metadata = {
            # Layout components
            'slide-base': {
                'category': 'layout',
                'description': 'Base container for all slides with consistent padding and styling',
                'usage': 'Automatically applied to all slides'
            },
            'header': {
                'category': 'layout',
                'description': 'Consistent header with title, subtitle, and optional logo',
                'usage': '# Title\n## Subtitle'
            },
            'footer': {
                'category': 'layout',
                'description': 'Footer with slide number and optional text',
                'usage': 'Automatically added based on template settings'
            },
            'columns': {
                'category': 'layout',
                'description': 'Multi-column layout with configurable ratios',
                'usage': ':::columns ratio=7:5\n### Left Column\nContent\n\n### Right Column\nContent\n:::'
            },
            'grid': {
                'category': 'layout',
                'description': 'Grid layout for organizing multiple items',
                'usage': ':::grid cols=3 gap=6\n### Item 1\nContent\n\n### Item 2\nContent\n:::'
            },
            
            # Content components
            'card': {
                'category': 'content',
                'description': 'Highlighted content box with optional title, icon, and color',
                'usage': ':::card title="Key Point" icon=lightbulb color=blue\nImportant information here\n:::'
            },
            'callout': {
                'category': 'content',
                'description': 'Attention-grabbing box for warnings, tips, or highlights',
                'usage': ':::callout type=warning icon=exclamation-triangle\nWarning message here\n:::'
            },
            'table': {
                'category': 'content',
                'description': 'Styled table from markdown',
                'usage': '| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |'
            },
            'code': {
                'category': 'content',
                'description': 'Syntax-highlighted code block',
                'usage': '```python\ndef hello():\n    print("Hello!")\n```'
            },
            'image': {
                'category': 'content',
                'description': 'Responsive image with optional caption',
                'usage': ':::image src="path/to/image.png" alt="Description"\nOptional caption\n:::'
            },
            'speaker-notes': {
                'category': 'content',
                'description': 'Hidden notes for presenter view',
                'usage': ':::speaker-notes\nNotes that only the presenter sees\n:::'
            },
            
            # Data visualization
            'chart': {
                'category': 'data',
                'description': 'Charts and graphs (bar, line, pie)',
                'usage': ':::chart type=bar\n```json\n{\n  "labels": ["Q1", "Q2"],\n  "datasets": [{\n    "label": "Revenue",\n    "data": [100, 150]\n  }]\n}\n```\n:::'
            },
            'metrics': {
                'category': 'data',
                'description': 'Key metrics display with values and changes',
                'usage': ':::metrics\n- label: Revenue\n  value: $10M\n  change: +15%\n  trend: up\n:::'
            },
            'timeline': {
                'category': 'data',
                'description': 'Timeline visualization for events or milestones',
                'usage': ':::timeline\n- date: 2025 Q1\n  title: Launch\n  description: Product launch\n:::'
            }
        }
        
        # Build component info list
        component_infos = []
        for comp_name in registry.list_components():
            metadata = component_metadata.get(comp_name, {})
            
            # Get component instance to inspect
            component = registry.get(comp_name)
            
            # Try to extract props from render method signature
            props_list = []
            if component:
                try:
                    # Get the render method
                    render_method = getattr(component, 'render', None)
                    if render_method:
                        # Inspect the method to understand expected props
                        # This is a simplified approach - in reality, we'd parse the render method
                        if comp_name == 'columns':
                            props_list = [
                                {'name': 'ratio', 'type': 'string', 'description': 'Column width ratio (e.g., "7:5")'},
                                {'name': 'gap', 'type': 'number', 'description': 'Gap between columns'},
                                {'name': 'sections', 'type': 'array', 'description': 'Column content sections'}
                            ]
                        elif comp_name == 'card':
                            props_list = [
                                {'name': 'title', 'type': 'string', 'description': 'Card title'},
                                {'name': 'icon', 'type': 'string', 'description': 'Icon name'},
                                {'name': 'color', 'type': 'string', 'description': 'Theme color'},
                                {'name': 'content', 'type': 'string', 'description': 'Card content (alias: children)'},
                                {'name': 'children', 'type': 'string', 'description': 'Card content (alias: content)'}
                            ]
                        elif comp_name == 'chart':
                            props_list = [
                                {'name': 'type', 'type': 'string', 'description': 'Chart type: bar, line, pie, doughnut'},
                                {'name': 'data', 'type': 'object', 'description': 'Chart.js data object'},
                                {'name': 'options', 'type': 'object', 'description': 'Chart.js options'}
                            ]
                        # Add more components as needed
                except Exception:
                    pass
            
            component_infos.append(ComponentInfo(
                name=comp_name,
                category=metadata.get('category', 'general'),
                description=metadata.get('description', f'{comp_name} component'),
                props=props_list,
                usage_example=metadata.get('usage', f':::{comp_name}\nContent\n:::')
            ))
        
        # Sort by category then name
        component_infos.sort(key=lambda x: (x.category, x.name))
        
        return ListComponentsOut(
            total_components=len(component_infos),
            components=component_infos
        )
    
    @mcp.tool()
    def get_component_doc(params: Union[ComponentDocIn, str, dict]) -> MarkdownOut:
        """Get detailed documentation for a specific component from Python source."""
        # Handle parameter conversion
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
        
        # Get component from registry
        registry = ComponentRegistry()
        component_instance = registry.get(params.component)
        
        if not component_instance:
            return MarkdownOut(
                content=f"# {params.component}\n\nComponent not found.",
                title=params.component,
                examples=[]
            )
        
        # Get the component class
        component_class = component_instance.__class__
        
        # Build documentation
        md_parts = [f"# {params.component}"]
        
        # Add class docstring if available
        if component_class.__doc__:
            md_parts.append(f"\n{component_class.__doc__.strip()}")
        
        # Get the render method source
        try:
            render_source = inspect.getsource(component_class.render)
            
            # Extract props from render method
            md_parts.append("\n## Props")
            
            # Parse the render method to find props usage
            props_found = set()
            for line in render_source.split('\n'):
                # Look for props.get() calls
                prop_matches = re.findall(r"props\.get\(['\"](\w+)['\"]", line)
                props_found.update(prop_matches)
            
            if props_found:
                md_parts.append("\n| Prop | Description |")
                md_parts.append("|------|-------------|")
                
                # Add known prop descriptions
                prop_descriptions = {
                    'children': 'Content to render inside the component',
                    'content': 'Content to render (alias for children)',
                    'className': 'Additional CSS classes',
                    'title': 'Component title',
                    'subtitle': 'Component subtitle',
                    'icon': 'Icon name (FontAwesome)',
                    'color': 'Theme color (blue, green, red, etc.)',
                    'type': 'Component variant type',
                    'ratio': 'Aspect ratio or column ratio',
                    'gap': 'Spacing between elements',
                    'cols': 'Number of columns',
                    'data': 'Data object for visualization',
                    'options': 'Configuration options',
                    'sections': 'Content sections array',
                    'items': 'Array of items to display',
                }
                
                for prop in sorted(props_found):
                    desc = prop_descriptions.get(prop, f'{prop} property')
                    md_parts.append(f"| `{prop}` | {desc} |")
            
            # Add usage example
            md_parts.append("\n## Usage Example")
            
            # Get usage from list_components metadata
            component_list = list_components()
            for comp_info in component_list.components:
                if comp_info.name == params.component:
                    md_parts.append(f"\n```markdown\n{comp_info.usage_example}\n```")
                    break
            
            # Add render method source
            md_parts.append("\n## Implementation Details")
            md_parts.append("\n```python")
            md_parts.append(render_source)
            md_parts.append("```")
            
        except Exception as e:
            md_parts.append(f"\n## Error\n\nCould not extract component details: {e}")
        
        return MarkdownOut(
            content='\n'.join(md_parts),
            title=params.component,
            examples=[]
        )
    
    @mcp.tool()
    def preview_component(params: Union[PreviewComponentIn, str, dict]) -> PreviewComponentOut:
        """Preview a component in isolation with given props."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = PreviewComponentIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = PreviewComponentIn(**params)
        elif not isinstance(params, PreviewComponentIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get component from registry
        registry = ComponentRegistry()
        
        try:
            # Render the component
            html = registry.render(params.component, params.props)
            
            # Extract CSS classes used (simple regex approach)
            class_matches = re.findall(r'class="([^"]*)"', html)
            all_classes = []
            for match in class_matches:
                all_classes.extend(match.split())
            
            # Get unique classes
            unique_classes = sorted(list(set(all_classes)))
            
            return PreviewComponentOut(
                success=True,
                html=html,
                css_classes=unique_classes
            )
            
        except Exception as e:
            return PreviewComponentOut(
                success=False,
                html=f"<div class='error'>Error rendering component: {str(e)}</div>",
                css_classes=['error']
            )