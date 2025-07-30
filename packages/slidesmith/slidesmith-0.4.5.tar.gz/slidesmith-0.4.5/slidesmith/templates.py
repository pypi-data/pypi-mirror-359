"""
Template system for Slidesmith - Maps slide templates to component layouts.
"""

from typing import Dict, Any, List
from .components import ComponentRegistry
from .parser import Slide, BlockType
import markdown


class SlideTemplate:
    """Base class for slide templates."""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.md = markdown.Markdown(extensions=['extra', 'tables', 'nl2br'])
    
    def render(self, slide: Slide) -> str:
        """Render a slide to HTML."""
        raise NotImplementedError
    
    def render_content_blocks(self, blocks: List[Any]) -> str:
        """Render a list of content blocks."""
        html_parts = []
        
        for block in blocks:
            if block.type == BlockType.MARKDOWN:
                # Render markdown content
                html = self.md.convert(block.content)
                html_parts.append(html)
            elif block.type == BlockType.COMPONENT:
                # Render component
                # Merge content into props if not already there
                props = block.props.copy()
                if block.content and 'content' not in props:
                    props['content'] = block.content
                
                html = self.registry.render(
                    block.component_type,
                    props
                )
                html_parts.append(html)
        
        return '\n'.join(html_parts)


class TitleTemplate(SlideTemplate):
    """Template for title slides."""
    
    def render(self, slide: Slide) -> str:
        # Extract title and subtitle from markdown blocks
        title = ""
        subtitle = ""
        other_content = []
        
        for block in slide.content_blocks:
            if block.type == BlockType.MARKDOWN:
                lines = block.content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# ') and not title:
                        title = line[2:].strip()
                    elif line.startswith('## ') and not subtitle:
                        subtitle = line[3:].strip()
                    else:
                        other_content.append(line)
            else:
                # Components go after title/subtitle
                props = block.props.copy()
                if block.content and 'content' not in props:
                    props['content'] = block.content
                other_content.append(self.registry.render(
                    block.component_type,
                    props
                ))
        
        # Build the slide
        slide_html = self.registry.render('slide-base', {
            'background': 'bg-gradient-to-br from-gray-50 to-blue-50',
            'children': f'''
                <div class="flex-1 flex flex-col justify-center items-center text-center">
                    <div class="mb-12">
                        <div class="w-24 h-1 bg-blue-600 mx-auto mb-12"></div>
                    </div>
                    <h1 class="text-8xl font-extrabold text-gray-900 mb-12 leading-tight tracking-tight max-w-5xl">{title}</h1>
                    {f'<h2 class="text-4xl text-gray-600 font-light mb-16 max-w-4xl">{subtitle}</h2>' if subtitle else ''}
                    <div class="text-2xl text-gray-600 font-light max-w-3xl">
                        {self.md.convert('\n'.join(other_content))}
                    </div>
                </div>
            '''
        })
        
        return slide_html


class StandardTemplate(SlideTemplate):
    """Template for standard content slides."""
    
    def render(self, slide: Slide) -> str:
        # Extract title from first markdown block if it's a header
        title = ""
        content_blocks = []
        
        for i, block in enumerate(slide.content_blocks):
            if i == 0 and block.type == BlockType.MARKDOWN:
                lines = block.content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                    # Keep remaining content
                    remaining = '\n'.join(lines[1:]).strip()
                    if remaining:
                        block.content = remaining
                        content_blocks.append(block)
                else:
                    content_blocks.append(block)
            else:
                content_blocks.append(block)
        
        # Render header
        header_html = self.registry.render('header', {
            'title': title,
            'subtitle': slide.metadata.get('subtitle', '')
        }) if title else ''
        
        # Render content
        content_html = self.render_content_blocks(content_blocks)
        
        # Render footer
        footer_html = self.registry.render('footer', {
            'slideNumber': slide.number,
            'text': ''
        })
        
        # Build the slide
        slide_html = self.registry.render('slide-base', {
            'children': f'''
                {header_html}
                <div class="flex-1 px-24 py-12">
                    {content_html}
                </div>
                {footer_html}
            '''
        })
        
        return slide_html


class MetricsTemplate(SlideTemplate):
    """Template for metrics-focused slides."""
    
    def render(self, slide: Slide) -> str:
        # Similar structure to standard but optimized for metrics display
        title = ""
        metrics_blocks = []
        other_blocks = []
        
        for i, block in enumerate(slide.content_blocks):
            if i == 0 and block.type == BlockType.MARKDOWN:
                lines = block.content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                    remaining = '\n'.join(lines[1:]).strip()
                    if remaining:
                        block.content = remaining
                        other_blocks.append(block)
            elif block.type == BlockType.COMPONENT and block.component_type == 'metrics':
                metrics_blocks.append(block)
            else:
                other_blocks.append(block)
        
        # Render header
        header_html = self.registry.render('header', {
            'title': title,
            'subtitle': slide.metadata.get('subtitle', '')
        }) if title else ''
        
        # Render metrics first, then other content
        content_parts = []
        for block in metrics_blocks:
            content_parts.append(self.registry.render(block.component_type, block.props))
        
        if other_blocks:
            content_parts.append('<div class="mt-12">')
            content_parts.append(self.render_content_blocks(other_blocks))
            content_parts.append('</div>')
        
        # Render footer
        footer_html = self.registry.render('footer', {
            'slideNumber': slide.number
        })
        
        # Build the slide
        slide_html = self.registry.render('slide-base', {
            'children': f'''
                {header_html}
                <div class="flex-1 px-24 py-12">
                    {' '.join(content_parts)}
                </div>
                {footer_html}
            '''
        })
        
        return slide_html


