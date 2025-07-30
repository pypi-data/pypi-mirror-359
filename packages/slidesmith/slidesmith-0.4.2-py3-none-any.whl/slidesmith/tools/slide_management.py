"""
Slide management tools for granular control over individual slides.
Empowers Claude to be the primary slide author.
"""

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Union, List, Optional
from datetime import datetime, timezone

from ..config import WORKSPACES_DIR
from ..models import (
    DeckRef,
    StatusOut,
)
from ..parser import MarkdownParser
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from fastmcp import FastMCP


# New models for slide management
class AddSlideIn(BaseModel):
    """Input for adding a new slide."""
    deck_id: str = Field(..., description="UUID of the deck")
    slide_number: Optional[int] = Field(None, description="Position to insert slide (1-based). If None, appends to end")
    template: str = Field("minimal", description="Slide template to use")
    content: str = Field(..., description="Markdown content for the slide")


class UpdateSlideIn(BaseModel):
    """Input for updating an existing slide."""
    deck_id: str = Field(..., description="UUID of the deck") 
    slide_number: int = Field(..., description="Slide number to update (1-based)")
    content: str = Field(..., description="New markdown content for the slide")


class SlideInfo(BaseModel):
    """Information about a single slide."""
    number: int
    template: str
    title: str = Field(..., description="First heading or first line of content")
    preview: str = Field(..., description="First 100 chars of content")
    has_components: bool = Field(..., description="Whether slide uses components")


class ListSlidesOut(BaseModel):
    """Output for list_slides."""
    deck_id: str
    total_slides: int
    slides: List[SlideInfo]


class RemoveSlideIn(BaseModel):
    """Input for removing a slide."""
    deck_id: str = Field(..., description="UUID of the deck")
    slide_number: int = Field(..., description="Slide number to remove (1-based)")


class ReorderSlidesIn(BaseModel):
    """Input for reordering slides."""
    deck_id: str = Field(..., description="UUID of the deck")
    slide_order: List[int] = Field(..., description="New order of slide numbers (1-based)")


