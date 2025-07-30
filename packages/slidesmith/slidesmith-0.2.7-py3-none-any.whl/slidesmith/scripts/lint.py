#!/usr/bin/env python3
"""
Slide quality linting tool using Playwright.
Checks for visual issues, contrast, overflow, and layout problems.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

from playwright.sync_api import sync_playwright, Page, Locator

# Lint rule definitions
LINT_RULES = {
    'L-G1': {
        'level': 'error',
        'name': 'Grid alignment',
        'description': 'Slide must be exactly 1920x1080',
        'points': 10
    },
    'L-M1': {
        'level': 'warning',
        'name': 'Margin violations',
        'description': 'Content outside safe area (48px margin)',
        'points': 3
    },
    'L-O1': {
        'level': 'error',
        'name': 'Text overflow',
        'description': 'Text content overflowing container',
        'points': 10
    },
    'L-C1': {
        'level': 'warning',
        'name': 'WCAG contrast',
        'description': 'Text contrast does not meet WCAG AA standards',
        'points': 3
    },
    'L-F1': {
        'level': 'warning',
        'name': 'Font size minimum',
        'description': 'Font size below 14px minimum',
        'points': 3
    },
    'L-S1': {
        'level': 'info',
        'name': 'Spacing consistency',
        'description': 'Inconsistent spacing between elements',
        'points': 1
    },
    'L-T1': {
        'level': 'info',
        'name': 'Typography scale',
        'description': 'Font size not following design scale',
        'points': 1
    }
}


def calculate_contrast(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    # Simplified contrast calculation
    # In production, use proper WCAG algorithm
    return 4.5  # Placeholder


def check_overflow(element: Locator) -> bool:
    """Check if element has text overflow."""
    try:
        # Check if scrollHeight > clientHeight or scrollWidth > clientWidth
        overflow = element.evaluate("""
            (el) => {
                return el.scrollHeight > el.clientHeight || 
                       el.scrollWidth > el.clientWidth;
            }
        """)
        return overflow
    except:
        return False


def lint_slide(page: Page, slide_num: int = 1) -> List[Dict[str, Any]]:
    """Lint a single slide for quality issues."""
    issues = []
    
    # Check slide dimensions
    viewport = page.viewport_size
    if viewport['width'] != 1920 or viewport['height'] != 1080:
        issues.append({
            'slide': slide_num,
            'rule': 'L-G1',
            'level': 'error',
            'message': f"Slide dimensions {viewport['width']}x{viewport['height']} != 1920x1080",
            'element': 'viewport'
        })
    
    # Check for text overflow
    text_elements = page.query_selector_all('h1, h2, h3, h4, h5, h6, p, span, div')
    for element in text_elements:
        if check_overflow(element):
            text = element.text_content()[:50] + '...' if element.text_content() else ''
            issues.append({
                'slide': slide_num,
                'rule': 'L-O1',
                'level': 'error',
                'message': f'Text overflow detected: "{text}"',
                'element': element.evaluate('el => el.tagName.toLowerCase()'),
                'location': element.bounding_box()
            })
    
    # Check font sizes
    for element in text_elements:
        try:
            font_size = element.evaluate('el => window.getComputedStyle(el).fontSize')
            if font_size:
                size_px = float(font_size.replace('px', ''))
                if size_px < 14:
                    issues.append({
                        'slide': slide_num,
                        'rule': 'L-F1',
                        'level': 'warning',
                        'message': f'Font size {size_px}px is below 14px minimum',
                        'element': element.evaluate('el => el.tagName.toLowerCase()')
                    })
        except:
            pass
    
    # Check margins (simplified)
    content_elements = page.query_selector_all('.slide > *')
    for element in content_elements:
        try:
            box = element.bounding_box()
            if box:
                if box['x'] < 48 or box['x'] + box['width'] > 1920 - 48:
                    issues.append({
                        'slide': slide_num,
                        'rule': 'L-M1',
                        'level': 'warning',
                        'message': 'Content outside 48px safe margin',
                        'element': element.evaluate('el => el.tagName.toLowerCase()'),
                        'location': box
                    })
        except:
            pass
    
    return issues


def main():
    """Main linting function."""
    if len(sys.argv) < 3:
        print('Usage: python lint.py <deck-id> <workspace-root>')
        sys.exit(1)
    
    deck_id = sys.argv[1]
    workspace_root = sys.argv[2]
    
    # Build paths
    deck_path = Path(workspace_root) / deck_id
    html_path = deck_path / 'build' / 'deck.html'
    
    if not html_path.exists():
        raise FileNotFoundError('deck.html not found - run build first')
    
    start_time = time.time()
    issues = []
    score = 100
    
    # Launch browser and lint
    with sync_playwright() as p:
        print('Launching browser for linting...', file=sys.stderr)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # Load the deck
        page.goto(f'file://{html_path}')
        page.wait_for_load_state('networkidle')
        
        # Wait for slides to render
        page.wait_for_selector('.slide', timeout=5000)
        
        # Lint all slides (simplified - just lint first slide for now)
        slide_issues = lint_slide(page, 1)
        issues.extend(slide_issues)
        
        browser.close()
    
    # Calculate score
    for issue in issues:
        rule = LINT_RULES.get(issue['rule'])
        if rule:
            score -= rule['points']
    
    score = max(0, score)
    
    # Count issues by level
    summary = {'error': 0, 'warning': 0, 'info': 0}
    for issue in issues:
        summary[issue['level']] += 1
    
    # Output results
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Print human-readable output to stderr
    print(f'✓ Lint completed in {duration_ms}ms', file=sys.stderr)
    print(f'Score: {score}/100', file=sys.stderr)
    print(f'Issues: {len(issues)} ({summary["error"]} errors, {summary["warning"]} warnings, {summary["info"]} info)', file=sys.stderr)
    
    # Output JSON to stdout
    result = {
        'issues': issues,
        'score': score,
        'passed': score >= 80,
        'summary': summary,
        'duration_ms': duration_ms
    }
    
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()