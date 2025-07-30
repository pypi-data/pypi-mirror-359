"""
Component system for Slidesmith - Python-based HTML component rendering.
Replaces React components with Python template classes.
"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape
import markdown


class Component(ABC):
    """Base class for all slide components."""
    
    def __init__(self):
        self.env = Environment(
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    @abstractmethod
    def render(self, props: Dict[str, Any]) -> str:
        """Render the component to HTML."""
        pass
    
    def generate_id(self) -> str:
        """Generate a unique ID for component instances."""
        return f"component-{uuid.uuid4().hex[:8]}"
    
    def render_template(self, template_str: str, **context) -> str:
        """Render a Jinja2 template string with context."""
        template = self.env.from_string(template_str)
        return template.render(**context)


class SlideBaseComponent(Component):
    """Base container component for all slides."""
    
    def render(self, props: Dict[str, Any]) -> str:
        children = props.get('children', '')
        className = props.get('className', '')
        background = props.get('background', 'bg-white')
        
        template = '''
        <div 
            class="w-full min-h-screen flex flex-col items-start justify-between {{ background }} {{ className }}"
            style="width: 1920px; min-height: 1080px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
            {{ children | safe }}
        </div>
        '''
        
        return self.render_template(template, 
            children=children,
            className=className,
            background=background
        )


class HeaderComponent(Component):
    """Header component with title and optional subtitle."""
    
    def render(self, props: Dict[str, Any]) -> str:
        title = props.get('title', '')
        subtitle = props.get('subtitle', '')
        className = props.get('className', '')
        
        template = '''
        <div class="w-full px-24 py-16 border-b-2 border-gray-200 {{ className }}">
            <h1 class="text-5xl font-bold text-gray-900 mb-3">{{ title }}</h1>
            {% if subtitle %}
                <p class="text-xl text-gray-600">{{ subtitle }}</p>
            {% endif %}
        </div>
        '''
        
        return self.render_template(template,
            title=title,
            subtitle=subtitle,
            className=className
        )


class FooterComponent(Component):
    """Footer component with slide number and optional text."""
    
    def render(self, props: Dict[str, Any]) -> str:
        slideNumber = props.get('slideNumber', '')
        text = props.get('text', '')
        className = props.get('className', '')
        
        template = '''
        <div class="w-full px-24 py-8 flex justify-end items-center {{ className }}">
            {% if text %}
            <div class="text-gray-500 mr-auto">{{ text }}</div>
            {% endif %}
            <div class="text-gray-500 font-medium">{{ slideNumber }}</div>
        </div>
        '''
        
        return self.render_template(template,
            slideNumber=slideNumber,
            text=text,
            className=className
        )


class ColumnsComponent(Component):
    """Columns layout component."""
    
    def render(self, props: Dict[str, Any]) -> str:
        sections = props.get('sections', [])
        ratio = props.get('ratio', '1:1')
        gap = props.get('gap', 8)
        className = props.get('className', '')
        
        # Parse ratio
        ratio_parts = ratio.split(':')
        if len(ratio_parts) != 2:
            ratio_parts = ['1', '1']
        
        total = int(ratio_parts[0]) + int(ratio_parts[1])
        left_cols = round(12 * int(ratio_parts[0]) / total)
        right_cols = 12 - left_cols
        
        # Process sections content
        processed_sections = []
        md = markdown.Markdown(extensions=['extra', 'tables'])
        
        for section in sections[:2]:  # Only take first 2 sections
            if isinstance(section, dict):
                content = section.get('content', '')
                title = section.get('title', '')
            else:
                content = str(section)
                title = ''
            
            # Process nested components in content
            html_content = self._process_content(content, md)
            processed_sections.append({
                'title': title,
                'content': html_content
            })
        
        template = '''
        <div class="grid grid-cols-12 gap-{{ gap }} {{ className }}">
            {% if sections|length > 0 %}
            <div class="col-span-{{ left_cols }}">
                {% if sections[0].title %}
                    <h3 class="text-2xl font-bold mb-4">{{ sections[0].title }}</h3>
                {% endif %}
                {{ sections[0].content | safe }}
            </div>
            {% endif %}
            {% if sections|length > 1 %}
            <div class="col-span-{{ right_cols }}">
                {% if sections[1].title %}
                    <h3 class="text-2xl font-bold mb-4">{{ sections[1].title }}</h3>
                {% endif %}
                {{ sections[1].content | safe }}
            </div>
            {% endif %}
        </div>
        '''
        
        return self.render_template(template,
            sections=processed_sections,
            left_cols=left_cols,
            right_cols=right_cols,
            gap=gap,
            className=className
        )
    
    def _process_content(self, content: str, md) -> str:
        """Process content for nested components and markdown."""
        # If content is already HTML (contains HTML tags), return as-is
        if '<' in content and '>' in content:
            return content
        # Otherwise render as markdown
        return md.convert(content)


class CardComponent(Component):
    """Card component with icon, title, and content."""
    
    def render(self, props: Dict[str, Any]) -> str:
        title = props.get('title', '')
        icon = props.get('icon', '')
        color = props.get('color', 'blue')
        content = props.get('content', '')
        className = props.get('className', '')
        
        # Color mapping
        color_map = {
            'blue': {
                'bg': 'bg-blue-100',
                'icon': 'text-blue-700',
                'border': 'border-blue-200'
            },
            'green': {
                'bg': 'bg-green-100',
                'icon': 'text-green-700',
                'border': 'border-green-200'
            },
            'red': {
                'bg': 'bg-red-100',
                'icon': 'text-red-700',
                'border': 'border-red-200'
            },
            'yellow': {
                'bg': 'bg-yellow-100',
                'icon': 'text-yellow-700',
                'border': 'border-yellow-200'
            },
            'purple': {
                'bg': 'bg-purple-100',
                'icon': 'text-purple-700',
                'border': 'border-purple-200'
            }
        }
        
        colors = color_map.get(color, color_map['blue'])
        
        template = '''
        <div class="bg-white border {{ colors.border }} rounded-lg p-6 {{ className }}">
            {% if icon or title %}
            <div class="flex items-center mb-4">
                {% if icon %}
                <div class="h-12 w-12 rounded-full {{ colors.bg }} flex items-center justify-center mr-4">
                    <i class="fas fa-{{ icon }} text-2xl {{ colors.icon }}"></i>
                </div>
                {% endif %}
                {% if title %}
                <h3 class="text-2xl font-bold text-gray-900">{{ title }}</h3>
                {% endif %}
            </div>
            {% endif %}
            <div class="text-gray-700">
                {{ content | safe }}
            </div>
        </div>
        '''
        
        return self.render_template(template,
            title=title,
            icon=icon,
            colors=colors,
            content=content,
            className=className
        )


class MetricsComponent(Component):
    """Metrics display component."""
    
    def render(self, props: Dict[str, Any]) -> str:
        items = props.get('items', [])
        className = props.get('className', '')
        
        template = '''
        <div class="grid grid-cols-{{ cols }} gap-8 {{ className }}">
            {% for item in items %}
            <div class="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center">
                <div class="text-5xl font-bold text-gray-900 mb-2">{{ item.value }}</div>
                <div class="text-xl text-gray-600 font-medium mb-2">{{ item.label }}</div>
                {% if item.trend %}
                <div class="text-sm text-green-600 font-medium">{{ item.trend }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        '''
        
        cols = min(len(items), 4)  # Max 4 columns
        
        return self.render_template(template,
            items=items,
            cols=cols,
            className=className
        )


class ChartComponent(Component):
    """Chart component (bar, pie, line, etc)."""
    
    def render(self, props: Dict[str, Any]) -> str:
        chart_type = props.get('type', 'bar')
        title = props.get('title', '')
        data = props.get('data', [])
        labels = props.get('labels', [])
        colors = props.get('colors', None)
        height = props.get('height', 300)
        className = props.get('className', '')
        
        chart_id = self.generate_id()
        
        # Default colors
        if not colors:
            colors = ['#374151', '#6B7280', '#9CA3AF', '#3B82F6', '#10B981', '#F59E0B']
        
        # Prepare chart config
        config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors[:len(data)],
                    'borderWidth': 0
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': chart_type == 'pie',
                        'position': 'bottom'
                    },
                    'title': {
                        'display': bool(title),
                        'text': title,
                        'font': {
                            'size': 20,
                            'family': "'Montserrat', sans-serif",
                            'weight': '600'
                        },
                        'padding': {
                            'bottom': 30
                        }
                    }
                }
            }
        }
        
        if chart_type == 'bar':
            config['options']['scales'] = {
                'y': {
                    'beginAtZero': True,
                    'grid': {
                        'color': '#E5E7EB'
                    }
                }
            }
        
        template = '''
        <div class="bg-white {{ className }}">
            <div style="height: {{ height }}px">
                <canvas id="{{ chart_id }}"></canvas>
            </div>
            <script>
                (function() {
                    const ctx = document.getElementById('{{ chart_id }}').getContext('2d');
                    new Chart(ctx, {{ config | tojson }});
                })();
            </script>
        </div>
        '''
        
        return self.render_template(template,
            chart_id=chart_id,
            height=height,
            config=config,
            className=className
        )


class TableComponent(Component):
    """Table component with markdown support."""
    
    def render(self, props: Dict[str, Any]) -> str:
        markdown_content = props.get('markdown', '')
        className = props.get('className', '')
        
        # Parse markdown table
        md = markdown.Markdown(extensions=['tables', 'extra'])
        table_html = md.convert(markdown_content)
        
        # Wrap with styling
        template = '''
        <div class="{{ className }}">
            <div class="overflow-x-auto">
                <div class="inline-block min-w-full">
                    <div class="overflow-hidden rounded-lg shadow">
                        {{ table_html | safe }}
                    </div>
                </div>
            </div>
        </div>
        <style>
            /* Style the generated table */
            table {
                min-width: 100%;
                border-collapse: collapse;
            }
            
            thead {
                background-color: #F3F4F6;
            }
            
            th {
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                color: #374151;
                border-bottom: 1px solid #E5E7EB;
            }
            
            tbody tr {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
            }
            
            tbody tr:hover {
                background-color: #F9FAFB;
            }
            
            td {
                padding: 12px 16px;
                color: #6B7280;
            }
        </style>
        '''
        
        return self.render_template(template,
            table_html=table_html,
            className=className
        )


class CalloutComponent(Component):
    """Callout/alert component."""
    
    def render(self, props: Dict[str, Any]) -> str:
        content = props.get('content', '')
        callout_type = props.get('type', 'info')
        className = props.get('className', '')
        
        # Type styling
        type_map = {
            'info': {
                'bg': 'bg-blue-50',
                'border': 'border-blue-200',
                'icon': 'fa-info-circle',
                'icon_color': 'text-blue-600',
                'text': 'text-blue-800'
            },
            'success': {
                'bg': 'bg-green-50',
                'border': 'border-green-200',
                'icon': 'fa-check-circle',
                'icon_color': 'text-green-600',
                'text': 'text-green-800'
            },
            'warning': {
                'bg': 'bg-yellow-50',
                'border': 'border-yellow-200',
                'icon': 'fa-exclamation-triangle',
                'icon_color': 'text-yellow-600',
                'text': 'text-yellow-800'
            },
            'error': {
                'bg': 'bg-red-50',
                'border': 'border-red-200',
                'icon': 'fa-times-circle',
                'icon_color': 'text-red-600',
                'text': 'text-red-800'
            }
        }
        
        styles = type_map.get(callout_type, type_map['info'])
        
        template = '''
        <div class="{{ styles.bg }} {{ styles.border }} border rounded-lg p-6 {{ className }}">
            <div class="flex items-start">
                <i class="fas {{ styles.icon }} {{ styles.icon_color }} text-xl mr-3 mt-1"></i>
                <div class="{{ styles.text }}">
                    {{ content | safe }}
                </div>
            </div>
        </div>
        '''
        
        return self.render_template(template,
            content=content,
            styles=styles,
            className=className
        )


class TimelineComponent(Component):
    """Timeline component for showing progression."""
    
    def render(self, props: Dict[str, Any]) -> str:
        items = props.get('items', [])
        className = props.get('className', '')
        
        template = '''
        <div class="relative {{ className }}">
            {% for item in items %}
            <div class="flex items-start mb-8 {% if not loop.last %}pb-8 border-l-2 border-gray-300 ml-4{% endif %}">
                <div class="bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center {% if not loop.last %}-ml-4{% endif %}">
                    <span class="text-white font-bold text-sm">{{ loop.index }}</span>
                </div>
                <div class="ml-6 flex-1">
                    <div class="text-sm text-gray-500 mb-1">{{ item.date }}</div>
                    <h4 class="text-xl font-bold text-gray-800 mb-2">{{ item.title }}</h4>
                    {% if item.description %}
                    <p class="text-gray-600">{{ item.description }}</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        '''
        
        return self.render_template(template,
            items=items,
            className=className
        )


class GridComponent(Component):
    """Grid layout component."""
    
    def render(self, props: Dict[str, Any]) -> str:
        sections = props.get('sections', [])
        cols = props.get('cols', 3)
        gap = props.get('gap', 4)
        className = props.get('className', '')
        
        # Process sections
        md = markdown.Markdown(extensions=['extra', 'tables'])
        processed_sections = []
        
        for section in sections:
            if isinstance(section, dict):
                content = section.get('content', '')
                title = section.get('title', '')
            else:
                content = str(section)
                title = ''
            
            html_content = md.convert(content)
            processed_sections.append({
                'title': title,
                'content': html_content
            })
        
        template = '''
        <div class="grid grid-cols-{{ cols }} gap-{{ gap }} {{ className }}">
            {% for section in sections %}
            <div>
                {% if section.title %}
                    <h3 class="text-xl font-bold mb-3">{{ section.title }}</h3>
                {% endif %}
                <div class="text-gray-700">
                    {{ section.content | safe }}
                </div>
            </div>
            {% endfor %}
        </div>
        '''
        
        return self.render_template(template,
            sections=processed_sections,
            cols=cols,
            gap=gap,
            className=className
        )


class CodeComponent(Component):
    """Code block component with syntax highlighting."""
    
    def render(self, props: Dict[str, Any]) -> str:
        content = props.get('content', '')
        language = props.get('language', 'text')
        className = props.get('className', '')
        
        # For now, use basic pre/code formatting
        # TODO: Add syntax highlighting with Pygments
        template = '''
        <div class="rounded-lg overflow-hidden {{ className }}">
            <div class="bg-gray-800 px-4 py-2 text-sm text-gray-400">
                {{ language }}
            </div>
            <pre class="bg-gray-900 p-4 overflow-x-auto"><code class="text-gray-300 text-sm">{{ content }}</code></pre>
        </div>
        '''
        
        return self.render_template(template,
            content=content,
            language=language,
            className=className
        )


class ImageComponent(Component):
    """Image component with caption support."""
    
    def render(self, props: Dict[str, Any]) -> str:
        src = props.get('src', '')
        alt = props.get('alt', '')
        caption = props.get('caption', '')
        width = props.get('width', None)
        height = props.get('height', None)
        className = props.get('className', '')
        
        style_parts = []
        if width:
            style_parts.append(f"width: {width}px")
        if height:
            style_parts.append(f"height: {height}px")
        
        style = "; ".join(style_parts) if style_parts else ""
        
        template = '''
        <figure class="{{ className }}">
            <img 
                src="{{ src }}" 
                alt="{{ alt }}"
                {% if style %}style="{{ style }}"{% endif %}
                class="rounded-lg shadow-lg"
            />
            {% if caption %}
            <figcaption class="mt-2 text-sm text-gray-600 text-center">
                {{ caption }}
            </figcaption>
            {% endif %}
        </figure>
        '''
        
        return self.render_template(template,
            src=src,
            alt=alt,
            caption=caption,
            style=style,
            className=className
        )


class SpeakerNotesComponent(Component):
    """Speaker notes component (hidden in presentation)."""
    
    def render(self, props: Dict[str, Any]) -> str:
        content = props.get('content', '')
        
        # Speaker notes are hidden in normal view
        template = '''
        <div class="speaker-notes hidden" data-speaker-notes>
            {{ content | safe }}
        </div>
        '''
        
        return self.render_template(template, content=content)


class ComponentRegistry:
    """Registry for all available components."""
    
    def __init__(self):
        self.components = {
            # Layout components
            'slide-base': SlideBaseComponent(),
            'header': HeaderComponent(),
            'footer': FooterComponent(),
            'columns': ColumnsComponent(),
            'grid': GridComponent(),
            
            # Content components
            'card': CardComponent(),
            'callout': CalloutComponent(),
            'table': TableComponent(),
            'code': CodeComponent(),
            'image': ImageComponent(),
            'speaker-notes': SpeakerNotesComponent(),
            
            # Data visualization
            'chart': ChartComponent(),
            'metrics': MetricsComponent(),
            'timeline': TimelineComponent(),
        }
    
    def get(self, component_type: str) -> Optional[Component]:
        """Get a component by type."""
        return self.components.get(component_type)
    
    def render(self, component_type: str, props: Dict[str, Any]) -> str:
        """Render a component by type."""
        component = self.get(component_type)
        if not component:
            raise ValueError(f"Unknown component type: {component_type}")
        return component.render(props)
    
    def list_components(self) -> List[str]:
        """List all available component types."""
        return list(self.components.keys())