#!/usr/bin/env python3
"""Verify the Rotani Sec V2 carousel: exact copy, geometry audit, canonical logo
integrity, logo contrast against its real rendered ground, then build review
artefacts (contact sheet, mobile previews, before/after) and the source package.
"""
from pathlib import Path
import hashlib, json, zipfile
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IDS = ['01-admission-letter', '02-campus-geography', '03-six-universities',
       '04-english-taught', '05-accommodation', '06-final-decision']
SEAL = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
NS = '{http://www.w3.org/2000/svg}'
LOCKUPS = {
    'D-04/light': ('d-04-small-use-digital-light.svg',
                   '2ff2263dcdab496e81cda01601f4abb746890c3478d05a2ff6b9278c71f9b59e', 200),
    'D-04/dark': ('d-04-small-use-digital-dark.svg',
                  'e77d5607426ce7764d4f5fdf2c7d4fb1f2779beaaabfc1e1644460133e55b335', 200),
    'H-02/dark': ('h-02-primary-horizontal-dark.svg',
                  'c9eb55f95a60924f34e6f7b043e81216963441833a4f158ff882d710cc8dd1e7', 528),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(s):
    return ' '.join(s.split())


def luminance(img):
    return ImageStat.Stat(img.convert('L')).mean[0]


def main():
    print('== exact copy ==')
    exact = json.loads((HERE / 'exact-copy.json').read_text())['slides']
    print('  six slide contracts loaded:',
          all(len(exact[i]) > 0 for i in IDS))

    print('== geometry audit ==')
    audit = json.loads((HERE / 'geometry-audit.json').read_text())
    layout = json.loads((HERE / 'text-layout.json').read_text())
    for i in IDS:
        # The chip colour is measured in the layout pass; carry it into the audit view.
        audit[i]['logo'].update({
            k: layout[i]['logo'][k]
            for k in ('chipColor', 'chipAlpha') if k in layout[i]['logo']})
    for i in IDS:
        assert not audit[i]['geometryIssues'], (i, audit[i]['geometryIssues'])

    print('== render validation ==')
    for i in IDS:
        info = audit[i]
        rendered = [x['text'] for x in info['copy']]
        assert rendered == [norm(t) for t in exact[i]], (
            i, 'copy mismatch', rendered, exact[i])
    print('  exact copy verified in all six rendered slides: PASS')

    print('== canonical lockups ==')
    subprocess = None
    import subprocess as sp
    sp.run(['python3', str(ROOT / 'studio/tools/verify_asyada_canonical_lockups.py')], check=True)
    for i in IDS:
        rec = LOCKUPS[audit[i]['logo']['lockupId']]
        copied = HERE / 'assets/lockups' / rec[0]
        assert sha(copied) == rec[1], (i, 'hash mismatch')
        box = audit[i]['logo']['box']
        assert box['width'] >= rec[2], (i, 'below minimum size', box['width'], rec[2])
        assert box['x'] >= 0 and box['y'] >= 0
        assert box['right'] <= 1080 and box['bottom'] <= 1350
        assert box['x'] >= 24 and box['y'] >= 24
    print('  all six lockups exact, unmodified and above minimum size')

    print('== logo contrast ==')
    # The approved "dark" variant carries a paper wordmark and belongs on dark
    # grounds; the "light" variant carries an ink wordmark and belongs on light
    # grounds. The true ground is the lockup's own opaque chip when present,
    # otherwise the rendered background beneath the lockup box.
    import re
    for i in IDS:
        lock_id = audit[i]['logo']['lockupId']
        b = audit[i]['logo']['box']
        chip = audit[i]['logo'].get('chipColor', 'rgba(0, 0, 0, 0)')
        nums = [float(x) for x in re.findall(r'[\d.]+', chip)]
        alpha = nums[3] if len(nums) > 3 else 1.0
        if alpha >= 0.85 and len(nums) >= 3:
            lum = 0.2126 * nums[0] + 0.7152 * nums[1] + 0.0722 * nums[2]
            ground = 'chip'
        else:
            bg = Image.open(HERE / 'originals' / f'{i}.png').convert('RGB')
            region = bg.crop((int(b['x']), int(b['y']), int(b['right']), int(b['bottom'])))
            lum = ImageStat.Stat(region.convert('L')).mean[0]
            ground = 'background'
        is_dark_ground = lum < 128
        uses_dark_variant = lock_id.endswith('/dark')
        assert is_dark_ground == uses_dark_variant, (
            i, f'contrast mismatch: lockup {lock_id} on ground luminance {lum:.1f} ({ground})')
        print(f'  {i}: {lock_id} on {ground} luminance {lum:.0f} -> PASS')

    print('== copy contrast on coloured cards ==')
    # Body copy that inherits --ink onto a deep city panel renders at roughly
    # 1.6:1, which is unreadable even though no collision test objects. Sample
    # each copy block's own pixels: the most common tone is its ground, and the
    # extreme tone deviating most from that ground is its glyph. Direction comes
    # from the deviation rather than brightness, because the failing case is
    # precisely dark ink on a dark panel.
    from collections import Counter

    def _lum(rgb):
        def ch(v):
            v /= 255.0
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * ch(rgb[0]) + 0.7152 * ch(rgb[1]) + 0.0722 * ch(rgb[2])

    def _contrast(a, b):
        hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
        return (hi + 0.05) / (lo + 0.05)

    gated = 0
    for i in IDS:
        im = Image.open(HERE / 'final' / f'{i}.png').convert('RGB')
        for item in audit[i]['copy']:
            b = item['box']
            crop = im.crop((int(b['x']), int(b['y']), int(b['right']), int(b['bottom'])))
            if crop.width < 4 or crop.height < 4:
                continue
            pixels = list(crop.getdata())
            counts = Counter(pixels)
            ground, ground_share = counts.most_common(1)[0]
            # A photographic ground has no dominant tone; gate flat panels only.
            if ground_share < 0.45:
                continue
            tones = sorted(pixels, key=_lum)
            dark, light = tones[0], tones[-1]
            cand = (dark if abs(_lum(dark) - _lum(ground)) >= abs(_lum(light) - _lum(ground))
                    else light)
            # Ignore stray antialiased pixels: a glyph has real mass.
            if counts[cand] / len(pixels) < 0.02:
                continue
            ratio = _contrast(cand, ground)
            assert ratio >= 4.5, (
                i, f'copy #{item["index"]} {item["role"]} contrast {ratio:.2f}:1 '
                   f'ink {cand} on ground {ground}')
            gated += 1
    print(f'  {gated} copy blocks on flat panels meet WCAG AA 4.5:1')

    print('== dimensions and profile ==')
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    for i in IDS:
        p = HERE / 'final' / f'{i}.png'
        im = Image.open(p)
        assert im.size == (1080, 1350), (i, im.size)
        im = im.convert('RGB')
        im.save(p, optimize=True, icc_profile=srgb)
        im = Image.open(p)
        assert im.size == (1080, 1350) and im.info.get('icc_profile'), i
    print('  six PNGs: 1080x1350 RGB sRGB with embedded profile')

    print('== mobile previews ==')
    (HERE / 'mobile').mkdir(exist_ok=True)
    font = ImageFont.truetype(str(HERE / 'assets/Jost-VF.ttf'), 16)
    finals = []
    for i in IDS:
        im = Image.open(HERE / 'final' / f'{i}.png').convert('RGB')
        im.resize((375, 469), Image.Resampling.LANCZOS).save(
            HERE / 'mobile' / f'{i}-375x469.png', optimize=True)
        finals.append((i, im))
    print('  six 375x469 previews exported')

    print('== review artefacts ==')
    sheet = Image.new('RGB', (1080, 1010), '#101318')
    d = ImageDraw.Draw(sheet)
    for n, (i, im) in enumerate(finals):
        x = (n % 3) * 360
        y = (n // 3) * 505
        sheet.paste(im.resize((360, 450), Image.Resampling.LANCZOS), (x, y))
        d.text((x + 14, y + 462), i, font=font, fill='#F7F3E9')
    sheet.save(HERE / 'contact-sheet.png', optimize=True)
    print('  contact-sheet.png')

    # V1 -> V2 before/after comparison strip.
    old_dir = HERE.parent
    pair = Image.new('RGB', (6 * 300, 420), '#101318')
    d = ImageDraw.Draw(pair)
    for n, (i, im) in enumerate(finals):
        legacy = old_dir / 'final' / '01-hook.png'
        old = Image.open(legacy).convert('RGB').resize((147, 184), Image.Resampling.LANCZOS)
        pair.paste(old, (n * 300, 0))
        pair.paste(im.resize((147, 184), Image.Resampling.LANCZOS), (n * 300 + 153, 0))
        d.text((n * 300 + 4, 198), 'V1 01', font=font, fill='#9BA0A8')
        d.text((n * 300 + 157, 198), 'V2 ' + i[3:5], font=font, fill='#D8F457')
        d.text((n * 300 + 4, 240), i, font=font, fill='#F7F3E9')
    pair.save(HERE / 'v1-vs-v2-contact-sheet.jpg', quality=92, optimize=True)
    print('  v1-vs-v2-contact-sheet.jpg')

    mobile_strip = Image.new('RGB', (6 * 215 + 70, 370), '#101318')
    d = ImageDraw.Draw(mobile_strip)
    for n, (i, im) in enumerate(finals):
        x = 35 + n * 215
        mobile_strip.paste(im.resize((205, 256), Image.Resampling.LANCZOS), (x, 42))
        d.text((x, 312), f'{n+1:02d}', font=font, fill='#F7F3E9')
    mobile_strip.save(HERE / 'mobile-carousel-preview.png', optimize=True)
    print('  mobile-carousel-preview.png')

    cover = finals[0][1]
    crop = ImageOps.fit(cover, (810, 810), centering=(.5, .45))
    feed = Image.new('RGB', (1080, 1080), '#EEEAE1')
    feed.paste(crop, (135, 135))
    d = ImageDraw.Draw(feed)
    d.rounded_rectangle((54, 52, 1026, 1028), radius=34, outline='#D2CBBB', width=4)
    d.ellipse((86, 78, 135, 127), fill='#BD2120')
    d.text((151, 87), 'asyadaegitim',
           font=ImageFont.truetype(str(HERE / 'assets/Jost-VF.ttf'), 23), fill='#1D2027')
    d.text((845, 87), '...', font=font, fill='#1D2027')
    feed.save(HERE / 'instagram-feed-cover-preview.png', optimize=True)
    print('  instagram-feed-cover-preview.png')

    # Clean photographic background vs final measured typography.
    svf = Image.new('RGB', (6 * 300, 410), '#101318')
    d = ImageDraw.Draw(svf)
    for n, (i, im) in enumerate(finals):
        bg = Image.open(HERE / 'originals' / f'{i}.png').convert('RGB')
        svf.paste(bg.resize((147, 184), Image.Resampling.LANCZOS), (n * 300, 0))
        svf.paste(im.resize((147, 184), Image.Resampling.LANCZOS), (n * 300 + 153, 0))
        d.text((n * 300 + 4, 198), 'BACKGROUND', font=font, fill='#9BA0A8')
        d.text((n * 300 + 157, 198), 'FINAL', font=font, fill='#D8F457')
        d.text((n * 300 + 4, 238), i, font=font, fill='#F7F3E9')
    svf.save(HERE / 'source-vs-final-contact-sheet.jpg', quality=92, optimize=True)
    print('  source-vs-final-contact-sheet.jpg')

    print('== manifest ==')
    photos = json.loads((HERE / 'photography-sources.json').read_text())['records']
    slides = []
    render_validation = {}
    for i in IDS:
        rec = LOCKUPS[audit[i]['logo']['lockupId']]
        # Read placement straight from the composited SVG attributes so the
        # manifest cannot drift from the artwork it describes.
        svg_root = ET.parse(HERE / 'source' / f'{i}.svg').getroot()
        mark = next(e for e in svg_root.iter(NS + 'image')
                    if e.attrib.get('id') == 'canonical-lockup')
        lx, ly = float(mark.attrib['x']), float(mark.attrib['y'])
        lw, lh = float(mark.attrib['width']), float(mark.attrib['height'])
        render_validation[i] = {
            'jostLoaded': audit[i]['jostLoaded'],
            'issues': audit[i]['geometryIssues'],
            'canvas': [1080, 1350],
            'text_blocks': len(audit[i]['copy']),
            'logo_lockup_id': audit[i]['logo']['lockupId'],
        }
        slides.append({
            'id': i,
            'final_file': f'final/{i}.png',
            'final_sha256': sha(HERE / 'final' / f'{i}.png'),
            'original_file': f'originals/{i}.png',
            'original_sha256': sha(HERE / 'originals' / f'{i}.png'),
            'source_file': f'source/{i}.svg',
            'source_sha256': sha(HERE / 'source' / f'{i}.svg'),
            'editable_html_file': f'source/{i}.html',
            'dimensions': [1080, 1350],
            'copy': exact[i],
            'canonical_lockup_id': audit[i]['logo']['lockupId'],
            'canonical_lockup_sha256': rec[1],
            'canonical_logo_sha256': SEAL,
            'canonical_seal_sha256': SEAL,
            'canonical_lockup_file': f'assets/lockups/{rec[0]}',
            'logo_width_px': lw,
            'logo_height_px': lh,
            'logo_x_y_px': [lx, ly],
            'minimum_supported_display_width_px': rec[2],
            'render_validation': render_validation[i],
        })
    (HERE / 'render-validation.json').write_text(
        json.dumps(render_validation, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {
        'title': "Asya'da Eğitim — Rotanı Seç #001 / V2 — Tokyo mu, Seul mü?",
        'campaign': 'Rotanı Seç / 001',
        'revision': 'v2',
        'status': 'HUMAN CAMPAIGN REVIEW PENDING — NOT SOCIAL-PUBLISHED',
        'dimensions': [1080, 1350],
        'colour_space': 'sRGB',
        'production_method': (
            'Licensed documentary photography plus a deterministic measured HTML/CSS/SVG '
            'layout. Text geometry is measured in the browser, composited as editable SVG '
            'runs, and validated by an automated geometry and contrast audit.'),
        'previous_revision': '../',
        'exact_copy': exact,
        'geometric_audit': 'geometry-audit.json',
        'font': {'family': 'Jost', 'file': 'assets/Jost-VF.ttf',
                 'sha256': sha(HERE / 'assets/Jost-VF.ttf')},
        'palette_anchors': {'red': '#BD2120', 'ink': '#1D2027', 'paper': '#F7F3E9'},
        'photography_sources': 'photography-sources.json',
        'photography_attributions': 'photography-attributions.md',
        'image_model_calls': {
            'generation_count': 2,
            'disclosure': ('Two illustrative housing interiors for slide 05 were AI-generated; '
                           'they are labelled as illustrative and not documentary photography. '
                           'All campus, city and location photography is licensed.')},
        'slides': slides,
        'mobile_preview_files': [f'mobile/{i}-375x469.png' for i in IDS],
        'contact_sheet_file': 'contact-sheet.png',
        'source_vs_final_contact_sheet_file': 'source-vs-final-contact-sheet.jpg',
        'revision_comparison_file': 'v1-vs-v2-contact-sheet.jpg',
        'mobile_carousel_preview_file': 'mobile-carousel-preview.png',
        'feed_cover_preview_file': 'instagram-feed-cover-preview.png',
        'package_file': 'package/rotani-sec-tokyo-seoul-001-v2.zip',
    }
    (HERE / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('  manifest.json written')

    print('== package ==')
    import subprocess as sp
    include = [HERE / 'manifest.json', HERE / 'exact-copy.json', HERE / 'build.py',
               HERE / 'extract-backgrounds.mjs', HERE / 'render.mjs',
               HERE / 'verify_and_package.py', HERE / 'geometry-audit.json',
               HERE / 'render-validation.json', HERE / 'text-layout.json',
               HERE / 'generation-notes.md', HERE / 'photography-sources.json',
               HERE / 'photography-attributions.md', HERE / 'quality-review.md',
               HERE / 'visual-qa.md', HERE / 'caption.md',
               HERE / 'platform-adaptation-notes.md']
    for folder in ('final', 'originals', 'source', 'templates', 'mobile', 'assets'):
        include.extend(p for p in (HERE / folder).rglob('*') if p.is_file())
    include += [HERE / 'contact-sheet.png', HERE / 'source-vs-final-contact-sheet.jpg', HERE / 'v1-vs-v2-contact-sheet.jpg',
                HERE / 'mobile-carousel-preview.png',
                HERE / 'instagram-feed-cover-preview.png']
    z = HERE / manifest['package_file']
    z.parent.mkdir(exist_ok=True)
    z.unlink(missing_ok=True)
    with zipfile.ZipFile(z, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=8) as f:
        for p in include:
            f.write(p, p.relative_to(HERE).as_posix())
        for i in IDS:
            f.write(HERE / 'final' / f'{i}.png', f'{i}.png')
    print(f'  {z.relative_to(HERE).as_posix()} ({z.stat().st_size} bytes)')

    print()
    print('ALL V2 CHECKS PASS')


if __name__ == '__main__':
    main()
