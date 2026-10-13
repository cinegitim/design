# Asya'da Eğitim — Başvuru Rehberi / 001
## Çince bilmeden Çin'de okuyabilir miyim?

Six-slide Instagram carousel, 1080×1350, built for the Asya'da Eğitim brand from
the approved V-01 canonical seal and the approved lockup family.

---

## 1. What this is

A production carousel, not a concept round. The copy was supplied locked and is
reproduced verbatim. The art direction was produced in response to the brief's
requirement that the series be *distinctively Chinese* — recognisable even with
the text hidden.

## 2. How it was produced

| Stage | Method |
|---|---|
| Factual check | Every fixed claim checked against official university sources before layout |
| Photography | 12 freely licensed Wikimedia Commons photographs, downloaded once, credited per file |
| Chinese motifs | Locally generated deterministic SVG geometry (`motifs.py`) |
| Typography | Jost embedded from the canonical brand file; Songti SC subset embedded for 17 verified CJK characters |
| Canonical lockups | Verbatim manifest-listed SVGs linked, never redrawn or retypeset |
| Render | One Playwright/Chromium pass at final resolution; copy-free plates rendered separately |
| Geometry audit | `render.mjs` measures every `<text>` box, the lockup box, CJK marks and icons, and throws on any overflow, collision or clipping |
| Visual review | Two full contact-sheet reviews with actual image inspection between them |

No image model was called at any point. No paid backend was used.

## 3. Per-slide art direction

| Slide | Concept | Chinese device | Ground |
|---|---|---|---|
| 01 | Cinematic cover | Circular moon-gate opening + ice-ray lattice panel, gold ring | Deep ink, China-red answer, bright-gold accents |
| 02 | Undergraduate field collage | Lattice geometry interrupting the right-hand photograph | Warm ivory, China-red typography, gold rules |
| 03 | University photo atlas | Flower-window lattice crop frames, red location band | Dominant central photograph + two supporting sections |
| 04 | Master's editorial | Gold editorial rules + small geometric seal-inspired accents | Deep ink, restrained China-red plane |
| 05 | Doctoral research | Large abstracted circular architectural motif + sparse xiangyun contour | Dark research photography, controlled red surface |
| 06 | Application dossier | Red archival-folder form, gold detailing, restrained seal-like accent | Warm paper, vector iconography |

Every slide uses **one or two primary devices only**. No slide repeats the same
ornamental border as another.

## 4. Colour system

Canonical brand values: `#BD2120` red, `#1D2027` ink, `#F7F3E9` paper.
Campaign-only treatments: `#DE2910` China red, `#D9A441` imperial gold,
`#F3C64D` bright gold, `#F4E8D3` warm ivory.

The two reds are never adjacent: brand red carries the canonical signature and
the hero answer word, China red carries campaign graphics (bands, planes, folder
form, kicker rules). Gold appears as large accents (the cover's answer underline,
slide 05's accent bar, the folder's inner rule), not only as hairlines.

## 5. Typography

Jost for all Turkish copy, embedded from
`brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf`.
Weights used: 400, 500, 600, 700. No text is rasterised; every line is an
editable `<text>` element inside `#editable-campaign-copy`.

Songti SC (subset to 17 characters) carries the secondary Chinese marks only —
`留学` on the cover and the three verified university names on the atlas slide.
No imitation "Chinese-style" display font is used.

## 6. Copy fidelity

`exact-copy.json` holds the locked copy and a line-by-line check. Multi-line
breaks split only at existing spaces; joining the fragments reproduces the
supplied text exactly. One line, `Asya'da Eğitim` on slide 06, is delivered by
the approved canonical lockup rather than retypeset — see that file for the
explicit record.

## 7. Honest limitations

- Photographs are authentic Commons images of the named institutions, but crops
  and tonal overlays were applied for legibility. They are documentary campus
  imagery, not commissioned campaign photography.
- Programme listings reflect official pages at the time of research (October
  2026) and are subject to the universities' own annual changes. Slide 06's
  document list is illustrative of common requirements, not a guarantee.
