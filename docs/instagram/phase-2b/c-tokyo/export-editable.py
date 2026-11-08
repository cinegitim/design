#!/usr/bin/env python3
"""Run inside an extracted carousel folder: python3 export-editable.py.
Requires Chrome. Set CHROME_BIN to override its executable path. No AI calls.
"""
from pathlib import Path
import os, subprocess, tempfile

root=Path(__file__).resolve().parent
chrome=os.environ.get('CHROME_BIN','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
out=root/'png';out.mkdir(exist_ok=True)
for source in sorted((root/'editable').glob('*.html')):
    with tempfile.TemporaryDirectory(prefix='carousel-export-') as profile:
        subprocess.run([chrome,'--headless','--disable-gpu','--hide-scrollbars',
            '--force-device-scale-factor=1','--window-size=1080,1350',
            '--virtual-time-budget=3000',f'--user-data-dir={profile}',
            f'--screenshot={out/(source.stem+".png")}',source.as_uri()],check=True,timeout=30)
    print(source.stem+' exported. Reinspect artwork and update PNG hashes before publishing.')