def register_slide_management_tools(mcp: "FastMCP") -> None:
    """Register slide management tools with the MCP server."""
    
    def _get_deck_path(deck_id: str) -> Path:
        """Get the path to a deck workspace."""
        deck_path = WORKSPACES_DIR / deck_id
        if not deck_path.exists():
            raise ValueError(f"Deck {deck_id} not found")
        return deck_path
    
    def _read_slides_file(deck_path: Path) -> str:
        """Read the current slides.md file."""
        slides_file = deck_path / "src" / "slides.md"
        if not slides_file.exists():
            return ""
        return slides_file.read_text()
    
    def _write_slides_file(deck_path: Path, content: str) -> None:
        """Write the slides.md file."""
        slides_file = deck_path / "src" / "slides.md"
        slides_file.write_text(content)
        
        # Update metadata
        _update_slide_count(deck_path)
    
    def _update_slide_count(deck_path: Path) -> None:
        """Update the slide count in metadata."""
        metadata_file = deck_path / ".metadata.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text())
            
            # Count slides properly
            slides_content = _read_slides_file(deck_path)
            slide_count = _count_actual_slides(slides_content)
            
            metadata["slides_count"] = slide_count
            metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            metadata_file.write_text(json.dumps(metadata, indent=2, default=str))
    
    def _count_actual_slides(content: str) -> int:
        """Count the actual number of slides, excluding empty slides and deck frontmatter."""
        if not content.strip():
            return 0
        
        # Parse the content to identify real slides
        lines = content.split('\n')
        slide_count = 0
        i = 0
        
        while i < len(lines):
            if lines[i].strip() == '---':
                # Found a delimiter, check if this starts a slide
                j = i + 1
                # Skip to find if this has slide metadata
                has_slide_meta = False
                while j < len(lines) and lines[j].strip() != '---':
                    if lines[j].strip().startswith('slide:'):
                        has_slide_meta = True
                        break
                    j += 1
                
                if has_slide_meta:
                    # This is a slide, check if it has content
                    # Skip past the closing --- of frontmatter
                    while j < len(lines) and lines[j].strip() != '---':
                        j += 1
                    j += 1  # Skip the closing ---
                    
                    # Check if there's content before the next ---
                    has_content = False
                    while j < len(lines) and lines[j].strip() != '---':
                        if lines[j].strip():
                            has_content = True
                            break
                        j += 1
                    
                    if has_content:
                        slide_count += 1
                    
                    i = j
                else:
                    i += 1
            else:
                i += 1
        
        return slide_count
    
    def _extract_slide_info(slide_content: str, number: int, template: str = "standard") -> SlideInfo:
        """Extract information from slide content."""
        # Parse the slide properly to get structured data
        parser = MarkdownParser()
        slides, _ = parser.parse(slide_content)
        
        if not slides:
            # Fallback if parsing fails
            return SlideInfo(
                number=number,
                template=template,
                title="Untitled",
                preview=slide_content[:100],
                has_components=False
            )
        
        slide = slides[0]
        
        # Extract title from content blocks
        title = "Untitled"
        preview_parts = []
        has_components = False
        
        for block in slide.content_blocks:
            if block.component_type:
                has_components = True
            
            if block.content:
                # Add to preview
                preview_parts.append(block.content.strip())
                
                # Look for title in first content block
                if title == "Untitled":
                    lines = block.content.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        # Check if it's a heading
                        heading_match = re.match(r'^#+\s+(.+)$', line)
                        if heading_match:
                            title = heading_match.group(1)
                            break
                        else:
                            # Use first non-empty line as title
                            title = line
                            break
        
        # Create preview from all content
        preview = ' '.join(preview_parts)[:100]
        if len(preview) == 100:
            preview += "..."
        
        return SlideInfo(
            number=number,
            template=slide.template,
            title=title,
            preview=preview,
            has_components=has_components
        )
    
    @mcp.tool()
    def add_slide(params: Union[AddSlideIn, str, dict]) -> StatusOut:
        """Add a new slide to the deck."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = AddSlideIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = AddSlideIn(**params)
        elif not isinstance(params, AddSlideIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck path
        deck_path = _get_deck_path(params.deck_id)
        
        # Read current content
        current_content = _read_slides_file(deck_path)
        
        # Parse existing slides
        parser = MarkdownParser()
        slides, _ = parser.parse(current_content)
        
        # Count actual slides properly
        actual_slide_count = _count_actual_slides(current_content)
        
        # Determine slide number
        if params.slide_number is None:
            slide_number = actual_slide_count + 1
        else:
            slide_number = params.slide_number
            if slide_number < 1 or slide_number > actual_slide_count + 1:
                raise ValueError(f"Invalid slide number {slide_number}. Must be between 1 and {actual_slide_count + 1}")
        
        # Create slide content with frontmatter
        slide_content = f"""---
slide: {slide_number}
template: {params.template}
---

