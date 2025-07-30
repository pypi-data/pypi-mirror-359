"""
Component documentation and discovery system.
Provides comprehensive information about available components, their usage, and examples.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ComponentExample:
    """Example usage of a component."""
    title: str
    description: str
    markdown: str
    props: Dict[str, Any]


@dataclass
class ComponentDoc:
    """Complete documentation for a component."""
    name: str
    display_name: str
    description: str
    category: str
    tags: List[str]
    props: Dict[str, Any]
    examples: List[ComponentExample]
    use_cases: List[str]
    related_components: List[str]


class ComponentDocumentationRegistry:
    """Registry for component documentation and discovery."""
    
    def __init__(self):
        self.docs = self._build_component_docs()
    
    def _build_component_docs(self) -> Dict[str, ComponentDoc]:
        """Build comprehensive documentation for all components."""
        return {
            'card': ComponentDoc(
                name='card',
                display_name='Card',
                description='Versatile content container with optional icon, title, and call-to-action elements',
                category='content',
                tags=['container', 'content', 'highlight', 'feature'],
                props={
                    'title': {'type': 'string', 'required': False, 'description': 'Card title/heading'},
                    'icon': {'type': 'string', 'required': False, 'description': 'FontAwesome icon name'},
                    'color': {'type': 'string', 'required': False, 'description': 'Card color theme', 'options': ['primary', 'secondary', 'success', 'warning', 'error']},
                    'content': {'type': 'markdown', 'required': False, 'description': 'Card body content (supports markdown)'}
                },
                examples=[
                    ComponentExample(
                        title='Basic Feature Card',
                        description='Simple card highlighting a key feature',
                        markdown=':::card title="Advanced Analytics" icon="chart-line"\nGet deep insights into your data with real-time analytics and custom dashboards.\n:::',
                        props={'title': 'Advanced Analytics', 'icon': 'chart-line'}
                    ),
                    ComponentExample(
                        title='Warning Card',
                        description='Card with warning styling for important notices',
                        markdown=':::card title="Important Notice" icon="exclamation-triangle" color="warning"\nThis feature will be deprecated in the next version. Please migrate to the new API.\n:::',
                        props={'title': 'Important Notice', 'icon': 'exclamation-triangle', 'color': 'warning'}
                    )
                ],
                use_cases=[
                    'Feature highlights on landing pages',
                    'Service descriptions',
                    'Key benefits overview',
                    'Important notices and alerts',
                    'Product feature callouts'
                ],
                related_components=['callout', 'grid', 'columns']
            ),
            
            'callout': ComponentDoc(
                name='callout',
                display_name='Callout',
                description='Attention-grabbing information boxes with semantic styling for different message types',
                category='content',
                tags=['alert', 'notification', 'message', 'emphasis'],
                props={
                    'type': {'type': 'string', 'required': True, 'description': 'Callout type', 'options': ['info', 'success', 'warning', 'error']},
                    'title': {'type': 'string', 'required': False, 'description': 'Callout title'},
                    'content': {'type': 'markdown', 'required': False, 'description': 'Callout content (supports markdown)'}
                },
                examples=[
                    ComponentExample(
                        title='Information Callout',
                        description='Blue-styled callout for general information',
                        markdown=':::callout type="info" title="Pro Tip"\nUse keyboard shortcuts to navigate slides faster: → for next, ← for previous.\n:::',
                        props={'type': 'info', 'title': 'Pro Tip'}
                    ),
                    ComponentExample(
                        title='Success Message',
                        description='Green callout for success messages',
                        markdown=':::callout type="success" title="Deployment Complete"\nYour application has been successfully deployed to production.\n:::',
                        props={'type': 'success', 'title': 'Deployment Complete'}
                    )
                ],
                use_cases=[
                    'Important announcements',
                    'Tips and best practices',
                    'Warnings and cautions',
                    'Success confirmations',
                    'Error messages and troubleshooting'
                ],
                related_components=['card', 'metrics']
            ),
            
            'chart': ComponentDoc(
                name='chart',
                display_name='Chart',
                description='Interactive data visualization using Chart.js with support for multiple chart types',
                category='data',
                tags=['visualization', 'data', 'analytics', 'graph'],
                props={
                    'type': {'type': 'string', 'required': True, 'description': 'Chart type', 'options': ['bar', 'line', 'pie', 'doughnut', 'scatter', 'radar']},
                    'title': {'type': 'string', 'required': False, 'description': 'Chart title'},
                    'data': {'type': 'json', 'required': True, 'description': 'Chart.js data object with labels and datasets'},
                    'options': {'type': 'json', 'required': False, 'description': 'Chart.js options for customization'}
                },
                examples=[
                    ComponentExample(
                        title='Revenue Growth Chart',
                        description='Bar chart showing monthly revenue growth',
                        markdown=''':::chart type="bar" title="Monthly Revenue Growth"
```json
{
  "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  "datasets": [{
    "label": "Revenue ($K)",
    "data": [45, 52, 48, 61, 58, 67],
    "backgroundColor": "#3B82F6"
  }]
}
```
:::''',
                        props={'type': 'bar', 'title': 'Monthly Revenue Growth'}
                    ),
                    ComponentExample(
                        title='User Distribution Pie Chart',
                        description='Pie chart showing user distribution by region',
                        markdown=''':::chart type="pie" title="User Distribution by Region"
```json
{
  "labels": ["North America", "Europe", "Asia", "Other"],
  "datasets": [{
    "data": [45, 30, 20, 5],
    "backgroundColor": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
  }]
}
```
:::''',
                        props={'type': 'pie', 'title': 'User Distribution by Region'}
                    )
                ],
                use_cases=[
                    'Financial reports and metrics',
                    'Performance dashboards',
                    'Market research presentations',
                    'User analytics and insights',
                    'Progress tracking and KPIs'
                ],
                related_components=['metrics', 'grid']
            ),
            
            'metrics': ComponentDoc(
                name='metrics',
                display_name='Metrics',
                description='Display key performance indicators and statistics with trend indicators and formatting',
                category='data',
                tags=['kpi', 'statistics', 'numbers', 'performance'],
                props={
                    'data': {'type': 'json', 'required': True, 'description': 'Metrics data object with values, changes, and trends'}
                },
                examples=[
                    ComponentExample(
                        title='Business KPIs',
                        description='Key business metrics with trend indicators',
                        markdown=''':::metrics
```json
{
  "revenue": {"value": "$2.4M", "change": "+12%", "trend": "up", "color": "success"},
  "users": {"value": "15,234", "change": "+8%", "trend": "up", "color": "success"},
  "conversion": {"value": "3.2%", "change": "-0.5%", "trend": "down", "color": "warning"}
}
```
:::''',
                        props={}
                    )
                ],
                use_cases=[
                    'Executive dashboards',
                    'Performance reports',
                    'Financial overviews',
                    'Product metrics',
                    'Growth tracking'
                ],
                related_components=['chart', 'card']
            ),
            
            'timeline': ComponentDoc(
                name='timeline',
                display_name='Timeline',
                description='Chronological display of events, milestones, or processes with dates and descriptions',
                category='content',
                tags=['events', 'chronology', 'milestones', 'roadmap'],
                props={
                    'events': {'type': 'json', 'required': True, 'description': 'Array of timeline events with dates, titles, and descriptions'}
                },
                examples=[
                    ComponentExample(
                        title='Product Roadmap',
                        description='Timeline showing product development milestones',
                        markdown=''':::timeline
```json
[
  {"date": "2024 Q1", "title": "Beta Launch", "description": "Initial beta release to select customers"},
  {"date": "2024 Q2", "title": "Public Launch", "description": "Full public release with core features"},
  {"date": "2024 Q3", "title": "Mobile App", "description": "iOS and Android mobile applications"},
  {"date": "2024 Q4", "title": "Enterprise", "description": "Enterprise features and integrations"}
]
```
:::''',
                        props={}
                    )
                ],
                use_cases=[
                    'Product roadmaps',
                    'Project timelines',
                    'Company milestones',
                    'Process workflows',
                    'Historical events'
                ],
                related_components=['card', 'callout']
            ),
            
            'grid': ComponentDoc(
                name='grid',
                display_name='Grid',
                description='Responsive grid layout for organizing multiple content blocks with customizable columns and spacing',
                category='layout',
                tags=['layout', 'responsive', 'organization', 'structure'],
                props={
                    'cols': {'type': 'number', 'required': False, 'description': 'Number of columns (2-4)', 'default': 2},
                    'gap': {'type': 'number', 'required': False, 'description': 'Gap between items in rem units', 'default': 6},
                    'sections': {'type': 'array', 'required': True, 'description': 'Array of grid sections with content'}
                },
                examples=[
                    ComponentExample(
                        title='Feature Grid',
                        description='3-column grid showcasing product features',
                        markdown=''':::grid cols=3 gap=6

### Speed
Lightning-fast performance with optimized rendering.

### Security
Enterprise-grade security with end-to-end encryption.

### Scalability
Built to scale from startup to enterprise.

:::''',
                        props={'cols': 3, 'gap': 6}
                    )
                ],
                use_cases=[
                    'Feature comparisons',
                    'Service offerings',
                    'Team member profiles',
                    'Product catalogs',
                    'Benefit highlights'
                ],
                related_components=['columns', 'card']
            ),
            
            'columns': ComponentDoc(
                name='columns',
                display_name='Columns',
                description='Two-column layout with customizable width ratios for side-by-side content presentation',
                category='layout',
                tags=['layout', 'split', 'comparison', 'sidebar'],
                props={
                    'ratio': {'type': 'string', 'required': False, 'description': 'Column width ratio (e.g., "1:1", "2:1", "7:5")', 'default': '1:1'}
                },
                examples=[
                    ComponentExample(
                        title='Content and Image Layout',
                        description='Asymmetric two-column layout with text and visual content',
                        markdown=''':::columns ratio=7:5

### The Future of Work
Remote collaboration tools have transformed how teams operate. Modern solutions enable seamless communication across time zones and create virtual workspaces that rival traditional offices.

![Team collaboration](https://via.placeholder.com/400x300)

:::''',
                        props={'ratio': '7:5'}
                    )
                ],
                use_cases=[
                    'Text and image layouts',
                    'Before/after comparisons',
                    'Feature explanations with visuals',
                    'Content and sidebar layouts',
                    'Split testimonials'
                ],
                related_components=['grid', 'card']
            ),
            
            'speaker-notes': ComponentDoc(
                name='speaker-notes',
                display_name='Speaker Notes',
                description='Private presenter notes visible only in presentation mode for speaker reference',
                category='content',
                tags=['presentation', 'notes', 'speaker', 'private'],
                props={
                    'content': {'type': 'markdown', 'required': True, 'description': 'Speaker note content (supports markdown)'}
                },
                examples=[
                    ComponentExample(
                        title='Slide with Speaker Notes',
                        description='Adding private notes for the presenter that are hidden from audience',
                        markdown='''# Revenue Growth Strategy

We've seen tremendous growth this quarter with revenue up 45%.

:::speaker-notes
Remember to mention:
- Q3 numbers were affected by seasonal trends
- New product launch contributed 20% of growth
- Emphasize the competitive advantage
- Ask for questions about the forecast
:::''',
                        props={}
                    ),
                    ComponentExample(
                        title='Detailed Presenter Notes',
                        description='Comprehensive speaker notes with formatting and bullet points',
                        markdown='''# Product Demo

Let me show you our latest features.

:::speaker-notes
**Demo Script:**
1. Start with the dashboard overview
2. Show the new analytics panel
3. Demonstrate real-time collaboration
4. **Important**: Mention the 30-day free trial

*Timing: Keep this section under 5 minutes*

Backup slides: 15-18 if they ask about technical details
:::''',
                        props={}
                    )
                ],
                use_cases=[
                    'Presentation talking points',
                    'Demo scripts and instructions',
                    'Timing reminders for speakers',
                    'Statistics and facts to mention',
                    'Backup information and Q&A prep',
                    'Transition cues between slides'
                ],
                related_components=['callout', 'card']
            )
        }
    
    def get_component_doc(self, component_name: str) -> Optional[ComponentDoc]:
        """Get documentation for a specific component."""
        return self.docs.get(component_name)
    
    def list_components(self) -> List[ComponentDoc]:
        """Get all component documentation."""
        return list(self.docs.values())
    
    def search_components(self, query: str) -> List[ComponentDoc]:
        """Search components by name, description, tags, or use cases."""
        query = query.lower()
        results = []
        
        for doc in self.docs.values():
            # Search in name, description, tags, and use cases
            searchable_text = ' '.join([
                doc.name,
                doc.display_name,
                doc.description,
                ' '.join(doc.tags),
                ' '.join(doc.use_cases)
            ]).lower()
            
            if query in searchable_text:
                results.append(doc)
        
        return results
    
    def get_components_by_category(self, category: str) -> List[ComponentDoc]:
        """Get components filtered by category."""
        return [doc for doc in self.docs.values() if doc.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all available component categories."""
        categories = set(doc.category for doc in self.docs.values())
        return sorted(list(categories))
    
    def get_component_examples(self, component_name: str) -> List[ComponentExample]:
        """Get examples for a specific component."""
        doc = self.get_component_doc(component_name)
        return doc.examples if doc else []
    
    def generate_component_guide(self, component_name: str) -> Optional[str]:
        """Generate a comprehensive usage guide for a component."""
        doc = self.get_component_doc(component_name)
        if not doc:
            return None
        
        guide = f"""# {doc.display_name} Component Guide

## Overview
{doc.description}

**Category:** {doc.category.title()}  
**Tags:** {', '.join(doc.tags)}

## Properties
"""
        
        for prop_name, prop_info in doc.props.items():
            required = "**Required**" if prop_info.get('required', False) else "Optional"
            prop_type = prop_info.get('type', 'string')
            description = prop_info.get('description', '')
            default = prop_info.get('default')
            options = prop_info.get('options')
            
            guide += f"\n### `{prop_name}` ({prop_type}) - {required}\n{description}\n"
            
            if default:
                guide += f"**Default:** `{default}`\n"
            
            if options:
                guide += f"**Options:** {', '.join(f'`{opt}`' for opt in options)}\n"
        
        guide += "\n## Examples\n"
        
        for i, example in enumerate(doc.examples, 1):
            guide += f"\n### Example {i}: {example.title}\n"
            guide += f"{example.description}\n\n"
            guide += f"```markdown\n{example.markdown}\n```\n"
        
        guide += "\n## Use Cases\n"
        for use_case in doc.use_cases:
            guide += f"- {use_case}\n"
        
        if doc.related_components:
            guide += "\n## Related Components\n"
            for related in doc.related_components:
                guide += f"- `{related}`\n"
        
        return guide


# Global instance
component_docs = ComponentDocumentationRegistry()


# Legacy compatibility functions for existing code
def get_component_documentation(component_name: str) -> dict:
    """Legacy function for backward compatibility."""
    doc = component_docs.get_component_doc(component_name)
    if not doc:
        return {
            "description": f"{component_name} component",
            "props": [],
            "example": f":::{component_name}\nContent\n:::",
            "tips": []
        }
    
    # Convert to legacy format
    props = []
    for prop_name, prop_info in doc.props.items():
        props.append({
            "name": prop_name,
            "type": prop_info.get('type', 'string'),
            "required": prop_info.get('required', False),
            "description": prop_info.get('description', '')
        })
    
    example = doc.examples[0].markdown if doc.examples else f":::{component_name}\nContent\n:::"
    
    return {
        "description": doc.description,
        "props": props,
        "example": example,
        "tips": doc.use_cases
    }


def get_all_components() -> list:
    """Legacy function for backward compatibility."""
    return list(component_docs.docs.keys())