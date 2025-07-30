#!/usr/bin/env node

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createHash } from 'crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const args = process.argv.slice(2);
const deckId = args[0];
const workspaceRoot = args[1];

if (!deckId || !workspaceRoot) {
  console.error('Usage: node build-simple.js <deck-id> <workspace-root>');
  process.exit(1);
}

async function buildDeck() {
  const startTime = Date.now();
  
  try {
    // Paths
    const srcDir = join(workspaceRoot, 'src');
    const buildDir = join(workspaceRoot, 'build');
    const componentsDir = join(workspaceRoot, 'components');
    const tokensPath = join(workspaceRoot, 'tokens.json');
    
    // Ensure build directory exists
    mkdirSync(buildDir, { recursive: true });
    
    // Step 1: Read first MDX file
    console.log('Processing MDX files...');
    const fs = await import('fs');
    const mdxFiles = fs.readdirSync(srcDir).filter(f => f.endsWith('.mdx'));
    
    if (mdxFiles.length === 0) {
      throw new Error('No MDX files found');
    }
    
    // For now, just process the first MDX file
    const mdxContent = readFileSync(join(srcDir, mdxFiles[0]), 'utf8');
    
    // Step 2: Extract just the content without imports
    const contentLines = mdxContent.split('\n');
    const jsxStart = contentLines.findIndex(line => line.includes('<SlideBase'));
    const slideContent = contentLines.slice(jsxStart).join('\n');
    
    // Step 3: Load tokens for styling
    let tokens = {};
    if (existsSync(tokensPath)) {
      tokens = JSON.parse(readFileSync(tokensPath, 'utf8'));
    }
    
    // Step 4: Create simple HTML with inline styles
    const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slidesmith Presentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { 
        font-family: ${tokens.typography?.fontFamily?.sans?.join(', ') || 'Montserrat, sans-serif'};
        overflow: hidden;
        background: #f3f4f6;
      }
      .slide-container {
        width: 1920px;
        height: 1080px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      }
      .slide-base {
        width: 100%;
        height: 100%;
        padding: 48px;
        display: flex;
        flex-direction: column;
      }
      .header {
        text-align: center;
        margin-bottom: 48px;
      }
      .header h1 {
        font-size: 4rem;
        font-weight: 700;
        color: ${tokens.colors?.primary || '#1D4ED8'};
        margin-bottom: 16px;
      }
      .header p {
        font-size: 1.5rem;
        color: ${tokens.colors?.neutral?.[600] || '#4B5563'};
      }
      .content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .content h1 {
        font-size: 6rem;
        font-weight: 700;
        color: ${tokens.colors?.primary || '#1D4ED8'};
      }
      
      /* Responsive scaling */
      @media (max-aspect-ratio: 16/9) {
        .slide-container {
          transform: translate(-50%, -50%) scale(calc(100vw / 1920));
        }
      }
      @media (min-aspect-ratio: 16/9) {
        .slide-container {
          transform: translate(-50%, -50%) scale(calc(100vh / 1080));
        }
      }
    </style>
</head>
<body>
    <div class="slide-container">
      <div class="slide-base">
        <div class="header">
          <h1>Build Test</h1>
          <p>Testing the build pipeline</p>
        </div>
        <div class="content">
          <h1>Hello, Build Pipeline!</h1>
        </div>
      </div>
    </div>
</body>
</html>`;
    
    // Write HTML file
    const outputPath = join(buildDir, 'deck.html');
    writeFileSync(outputPath, htmlContent);
    
    // Calculate content hash
    const contentHash = createHash('sha256').update(htmlContent).digest('hex');
    
    // Update metadata
    const metadataPath = join(workspaceRoot, '.metadata.json');
    if (existsSync(metadataPath)) {
      const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'));
      metadata.last_build = {
        timestamp: new Date().toISOString(),
        bundle_sha: contentHash,
        duration_ms: Date.now() - startTime,
      };
      writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    }
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`✓ Build completed in ${duration}s`);
    console.log(`Output: ${outputPath}`);
    
    return {
      path: outputPath,
      bundle_sha: contentHash,
      duration_ms: Date.now() - startTime,
    };
    
  } catch (error) {
    console.error('Build failed:', error);
    throw error;
  }
}

// Run build if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  buildDeck().catch(error => {
    console.error(error);
    process.exit(1);
  });
}

export { buildDeck };