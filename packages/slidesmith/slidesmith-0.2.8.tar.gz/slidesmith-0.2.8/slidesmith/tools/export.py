"""
Export tools: pdf_export.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Union

from ..models import DeckRef, PathOut, PdfExportIn

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_export_tools(mcp: "FastMCP") -> None:
    """Register export tools with the MCP server."""
    
    @mcp.tool()
    def pdf_export(params: Union[PdfExportIn, str, dict]) -> PathOut:
        """Export deck to PDF."""
        # Handle Claude Code sending params as string
        if isinstance(params, str):
            try:
                params_data = json.loads(params)
                params = PdfExportIn(**params_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Invalid parameters: {e}")
        elif isinstance(params, dict):
            params = PdfExportIn(**params)
        elif not isinstance(params, PdfExportIn):
            raise ValueError(f"Invalid parameter type: {type(params)}")
        
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Check if build exists
        build_dir = deck_root / "build"
        if not build_dir.exists() or not (build_dir / "deck.html").exists():
            raise ValueError(f"Deck not built - run html_preview first")
        
        # Check quality score if we need to enforce it
        if params.quality_check:
            metadata_path = deck_root / ".metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                if "last_lint" in metadata:
                    score = metadata["last_lint"].get("score", 0)
                    if score < 80:
                        raise ValueError(
                            f"Quality score too low: {score}/100. "
                            "Run slide_lint and fix issues before exporting."
                        )
            else:
                # No lint data, run lint first
                from .quality import register_quality_tools
                
                # Create a mini MCP to get slide_lint
                class MiniMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self, name=None):
                        def decorator(func):
                            self.tools[name or func.__name__] = func
                            return func
                        return decorator
                
                mini_mcp = MiniMCP()
                register_quality_tools(mini_mcp)
                
                # Run lint
                slide_lint = mini_mcp.tools.get("slide_lint")
                if not slide_lint:
                    raise RuntimeError("Could not load slide_lint tool")
                    
                lint_result = slide_lint(DeckRef(deck_id=params.deck_id))
                if lint_result.score < 80:
                    raise ValueError(
                        f"Quality score too low: {lint_result.score}/100. "
                        f"Found {len(lint_result.issues)} issues. "
                        "Fix issues before exporting."
                    )
        
        # Run the PDF export script
        pdf_script = Path(__file__).parent.parent / "scripts" / "pdf_export.py"
        
        # Prepare arguments
        cmd_args = [
            sys.executable,
            str(pdf_script),
            params.deck_id,
            str(workspaces_dir),
            params.filename,
            params.format.value,
            params.orientation.value
        ]
        
        print(f"Exporting deck {params.deck_id} to PDF...")
        result = subprocess.run(cmd_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"PDF export failed: {result.stderr}")
        
        # Parse the JSON output
        try:
            # Find the JSON in the output
            lines = result.stdout.strip().split('\n')
            json_output = None
            for line in reversed(lines):
                if line.strip().startswith('{'):
                    json_output = '\n'.join(lines[lines.index(line):])
                    break
            
            if not json_output:
                raise ValueError("No JSON output from PDF export script")
            
            pdf_data = json.loads(json_output)
            
            return PathOut(
                path=pdf_data['path'],
                size_bytes=pdf_data['size_bytes']
            )
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse PDF export output: {e}\nOutput: {result.stdout}")