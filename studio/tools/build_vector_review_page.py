#!/usr/bin/env python
"""Assemble the vector-quality review page under docs/asyada-seal/vector-review/."""
import json
import os
import shutil

ROOT = "/Users/serdaryurt/Documents/OpenCode/Design"
RUN = os.path.join(ROOT, "brands/asyada-egitim/explorations/wordmark-ref")
DOC = os.path.join(ROOT, "docs/asyada-seal/vector-review")
A = os.path.join(DOC, "assets")

VARIANTS = [("poly", "WU-poly.svg", "1 · WU polygonal",
             "552 straight segments &middot; 0 curves"),
            ("smooth", "WU.svg", "2 · WU smooth (overfitted)",
             "1460 cubics &middot; 0 straight segments"),
            ("A", "WA.svg", "3 · Candidate A &mdash; typeface",
             "genuine Jost outlines, SIL OFL, wght 700"),
            ("B", "WB.svg", "4 · Candidate B &mdash; custom",
             "hand-drafted &middot; straight edges exact, curves circular arcs")]


def main():
    os.makedirs(A, exist_ok=True)
    rep = json.load(open(os.path.join(RUN, "audit/vector-review.json")))
    cand = json.load(open(os.path.join(RUN, "audit/type-candidates.json")))
    oa = json.load(open(os.path.join(RUN, "audit/optical-alignment.json")))

    copy = []
    for key, wm, _l, _d in VARIANTS:
        shutil.copy2(os.path.join(RUN, "svg", wm),
                     os.path.join(A, "wm-%s.svg" % key))
        shutil.copy2(os.path.join(RUN, "vector-review", "%s-full.png" % key),
                     os.path.join(A, "full-%s.png" % key))
        shutil.copy2(os.path.join(RUN, "vector-review", "usage-%s.png" % key),
                     os.path.join(A, "usage-%s.png" % key))
        shutil.copy2(os.path.join(RUN, "vector-review", "glyphs-%s.png" % key),
                     os.path.join(A, "glyphs-%s.png" % key))
    shutil.copy2(os.path.join(RUN, "reference.jpg"), os.path.join(A, "reference.jpg"))
    for key in ("A", "B"):
        for kind in ("horizontal", "stacked"):
            shutil.copy2(os.path.join(RUN, "vector-review",
                                      "%s-lockup-%s.png" % (key, kind)),
                         os.path.join(A, "%s-lockup-%s.png" % (key, kind)))
        for off in ("-4", "+0", "+4", "+8"):
            shutil.copy2(os.path.join(RUN, "vector-review",
                                      "%s-align%s.png" % (key, off)),
                         os.path.join(A, "%s-align%s.png" % (key, off)))

    def v(k, f, d="&mdash;"):
        return rep["variants"][k].get(f, d)

    rows = "\n".join(
        "<tr><td><b>%s</b></td><td>%s</td><td class=n>%d</td><td class=n>%d</td>"
        "<td class=n>%d</td><td class=n>%d</td><td class=n>%d</td>"
        "<td class=n>%s</td></tr>"
        % (lab, desc, v(k, "nodes"), v(k, "curves"), v(k, "lines"),
           v(k, "subpaths"), v(k, "curvature_sign_flips"),
           v(k, "measure")["spread_px"] if isinstance(v(k, "measure"), dict) else "&mdash;")
        for k, _w, lab, desc in VARIANTS)

    fulls = "\n".join(
        '<figure class="card"><img src="assets/full-%s.png" alt="%s">'
        '<figcaption>%s<br><span class=sm>%s</span></figcaption></figure>'
        % (k, lab, lab, desc) for k, _w, lab, desc in VARIANTS)

    usages = "\n".join(
        '<figure class="card"><img src="assets/usage-%s.png" alt="%s usage">'
        '<figcaption>candidate %s &middot; 1000 / 600 / 320 / 200 / 120 px</figcaption>'
        '</figure>' % (k, k, k) for k in ("poly", "smooth", "A", "B"))

    glyphs = "\n".join(
        '<figure class="card"><img src="assets/glyphs-%s.png" alt="glyphs %s">'
        '<figcaption>A S G D M I-dot apostrophe breve &middot; 100 / 400 / 800 %%</figcaption>'
        '</figure>' % (k, k) for k in ("poly", "smooth", "A", "B"))

    lockups = "\n".join(
        '<figure class="card"><img src="assets/%s-lockup-%s.png">'
        '<figcaption>candidate %s &middot; %s &middot; canonical seal '
        'SHA-256 %s&hellip;</figcaption></figure>'
        % (k, kind, k, kind, rep["canonical_sha256"][:12])
        for k in ("A", "B") for kind in ("stacked", "horizontal"))

    aligns = "\n".join(
        '<figure class="card"><img src="assets/%s-align%s.png">'
        '<figcaption>candidate %s &middot; seal offset %s px</figcaption></figure>'
        % (k, off, k, off) for k in ("A", "B") for off in ("-4", "+0", "+4", "+8"))

    wa, wb = cand["candidates"]["A"], cand["candidates"]["B"]
    meas_rows = "\n".join(
        "<tr><td>%s</td><td class=n>%s</td><td class=n>%s</td>"
        "<td class=n>%s</td><td class=n>%s</td></tr>"
        % (k,
           "%.2f" % wa["ink"][l]["x0"], "%.2f" % wa["ink"][l]["x1"],
           "%.2f" % wa["ink"][l]["w"], "%.2f" % wb["ink"][l]["w"])
        for k, l in (("TR1", "tr1"), ("TR2", "tr2"), ("EN", "en")))

    html = PAGE
    for _k, _v in [("@ROWS@", rows), ("@FULLS@", fulls), ("@USAGES@", usages),
                   ("@GLYPHS@", glyphs), ("@LOCKUPS@", lockups), ("@ALIGNS@", aligns),
                   ("@MEAS@", meas_rows), ("@SEAL@", rep["canonical_sha256"]), ("@OPTC@", oa.get("optical_reference", {}).get("cap_to_baseline_mid_y", "-")),
                   ("@BBOXC@", round(oa["wordmark"]["bbox_centre"], 2)), ("@INKC@", round(oa["wordmark"]["ink_centroid"], 2))]:
        html = html.replace(_k, str(_v))
    open(os.path.join(DOC, "index.html"), "w", encoding="utf-8").write(html)
    print("wrote %s/index.html (%d bytes)" % (DOC, len(html)))