{params.content}"""
        
        # Split current content into sections
        sections = re.split(r'\n---\s*\n', current_content)
        
        # If we have frontmatter at the beginning, preserve it
        deck_frontmatter = ""
        slides_start_idx = 0
        if sections and sections[0].strip() and not sections[0].strip().startswith('slide:'):
            deck_frontmatter = sections[0]
            slides_start_idx = 1
        
        # Validate that we have content
        if not params.content or not params.content.strip():
            raise ValueError("Slide content cannot be empty")
        
        # Insert the new slide - complete rewrite for clarity
        if slide_number == actual_slide_count + 1:
            # Append to end - ensure proper formatting
            if current_content.rstrip().endswith('---'):
                # Already has a slide delimiter at the end
                new_content = current_content.rstrip() + "\n" + slide_content
            else:
                # Need to add delimiter before new slide
                new_content = current_content.rstrip() + "\n---\n" + slide_content
        else:
            # Insert at specific position - rebuild the entire content
            # Parse the current content more carefully
            lines = current_content.split('\n')
            new_lines = []
            
            # Track where we are
            in_frontmatter = False
            current_slide_num = 0
            slide_inserted = False
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Check if this is the start of deck frontmatter
                if i == 0 and line == '---':
                    in_frontmatter = True
                    new_lines.append(line)
                    i += 1
                    # Copy frontmatter
                    while i < len(lines) and lines[i] != '---':
                        new_lines.append(lines[i])
                        i += 1
                    if i < len(lines):
                        new_lines.append(lines[i])  # closing ---
                        i += 1
                    continue
                
                # Check if this is a slide delimiter
                if line == '---':
                    # Look ahead to see if next line has slide metadata
                    if i + 1 < len(lines) and lines[i + 1].startswith('slide:'):
                        # This is the start of a slide
                        current_slide_num += 1
                        
                        # Insert new slide here if it's the right position
                        if current_slide_num == slide_number and not slide_inserted:
                            # Add the new slide
                            new_lines.append('---')
                            new_lines.append(f'slide: {slide_number}')
                            new_lines.append(f'template: {params.template}')
                            new_lines.append('---')
                            new_lines.append('')
                            # Add content lines
                            for content_line in params.content.split('\n'):
                                new_lines.append(content_line)
                            slide_inserted = True
                            
                            # Now add the current slide with updated number
                            new_lines.append('---')
                            new_lines.append(f'slide: {current_slide_num + 1}')
                            i += 2  # Skip the original slide: line
                            
                            # Copy the rest of the slide metadata and content
                            while i < len(lines) and lines[i] != '---':
                                if not lines[i].startswith('slide:'):
                                    new_lines.append(lines[i])
                                i += 1
                        else:
                            # Just copy the slide, updating number if needed
                            new_lines.append(line)
                            i += 1
                            if i < len(lines):
                                if slide_inserted and lines[i].startswith('slide:'):
                                    new_lines.append(f'slide: {current_slide_num + 1}')
                                    i += 1
                                else:
                                    new_lines.append(lines[i])
                                    i += 1
                    else:
                        new_lines.append(line)
                        i += 1
                else:
                    new_lines.append(line)
                    i += 1
            
            # If we haven't inserted the slide yet (inserting at end), add it now
            if not slide_inserted:
                new_lines.append('---')
                new_lines.append(f'slide: {slide_number}')
                new_lines.append(f'template: {params.template}')
                new_lines.append('---')
                new_lines.append('')
                for content_line in params.content.split('\n'):
                    new_lines.append(content_line)
            
            new_content = '\n'.join(new_lines)
        
        # Write updated content
        _write_slides_file(deck_path, new_content)
        
        return StatusOut(
            success=True,
            message=f"Added slide {slide_number} to deck {params.deck_id}"
        )
    
    @mcp.tool()
    def update_slide(params: Union[UpdateSlideIn, str, dict]) -> StatusOut:
        """Update an existing slide's content."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = UpdateSlideIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = UpdateSlideIn(**params)
        elif not isinstance(params, UpdateSlideIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck path
        deck_path = _get_deck_path(params.deck_id)
        
        # Read current content
        current_content = _read_slides_file(deck_path)
        
        # Parse existing slides
        parser = MarkdownParser()
        slides, _ = parser.parse(current_content)
        
        # Count actual slides properly
        actual_slide_count = _count_actual_slides(current_content)
        
        if params.slide_number < 1 or params.slide_number > actual_slide_count:
            raise ValueError(f"Slide {params.slide_number} not found. Deck has {actual_slide_count} slides.")
        
        # Update the specific slide
        lines = current_content.split('\n')
        new_lines = []
        i = 0
        current_slide = 0
        updated = False
        
        while i < len(lines):
            if lines[i].strip() == '---' and i + 1 < len(lines):
                # Check if this is a slide start
                j = i + 1
                has_slide_meta = False
                slide_num = None
                template = "minimal"
                
                # Check frontmatter
                while j < len(lines) and lines[j].strip() != '---':
                    if lines[j].strip().startswith('slide:'):
                        has_slide_meta = True
                        slide_num = int(re.search(r'slide:\s*(\d+)', lines[j]).group(1))
                    elif lines[j].strip().startswith('template:'):
                        template = lines[j].strip().split(':', 1)[1].strip()
                    j += 1
                
                if has_slide_meta:
                    # This is a slide
                    # Find the content section
                    content_start = j + 1 if j < len(lines) and lines[j].strip() == '---' else j
                    content_end = content_start
                    
                    # Find where content ends
                    while content_end < len(lines) and lines[content_end].strip() != '---':
                        content_end += 1
                    
                    # Check if this slide has content
                    has_content = any(lines[k].strip() for k in range(content_start, content_end))
                    
                    if has_content:
                        current_slide += 1
                        
                        if current_slide == params.slide_number:
                            # Update this slide
                            updated = True
                            new_lines.append('---')
                            new_lines.append(f'slide: {slide_num}')
                            new_lines.append(f'template: {template}')
                            new_lines.append('---')
                            new_lines.append('')
                            for content_line in params.content.split('\n'):
                                new_lines.append(content_line)
                            
                            # Skip to end of this slide
                            i = content_end - 1  # -1 because loop will increment
                        else:
                            # Copy the slide as-is
                            for k in range(i, content_end):
                                new_lines.append(lines[k])
                            i = content_end - 1
                    else:
                        # Empty slide, copy as-is
                        for k in range(i, content_end):
                            new_lines.append(lines[k])
                        i = content_end - 1
                else:
                    # Not a slide, just copy
                    new_lines.append(lines[i])
            else:
                new_lines.append(lines[i])
            
            i += 1
        
        if not updated:
            raise ValueError(f"Failed to update slide {params.slide_number}")
        
        new_content = '\n'.join(new_lines)
        
        # Write updated content
        _write_slides_file(deck_path, new_content)
        
        return StatusOut(
            success=True,
            message=f"Updated slide {params.slide_number} in deck {params.deck_id}"
        )
    
    @mcp.tool()
    def list_slides(params: Union[DeckRef, str, dict]) -> ListSlidesOut:
        """List all slides in a deck with summaries."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = DeckRef(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = DeckRef(**params)
        elif not isinstance(params, DeckRef):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck path
        deck_path = _get_deck_path(params.deck_id)
        
        # Read current content
        current_content = _read_slides_file(deck_path)
        
        if not current_content.strip():
            return ListSlidesOut(
                deck_id=params.deck_id,
                total_slides=0,
                slides=[]
            )
        
        # Parse slides more carefully
        lines = current_content.split('\n')
        slide_infos = []
        i = 0
        
        while i < len(lines):
            if lines[i].strip() == '---' and i + 1 < len(lines):
                # Check if this is a slide start
                j = i + 1
                has_slide_meta = False
                slide_num = None
                template = "minimal"
                
                # Check frontmatter
                while j < len(lines) and lines[j].strip() != '---':
                    if lines[j].strip().startswith('slide:'):
                        has_slide_meta = True
                        slide_num = int(re.search(r'slide:\s*(\d+)', lines[j]).group(1))
                    elif lines[j].strip().startswith('template:'):
                        template = lines[j].strip().split(':', 1)[1].strip()
                    j += 1
                
                if has_slide_meta:
                    # Find the content section
                    content_start = j + 1 if j < len(lines) and lines[j].strip() == '---' else j
                    content_end = content_start
                    
                    # Find where content ends
                    while content_end < len(lines) and lines[content_end].strip() != '---':
                        content_end += 1
                    
                    # Extract the content
                    content_lines = lines[content_start:content_end]
                    content = '\n'.join(content_lines)
                    
                    # Check if this slide has actual content
                    if content.strip():
                        # Build full slide markdown for info extraction
                        slide_markdown = '\n'.join(lines[i:content_end])
                        info = _extract_slide_info(slide_markdown, len(slide_infos) + 1, template)
                        slide_infos.append(info)
                    
                    i = content_end - 1
            i += 1
        
        return ListSlidesOut(
            deck_id=params.deck_id,
            total_slides=len(slide_infos),
            slides=slide_infos
        )
    
    @mcp.tool()
    def remove_slide(params: Union[RemoveSlideIn, str, dict]) -> StatusOut:
        """Remove a slide from the deck and renumber remaining slides."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = RemoveSlideIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = RemoveSlideIn(**params)
        elif not isinstance(params, RemoveSlideIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck path
        deck_path = _get_deck_path(params.deck_id)
        
        # Read current content
        current_content = _read_slides_file(deck_path)
        
        # Parse existing slides
        parser = MarkdownParser()
        slides, _ = parser.parse(current_content)
        
        # Count actual slides properly
        actual_slide_count = _count_actual_slides(current_content)
        
        if params.slide_number < 1 or params.slide_number > actual_slide_count:
            raise ValueError(f"Slide {params.slide_number} not found. Deck has {actual_slide_count} slides.")
        
        # Remove the specific slide and renumber
        lines = current_content.split('\n')
        new_lines = []
        i = 0
        current_slide = 0
        
        while i < len(lines):
            if lines[i].strip() == '---' and i + 1 < len(lines):
                # Check if this is a slide start
                j = i + 1
                has_slide_meta = False
                slide_num = None
                
                # Check frontmatter
                while j < len(lines) and lines[j].strip() != '---':
                    if lines[j].strip().startswith('slide:'):
                        has_slide_meta = True
                        slide_num = int(re.search(r'slide:\s*(\d+)', lines[j]).group(1))
                    j += 1
                
                if has_slide_meta:
                    # Find the content section
                    content_start = j + 1 if j < len(lines) and lines[j].strip() == '---' else j
                    content_end = content_start
                    
                    # Find where content ends
                    while content_end < len(lines) and lines[content_end].strip() != '---':
                        content_end += 1
                    
                    # Check if this slide has content
                    has_content = any(lines[k].strip() for k in range(content_start, content_end))
                    
                    if has_content:
                        current_slide += 1
                        
                        if current_slide == params.slide_number:
                            # Skip this slide entirely - don't add anything to new_lines
                            i = content_end - 1
                        else:
                            # Copy the slide, renumbering if necessary
                            # If we've removed a slide, all subsequent slides need to be renumbered
                            new_slide_num = current_slide - 1 if current_slide > params.slide_number else current_slide
                            
                            # Copy slide with potentially new number
                            for k in range(i, content_end):
                                if lines[k].strip().startswith('slide:'):
                                    new_lines.append(f'slide: {new_slide_num}')
                                else:
                                    new_lines.append(lines[k])
                            i = content_end - 1
                    else:
                        # Empty slide, copy as-is
                        for k in range(i, content_end):
                            new_lines.append(lines[k])
                        i = content_end - 1
                else:
                    # Not a slide, just copy
                    new_lines.append(lines[i])
            else:
                new_lines.append(lines[i])
            
            i += 1
        
        new_content = '\n'.join(new_lines)
        
        # Write updated content
        _write_slides_file(deck_path, new_content)
        
        return StatusOut(
            success=True,
            message=f"Removed slide {params.slide_number} from deck {params.deck_id}"
        )
    
    @mcp.tool()
    def reorder_slides(params: Union[ReorderSlidesIn, str, dict]) -> StatusOut:
        """Reorder slides in the deck."""
        # Handle parameter conversion
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = ReorderSlidesIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = ReorderSlidesIn(**params)
        elif not isinstance(params, ReorderSlidesIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck path
        deck_path = _get_deck_path(params.deck_id)
        
        # Read current content
        current_content = _read_slides_file(deck_path)
        
        # Count actual slides properly
        actual_slide_count = _count_actual_slides(current_content)
        
        # Validate slide order
        if len(params.slide_order) != actual_slide_count:
            raise ValueError(f"slide_order must contain exactly {actual_slide_count} slide numbers")
        
        if actual_slide_count > 0 and set(params.slide_order) != set(range(1, actual_slide_count + 1)):
            raise ValueError("slide_order must contain each slide number exactly once")
        
        # Parse slides to collect them for reordering
        lines = current_content.split('\n')
        deck_frontmatter_lines = []
        slides_data = []  # List of (start_idx, end_idx, slide_num) tuples
        i = 0
        in_deck_fm = True
        
        while i < len(lines):
            if lines[i].strip() == '---':
                if i == 0:
                    # Start of deck frontmatter
                    j = i + 1
                    while j < len(lines) and lines[j].strip() != '---':
                        j += 1
                    if j < len(lines):
                        # Include the closing ---
                        deck_frontmatter_lines.extend(lines[i:j+1])
                        i = j
                        # Check if there's content after frontmatter
                        k = j + 1
                        while k < len(lines) and lines[k].strip() != '---':
                            deck_frontmatter_lines.append(lines[k])
                            k += 1
                        i = k - 1
                else:
                    # Potential slide start
                    j = i + 1
                    has_slide_meta = False
                    slide_num = None
                    
                    # Check for slide metadata
                    while j < len(lines) and lines[j].strip() != '---':
                        if lines[j].strip().startswith('slide:'):
                            has_slide_meta = True
                            slide_num = int(re.search(r'slide:\s*(\d+)', lines[j]).group(1))
                            break
                        j += 1
                    
                    if has_slide_meta:
                        in_deck_fm = False
                        # Find the full slide boundaries
                        fm_end = j
                        while fm_end < len(lines) and lines[fm_end].strip() != '---':
                            fm_end += 1
                        
                        content_start = fm_end + 1 if fm_end < len(lines) else fm_end
                        content_end = content_start
                        
                        # Find where content ends
                        while content_end < len(lines) and lines[content_end].strip() != '---':
                            content_end += 1
                        
                        # Check if this slide has content
                        has_content = any(lines[k].strip() for k in range(content_start, content_end))
                        
                        if has_content:
                            slides_data.append((i, content_end, slide_num))
                        
                        i = content_end - 1
            
            i += 1
        
        # Validate we have the right number of slides
        if len(slides_data) != len(params.slide_order):
            raise ValueError(f"Expected {len(slides_data)} slides but got {len(params.slide_order)} in slide_order")
        
        # Build new content
        new_lines = []
        
        # Add deck frontmatter if exists
        if deck_frontmatter_lines:
            new_lines.extend(deck_frontmatter_lines)
        
        # Add slides in new order
        for new_position, old_position in enumerate(params.slide_order, 1):
            if old_position < 1 or old_position > len(slides_data):
                raise ValueError(f"Invalid slide position {old_position}")
            
            # Get the slide data (find which slide was at old_position)
            slide_idx = old_position - 1
            start_idx, end_idx, _ = slides_data[slide_idx]
            
            # Copy the slide with new number
            for i in range(start_idx, end_idx):
                if lines[i].strip().startswith('slide:'):
                    new_lines.append(f'slide: {new_position}')
                else:
                    new_lines.append(lines[i])
        
        new_content = '\n'.join(new_lines)
        
        # Write updated content
        _write_slides_file(deck_path, new_content)
        
        return StatusOut(
            success=True,
            message=f"Reordered slides in deck {params.deck_id}"
        )