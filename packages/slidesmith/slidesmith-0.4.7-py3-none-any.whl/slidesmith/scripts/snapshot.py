#!/usr/bin/env python3
"""
Slide snapshot tool using Playwright.
Generates PNG screenshots of slides.
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

from playwright.sync_api import sync_playwright


def main():
    """Main snapshot function."""
    if len(sys.argv) < 3:
        print('Usage: python snapshot.py <deck-id> <workspace-root> [slide-number] [clip-json]')
        sys.exit(1)
    
    deck_id = sys.argv[1]
    workspace_root = sys.argv[2]
    slide_number = sys.argv[3] if len(sys.argv) > 3 else '1'
    clip_json = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Check if we need to capture all slides
    capture_all = slide_number == 'all'
    
    # Build paths
    deck_path = Path(workspace_root) / deck_id
    html_path = deck_path / 'build' / 'deck.html'
    snapshots_dir = deck_path / 'snapshots'
    
    if not html_path.exists():
        raise FileNotFoundError('deck.html not found - run build first')
    
    # Create snapshots directory
    snapshots_dir.mkdir(exist_ok=True)
    
    start_time = time.time()
    
    # Parse clip region if provided
    clip = None
    if clip_json:
        try:
            clip_data = json.loads(clip_json)
            clip = {
                'x': clip_data.get('x', 0),
                'y': clip_data.get('y', 0),
                'width': clip_data.get('width', 1920),
                'height': clip_data.get('height', 1080)
            }
            print(f'Using clip region: {clip}', file=sys.stderr)
        except:
            print('Invalid clip JSON, capturing full slide', file=sys.stderr)
    
    # Launch browser and take snapshot
    with sync_playwright() as p:
        print('Launching browser for snapshot...', file=sys.stderr)
        browser = p.chromium.launch(
            headless=True,
            args=['--force-device-scale-factor=2']  # For high DPI screenshots
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2  # Retina quality
        )
        page = context.new_page()
        
        # Load the deck
        if capture_all:
            page.goto(f'file://{html_path}')
        else:
            page.goto(f'file://{html_path}#slide-{slide_number}')
        page.wait_for_load_state('networkidle')
        
        # Wait for slides to be in DOM (they may be hidden)
        page.wait_for_selector('.slide', state='attached', timeout=5000)
        
        if capture_all:
            # Get total number of slides (excluding deck metadata slide)
            total_slides = page.evaluate('''
                const slides = document.querySelectorAll('.slide[data-slide]');
                // Filter out slides that only contain deck metadata
                const contentSlides = Array.from(slides).filter(slide => {
                    const text = slide.innerText || '';
                    return !text.includes('This deck is empty. Use the slide management tools');
                });
                return contentSlides.length;
            ''')
            
            print(f'Found {total_slides} content slides to capture', file=sys.stderr)
            
            # Create a combined image by arranging slides in a grid
            # For now, just capture the first content slide
            page.evaluate('''
                const slides = document.querySelectorAll('.slide[data-slide]');
                slides.forEach(slide => slide.style.display = 'none');
                
                // Find and show the first content slide
                const contentSlides = Array.from(slides).filter(slide => {
                    const text = slide.innerText || '';
                    return !text.includes('This deck is empty. Use the slide management tools');
                });
                
                if (contentSlides.length > 0) {
                    contentSlides[0].style.display = 'block';
                }
            ''')
            
            output_path = snapshots_dir / 'slide-all.png'
        else:
            # Navigate to specific slide if not slide 1
            if slide_number != '1':
                # Use JavaScript to show the correct slide
                page.evaluate(f'''
                    const slides = document.querySelectorAll('.slide');
                    slides.forEach(slide => slide.style.display = 'none');
                    const targetSlide = document.querySelector('.slide[data-slide="{slide_number}"]');
                    if (targetSlide) {{
                        targetSlide.style.display = 'block';
                    }}
                ''')
            
            output_path = snapshots_dir / f'slide-{slide_number.zfill(2)}.png'
        
        # Wait a bit more for fonts and animations
        page.wait_for_timeout(500)
        
        screenshot_options = {
            'path': str(output_path),
            'type': 'png',
            'full_page': False
        }
        
        if clip:
            screenshot_options['clip'] = clip
            page.screenshot(**screenshot_options)
        else:
            # Try to capture just the visible slide container
            slide_selector = f'.slide[data-slide="{slide_number}"]'
            slide_element = page.query_selector(slide_selector)
            if slide_element:
                # Check if this is the deck metadata slide
                is_metadata_slide = page.evaluate(f'''
                    const slide = document.querySelector('{slide_selector}');
                    const text = slide ? (slide.innerText || '') : '';
                    return text.includes('This deck is empty. Use the slide management tools');
                ''')
                
                if is_metadata_slide:
                    # Skip to the next actual content slide
                    page.evaluate(f'''
                        const slides = document.querySelectorAll('.slide[data-slide]');
                        slides.forEach(slide => slide.style.display = 'none');
                        
                        // Find the first content slide after this one
                        let found = false;
                        for (let i = {int(slide_number)}; i <= slides.length; i++) {{
                            const slide = document.querySelector('.slide[data-slide="' + i + '"]');
                            if (slide) {{
                                const text = slide.innerText || '';
                                if (!text.includes('This deck is empty. Use the slide management tools')) {{
                                    slide.style.display = 'block';
                                    found = true;
                                    break;
                                }}
                            }}
                        }}
                        
                        // If no content slide found, show the first content slide
                        if (!found) {{
                            const contentSlides = Array.from(slides).filter(slide => {{
                                const text = slide.innerText || '';
                                return !text.includes('This deck is empty. Use the slide management tools');
                            }});
                            if (contentSlides.length > 0) {{
                                contentSlides[0].style.display = 'block';
                            }}
                        }}
                    ''')
                    page.wait_for_timeout(100)
                    
                    # Re-query for the visible slide
                    visible_slide = page.query_selector('.slide[style*="display: block"]')
                    if visible_slide:
                        visible_slide.screenshot(path=str(output_path))
                    else:
                        page.screenshot(**screenshot_options)
                else:
                    # Ensure the slide is visible before screenshot
                    page.evaluate(f'''
                        const slide = document.querySelector('{slide_selector}');
                        if (slide) slide.style.display = 'block';
                    ''')
                    page.wait_for_timeout(100)  # Brief wait for render
                    slide_element.screenshot(path=str(output_path))
            else:
                # Fallback to full page
                page.screenshot(**screenshot_options)
        
        browser.close()
    
    # Get file size
    size_bytes = output_path.stat().st_size
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Print human-readable output to stderr
    print(f'✓ Snapshot saved to {output_path}', file=sys.stderr)
    print(f'Size: {size_bytes / 1024:.1f} KB', file=sys.stderr)
    print(f'Duration: {duration_ms}ms', file=sys.stderr)
    
    # Output JSON to stdout
    result = {
        'path': str(output_path),
        'size_bytes': size_bytes,
        'duration_ms': duration_ms
    }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()