#!/usr/bin/env node

import { chromium } from 'playwright';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse command line arguments
const args = process.argv.slice(2);
const deckId = args[0];
const workspaceRoot = args[1];

if (!deckId || !workspaceRoot) {
  console.error('Usage: node lint.js <deck-id> <workspace-root>');
  process.exit(1);
}

// Lint rule definitions
const LINT_RULES = {
  'L-G1': {
    level: 'error',
    name: 'Grid alignment',
    description: 'Slide must be exactly 1920x1080',
    points: 10
  },
  'L-M1': {
    level: 'warning',
    name: 'Margin violations',
    description: 'Content outside safe area (48px margin)',
    points: 3
  },
  'L-O1': {
    level: 'error',
    name: 'Text overflow',
    description: 'Text content overflowing container',
    points: 10
  },
  'L-C1': {
    level: 'warning',
    name: 'WCAG contrast',
    description: 'Text contrast does not meet WCAG AA standards',
    points: 3
  },
  'L-F1': {
    level: 'warning',
    name: 'Font size minimum',
    description: 'Font size below 14px minimum',
    points: 3
  },
  'L-S1': {
    level: 'info',
    name: 'Spacing consistency',
    description: 'Inconsistent spacing between elements',
    points: 1
  },
  'L-T1': {
    level: 'info',
    name: 'Typography scale',
    description: 'Font size not following design scale',
    points: 1
  }
};

async function lintDeck() {
  const startTime = Date.now();
  const issues = [];
  let score = 100;
  
  try {
    // Check if deck.html exists
    const htmlPath = join(workspaceRoot, 'build', 'deck.html');
    if (!existsSync(htmlPath)) {
      throw new Error('deck.html not found - run build first');
    }
    
    // Launch browser
    console.error('Launching browser for linting...');
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 }
    });
    const page = await context.newPage();
    
    // Load the deck
    await page.goto(`file://${htmlPath}`);
    await page.waitForLoadState('networkidle');
    
    // Wait for slide to render
    await page.waitForSelector('.slide', { timeout: 5000 });
    
    // L-G1: Check grid alignment
    const slideContainer = await page.$('.slide');
    if (slideContainer) {
      const box = await slideContainer.boundingBox();
      if (box.width !== 1920 || box.height !== 1080) {
        issues.push({
          rule: 'L-G1',
          level: 'error',
          message: `Slide dimensions ${box.width}x${box.height} do not match 1920x1080`,
          element: '.slide-container',
          location: { x: box.x, y: box.y }
        });
        score -= LINT_RULES['L-G1'].points;
      }
    }
    
    // L-M1: Check margin violations
    const elements = await page.$$('.slide-base > *');
    for (const element of elements) {
      const box = await element.boundingBox();
      if (box) {
        if (box.x < 48 || box.y < 48 || 
            box.x + box.width > 1920 - 48 || 
            box.y + box.height > 1080 - 48) {
          const handle = await element.evaluateHandle(el => el);
          const tagName = await handle.evaluate(el => el.tagName);
          
          issues.push({
            rule: 'L-M1',
            level: 'warning',
            message: 'Content extends outside 48px safe margin',
            element: tagName.toLowerCase(),
            location: { x: box.x, y: box.y }
          });
          score -= LINT_RULES['L-M1'].points;
        }
      }
    }
    
    // L-O1: Check text overflow
    const textElements = await page.$$('h1, h2, h3, p, span, div');
    for (const element of textElements) {
      const isOverflowing = await element.evaluate(el => {
        return el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight;
      });
      
      if (isOverflowing) {
        const box = await element.boundingBox();
        const text = await element.textContent();
        
        issues.push({
          rule: 'L-O1',
          level: 'error',
          message: `Text overflow detected: "${text.substring(0, 50)}..."`,
          element: await element.evaluate(el => el.tagName.toLowerCase()),
          location: box ? { x: box.x, y: box.y } : null
        });
        score -= LINT_RULES['L-O1'].points;
      }
    }
    
    // L-F1: Check font sizes
    const textNodes = await page.$$('h1, h2, h3, h4, h5, h6, p, span, li');
    for (const element of textNodes) {
      const fontSize = await element.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return parseFloat(computed.fontSize);
      });
      
      if (fontSize < 14) {
        const box = await element.boundingBox();
        const text = await element.textContent();
        
        issues.push({
          rule: 'L-F1',
          level: 'warning',
          message: `Font size ${fontSize}px below 14px minimum`,
          element: await element.evaluate(el => el.tagName.toLowerCase()),
          location: box ? { x: box.x, y: box.y } : null
        });
        score -= LINT_RULES['L-F1'].points;
      }
    }
    
    // L-C1: Basic contrast check (simplified)
    const textWithBg = await page.$$('[style*="color"], [style*="background"]');
    for (const element of textWithBg) {
      const styles = await element.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          color: computed.color,
          background: computed.backgroundColor
        };
      });
      
      // Simple check - would need proper WCAG calculation
      if (styles.color && styles.background && 
          styles.color !== 'rgb(0, 0, 0)' && 
          styles.background !== 'rgba(0, 0, 0, 0)') {
        // This is a placeholder - real implementation would calculate contrast ratio
        console.error('Contrast check needed for:', styles);
      }
    }
    
    // Clean up
    await browser.close();
    
    // Ensure score doesn't go below 0
    score = Math.max(0, score);
    
    // Calculate summary
    const summary = {
      error: issues.filter(i => i.level === 'error').length,
      warning: issues.filter(i => i.level === 'warning').length,
      info: issues.filter(i => i.level === 'info').length
    };
    
    const duration = Date.now() - startTime;
    console.error(`✓ Lint completed in ${duration}ms`);
    console.error(`Score: ${score}/100`);
    console.error(`Issues: ${issues.length} (${summary.error} errors, ${summary.warning} warnings, ${summary.info} info)`);
    
    // Return result
    return {
      issues,
      score,
      passed: score >= 70,
      summary,
      duration_ms: duration
    };
    
  } catch (error) {
    console.error('Lint failed:', error);
    throw error;
  }
}

// Run lint if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  lintDeck().then(result => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.passed ? 0 : 1);
  }).catch(error => {
    console.error(error);
    process.exit(1);
  });
}

export { lintDeck };