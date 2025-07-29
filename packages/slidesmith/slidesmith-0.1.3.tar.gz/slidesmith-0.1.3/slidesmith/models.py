"""
Pydantic models for Slidesmith tool inputs and outputs.

All models follow MCP 2025-06 specification requirements.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


# Enums
class TemplateType(str, Enum):
    """Available slide templates."""
    MARKOV_PRO = "markov-pro"
    MINIMAL = "minimal"
    TECH = "tech"


class LintLevel(str, Enum):
    """Severity levels for lint issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class TokenCategory(str, Enum):
    """Token categories for theming."""
    COLORS = "colors"
    TYPOGRAPHY = "typography"
    SPACING = "spacing"
    BORDERS = "borders"
    SHADOWS = "shadows"
    TRANSITIONS = "transitions"


# Input Models
class InitDeckIn(BaseModel):
    """Input for init_deck tool."""
    template: TemplateType = Field(
        description="Template to use for the deck"
    )
    title: str = Field(
        description="Title of the deck",
        min_length=1,
        max_length=200,
    )
    author: Optional[str] = Field(
        default=None,
        description="Author of the deck",
    )


class DeckRef(BaseModel):
    """Reference to an existing deck."""
    deck_id: str = Field(
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )


class ThemeBaseIn(BaseModel):
    """Input for theme_base tool."""
    template: TemplateType = Field(
        description="Template to get base tokens for"
    )


class ApplyTokensIn(BaseModel):
    """Input for apply_tokens tool."""
    deck_id: str = Field(
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )
    patches: Dict[str, Any] = Field(
        description="JSON patches to apply to tokens"
    )


class SnapshotIn(BaseModel):
    """Input for snapshot tool."""
    deck_id: str = Field(
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )
    slide_number: Optional[int] = Field(
        default=None,
        description="Specific slide to snapshot (1-based), or None for all",
        ge=1,
    )
    clip: Optional[Dict[str, int]] = Field(
        default=None,
        description="Optional clip region {x, y, width, height}",
    )


class PdfFormat(str, Enum):
    """PDF page format options."""
    A4 = "A4"
    LETTER = "Letter"
    SLIDE = "Slide"  # 16:9
    CUSTOM = "Custom"  # Wide format


class PdfOrientation(str, Enum):
    """PDF orientation options."""
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"


class PdfExportIn(BaseModel):
    """Input for pdf_export tool."""
    deck_id: str = Field(
        description="UUID of the deck",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    )
    filename: Optional[str] = Field(
        default="deck",
        description="Output filename (without .pdf extension)",
        pattern=r"^[a-zA-Z0-9_\-]+$",
    )
    format: Optional[PdfFormat] = Field(
        default=PdfFormat.A4,
        description="PDF page format"
    )
    orientation: Optional[PdfOrientation] = Field(
        default=PdfOrientation.LANDSCAPE,
        description="PDF orientation"
    )
    quality_check: Optional[bool] = Field(
        default=True,
        description="Require lint score >= 80 before export"
    )


class ComponentDocIn(BaseModel):
    """Input for get_component_doc tool."""
    component: str = Field(
        description="Component name to get documentation for",
        pattern=r"^[A-Z][a-zA-Z0-9]+$",
    )
    template: str = Field(
        default="markov-pro",
        description="Template to search for component in"
    )


class SvgIconIn(BaseModel):
    """Input for svg_icon tool."""
    name: str = Field(
        description="Icon name from FontAwesome collection",
        pattern=r"^[a-z0-9\-]+$",
    )
    style: str = Field(
        default="solid",
        description="Icon style (solid, regular, brands)",
        pattern=r"^(solid|regular|light|duotone|brands)$",
    )
    size: Optional[int] = Field(
        default=24,
        description="Icon size in pixels",
        ge=8,
        le=512,
    )
    color: Optional[str] = Field(
        default=None,
        description="Icon color in hex format",
        pattern=r"^#[0-9A-Fa-f]{6}$|^#[0-9A-Fa-f]{3}$",
    )


# Output Models
class TemplateInfo(BaseModel):
    """Information about a template."""
    name: str
    display_name: str
    description: str
    preview_image: Optional[str] = None
    components: List[str] = Field(default_factory=list)


class TemplatesOut(BaseModel):
    """Output for list_templates tool."""
    templates: List[TemplateInfo]
    count: int


