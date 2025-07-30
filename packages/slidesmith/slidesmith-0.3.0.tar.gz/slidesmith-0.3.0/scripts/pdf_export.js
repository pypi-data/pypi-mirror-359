#!/usr/bin/env node

import { chromium } from 'playwright';
import { existsSync, mkdirSync, readFileSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const args = process.argv.slice(2);
const deckId = args[0];
const workspaceRoot = args[1];
const outputFilename = args[2] || 'deck.pdf';
const format = args[3] || 'A4';
const orientation = args[4] || 'landscape';

if (!deckId || !workspaceRoot) {
  console.error('Usage: node pdf_export.js <deck-id> <workspace-root> [filename] [format] [orientation]');
  process.exit(1);
}

// Page formats in inches
const PAGE_FORMATS = {
  'A4': { width: 11.69, height: 8.27 }, // Landscape A4
  'Letter': { width: 11, height: 8.5 },
  'Slide': { width: 10, height: 5.625 }, // 16:9 aspect ratio
  'Custom': { width: 13.33, height: 7.5 } // Custom widescreen
};

async function exportPdf() {
  const startTime = Date.now();
  
  try {
    // Check if deck.html exists
    const htmlPath = join(workspaceRoot, deckId, 'build', 'deck.html');
    if (!existsSync(htmlPath)) {
      throw new Error('deck.html not found - run build first');
    }
    
    // Check lint score if available
    const metadataPath = join(workspaceRoot, deckId, '.metadata.json');
    if (existsSync(metadataPath)) {
      const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'));
      if (metadata.last_lint && metadata.last_lint.score < 80) {
        throw new Error(`Quality score too low: ${metadata.last_lint.score}/100. Required: 80/100`);
      }
    }
    
    // Create exports directory
    const exportsDir = join(workspaceRoot, deckId, 'exports');
    mkdirSync(exportsDir, { recursive: true });
    
    // Launch browser
    console.log('Launching browser for PDF export...');
    const browser = await chromium.launch({ 
      headless: true,
      args: [
        '--force-device-scale-factor=2', // High DPI
        '--font-render-hinting=none', // Better font rendering
        '--disable-lcd-text' // Disable LCD optimization for print
      ]
    });
    
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 2 // High quality rendering
    });
    
    const page = await context.newPage();
    
    // Load the deck
    await page.goto(`file://${htmlPath}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    // Wait for slide to render completely
    await page.waitForSelector('.slide', { timeout: 5000 });
    
    // Wait for fonts to load
    await page.evaluate(() => {
      return document.fonts.ready;
    });
    
    // Additional wait for animations and images
    await page.waitForTimeout(1000);
    
    // Get page dimensions
    const pageFormat = PAGE_FORMATS[format] || PAGE_FORMATS['A4'];
    const isLandscape = orientation === 'landscape';
    
    const width = isLandscape ? pageFormat.width : pageFormat.height;
    const height = isLandscape ? pageFormat.height : pageFormat.width;
    
    // Configure PDF options
    const pdfOptions = {
      path: join(exportsDir, outputFilename),
      format: format === 'Custom' || format === 'Slide' ? undefined : format,
      width: format === 'Custom' || format === 'Slide' ? `${width}in` : undefined,
      height: format === 'Custom' || format === 'Slide' ? `${height}in` : undefined,
      landscape: isLandscape && format !== 'Custom' && format !== 'Slide',
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
      margin: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      },
      scale: 1.0
    };
    
    // Count the number of slides
    const slideCount = await page.evaluate(() => {
      return document.querySelectorAll('.slide-container').length;
    });
    
    console.log(`Found ${slideCount} slides to export...`);
    
    // Add custom CSS for print - ensure all slides are visible
    await page.addStyleTag({
      content: `
        @media print {
          body {
            margin: 0;
            padding: 0;
          }
          .slide-navigation {
            display: none !important;
          }
          .slide-container {
            display: block !important;
            page-break-after: always;
            page-break-inside: avoid;
            transform: none !important;
            position: relative !important;
            top: 0 !important;
            left: 0 !important;
            width: 1920px !important;
            height: 1080px !important;
            max-width: none !important;
            max-height: none !important;
            margin: 0 !important;
            padding: 0 !important;
          }
          /* Ensure last slide doesn't have page break */
          .slide-container:last-of-type {
            page-break-after: avoid;
          }
        }
      `
    });
    
    // Make all slides visible for PDF export
    await page.evaluate(() => {
      const slides = document.querySelectorAll('.slide-container');
      slides.forEach(slide => {
        slide.style.display = 'block';
        slide.style.pageBreakAfter = 'always';
        slide.style.pageBreakInside = 'avoid';
      });
      // Remove page break from last slide
      if (slides.length > 0) {
        slides[slides.length - 1].style.pageBreakAfter = 'avoid';
      }
    });
    
    // Generate PDF
    console.log(`Generating PDF (${format} ${orientation})...`);
    await page.pdf(pdfOptions);
    
    // Get file stats
    const stats = statSync(pdfOptions.path);
    const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
    
    // Close browser
    await browser.close();
    
    const duration = Date.now() - startTime;
    console.log(`✓ PDF exported in ${duration}ms`);
    console.log(`Output: ${pdfOptions.path}`);
    console.log(`Size: ${sizeInMB} MB`);
    console.log(`Format: ${format} ${orientation}`);
    
    // Check file size
    if (stats.size > 10 * 1024 * 1024) {
      console.warn(`⚠️  Warning: PDF size (${sizeInMB} MB) exceeds recommended 10 MB`);
    }
    
    // Return result
    return {
      path: pdfOptions.path,
      size_bytes: stats.size,
      duration_ms: duration,
      format: `${format} ${orientation}`,
      pages: slideCount
    };
    
  } catch (error) {
    console.error('PDF export failed:', error);
    throw error;
  }
}

// Run export if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  exportPdf().then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error(error);
    process.exit(1);
  });
}

export { exportPdf };