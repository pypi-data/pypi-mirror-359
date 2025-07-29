"""
Quality tools: slide_lint, snapshot.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from ..models import DeckRef, LintIssue, LintLevel, LintReport, PathOut, SnapshotIn

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_quality_tools(mcp: "FastMCP") -> None:
    """Register quality assurance tools with the MCP server."""
    
    @mcp.tool()
    def slide_lint(params: DeckRef) -> LintReport:
        """Check slide quality and compliance."""
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Check if build exists
        build_dir = deck_root / "build"
        if not build_dir.exists() or not (build_dir / "deck.html").exists():
            raise ValueError(f"Deck not built - run html_preview first")
        
        # Run the lint script
        lint_script = Path(__file__).parent.parent.parent / "scripts" / "lint.js"
        
        print(f"Linting deck {params.deck_id}...")
        result = subprocess.run(
            ["node", str(lint_script), params.deck_id, str(deck_root)],
            capture_output=True,
            text=True
        )
        
        if result.returncode not in [0, 1]:  # 0 = passed, 1 = failed with issues
            raise RuntimeError(f"Lint failed: {result.stderr}")
        
        # Parse the JSON output
        try:
            # Find the JSON in the output (last line should be JSON)
            lines = result.stdout.strip().split('\n')
            json_output = None
            for line in reversed(lines):
                if line.strip().startswith('{'):
                    json_output = '\n'.join(lines[lines.index(line):])
                    break
            
            if not json_output:
                # Debug output
                print(f"Lint stdout: {result.stdout}")
                print(f"Lint stderr: {result.stderr}")
                raise ValueError("No JSON output from lint script")
            
            lint_data = json.loads(json_output)
            
            # Convert issues to LintIssue objects
            issues = []
            for issue in lint_data['issues']:
                lint_issue = LintIssue(
                    rule=issue['rule'],
                    level=LintLevel(issue['level']),
                    message=issue['message'],
                    element=issue.get('element', ''),
                    location=issue.get('location')
                )
                issues.append(lint_issue)
            
            # Create summary
            summary = {
                LintLevel.ERROR: lint_data['summary']['error'],
                LintLevel.WARNING: lint_data['summary']['warning'],
                LintLevel.INFO: lint_data['summary']['info'],
            }
            
            # Update metadata with lint results
            metadata_path = deck_root / ".metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                metadata["last_lint"] = {
                    "score": lint_data['score'],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "issue_count": len(issues),
                    "summary": summary
                }
                metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
                metadata_path.write_text(json.dumps(metadata, indent=2))
            
            return LintReport(
                issues=issues,
                score=lint_data['score'],
                passed=lint_data['passed'],
                summary=summary
            )
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse lint output: {e}\nOutput: {result.stdout}")
    
    @mcp.tool()
    def snapshot(params: SnapshotIn) -> PathOut:
        """Generate PNG snapshot of slides."""
        # Get deck workspace
        workspaces_dir = Path.home() / "slidesmith_workspaces"
        deck_root = workspaces_dir / params.deck_id
        
        if not deck_root.exists():
            raise ValueError(f"Deck {params.deck_id} not found")
        
        # Check if build exists
        build_dir = deck_root / "build"
        if not build_dir.exists() or not (build_dir / "deck.html").exists():
            raise ValueError(f"Deck not built - run html_preview first")
        
        # Run the snapshot script
        snapshot_script = Path(__file__).parent.parent.parent / "scripts" / "snapshot.js"
        
        # Prepare arguments
        cmd_args = [
            "node",
            str(snapshot_script),
            params.deck_id,
            str(deck_root),
            str(params.slide_number)
        ]
        
        # Add clip region if provided
        if params.clip:
            clip_json = json.dumps({
                "x": params.clip.get("x", 0),
                "y": params.clip.get("y", 0),
                "width": params.clip.get("width", 1920),
                "height": params.clip.get("height", 1080)
            })
            cmd_args.append(clip_json)
        
        print(f"Taking snapshot of deck {params.deck_id}, slide {params.slide_number}...")
        result = subprocess.run(cmd_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Snapshot failed: {result.stderr}")
        
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
                raise ValueError("No JSON output from snapshot script")
            
            snapshot_data = json.loads(json_output)
            
            return PathOut(
                path=snapshot_data['path'],
                size_bytes=snapshot_data['size_bytes']
            )
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse snapshot output: {e}\nOutput: {result.stdout}")