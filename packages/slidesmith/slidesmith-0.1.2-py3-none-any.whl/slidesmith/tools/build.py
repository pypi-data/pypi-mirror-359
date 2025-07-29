"""
Build tools: html_preview.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ..models import DeckRef, PathOut

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_build_tools(mcp: "FastMCP") -> None:
    """Register build tools with the MCP server."""
    
    @mcp.tool()
    def html_preview(params: DeckRef) -> PathOut:
        """Generate HTML preview of the deck."""
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Check if deck has source files
        src_dir = deck_root / "src"
        if not src_dir.exists() or not list(src_dir.glob("*.mdx")):
            raise ValueError(f"No MDX files found in {src_dir}")
        
        # Install Node dependencies if needed
        package_json = Path(__file__).parent.parent.parent / "package.json"
        node_modules = Path(__file__).parent.parent.parent / "node_modules"
        
        if not node_modules.exists():
            print("Installing Node dependencies...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=package_json.parent,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"npm install failed: {result.stderr}")
        
        # Run the build script
        build_script = Path(__file__).parent.parent.parent / "scripts" / "build.js"
        
        print(f"Building deck {params.deck_id}...")
        result = subprocess.run(
            ["node", str(build_script), params.deck_id, str(deck_root)],
            capture_output=True,
            text=True
        )
        
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