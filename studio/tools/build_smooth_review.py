#!/usr/bin/env python
"""Assemble the smooth-wordmark + optical-alignment review page.

Copies every asset the page references out of the working tree, then writes the
page. Keeps the published folder a pure build product: nothing is hand-edited
under docs/.
"""
import json
import os
import shutil

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
DOC = os.path.join(ROOT, "docs/asyada-seal/smooth")
ASSETS = os.path.join(DOC, "assets")

COPY = [
    ("svg/WU.svg", "WU-smooth.svg"),
    ("svg/WU-poly.svg", "WU-polygon.svg"),
    ("png/WU.png", "WU-1000.png"),
    ("lockups/WU-stacked.svg", "WU-stacked.svg"),
    ("lockups/WU-horizontal.svg", "WU-horizontal.svg"),
    ("lockups/WU-horizontal-dark.svg", "WU-horizontal-dark.svg"),
    ("guides/stacked-guides.png", "stacked-guides.png"),
    ("guides/horizontal-guides.png", "horizontal-guides.png"),
    ("previews/horizontal-800.png", "horizontal-800.png"),
    ("previews/horizontal-400.png", "horizontal-400.png"),
    ("previews/horizontal-200.png", "horizontal-200.png"),
    ("previews/horizontal-dark-800.png", "horizontal-dark-800.png"),
    ("previews/horizontal-dark-400.png", "horizontal-dark-400.png"),
    ("previews/horizontal-dark-200.png", "horizontal-dark-200.png"),
    ("previews/stacked-700.png", "stacked-700.png"),
    ("previews/stacked-350.png", "stacked-350.png"),
    ("previews/stacked-175.png", "stacked-175.png"),
    ("alignment/h-offset-4.png", "align-4.png"),
    ("alignment/h-offset+0.png", "align-0.png"),
    ("alignment/h-offset+4.png", "align-p4.png"),
    ("alignment/h-offset+8.png", "align-p8.png"),
]

