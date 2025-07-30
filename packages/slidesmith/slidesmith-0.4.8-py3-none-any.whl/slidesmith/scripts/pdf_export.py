#!/usr/bin/env python3
"""
PDF export tool using Playwright.
Generates print-ready PDFs with metadata and bookmarks.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from playwright.sync_api import sync_playwright
from PyPDF2 import PdfReader, PdfWriter

# Page formats in inches
PAGE_FORMATS = {
    'A4': {'width': 11.69, 'height': 8.27},  # Landscape A4
    'Letter': {'width': 11, 'height': 8.5},
    'Slide': {'width': 10, 'height': 5.625},  # 16:9 aspect ratio
    'Custom': {'width': 13.33, 'height': 7.5}  # Custom widescreen
}


def extract_deck_metadata(deck_path: Path) -> Dict[str, Any]:
    """Extract deck metadata for PDF properties."""
    metadata = {}
    
    # Read deck metadata if available
    metadata_path = deck_path / '.metadata.json'
    if metadata_path.exists():
        with open(metadata_path) as f:
            deck_meta = json.load(f)
            metadata.update(deck_meta)
    
    # Try to get title from deck configuration
    config_path = deck_path / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            if 'title' in config:
                metadata['title'] = config['title']
            if 'author' in config:
                metadata['author'] = config['author']
    
    return metadata


def extract_slide_titles(page) -> List[Dict[str, Any]]:
    """Extract slide titles and positions for bookmarks."""
    slides_info = []
    
    # Execute JavaScript to get slide information
    slide_data = page.evaluate("""
        () => {
            const slides = document.querySelectorAll('.slide');
            const slideInfo = [];
            
            slides.forEach((slide, index) => {
                const slideNumber = index + 1;
                
                // Try to find the main heading in order of preference
                let title = '';
                const h1 = slide.querySelector('h1');
                const h2 = slide.querySelector('h2');
                const h3 = slide.querySelector('h3');
                const titleEl = slide.querySelector('[data-title]');
                
                if (titleEl) {
                    title = titleEl.getAttribute('data-title');
                } else if (h1) {
                    title = h1.textContent.trim();
                } else if (h2) {
                    title = h2.textContent.trim();
                } else if (h3) {
                    title = h3.textContent.trim();
                }
                
                // Fallback to slide number if no title found
                if (!title) {
                    title = `Slide ${slideNumber}`;
                }
                
                // Clean up title (remove extra whitespace, limit length)
                title = title.replace(/\\s+/g, ' ').trim();
                if (title.length > 60) {
                    title = title.substring(0, 57) + '...';
                }
                
                slideInfo.push({
                    number: slideNumber,
                    title: title,
                    page: slideNumber
                });
            });
            
            return slideInfo;
        }
    """)
    
    return slide_data


def create_pdf_metadata(deck_metadata: Dict[str, Any], slides_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create PDF metadata object."""
    # Get current date
    now = datetime.now()
    
    # Build PDF metadata
    pdf_metadata = {
        'title': deck_metadata.get('title', 'SlideSmith Presentation'),
        'author': deck_metadata.get('author', 'SlideSmith'),
        'subject': f'Presentation with {len(slides_info)} slides',
        'keywords': 'slidesmith, presentation, slides',
        'creator': 'SlideSmith MCP Server',
        'producer': 'SlideSmith via Playwright',
        'creation_date': now.isoformat(),
        'modification_date': now.isoformat()
    }
    
    return pdf_metadata


def add_pdf_metadata_and_bookmarks(pdf_path: Path, metadata: Dict[str, Any], slides_info: List[Dict[str, Any]]) -> None:
    """Add metadata and bookmarks to the PDF file."""
    try:
        # Read the original PDF
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Add metadata
        writer.add_metadata({
            '/Title': metadata['title'],
            '/Author': metadata['author'],
            '/Subject': metadata['subject'],
            '/Keywords': metadata['keywords'],
            '/Creator': metadata['creator'],
            '/Producer': metadata['producer']
        })
        
        # Add bookmarks for each slide
        for slide_info in slides_info:
            # Page numbers in PyPDF2 are 0-indexed
            page_num = slide_info['page'] - 1
            if page_num < len(reader.pages):
                writer.add_outline_item(
                    title=slide_info['title'],
                    page_number=page_num
                )
        
        # Write the enhanced PDF
        temp_path = pdf_path.with_suffix('.tmp.pdf')
        with open(temp_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Replace original with enhanced version
        temp_path.replace(pdf_path)
        
        print(f'✓ Added metadata and {len(slides_info)} bookmarks', file=sys.stderr)
        
    except Exception as e:
        print(f'⚠ Warning: Could not add PDF metadata/bookmarks: {e}', file=sys.stderr)
        # Continue without metadata enhancement


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
    
    # Extract deck metadata for PDF properties
    deck_metadata = extract_deck_metadata(deck_path)
    
    # Check lint score if metadata exists
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
            last_lint = metadata.get('last_lint')
            if last_lint and isinstance(last_lint, dict):
                score = last_lint.get('score', 0)
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
        
        # Extract slide information for bookmarks
        slides_info = extract_slide_titles(page)
        print(f'Found {len(slides_info)} slides', file=sys.stderr)
        
        # Create PDF metadata
        pdf_metadata = create_pdf_metadata(deck_metadata, slides_info)
        
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
    
    # Add metadata and bookmarks to the PDF
    add_pdf_metadata_and_bookmarks(output_path, pdf_metadata, slides_info)
    
    # Get file size (after metadata enhancement)
    size_bytes = output_path.stat().st_size
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Print human-readable output to stderr
    print(f'✓ PDF exported to {output_path}', file=sys.stderr)
    print(f'Size: {size_bytes / 1024 / 1024:.1f} MB', file=sys.stderr)
    print(f'Pages: {len(slides_info)}', file=sys.stderr)
    print(f'Title: {pdf_metadata["title"]}', file=sys.stderr)
    print(f'Author: {pdf_metadata["author"]}', file=sys.stderr)
    print(f'Bookmarks: {len(slides_info)}', file=sys.stderr)
    print(f'Duration: {duration_ms}ms', file=sys.stderr)
    
    # Output JSON to stdout
    result = {
        'path': str(output_path),
        'size_bytes': size_bytes,
        'format': format_name,
        'orientation': orientation,
        'duration_ms': duration_ms,
        'pages': len(slides_info),
        'metadata': pdf_metadata,
        'bookmarks': slides_info
    }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()