# Figma file blueprint — `<slug> — Brand System`

> Amaç: brand-studio'da seçilip canonical hâle gelen marka dilini Figma'da
> **Variables + Components + Templates** olarak uygulanabilir kılmak.
> Sıfırdan AI tasarımı üretmek **değil**. Determinizm: typography, spacing,
> colors, logo rules ve layout mümkün olduğunca token'a bağlı; image generation
> yalnızca *değişken içeriği* üretir.

## Dosya

- **Ad:** `<brand-slug> — Brand System` (örn. `asya-egitim — Brand System`)
- **Kaynak:** `brands/<slug>/brand-system.md` + `figma/tokens/<slug>.tokens.json`
- **Kural:** Dosyadaki her karar, brand-system.md'nin bir maddesine işaret eder;
  madde yoksa karar da yoktur.

## Sayfa sırası (8 sayfa)

| # | Sayfa | İçerik |
|---|---|---|
| 1 | **00 Cover** | Kapak frame'i (1920×1080): marka adı, versiyon/tarih, repo yolu, kapsam listesi. Kapakta yalnızca canonical varlıklar. |
| 2 | **01 Brand DNA** | Concept paragrafı (§1), logo mantığı + kilitli geometri tablosu (§2 — token referanslı), wordmark karakteri (§3), palet oransal çubuklarla (§5), tip örnekleri. Bu sayfa **salt-okunur referans**tır; üretim burada yapılmaz. |
| 3 | **02 Foundations** | **Variables/Styles kurulum sayfası** — aşağıdaki Foundations bölümüne bak. Hiçbir bileşen/şablon, bu sayfada tanımsız bir token kullanamaz. |
| 4 | **03 Components** | Yeniden kullanılabilir bileşenler + varyantlar — aşağıdaki Components bölümüne bak. |
| 5 | **04 Patterns** | Pattern dili kararı belgelenir (örn. asya-egitim: *"desen yok"* — §8). Açıklık işaretinin tek-rol kuralı (§7), serbest doku sınırları (kâğıt greni %4–6). Yayılma yasakları burada görsel örneklerle gösterilir. |
| 6 | **05 Templates** | Kontrollü üretim şablonları — aşağıdaki Templates bölümüne bak. |
| 7 | **06 Applications** | brand-system.md §18 kontrol listesini aynalayan uygulama frame'leri; her biri 05 Templates'in bir instance'ıdır. Export preset'leri (PNG @1x/@2x, SVG, PDF) burada tanımlanır. |
| 8 | **07 Playground** | **Sandbox.** Serbest deneme alanı. Buradaki hiçbir şey 05/06'ya, oradan da canlıya akmaz; akması için brand-studio onay hattı ( `/brand-refine` → `brand-system.md` → yeniden türetme) gerekir. |

## 02 Foundations → Variables/Styles

**Variables koleksiyonları** (Tokens Studio gruplarından eşlenir):

| Koleksiyon | Kaynak grup | Mod/Not |
|---|---|---|
| `core/color` | `color` | Primitive; Figma'da semantik alias'lar buna bağlanır |
| `core/typography` | `typography.family`, `typography.weight` | Family string + weight number |
| `core/space` | `space` | 4pt taban ölçeği |
| `core/logo` | `logo.geometry`, `logo.sizes` | Kilitli geometri — asla değişken-dışı ölçü kullanılmaz |
| `core/motion` | `motion` | duration (ms) |
| `core/grid` | `grid` | 12 kolon editoryal |

**Text Styles** (token'lı, serbest ölçü yasak):

- Display: Fraunces 600 — ölçek oranı 1.333 (örn. 64 / 48 / 36 / 27)
- UI: Inter 400/500/600 — ölçek oranı 1.25 (örn. 16 / 12.8→13 / 10)
- Mono: IBM Plex Mono 400/500 — etiket/veri

**Layout/Grid Styles:** 12 kolon editoryal; marj/gutter space token'larından.

**Radius:** yalnızca sistemde tanımlıysa (`brand-system.md` radius kilitlemiyorsa
radius koleksiyonu kurulmaz; serbest radius yasak).

## 03 Components → reusable yapılar

- **Logo component set** (tek set, varyantlar): `logo/primary`, `logo/secondary`,
  `logo/compact`, `logo/icon`, `logo/mono`. Tüm ölçüler `core/logo` değişkenlerine
  bağlı; resize yalnızca oransal (constrain: scale). Clear space kılavuzu (32 birim,
  2b) bileşen gömülü rehberi.
- **Icon set:** 2px yapılandırılmış çizgi, kare kapak (§9); tek boyut varyantı
  (24px) + `core/color`'a bağlı stroke.
- **Bilgi paneli** (device 2, §7): son-tarih / gereken / danışman-notu üçlü blok;
  auto-layout, space token'lı.
- **CTA:** tek CTA kuralı (§12); tek primary varyant, disabled/hover yoksa varyant da yok.

İsimlendirme: `component/variant` (örn. `logo/primary`); layer adları Türkçe/İngilizce
karmaşmaz — bileşen adları İngilizce, içerik metni markanın dili.

## 05 Templates → kontrollü üretim şablonları

| Şablon | Boyut | Not |
|---|---|---|
| Social post | 1080×1080 | Tek CTA; image slot + metin bloğu space token'lı |
| Story | 1080×1920 | 480px altı simge düşüşü kuralı digital §12'den |
| Poster | A3 · 297×420mm | Print §13; bronz yalnızca spot eşlemeli |
| Web hero | 1440×900 | Açıklık-kırpmalı slot + somut sonuç başlığı + tek CTA |
| Brochure | A4 katlamalı | İç sayfa ritmi: bilgi paneli tekrarı |

Kurallar:

- Her şablon = frame + **component instance'ları** + değişken-bağlı fill/stroke.
  Serbest renk, serbest font, serbest ölçü kullanılamaz.
- **Image slot** = placeholder frame (`image/<rol>`); gerçek raster yalnızca
  brand-studio üretiminden (Pollinations/GPT adapter, onaylı) gelir. Figma içinde
  raster üretimi yapılmaz; üretilse bile yalnızca *değişken içeriği* (görsel seçimi)
  doldurur — tipografi/spacing/logo/layout asla AI'a bırakılmaz.
- Export preset'leri şablon başına 06 Applications'ta tanımlanır.

## Sync (Faz 2 — henüz kurulmaz)

- Bugün aktarım manuel: Tokens Studio *Import* (adımlar `figma/tokens/README.md`).
- Faz 2: Tokens Studio ↔ repo sync **yalnızca gerçekten çalışan bir entegrasyon
  varsa**; çalışma kanıtlanmadan `/figma-sync` komutu yazılmaz.
- Türetme yönü hiçbir fazda tersine dönmez: repo → Figma.
