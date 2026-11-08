# Brand System — Asya Eğitim

> Canonical source of truth. Direction 3 — CURATED PASSAGE / THE SELECTIVE FIELD (kanonik, production). Eski B/Mürekkep/Satır/Köşe/İm kararları çıkarıldı; tarihsel exploration dosyaları silinmedi, deprecated olarak işaretlendi. Her logo, pano ve uygulama buradan türer.

## 1. Concept

- Central concept: Seçim → odak → geçit → imkân. Yoğun olasılık alanından tek anlamlı açıklığın bilinçli açılması.
- Why it fits: TR rakiplerin yolculuk/küre dilinden kopar; veliye seçicilik + güven, öğrenciye imkân hissi; ülkeye indirgenemeyen pan-Asya yapı; Çin Eğitim'e doğal uzar.
- Name/tagline handling: "ASYA EĞİTİM" Fraunces Semibold caps (+15/1000 tracking); yardımcı kilit "STUDY IN ASIA" (Inter Medium caps +420/1000); aday slogan: "Doğru açıklık." (TR).

## 2. Logo logic + signature geometry lock (variant C)

Seçilen optik varyant: **C** — üst taşma belirgin, siluet en ayırt edici; boşluğu zorla görünür kılmak değil, toplam siluet dengesi kriteriyle.

| Parametre | Değer |
|---|---|
| Alan en/boy | 226 × 190 birim (çıta bandı 226 × 130) |
| Çıta sayısı | 9 (slot 0,1,2,3,5,6,7,8,9; slot 4 eksik = seçim boşluğu) |
| Çıta kalınlığı (s) | 10 |
| Pitch (p) / aralık | 24 / 14 |
| Boşluk iç genişliği | 34 (komşu çıta kenarları arası) |
| Blade genişliği (b) | 16, boşluk merkezinde (x 100–116) |
| Blade üst taşma | 26 (y 4–30) |
| Blade alt taşma | 16 (y 160–176) |
| Taşma oranı (üst:alt) | ≈ φ (26:16) |
| Dış güvenli alan | 32 birim (2b) her yönde |