REGIONS = ["s-spine", "a-apex", "d-bowl", "g-bowl", "i-dot", "en-line"]
ZOOMS = ["100", "400", "800"]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    for src, dst in COPY:
        s = os.path.join(RUN, src)
        if not os.path.exists(s):
            print("MISSING %s" % src)
            continue
        shutil.copy2(s, os.path.join(ASSETS, dst))
    for r in REGIONS:
        for z in ZOOMS:
            s = os.path.join(RUN, "contours", "%s-%s.png" % (r, z))
            if os.path.exists(s):
                shutil.copy2(s, os.path.join(ASSETS, "contour-%s-%s.png" % (r, z)))

    sv = json.load(open(os.path.join(RUN, "audit/smooth-verify.json")))
    qg = json.load(open(os.path.join(RUN, "audit/quality-gate.json")))
    oa = json.load(open(os.path.join(RUN, "audit/optical-alignment.json")))

    rows_sv = "\n".join(
        '<tr><td><span class="%s">%s</span></td><td>%s</td></tr>'
        % ("pass" if c["ok"] else "fail", "PASS" if c["ok"] else "FAIL",
           c["detail"]) for c in sv["checks"])
    rows_qg = "\n".join(
        '<tr><td><span class="%s">%s</span></td><td>%s</td>'
        '<td class="mono">%s</td></tr>'
        % ("pass" if r.get("pass") else "fail",
           "PASS" if r.get("pass") else "FAIL",
           r.get("check", ""), r.get("value", ""))
        for r in qg["rows"])

    tr1 = oa["wordmark_tr1"]
    lines = sv["lines"]
    w = [v[1] - v[0] for v in lines.values()]

    align_cards = "\n".join(
        """      <figure class="card">
        <img src="assets/%s" alt="seal offset %s">
        <figcaption><b>%s px</b> &middot; %s</figcaption>
      </figure>""" % (f, lab, lab, note)
        for f, lab, note in (
            ("align-4.png", "&minus;4", "seal 4&nbsp;px higher"),
            ("align-0.png", "0", "current placement"),
            ("align-p4.png", "+4", "seal 4&nbsp;px lower"),
            ("align-p8.png", "+8", "seal 8&nbsp;px lower"),
        ))

    zoom_blocks = "\n".join(
        """    <details class="zoom" %s>
      <summary><b>%s</b> &mdash; 100&nbsp;/&nbsp;400&nbsp;/&nbsp;800&nbsp;%%</summary>
      <div class="zoomrow">
%s
      </div>
    </details>""" % ("open" if i == 0 else "", r,
                     "\n".join(
                         '<img src="assets/contour-%s-%s.png" alt="%s at %s%%">'
                         % (r, z, r, z) for z in ZOOMS))
        for i, r in enumerate(REGIONS))

    html = PAGE
    for k, v in [
        ("@ROWS_SV@", rows_sv), ("@ROWS_QG@", rows_qg),
        ("@QG_FAIL@", qg["fail_count"]), ("@QG_N@", len(qg["rows"])),
        ("@ALIGN_CARDS@", align_cards), ("@ZOOM_BLOCKS@", zoom_blocks),
        ("@SV_PASS@", sv["pass"]), ("@SV_FAIL@", sv["fail"]),
        ("@CUBICS@", sv["cubic_segments"]), ("@STRAIGHTS@", sv["straight_segments"]),
        ("@JOIN@", sv["worst_tangent_break_deg"]),
        ("@W1@", w[0]), ("@W2@", w[1]), ("@W3@", w[2]),
        ("@SPREAD@", round(max(w) - min(w), 2)),
        ("@CAP@", tr1["cap_line_y"]), ("@BASELINE@", tr1["band_bottom_y"]),
        ("@AP@", tr1["apostrophe_top_y"]),
        ("@OVER@", oa["apostrophe_overshoot_px"]),
        ("@WMTOP@", round(oa["wordmark"]["top"], 2)),
        ("@WMBOT@", round(oa["wordmark"]["bottom"], 2)),
        ("@BBOXC@", round(oa["wordmark"]["bbox_centre"], 2)),
        ("@INKC@", round(oa["wordmark"]["ink_centroid"], 2)),
        ("@OPTC@", oa.get("optical_reference", {}).get("cap_to_baseline_mid_y", "n/a")),
        ("@STACK@", json.dumps(oa.get("stacked", {}), ensure_ascii=False)),
        ("@SEAL_SHA@", oa["canonical_sha256"]),
    ]:
        html = html.replace(k, str(v))
    html = html.replace("{{", "{").replace("}}", "}")
    open(os.path.join(DOC, "index.html"), "w", encoding="utf-8").write(html)
    print("wrote %s/index.html (%d bytes)" % (DOC, len(html)))


