# Çin Eğitim — sıfırlanmış çalışma

- Durum: **yalnız hedef referans kilitli**.
- Hedef: `reference/target-symbol.png` — kullanıcının son paylaştığı Concept 03 panosundaki işaretin değiştirilmemiş kırpımı.
- Kapsam: kırmızı fırça halkası + siyah pagoda + mürekkep zemini. **Tipografi dahil değil.**
- Kaynak pano ve SHA-256 kaydı: `reference/target-board.png`, `reference/target-lock.json`.
- Önceki Çin Eğitim yönleri, SVG denemeleri, ölçümler ve üretici kodlar silindi. Git geçmişi yeniden yazılmadı.
- Kullanıcı yalnız büyütmenin yetmediğini belirtti ve gerçek görüntü temizleme/süper çözünürlük istedi. Ayrı `realesrgan-x4plus` kalite adayı (`enhancements/target-symbol-super-resolution-4x.png`) 916×924 px olarak hazırlandı. Önceki 6× interpolasyon yalnız karşılaştırma içindir.
- Kaynak/kilit değişmedi. Model detay tahmini yapar, ancak çıktı yeni hedef veya onaylı üretim logosu değildir. SVG izleme, logo yeniden tasarımı ve tipografi hâlâ kapsam dışı.
- Üretim logosu/kanonik SVG: yok. Referans kilidi, üretim logosu onayı değildir.
- Sonraki eylem: yeni süper çözünürlük adayını önceki yöntemle karşılaştırmalı göster; yeni talimatı bekle.
- Asya'da Eğitim'in ayrı, onaylı varlıkları değiştirilmedi.
