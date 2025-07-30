"""
Theming tools for SlideSmith MCP server.
Provides theme management and customization capabilities.
"""

from typing import TYPE_CHECKING, Union, Dict, Any, List
from ..models import StatusOut
from ..themes import theme_registry

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_theming_tools(mcp: "FastMCP") -> None:
    """Register theming tools with the MCP server."""
    
    @mcp.tool("list_themes")
    def list_themes() -> Dict[str, Any]:
        """
        List all available themes with their descriptions.
        
        Returns:
            Dictionary containing theme information
        """
        themes = []
        for theme_name in theme_registry.list_themes():
            theme_data = theme_registry.get_theme(theme_name)
            themes.append({
                "name": theme_name,
                "display_name": theme_data.get("name", theme_name.title()),
                "description": theme_data.get("description", ""),
                "preview": {
                    "primary_color": theme_data["colors"]["primary"],
                    "accent_color": theme_data["colors"]["accent"],
                    "background": theme_data["colors"]["background"],
                    "heading_font": theme_data["fonts"]["heading"]
                }
            })
        
        return {
            "themes": themes,
            "total": len(themes),
            "default": "markov-pro"
        }
    
    @mcp.tool("get_theme")
    def get_theme(theme_name: str) -> Dict[str, Any]:
        """
        Get complete theme configuration including all tokens.
        
        Args:
            theme_name: Name of the theme to retrieve
            
        Returns:
            Complete theme configuration
        """
        if theme_name not in theme_registry.list_themes():
            available = ", ".join(theme_registry.list_themes())
            raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")
        
        theme_data = theme_registry.get_theme(theme_name)
        return {
            "theme_name": theme_name,
            "theme_data": theme_data,
            "usage_example": f"Use theme '{theme_name}' by setting template parameter in init_deck"
        }
    
    @mcp.tool("create_custom_theme")
    def create_custom_theme(
        theme_name: str,
        base_theme: str = "markov-pro",
        color_overrides: Dict[str, str] = None,
        font_overrides: Dict[str, str] = None,
        typography_overrides: Dict[str, str] = None,
        spacing_overrides: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom theme by overriding tokens from a base theme.
        
        Args:
            theme_name: Name for the new custom theme
            base_theme: Base theme to extend (default: markov-pro)
            color_overrides: Color token overrides
            font_overrides: Font token overrides  
            typography_overrides: Typography token overrides
            spacing_overrides: Spacing token overrides
            
        Returns:
            Created theme configuration
        """
        if base_theme not in theme_registry.list_themes():
            available = ", ".join(theme_registry.list_themes())
            raise ValueError(f"Base theme '{base_theme}' not found. Available themes: {available}")
        
        # Get base theme
        base_config = theme_registry.get_theme(base_theme).copy()
        
        # Apply overrides
        if color_overrides:
            base_config["colors"].update(color_overrides)
        if font_overrides:
            base_config["fonts"].update(font_overrides)
        if typography_overrides:
            base_config["typography"].update(typography_overrides)
        if spacing_overrides:
            base_config["spacing"].update(spacing_overrides)
        
        # Update metadata
        base_config["name"] = theme_name.title()
        base_config["description"] = f"Custom theme based on {base_theme}"
        
        # Register the custom theme
        theme_registry.themes[theme_name] = base_config
        
        return {
            "theme_name": theme_name,
            "base_theme": base_theme,
            "theme_data": base_config,
            "status": "created",
            "usage": f"Theme '{theme_name}' is now available for use in presentations"
        }
    
    @mcp.tool("get_theme_tokens")
    def get_theme_tokens(theme_name: str, category: str = None) -> Dict[str, Any]:
        """
        Get specific token categories from a theme.
        
        Args:
            theme_name: Name of the theme
            category: Token category (colors, fonts, typography, spacing, shadows, animations)
            
        Returns:
            Theme tokens for the specified category or all tokens
        """
        if theme_name not in theme_registry.list_themes():
            available = ", ".join(theme_registry.list_themes())
            raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")
        
        theme_data = theme_registry.get_theme(theme_name)
        
        if category:
            if category not in theme_data:
                available_categories = list(theme_data.keys())
                raise ValueError(f"Category '{category}' not found. Available: {available_categories}")
            return {
                "theme_name": theme_name,
                "category": category,
                "tokens": theme_data[category]
            }
        else:
            return {
                "theme_name": theme_name,
                "all_tokens": theme_data
            }
    
    @mcp.tool("compare_themes")
    def compare_themes(theme1: str, theme2: str) -> Dict[str, Any]:
        """
        Compare two themes side by side.
        
        Args:
            theme1: First theme to compare
            theme2: Second theme to compare
            
        Returns:
            Side-by-side comparison of theme tokens
        """
        for theme in [theme1, theme2]:
            if theme not in theme_registry.list_themes():
                available = ", ".join(theme_registry.list_themes())
                raise ValueError(f"Theme '{theme}' not found. Available themes: {available}")
        
        theme1_data = theme_registry.get_theme(theme1)
        theme2_data = theme_registry.get_theme(theme2)
        
        comparison = {
            "theme1": {
                "name": theme1,
                "display_name": theme1_data.get("name"),
                "description": theme1_data.get("description"),
                "tokens": theme1_data
            },
            "theme2": {
                "name": theme2,
                "display_name": theme2_data.get("name"),
                "description": theme2_data.get("description"), 
                "tokens": theme2_data
            },
            "differences": {}
        }
        
        # Find differences in colors
        differences = {}
        for category in ["colors", "fonts", "typography", "spacing"]:
            if category in theme1_data and category in theme2_data:
                cat_diff = {}
                for key in theme1_data[category]:
                    if key in theme2_data[category]:
                        if theme1_data[category][key] != theme2_data[category][key]:
                            cat_diff[key] = {
                                theme1: theme1_data[category][key],
                                theme2: theme2_data[category][key]
                            }
                if cat_diff:
                    differences[category] = cat_diff
        
        comparison["differences"] = differences
        return comparison