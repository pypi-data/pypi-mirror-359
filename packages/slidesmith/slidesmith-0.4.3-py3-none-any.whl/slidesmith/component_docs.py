"""
Comprehensive component documentation for SlideSmith.
"""

COMPONENT_DOCS = {
    "BulletList": {
        "description": "Creates a styled bullet list with icons",
        "props": [
            {"name": "items", "type": "array", "required": True, "description": "Array of items with icon and text"},
        ],
        "example": """:::BulletList items='[
  { "icon": "rocket", "text": "Fast development cycles" },
  { "icon": "shield", "text": "Secure by default" },
  { "icon": "users", "text": "Team collaboration" }
]':::""",
        "tips": [
            "Icons come from Font Awesome library",
            "Each item needs both 'icon' and 'text' properties",
            "Use single quotes around the JSON array"
        ]
    },
    
    "MetricSection": {
        "description": "Displays key metrics with values, trends, and colors",
        "props": [
            {"name": "metrics", "type": "array", "required": True, "description": "Array of metric objects"},
        ],
        "example": """:::MetricSection metrics='[
  { "label": "Revenue", "value": "$1.2M", "trend": "up", "color": "green" },
  { "label": "Users", "value": "5,234", "trend": "up", "color": "blue" },
  { "label": "Churn", "value": "2.3%", "trend": "down", "color": "red" }
]':::""",
        "tips": [
            "Trend can be 'up', 'down', or 'neutral'",
            "Colors: green, blue, red, purple, orange, yellow",
            "Value can be any string (numbers, percentages, currency)"
        ]
    },
    
    "CardGrid": {
        "description": "Grid layout for cards with icons and descriptions",
        "props": [
            {"name": "cards", "type": "array", "required": True, "description": "Array of card objects"},
            {"name": "columns", "type": "number", "default": 2, "description": "Number of columns (1-4)"},
        ],
        "example": """:::CardGrid cards='[
  {
    "title": "Feature One",
    "description": "Description of the first feature",
    "icon": "star",
    "color": "blue"
  },
  {
    "title": "Feature Two",
    "description": "Description of the second feature",
    "icon": "heart",
    "color": "red"
  }
]' columns="2":::""",
        "tips": [
            "Columns can be 1, 2, 3, or 4",
            "Each card needs title, description, icon, and color",
            "Cards automatically wrap to new rows"
        ]
    },
    
    "Timeline": {
        "description": "Visual timeline with events and descriptions",
        "props": [
            {"name": "items", "type": "array", "required": True, "description": "Array of timeline events"},
            {"name": "orientation", "type": "string", "default": "vertical", "description": "vertical or horizontal"},
            {"name": "style", "type": "string", "default": "default", "description": "default, minimal, or detailed"},
        ],
        "example": """:::Timeline items='[
  { "date": "2020", "title": "Company Founded", "description": "Started in a garage", "icon": "rocket", "color": "blue" },
  { "date": "2022", "title": "Series A", "description": "$10M funding round", "icon": "dollar-sign", "color": "green" },
  { "date": "2024", "title": "IPO", "description": "Public offering", "icon": "chart-line", "color": "purple" }
]' orientation="horizontal" style="detailed":::""",
        "tips": [
            "Dates can be any format (years, months, specific dates)",
            "Style options change the visual appearance",
            "Horizontal works best with 3-6 items"
        ]
    },
    
    "ImpactBox": {
        "description": "Highlighted box for key information or statistics",
        "props": [
            {"name": "title", "type": "string", "required": True, "description": "Box title"},
            {"name": "icon", "type": "string", "description": "Optional icon"},
            {"name": "color", "type": "string", "default": "indigo", "description": "Theme color"},
            {"name": "children", "type": "string", "description": "Box content (markdown supported)"},
        ],
        "example": """:::ImpactBox title="70% Productivity Gain" icon="rocket" color="green"
Our AI tools help developers write code 70% faster while maintaining quality.
- Automated code generation
- Intelligent suggestions
- Real-time error detection
:::""",
        "tips": [
            "Content supports full markdown including lists",
            "Color affects the border and icon",
            "Great for highlighting key statistics or outcomes"
        ]
    },
    
    "CTABox": {
        "description": "Call-to-action box with button",
        "props": [
            {"name": "title", "type": "string", "required": True, "description": "CTA title"},
            {"name": "buttonText", "type": "string", "required": True, "description": "Button label"},
            {"name": "buttonUrl", "type": "string", "required": True, "description": "Button link"},
            {"name": "color", "type": "string", "default": "indigo", "description": "Theme color"},
            {"name": "children", "type": "string", "description": "Additional content"},
        ],
        "example": """:::CTABox title="Ready to Get Started?" buttonText="Schedule Demo" buttonUrl="#demo" color="green"
Join thousands of developers already using our AI tools to build better software faster.
:::""",
        "tips": [
            "ButtonUrl can be external link or anchor (#section)",
            "Color affects button and border styling",
            "Keep title and button text concise"
        ]
    },
    
    "CheckList": {
        "description": "Checklist with checkboxes",
        "props": [
            {"name": "items", "type": "array", "required": True, "description": "Array of checklist items"},
        ],
        "example": """:::CheckList items='[
  { "text": "Complete project setup", "checked": true },
  { "text": "Write documentation", "checked": true },
  { "text": "Deploy to production", "checked": false },
  { "text": "Monitor performance", "checked": false }
]':::""",
        "tips": [
            "Use 'checked': true/false to control checkbox state",
            "Great for showing progress or task lists",
            "Items appear in the order defined"
        ]
    },
    
    "BarChart": {
        "description": "Bar chart visualization",
        "props": [
            {"name": "data", "type": "object", "required": True, "description": "Chart.js data format"},
            {"name": "options", "type": "object", "description": "Chart.js options"},
        ],
        "example": """:::BarChart data='{
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [{
    "label": "Revenue ($M)",
    "data": [1.2, 1.8, 2.1, 2.9],
    "backgroundColor": "rgba(79, 70, 229, 0.8)"
  }]
}' options='{
  "responsive": true,
  "plugins": {
    "title": { "display": true, "text": "Quarterly Revenue" }
  }
}':::""",
        "tips": [
            "Use Chart.js data format",
            "backgroundColor accepts rgba() for transparency",
            "Can have multiple datasets for grouped bars"
        ]
    },
    
    "PieChart": {
        "description": "Pie or doughnut chart",
        "props": [
            {"name": "data", "type": "object", "required": True, "description": "Chart.js data format"},
            {"name": "options", "type": "object", "description": "Chart.js options"},
        ],
        "example": """:::PieChart data='{
  "labels": ["Desktop", "Mobile", "Tablet"],
  "datasets": [{
    "data": [65, 25, 10],
    "backgroundColor": [
      "rgba(79, 70, 229, 0.8)",
      "rgba(16, 185, 129, 0.8)",
      "rgba(251, 146, 60, 0.8)"
    ]
  }]
}':::""",
        "tips": [
            "Each data point needs a corresponding color",
            "Use rgba() colors for better appearance",
            "Legend position can be customized in options"
        ]
    },
    
    "columns": {
        "description": "Multi-column layout",
        "props": [
            {"name": "ratio", "type": "string", "default": "6:6", "description": "Column width ratio"},
        ],
        "syntax": """:::columns ratio="7:5"
## Left Column
Content for the left column

---

## Right Column  
Content for the right column
:::""",
        "tips": [
            "Use --- to separate columns",
            "Ratios should add up to 12 (e.g., 7:5, 8:4, 4:4:4)",
            "Supports 2-3 columns"
        ]
    },
    
    "Calculation": {
        "description": "Animated calculation or metric display",
        "props": [
            {"name": "values", "type": "array", "required": True, "description": "Array of values"},
            {"name": "labels", "type": "array", "description": "Labels for each value"},
            {"name": "calculation_type", "type": "string", "description": "sum, average, growth, etc."},
            {"name": "format", "type": "string", "default": "number", "description": "number, percentage, currency"},
            {"name": "title", "type": "string", "description": "Calculation title"},
        ],
        "example": """:::Calculation values="[100, 150, 225, 340]" labels='["Q1", "Q2", "Q3", "Q4"]' calculation_type="growth" format="percentage" title="Quarterly Growth":::""",
        "tips": [
            "Growth shows percentage increase between first and last",
            "Format options: number, percentage, currency",
            "Values can be numbers or arrays of numbers"
        ]
    }
}


