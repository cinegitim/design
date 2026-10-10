# SVG round 01 — gerçek görsel inceleme

Gerçek görsel olarak okunanlar: SR kaynak, `source-vs-svg.png`, `detail-brush.png`, `detail-pagoda.png`. Potrace çıktısı `rsvg-convert` ile render edildi.

- **Korunan:** açık fırça halkasının hareketi, sağ üstteki ayrık kırmızı darbeler, iki çatı/kolonlar, pagoda açıklıkları, alttaki kırmızı/siyah mürekkep süpürmesinin negatif çizgileri.
- **Daha temiz:** büyük ölçekte Bézier kenarlar. SVG gömülü raster değil.
- **Açık fark:** hafif raster ton gölgeleri yerine örneklenen iki düz renk (`#BF0C1A`, `#202020`). Bu bir kontur/logo aktarımı; fotometrik PNG kopyası değildir.
- **Düşük önem:** çok ince uçlarda ve kırmızı/siyah birleşim noktasında eşik kaynaklı küçük boşluk/şekil değişimleri olabilir.
- **Yapılmayan:** 16 px kullanımı, tipografi, lockup ailesi, kanonik sistem veya üretim onayı.

Maske IoU'su yardımcı kontur ölçümüdür; tonu, kaynak detayının gerçekliğini veya insan onayını kanıtlamaz. Teknik değerler manifesttedir.

## HTML doğrulaması

Yerel HTTP önizlemesi gerçek browser sekmesinde açıldı. 1000 px viewport'ta yatay overflow yok; beş görselin tamamı yüklendi, yedi indirme/not linkinin tamamı HTTP 200 döndü. Browser screenshot aracı görünür desktop penceresi şartı nedeniyle başarısız oldu; HTML screenshot incelemesi veya 375/768/1440 responsive test iddiası yok. Sembol karşılaştırmaları yukarıdaki gerçek PNG girişleriyle incelendi.
