#!/usr/bin/env node

import { createRequire } from 'module';
import { execSync } from 'child_process';
import { createHash } from 'crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync, unlinkSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const args = process.argv.slice(2);
const deckId = args[0];
const workspaceRoot = args[1];

if (!deckId || !workspaceRoot) {
  console.error('Usage: node build-debug.js <deck-id> <workspace-root>');
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
    const tailwindConfigPath = join(workspaceRoot, 'tailwind.config.js');
    
    // Ensure build directory exists
    mkdirSync(buildDir, { recursive: true });
    
    // Dynamic module loading with workspace resolution
    console.log('Loading build dependencies...');
    const require = createRequire(join(workspaceRoot, 'package.json'));
    
    // Import esbuild and MDX plugin
    let esbuild, mdxPlugin;
    try {
      // Resolve and import esbuild
      const esbuildPath = require.resolve('esbuild');
      console.log('esbuild path:', esbuildPath);
      const esbuildModule = await import(esbuildPath);
      esbuild = esbuildModule.default || esbuildModule;
      console.log('esbuild loaded:', typeof esbuild.build);
      
      // Resolve and import MDX plugin
      const mdxPath = require.resolve('@mdx-js/esbuild');
      console.log('MDX plugin path:', mdxPath);
      const mdxModule = await import(mdxPath);
      console.log('MDX module keys:', Object.keys(mdxModule));
      console.log('MDX module.default type:', typeof mdxModule.default);
      
      mdxPlugin = mdxModule.default || mdxModule;
      
      // If mdxPlugin is still not a function, try to extract it
      if (typeof mdxPlugin !== 'function' && mdxPlugin.mdx) {
        console.log('Extracting mdx from mdxPlugin object');
        mdxPlugin = mdxPlugin.mdx;
      }
      
      console.log('Final mdxPlugin type:', typeof mdxPlugin);
    } catch (error) {
      console.error('Error loading build dependencies:', error);
      throw new Error(`Failed to load build dependencies: ${error.message}`);
    }
    
    // Get all MDX files
    const fs = await import('fs');
    const mdxFiles = [];
    const files = fs.readdirSync(srcDir);
    for (const file of files) {
      if (file.endsWith('.mdx')) {
        mdxFiles.push(join(srcDir, file));
      }
    }
    
    if (mdxFiles.length === 0) {
      throw new Error('No MDX files found in src directory');
    }
    
    console.log(`Found ${mdxFiles.length} MDX files to build`);
    
    // Configure MDX plugin options
    const mdxOptions = {
      jsxRuntime: 'automatic',
      jsxImportSource: 'react',
      development: false,
      providerImportSource: '@mdx-js/react'
    };
    
    // Create the plugin instance
    let plugin;
    try {
      console.log('Creating MDX plugin with options:', mdxOptions);
      plugin = typeof mdxPlugin === 'function' ? mdxPlugin(mdxOptions) : mdxPlugin;
      console.log('Plugin created:', plugin);
      console.log('Plugin name:', plugin?.name);
      console.log('Plugin setup type:', typeof plugin?.setup);
    } catch (error) {
      console.error('Error creating MDX plugin:', error);
      throw new Error(`Failed to create MDX plugin: ${error.message}`);
    }
    
    // Build configuration
    const buildOptions = {
      entryPoints: mdxFiles,
      bundle: true,
      outdir: buildDir,
      format: 'esm',
      platform: 'browser',
      target: ['es2020'],
      jsx: 'automatic',
      jsxImportSource: 'react',
      loader: {
        '.js': 'jsx',
        '.jsx': 'jsx',
        '.ts': 'tsx',
        '.tsx': 'tsx',
        '.woff': 'dataurl',
        '.woff2': 'dataurl',
      },
      plugins: plugin ? [plugin] : [],
      external: ['react', 'react-dom', '@mdx-js/react', 'react/jsx-runtime', 'react/jsx-dev-runtime', 'chart.js/auto'],
      define: {
        'process.env.NODE_ENV': '"production"',
      },
      minify: false,
      sourcemap: false,
      metafile: true,
      logLevel: 'info',
    };
    
    console.log('Build options plugins:', buildOptions.plugins);
    console.log('Starting esbuild...');
    
    let result;
    try {
      result = await esbuild.build(buildOptions);
      console.log('Build completed successfully');
    } catch (error) {
      console.error('esbuild error:', error);
      if (error.errors) {
        for (const err of error.errors) {
          console.error('Build error:', err);
        }
      }
      throw error;
    }
    
    console.log('Build succeeded!');
    
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