- Primary (`assets/logo-primary.svg`): işaret + path-kelime-mark, taban hizalı (baseline y=160), cap 92.
- Secondary (`assets/logo-secondary.svg`): üstte işaret + ortalı kelime-mark + Inter EN alt satırı.
- Compact (`assets/logo-compact.svg`): işaret + "AE" path.
- Icon (`assets/icon.svg`): yuvarlak karede kâğıt çıtalar + bronz blade.
- Monochrome (`assets/logo-mono.svg`): currentColor tek renk. KRİTİK KULLANIM NOTU: harici `<img>` gömmede `color` kalıtımı SVG belgesine geçmez — koyu zeminde ya inline SVG ile gömün (logo-board'da kanıtlı) ya da renge özel sürüm üretin.
- Favicon (`assets/favicon.svg`): tam geometri, 16px piksel-kanıtlı.
- Clear space: 32 birim; min: primary ekran 120px / baskı 35mm; icon min 24px / 8mm.
- Misuses (6): döndürme, esnetme, sistem-dışı renk, efekt, taşıyıcısız kalabalık zemin, bıçağı/boşluğu silme veya yeri değiştirme.

## 3. Wordmark character

- Fraunces SemiBold caps, tracking +15/1000; optik hiza: cap 92 birim, taban çıta-altıyla hizalı. Ğ brevesi satır-üstü boşlukta korunur; İ/Ç sedillaları testli.
- Fallback stack: "Fraunces", Georgia, serif. Final assetlerde path (aşağıda).

## 4. Typography

| Role | Family | Weights | Usage |
|---|---|---|---|
| Display / wordmark | Fraunces | 600 (+ italic vurgu) | başlık, kelime-mark, alıntı |
| Text / UI | Inter | 400 / 500 / 600 | gövde, arayüz, EN kilit |
| Accent/Mono | IBM Plex Mono | 400 / 500 | indeks, etiket, veri |

- Scale ratio 1.333 (display) / 1.25 (UI). Gövde 1.6; başlık 1.05–1.15.
- Licensing: üçü de Google Fonts OFL.
- Turkish verification (gerçek render, 2026-09-30): ASYA EĞİTİM · ÇİN EĞİTİM · JAPONYA'DA EĞİTİM · GÜNEY KORE'DE EĞİTİM · STUDY IN ASIA · Ğ ğ İ ı Ş ş Ç ç Ö ö Ü ü — üç adaydan Fraunces seçildi (karakter + sıcaklık; Source Serif 4 yedek).

## 5. Palette

| Token | Hex | RGB | Role | Proportion |
|---|---|---|---|---|
| `--brand-ink` | #141210 | 20,18,16 | Mürekkep · birincil | 30 |
| `--bg-paper` | #F7F3E9 | 247,243,233 | Sıcak Kâğıt · zemin | 60 |
| `--brand-bronze` | #A8875B | 168,135,91 | Mineral Bronz · imza | <8 |
| `--text-muted` | #6F6A5E | 111,106,94 | ikincil metin | — |
| `--brand-indigo` | #2A3A6B | 42,58,107 | (emekli — eski B kararı, kullanılmaz) | — |

- Contrast: ink/paper ~15:1; muted/paper ~5:1 (AA normal metin); bronz yalnızca grafik imza.
- Print: kuşe dışı sıcak kâğıt; bronz spot/matbaa eşlemeli.

## 6. Composition / grid

- 12 kolon editoryal; bilgi yoğunluğu + kontrollü boşluk karşıtlığı; imza hareketi: açıklık-kırpma (görsel seçimi) + danışman marj-notu. Hero: öğrenci anlatısı somut sonuç başlığıyla; bilgi paneli: son-tarih/gereken/durum üçlüsü.

## 7. Graphic devices

- Device 1: açıklık işareti (tek geometri, tek rol: seçim). Asla dekoratif çıta deseni olarak yayılmaz.
- Device 2: bilgi paneli kuralı (son-tarih/gereken/danışman-notu üçlü blok).

## 8. Pattern language

- Desen yok (karar): alan-çizgi dili yalnızca işarette yaşar; yayılırsa jefatura etkisi kaybolur. Dokuda kâğıt greni (%4–6) serbest.

## 9. Iconography

- 2px yapılandırılmış çizgi ikonlar, kare kapak; örnekler logo-board'da (üniversite, takvim, belge).

## 10. Photography / illustration language

- Soyut mimari ışık, yakın malzeme detayı (kâğıt/mürekkep/cam/metal), kırpılmış mekân, kontrollü renk alanları. Ülke manzarası yok; stok yüz yok; sonuç anlatan gerçek öğrenci portresi serbest (doğal ışık, pozsuz).

## 11. Texture / material

- Kâğıt greni, mürekkep kenarı, bronz folyo (premium baskı), cam/metal vurgular dijitalde.

## 12. Digital behaviour

- Hero: açıklık-kırpmalı görsel + somut sonuç başlığı + tek CTA; bilgi UI: beyaz yüksek-bilgi sayfaları; 480px altında simgeye düşme; reduced-motion: solma.

## 13. Print behaviour

- Kapak: işaret gofre + bronz folyo bıçak; iç: bilgi-paneli ritmi; fuar: parlak zemin duvar + kabul-hikâyesi bandı.

## 14. Motion behaviour

- Açıklık-perdesi (ışık bandı genişler, ≤700ms); reduced-motion'da solma. Otomatik kayan bant yok.

## 15. Tokens (`:root`)

```css
:root {
  --brand-ink: #141210;
  --bg-paper: #F7F3E9;
  --brand-bronze: #A8875B;
  --text-muted: #6F6A5E;
  --font-display: "Fraunces", Georgia, serif;
  --font-text: "Inter", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}
```

## 16. Sub-brand architecture

- Asya Eğitim (şemsiye, tam sistem) └── Çin Eğitim (ilk uzantı: aynı işaret + %78 mono-muted alt satır, girintili, kısa satırsız).
- Kural (gelecek: Japonya, Güney Kore, Singapur, Hong Kong): aynı işaret + aynı basamak; ülke satırı mono-muted; asla eşdeğer ikinci marka yok; bugün ayrı logo üretilmez.

## 17. Wordmark path status

- PRODUCTION PATH SHIPPED: `logo-primary.svg`, `logo-secondary.svg`, `logo-compact.svg`, `logo-mono.svg` kelime-markları gerçek outline path (Fraunces-SemiBold + tracking 60/2048, fontTools ile üretildi, render-doğrulamalı).
- Master: Fraunces-SemiBold statik TTF + tracking tablosu (§3); editable-text master board'da belgeli. EN alt satır Inter-Medium path.

## 18. Applications checklist

- [x] business cards · [x] letterhead · [ ] envelope · [ ] flyer · [ ] brochure · [ ] poster · [x] presentation · [x] social post · [x] story · [ ] LinkedIn/X/YouTube banners · [x] web hero · [x] event/signage · [x] favicon · [ ] email

## Coverage

- [x] All 14 points defined · [x] SVGs built (6, path-based) · [x] logo board built · [x] self-critique passed (render-based; Critical/High: 1 icon-bg defect found & fixed in QA harness)
