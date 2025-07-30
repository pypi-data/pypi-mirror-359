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
  console.error('Usage: node build.js <deck-id> <workspace-root>');
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
      const esbuildModule = await import(esbuildPath);
      esbuild = esbuildModule.default || esbuildModule;
      
      // Resolve and import MDX plugin
      const mdxPath = require.resolve('@mdx-js/esbuild');
      const mdxModule = await import(mdxPath);
      mdxPlugin = mdxModule.default || mdxModule;
      
      // If mdxPlugin is still not a function, try to extract it
      if (typeof mdxPlugin !== 'function' && mdxPlugin.mdx) {
        mdxPlugin = mdxPlugin.mdx;
      }
    } catch (error) {
      console.error('Error loading build dependencies:', error);
      throw new Error(`Failed to load build dependencies: ${error.message}`);
    }
    
    // Step 1: Build MDX with esbuild
    console.log('Building MDX files...');
    
    // Get all MDX files
    const mdxFiles = [];
    const fs = await import('fs');
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
      plugin = typeof mdxPlugin === 'function' ? mdxPlugin(mdxOptions) : mdxPlugin;
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
    
    console.log('Starting esbuild...');
    let result;
    try {
      result = await esbuild.build(buildOptions);
    } catch (error) {
      console.error('esbuild error:', error);
      if (error.errors) {
        for (const err of error.errors) {
          console.error('Build error:', err);
        }
      }
      throw error;
    }
    
    // Step 2: Combine all JS outputs and calculate hash
    console.log('Combining output files...');
    let combinedContent = '';
    const outputFiles = fs.readdirSync(buildDir).filter(f => f.endsWith('.js'));
    
    if (outputFiles.length === 0) {
      throw new Error('No output files generated from build');
    }
    
    for (const file of outputFiles) {
      const content = readFileSync(join(buildDir, file), 'utf8');
      // Extract slide name from filename (e.g., slide-01.js -> Slide01)
      if (file.includes('slide-')) {
        const slideNum = file.match(/slide-(\d+)/)?.[1] || '01';
        const slideName = `Slide${slideNum.padStart(2, '0')}`;
        // Wrap the content to expose the default export to window
        combinedContent += `\n// File: ${file}\n(function() {\n${content}\nif (typeof export_default !== 'undefined') { window.${slideName} = export_default; }\n})();\n`;
      } else {
        combinedContent += `\n// File: ${file}\n${content}\n`;
      }
    }
    
    // Write combined bundle
    const bundlePath = join(buildDir, 'bundle.js');
    writeFileSync(bundlePath, combinedContent);
    
    const bundleHash = createHash('sha256').update(combinedContent).digest('hex');
    console.log(`Bundle hash: ${bundleHash.substring(0, 8)}`);
    
    // Step 3: Generate Tailwind CSS
    console.log('Generating Tailwind CSS...');
    
    // Create a temporary HTML file with all content for Tailwind to scan
    const tempHtml = `
      <html>
        <body>
          <div id="root"></div>
          <script type="module">${combinedContent}</script>
        </body>
      </html>
    `;
    writeFileSync(join(buildDir, 'temp.html'), tempHtml);
    
    // Run Tailwind CLI
    const tailwindCmd = `npx tailwindcss -i ${join(__dirname, '..', 'styles', 'base.css')} -o ${join(buildDir, 'styles.css')} --config ${tailwindConfigPath}`;
    
    try {
      execSync(tailwindCmd, { 
        stdio: 'inherit',
        cwd: workspaceRoot,
        env: { ...process.env, NODE_ENV: 'production' }
      });
    } catch (error) {
      console.error('Tailwind CSS generation failed:', error);
      throw error;
    }
    
    // Step 4: Create final HTML
    console.log('Creating final HTML...');
    
    const htmlTemplate = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slidesmith Presentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css">
    <style>${readFileSync(join(buildDir, 'styles.css'), 'utf8')}</style>
    <style>
      body { margin: 0; padding: 0; overflow: hidden; }
      #root { width: 100vw; height: 100vh; }
      .slide-container { 
        width: 1920px; 
        height: 1080px; 
        transform-origin: top left;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
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
      /* Hide navigation in print mode */
      @media print {
        .slide-navigation {
          display: none !important;
        }
        .slide-container {
          display: block !important;
          page-break-after: always;
          page-break-inside: avoid;
          position: relative !important;
          transform: none !important;
          top: 0 !important;
          left: 0 !important;
          width: 1920px !important;
          height: 1080px !important;
        }
      }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="module">
      import React from 'https://esm.sh/react@18';
      import ReactDOM from 'https://esm.sh/react-dom@18/client';
      import { MDXProvider } from 'https://esm.sh/@mdx-js/react@3';
      
      // Import components
      ${combinedContent}
      
      // Components map for MDX
      const components = {
        SlideBase: window.SlideBase,
        Header: window.Header,
        Footer: window.Footer,
        Columns: window.Columns,
        CardGrid: window.CardGrid,
        ImpactBox: window.ImpactBox,
        BulletList: window.BulletList,
        CheckList: window.CheckList,
        BarChart: window.BarChart,
        PieChart: window.PieChart,
        Timeline: window.Timeline,
        MetricSection: window.MetricSection,
        Calculation: window.Calculation,
        CTABox: window.CTABox
      };
      
      // Find all slide modules
      const slideModules = [];
      for (const key in window) {
        if (key.toLowerCase().includes('slide') && typeof window[key] === 'function') {
          slideModules.push({ key, component: window[key] });
        }
      }
      
      // Sort slides by key to ensure consistent order
      slideModules.sort((a, b) => a.key.localeCompare(b.key));
      
      if (slideModules.length > 0) {
        const root = ReactDOM.createRoot(document.getElementById('root'));
        
        // Create a slide deck component that renders all slides
        const SlideDeck = () => {
          const [currentSlide, setCurrentSlide] = React.useState(0);
          
          React.useEffect(() => {
            // Keyboard navigation
            const handleKeyDown = (e) => {
              if (e.key === 'ArrowRight' || e.key === ' ') {
                setCurrentSlide(prev => Math.min(prev + 1, slideModules.length - 1));
              } else if (e.key === 'ArrowLeft') {
                setCurrentSlide(prev => Math.max(prev - 1, 0));
              }
            };
            
            window.addEventListener('keydown', handleKeyDown);
            return () => window.removeEventListener('keydown', handleKeyDown);
          }, []);
          
          return React.createElement('div', {
            style: { width: '100%', height: '100%', position: 'relative' }
          },
            // Render all slides (for PDF export)
            slideModules.map((module, index) =>
              React.createElement('div', {
                key: module.key,
                className: 'slide-container',
                style: {
                  display: index === currentSlide ? 'block' : 'none',
                  pageBreakAfter: 'always',
                  pageBreakInside: 'avoid'
                }
              },
                React.createElement(module.component)
              )
            ),
            // Navigation UI (only visible in browser)
            React.createElement('div', {
              style: {
                position: 'fixed',
                bottom: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                zIndex: 1000,
                display: 'flex',
                gap: '10px',
                alignItems: 'center',
                background: 'rgba(0,0,0,0.8)',
                padding: '10px 20px',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px'
              },
              className: 'slide-navigation'
            },
              React.createElement('button', {
                onClick: () => setCurrentSlide(prev => Math.max(prev - 1, 0)),
                disabled: currentSlide === 0,
                style: { cursor: currentSlide === 0 ? 'not-allowed' : 'pointer' }
              }, '←'),
              React.createElement('span', {}, 
                (currentSlide + 1) + ' / ' + slideModules.length
              ),
              React.createElement('button', {
                onClick: () => setCurrentSlide(prev => Math.min(prev + 1, slideModules.length - 1)),
                disabled: currentSlide === slideModules.length - 1,
                style: { cursor: currentSlide === slideModules.length - 1 ? 'not-allowed' : 'pointer' }
              }, '→')
            )
          );
        };
        
        root.render(
          React.createElement(MDXProvider, { components },
            React.createElement(SlideDeck)
          )
        );
      }
    </script>
</body>
</html>`;
    
    // Write final HTML
    const outputPath = join(buildDir, 'deck.html');
    writeFileSync(outputPath, htmlTemplate);
    
    // Step 5: Update metadata with build info
    const metadataPath = join(workspaceRoot, '.metadata.json');
    if (existsSync(metadataPath)) {
      const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'));
      metadata.last_build = {
        timestamp: new Date().toISOString(),
        bundle_sha: bundleHash,
        duration_ms: Date.now() - startTime,
      };
      writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    }
    
    // Clean up temp files
    try {
      unlinkSync(join(buildDir, 'temp.html'));
    } catch (e) {
      // Ignore cleanup errors
    }
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`✓ Build completed in ${duration}s`);
    console.log(`Output: ${outputPath}`);
    
    // Return result for MCP tool
    return {
      path: outputPath,
      bundle_sha: bundleHash,
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