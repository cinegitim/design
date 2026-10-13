# Teslim notu (handoff) · Başvuru Rehberi / 001

## Kim / ne

| Alan | Değer |
|---|---|
| Yürütücü | OpenCode (`brand-director`) |
| Marka | `asyada-egitim` (Asya'da Eğitim) — V-01 kanonik mühür, onaylı lockup ailesi |
| Görev dalı | `publish/opencode-basvuru-rehberi-001-cince-20261013` |
| Taban SHA | `f7624fcf5e5140a9d5c704c4d9606bbcedce4f36` (`origin/main`) |
| Paket | `docs/instagram/basvuru-rehberi-001-cince-bilmeden` |
| Format | 6 × 1080×1350 PNG carousel + düzenlenebilir kaynaklar + inceleme galerisi |
| Durum | Teknik üretim ve doğrulama tamam · **insan yaratıcı incelemesi bekliyor** · birleştirme/Instagram yayını için açık yetki bekliyor |

## Girdiler

- Kullanıcı brief'i: yedi bölümlü üretim brief'i (başvuru rehberi 001, Çince bilmeden Çin'de okuyabilir miyim?).
- `AGENTS.md`, `.opencode/commands/brand-apply.md`, `.opencode/skills/brand-studio/SKILL.md`,
  `studio/workflow/PUBLISHING.md`, `.opencode/skills/brand-studio/references/image-production.md`.
- `brands/asyada-egitim/brand.json` + `canonical-lockups.json` (kilitli).
- Önceki kampanya altyapısı: `docs/instagram/launch-creative-02` render/doğrulama hattı,
  `docs/instagram/tsinghua-atlas-2027` Commons fotoğraf lisanslama örneği.

## Çıktılar

- `final/` — 6 adet 1080×1350 PNG.
- `originals/` — metin ve logo içermeyen sanat yönetimi tabanları (fotoğraf + motif geometrisi).
- `source/` — her slayt için SVG + HTML (Jost ve Songti SC gömülü) ve `-plate` varyantları.
- `assets/` — Jost (OFL), CJK alt kümesi, kanonik manifest, bağlantılı kanonik lockup SVG'leri.
- `photos/` — 12 lisanslı Wikimedia Commons fotoğrafı (1500 px'e küçültülmüş türevler).
- `mobile/` — 324×405 ve 375×469 önizlemeler.
- `index.html` — inceleme galerisi; `contact-sheet.png`,
  `original-to-final-contact-sheet.jpg`, `mobile-preview-contact-sheet.png`.
- `manifest.json`, `exact-copy.json`, `exact-copy.md`, `caption-and-credits.md`,
  `generation-notes.md`, `quality-review.md`, `render-validation.json`.
- `package/basvuru-rehberi-001-cince.zip` — teslim paketi.
- `studio/cloud/policy.json` — paket kaydı eklendi (mevcut sözleşmeler değişmedi).

## Yapılan araç çağrıları

| Araç / komut | Amaç |
|---|---|
| `verify_asyada_canonical_lockups.py` | Build öncesi ve commit öncesi kanonik kilit doğrulama (PASS) |
| `preflight.py --brand asyada-egitim` | Dal ve kilitli kaynak hash kontrolü (PASS) |
| `studio/cloud/audit.py` | Bağımsız gönderi denetimi (PASS, 5 paket) |
| Wikimedia Commons API | 12 fotoğrafın lisans/fotoğrafçı/kaynak doğrulaması ve indirme |
| zh.wikipedia.org + resmî üniversite alan adları | Çince karakter ve program iddialarının doğrulanması |
| `node render.mjs` (Playwright/Chromium) | 6 slayt + 6 taban render'ı ve geometri ölçümü |
| `python3 verify_and_package.py` | Bağımsız doğrulama, mobil/önizleme üretimi, ZIP |

## Kontroller

- [x] 6 gerçek 1080×1350 PNG; hash'leri manifest ile eşleşiyor.
- [x] Kilitli metnin tamamı birebir (`exact-copy.json` → PASS, 6/6 slayt).
- [x] Metin–metin / metin–lockup / Çince işaret / ikon–etiket çakışması yok; kırpma yok.
- [x] Jost ve Songti SC gömülü ve doğrulandı.
- [x] Kanonik lockup: bağlantılı, orantısız, minimum boyut üzerinde, çerçevede.
- [x] Üniversite–şehir–program ilişkileri doğru; fotoğraflar yanlış ad altında kullanılmadı.
- [x] Görsel üretim çağrısı: **0**. Ücretli backend: **0**.
- [x] Paket `studio/cloud/policy.json`'a kaydedildi; bağımsız denetim PASS.

## Çözümlenmemiş kısıtlar (insan incelemesi)

1. **`Asya'da Eğitim` satırı (slayt 06):** brief hem kanonik lockup kullanımını hem de
   "marka wordmark'ını yeniden dizme" yasağını getiriyor. Marka adı kanonik lockup ile
   verildi; bu nedenle bu satır `<text>` olarak dizilmedi. Kayıt `exact-copy.md` ve
   `exact-copy.json` içinde açıkça tutuldu.
2. **Zhejiang MBBS kampüsü:** 2025 broşüre göre MBBS sınıfları 2023'ten itibaren Yiwu
   Kampüsü'nde; üniversite ve Tıp Fakültesi Hangzhou'da. Kilitli metin değiştirilmedi,
   çelişki kayda geçirildi.
3. **Program listeleri:** Ekim 2026 itibarıyla resmî kaynaklara dayanır; üniversitelerin
   yıllık güncellemelerine tabidir. Sayısal program sayısı uydurulmadı.
4. **Fotoğraflar:** Belgesel Commons görüntüleri; kırpma ve ton geçişi uygulandı.
5. **CC BY-SA atıfı:** Instagram'da yayınlanması hâlinde fotoğrafçı + lisans gösterimi
   gerekir; metin `caption-and-credits.md` içinde hazırdır.

## Yetki durumu

Birleştirme, Pages yayını ve Instagram paylaşımı **yalnızca kullanıcının açık izniyle**
yapılabilir. Bu PR birleştirilmemiş olarak teslim edilmiştir; canlı URL iddiası yoktur.