PAGE = r"""<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asya'da Eğitim — Vektör Kalite İncelemesi · İNCELEME</title>
<style>
:root{--paper:#F7F3E9;--ink:#141210;--verm:#BD2120;--mute:#6b635a;--line:#ddd5c4}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding:40px 22px 90px}
h1{font-size:34px;line-height:1.2;margin:0 0 6px}
h2{font-size:23px;margin:56px 0 4px;padding-top:22px;border-top:1px solid var(--line)}
h3{font-size:16px;margin:26px 0 6px}
p{margin:9px 0}
.sub{color:var(--mute);font-size:15px;margin-bottom:24px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:14px 0}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--mute);font-weight:600}
td.n,th.n{text-align:right;font-family:ui-monospace,Menlo,monospace}
.pending{background:var(--verm);color:#fff;padding:16px 20px;margin:26px 0;font-weight:600;letter-spacing:.04em}
.note{background:#fff;border:1px solid var(--line);border-left:5px solid var(--verm);padding:15px 19px;margin:20px 0}
.note.ok{border-left-color:#2f7a4a}
.small,.sm{font-size:14px;color:var(--mute)}
.sm{font-size:12.5px}
img{max-width:100%;display:block}
figure{margin:0}
figcaption{font-size:13px;color:var(--mute);margin-top:7px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.card{background:#fff;border:1px solid var(--line);border-radius:2px;padding:10px;margin:0}
.good{color:#2f7a4a;font-weight:700}
.bad{color:var(--verm);font-weight:700}
a{color:var(--verm)}
</style></head>
<body><div class="wrap">

<div class="pending">TARİHSEL ÇALIŞMA — B REDDEDİLDİ. A / JOST 700 ONAYLANMADI.</div>
<div class="note"><b>Bu sayfa artık geliştirme kaynağı değildir.</b> Önceki düğüm ve raster eğri sayımları tipografik doğruluğu veya görsel kaliteyi kanıtlamaz. Güncel çalışma özgün referansa göre ayrı Türkçe/İngilizce ağırlıklarını karşılaştırır. <a href="../typography-weights/">Referans öncelikli tipografi incelemesini aç →</a></div>

<h1>Kelime Markası — Vektör Kalite İncelemesi</h1>
<p class="sub">Raster izleme → kübik uydurma → yumuşatma hattı <b>durduruldu</b>. Onaylı referansın aynısı, iki yeni vektör yöntemle yeniden kuruldu.</p>

<div class="pending">A ONAYLANMADI · B REDDEDİLDİ · HİZALAMA SEÇİLMEDİ · KANONİKLEŞTİRME YOK</div>

<div class="note">
<b>Neden yeniden yapıldı.</b> "Pürüzsüz" sürüm 1460 kübik, 0 düz çizgi üretiyordu. Otomatik raster→Bézier dönüşümü, ölçtüğümüz her şeyi daha iyi yaptı ama <i>görsel olarak daha kötü</i>. Aşağıdaki ölçüm bunu doğruluyor: aşırı uydurulmuş sürüm, düğüm sayısında ve eğri salınımında çokgen sürümden daha kötüdür. Sıfır düz çizgi bir kalite hedefi değildir.
</div>

<h2>1 · Beşli karşılaştırma</h2>
<figure class="card"><img src="assets/reference.jpg" alt="approved typography reference">
<figcaption>0 · Onaylı tipografi referansı (raster, 1012&times;558)</figcaption></figure>
<div class="grid2">
@FULLS@
</div>

<h2>2 · Geometri ölçümü &mdash; son SVG konturlarından</h2>
<p class="small">Sayımlar <b>nihai SVG dosyasının</b> <span class=sm>path d</span> verisinden okundu; girdi konturlarından veya yeniden oluşturulmuş vekillerden değil.</p>
<table>
<tr><th>Sürüm</th><th>Kaynak</th><th class=n>Düğüm</th><th class=n>Eğri</th><th class=n>Düz çizgi</th><th class=n>Alt yol</th><th class=n>Eğri işaret değişimi</th><th class=n>Ölçü farkı</th></tr>
@ROWS@
</table>
<p class="small"><b>Eğri işaret değişimi</b>, kontur normalinin yön değiştirdiği yer sayısıdır &mdash; salınım ve kıpırdamanın ölçüsü. Düşük iyidir. Aday B en düşük değere sahiptir; aşırı uydurulmuş sürüm çokgen sürümden <i>daha kötüdür</i>.</p>

<h3>Üç satır ortak ölçü (aday A / aday B)</h3>
<table>
<tr><th>Satır</th><th class=n>A: sol</th><th class=n>A: sağ</th><th class=n>A: genişlik</th><th class=n>B: genişlik</th></tr>
@MEAS@
</table>
<p class="small">Her iki adayda da üç satır da 880.90 px ile ölçüyü tamamen doldurur; yalnızca harfler arası boşluk değiştirilir, hiçbir harf esnetilmez.</p>

<h2>3 · Harf bazında &mdash; 100 / 400 / 800 %</h2>
<p class="small">A S G D M &middot; İ noktası &middot; kırmızı tırnak &middot; Ğ breve. Üç panel: çokgen, aşırı uydurulmuş, aday A, aday B.</p>
@GLYPHS@

<h2>4 · Gerçek kullanım boyutları</h2>
@USAGES@

<h2>5 · Kilitler &mdash; gerçek kanonik mühür</h2>
<p class="small">Her ikilide kanonik mühür dosyası olduğu gibi kullanıldı: SHA-256 <span class=sm>@SEAL@</span>. Mühür hiçbir aday tarafından değiştirilmedi.</p>
<div class="grid2">
@LOCKUPS@
</div>

<h2>6 · Optik hizalama alternatifleri</h2>
<p class="small">Mühür yalnızca dikeyde kaydırıldı; ölçek veya bozulma yok. <b>Seçim yapılmadı.</b> Ölçülen referanslar: kap→taban ortası @OPTC@ px, kutu merkezi @BBOXC@ px, mürekkep ağırlık merkezi @INKC@ px.</p>
<div class="grid4">
@ALIGNS@
</div>

<h2>7 · Yöntem</h2>
<div class="note ok">
<b>Aday A &mdash; yazıtipi tabanlı.</b> Referansın belirleyici özellikleri: eğik kesimli S terminalleri, yuvarlak G ve D kâsiteleri, sivri A apeksi. Bu, Futura soyundan gelen <b>Jost</b>'u (SIL OFL) işaret eder. Poppins ikinci sırada geldi (0.420 IoU'ya karşı 0.386) ama S terminalleri yatay olduğu için en görünür uyumsuzluğu oluşturuyordu. Gerçek konturlar fonttan gelir; hiçbir izleme yok.
</div>
<div class="note ok">
<b>Aday B &mdash; özel vektör harfleme.</b> 1000 birimlik em üzerinde, tek bir gövde ağırlığı parametresiyle harf harf çizildi. Düz kenarlar tam olarak düzdür (<span class=sm>H</span>/<span class=sm>V</span> komutları), eğriler gerçek dairelerdir (<span class=sm>A</span> yayları) &mdash; bu yüzden merdiven basamağı, çıkıntı, sivri uç veya salınım <i>oluşamaz</i>. Gövde ağırlığı tüm alfabe boyunca yapısal olarak tutarlıdır. Ğ breve, İ noktaları ve kırmızı tırnak çizilmiştir; ödünç alınmamıştır.
</div>

<h2>8 · Bilinen açık kusurlar</h2>
<div class="note">
<ul style="margin:0;padding-left:20px">
<li><b>Aday B:</b> M'in orta tepesi hâlâ hafif bir çentik bırakıyor; G'nin barı ağız açısına göre ayarlanabilir. Bunlar eleyici değil, insanın düzeltmesi için notlar.</li>
<li><b>Aday A:</b> Jost'un kendi M genişliği referanstan biraz daha geniş; A'nın apoks açıklığı da referanstan farklı. Optik düzeltme önerilir.</li>
<li>Hiçbir aday otomatik olarak seçilmedi. Ölçümler karşılaştırma içindir, onay değildir.</li>
</ul>
</div>

<div class="note">
<b>Ne yapılmadı.</b> Hizalama seçilmedi. Kilitler kanonikleştirilmedi. Mühür dosyası değiştirilmedi — SHA-256 her ikilide doğrulandı. Görsel üretim yok, ölçek büyütme yok, <span class=sm>approxPolyDP</span> yok, otomatik raster→Bézier dönüşümü yok.
</div>

<p class="small"><a href="../">← Asya'da Eğitim mühür galerisi</a></p>
</div></body></html>
"""

if __name__ == "__main__":
    main()
