# Slidesmith MCP Server

[![MCP-COMPAT](https://img.shields.io/badge/MCP-Compatible-green)](https://github.com/anthropics/mcp)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/slidesmith)](https://pypi.org/project/slidesmith/)

An on-device Model Context Protocol (MCP) server that converts Markdown content into pixel-perfect slide decks with Tailwind/React components and print-ready PDFs. Built for AI-powered presentation creation with zero network dependencies.

## 🚀 Quick Start

### Installation

```bash
# Install via pipx (recommended)
pipx install slidesmith

# Or via pip
pip install slidesmith
```

### First-time Setup

```bash
# Install required browsers and templates
slidesmith setup

# Start the MCP server
slidesmith serve
```

### Using with Claude Code

```bash
# Add to Claude Code
claude mcp add slidesmith -s local -- slidesmith serve

# Verify connection
claude --debug
```

## ✨ Features

- 🏠 **Local-first**: No Docker, no network I/O, no telemetry
- 🤖 **AI-optimized**: Designed for Claude Code to create professional presentations
- ⚡ **Fast builds**: Sub-second deck generation with Python renderer
- 🎨 **Token-based theming**: Easy brand customization via JSON
- ✅ **Quality gates**: Automated linting ensures pixel-perfect output
- 📄 **Export ready**: Generate print-quality PDFs with embedded fonts
- 🖼️ **Rich components**: Charts, timelines, metrics, and more
- 🔒 **Fully offline**: All assets bundled, no CDN dependencies

## 📚 MCP Tools

### Deck Management
- `list_templates` - List available slide templates
- `init_deck` - Initialize a new slide deck
- `cleanup` - Clean up deck workspace

### Theming
- `theme_base` - Get base theme tokens for a template
- `apply_tokens` - Apply custom theme tokens to a deck

### Building & Export
- `html_preview` - Generate HTML preview of deck
- `pdf_export` - Export deck to print-ready PDF
- `snapshot` - Generate PNG screenshots of slides

### Quality & Utilities
- `slide_lint` - Check slides for quality issues
- `get_component_doc` - Get component documentation
- `svg_icon` - Get SVG icons from offline library

## 🎯 Example Usage

```python
# In Claude Code, you can use natural language:
"Create a startup pitch deck for TechVision AI"
"Apply a blue color scheme with Montserrat font"
"Add a chart showing 200% YoY growth"
"Export to PDF for investors"
```

## 📦 What's Included

### Templates
- **markov-pro**: Professional business template
- **minimal**: Clean, minimalist design
- **tech**: Modern tech presentation style

### Components
- `SlideBase` - Standard slide container (1920x1080)
- `Header/Footer` - Consistent branding elements
- `BarChart/PieChart` - Data visualization
- `Timeline` - Event sequences
- `MetricSection` - KPI displays
- `CardGrid` - Feature showcases
- `ImpactBox` - Highlighted metrics
- And many more...

### Example Decks
- **Startup Pitch** (10 slides) - Series B investor deck
- **Product Demo** (15 slides) - Feature showcase
- **Company Overview** (20 slides) - Corporate presentation

## 📝 Slide Format (v0.2.0+)

Slidesmith uses Markdown with a custom component syntax:

```markdown
---
slide: 1
template: title
---

# My Presentation

## Subtitle Here

:::speaker-notes
These are my speaker notes
:::
```

### Components

```markdown
:::card title="Feature Card" icon=rocket color=blue
This is the card content
:::

:::columns ratio=2:1
Left column content

Right column content
:::

:::chart type=bar
labels: ['Q1', 'Q2', 'Q3', 'Q4']
data: [100, 200, 150, 300]
:::
```

See [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) for converting from MDX format.

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/markov/slidesmith.git
cd slidesmith

# Create virtual environment
python -m venv slidesmith-env
source slidesmith-env/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install Node dependencies
npm install

# Run tests
pytest
```

### Project Structure

```
slidesmith/
├── slidesmith/          # Python MCP server
│   ├── tools/          # MCP tool implementations
│   ├── models.py       # Pydantic models
│   └── server.py       # FastMCP server
├── scripts/            # Node.js build scripts
├── templates/          # Slide templates
├── examples/           # Example presentations
└── tests/             # Test suite
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=slidesmith --cov-report=html

# Run specific test category
pytest tests/test_tools_unit.py -v
```

## 📋 Requirements

- Python 3.11+
- Node.js 18+
- macOS, Linux, or Windows
- 500MB free disk space

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Documentation](https://slidesmith.readthedocs.io)
- [PyPI Package](https://pypi.org/project/slidesmith/)
- [GitHub Repository](https://github.com/markov/slidesmith)
- [Issue Tracker](https://github.com/markov/slidesmith/issues)

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/anthropics/fastmcp) - MCP framework
- [Playwright](https://playwright.dev) - Browser automation
- [MDX](https://mdxjs.com) - Markdown + JSX
- [Tailwind CSS](https://tailwindcss.com) - Styling
- [esbuild](https://esbuild.github.io) - Bundling

---

Made with ❤️ for the MCP community
