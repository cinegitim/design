# Çin Eğitim · Tipografi turu 01

Kullanıcının onayladığı sembol SVG'si değiştirilmeden, üç tipografi ve wordmark yerleşimi denemesiyle birlikte gösteriliyor. Bu tur kanonik wordmark, tam kimlik veya tipografi sistemi onayı değildir.

## Review

- `docs/cin-egitim/typography-round-01/index.html` — all three directions on one comparison board.
- `direction-a.html` — **Sessiz Kütüphane**, Source Serif 4 + Manrope; yatay, iki satırlı serif imza.
- `direction-b.html` — **Açık Rehber**, Manrope; sembol üstte, tek satır iki ağırlıklı isim.
- `direction-c.html` — **Program İndeksi**, Barlow Condensed + Manrope; yatay, kompakt büyük harfli imza.
- `manifest.json` records exact output hashes and the canonical logo hash.

Pano tarayıcıda yazı tiplerini Google Fonts üzerinden yükler; font ve ağırlık seçimi denemedir. Tipografiyi renkten bağımsız karşılaştırmak için üç yönde aynı kâğıt/mürekkep/kırmızı paleti kullanılır.

## Kilitli sembolün sınırı

Her sembol görseli `brands/cin-egitim/assets/symbol.svg` dosyasını (SHA-256 `1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381`) yolları, kırpımı, oranı ve renkleri değişmeden kullanır. Kilitli dosyaya tipografi eklenmez. Wordmark eskizleri yalnız HTML/CSS içindedir. Türkçe dışında dil eklenmemiştir.

## Regeneration / validation

```sh
python3 brands/cin-egitim/explorations/typography-round-01/build.py
python3 brands/cin-egitim/explorations/typography-round-01/verify.py
```

Sayfalar standart HTML/CSS ve Google Fonts kullanır. Görsel model çağrısı veya raster üretimi yapılmadı. `research.md`, `quality-review.md`, `handoff.md` dosyalarına bakın.

## Gate

İnsan A/B/C seçimi bekleniyor. Seçimden sonra yalnız seçilen yön geliştirilecek. Bu turda `brand-system.md`, kanonik wordmark/lockup veya site gezinmesine bağlantı eklenmedi.
