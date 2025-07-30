"""
Build tools: html_preview using the new Python renderer.
"""

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..models import DeckRef, PathOut
from ..renderer import SlideRenderer

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
        
        # Check if deck has source files (now looking for .md files)
        src_dir = deck_root / "src"
        md_files = list(src_dir.glob("*.md"))
        mdx_files = list(src_dir.glob("*.mdx"))  # Also check for MDX for compatibility
        
        if not src_dir.exists() or not (md_files or mdx_files):
            raise ValueError(f"No markdown files found in {src_dir}")
        
        # Use the first markdown file found (preferring .md over .mdx)
        if md_files:
            source_file = md_files[0]
        else:
            source_file = mdx_files[0]
        
        print(f"Building deck {params.deck_id} from {source_file.name}...")
        
        # Start timing
        start_time = time.time()
        
        # Read the markdown content
        try:
            markdown_content = source_file.read_text(encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Error reading source file: {e}")
        
        # Get theme from tokens.json if available
        theme = "markov-pro"  # default
        tokens_path = deck_root / "tokens.json"
        if tokens_path.exists():
            try:
                tokens = json.loads(tokens_path.read_text())
                theme = tokens.get("theme", theme)
            except:
                pass
        
        # Create renderer and render
        renderer = SlideRenderer(theme=theme)
        html, errors = renderer.render_markdown(markdown_content)
        
        if errors:
            raise RuntimeError(f"Render errors: {'; '.join(errors)}")
        
        # Create build directory
        build_dir = deck_root / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Write HTML file
        html_path = build_dir / "deck.html"
        try:
            html_path.write_text(html, encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Error writing HTML file: {e}")
        
        # Calculate build time
        build_time_ms = int((time.time() - start_time) * 1000)
        
        # Get file size
        size_bytes = html_path.stat().st_size
        
        # Update metadata with build info
        metadata_path = deck_root / ".metadata.json"
        metadata = {}
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text())
            except:
                pass
        
        # Update build info
        metadata["last_build"] = {
            "timestamp": time.time(),
            "duration_ms": build_time_ms,
            "source_file": source_file.name,
            "renderer": "python",
            "size_bytes": size_bytes
        }
        
        # Write updated metadata
        try:
            metadata_path.write_text(json.dumps(metadata, indent=2))
        except:
            pass  # Non-critical if metadata update fails
        
        print(f"Build completed in {build_time_ms}ms")
        
        return PathOut(
            path=str(html_path),
            size_bytes=size_bytes,
        )