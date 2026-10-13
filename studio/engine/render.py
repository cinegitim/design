"""
Universal Design Engine Renderer
Supports: Carousel, Rollup, Flyer, Business Card
Uses Google Chrome in headless mode for zero-dependency high-resolution rendering.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

CHROME_BIN = os.environ.get(
    "CHROME_PATH",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)

def render_html_to_png(html_path, out_png, width, height, scale=2):
    """Render a local HTML file to PNG using headless Chrome."""
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--force-device-scale-factor={scale}",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"file://{os.path.abspath(html_path)}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Chrome screenshot failed: {res.stderr}")
    return out_png

def generate_carousel(data, template_html, output_dir):
    """Generate all slides of a carousel from JSON data."""
    os.makedirs(output_dir, exist_ok=True)
    slides = data.get("slides", [])
    campaign_title = data.get("title", "Carousel")
    
    generated_images = []
    
    # Process each slide
    for idx, slide in enumerate(slides, 1):
        slide_id = f"{idx:02d}-{slide.get('type', 'slide')}"
        slide_data = {
            "title": campaign_title,
            "current_slide": idx,
            "total_slides": len(slides),
            **slide
        }
        
        # Inject data into template
        slide_html_content = template_html.replace("__SLIDE_DATA__", json.dumps(slide_data, ensure_ascii=False))
        html_file = os.path.join(output_dir, f"{slide_id}.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(slide_html_content)
        
        # Render PNG
        png_file = os.path.join(output_dir, f"{slide_id}.png")
        render_html_to_png(html_file, png_file, width=1080, height=1350, scale=1)
        generated_images.append({
            "id": slide_id,
            "html": f"{slide_id}.html",
            "png": f"{slide_id}.png",
            "headline": slide.get("headline", "")
        })
        print(f"  ✓ Rendered slide {idx}/{len(slides)}: {slide_id}.png")
        
    # Generate gallery review index.html
    generate_gallery_index(campaign_title, generated_images, output_dir)
    return generated_images

def generate_gallery_index(title, slides, output_dir):
    """Generate a clean review gallery index.html for viewing/sharing."""
    cards_html = ""
    for s in slides:
        cards_html += f"""
        <div class="card">
            <div class="card-header">{s['id']} — {s['headline']}</div>
            <a href="{s['png']}" target="_blank">
                <img src="{s['png']}" alt="{s['id']}" loading="lazy"/>
            </a>
            <div class="card-footer">
                <a href="{s['html']}" target="_blank">HTML Kaynağı</a> • 
                <a href="{s['png']}" download>PNG İndir</a>
            </div>
        </div>
        """
        
    index_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Tasarım İnceleme</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&display=swap">
    <style>
        :root {{
            --paper: #F7F3E9;
            --ink: #1D2027;
            --red: #BD2120;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #0f1115;
            color: #e5e7eb;
            font-family: 'Jost', sans-serif;
            padding: 30px 20px;
        }}
        header {{
            max-width: 1400px;
            margin: 0 auto 30px auto;
            border-bottom: 1px solid #2d3748;
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{ font-size: 26px; color: #fff; }}
        .badge {{
            background: var(--red);
            color: #fff;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .card {{
            background: #1a1e26;
            border: 1px solid #2d3748;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-4px); }}
        .card-header {{
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 600;
            color: #a0aec0;
            background: #14171e;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .card img {{
            width: 100%;
            height: auto;
            display: block;
            background: var(--paper);
        }}
        .card-footer {{
            padding: 12px 16px;
            font-size: 13px;
            color: #718096;
            background: #14171e;
            text-align: right;
        }}
        .card-footer a {{
            color: #63b3ed;
            text-decoration: none;
            font-weight: 500;
        }}
        .card-footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>{title}</h1>
            <p style="color: #a0aec0; margin-top: 4px;">Asya'da Eğitim — Hızlı Üretim Motoru v2</p>
        </div>
        <span class="badge">{len(slides)} Slayt Hazır</span>
    </header>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

if __name__ == "__main__":
    print("Renderer loaded successfully.")
