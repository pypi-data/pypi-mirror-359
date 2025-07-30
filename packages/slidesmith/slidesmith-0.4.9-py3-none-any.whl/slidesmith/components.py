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
        show_slide_number = props.get('show_slide_number', False)
        
        template = '''
        <div 
            class="relative w-full h-full flex flex-col {{ background }} {{ className }}"
            style="width: 1920px; height: 1080px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 80px;">
            <div class="flex-1 flex flex-col justify-between">
                {{ children | safe }}
            </div>
            {% if show_slide_number %}
            <!-- Slide number -->
            <div class="absolute bottom-8 right-12 text-gray-400 text-lg font-medium">
                <span class="slide-number"></span>
            </div>
            {% endif %}
        </div>
        '''
        
        return self.render_template(template, 
            children=children,
            className=className,
            background=background,
            show_slide_number=show_slide_number
        )


class HeaderComponent(Component):
    """Header component with title and optional subtitle."""
    
    def render(self, props: Dict[str, Any]) -> str:
        title = props.get('title', '')
        subtitle = props.get('subtitle', '')
        className = props.get('className', '')
        
        template = '''
        <div class="w-full {{ className }}">
            <div class="flex items-center justify-between mb-12">
                <div class="w-48 h-1 bg-gradient-to-r from-blue-600 to-blue-400"></div>
                <div class="text-gray-400 font-medium">SLIDESMITH</div>
            </div>
            <h1 class="text-7xl font-bold text-gray-900 mb-6 leading-tight">{{ title }}</h1>
            {% if subtitle %}
                <p class="text-3xl text-gray-600 font-light">{{ subtitle }}</p>
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
        
        # Process sections content with nested component support
        processed_sections = []
        md = markdown.Markdown(extensions=['extra', 'tables'])
        
        for section in sections[:2]:  # Only take first 2 sections
            if isinstance(section, dict):
                content = section.get('content', '')
                title = section.get('title', '')
                blocks = section.get('blocks', [])
                
                # Render blocks if they exist
                if blocks:
                    html_content = self._render_blocks(blocks)
                else:
                    # Fallback to markdown conversion for content
                    html_content = self._process_content(content, md)
            else:
                content = str(section)
                title = ''
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
    
    def _render_blocks(self, blocks):
        """Render a list of content blocks."""
        from .parser import BlockType
        html_parts = []
        md = markdown.Markdown(extensions=['extra', 'tables'])
        
        for block in blocks:
            if block.type == BlockType.MARKDOWN:
                html_parts.append(md.convert(block.content))
            elif block.type == BlockType.COMPONENT:
                # Get the registry from the component registry
                component_registry = ComponentRegistry()
                component = component_registry.get(block.component_type)
                if component:
                    # Make sure to include content in props for components that need it
                    render_props = dict(block.props)
                    if block.content and 'content' not in render_props:
                        render_props['content'] = block.content
                    html_parts.append(component.render(render_props))
                else:
                    html_parts.append(f"<!-- Unknown component: {block.component_type} -->")
        
        return '\n'.join(html_parts)


class CardComponent(Component):
    """Card component with icon, title, and content."""
    
    def render(self, props: Dict[str, Any]) -> str:
        title = props.get('title', '')
        icon = props.get('icon', '')
        color = props.get('color', 'blue')
        # Support both 'content' and 'children' props
        content = props.get('content', '') or props.get('children', '')
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
        <div class="group relative bg-white border-2 {{ colors.border }} rounded-2xl p-10 shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 ease-out {{ className }}">
            <!-- Animated background gradient -->
            <div class="absolute inset-0 bg-gradient-to-br from-transparent via-{{ colors.bg }}/5 to-{{ colors.bg }}/10 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            <!-- Content -->
            <div class="relative z-10">
                {% if icon or title %}
                <div class="flex items-center mb-6">
                    {% if icon %}
                    <div class="h-16 w-16 rounded-2xl {{ colors.bg }} flex items-center justify-center mr-6 shadow-md group-hover:scale-110 group-hover:shadow-lg transition-all duration-300">
                        <i class="fas fa-{{ icon }} text-3xl {{ colors.icon }} group-hover:animate-pulse"></i>
                    </div>
                    {% endif %}
                    {% if title %}
                    <h3 class="text-3xl font-bold text-gray-900 group-hover:text-gray-800 transition-colors duration-300">{{ title }}</h3>
                    {% endif %}
                </div>
                {% endif %}
                <div class="text-xl text-gray-700 leading-relaxed group-hover:text-gray-600 transition-colors duration-300">
                    {{ content | safe }}
                </div>
            </div>
            
            <!-- Hover border glow -->
            <div class="absolute inset-0 rounded-2xl border-2 border-{{ colors.border }} opacity-0 group-hover:opacity-30 group-hover:border-{{ colors.icon }} transition-all duration-300"></div>
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
        
        # Color palette for metrics
        colors = [
            'from-blue-500 to-blue-600',
            'from-green-500 to-green-600',
            'from-purple-500 to-purple-600',
            'from-orange-500 to-orange-600',
        ]
        
        template = '''
        <div class="grid grid-cols-{{ cols }} gap-12 {{ className }}">
            {% for item in items %}
            <div class="relative group cursor-pointer">
                <div class="absolute inset-0 bg-gradient-to-r {{ colors[loop.index0 % colors|length] }} rounded-2xl opacity-10 group-hover:opacity-25 transition-all duration-500"></div>
                <div class="relative bg-white rounded-2xl shadow-lg group-hover:shadow-2xl p-10 text-center border border-gray-100 transform group-hover:-translate-y-3 group-hover:scale-105 transition-all duration-500 ease-out">
                    <div class="text-6xl font-bold bg-gradient-to-r {{ colors[loop.index0 % colors|length] }} bg-clip-text text-transparent mb-4 group-hover:scale-110 transition-transform duration-300">
                        {{ item.value }}
                    </div>
                    <div class="text-2xl text-gray-700 font-semibold mb-2 group-hover:text-gray-800 transition-colors duration-300">{{ item.label }}</div>
                    {% if item.change %}
                    <div class="flex items-center justify-center gap-2 text-lg font-medium">
                        <span class="{% if item.trend == 'up' %}text-green-600{% elif item.trend == 'down' %}text-red-600{% else %}text-gray-600{% endif %}">
                            {{ item.change }}
                        </span>
                        {% if item.trend == 'up' %}
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
                        </svg>
                        {% elif item.trend == 'down' %}
                        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
                        </svg>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        '''
        
        cols = min(len(items), 4)  # Max 4 columns
        
        return self.render_template(template,
            items=items,
            cols=cols,
            colors=colors,
            className=className
        )


class ChartComponent(Component):
    """
    Chart component supporting multiple chart types:
    - bar: Bar charts with Y-axis scaling
    - line: Line charts with smooth curves 
    - pie: Pie charts with legends
    - doughnut: Doughnut charts with optional center text
    - scatter: Scatter plots with X/Y coordinates
    - radar: Radar/spider charts for multi-dimensional data
    
    Examples:
    :::chart type=scatter title="Performance Analysis"
    {"labels": ["Team A", "Team B"], "data": [{"x": 85, "y": 92}, {"x": 78, "y": 88}]}
    :::
    
    :::chart type=radar title="Skills Assessment"
    {"labels": ["Frontend", "Backend", "DevOps"], "data": [85, 90, 75]}
    :::
    
    :::chart type=doughnut title="Market Share" centerText="2024"
    {"labels": ["Product A", "Product B", "Product C"], "data": [40, 35, 25]}
    :::
    """
    
    def render(self, props: Dict[str, Any]) -> str:
        chart_type = props.get('type', 'bar')
        title = props.get('title', '')
        data = props.get('data', [])
        labels = props.get('labels', [])
        label = props.get('label', '')
        backgroundColor = props.get('backgroundColor', None)
        borderColor = props.get('borderColor', None)
        borderWidth = props.get('borderWidth', 0)
        colors = props.get('colors', None)
        height = props.get('height', 300)
        className = props.get('className', '')
        
        chart_id = self.generate_id()
        
        # Default colors
        if not colors and not backgroundColor:
            colors = ['#374151', '#6B7280', '#9CA3AF', '#3B82F6', '#10B981', '#F59E0B']
        
        # Prepare dataset
        dataset = {
            'data': data,
            'label': label,
            'borderWidth': borderWidth
        }
        
        # Handle colors
        if backgroundColor:
            dataset['backgroundColor'] = backgroundColor
        elif colors:
            dataset['backgroundColor'] = colors[:len(data)]
            
        if borderColor:
            dataset['borderColor'] = borderColor
        
        # Prepare chart config
        config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': [dataset]
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
        
        # Chart-specific configurations
        if chart_type == 'bar':
            config['options']['scales'] = {
                'y': {
                    'beginAtZero': True,
                    'grid': {
                        'color': '#E5E7EB'
                    }
                }
            }
        elif chart_type == 'line':
            config['options']['scales'] = {
                'y': {
                    'beginAtZero': True,
                    'grid': {
                        'color': '#E5E7EB'
                    }
                }
            }
            # Add tension for smoother lines
            dataset['tension'] = 0.4
        elif chart_type == 'scatter':
            config['options']['scales'] = {
                'x': {
                    'type': 'linear',
                    'position': 'bottom',
                    'grid': {
                        'color': '#E5E7EB'
                    }
                },
                'y': {
                    'beginAtZero': True,
                    'grid': {
                        'color': '#E5E7EB'
                    }
                }
            }
            # For scatter plots, data should be array of {x, y} objects
            dataset['pointBackgroundColor'] = backgroundColor or colors[0] if colors else '#3B82F6'
            dataset['pointBorderColor'] = borderColor or '#1E40AF'
            dataset['pointRadius'] = 6
        elif chart_type == 'radar':
            config['options'] = {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': config['options']['plugins'],
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'grid': {
                            'color': '#E5E7EB'
                        },
                        'angleLines': {
                            'color': '#E5E7EB'
                        },
                        'pointLabels': {
                            'font': {
                                'size': 12
                            }
                        }
                    }
                }
            }
            dataset['fill'] = True
            dataset['backgroundColor'] = backgroundColor or 'rgba(59, 130, 246, 0.2)'
            dataset['borderColor'] = borderColor or '#3B82F6'
            dataset['pointBackgroundColor'] = '#3B82F6'
        elif chart_type == 'doughnut':
            config['options']['plugins']['legend']['display'] = True
            config['options']['cutout'] = '70%'  # Makes it a doughnut instead of pie
            # Add center text for doughnut charts
            center_text = props.get('centerText', '')
            if center_text:
                config['options']['plugins']['centerText'] = center_text
        elif chart_type == 'pie':
            config['options']['plugins']['legend']['display'] = True
        
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
        <div class="group relative {{ styles.bg }} {{ styles.border }} border rounded-lg p-6 hover:shadow-lg transform hover:scale-[1.02] transition-all duration-300 ease-out {{ className }}">
            <div class="flex items-start relative z-10">
                <div class="flex-shrink-0 w-8 h-8 rounded-full {{ styles.bg }} flex items-center justify-center group-hover:scale-110 transition-transform duration-300 border {{ styles.border }}">
                    <i class="fas {{ styles.icon }} {{ styles.icon_color }} text-lg group-hover:animate-bounce"></i>
                </div>
                <div class="{{ styles.text }} ml-4 group-hover:text-gray-800 transition-colors duration-300">
                    {{ content | safe }}
                </div>
            </div>
            
            <!-- Animated border glow -->
            <div class="absolute inset-0 rounded-lg border-2 {{ styles.border }} opacity-0 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none"></div>
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
            <div class="flex items-start mb-12 {% if not loop.last %}pb-12{% endif %}">
                <!-- Timeline line -->
                {% if not loop.last %}
                <div class="absolute left-8 top-16 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 to-blue-200"></div>
                {% endif %}
                
                <!-- Timeline dot and content -->
                <div class="relative z-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl w-16 h-16 flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300 cursor-pointer group">
                    <span class="text-white font-bold text-xl group-hover:animate-pulse">{{ loop.index }}</span>
                </div>
                <div class="ml-8 flex-1 group">
                    <div class="bg-white rounded-2xl shadow-md hover:shadow-xl p-8 border border-gray-100 hover:border-blue-200 transform hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                        <div class="text-lg text-blue-600 font-semibold mb-2 group-hover:text-blue-700 transition-colors duration-300">{{ item.date }}</div>
                        <h4 class="text-2xl font-bold text-gray-800 mb-3 group-hover:text-gray-900 transition-colors duration-300">{{ item.title }}</h4>
                        {% if item.description %}
                        <p class="text-lg text-gray-600 leading-relaxed group-hover:text-gray-700 transition-colors duration-300">{{ item.description }}</p>
                        {% endif %}
                    </div>
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
        
        # Process sections with nested component support
        md = markdown.Markdown(extensions=['extra', 'tables'])
        processed_sections = []
        
        for section in sections:
            if isinstance(section, dict):
                content = section.get('content', '')
                title = section.get('title', '')
                blocks = section.get('blocks', [])
                
                # Render blocks if they exist
                if blocks:
                    html_content = self._render_blocks(blocks)
                else:
                    # Fallback to markdown conversion for content
                    html_content = md.convert(content) if content else ''
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
    
    def _render_blocks(self, blocks):
        """Render a list of content blocks."""
        from .parser import BlockType
        html_parts = []
        md = markdown.Markdown(extensions=['extra', 'tables'])
        
        for block in blocks:
            if block.type == BlockType.MARKDOWN:
                html_parts.append(md.convert(block.content))
            elif block.type == BlockType.COMPONENT:
                # Get the registry from the component registry
                component_registry = ComponentRegistry()
                component = component_registry.get(block.component_type)
                if component:
                    # Make sure to include content in props for components that need it
                    render_props = dict(block.props)
                    if block.content and 'content' not in render_props:
                        render_props['content'] = block.content
                    html_parts.append(component.render(render_props))
                else:
                    html_parts.append(f"<!-- Unknown component: {block.component_type} -->")
        
        return '\n'.join(html_parts)


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
    """Speaker notes component - visible only in presentation mode for presenters."""
    
    def render(self, props: Dict[str, Any]) -> str:
        content = props.get('content', '')
        
        # Process markdown content if provided
        if content:
            # Simple markdown processing for speaker notes
            md = markdown.Markdown(extensions=['nl2br'])
            content = md.convert(content)
        
        # Speaker notes are hidden in normal view, visible in presentation mode
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