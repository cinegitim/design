#!/usr/bin/env python3
"""Render Çin Eğitim typography finalists comparison board using Headless Chromium."""
import os
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML_PATH = HERE / "index.html"
OUT_PNG = HERE / "typography-finalists-comparison.png"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def main():
    if not HTML_PATH.exists():
        raise FileNotFoundError(f"Missing {HTML_PATH}")
    
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--virtual-time-budget=5000",
        "--run-all-compositor-stages-before-draw",
        "--window-size=1500,3100",
        "--default-background-color=00000000",
        f"--screenshot={OUT_PNG}",
        f"file://{HTML_PATH}"
    ]
    print("Rendering typography finalists board to PNG...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Chrome error:", res.stderr)
        raise RuntimeError("Failed to render screenshot")
    
    if not OUT_PNG.exists() or OUT_PNG.stat().st_size == 0:
        raise RuntimeError("Output image is empty or missing")
    
    size_kb = OUT_PNG.stat().st_size / 1024
    print(f"Successfully rendered: {OUT_PNG} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
