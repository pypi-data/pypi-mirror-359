"""
Markdown parser for Slidesmith slide format.
Converts Markdown with custom component syntax to structured slide data.
"""

import re
import yaml
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import markdown
from markdown.extensions import fenced_code, tables, nl2br, attr_list


class BlockType(Enum):
    """Types of content blocks in a slide."""
    MARKDOWN = "markdown"
    COMPONENT = "component"
    RAW_HTML = "raw_html"


@dataclass
class ContentBlock:
    """Represents a single content block within a slide."""
    type: BlockType
    content: str = ""
    component_type: Optional[str] = None
    props: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0


@dataclass
class Slide:
    """Represents a single slide with metadata and content."""
    number: int
    template: str = "standard"
    theme: str = "markov-pro"
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_blocks: List[ContentBlock] = field(default_factory=list)
    raw_markdown: str = ""


class MarkdownParser:
    """Parser for Slidesmith Markdown format."""
    
    # Regex patterns
    SLIDE_SEPARATOR = re.compile(r'^---\s*$', re.MULTILINE)
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*$', re.MULTILINE | re.DOTALL)
    COMPONENT_START = re.compile(r'^:::([a-z-]+)(?:\s+(.*))?$', re.MULTILINE)
    COMPONENT_END = re.compile(r'^:::$', re.MULTILINE)
    PARAM_PATTERN = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\[[^\]]*\])|(\{[^\}]*\})|([^\s]+))')
    
    def __init__(self):
        """Initialize the parser with markdown processor."""
        self.md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'attr_list',
            'md_in_html',
            'sane_lists',
            'admonition'
        ])
        self.reset()
    
    def reset(self):
        """Reset parser state."""
        self.current_line = 0
        self.errors = []
    
    def parse(self, content: str) -> Tuple[List[Slide], List[str]]:
        """
        Parse markdown content into slides.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (slides, errors)
        """
        self.reset()
        slides = []
        
        # Split content by slide separators
        raw_slides = self._split_slides(content)
        
        for idx, raw_slide in enumerate(raw_slides, 1):
            slide = self._parse_slide(raw_slide, idx)
            if slide:
                slides.append(slide)
        
        return slides, self.errors
    
    def _split_slides(self, content: str) -> List[str]:
        """Split content into individual slide sections."""
        # More robust slide splitting
        slides = []
        lines = content.split('\n')
        current_slide = []
        i = 0
        in_frontmatter = False
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a separator
            if line.strip() == '---':
                # If we're at the beginning or current slide is empty (only whitespace)
                if not current_slide or all(l.strip() == '' for l in current_slide):
                    # This starts frontmatter
                    in_frontmatter = True
                    current_slide.append(line)
                # If we're in frontmatter, this closes it
                elif in_frontmatter:
                    in_frontmatter = False
                    current_slide.append(line)
                else:
                    # This is a slide separator
                    # Check if next lines look like frontmatter
                    has_frontmatter = False
                    if i + 1 < len(lines):
                        # Peek ahead
                        for j in range(i + 1, min(i + 4, len(lines))):
                            if ':' in lines[j] and not lines[j].startswith(' '):
                                has_frontmatter = True
                                break
                    
                    if has_frontmatter:
                        # Start new slide with frontmatter
                        slides.append('\n'.join(current_slide))
                        current_slide = [line]
                        in_frontmatter = True
                    else:
                        # Just a separator without frontmatter - new slide
                        slides.append('\n'.join(current_slide))
                        current_slide = []
            else:
                current_slide.append(line)
            
            i += 1
        
        # Don't forget the last slide
        if current_slide and not all(l.strip() == '' for l in current_slide):
            slides.append('\n'.join(current_slide))
        
        # Handle empty input
        if not slides:
            return ['']
        
        return slides
    
    def _parse_slide(self, raw_content: str, default_number: int) -> Optional[Slide]:
        """Parse a single slide from raw content."""
        # Extract frontmatter
        metadata, content = self._extract_frontmatter(raw_content)
        
        # Create slide with metadata
        slide = Slide(
            number=metadata.pop('slide', default_number),
            template=metadata.pop('template', 'standard'),
            theme=metadata.pop('theme', 'markov-pro'),
            metadata=metadata,
            raw_markdown=raw_content
        )
        
        # Parse content blocks
        slide.content_blocks = self._parse_content_blocks(content)
        
        return slide
    
    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter from content."""
        # Handle content that starts with frontmatter
        content = content.strip()
        if not content.startswith('---'):
            return {}, content
        
        # Find the end of frontmatter
        lines = content.split('\n')
        end_index = -1
        
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return {}, content
        
        # Extract frontmatter and remaining content
        frontmatter_lines = lines[1:end_index]
        frontmatter_str = '\n'.join(frontmatter_lines)
        remaining_content = '\n'.join(lines[end_index + 1:]).strip()
        
        try:
            metadata = yaml.safe_load(frontmatter_str) or {}
            if not isinstance(metadata, dict):
                self.errors.append(f"Line {self.current_line}: Frontmatter must be a valid YAML mapping")
                return {}, content
            return metadata, remaining_content
        except yaml.YAMLError as e:
            self.errors.append(f"Line {self.current_line}: Invalid YAML frontmatter: {e}")
            return {}, content
    
    def _parse_content_blocks(self, content: str) -> List[ContentBlock]:
        """Parse content into blocks (markdown and components)."""
        blocks = []
        lines = content.split('\n')
        i = 0
        
        current_markdown = []
        
        while i < len(lines):
            line = lines[i]
            
            # Check for component start
            match = self.COMPONENT_START.match(line)
            if match:
                # Save any accumulated markdown
                if current_markdown:
                    md_content = '\n'.join(current_markdown).strip()
                    if md_content:
                        blocks.append(ContentBlock(
                            type=BlockType.MARKDOWN,
                            content=md_content,
                            line_number=i - len(current_markdown)
                        ))
                    current_markdown = []
                
                # Parse component
                component_block, end_line = self._parse_component(lines, i)
                if component_block:
                    blocks.append(component_block)
                i = end_line
            else:
                current_markdown.append(line)
                i += 1
        
        # Save any remaining markdown
        if current_markdown:
            md_content = '\n'.join(current_markdown).strip()
            if md_content:
                blocks.append(ContentBlock(
                    type=BlockType.MARKDOWN,
                    content=md_content,
                    line_number=len(lines) - len(current_markdown)
                ))
        
        return blocks
    
    def _parse_component(self, lines: List[str], start_line: int) -> Tuple[Optional[ContentBlock], int]:
        """Parse a component block starting at the given line."""
        match = self.COMPONENT_START.match(lines[start_line])
        if not match:
            return None, start_line + 1
        
        component_type = match.group(1)
        params_str = match.group(2) or ""
        
        # Parse parameters
        props = self._parse_parameters(params_str)
        
        # Find component end
        content_lines = []
        i = start_line + 1
        nesting_level = 1
        
        while i < len(lines) and nesting_level > 0:
            line = lines[i]
            
            # Check for nested component start
            if self.COMPONENT_START.match(line):
                nesting_level += 1
            # Check for component end
            elif self.COMPONENT_END.match(line):
                nesting_level -= 1
                if nesting_level == 0:
                    break
            
            content_lines.append(line)
            i += 1
        
        if nesting_level > 0:
            self.errors.append(
                f"Line {start_line + 1}: Unclosed component '{component_type}'"
            )
            return None, len(lines)
        
        # Process component content
        content = '\n'.join(content_lines).strip()
        
        # Special handling for certain components
        if component_type in ['metrics', 'timeline']:
            props['items'] = self._parse_list_items(content)
            content = ""
        elif component_type == 'table':
            props['markdown'] = content
            content = ""
        elif component_type in ['columns', 'grid']:
            props['sections'] = self._parse_sections(content)
            content = ""
        
        return ContentBlock(
            type=BlockType.COMPONENT,
            component_type=component_type,
            props=props,
            content=content,
            line_number=start_line + 1
        ), i + 1
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse component parameters from string."""
        props = {}
        
        for match in self.PARAM_PATTERN.finditer(params_str):
            key = match.group(1)
            # Try each capture group in order
            value = (match.group(2) or match.group(3) or 
                    match.group(4) or match.group(5) or match.group(6))
            
            # Parse arrays and objects
            if value.startswith('['):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    self.errors.append(f"Invalid array syntax: {value}")
            elif value.startswith('{'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    self.errors.append(f"Invalid object syntax: {value}")
            # Try to parse as number
            elif value.replace('.', '').replace('-', '').isdigit():
                try:
                    value = int(value) if '.' not in value else float(value)
                except ValueError:
                    pass
            # Parse boolean
            elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            
            props[key] = value
        
        return props
    
    def _parse_list_items(self, content: str) -> List[Dict[str, Any]]:
        """Parse YAML-style list items for metrics/timeline components."""
        try:
            # Parse as YAML list
            items = yaml.safe_load(content)
            if isinstance(items, list):
                return items
            else:
                self.errors.append("Expected a list of items")
                return []
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML list: {e}")
            return []
    
    def _parse_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse sections for columns/grid components."""
        sections = []
        current_section = {'title': '', 'content': []}
        
        for line in content.split('\n'):
            # Check if line is a header (### Title)
            if line.strip().startswith('###'):
                # Save previous section if exists
                if current_section['content']:
                    current_section['content'] = '\n'.join(current_section['content']).strip()
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line.strip().lstrip('#').strip(),
                    'content': []
                }
            else:
                current_section['content'].append(line)
        
        # Save last section
        if current_section['content'] or current_section['title']:
            current_section['content'] = '\n'.join(current_section['content']).strip()
            sections.append(current_section)
        
        return sections
    
    def render_markdown(self, content: str) -> str:
        """Render markdown content to HTML."""
        return self.md.convert(content)