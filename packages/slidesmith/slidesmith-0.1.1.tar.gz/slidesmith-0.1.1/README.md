# Slidesmith MCP Server

An on-device Model Context Protocol (MCP) server that converts Markdown briefs into pixel-perfect Tailwind/React slide decks and print-ready PDFs.

## Quick Start

### Virtual Environment Setup

```bash
# Create and activate virtual environment
python3.12 -m venv slidesmith-env
source slidesmith-env/bin/activate  # macOS/Linux
# or
slidesmith-env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### Development

```bash
# Always activate venv first
source slidesmith-env/bin/activate

# Run MCP server
slidesmith serve

# Run tests
pytest
```

## Features

- 🏠 **Local-first**: No Docker, no network I/O, no telemetry
- 🤖 **AI-optimized**: Designed for Claude Code to create professional presentations
- ✨ **Quality gates**: Automated linting ensures pixel-perfect output
- 📄 **Export ready**: Generate print-quality PDFs with embedded fonts
- 🎨 **Token-based theming**: Easy brand customization via JSON

## MCP Tools

- `list_templates` - List available slide templates
- `init_deck` - Initialize a new slide deck
- `theme_base` - Get base theme tokens
- `apply_tokens` - Apply custom theme tokens
- `html_preview` - Generate HTML preview
- `slide_lint` - Check slide quality
- `snapshot` - Generate PNG screenshots
- `pdf_export` - Export to PDF
- `get_component_doc` - Get component documentation
- `svg_icon` - Get SVG icons
- `cleanup` - Clean up deck workspace

## Technology Stack

- **Framework**: FastMCP 2.9.2 (MCP 2025-06 spec)
- **Frontend**: React + Tailwind + MDX
- **Build**: esbuild + Node.js
- **Quality**: Playwright for linting & PDF generation
- **Language**: Python 3.12+