class DeckInfo(BaseModel):
    """Information about a created deck."""
    deck_id: str
    root: str = Field(description="Absolute path to deck workspace")
    created_at: datetime
    template: str
    title: str


class TokenColors(BaseModel):
    """Token colors structure."""
    primary: Optional[Union[str, Dict[str, str]]] = None
    secondary: Optional[Union[str, Dict[str, str]]] = None
    accent: Optional[Union[str, Dict[str, str]]] = None
    neutral: Optional[Union[str, Dict[str, str]]] = None
    success: Optional[Union[str, Dict[str, str]]] = None
    warning: Optional[Union[str, Dict[str, str]]] = None
    error: Optional[Union[str, Dict[str, str]]] = None
    # Allow additional color definitions
    model_config = ConfigDict(extra="allow")


class TokenTypography(BaseModel):
    """Token typography structure."""
    fontFamily: Optional[Dict[str, List[str]]] = None
    fontSize: Optional[Dict[str, str]] = None
    fontWeight: Optional[Dict[str, Union[int, str]]] = None
    lineHeight: Optional[Dict[str, Union[float, str]]] = None
    letterSpacing: Optional[Dict[str, str]] = None


class TokenSpacing(BaseModel):
    """Token spacing structure."""
    # Allow string keys for spacing scales
    model_config = ConfigDict(extra="allow")


class TokenBorders(BaseModel):
    """Token borders structure."""
    radius: Optional[Dict[str, str]] = None
    width: Optional[Dict[str, str]] = None
    style: Optional[Dict[str, str]] = None
    color: Optional[Dict[str, str]] = None


class TokenShadows(BaseModel):
    """Token shadows structure."""
    # Allow string keys for shadow definitions
    model_config = ConfigDict(extra="allow")


class TokenTransitions(BaseModel):
    """Token transitions structure."""
    duration: Optional[Dict[str, str]] = None
    easing: Optional[Dict[str, str]] = None
    property: Optional[Dict[str, str]] = None


class Tokens(BaseModel):
    """Complete theme tokens structure."""
    colors: Optional[TokenColors] = Field(default_factory=TokenColors)
    typography: Optional[TokenTypography] = Field(default_factory=TokenTypography)
    spacing: Optional[Dict[str, str]] = Field(default_factory=dict)
    borders: Optional[TokenBorders] = Field(default_factory=TokenBorders)
    shadows: Optional[Dict[str, str]] = Field(default_factory=dict)
    transitions: Optional[TokenTransitions] = Field(default_factory=TokenTransitions)
    
    # Allow additional token categories
    model_config = ConfigDict(extra="allow")


class LintIssue(BaseModel):
    """A single lint issue."""
    slide: int = Field(description="Slide number (1-based)")
    code: str = Field(description="Issue code (e.g., L-G1)")
    level: LintLevel
    message: str
    element: Optional[str] = Field(default=None, description="CSS selector of problematic element")


class LintReport(BaseModel):
    """Output for slide_lint tool."""
    issues: List[LintIssue]
    score: int = Field(ge=0, le=100, description="Overall quality score")
    passed: bool = Field(description="Whether deck passes quality threshold")
    summary: Dict[LintLevel, int] = Field(
        description="Count of issues by level"
    )


class PathOut(BaseModel):
    """Output for tools that return a file path."""
    path: str = Field(description="Absolute path to generated file")
    size_bytes: Optional[int] = Field(default=None, description="File size in bytes")


class MarkdownOut(BaseModel):
    """Output for documentation tools."""
    content: str = Field(description="Markdown content")
    title: Optional[str] = None
    examples: List[str] = Field(default_factory=list)


class StatusOut(BaseModel):
    """Output for status operations."""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


# Metadata Models
class DeckMetadata(BaseModel):
    """Metadata stored in .metadata.json."""
    deck_id: str
    created_at: datetime
    updated_at: datetime
    template: str
    title: str
    author: Optional[str] = None
    slides_count: int = 0
    last_build: Optional[Dict[str, Any]] = None
    last_lint: Optional[Dict[str, Any]] = None
    metadata_version: str = Field(default="1.0", description="Version of metadata format")
    
    model_config = ConfigDict(
        json_schema_serialization_defaults_required=True
    )
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def datetime_to_isoformat(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v