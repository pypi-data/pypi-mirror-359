#!/usr/bin/env python3
"""
PDF export tool using Playwright.
Generates print-ready PDFs from slide decks.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

from playwright.sync_api import sync_playwright

# Page formats in inches
PAGE_FORMATS = {
    'A4': {'width': 11.69, 'height': 8.27},  # Landscape A4
    'Letter': {'width': 11, 'height': 8.5},
    'Slide': {'width': 10, 'height': 5.625},  # 16:9 aspect ratio
    'Custom': {'width': 13.33, 'height': 7.5}  # Custom widescreen
}


def main():
    """Main PDF export function."""
    if len(sys.argv) < 3:
        print('Usage: python pdf_export.py <deck-id> <workspace-root> [filename] [format] [orientation]')
        sys.exit(1)
    
    deck_id = sys.argv[1]
    workspace_root = sys.argv[2]
    output_filename = sys.argv[3] if len(sys.argv) > 3 else 'deck.pdf'
    format_name = sys.argv[4] if len(sys.argv) > 4 else 'A4'
    orientation = sys.argv[5] if len(sys.argv) > 5 else 'landscape'
    
    # Build paths
    deck_path = Path(workspace_root) / deck_id
    html_path = deck_path / 'build' / 'deck.html'
    exports_dir = deck_path / 'exports'
    metadata_path = deck_path / '.metadata.json'
    
    if not html_path.exists():
        raise FileNotFoundError('deck.html not found - run build first')
    
    # Check lint score if metadata exists
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
            if 'last_lint' in metadata and metadata['last_lint'] is not None:
                score = metadata['last_lint'].get('score', 0)
                if score < 80:
                    raise ValueError(
                        f'Quality score too low: {score}/100. Required: 80/100'
                    )
    
    # Create exports directory
    exports_dir.mkdir(exist_ok=True)
    
    start_time = time.time()
    
    # Get page format
    page_format = PAGE_FORMATS.get(format_name, PAGE_FORMATS['A4'])
    
    # Swap dimensions for portrait
    if orientation == 'portrait':
        page_format = {
            'width': page_format['height'],
            'height': page_format['width']
        }
    
    # Launch browser and export PDF
    with sync_playwright() as p:
        print('Launching browser for PDF export...', file=sys.stderr)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Load the deck
        page.goto(f'file://{html_path}')
        page.wait_for_load_state('networkidle')
        
        # Wait for all slides to render
        page.wait_for_selector('.slide', timeout=5000)
        
        # Add print styles
        page.add_style_tag(content="""
            @media print {
                body { margin: 0; padding: 0; }
                .slide {
                    page-break-after: always;
                    width: 100vw !important;
                    height: 100vh !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    overflow: hidden !important;
                }
                .slide:last-child {
                    page-break-after: avoid;
                }
                @page {
                    margin: 0;
                    size: A4 landscape;
                }
            }
        """)
        
        # Wait for styles to apply
        page.wait_for_timeout(500)
        
        # Generate PDF
        output_path = exports_dir / f'{output_filename}.pdf'
        page.pdf(
            path=str(output_path),
            format=format_name if format_name != 'Custom' else None,
            width=f'{page_format["width"]}in' if format_name == 'Custom' else None,
            height=f'{page_format["height"]}in' if format_name == 'Custom' else None,
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
            prefer_css_page_size=True
        )
        
        browser.close()
    
    # Get file size
    size_bytes = output_path.stat().st_size
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Print human-readable output to stderr
    print(f'✓ PDF exported to {output_path}', file=sys.stderr)
    print(f'Size: {size_bytes / 1024 / 1024:.1f} MB', file=sys.stderr)
    print(f'Pages: estimated {len(list(deck_path.glob("src/slide-*.md")))}', file=sys.stderr)
    print(f'Duration: {duration_ms}ms', file=sys.stderr)
    
    # Output JSON to stdout
    result = {
        'path': str(output_path),
        'size_bytes': size_bytes,
        'format': format_name,
        'orientation': orientation,
        'duration_ms': duration_ms
    }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()