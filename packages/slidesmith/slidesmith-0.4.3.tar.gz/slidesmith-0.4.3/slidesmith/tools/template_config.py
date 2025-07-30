"""
Template configuration tools: configure_template_defaults, set_slide_template.
Allows Claude to control template behavior explicitly.
"""

import json
from typing import TYPE_CHECKING, Union, Dict, Any
from pathlib import Path
from ..models import DeckRef, StatusOut
from ..config import WORKSPACES_DIR
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


class ConfigureTemplateIn(BaseModel):
    """Input for configure_template_defaults."""
    deck_id: str = Field(
        ...,
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )
    show_headers: bool = Field(
        True,
        description="Whether to show headers on slides by default"
    )
    show_footers: bool = Field(
        True,
        description="Whether to show footers on slides by default"
    )
    auto_extract_title: bool = Field(
        False,
        description="Whether to auto-extract title from first # header"
    )
    default_template: str = Field(
        "minimal",
        description="Default template for slides (minimal, standard, etc.)"
    )


class SetSlideTemplateIn(BaseModel):
    """Input for set_slide_template."""
    deck_id: str = Field(
        ...,
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )
    slide_number: int = Field(
        ..., 
        description="Slide number (1-based)",
        ge=1
    )
    template: str = Field(
        ...,
        description="Template name (minimal, standard, metrics, etc.)"
    )
    show_header: bool = Field(
        True,
        description="Whether to show header on this slide"
    )
    show_footer: bool = Field(
        True, 
        description="Whether to show footer on this slide"
    )


def register_template_config_tools(mcp: "FastMCP") -> None:
    """Register template configuration tools with the MCP server."""
    
    @mcp.tool()
    def configure_template_defaults(params: Union[ConfigureTemplateIn, str, dict]) -> StatusOut:
        """Configure default template behavior for the deck."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ConfigureTemplateIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ConfigureTemplateIn(**params)
        elif not isinstance(params, ConfigureTemplateIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        deck_path = WORKSPACES_DIR / params.deck_id
        if not deck_path.exists():
            return StatusOut(
                success=False,
                message=f"Deck not found: {params.deck_id}"
            )
        
        # Save template configuration
        config_file = deck_path / ".template_config.json"
        config = {
            "show_headers": params.show_headers,
            "show_footers": params.show_footers,
            "auto_extract_title": params.auto_extract_title,
            "default_template": params.default_template
        }
        
        config_file.write_text(json.dumps(config, indent=2))
        
        return StatusOut(
            success=True,
            message="Template defaults configured",
            details=config
        )
    
    @mcp.tool()
    def set_slide_template(params: Union[SetSlideTemplateIn, str, dict]) -> StatusOut:
        """Set template and display options for a specific slide."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = SetSlideTemplateIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = SetSlideTemplateIn(**params)
        elif not isinstance(params, SetSlideTemplateIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        deck_path = WORKSPACES_DIR / params.deck_id
        if not deck_path.exists():
            return StatusOut(
                success=False,
                message=f"Deck not found: {params.deck_id}"
            )
        
        # Load slide overrides
        overrides_file = deck_path / ".slide_overrides.json"
        if overrides_file.exists():
            overrides = json.loads(overrides_file.read_text())
        else:
            overrides = {}
        
        # Set overrides for this slide
        slide_key = f"slide_{params.slide_number}"
        overrides[slide_key] = {
            "template": params.template,
            "show_header": params.show_header,
            "show_footer": params.show_footer
        }
        
        # Save overrides
        overrides_file.write_text(json.dumps(overrides, indent=2))
        
        return StatusOut(
            success=True,
            message=f"Template settings updated for slide {params.slide_number}",
            details=overrides[slide_key]
        )