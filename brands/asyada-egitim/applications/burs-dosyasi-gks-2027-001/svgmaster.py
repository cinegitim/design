#!/usr/bin/env python3
"""
Generate SVG slide masters (1080x1350) for Burs Dosyası / 001 from the measured
CSS-render geometry in qa/geometry-report.json, and rebuild source/NN.html as a
thin wrapper that inlines the SVG (the audit contract requires the editable HTML
to embed the same SVG) plus the QA harness.

Photos are pre-cropped with object-fit:cover semantics so every <image> places
undistorted. Canonical lockups are linked, never redrawn.
"""
import json, re
from pathlib import Path
from PIL import Image

APP  = Path(__file__).resolve().parent
QA   = json.loads((APP/'qa/geometry-report.json').read_text())
COPY = json.loads((APP/'copy-manifest.json').read_text())['slides']
CROP = APP/'assets/photos-crop'; CROP.mkdir(exist_ok=True)
FONT = (APP/'assets/Jost-VF.ttf').as_posix()

def esc(t):
    return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def rects(slide, qid):
    for r in QA['slides'][slide]['rects']:
        if r['id'] == qid: return r
    raise KeyError(f'{slide}:{qid}')

def asc(slide, size_px):
    m = QA['slides'][slide]['metrics'].get(f'{size_px}px')
    if m: return m['asc']
    # fall back to nearest measured size, scaled
    keys = sorted(int(k[:-2]) for k in QA['slides'][slide]['metrics'])
    near = min(keys, key=lambda k: abs(k-size_px))
    ratio = size_px/near
    return QA['slides'][slide]['metrics'][f'{near}px']['asc']*ratio

def crop(photo, box_w, box_h, posx=0.5, posy=0.5, out=None):
    """object-fit:cover crop with object-position semantics."""
    im = Image.open(APP/'assets/photos'/photo).convert('RGB')
    pw, ph = im.size
    target = box_w/box_h
    if pw/ph > target:
        h = ph; w = h*target
    else:
        w = pw; h = w/target
    x = (pw-w)*posx; y = (ph-h)*posy
    box = (round(x), round(y), round(x+w), round(y+h))
    im = im.crop(box)
    if out:
        im.save(CROP/out, quality=88, optimize=True)
    return im.size

# ---------------------------------------------------------------- text helpers
def text_el(slide, qid, size, weight, fill, ls=None, line_fill=None, lh=None, extra=''):
    """One <text> element per measured line; returns list of (copy_text, svg)."""
    r = rects(slide, qid)
    out = []
    for i, ln in enumerate(r['lines']):
        a = asc(slide, size)
        y = round(ln['y'] + a, 2)
        f = line_fill[i] if line_fill and i < len(line_fill) else fill
        lsattr = f' letter-spacing="{ls}"' if ls else ''
        weightattr = f' font-weight="{weight}"' if weight != 400 else ''
        out.append((ln['text'],
            f'<text x="{ln["x"]}" y="{y}" font-size="{size}"{weightattr} fill="{f}"{lsattr}{extra}>{esc(ln["text"])}</text>'))
    return out

class Slide:
    def __init__(self, num, bg):
        self.num, self.bg = num, bg
        self.body = []          # decorative + visual ops (outside copy group)
        self.copy_groups = []   # (copy_string, [svg_text_elements])
    def add(self, svg): self.body.append(svg); return self
    def copy_group(self, text, elements):
        self.copy_groups.append((text, elements))
    def render(self):
        parts = [f'<rect x="0" y="0" width="1080" height="1350" fill="{self.bg}"/>']
        parts += self.body
        exact = json.dumps([c for c,_ in self.copy_groups], ensure_ascii=False)
        group = [f'<g id="editable-campaign-copy" data-exact-copy-json=\'{exact}\'>']
        for text, els in self.copy_groups:
            group.append(f'<g data-copy="{esc(text)}">' + ''.join(els) + '</g>')
        group.append('</g>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" '
               f'viewBox="0 0 1080 1350" font-family="Jost">'
               f'<style>@font-face{{font-family:Jost;src:url({FONT}) format(\'truetype\');font-weight:100 900}}</style>'
               + ''.join(parts) + ''.join(group) + '</svg>')
        # self-check: visible copy text equals the locked copy for this slide
        visible = ' '.join(t for t,_ in self.copy_groups)
        want = ' '.join(COPY[self.num])
        if ' '.join(visible.split()) != ' '.join(want.split()):
            raise SystemExit(f'slide {self.num} copy mismatch:\n{visible}\n---\n{want}')
        return svg