def get_component_documentation(component_name: str) -> dict:
    """Get documentation for a specific component."""
    # Check if it's a documented component
    if component_name in COMPONENT_DOCS:
        return COMPONENT_DOCS[component_name]
    
    # Provide basic documentation for undocumented components
    # Try to generate meaningful defaults based on component name
    basic_components = {
        "slide-base": {
            "description": "Base container for all slides with consistent padding and styling",
            "props": [],
            "example": "Automatically applied to all slides",
            "tips": []
        },
        "header": {
            "description": "Consistent header with title, subtitle, and optional logo",
            "props": [],
            "example": "# Title\n## Subtitle",
            "tips": []
        },
        "footer": {
            "description": "Footer with slide number and optional text",
            "props": [],
            "example": "Automatically added based on template settings",
            "tips": []
        },
        "grid": {
            "description": "Grid layout for organizing multiple items",
            "props": [
                {"name": "cols", "type": "number", "default": 3, "description": "Number of columns"},
                {"name": "gap", "type": "number", "default": 6, "description": "Gap between items"}
            ],
            "example": ":::grid cols=3 gap=6\n### Item 1\nContent\n\n### Item 2\nContent\n:::",
            "tips": ["Grid automatically wraps items to new rows"]
        },
        "card": {
            "description": "Highlighted content box with optional title, icon, and color",
            "props": [
                {"name": "title", "type": "string", "description": "Card title"},
                {"name": "icon", "type": "string", "description": "Font Awesome icon name"},
                {"name": "color", "type": "string", "default": "blue", "description": "Theme color"},
                {"name": "content", "type": "string", "description": "Card content"}
            ],
            "example": ':::card title="Key Point" icon="lightbulb" color="blue"\nImportant information here\n:::',
            "tips": ["Colors: blue, green, red, yellow, purple"]
        },
        "callout": {
            "description": "Attention-grabbing box for warnings, tips, or highlights",
            "props": [
                {"name": "type", "type": "string", "default": "info", "description": "Callout type"},
                {"name": "icon", "type": "string", "description": "Font Awesome icon name"}
            ],
            "example": ':::callout type="warning" icon="exclamation-triangle"\nWarning message here\n:::',
            "tips": ["Types: info, warning, success, error"]
        },
        "table": {
            "description": "Styled table from markdown",
            "props": [],
            "example": "| Column 1 | Column 2 |\n|----------|----------|\n| Data 1   | Data 2   |",
            "tips": ["Use standard markdown table syntax"]
        },
        "code": {
            "description": "Syntax-highlighted code block",
            "props": [],
            "example": '```python\ndef hello():\n    print("Hello!")\n```',
            "tips": ["Specify language after ``` for syntax highlighting"]
        },
        "image": {
            "description": "Responsive image with optional caption",
            "props": [
                {"name": "src", "type": "string", "required": True, "description": "Image source URL or path"},
                {"name": "alt", "type": "string", "required": True, "description": "Alt text for accessibility"}
            ],
            "example": ':::image src="path/to/image.png" alt="Description"\nOptional caption\n:::',
            "tips": ["Always provide alt text for accessibility"]
        },
        "speaker-notes": {
            "description": "Hidden notes for presenter view",
            "props": [],
            "example": ":::speaker-notes\nNotes that only the presenter sees\n:::",
            "tips": ["Notes are hidden in normal view but visible in presenter mode"]
        },
        "chart": {
            "description": "Charts and graphs using Chart.js",
            "props": [
                {"name": "type", "type": "string", "required": True, "description": "Chart type: bar, line, pie, doughnut"},
                {"name": "data", "type": "object", "required": True, "description": "Chart.js data object"}
            ],
            "example": ':::chart type="bar"\n```json\n{\n  "labels": ["Q1", "Q2"],\n  "datasets": [{\n    "label": "Revenue",\n    "data": [100, 150]\n  }]\n}\n```\n:::',
            "tips": ["Use Chart.js data format"]
        },
        "metrics": {
            "description": "Key metrics display with values and changes",
            "props": [],
            "example": ":::metrics\n- label: Revenue\n  value: $10M\n  change: +15%\n  trend: up\n:::",
            "tips": ["Trend can be up, down, or neutral"]
        }
    }
    
    # Return basic documentation for known components
    if component_name in basic_components:
        return basic_components[component_name]
    
    # Default for unknown components
    return {
        "description": f"{component_name} component",
        "props": [],
        "example": f":::{component_name}\nContent\n:::",
        "tips": []
    }


def get_all_components() -> list:
    """Get list of all documented components."""
    return list(COMPONENT_DOCS.keys())