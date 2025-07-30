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
            if not slides_content.strip():
                slide_count = 0
            else:
                # Split content into sections
                sections = re.split(r'\n---\s*\n', slides_content)
                
                # Skip deck frontmatter if present
                slides_start_idx = 0
                if sections and sections[0].strip() and not re.search(r'^slide:\s*\d+', sections[0], re.MULTILINE):
                    # First section is deck frontmatter, skip it
                    slides_start_idx = 1
                
                # Count actual slides
                slide_count = 0
                for i in range(slides_start_idx, len(sections)):
                    section = sections[i].strip()
                    if section:
                        slide_count += 1
            
            metadata["slides_count"] = slide_count
            metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            metadata_file.write_text(json.dumps(metadata, indent=2, default=str))
    
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
        
        # Count actual slides (excluding deck frontmatter) - same as list_slides
        actual_slide_count = 0
        for slide in slides:
            if slide.raw_markdown.strip():
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Skip deck metadata
                if content_after_fm and not (content_after_fm.startswith('# Deck:') and 
                                           'Use the slide management tools' in content_after_fm):
                    actual_slide_count += 1
        
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
        
        # Insert the new slide
        if slide_number == actual_slide_count + 1:
            # Append to end
            new_content = current_content.rstrip() + "\n\n" + slide_content
        else:
            # Insert at specific position
            # We need to renumber subsequent slides
            new_sections = []
            
            # Add deck frontmatter if exists
            if deck_frontmatter:
                new_sections.append(deck_frontmatter)
            
            # Process slides
            slide_idx = 0
            for i in range(slides_start_idx, len(sections)):
                section = sections[i].strip()
                if not section:
                    continue
                
                slide_idx += 1
                
                # Insert new slide at the right position
                if slide_idx == slide_number:
                    new_sections.append(slide_content.strip())
                
                # Update slide number if needed
                if slide_idx >= slide_number:
                    # Increment slide number
                    section = re.sub(r'^slide:\s*\d+', f'slide: {slide_idx + 1}', section, flags=re.MULTILINE)
                
                new_sections.append(section)
            
            # Join with proper separators
            new_content = '\n---\n'.join(new_sections)
        
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
        
        # Count actual slides (excluding deck frontmatter) - same as list_slides
        actual_slide_count = 0
        for slide in slides:
            if slide.raw_markdown.strip():
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Skip deck metadata
                if content_after_fm and not (content_after_fm.startswith('# Deck:') and 
                                           'Use the slide management tools' in content_after_fm):
                    actual_slide_count += 1
        
        if params.slide_number < 1 or params.slide_number > actual_slide_count:
            raise ValueError(f"Slide {params.slide_number} not found. Deck has {actual_slide_count} slides.")
        
        # We need to properly handle the slide update
        lines = current_content.split('\n')
        new_lines = []
        current_section = []
        in_frontmatter = False
        slide_count = 0
        is_deck_frontmatter = True
        found_target = False
        current_template = "minimal"
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '---':
                if not current_section or all(l.strip() == '' for l in current_section):
                    # Start of frontmatter
                    in_frontmatter = True
                    current_section.append(line)
                elif in_frontmatter:
                    # End of frontmatter
                    in_frontmatter = False
                    current_section.append(line)
                    
                    # Check if this section has slide metadata
                    section_text = '\n'.join(current_section)
                    has_slide_num = re.search(r'^slide:\s*(\d+)', section_text, re.MULTILINE)
                    
                    if has_slide_num and is_deck_frontmatter:
                        is_deck_frontmatter = False
                    
                    if has_slide_num:
                        slide_count += 1
                        
                        if slide_count == params.slide_number:
                            # This is the slide to update
                            found_target = True
                            # Extract template
                            template_match = re.search(r'^template:\s*(.+)$', section_text, re.MULTILINE)
                            current_template = template_match.group(1) if template_match else "standard"
                            
                            # Create new frontmatter
                            new_fm = f"""---
slide: {params.slide_number}
template: {current_template}
---"""
                            new_lines.extend(new_fm.split('\n'))
                            
                            # Add the new content
                            new_lines.extend(['', params.content])
                            
                            # Skip the old content
                            j = i + 1
                            while j < len(lines) and lines[j].strip() != '---':
                                j += 1
                            i = j - 1  # Will be incremented at end of loop
                            current_section = []
                        else:
                            # Keep this section as is
                            new_lines.extend(current_section)
                            current_section = []
                    else:
                        # This is deck frontmatter
                        new_lines.extend(current_section)
                        current_section = []
                else:
                    # This could be start of a new slide
                    # Add current content if any
                    if current_section:
                        new_lines.extend(current_section)
                    current_section = [line]
                    in_frontmatter = True
            else:
                if not found_target or slide_count != params.slide_number:
                    current_section.append(line)
            
            i += 1
        
        # Don't forget the last section
        if current_section:
            new_lines.extend(current_section)
        
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
        
        # Use the parser to properly parse slides
        parser = MarkdownParser()
        slides, _ = parser.parse(current_content)
        
        # Extract info for each actual slide (skip deck frontmatter)
        slide_infos = []
        slide_num = 0
        for i, slide in enumerate(slides):
            # Check if this slide has explicit content after frontmatter
            # The parser gives sequential numbers, but deck frontmatter doesn't have actual slide content
            if slide.raw_markdown.strip():
                # Check if this is a real slide (has content after frontmatter) vs just deck metadata
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    # Extract content after frontmatter
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Skip if this looks like just deck metadata (e.g., "# Deck: Title")
                if content_after_fm and not (content_after_fm.startswith('# Deck:') and 
                                           'Use the slide management tools' in content_after_fm):
                    slide_num += 1
                    # Extract template
                    template = slide.template if hasattr(slide, 'template') else "standard"
                    
                    # Extract slide info from raw markdown
                    info = _extract_slide_info(slide.raw_markdown, slide_num, template)
                    slide_infos.append(info)
        
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
        
        # Count actual slides (excluding deck frontmatter) - same as list_slides
        actual_slide_count = 0
        for slide in slides:
            if slide.raw_markdown.strip():
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Skip deck metadata
                if content_after_fm and not (content_after_fm.startswith('# Deck:') and 
                                           'Use the slide management tools' in content_after_fm):
                    actual_slide_count += 1
        
        if params.slide_number < 1 or params.slide_number > actual_slide_count:
            raise ValueError(f"Slide {params.slide_number} not found. Deck has {actual_slide_count} slides.")
        
        # We need to properly handle the slide removal
        # First, let's identify what we have
        lines = current_content.split('\n')
        new_lines = []
        current_section = []
        in_frontmatter = False
        section_count = 0
        removed = False
        slide_count = 0
        is_deck_frontmatter = True
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '---':
                if not current_section or all(l.strip() == '' for l in current_section):
                    # Start of frontmatter
                    in_frontmatter = True
                    current_section.append(line)
                elif in_frontmatter:
                    # End of frontmatter
                    in_frontmatter = False
                    current_section.append(line)
                    
                    # Check if this section has slide metadata
                    section_text = '\n'.join(current_section)
                    has_slide_num = re.search(r'^slide:\s*(\d+)', section_text, re.MULTILINE)
                    
                    if has_slide_num and is_deck_frontmatter:
                        is_deck_frontmatter = False
                    
                    if has_slide_num:
                        slide_count += 1
                        
                        if slide_count == params.slide_number:
                            # Skip this slide and its content
                            removed = True
                            # Find the end of this slide's content
                            j = i + 1
                            while j < len(lines) and lines[j].strip() != '---':
                                j += 1
                            i = j - 1  # Will be incremented at end of loop
                            current_section = []
                        else:
                            # Renumber if needed
                            if removed and has_slide_num:
                                old_num = int(has_slide_num.group(1))
                                new_num = slide_count - 1
                                section_text = re.sub(r'^slide:\s*\d+', f'slide: {new_num}', section_text, flags=re.MULTILINE)
                                current_section = section_text.split('\n')
                            
                            # Add this section
                            new_lines.extend(current_section)
                            current_section = []
                    else:
                        # This is deck frontmatter
                        new_lines.extend(current_section)
                        current_section = []
                else:
                    # This could be start of a new slide
                    # Add current content if any
                    if current_section:
                        new_lines.extend(current_section)
                    current_section = [line]
                    in_frontmatter = True
            else:
                current_section.append(line)
            
            i += 1
        
        # Don't forget the last section
        if current_section:
            new_lines.extend(current_section)
        
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
        
        # Count actual slides (excluding deck frontmatter)
        parser = MarkdownParser()
        slides, _ = parser.parse(current_content)
        
        # Count only real slides (skip deck frontmatter)
        actual_slide_count = 0
        for slide in slides:
            # Check if this slide has real content (not just deck metadata)
            if slide.raw_markdown.strip():
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Skip deck metadata
                if content_after_fm and not (content_after_fm.startswith('# Deck:') and 
                                           'Use the slide management tools' in content_after_fm):
                    actual_slide_count += 1
        
        # Validate slide order
        if len(params.slide_order) != actual_slide_count:
            raise ValueError(f"slide_order must contain exactly {actual_slide_count} slide numbers")
        
        if actual_slide_count > 0 and set(params.slide_order) != set(range(1, actual_slide_count + 1)):
            raise ValueError("slide_order must contain each slide number exactly once")
        
        # Parse slides properly to maintain structure
        parser = MarkdownParser()
        all_slides, _ = parser.parse(current_content)
        
        # Separate deck frontmatter from actual slides
        deck_frontmatter_content = ""
        slides_to_reorder = []
        
        for slide in all_slides:
            # Check if this is deck frontmatter
            if slide.raw_markdown.strip():
                content_after_fm = slide.raw_markdown
                if content_after_fm.startswith('---'):
                    parts = content_after_fm.split('---', 2)
                    if len(parts) >= 3:
                        content_after_fm = parts[2].strip()
                
                # Check if this is deck metadata
                if content_after_fm and content_after_fm.startswith('# Deck:') and 'Use the slide management tools' in content_after_fm:
                    deck_frontmatter_content = slide.raw_markdown
                else:
                    slides_to_reorder.append(slide.raw_markdown)
        
        # Validate we have the right number of slides
        if len(slides_to_reorder) != len(params.slide_order):
            raise ValueError(f"Expected {len(slides_to_reorder)} slides but got {len(params.slide_order)} in slide_order")
        
        # Build new content
        new_content_parts = []
        
        # Add deck frontmatter if exists
        if deck_frontmatter_content:
            new_content_parts.append(deck_frontmatter_content)
        
        # Add slides in new order
        for new_position, old_position in enumerate(params.slide_order, 1):
            if old_position < 1 or old_position > len(slides_to_reorder):
                raise ValueError(f"Invalid slide position {old_position}")
            
            # Get the slide content
            slide_content = slides_to_reorder[old_position - 1]
            
            # Update slide number in frontmatter
            if slide_content.startswith('---'):
                # Find frontmatter section
                lines = slide_content.split('\n')
                in_fm = False
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        if not in_fm:
                            in_fm = True
                        else:
                            # End of frontmatter
                            break
                    elif in_fm and line.strip().startswith('slide:'):
                        lines[i] = f'slide: {new_position}'
                
                slide_content = '\n'.join(lines)
            
            new_content_parts.append(slide_content)
        
        # Join with proper spacing
        new_content = '\n\n'.join(new_content_parts)
        
        # Write updated content
        _write_slides_file(deck_path, new_content)
        
        return StatusOut(
            success=True,
            message=f"Reordered slides in deck {params.deck_id}"
        )