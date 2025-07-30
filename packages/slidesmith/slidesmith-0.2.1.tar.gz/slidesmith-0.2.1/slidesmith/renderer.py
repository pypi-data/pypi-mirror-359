"""
Slide renderer for Slidesmith - Combines parser, components, and templates.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .parser import MarkdownParser, Slide, ContentBlock, BlockType
from .components import ComponentRegistry
from .templates import TemplateRegistry


class SlideRenderer:
    """Main renderer that converts markdown to HTML slides."""
    
    def __init__(self, theme: str = "markov-pro"):
        self.theme = theme
        self.parser = MarkdownParser()
        self.templates = TemplateRegistry()
        self.components = self.templates.component_registry
        
        # Load theme tokens
        self.tokens = self._load_theme_tokens(theme)
    
    def _load_theme_tokens(self, theme: str) -> Dict[str, Any]:
        """Load theme tokens from JSON file."""
        # For now, return default tokens
        # TODO: Load from actual theme files
        return {
            "colors": {
                "primary": "#1D4ED8",
                "secondary": "#3B82F6",
                "accent": "#10B981",
                "background": "#FFFFFF",
                "text": "#1F2937",
                "muted": "#6B7280"
            },
            "fonts": {
                "heading": "'Montserrat', sans-serif",
                "body": "'Inter', sans-serif",
                "mono": "'Fira Code', monospace"
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "1rem",
                "md": "1.5rem",
                "lg": "2rem",
                "xl": "3rem"
            }
        }
    
    def render_markdown(self, markdown_content: str) -> Tuple[str, List[str]]:
        """
        Render markdown content to HTML slides.
        
        Returns:
            Tuple of (html, errors)
        """
        # Parse markdown
        slides, errors = self.parser.parse(markdown_content)
        
        if errors:
            return "", errors
        
        # Process nested components in content blocks
        for slide in slides:
            slide.content_blocks = self._process_nested_components(slide.content_blocks)
        
        # Render slides to HTML
        html = self._render_slides_to_html(slides)
        
        return html, []
    
    def _process_nested_components(self, blocks: List[ContentBlock]) -> List[ContentBlock]:
        """Process nested components within markdown blocks."""
        processed_blocks = []
        
        for block in blocks:
            if block.type == BlockType.COMPONENT and block.component_type in ['columns', 'grid']:
                # Process sections for layout components
                sections = block.props.get('sections', [])
                processed_sections = []
                
                for section in sections:
                    if isinstance(section, dict) and 'content' in section:
                        # Parse nested components in section content
                        nested_blocks = self.parser._parse_content_blocks(section['content'])
                        
                        # If there are components, render them directly
                        has_components = any(b.type == BlockType.COMPONENT for b in nested_blocks)
                        
                        if has_components:
                            # Render nested blocks
                            section_html = []
                            for nested_block in nested_blocks:
                                if nested_block.type == BlockType.MARKDOWN:
                                    section_html.append(self.parser.render_markdown(nested_block.content))
                                elif nested_block.type == BlockType.COMPONENT:
                                    # Merge content into props if not already there
                                    props = nested_block.props.copy()
                                    if nested_block.content and 'content' not in props:
                                        props['content'] = nested_block.content
                                    
                                    html = self.components.render(
                                        nested_block.component_type,
                                        props
                                    )
                                    section_html.append(html)
                            
                            section['content'] = '\n'.join(section_html)
                        # Otherwise leave content as-is for markdown processing
                    
                    processed_sections.append(section)
                
                block.props['sections'] = processed_sections
            
            processed_blocks.append(block)
        
        return processed_blocks
    
    def _render_slides_to_html(self, slides: List[Slide]) -> str:
        """Render slides to complete HTML document."""
        # Render individual slides
        slide_htmls = []
        for slide in slides:
            slide_html = self.templates.render_slide(slide)
            slide_htmls.append(f'<div class="slide" data-slide="{slide.number}">\n{slide_html}\n</div>')
        
        # Build complete HTML document
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slidesmith Presentation</title>
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Custom Styles -->
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: {self.tokens['fonts']['body']};
        }}
        
        .slide {{
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
            display: none;
        }}
        
        .slide[data-slide="1"] {{
            display: block;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                overflow: visible;
            }}
            
            .slide {{
                position: relative;
                page-break-after: always;
                display: block !important;
                width: 1920px;
                height: 1080px;
                margin: 0 auto;
            }}
        }}
        
        /* Custom theme tokens */
        :root {{
            --color-primary: {self.tokens['colors']['primary']};
            --color-secondary: {self.tokens['colors']['secondary']};
            --color-accent: {self.tokens['colors']['accent']};
            --font-heading: {self.tokens['fonts']['heading']};
            --font-body: {self.tokens['fonts']['body']};
        }}
    </style>
    
    <!-- Slide Navigation -->
    <script>
        let currentSlide = 1;
        const totalSlides = {len(slides)};
        
        function showSlide(n) {{
            const slides = document.querySelectorAll('.slide');
            
            if (n > totalSlides) currentSlide = 1;
            if (n < 1) currentSlide = totalSlides;
            
            slides.forEach(slide => {{
                slide.style.display = 'none';
            }});
            
            const targetSlide = document.querySelector(`.slide[data-slide="${{currentSlide}}"]`);
            if (targetSlide) {{
                targetSlide.style.display = 'block';
            }}
            
            // Update URL hash
            window.location.hash = `slide-${{currentSlide}}`;
        }}
        
        function nextSlide() {{
            currentSlide++;
            showSlide(currentSlide);
        }}
        
        function prevSlide() {{
            currentSlide--;
            showSlide(currentSlide);
        }}
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') {{
                nextSlide();
            }} else if (e.key === 'ArrowLeft') {{
                prevSlide();
            }} else if (e.key === 'Home') {{
                currentSlide = 1;
                showSlide(currentSlide);
            }} else if (e.key === 'End') {{
                currentSlide = totalSlides;
                showSlide(currentSlide);
            }}
        }});
        
        // Handle hash navigation
        window.addEventListener('hashchange', () => {{
            const hash = window.location.hash;
            const match = hash.match(/slide-(\\d+)/);
            if (match) {{
                currentSlide = parseInt(match[1]);
                showSlide(currentSlide);
            }}
        }});
        
        // Initialize from hash
        window.addEventListener('DOMContentLoaded', () => {{
            const hash = window.location.hash;
            const match = hash.match(/slide-(\\d+)/);
            if (match) {{
                currentSlide = parseInt(match[1]);
                showSlide(currentSlide);
            }}
        }});
    </script>
</head>
<body>
    <!-- Slides -->
    {''.join(slide_htmls)}
    
    <!-- Navigation hint -->
    <div style="position: fixed; bottom: 20px; right: 20px; background: rgba(0,0,0,0.7); color: white; padding: 10px 20px; border-radius: 5px; font-size: 14px; opacity: 0.7;">
        Use arrow keys to navigate
    </div>
</body>
</html>'''
        
        return html
    
    def render_file(self, markdown_path: str, output_path: str) -> List[str]:
        """
        Render a markdown file to HTML.
        
        Args:
            markdown_path: Path to input markdown file
            output_path: Path to output HTML file
            
        Returns:
            List of errors (empty if successful)
        """
        # Read markdown file
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
            return [f"Error reading file: {e}"]
        
        # Render to HTML
        html, errors = self.render_markdown(markdown_content)
        
        if errors:
            return errors
        
        # Write HTML file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            return [f"Error writing file: {e}"]
        
        return []
    
    def render_to_dict(self, markdown_content: str) -> Dict[str, Any]:
        """
        Render markdown to a structured dictionary (for JSON export).
        
        Returns:
            Dictionary with slides data and metadata
        """
        slides, errors = self.parser.parse(markdown_content)
        
        if errors:
            return {"error": errors}
        
        # Process slides to dictionary format
        slides_data = []
        for slide in slides:
            slide_data = {
                "number": slide.number,
                "template": slide.template,
                "theme": slide.theme,
                "metadata": slide.metadata,
                "html": self.templates.render_slide(slide),
                "blocks": []
            }
            
            for block in slide.content_blocks:
                if block.type == BlockType.MARKDOWN:
                    slide_data["blocks"].append({
                        "type": "markdown",
                        "content": block.content,
                        "html": self.parser.render_markdown(block.content)
                    })
                else:
                    slide_data["blocks"].append({
                        "type": "component",
                        "component": block.component_type,
                        "props": block.props,
                        "html": self.components.render(block.component_type, block.props)
                    })
            
            slides_data.append(slide_data)
        
        return {
            "theme": self.theme,
            "tokens": self.tokens,
            "total_slides": len(slides),
            "slides": slides_data
        }