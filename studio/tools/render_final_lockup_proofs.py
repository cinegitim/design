#!/usr/bin/env python3
"""Capability-aware headless Chrome proof captures. No image-model calls."""
from pathlib import Path
import os
import signal
import subprocess
import tempfile
import json
import hashlib

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'brands/asyada-egitim/explorations/final-lockup-family'
CHROME=Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
SIZES={'P-01':(560,794),'H-02':(1100,240),'C-03':(600,256),'D-04':(375,112),'F-05':(1123,794)}

def main():
    if not CHROME.exists():raise RuntimeError('Headless Chrome unavailable; do not claim screenshots.')
    (RUN/'application-screenshots').mkdir(exist_ok=True)
    for i,(w,h) in SIZES.items():
        out=RUN/'application-screenshots'/f'{i}.png';source=RUN/'applications'/f'{i}-application.html'
        with tempfile.TemporaryDirectory(prefix='lockup-browser-',dir=Path.home()/'.cache/brand-studio') as profile:
            args=[str(CHROME),'--headless','--disable-gpu','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--no-first-run','--no-default-browser-check','--hide-scrollbars','--force-device-scale-factor=1',f'--user-data-dir={profile}',f'--window-size={w},{h}','--timeout=4000',f'--screenshot={out}',source.as_uri()]
            # Chrome's updater may outlive capture. Bound this OWN process group,
            # never touch a user's existing browser. A file must exist to accept.
            p=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=5)
            if not out.exists():raise RuntimeError(f'{i}: no screenshot; inspection unavailable')
            print(f'{i}: {out.relative_to(ROOT)} ({w}×{h} viewport)')
    manifest=json.loads((RUN/'manifest.json').read_text())
    proofs={}
    for p in sorted(RUN.rglob('*.png')):
        proofs[p.relative_to(RUN).as_posix()]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
             'canonical_logo_sha256':manifest['canonical_logo_sha256'],
             'source_wordmark_sha256':manifest['source_wordmark_sha256'],
             'method':'Deterministic SVG rasterization or headless Chrome screenshot; no image generation.',
             'status':'HUMAN FINAL LOCKUP APPROVAL PENDING'}
    (RUN/'inspection-manifest.json').write_text(json.dumps(proofs,indent=2))

if __name__=='__main__':main()
