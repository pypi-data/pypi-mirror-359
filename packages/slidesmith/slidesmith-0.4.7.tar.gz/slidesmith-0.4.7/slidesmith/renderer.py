"""
Slide renderer for Slidesmith - Combines parser, components, and templates.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .parser import MarkdownParser, Slide, ContentBlock, BlockType
from .components import ComponentRegistry
from .templates import TemplateRegistry
from .themes import theme_registry


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
        """Load theme tokens from the theme registry."""
        return theme_registry.get_theme(theme)
    
    def render_markdown(self, markdown_content: str) -> Tuple[str, List[str]]:
        """
        Render markdown content to HTML slides.
        
        Returns:
            Tuple of (html, errors)
        """
        # Parse markdown
        slides, errors = self.parser.parse(markdown_content)
        
        if errors:
            # Enhance error messages with more context
            enhanced_errors = []
            for error in errors:
                if "Invalid YAML frontmatter" in error:
                    enhanced_errors.append(
                        f"{error} - Tip: Check for unquoted colons in titles or use quotes around values with special characters"
                    )
                elif "Unclosed component" in error:
                    enhanced_errors.append(
                        f"{error} - Tip: Ensure all ::: component blocks have matching closing :::"
                    )
                else:
                    enhanced_errors.append(error)
            return "", enhanced_errors
        
        # Process nested components in content blocks
        try:
            for slide in slides:
                slide.content_blocks = self._process_nested_components(slide.content_blocks)
        except Exception as e:
            return "", [f"Error processing components: {str(e)} - Check component syntax and prop formatting"]
        
        # Render slides to HTML
        try:
            html = self._render_slides_to_html(slides)
        except Exception as e:
            return "", [f"Error rendering HTML: {str(e)} - This may be due to invalid component properties or template issues"]
        
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    
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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        .slide {{
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: block;
        }}
        
        .slide.active {{
            opacity: 1;
            transform: translateX(0);
            z-index: 10;
        }}
        
        .slide.prev {{
            transform: translateX(-100%);
        }}
        
        .slide.next {{
            transform: translateX(100%);
        }}
        
        /* Animation variants */
        .slide.fade-transition {{
            transform: none;
        }}
        
        .slide.fade-transition.active {{
            opacity: 1;
        }}
        
        .slide.slide-up-transition {{
            transform: translateY(100%);
        }}
        
        .slide.slide-up-transition.active {{
            transform: translateY(0);
        }}
        
        .slide.slide-up-transition.prev {{
            transform: translateY(-100%);
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
            /* Colors */
            --color-primary: {self.tokens['colors']['primary']};
            --color-secondary: {self.tokens['colors']['secondary']};
            --color-accent: {self.tokens['colors']['accent']};
            --color-success: {self.tokens['colors']['success']};
            --color-warning: {self.tokens['colors']['warning']};
            --color-error: {self.tokens['colors']['error']};
            --color-background: {self.tokens['colors']['background']};
            --color-surface: {self.tokens['colors']['surface']};
            --color-text: {self.tokens['colors']['text']};
            --color-text-secondary: {self.tokens['colors']['text_secondary']};
            --color-border: {self.tokens['colors']['border']};
            
            /* Typography */
            --font-heading: {self.tokens['fonts']['heading']};
            --font-body: {self.tokens['fonts']['body']};
            --font-mono: {self.tokens['fonts']['mono']};
            
            /* Spacing */
            --spacing-xs: {self.tokens['spacing']['xs']};
            --spacing-sm: {self.tokens['spacing']['sm']};
            --spacing-md: {self.tokens['spacing']['md']};
            --spacing-lg: {self.tokens['spacing']['lg']};
            --spacing-xl: {self.tokens['spacing']['xl']};
            --spacing-2xl: {self.tokens['spacing']['2xl']};
            --spacing-3xl: {self.tokens['spacing']['3xl']};
            
            /* Shadows */
            --shadow-sm: {self.tokens['shadows']['sm']};
            --shadow-md: {self.tokens['shadows']['md']};
            --shadow-lg: {self.tokens['shadows']['lg']};
            --shadow-xl: {self.tokens['shadows']['xl']};
            
            /* Animations */
            --duration-fast: {self.tokens['animations']['duration_fast']};
            --duration-normal: {self.tokens['animations']['duration_normal']};
            --duration-slow: {self.tokens['animations']['duration_slow']};
            --easing: {self.tokens['animations']['easing']};
        }}
        
        /* Typography improvements */
        h1 {{
            font-size: {self.tokens['typography']['h1_size']};
            font-weight: {self.tokens['typography']['h1_weight']};
            line-height: 1.1;
            letter-spacing: -0.02em;
            font-family: {self.tokens['fonts']['heading']};
        }}
        
        h2 {{
            font-size: {self.tokens['typography']['h2_size']};
            font-weight: {self.tokens['typography']['h2_weight']};
            line-height: 1.2;
            letter-spacing: -0.01em;
            font-family: {self.tokens['fonts']['heading']};
        }}
        
        h3 {{
            font-size: {self.tokens['typography']['h3_size']};
            font-weight: {self.tokens['typography']['h3_weight']};
            line-height: 1.3;
            font-family: {self.tokens['fonts']['heading']};
        }}
        
        h4 {{
            font-size: 1.875rem;
            font-weight: 600;
            line-height: 1.4;
            font-family: {self.tokens['fonts']['heading']};
        }}
        
        p {{
            font-size: {self.tokens['typography']['body_size']};
            line-height: {self.tokens['typography']['body_line_height']};
            font-family: {self.tokens['fonts']['body']};
        }}
        
        /* Better list styling */
        ul, ol {{
            font-size: {self.tokens['typography']['body_size']};
            line-height: {self.tokens['typography']['body_line_height']};
            font-family: {self.tokens['fonts']['body']};
        }}
        
        ul li, ol li {{
            margin-bottom: {self.tokens['spacing']['sm']};
        }}
        
        /* Clean code blocks */
        pre {{
            background-color: {self.tokens['colors']['surface']};
            color: {self.tokens['colors']['text']};
            border-radius: 0.75rem;
            padding: {self.tokens['spacing']['lg']};
            overflow-x: auto;
            font-size: 1.125rem;
            border: 1px solid {self.tokens['colors']['border']};
        }}
        
        code {{
            font-family: {self.tokens['fonts']['mono']};
            font-size: 0.95em;
        }}
        
        /* Slide-specific typography */
        .slide h1:first-child {{
            color: var(--color-primary);
            margin-bottom: {self.tokens['spacing']['xl']};
        }}
        
        .slide h2 {{
            color: var(--color-secondary);
            margin-top: {self.tokens['spacing']['xl']};
            margin-bottom: {self.tokens['spacing']['lg']};
        }}
        
        .slide h3 {{
            color: var(--color-secondary);
            margin-top: {self.tokens['spacing']['lg']};
            margin-bottom: {self.tokens['spacing']['md']};
        }}
    </style>
    
    <!-- Slide Navigation -->
    <script>
        let currentSlide = 1;
        const totalSlides = {len(slides)};
        
        function showSlide(n, direction = 'next') {{
            const slides = document.querySelectorAll('.slide');
            
            if (n > totalSlides) currentSlide = 1;
            if (n < 1) currentSlide = totalSlides;
            
            // Remove all animation classes
            slides.forEach(slide => {{
                slide.classList.remove('active', 'prev', 'next');
            }});
            
            // Set animation classes based on direction
            slides.forEach((slide, index) => {{
                const slideNum = index + 1;
                if (slideNum === currentSlide) {{
                    slide.classList.add('active');
                }} else if (slideNum < currentSlide) {{
                    slide.classList.add('prev');
                }} else {{
                    slide.classList.add('next');
                }}
            }});
            
            // Update URL hash
            window.location.hash = `slide-${{currentSlide}}`;
        }}
        
        function nextSlide() {{
            const oldSlide = currentSlide;
            currentSlide++;
            showSlide(currentSlide, 'next');
        }}
        
        function prevSlide() {{
            const oldSlide = currentSlide;
            currentSlide--;
            showSlide(currentSlide, 'prev');
        }}
        
        // Animation control functions
        function setAnimationType(type) {{
            const slides = document.querySelectorAll('.slide');
            slides.forEach(slide => {{
                slide.className = slide.className.replace(/\\b\\w+-transition\\b/g, '');
                if (type !== 'slide') {{
                    slide.classList.add(type + '-transition');
                }}
            }});
        }}
        
        // Animation type switching (can be controlled via URL params)
        const urlParams = new URLSearchParams(window.location.search);
        const animationType = urlParams.get('animation') || 'slide';
        setAnimationType(animationType);
        
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
            }} else if (e.key === 'f' || e.key === 'F') {{
                // Toggle fade animation
                setAnimationType('fade');
            }} else if (e.key === 's' || e.key === 'S') {{
                // Toggle slide animation
                setAnimationType('slide');
            }} else if (e.key === 'u' || e.key === 'U') {{
                // Toggle slide-up animation
                setAnimationType('slide-up');
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
            }}
            
            // Initialize the presentation
            showSlide(currentSlide);
            
            // Add slide numbers
            document.querySelectorAll('.slide').forEach((slide, index) => {{
                const slideNum = slide.querySelector('.slide-number');
                if (slideNum) {{
                    slideNum.textContent = `${{index + 1}} / ${{totalSlides}}`;
                }}
            }});
            
            // Show animation help on first load
            if (!localStorage.getItem('slidesmith-help-shown')) {{
                console.log('SlideSmith Animation Controls:');
                console.log('→/Space: Next slide');
                console.log('←: Previous slide');
                console.log('F: Fade animation');
                console.log('S: Slide animation');
                console.log('U: Slide-up animation');
                localStorage.setItem('slidesmith-help-shown', 'true');
            }}
        }});
    </script>
</head>
<body>
    <!-- Slides -->
    {''.join(slide_htmls)}
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