ICONS = {
 'calendar': '<rect x="7" y="11" width="34" height="30" rx="3"/><path d="M7 20h34M16 7v8M32 7v8"/><path d="M17 30h6"/>',
 'cap':      '<path d="M4 19 24 9l20 10-20 10z"/><path d="M12 23.5V33c0 3.4 5.4 6 12 6s12-2.6 12-6V23.5"/><path d="M44 19v10"/>',
 'medal':    '<circle cx="24" cy="31" r="12"/><path d="M17 19l-4-11 10 5zM31 19l4-11-10 5z"/>',
 'bubble':   '<path d="M6 8h30a4 4 0 0 1 4 4v14a4 4 0 0 1-4 4H16l-10 8z"/><path d="M15 17h12M15 24h8"/>',
 'plane':    '<path d="M43 4 6 20l11 4 4 11z"/><path d="M43 4 17 28"/>',
}
def icon(name, x, y, size, stroke):
    return (f'<g transform="translate({x},{y}) scale({size/48})" fill="none" stroke="{stroke}" '
            f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

VG = lambda stops: ('<linearGradient id="g{0}" x1="0" y1="0" x2="0" y2="1">'
    + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>')

def lockup(file, x, y, w, vb_w, vb_h, qa_slide=None, qa_id='logo'):
    h = round(w*vb_h/vb_w, 4)
    if qa_slide:
        r = rects(qa_slide, qa_id)
        x, y = r['x'], r['y']
    return (f'<image id="canonical-lockup" href="../assets/lockups/{file}" x="{x}" y="{y}" '
            f'width="{w}" height="{h}"/>'), h

LOCKUPS = {  # file -> (viewBox w, h, min display width)
 'p-01-primary-stacked-dark.svg':  (1021.0, 1003.79998779, 352),
 'p-01-primary-stacked-light.svg': (1021.0, 1003.79998779, 352),
 'h-02-primary-horizontal-light.svg': (1566.54054071, 587.56787109, 528),
 'd-04-small-use-digital-light.svg': (1314.83783798, 503.35108119, 200),
}

# ---------------------------------------------------------------- slide 01
s = Slide('01', '#101318')
crop('campus-hero-ewha.jpg', 1080, 1350, 0.5, 0.62, '01-hero.jpg')
s.add(f'<image href="../assets/photos-crop/01-hero.jpg" x="0" y="0" width="1080" height="1350" preserveAspectRatio="none"/>')
s.add(f'<defs>{VG([(0,'rgba(13,15,20,.86)'),(.3,'rgba(13,15,20,.52)'),(.58,'rgba(13,15,20,.58)'),(1,'rgba(13,15,20,.93)')]).format("v1")}</defs>')
s.add('<rect x="0" y="0" width="1080" height="1350" fill="url(#gv1)"/>')
# deco date + strike
d_top = 636; d_size = 212
s.add(f'<text x="540" y="{round(d_top+asc("01",d_size),2)}" font-size="{d_size}" font-weight="650" '
      f'letter-spacing="4.24" fill="rgba(247,243,233,.13)" text-anchor="middle">30 EYLÜL</text>')
s.add('<rect x="88" y="744" width="904" height="12" rx="6" fill="#BD2120" opacity=".85" transform="rotate(-1.6 540 750)"/>')
sid = rects('01','sid')
s.add(f'<rect x="72" y="{round(sid["y"]+sid["h"]+16,2)}" width="96" height="5" fill="#BD2120"/>')
s.copy_group('BURS DOSYASI / 001', [e for _,e in text_el('01','sid',30,600,'#F7F3E9',4.2)])
s.copy_group('Kore devlet bursunu kaçırdın mı?',
             [e for _,e in text_el('01','question',78,600,'#F7F3E9',-1.56,
                                   line_fill=['#F7F3E9','#BD2120'])])
s.copy_group('30 Eylül’de büyükelçilik başvuruları kapandı.',
             [e for _,e in text_el('01','embassy-closed',35,500,'rgba(247,243,233,.92)')])
p2 = rects('01','university-track')
s.add(f'<rect x="72" y="{p2["y"]}" width="10" height="{round(p2["h"],2)}" fill="#BD2120"/>')
s.copy_group('Ama üniversite yolunda Ekim son tarihleri var.',
             [e for _,e in text_el('01','university-track',47,600,'#F7F3E9',-0.47)])
s.copy_group('GKS-UIC 2027', [e for _,e in text_el('01','gks-uic',44,650,'#F7F3E9',0.88)])
s.copy_group('Türkiye’den başvuru mümkün.',
             [e for _,e in text_el('01','tr-apply',30,500,'rgba(247,243,233,.85)')])
lg,_ = lockup('p-01-primary-stacked-dark.svg', 628, None, 380, *LOCKUPS['p-01-primary-stacked-dark.svg'][:2], '01')
s.add(lg)
SVG01 = s.render()

# ---------------------------------------------------------------- slide 02
s = Slide('02', '#F7F3E9')
rail_top, rail_bot = 237, 929
s.add(f'<line x1="77.5" y1="{rail_top}" x2="77.5" y2="{rail_bot}" stroke="rgba(29,32,39,.22)" stroke-width="3"/>')
s.add('<circle cx="77.5" cy="237" r="13" fill="#BD2120"/><circle cx="77.5" cy="707" r="10" fill="#1D2027"/>'
      '<circle cx="77.5" cy="929" r="10" fill="#1D2027"/>')
e1 = rects('02','entry-koreatech')
photo = {'x': e1['x']+e1['w']-400, 'y': e1['y']+18}
crop('koreatech-hum.jpg', 400, 400, 0.5, 0.38, '02-koreatech.jpg')
s.add(f'<image href="../assets/photos-crop/02-koreatech.jpg" x="{photo["x"]}" y="{photo["y"]}" width="400" height="400" preserveAspectRatio="none"/>')
s.add(f'<rect x="{photo["x"]}" y="{photo["y"]}" width="400" height="8" fill="#BD2120"/>')
s.copy_group('GKS-UIC’de üç üniversitenin başvurusu sürüyor.',
             [e for _,e in text_el('02','head',54,600,'#1D2027',-0.81)])
s.copy_group('23 EKİM 2026', [e for _,e in text_el('02','date-1',58,650,'#BD2120',-0.58)])
s.copy_group('KOREATECH', [e for _,e in text_el('02','name-1',46,650,'#1D2027')])
s.copy_group('Bilgisayar / Makine Mühendisliği',
             [e for _,e in text_el('02','prog-1',30,500,'rgba(29,32,39,.88)')])
for row, photo_name, cropname, dq, nq, pq in (
    ('entry-ajou','ajou-campus.jpg','02-ajou.jpg','date-2','name-2','prog-2'),
    ('entry-kookmin','kookmain-10.jpg','02-kookmin.jpg','date-3','name-3','prog-3')):
    r = rects('02', row)
    crop(photo_name, 250, 170, 0.5, 0.5, cropname)
    py = round(r['y'] + (r['h']-170)/2, 2)
    s.add(f'<rect x="106" y="{r["y"]}" width="902" height="2" fill="rgba(29,32,39,.16)"/>')
    s.add(f'<image href="../assets/photos-crop/{cropname}" x="106" y="{py}" width="250" height="170" preserveAspectRatio="none"/>')
    s.copy_group({'date-2':'30 EKİM 2026','date-3':'30 EKİM 2026'}[dq],
                 [e for _,e in text_el('02',dq,44,650,'#1D2027',-0.44)])
    s.copy_group({'name-2':'Ajou University','name-3':'Kookmin University'}[nq],
                 [e for _,e in text_el('02',nq,37,600,'#1D2027')])
    s.copy_group({'prog-2':'Yapay Zekâ ve Bilgisayar Mühendisliği','prog-3':'Yazılım'}[pq],
                 [e for _,e in text_el('02',pq,28,500,'rgba(29,32,39,.85)')])
foot = rects('02','footer')
s.add(f'<rect x="106" y="{foot["y"]+26}" width="902" height="3" fill="#1D2027"/>')
s.copy_group('Son tarihler Kore saatine göredir. Belge teslim yöntemleri üniversiteye göre değişir.',
             [e for _,e in text_el('02','note-1',24,500,'rgba(29,32,39,.9)')])
s.copy_group('13 Ekim 2026 itibarıyla.', [e for _,e in text_el('02','note-2',24,650,'#BD2120')])
lg,_ = lockup('d-04-small-use-digital-light.svg', 0, None, 240, *LOCKUPS['d-04-small-use-digital-light.svg'][:2], '02')
s.add(lg)
SVG02 = s.render()

# ---------------------------------------------------------------- slide 03
s = Slide('03', '#ECE5D3')
crop('koreatech-eng4.jpg', 462, 520, 0.5, 0.42, '03-eng.jpg')
s.add('<image href="../assets/photos-crop/03-eng.jpg" x="546" y="318" width="462" height="520" preserveAspectRatio="none"/>')
s.add(f'<defs>{VG([(0,'rgba(29,32,39,.05)'),(1,'rgba(29,32,39,.42)')]).format("v3")}</defs>')
s.add('<rect x="546" y="318" width="462" height="520" fill="url(#gv3)"/>')
big_top, big_size, big_lh = 300, 300, 270
s.add(f'<text x="58" y="{round(big_top+(big_lh-(asc("03",big_size)+80))/2+asc("03",big_size),2)}" '
      f'font-size="{big_size}" font-weight="650" letter-spacing="-9" fill="#BD2120">100</text>')
sub_top = big_top+big_lh+6
s.add(f'<text x="58" y="{round(sub_top+asc("03",30),2)}" font-size="30" font-weight="650" letter-spacing="0.6" '
      f'fill="#1D2027">DÜNYA GENELİNDEN BAŞVURU</text>')
s.copy_group('100 burs kontenjanı. Dünya genelinden başvuru.',
             [e for _,e in text_el('03','headline',48,600,'#1D2027',-0.72)])
s.copy_group('13 kurum · Lisans ve ön lisans',
             [e for _,e in text_el('03','institutions',31,650,'#BD2120',0.31)])
for fig, lab, att, cfig, catt in (
    ('fig-ajou','lab-ajou','att-ajou','7 KONTENJAN','Ajou — Yapay Zekâ ve Bilgisayar Mühendisliği'),
    ('fig-kookmin','lab-kookmin','att-kookmin','7 KONTENJAN','Kookmin — Yazılım'),
    ('fig-koreatech','lab-koreatech','att-koreatech','5 + 5 KONTENJAN','KOREATECH — Bilgisayar ve Makine Mühendisliği')):
    els  = [e for _,e in text_el('03',fig,86,650,'#BD2120',-1.72)]
    els += [e for _,e in text_el('03',lab,26,650,'#1D2027',2.08)]
    s.copy_group(cfig, els)
    s.copy_group(catt, [e for _,e in text_el('03',att,25,500,'rgba(29,32,39,.9)')])
s.add('<rect x="0" y="1210" width="1080" height="140" fill="#1D2027"/>')
s.copy_group('Kontenjanlar uluslararası adaylara açık. Türkiye’ye özel kota değil.',
             [e for _,e in text_el('03','strip-t',30,550,'#F7F3E9')])
lg,_ = lockup('p-01-primary-stacked-light.svg', 656, None, 352, *LOCKUPS['p-01-primary-stacked-light.svg'][:2], '03')
s.add(lg)
SVG03 = s.render()

# ---------------------------------------------------------------- slide 04
s = Slide('04', '#F2ECDF')
lg,lgh = lockup('h-02-primary-horizontal-light.svg', 72, None, 560, *LOCKUPS['h-02-primary-horizontal-light.svg'][:2], '04')
s.add(lg)
s.add('<rect x="72" y="440" width="936" height="104" fill="#BD2120"/>')
crop('kyunghee-library.jpg', 936, 142, 0.5, 0.46, '04-library.jpg')
s.add('<image href="../assets/photos-crop/04-library.jpg" x="72" y="564" width="936" height="142" preserveAspectRatio="none"/>')
s.copy_group('Türkiye’den kimler GKS-UIC’ye başvurabilir?',
             [e for _,e in text_el('04','question',52,600,'#1D2027',-0.78)])
s.copy_group('TÜRK VATANDAŞLARI', [e for _,e in text_el('04','answer-a',38,650,'#F7F3E9',2.28)])
s.copy_group('Başvurabilir.', [e for _,e in text_el('04','answer-b',46,700,'#F7F3E9')])
for grp, num, gh, gb, ico, cgh, cgb in (
    ('grp-yas','01','gh-1','gb-1','calendar','YAŞ','1 Mart 2002’den sonra doğmuş olmak.'),
    ('grp-mezuniyet','02','gh-2','gb-2','cap','MEZUNİYET','Lise veya ön lisans mezunu olmak ya da en geç 31 Aralık 2026’da mezun olmak.'),
    ('grp-akademik','03','gh-3','gb-3','medal','AKADEMİK BAŞARI','80/100 veya sınıfın ilk %20’si veya kabul edilen eşdeğer not ortalaması.')):
    g = rects('04', grp)
    s.add(f'<rect x="72" y="{g["y"]}" width="936" height="2" fill="rgba(29,32,39,.16)"/>')
    nr = rects('04', {'01':'num-1','02':'num-2','03':'num-3'}[num])
    nbase = nr['y'] + asc('04', 58)
    s.add(f'<text x="72" y="{round(nbase,2)}" font-size="58" font-weight="650" fill="#BD2120">{num}</text>')
    hr = rects('04', gh)
    s.add(icon(ico, round(hr['x']-58,2), round(hr['y']+(hr['h']-42)/2,2), 42, '#1D2027'))
    s.copy_group(cgh, [e for _,e in text_el('04',gh,33,650,'#1D2027',0.66)])
    s.copy_group(cgb, [e for _,e in text_el('04',gb,26,500,'rgba(29,32,39,.92)')])
last = rects('04','grp-akademik')
s.add(f'<rect x="72" y="{round(last["y"]+last["h"],2)}" width="936" height="2" fill="rgba(29,32,39,.16)"/>')
s.add('<rect x="0" y="1181" width="1080" height="130" fill="#1D2027"/>')
s.copy_group('Adayın ve ebeveynlerinin Kore vatandaşlığı olmamalı. Lisans diploması sahipleri uygun değil. Bölüme özel şartlar ayrıca geçerli.',
             [e for _,e in text_el('04','disc-p',26,500,'#F7F3E9')])
SVG04 = s.render()

# ---------------------------------------------------------------- slide 05
s = Slide('05', '#1D2027')
lg,_ = lockup('p-01-primary-stacked-dark.svg', 656, None, 352, *LOCKUPS['p-01-primary-stacked-dark.svg'][:2], '05')
s.add(lg)
s.copy_group('GKS 2027 bursu ne kadar?', [e for _,e in text_el('05','question',58,600,'#F7F3E9',-0.87)])
krw = []
krw += [e for _,e in text_el('05','krw-amount',122,650,'#F7F3E9',-3.05)]
krw += [e for _,e in text_el('05','krw-cur',54,600,'#BD2120')]
krw += [e for _,e in text_el('05','krw-yr',38,500,'rgba(247,243,233,.66)')]
s.copy_group('14.400.000 KRW* / yıl', krw)
s.copy_group('≈ 9.675 € / yıl', [e for _,e in text_el('05','eur',54,500,'rgba(247,243,233,.74)',-0.54)])
s.copy_group('Lisans eğitimi döneminde verilen yaşam desteği.',
             [e for _,e in text_el('05','life',32,550,'#F7F3E9')])
s.copy_group('Ayrıca karşılananlar:', [e for _,e in text_el('05','also',30,650,'#F7F3E9',0.6)])
for iq, it, ico, cpy in (('item-1','item-1-t','cap','Öğrenim ücreti'),
                          ('item-2','item-2-t','bubble','Korece hazırlık eğitimi (gerektiğinde)'),
                          ('item-3','item-3-t','plane','Uygun adaylar için ekonomi sınıfı uçak bileti')):
    r = rects('05', iq)
    s.add(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="3" fill="rgba(247,243,233,.34)"/>')
    s.add(icon(ico, r['x'], round(r['y']+21,2), 54, '#F7F3E9'))
    s.copy_group(cpy, [e for _,e in text_el('05',it,28,500,'#F7F3E9')])
na = rects('05','note-a')
s.add(f'<rect x="{na["x"]}" y="{na["y"]}" width="{na["w"]}" height="{round(na["h"],2)}" fill="none" stroke="rgba(247,243,233,.4)" stroke-width="2"/>')
s.copy_group('Yaşam desteğine barınma, sağlık sigortası ve ilgili ödenekler dahildir.',
             [e for _,e in text_el('05','note-a',27,550,'#F7F3E9')])
s.add('<rect x="72" y="1230" width="936" height="2" fill="rgba(247,243,233,.28)"/>')
s.copy_group('Avro karşılığı 12 Ekim 2026 kuru üzerinden yaklaşık hesaplanmıştır.',
             [e for _,e in text_el('05','note-b',24,400,'rgba(247,243,233,.72)')])
SVG05 = s.render()

# ---------------------------------------------------------------- slide 06
s = Slide('06', '#101318')
crop('campus-skku.jpg', 1080, 1350, 0.5, 0.30, '06-campus.jpg')
s.add('<image href="../assets/photos-crop/06-campus.jpg" x="0" y="0" width="1080" height="1350" preserveAspectRatio="none"/>')
s.add(f'<defs>{VG([(0,'rgba(13,15,20,.9)'),(.34,'rgba(13,15,20,.62)'),(.62,'rgba(13,15,20,.7)'),(1,'rgba(13,15,20,.94)')]).format("v6")}</defs>')
s.add('<rect x="0" y="0" width="1080" height="1350" fill="url(#gv6)"/>')
sid = rects('06','sid')
s.add(f'<rect x="72" y="{round(sid["y"]+sid["h"]+16,2)}" width="96" height="5" fill="#BD2120"/>')
s.copy_group('BURS DOSYASI / 001', [e for _,e in text_el('06','sid',30,600,'#F7F3E9',4.2)])
s.copy_group('GKS-UIC’de ikinci üniversite tercihi yok.',
             [e for _,e in text_el('06','headline',64,650,'#F7F3E9',-1.28)])
path = rects('06','path')
s.add(f'<rect x="78" y="{path["y"]}" width="4" height="{round(path["h"],2)}" fill="#BD2120" opacity=".9"/>')
node = rects('06','node')
s.add(f'<circle cx="{round(node["x"]+node["w"]/2,2)}" cy="{round(node["y"]+node["h"]/2,2)}" r="11" fill="#BD2120"/>')
s.copy_group('1 ÜNİVERSİTE', [e for _,e in text_el('06','one-uni',92,650,'#F7F3E9',-0.92)])
s.copy_group('1 BÖLÜM', [e for _,e in text_el('06','one-dept',92,650,'#F7F3E9',-0.92)])
wr = rects('06','warning')
s.add(f'<rect x="72" y="{wr["y"]}" width="8" height="{round(wr["h"],2)}" fill="#BD2120"/>')
s.copy_group('Birden fazla üniversiteye başvurmak GKS değerlendirmesinden çıkarılmana neden olabilir.',
             [e for _,e in text_el('06','warning',31,500,'rgba(247,243,233,.94)')])
s.copy_group('Türkiye’den başvurabileceğin programları, gerekli belgeleri ve son tarihleri birlikte kontrol edelim.',
             [e for _,e in text_el('06','service',31,500,'rgba(247,243,233,.94)')])
cta = rects('06','cta')
s.add(f'<rect x="{cta["x"]}" y="{cta["y"]}" width="{round(cta["w"],2)}" height="{round(cta["h"],2)}" fill="#BD2120"/>')
s.copy_group('Ücretsiz ön görüşme', [e for _,e in text_el('06','cta',40,650,'#F7F3E9',0.4)])
lg,_ = lockup('p-01-primary-stacked-dark.svg', 628, None, 380, *LOCKUPS['p-01-primary-stacked-dark.svg'][:2], '06')
s.add(lg)
SVG06 = s.render()

SVGS = {'01':SVG01,'02':SVG02,'03':SVG03,'04':SVG04,'05':SVG05,'06':SVG06}

# ---------------------------------------------------------------- write sources
QA_JS = None
import importlib.util
spec = importlib.util.spec_from_file_location('b', APP/'build.py')
bm = importlib.util.module_from_spec(spec); sys_modules = __import__('sys').modules
bm.__dict__['__name__'] = 'buildmod'
spec.loader.exec_module(bm) if False else None
# QA_JS lives in build.py as a module-level constant; read it without executing build
build_src = (APP/'build.py').read_text()
m = re.search(r'QA_JS = r"""(.*?)"""', build_src, re.S)
QA_JS = m.group(1)

for num, svg in SVGS.items():
    (APP/'source'/f'{num}.svg').write_text(svg + '\n', encoding='utf-8')
    html = ('<!doctype html><html lang="tr"><head><meta charset="utf-8">'
            '<style>@font-face{font-family:Jost;src:url(../assets/Jost-VF.ttf) format(\'truetype\');font-weight:100 900}'
            'html,body{margin:0;width:1080px;height:1350px;overflow:hidden;background:#1D2027}svg{display:block}</style>'
            f'</head><body>{svg}<script>{QA_JS}</script></body></html>')
    (APP/'source'/f'{num}.html').write_text(html, encoding='utf-8')
    # audit contract: editable HTML must embed the SVG verbatim
    assert svg in html
print('SVG masters + wrapper HTML written for', ', '.join(sorted(SVGS)))
