# Tokens — isimlendirme + Figma aktarımı

> Format: W3C Design Tokens tarzı `$value` / `$type` / `$description` (+ opsiyonel
> `$unit`), Tokens Studio for Figma ile uyumlu. Yapıyı `tokens.schema.json` doğrular.

## Kurallar

1. **Türetme:** Her dosya `brands/<slug>/brand-system.md`'den türetilir; değer orada
   yaşar, burada yansıtılır. Elle bağımsız düzenleme yok.
2. **Dosya adı:** `<slug>.tokens.json` (örn. `asya-egitim.tokens.json`).
3. **Gruplar** (tek seviye): `color`, `typography`, `logo`, `space`, `grid`,
   `motion`, `texture`, `subbrand`. Sistemde tanımsız grup kurulmaz
   (örn. radius kilitlememiş markada `radius` yoktur).
4. **İsimlendirme:** token adları İngilizce, küçük harf camelCase; `$description`
   markanın dilinde ( insan-okunur kanıt: brand-system.md madde numarası).
5. **Birim:** px ölçüler `$type: "dimension"` + `$unit` notu; oransız değerler
   `$type: "number"`; süreler `$type: "duration"` (ms).

## Grup → Figma koleksiyonu eşlemesi

| JSON grubu | Figma Variables koleksiyonu | Styles |
|---|---|---|
| `color` | `core/color` | color styles (primitive + semantik alias) |
| `typography.family` + `typography.weight` | `core/typography` | text styles |
| `space` | `core/space` | layout/grid styles |
| `logo.*` | `core/logo` | — (bileşen ölçüleri) |
| `motion` | `core/motion` | — (smart animate süreleri) |
| `grid` | `core/grid` | layout grid styles |
| `texture` | `core/texture` | — (opaklık/doku) |
| `subbrand` | `core/subbrand` | alt-marka varyant değerleri |

## Figma'ya aktarım (manuel, Faz 1)

1. Figma → **Tokens Studio for Figma** eklentisi → *Tokens* sekmesi → *Import*.
2. `figma/tokens/<slug>.tokens.json` seç → gruplar yukarıdaki eşlemeyle
   Variables/Styles olarak kur.
3. Semantik alias'ları Figma'da bağla (örn. `text-primary` → `color.ink`).
4. Blueprint'teki **02 Foundations** sayfasında dokümante et.

## Doğrulama

```sh
python3 -c "import json,sys; json.load(open('figma/tokens/asya-egitim.tokens.json'))"
# veya şema ile:
npx ajv-cli validate -s figma/tokens/tokens.schema.json -d 'figma/tokens/*.tokens.json'
```
