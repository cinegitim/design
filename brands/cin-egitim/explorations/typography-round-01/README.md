# Çin Eğitim · Tipografi turu 01

Kullanıcının onayladığı sembol SVG'sini değiştirmeden, **12 ayrı yazı ailesi ve tipografik yerleşim** inceleniyor. Bunlar wordmark taslaklarıdır; hiçbiri kanonik logo, lockup ailesi, tam kimlik veya tipografi sistemi onayı değildir.

## Karşılaştırma panosu

`docs/cin-egitim/typography-round-01/index.html` on iki seçeneği aynı sayfada gösterir. Her biri için detay kartı da vardır:

| Yön | Ad | Yazı ailesi | Ana kurgu |
|---|---|---|---|
| A | Sessiz Kütüphane | Source Serif 4 | Yatay sembol, iki satırlı serif |
| B | Açık Rehber | Manrope | Ortalı dikey imza, tek satır sans |
| C | Program İndeksi | Barlow Condensed | Yatay, çizgiyle başlayan büyük harf bloğu |
| D | İnce Klasik | Cormorant Garamond | Yatay, tek satırlı yüksek kontrast serif |
| E | Yeni Nesil | IBM Plex Sans | İki ağırlıklı, iki satırlı grotesk |
| F | Arşiv Kaydı | IBM Plex Mono | İki satırlı monospaced kayıt düzeni |
| G | Yumuşak Karşılama | Nunito Sans | Sağda sembol, sağ hizalı yuvarlak sans |
| H | Dikey Vurgu | Oswald | Ortalı dikey, condensed büyük harf |
| I | Kültür Defteri | DM Serif Display | Üstte sembol, merkezî display serif |
| J | Açık Ufuk | Space Grotesk | Sembol sağda, açık aralıklı tek satır |
| K | Mektup Tonu | Lora | Sağda sembol, italik iki satır |
| L | Sağlam Rehber | Roboto Slab | Yatay, kalın slab-serif blok |

## Kilitli sembolün sınırı

Her lockup, `brands/cin-egitim/assets/symbol.svg` dosyasını (SHA-256 `1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381`) aynen kullanır. Sembolün yolları, kırpımı, oranı veya rengi değiştirilmedi; sembole yazı eklenmedi. Türkçe marka adı dışında İngilizce veya Çince metin kullanılmadı.

## Yeniden üretim / doğrulama

```sh
python3 brands/cin-egitim/explorations/typography-round-01/build.py
python3 brands/cin-egitim/explorations/typography-round-01/verify.py
```

HTML/CSS panosu Google Fonts üzerinden tipografi yükler. Görsel model çağrısı veya raster üretimi yapılmadı. Araştırma, risk ve tarayıcı testlerinin durumu `research.md`, `quality-review.md`, `handoff.md` dosyalarında.

## İnsan kararı

A–L arasından bir yön seçilecek; ardından yalnız seçilen yön optik boşluk, ağırlık, kerning ve uygulama testleriyle geliştirilecek. Seçimden önce kanonik wordmark veya `brand-system.md` oluşturulmayacak.
