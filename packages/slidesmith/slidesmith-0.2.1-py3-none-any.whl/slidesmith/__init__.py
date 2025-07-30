"""
Slidesmith MCP Server - Convert Markdown to pixel-perfect slide decks.

An on-device Model Context Protocol server that transforms Markdown briefs into
professional Tailwind/React slide decks and print-ready PDFs.
"""

__version__ = "0.2.1"
__author__ = "Slidesmith Team"

# Re-export commonly used items
from .server import create_server

__all__ = ["create_server", "__version__"]