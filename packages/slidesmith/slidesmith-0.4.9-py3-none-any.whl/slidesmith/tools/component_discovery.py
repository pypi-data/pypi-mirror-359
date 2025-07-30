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
from ..component_docs import get_component_documentation, get_all_components, component_docs
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


# New models for component discovery
class ComponentInfo(BaseModel):
    """Information about a single component."""
    name: str = Field(..., description="Component name (e.g., 'card', 'columns')")
    category: str = Field(..., description="Component category (e.g., 'layout', 'content', 'data')")
    description: str = Field(..., description="Brief description of what the component does")
    props: List[Dict[str, Any]] = Field(default_factory=list, description="List of component properties")
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
        
        # Build component info list using the comprehensive documentation
        component_infos = []
        
        # Get all documented components
        documented_components = get_all_components()
        
        # Also get components from registry to ensure we don't miss any
        registry_components = registry.list_components()
        
        # Combine both lists
        all_components = set(documented_components + registry_components)
        
        # Define categories for components not in COMPONENT_DOCS
        component_categories = {
            'slide-base': 'layout',
            'header': 'layout',
            'footer': 'layout',
            'grid': 'layout',
            'card': 'content',
            'callout': 'content',
            'table': 'content',
            'code': 'content',
            'image': 'content',
            'speaker-notes': 'content',
            'chart': 'data',
            'metrics': 'data'
        }
        
        for comp_name in all_components:
            # Get documentation from COMPONENT_DOCS if available
            doc = get_component_documentation(comp_name)
            
            # Extract props in the expected format
            props_list = []
            if doc.get('props'):
                for prop in doc['props']:
                    prop_info = {
                        'name': prop.get('name', ''),
                        'type': prop.get('type', 'string'),
                        'description': prop.get('description', '')
                    }
                    if prop.get('required'):
                        prop_info['required'] = True
                    if 'default' in prop:
                        prop_info['default'] = prop['default']
                    props_list.append(prop_info)
            
            # Determine category
            if comp_name in ['BulletList', 'CardGrid', 'CheckList']:
                category = 'content'
            elif comp_name in ['MetricSection', 'Timeline', 'BarChart', 'PieChart', 'Calculation']:
                category = 'data'
            elif comp_name in ['columns']:
                category = 'layout'
            elif comp_name in ['ImpactBox', 'CTABox']:
                category = 'highlight'
            else:
                category = component_categories.get(comp_name, 'general')
            
            # Get the appropriate example
            if 'example' in doc:
                usage_example = doc['example']
            elif 'syntax' in doc:  # For columns component
                usage_example = doc['syntax']
            else:
                usage_example = f':::{comp_name}\nContent\n:::'
            
            component_infos.append(ComponentInfo(
                name=comp_name,
                category=category,
                description=doc.get('description', f'{comp_name} component'),
                props=props_list,
                usage_example=usage_example
            ))
        
        # Sort by category then name
        component_infos.sort(key=lambda x: (x.category, x.name))
        
        return ListComponentsOut(
            total_components=len(component_infos),
            components=component_infos
        )
    
    @mcp.tool()
    def get_component_doc(params: Union[ComponentDocIn, str, dict]) -> MarkdownOut:
        """Get detailed documentation for a specific component."""
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
        
        # Check if component exists in registry
        registry = ComponentRegistry()
        component_instance = registry.get(params.component)
        
        # If component doesn't exist in registry, return not found
        if not component_instance:
            return MarkdownOut(
                content=f"# {params.component}\n\nComponent not found.",
                title=params.component,
                examples=[]
            )
        
        # Get documentation from COMPONENT_DOCS
        doc = get_component_documentation(params.component)
        
        # Build documentation
        md_parts = [f"# {params.component}"]
        
        # Add description
        md_parts.append(f"\n{doc['description']}")
        
        # Add props table
        if doc.get('props'):
            md_parts.append("\n## Props")
            md_parts.append("\n| Prop | Type | Required | Description |")
            md_parts.append("|------|------|----------|-------------|")
            
            for prop in doc['props']:
                required = "Yes" if prop.get('required', False) else "No"
                default = f" (default: {prop.get('default')})" if 'default' in prop else ""
                md_parts.append(f"| `{prop['name']}` | {prop['type']} | {required} | {prop['description']}{default} |")
        
        # Add usage example
        md_parts.append("\n## Usage Example")
        if 'example' in doc:
            md_parts.append(f"\n```markdown\n{doc['example']}\n```")
        elif 'syntax' in doc:
            md_parts.append(f"\n```markdown\n{doc['syntax']}\n```")
        
        # Add tips if available
        if doc.get('tips'):
            md_parts.append("\n## Tips")
            for tip in doc['tips']:
                md_parts.append(f"- {tip}")
        
        # Try to get additional implementation details from component
        if component_instance:
            try:
                # Get the component class
                component_class = component_instance.__class__
                
                # Add class docstring if available and not already added
                if component_class.__doc__ and component_class.__doc__.strip() not in doc['description']:
                    md_parts.append(f"\n## Additional Details\n\n{component_class.__doc__.strip()}")
                
                # Get the render method source for developers
                render_source = inspect.getsource(component_class.render)
                md_parts.append("\n## Implementation Details")
                md_parts.append("\n<details>")
                md_parts.append("<summary>Click to see render method source</summary>")
                md_parts.append("\n```python")
                md_parts.append(render_source)
                md_parts.append("```")
                md_parts.append("</details>")
                
            except Exception:
                pass  # Don't fail if we can't get source
        
        return MarkdownOut(
            content='\n'.join(md_parts),
            title=params.component,
            examples=doc.get('tips', [])  # Use tips as examples
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
    
    @mcp.tool()
    def search_components(query: str) -> Dict[str, Any]:
        """
        Search components by name, description, tags, or use cases.
        
        Args:
            query: Search query (e.g., "chart", "layout", "data visualization")
            
        Returns:
            List of matching components with relevance information
        """
        results = component_docs.search_components(query)
        
        if not results:
            # Suggest browsing by category
            categories = component_docs.get_categories()
            return {
                "query": query,
                "results": [],
                "found": 0,
                "message": f"No components found for '{query}'",
                "suggestions": [
                    "Try broader terms like 'data', 'layout', or 'content'",
                    "Browse by category: " + ", ".join(categories),
                    "Use list_components to see all available components"
                ]
            }
        
        formatted_results = []
        for doc in results:
            # Get best example for this component
            best_example = doc.examples[0] if doc.examples else None
            
            formatted_results.append({
                "name": doc.name,
                "display_name": doc.display_name,
                "description": doc.description,
                "category": doc.category,
                "tags": doc.tags,
                "use_cases": doc.use_cases[:2],  # Show first 2 use cases
                "example": {
                    "title": best_example.title if best_example else "",
                    "markdown": best_example.markdown if best_example else f":::{doc.name}\nContent\n:::"
                },
                "related_components": doc.related_components
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "found": len(results),
            "tip": "Use get_component_doc to get detailed information about any component"
        }
    
    @mcp.tool()
    def browse_components_by_category(category: str) -> Dict[str, Any]:
        """
        Browse components filtered by category.
        
        Args:
            category: Component category (content, data, layout)
            
        Returns:
            Components in the specified category with detailed information
        """
        available_categories = component_docs.get_categories()
        
        if category not in available_categories:
            return {
                "category": category,
                "found": False,
                "message": f"Category '{category}' not found.",
                "available_categories": available_categories
            }
        
        components = component_docs.get_components_by_category(category)
        
        category_descriptions = {
            "content": "Content display components for text, callouts, and information presentation",
            "data": "Data visualization and metrics components for charts and analytics", 
            "layout": "Layout and structure components for organizing and arranging content"
        }
        
        return {
            "category": category,
            "description": category_descriptions.get(category, f"Components in the {category} category"),
            "found": True,
            "components": [
                {
                    "name": doc.name,
                    "display_name": doc.display_name,
                    "description": doc.description,
                    "tags": doc.tags,
                    "quick_example": doc.examples[0].markdown if doc.examples else f":::{doc.name}\nContent\n:::",
                    "use_cases": doc.use_cases[:3],
                    "props_count": len(doc.props)
                }
                for doc in components
            ],
            "total": len(components),
            "tip": f"Use get_component_doc for detailed documentation of any {category} component"
        }
    
    @mcp.tool()
    def generate_component_showcase() -> Dict[str, Any]:
        """
        Generate a comprehensive showcase of all components with examples.
        
        Returns:
            A complete showcase including all components organized by category
        """
        categories = component_docs.get_categories()
        showcase = {
            "title": "SlideSmith Component Showcase",
            "description": "Complete guide to all available components with examples and use cases",
            "categories": {},
            "total_components": len(component_docs.list_components())
        }
        
        for category in categories:
            components = component_docs.get_components_by_category(category)
            
            category_info = {
                "name": category.title(),
                "description": {
                    "content": "Content display components for text, callouts, and information presentation",
                    "data": "Data visualization and metrics components for charts and analytics",
                    "layout": "Layout and structure components for organizing and arranging content"
                }.get(category, f"Components in the {category} category"),
                "components": []
            }
            
            for doc in components:
                component_info = {
                    "name": doc.name,
                    "display_name": doc.display_name,
                    "description": doc.description,
                    "tags": doc.tags,
                    "examples": [
                        {
                            "title": ex.title,
                            "description": ex.description,
                            "markdown": ex.markdown
                        }
                        for ex in doc.examples
                    ],
                    "use_cases": doc.use_cases,
                    "props": doc.props,
                    "related_components": doc.related_components
                }
                category_info["components"].append(component_info)
            
            showcase["categories"][category] = category_info
        
        return showcase