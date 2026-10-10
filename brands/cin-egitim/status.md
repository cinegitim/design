# Çin Eğitim — sıfırlanmış çalışma

- Durum: **hedef referans ve kullanıcı onaylı sembol SVG'si kilitli**. Tam brand-system/kimlik kanonik değil.
- Hedef: `reference/target-symbol.png` — kullanıcının son paylaştığı Concept 03 panosundaki işaretin değiştirilmemiş kırpımı.
- Kapsam: kırmızı fırça halkası + siyah pagoda + mürekkep zemini. **Tipografi dahil değil.**
- Kaynak pano ve SHA-256 kaydı: `reference/target-board.png`, `reference/target-lock.json`.
- Önceki Çin Eğitim yönleri, SVG denemeleri, ölçümler ve üretici kodlar silindi. Git geçmişi yeniden yazılmadı.
- Kullanıcı yalnız büyütmenin yetmediğini belirtti ve gerçek görüntü temizleme/süper çözünürlük istedi. Ayrı `realesrgan-x4plus` kalite adayı (`enhancements/target-symbol-super-resolution-4x.png`) 916×924 px olarak hazırlandı. Önceki 6× interpolasyon yalnız karşılaştırma içindir.
- Kaynak/kilit değişmedi. `explorations/svg-round-01/` son SR PNG'den üretilen, kullanıcı tarafından onaylanıp kilitlenen path-only semboldür.
- Kanonik sembol: `assets/symbol.svg` — kullanıcı 2026-10-10'da SVG'yi onaylayıp kilitlememi istedi. SHA-256 ve karar `brand.json` / `decisions/2026-10-10-symbol-svg-lock.md` içinde kayıtlıdır.
- Sembol onayı tam brand-system veya identity approval değildir. PR #73 merge edildi; sembol site ana sayfası ve Çin Eğitim bölümünde yayında.
- Yeni kapsam: `explorations/typography-round-01/` içinde kilitli SVG ile birlikte üç tipografik/yerleşim denemesi; A/B/C kullanıcı seçimi bekleniyor. Hiçbiri wordmark olarak kilitlenmedi ve `brand-system.md` oluşturulmadı.
- Asya'da Eğitim'in ayrı, onaylı varlıkları değiştirilmedi.
