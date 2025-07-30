"""
Build tools: html_preview.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..models import DeckRef, PathOut
from ..build_manager import BuildManager

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_build_tools(mcp: "FastMCP") -> None:
    """Register build tools with the MCP server."""
    
    @mcp.tool()
    def html_preview(params: Union[DeckRef, str, dict]) -> PathOut:
        """Generate HTML preview of the deck."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = DeckRef(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = DeckRef(**params)
        elif not isinstance(params, DeckRef):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Check if deck has source files
        src_dir = deck_root / "src"
        if not src_dir.exists() or not list(src_dir.glob("*.mdx")):
            raise ValueError(f"No MDX files found in {src_dir}")
        
        # Use BuildManager to handle Node.js environment
        build_manager = BuildManager()
        
        print(f"Building deck {params.deck_id}...")
        result = build_manager.run_build(params.deck_id, deck_root)
        
        if result.returncode != 0:
            raise RuntimeError(f"Build failed: {result.stderr}")
        
        # Parse the build output to get the HTML path
        build_dir = deck_root / "build"
        html_path = build_dir / "deck.html"
        
        if not html_path.exists():
            raise RuntimeError("Build completed but HTML file not found")
        
        # Get file size
        size_bytes = html_path.stat().st_size
        
        # Update metadata with build info
        metadata_path = deck_root / ".metadata.json"
        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            if "last_build" in metadata:
                print(f"Build completed in {metadata['last_build']['duration_ms']}ms")
        
        return PathOut(
            path=str(html_path),
            size_bytes=size_bytes,
        )