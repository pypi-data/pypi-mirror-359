#!/usr/bin/env node

/**
 * Wrapper script to handle module resolution in different environments
 */

import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Dynamic import with fallback paths
async function loadModule(moduleName, workspaceRoot) {
  const possiblePaths = [
    // Try workspace node_modules first
    join(workspaceRoot, 'node_modules', moduleName),
    // Try relative to this script
    join(__dirname, '..', '..', 'node_modules', moduleName),
    // Try global import as last resort
    moduleName
  ];
  
  for (const path of possiblePaths) {
    try {
      return await import(path);
    } catch (e) {
      // Continue to next path
    }
  }
  
  throw new Error(`Could not load module ${moduleName} from any location`);
}

// Main wrapper
async function main() {
  const args = process.argv.slice(2);
  const deckId = args[0];
  const workspaceRoot = args[1];
  
  if (!deckId || !workspaceRoot) {
    console.error('Usage: node build-wrapper.js <deck-id> <workspace-root>');
    process.exit(1);
  }
  
  // Set NODE_PATH for child processes
  process.env.NODE_PATH = join(workspaceRoot, 'node_modules');
  
  // Load the actual build script
  try {
    const buildScript = await import('./build.js');
    // The build script should export a default function or handle execution directly
  } catch (error) {
    console.error('Failed to load build script:', error);
    process.exit(1);
  }
}

main().catch(error => {
  console.error('Build wrapper error:', error);
  process.exit(1);
});