- No image model was asked to produce or reproduce any logo, wordmark, seal or
  institution.

## 8. Status

Technical production complete: geometry audit, copy verification, canonical
lockup verification and packaging all pass. **Human creative review pending.**
Not published to Instagram.

---

# Revizyon 2 — kullanıcı geri bildirimi üzerine düzeltmeler

Kullanıcı iki majör sorun bildirdi; ikisi de doğrulandı ve düzeltildi. Bu bölüm
yalnızca revizyon 2'yi belgeler; revizyon 1'in kaydı yukarıdadır.

## 2.1 Logo varyantları ters atanmıştı

Onaylı varyant adlandırması SVG dolgularından okundu:

| Varyant | Harf dolgusu | Doğru zemin |
|---|---|---|
| `light` | `#1D2027` | açık |
| `dark` | `#F7F3E9` | koyu |

Üretimde bu adlandırma ters varsayılmıştı. Sonuç: koyu zeminli 01/03/04/05'te
mürekkep wordmark mürekkep zeminde **görünmez**; açık zeminli 02/06'da kâğıt
wordmark fildişi/kâğıt zeminde kontrast ~1,1:1. Yani altı slaydın tamamında
marka tipografisi kayboluyordu — yalnızca kırmızı mühür ve apostrof görünüyordu.

| Slayt | Zemin | Hatalı | Düzeltilmiş | Ölçülen kontrast |
|---|---|---|---|---|
| 01 | mürekkep | D-04/light | D-04/dark @340 | 14,4:1 |
| 02 | sıcak fildişi | D-04/dark | D-04/light @300 | 13,5:1 |
| 03 | mürekkep | D-04/light | D-04/dark @340 | 14,7:1 |
| 04 | mürekkep | D-04/light | D-04/dark @340 | 14,7:1 |
| 05 | mürekkep | D-04/light | D-04/dark @340 | 13,0:1 |
| 06 | kâğıt | D-04/dark | **H-02/light @528** | 14,7:1 |

Ekler:
- 01/03/04/05'teki D-04 boyutu 300–340 px'e çıkarıldı (varyant minimumu 200 px).
- Slayt 06'da kapanış imzası **birincil yatay H-02** yapıldı (min. 528 px).
  D-04 "küçük dijital kullanım" varyantıdır ve kapanış imzası için zayıftı.
  H-02 yatay oran (2,6655) korunarak 528 × 198,04 px olarak kompozit edildi;
  İngilizce `EDUCATION IN ASIA` satırı tam olarak görünüyor.
- `verify_and_package.py` içine **kalıcı bir marka uyumu kapısı** eklendi: her
  slaytta zemin parlaklığı ölçülür, seçilen varyantın o zemin için doğru olup
  olmadığı ve wordmark/zemin kontrastının ≥ 4,5:1 olup olmadığı denetlenir.
  Kapı, orijinal hatayı (D-04/light + mürekkep zemin) enjekte edilerek test
  edildi ve doğru biçimde reddetti.

## 2.2 "Ve çok daha fazlası." üç kez tekrar ediyordu

Kilitli metinde kalıp 02, 04 ve 05'te birebir geçiyordu. Kullanıcı en fazla bir
kez olmasını istedi.

- **02** (beş alan grubundan sonra): kalıp **korundu** — alan genişliğini
  anlattığı için burada en doğal yer.
- **04** → `Başka üniversitelerde de İngilizce programlar var.`
- **05** → `Sunulan alanlar bununla sınırlı değil.`

İki yeni ifade de olgusal ve promosyon olmayandır; resmî kaynaklarla
doğrulanabilir (SHU, Tsinghua ve Fudan'un listelenenlerden çok daha fazla
İngilizce programı vardır). Slogan eklenmedi, diğer hiçbir satıra dokunulmadı.

`exact-copy.json` artık her slaydın *birleşik* metnini, yalnızca bu iki belgeli
değişiklik uygulandıktan ve lockup ile teslim edilen marka satırı çıkarıldıktan
sonra karşılaştırır; başka her fark üretimi durdurur.
