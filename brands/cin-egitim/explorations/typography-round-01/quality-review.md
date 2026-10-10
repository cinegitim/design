# Görsel kalite incelemesi — tipografi turu 01

## Genişletme kararı

- Önceki üç örnek aynı dar karşılaştırma alanında kalıyordu. Bu tur 12 yazı ailesini, sembolün yazıya göre üç konumunu (solda, üstte, sağda), tek/çift satırı, büyük harf, italik ve farklı harf aralıklarını kapsayacak biçimde genişletildi.
- A–L yalnız font adıyla ayrılmıyor: hizalama, satır sayısı, ağırlık, case ve lockup silueti de değişiyor. Ortak kâğıt/mürekkep/kırmızı rolleri renk değişiminin tipografik ayrımları maskelemesini önlüyor.
- Tüm 12 örnek kanonik sembol dosyasını kullanır; sembol geometrisi ve rengiyle oynanmadı. Hiçbirinde görüntü modeli veya raster kullanılmadı.

## Riskler

- **Yüksek — üretim kimliği değil:** Hepsi HTML/CSS yazısıdır; henüz harf aralığı/kerning optik olarak düzeltilmedi ve fontlar web'den gelir. Bir seçimden sonra yalnız o yönü özel olarak geliştirmek gerekir.
- **Orta — görünürlük:** Condensed (C/H), mono (F) ve geniş tracking (J) küçük kullanımda okunurluk kaybedebilir. Seçilen yön 16–24 px ve gerçek uygulamalarda sınanmalı.
- **Orta — ton:** A/D/I/K/L serif yönleri birbirinden ağırlık/kontrast/italik ile ayrılsa da marka için en uygun duygusal ton kullanıcı seçimiyle belirlenmeli; hiçbir stil kanonik sayılmaz.
- **Düşük — font teslimi:** Google Fonts bağlantısı çevrimdışı çalışmayabilir ve fallback ölçüleri değiştirir. Nihai lisans, subset ve statik/variable font dosyası seçilen yön için tekrar kontrol edilmeli.

## Gerçek kontroller / sınırlar

- Karşılaştırma panosu ve A–L'nin 12 detay sayfası tarayıcıda açıldı. 1000 px genişlikte her sayfada kanonik SVG ve ilgili Google Font yüklendi; yatay document taşması olmadı. Pano 12 kart/13 sembol görselini yükledi, kartlardaki lockup'ların tamamı önizleme kutularına sığdı.
- Tarayıcı screenshot aracı masaüstü sekmesini yakalayamadı. Görsel ekran görüntüsü incelemesi bu nedenle **tamamlanmadı**; gerçek tarayıcı render ölçümleri insanın estetik değerlendirmesinin yerini tutmaz.
- Mobil cihaz emülasyonu ve küçük boyut optik kontrolü yapılmadı.
- `verify.py` sembolün tam SHA-256 hash'ini ve 12 sayfanın kaynak hash'lerini denetler; estetik kaliteyi onaylamaz.