class ConclusionTemplate(SlideTemplate):
    """Template for conclusion/summary slides."""
    
    def render(self, slide: Slide) -> str:
        # Extract title
        title = "Summary"
        content_blocks = []
        
        for i, block in enumerate(slide.content_blocks):
            if i == 0 and block.type == BlockType.MARKDOWN:
                lines = block.content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                    remaining = '\n'.join(lines[1:]).strip()
                    if remaining:
                        block.content = remaining
                        content_blocks.append(block)
                else:
                    content_blocks.append(block)
            else:
                content_blocks.append(block)
        
        # Build the slide with emphasis styling
        slide_html = self.registry.render('slide-base', {
            'background': 'bg-white',
            'children': f'''
                <div class="w-full bg-gray-100 px-24 py-20 border-b-4 border-gray-900">
                    <h1 class="text-6xl font-bold text-gray-900">{title}</h1>
                </div>
                <div class="flex-1 px-24 py-16">
                    <div class="max-w-5xl mx-auto">
                        {self.render_content_blocks(content_blocks)}
                    </div>
                </div>
                <div class="px-24 py-8">
                    <div class="flex justify-end">
                        <div class="text-gray-600 font-semibold">{slide.number}</div>
                    </div>
                </div>
            '''
        })
        
        return slide_html


class ThankYouTemplate(SlideTemplate):
    """Template for thank you/closing slides."""
    
    def render(self, slide: Slide) -> str:
        # Extract content
        title = "Thank You!"
        content_parts = []
        
        for block in slide.content_blocks:
            if block.type == BlockType.MARKDOWN:
                lines = block.content.split('\n')
                if lines and lines[0].startswith('# '):
                    title = lines[0][2:].strip()
                    remaining = '\n'.join(lines[1:]).strip()
                    if remaining:
                        content_parts.append(self.md.convert(remaining))
                else:
                    content_parts.append(self.md.convert(block.content))
            else:
                content_parts.append(self.registry.render(
                    block.component_type,
                    block.props
                ))
        
        # Build centered thank you slide
        slide_html = self.registry.render('slide-base', {
            'background': 'bg-gray-50',
            'children': f'''
                <div class="flex-1 flex flex-col justify-center items-center px-24 text-center">
                    <h1 class="text-8xl font-bold text-gray-900 mb-12">{title}</h1>
                    <div class="text-2xl text-gray-700 space-y-4">
                        {' '.join(content_parts)}
                    </div>
                </div>
            '''
        })
        
        return slide_html


class MinimalTemplate(SlideTemplate):
    """Minimal template that renders exactly what Claude specifies."""
    
    def render(self, slide: Slide) -> str:
        # Just render the content blocks - no auto-extraction, no auto-components
        content_html = self.render_content_blocks(slide.content_blocks)
        
        # Wrap in slide-base but don't add anything else
        slide_html = self.registry.render('slide-base', {
            'children': f'''
                <div class="flex-1 px-24 py-12">
                    {content_html}
                </div>
            '''
        })
        
        return slide_html


class ManualTemplate(SlideTemplate):
    """Manual template where Claude controls every element explicitly."""
    
    def render(self, slide: Slide) -> str:
        # Get config if available
        show_header = slide.metadata.get('show_header', False)
        show_footer = slide.metadata.get('show_footer', False)
        header_title = slide.metadata.get('header_title', '')
        
        parts = []
        
        # Only add header if explicitly requested
        if show_header and header_title:
            parts.append(self.registry.render('header', {
                'title': header_title,
                'subtitle': slide.metadata.get('subtitle', '')
            }))
        
        # Render content
        parts.append(f'<div class="flex-1 px-24 py-12">')
        parts.append(self.render_content_blocks(slide.content_blocks))
        parts.append('</div>')
        
        # Only add footer if explicitly requested
        if show_footer:
            parts.append(self.registry.render('footer', {
                'slideNumber': slide.number,
                'text': slide.metadata.get('footer_text', '')
            }))
        
        # Build the slide
        slide_html = self.registry.render('slide-base', {
            'background': slide.metadata.get('background', 'bg-white'),
            'children': '\n'.join(parts)
        })
        
        return slide_html


class TemplateRegistry:
    """Registry for slide templates."""
    
    def __init__(self):
        self.component_registry = ComponentRegistry()
        self.templates = {
            # New minimal templates
            'minimal': MinimalTemplate(self.component_registry),
            'manual': ManualTemplate(self.component_registry),
            
            # Legacy templates (kept for backward compatibility)
            'title': TitleTemplate(self.component_registry),
            'standard': StandardTemplate(self.component_registry),
            'metrics': MetricsTemplate(self.component_registry),
            'conclusion': ConclusionTemplate(self.component_registry),
            'thank-you': ThankYouTemplate(self.component_registry),
        }
        
        # Aliases - default now points to minimal
        self.templates['default'] = self.templates['minimal']
        self.templates['summary'] = self.templates['conclusion']
    
    def get(self, template_name: str) -> SlideTemplate:
        """Get a template by name."""
        return self.templates.get(template_name, self.templates['minimal'])
    
    def render_slide(self, slide: Slide) -> str:
        """Render a slide using the appropriate template."""
        template = self.get(slide.template)
        return template.render(slide)
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        # Return unique template names (excluding aliases)
        return ['minimal', 'manual', 'title', 'standard', 'metrics', 'conclusion', 'thank-you']