"""
Presentation mode tools: start_presentation, extract_speaker_notes.
Professional presentation features for SlideSmith.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Union, List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..models import DeckRef, StatusOut, MarkdownOut
from ..config import WORKSPACES_DIR
from ..renderer import SlideRenderer
from ..parser import MarkdownParser

if TYPE_CHECKING:
    from fastmcp import FastMCP


class StartPresentationIn(BaseModel):
    """Input for start_presentation."""
    deck_id: str = Field(..., description="UUID of the deck")
    target_duration: Optional[int] = Field(None, description="Target presentation duration in minutes")
    animation_type: str = Field("slide", description="Animation type (slide, fade, slide-up)")


class StartPresentationOut(BaseModel):
    """Output for start_presentation."""
    success: bool
    presentation_url: str = Field(..., description="URL to open for presentation mode")
    notes_extracted: int = Field(..., description="Number of slides with speaker notes")
    total_slides: int = Field(..., description="Total number of slides")
    instructions: List[str] = Field(default_factory=list, description="Presentation mode instructions")


class ExtractSpeakerNotesIn(BaseModel):
    """Input for extract_speaker_notes."""
    deck_id: str = Field(..., description="UUID of the deck")
    format: str = Field("markdown", description="Output format (markdown, json)")


class ExtractSpeakerNotesOut(BaseModel):
    """Output for extract_speaker_notes."""
    success: bool
    notes: Union[str, Dict[str, Any]] = Field(..., description="Extracted speaker notes")
    slides_with_notes: int = Field(..., description="Number of slides with notes")
    total_slides: int = Field(..., description="Total number of slides")


def register_presentation_tools(mcp: "FastMCP") -> None:
    """Register presentation tools with the MCP server."""
    
    @mcp.tool()
    def start_presentation(params: Union[StartPresentationIn, str, dict]) -> StartPresentationOut:
        """
        Start presentation mode for a deck with speaker notes and timing features.
        
        This tool prepares the deck for professional presentation with:
        - Dual-screen presenter view
        - Speaker notes display
        - Presentation timer
        - Slide controls
        """
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = StartPresentationIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = StartPresentationIn(**params)
        elif not isinstance(params, StartPresentationIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        deck_dir = WORKSPACES_DIR / params.deck_id
        if not deck_dir.exists():
            return StartPresentationOut(
                success=False,
                presentation_url="",
                notes_extracted=0,
                total_slides=0,
                instructions=["Error: Deck not found"]
            )
        
        # Check if deck has been built
        slides_file = deck_dir / "src" / "slides.md"
        index_file = deck_dir / "index.html"
        
        if not slides_file.exists():
            return StartPresentationOut(
                success=False,
                presentation_url="",
                notes_extracted=0,
                total_slides=0,
                instructions=["Error: Deck source not found. Run html_preview first."]
            )
        
        try:
            # Read and parse slides to count notes
            with open(slides_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parser = MarkdownParser()
            slides, errors = parser.parse(content)
            
            if errors:
                return StartPresentationOut(
                    success=False,
                    presentation_url="",
                    notes_extracted=0,
                    total_slides=0,
                    instructions=[f"Error parsing slides: {'; '.join(errors)}"]
                )
            
            # Count slides with speaker notes
            notes_count = 0
            for slide in slides:
                for block in slide.content:
                    if block.component_type == "speaker-notes":
                        notes_count += 1
                        break
            
            # Build presentation URL with parameters
            presentation_url = f"file://{index_file.resolve()}"
            if params.animation_type != "slide":
                presentation_url += f"?animation={params.animation_type}"
            
            instructions = [
                "🎤 Presentation Mode Ready!",
                "",
                "📋 Controls:",
                "  • Press 'P' to enter presentation mode",
                "  • Press 'Esc' to exit presentation mode", 
                "  • Use → and ← arrows to navigate slides",
                "  • Press 'T' to reset the timer",
                "",
                "⏰ Timer Features:",
                "  • Click 'Set Target' to set presentation duration",
                "  • Timer turns red when over target time",
                "  • Timer shows elapsed time (MM:SS format)",
                "",
                "📝 Speaker Notes:",
                f"  • {notes_count} slides have speaker notes",
                "  • Notes appear in left panel during presentation",
                "  • Notes support markdown formatting",
                "",
                "🖥️ Dual Screen:",
                "  • Left panel: Presenter view with notes",
                "  • Right panel: Audience view",
                "  • Browser may open second window for audience"
            ]
            
            if params.target_duration:
                instructions.append(f"⏱️ Target Duration: {params.target_duration} minutes")
            
            return StartPresentationOut(
                success=True,
                presentation_url=presentation_url,
                notes_extracted=notes_count,
                total_slides=len(slides),
                instructions=instructions
            )
            
        except Exception as e:
            return StartPresentationOut(
                success=False,
                presentation_url="",
                notes_extracted=0,
                total_slides=0,
                instructions=[f"Error: {str(e)}"]
            )
    
    @mcp.tool()
    def extract_speaker_notes(params: Union[ExtractSpeakerNotesIn, str, dict]) -> ExtractSpeakerNotesOut:
        """
        Extract all speaker notes from a deck for review or printing.
        
        This tool extracts speaker notes from all slides for:
        - Review and preparation
        - Printing speaker scripts
        - Backup reference materials
        """
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ExtractSpeakerNotesIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ExtractSpeakerNotesIn(**params)
        elif not isinstance(params, ExtractSpeakerNotesIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        deck_dir = WORKSPACES_DIR / params.deck_id
        slides_file = deck_dir / "src" / "slides.md"
        
        if not slides_file.exists():
            return ExtractSpeakerNotesOut(
                success=False,
                notes="",
                slides_with_notes=0,
                total_slides=0
            )
        
        try:
            # Read and parse slides
            with open(slides_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parser = MarkdownParser()
            slides, errors = parser.parse(content)
            
            if errors:
                return ExtractSpeakerNotesOut(
                    success=False,
                    notes=f"Error parsing slides: {'; '.join(errors)}",
                    slides_with_notes=0,
                    total_slides=0
                )
            
            # Extract notes
            if params.format == "json":
                notes_data = {}
                slides_with_notes = 0
                
                for i, slide in enumerate(slides, 1):
                    slide_title = slide.title or f"Slide {i}"
                    notes_content = None
                    
                    for block in slide.content:
                        if block.component_type == "speaker-notes":
                            notes_content = block.content
                            slides_with_notes += 1
                            break
                    
                    if notes_content:
                        notes_data[f"slide_{i}"] = {
                            "title": slide_title,
                            "notes": notes_content
                        }
                
                return ExtractSpeakerNotesOut(
                    success=True,
                    notes=notes_data,
                    slides_with_notes=slides_with_notes,
                    total_slides=len(slides)
                )
            
            else:  # markdown format
                notes_md = "# Speaker Notes\n\n"
                slides_with_notes = 0
                
                for i, slide in enumerate(slides, 1):
                    slide_title = slide.title or f"Slide {i}"
                    notes_content = None
                    
                    for block in slide.content:
                        if block.component_type == "speaker-notes":
                            notes_content = block.content
                            slides_with_notes += 1
                            break
                    
                    if notes_content:
                        notes_md += f"## {slide_title}\n\n"
                        notes_md += f"{notes_content}\n\n"
                        notes_md += "---\n\n"
                
                if slides_with_notes == 0:
                    notes_md += "*No speaker notes found in this deck.*\n"
                
                return ExtractSpeakerNotesOut(
                    success=True,
                    notes=notes_md,
                    slides_with_notes=slides_with_notes,
                    total_slides=len(slides)
                )
                
        except Exception as e:
            return ExtractSpeakerNotesOut(
                success=False,
                notes=f"Error: {str(e)}",
                slides_with_notes=0,
                total_slides=0
            )