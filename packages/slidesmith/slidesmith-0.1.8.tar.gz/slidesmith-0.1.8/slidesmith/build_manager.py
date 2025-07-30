"""
Build manager for handling Node.js dependencies in pipx environments.
"""
import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

class BuildManager:
    """Manages Node.js build environment for slidesmith."""
    
    def __init__(self):
        self.slidesmith_dir = Path(__file__).parent
        self.scripts_dir = self.slidesmith_dir / "scripts"
        self.node_modules_cache = Path.home() / ".slidesmith" / "node_modules_cache"
        
    def ensure_node_modules(self, workspace_dir: Path) -> None:
        """Ensure node_modules exist in workspace, using cache if available."""
        workspace_node_modules = workspace_dir / "node_modules"
        
        # If node_modules already exist in workspace, we're good
        if workspace_node_modules.exists() and (workspace_node_modules / "esbuild").exists():
            return
            
        # Check if we have a cached version
        if self.node_modules_cache.exists() and (self.node_modules_cache / "esbuild").exists():
            print("Using cached node_modules...")
            shutil.copytree(self.node_modules_cache, workspace_node_modules, dirs_exist_ok=True)
            return
            
        # Otherwise, install fresh
        print("Installing Node dependencies...")
        package_json = workspace_dir / "package.json"
        
        # Ensure package.json exists
        if not package_json.exists():
            self._create_package_json(workspace_dir)
            
        # Run npm install
        result = subprocess.run(
            ["npm", "install"],
            cwd=workspace_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"npm install failed: {result.stderr}")
            
        # Cache the node_modules for future use
        if workspace_node_modules.exists():
            print("Caching node_modules for future use...")
            self.node_modules_cache.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(workspace_node_modules, self.node_modules_cache, dirs_exist_ok=True)
    
    def _create_package_json(self, workspace_dir: Path) -> None:
        """Create a minimal package.json for the workspace."""
        package_data = {
            "name": f"slidesmith-deck-{workspace_dir.name}",
            "private": True,
            "type": "module",
            "dependencies": {
                "@mdx-js/esbuild": "^3.0.1",
                "esbuild": "^0.21.5",
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "tailwindcss": "^3.4.4",
                "chart.js": "^4.4.3"
            }
        }
        
        package_json = workspace_dir / "package.json"
        package_json.write_text(json.dumps(package_data, indent=2))
    
    def run_build(self, deck_id: str, workspace_dir: Path) -> subprocess.CompletedProcess:
        """Run the build script with proper environment setup."""
        # Ensure node_modules exist
        self.ensure_node_modules(workspace_dir)
        
        # Set up environment variables
        env = os.environ.copy()
        env["NODE_PATH"] = str(workspace_dir / "node_modules")
        
        # Run build script
        build_script = self.scripts_dir / "build.js"
        
        # Change to workspace directory for relative path resolution
        return subprocess.run(
            ["node", str(build_script), deck_id, str(workspace_dir)],
            cwd=workspace_dir,
            env=env,
            capture_output=True,
            text=True
        )