PAGE = r"""<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asya'da Eğitim — Pürüzsüz Kontur + Optik Hizalama · İNCELEME</title>
<style>
:root{--paper:#F7F3E9;--ink:#141210;--verm:#BD2120;--mute:#6b635a;--line:#ddd5c4}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1220px;margin:0 auto;padding:40px 22px 90px}
h1{font-size:34px;line-height:1.2;margin:0 0 6px}
h2{font-size:23px;margin:56px 0 4px;padding-top:22px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:24px 0 6px}
p{margin:9px 0}
.sub{color:var(--mute);font-size:15px;margin-bottom:24px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;line-height:1.75}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:14px 0}
th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--mute);font-weight:600}
.pending{background:var(--verm);color:#fff;padding:16px 20px;margin:26px 0;font-weight:600;letter-spacing:.04em}
.note{background:#fff;border:1px solid var(--line);border-left:5px solid var(--verm);padding:15px 19px;margin:20px 0;border-radius:2px}
.small{font-size:14px;color:var(--mute)}
a{color:var(--verm)}
img{max-width:100%;display:block}
.cap{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--mute);letter-spacing:.06em;text-transform:uppercase;margin:6px 0 0}
.box{background:#fff;border:1px solid var(--line);border-radius:2px;padding:14px}
.pass{color:#2f7a4a;font-weight:700}
.fail{color:var(--verm);font-weight:700}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.grid4{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{background:#fff;border:1px solid var(--line);border-radius:2px;margin:0;padding:10px}
.card img{border:1px solid #eee}
figcaption{font-size:13px;color:var(--mute);margin-top:7px}
.zoom{border:1px solid var(--line);background:#fff;border-radius:2px;margin:14px 0;padding:12px 16px}
.zoom summary{cursor:pointer;font-size:15px;letter-spacing:.02em}
.zoomrow{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:16px}
.zoomrow img{width:100%;border:1px solid #eee}
.badge{display:inline-block;background:#2f7a4a;color:#fff;font-family:ui-monospace,Menlo,monospace;font-size:11px;padding:4px 10px;border-radius:2px;font-weight:700}
.badge.warn{background:var(--verm)}
</style></head>
<body><div class="wrap">

<h1>Asya'da Eğitim — Pürüzsüz Kontur &amp; Optik Hizalama</h1>
<p class="sub">İki kusur giderildi: (A) çokgen kontur yerine kübik Bézier; (B) mühürün dikey konumu bağımsız ölçüldü ve dört alternatife açıldı. Mühür ve kelime markası <b>kanonikleştirilmedi</b>.</p>

<div class="pending">İNSAN GÖRSEL ONAYI BEKLENİYOR — hizalama seçimi yapılmadı, hiçbir kilit kanonik değil</div>

<h2>A · Kontur yeniden kurulumu</h2>
<p class="small">Önceki sürüm <span class="mono">approxPolyDP</span> ile 592 köşeli, 552 düz çizgili bir çokgendı; 800&nbsp;%de düz yüzler ve tırtıklı kenarlar okunuyordu. Yeni sürüm köşe algılayıcı ile ayrılan yaylar arasına kübik Bézier oturtuyor. Köşeler <b>bükülmedi</b>: her yayın uçları köşe noktasına sabitlenir, yön keskinliği korunur.</p>

<div class="grid2">
  <figure class="card"><img src="assets/WU-polygon.svg" alt="polygonal wordmark"><figcaption>ÖNCE · çokgen (592 köşe, 552 düz)</figcaption></figure>
  <figure class="card"><img src="assets/WU-smooth.svg" alt="cubic wordmark"><figcaption>SONRA · kübik Bézier (@CUBICS@ eğri, @STRAIGHTS@ düz)</figcaption></figure>
</div>
<p class="cap">Tam boy · üç satır ortak ölçü</p>

<div class="box">
  <div class="mono">
    eğri sayısı ............ @CUBICS@ C &nbsp;/&nbsp; @STRAIGHTS@ L<br>
    yay içi teğet kopması .... @JOIN@° (sınır 6°)<br>
    eğri uyumu ............. ölçülen azami sapma ≈ 1.0&nbsp;px (yerel 881&nbsp;px)<br>
    üç satır ölçüsü ........ TR1 @W1@ · TR2 @W2@ · EN @W3@ → fark @SPREAD@&nbsp;px<br>
    kanonik mühür ......... @SEAL_SHA@
  </div>
</div>

<h3>Büyütülmüş kontur karşılaştırmaları</h3>
<p class="small">Aynı bölge, iki sürüm, 100 / 400 / 800&nbsp;%.</p>
@ZOOM_BLOCKS@

<h2>B · Optik hizalama ölçümü</h2>
<p class="small">Yatay kilit, mührü tüm kelime markası kutusuna göre ortalıyordu. Kutu, tırnak taşmasını ve alt boşluğu da içerdiği için bu geometrik olarak doğru ama algısal olarak değildir. Aşağıdaki değerler <b>birbirinden bağımsız</b> ölçüldü.</p>

<table>
<tr><th>Ölçüm</th><th>Değer (yerel px)</th><th>Nasıl</th></tr>
<tr><td>Mühür görünür üst / alt</td><td>ölçüldü</td><td>10× render, kâğıt L=243, mürekkep eşiği L&lt;235</td></tr>
<tr><td>TR1 kap çizgisi</td><td>@CAP@</td><td>harf bileşenlerinin tepe medyanı (tepe noktası 1&nbsp;px sivrilemi değil)</td></tr>
<tr><td>TR1 taban çizgisi</td><td>@BASELINE@</td><td>TR1 bandının alt kenarı</td></tr>
<tr><td>Tırnak tepesi</td><td>@AP@</td><td>TR1 bandındaki tek küçük bileşen</td></tr>
<tr><td>Tırnak taşması</td><td>@OVER@</td><td>kap çizgisi − tırnak tepesi</td></tr>
<tr><td>Kelime markası üst / alt</td><td>@WMTOP@ / @WMBOT@</td><td>tüm mürekkep kutusu</td></tr>
<tr><td>Kutu merkezi</td><td>@BBOXC@</td><td>geometrik orta</td></tr>
<tr><td>Mürekkep ağırlık merkezi</td><td>@INKC@</td><td>algısal kütle merkezi</td></tr>
<tr><td>Kap→taban orta</td><td>@OPTC@</td><td>düz kenarlı mührün gözle hizalandığı referans</td></tr>
</table>

<h3>Dört yatay hizalama alternatifi</h3>
<p class="small">Mühür yalnızca dikeyde kaydırıldı. Ölçekleme veya bozulma yok; her ikilide <b>tam olarak kanonik mühür</b> kullanıldı. Seçim yapılmadı.</p>
<div class="grid4">
@ALIGN_CARDS@
</div>

<h3>Kilit dikey &amp; yığın önizleme</h3>
<div class="grid2">
  <figure class="card"><img src="assets/WU-stacked.svg" alt="stacked lockup"><figcaption>Yığın</figcaption></figure>
  <figure class="card"><img src="assets/WU-horizontal.svg" alt="horizontal lockup"><figcaption>Yatay</figcaption></figure>
</div>
<div class="box"><div class="mono">yığın ölçümü: @STACK@</div></div>

<h2>C · Doğrulama</h2>
<h3>Kontur ve içerik kontrolleri (@SV_PASS@ PASS / @SV_FAIL@ FAIL)</h3>
<table>@ROWS_SV@</table>

<h3>Geometri kabul kapısı &mdash; @QG_FAIL@ FAIL / @QG_N@ kontrol</h3>
<table>@ROWS_QG@</table>

<h2>D · Son boyut kullanım önizlemeleri</h2>
<div class="grid2">
  <figure class="card"><img src="assets/horizontal-800.png"><figcaption>yatay 800&nbsp;px</figcaption></figure>
  <figure class="card"><img src="assets/horizontal-400.png"><figcaption>yatay 400&nbsp;px</figcaption></figure>
  <figure class="card"><img src="assets/horizontal-200.png"><figcaption>yatay 200&nbsp;px</figcaption></figure>
  <figure class="card"><img src="assets/stacked-350.png"><figcaption>yığın 350&nbsp;px</figcaption></figure>
</div>
<h3>Koyu zemin</h3>
<div class="grid2">
  <figure class="card" style="background:#141210"><img src="assets/horizontal-dark-800.png"><figcaption style="color:#ddd">yatay · koyu</figcaption></figure>
  <figure class="card" style="background:#141210"><img src="assets/horizontal-dark-400.png"><figcaption style="color:#ddd">yatay · koyu</figcaption></figure>
</div>

<div class="note">
<b>Ne yapılmadı.</b> Hizalama otomatik seçilmedi. Kelime markası ve kilitler kanonikleştirilmedi. Mühür dosyası değiştirilmedi — SHA-256 her kilitte doğrulandı. Görsel Üretim yok, ölçek büyütme yok; yalnızca gerçek vektör geometrisi.
</div>

<p class="small"><a href="../">← Asya'da Eğitim mühür galerisi</a></p>
</div></body></html>
"""


if __name__ == "__main__":
    main()