#!/usr/bin/env node

import { chromium } from 'playwright';
import { existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const args = process.argv.slice(2);
const deckId = args[0];
const workspaceRoot = args[1];
const slideNumber = args[2] || '1';
const clipJson = args[3]; // Optional clip region as JSON string

if (!deckId || !workspaceRoot) {
  console.error('Usage: node snapshot.js <deck-id> <workspace-root> [slide-number] [clip-json]');
  process.exit(1);
}

async function takeSnapshot() {
  const startTime = Date.now();
  
  try {
    // Check if deck.html exists
    const htmlPath = join(workspaceRoot, 'build', 'deck.html');
    if (!existsSync(htmlPath)) {
      throw new Error('deck.html not found - run build first');
    }
    
    // Create snapshots directory
    const snapshotsDir = join(workspaceRoot, 'snapshots');
    mkdirSync(snapshotsDir, { recursive: true });
    
    // Launch browser
    console.log('Launching browser for snapshot...');
    const browser = await chromium.launch({ 
      headless: true,
      args: ['--force-device-scale-factor=2'] // For high DPI screenshots
    });
    
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 2 // Retina quality
    });
    
    const page = await context.newPage();
    
    // Load the deck
    await page.goto(`file://${htmlPath}`);
    await page.waitForLoadState('networkidle');
    
    // Wait for slide to render
    await page.waitForSelector('.slide', { timeout: 5000 });
    
    // Wait a bit more for fonts and animations
    await page.waitForTimeout(500);
    
    // Prepare screenshot options
    const screenshotOptions = {
      type: 'png',
      fullPage: false
    };
    
    // Handle clip region if provided
    if (clipJson) {
      try {
        const clip = JSON.parse(clipJson);
        screenshotOptions.clip = {
          x: clip.x || 0,
          y: clip.y || 0,
          width: clip.width || 1920,
          height: clip.height || 1080
        };
        console.log(`Using clip region:`, screenshotOptions.clip);
      } catch (e) {
        console.warn('Invalid clip JSON, capturing full slide');
      }
    }
    
    // Take screenshot
    const outputPath = join(snapshotsDir, `slide-${slideNumber.padStart(2, '0')}.png`);
    
    if (screenshotOptions.clip) {
      // For clipped screenshots, capture the page
      await page.screenshot({
        ...screenshotOptions,
        path: outputPath
      });
    } else {
      // For full slide, capture the slide container
      const slideContainer = await page.$('.slide');
      if (slideContainer) {
        await slideContainer.screenshot({
          path: outputPath
        });
      } else {
        // Fallback to full page
        await page.screenshot({
          path: outputPath,
          fullPage: false
        });
      }
    }
    
    // Get file stats
    const fs = await import('fs');
    const stats = fs.statSync(outputPath);
    
    // Clean up
    await browser.close();
    
    const duration = Date.now() - startTime;
    console.log(`✓ Snapshot saved in ${duration}ms`);
    console.log(`Output: ${outputPath}`);
    console.log(`Size: ${(stats.size / 1024).toFixed(1)} KB`);
    
    // Return result
    return {
      path: outputPath,
      size_bytes: stats.size,
      duration_ms: duration,
      dimensions: {
        width: screenshotOptions.clip ? screenshotOptions.clip.width : 1920,
        height: screenshotOptions.clip ? screenshotOptions.clip.height : 1080
      }
    };
    
  } catch (error) {
    console.error('Snapshot failed:', error);
    throw error;
  }
}

// Run snapshot if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  takeSnapshot().then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error(error);
    process.exit(1);
  });
}

export { takeSnapshot };