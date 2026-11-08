# Yalnız raster büyütme

Kullanıcı hedefin doğru olduğunu teyit etti ve önce kalitesini artırmamızı istedi.

- Kilitli `../reference/target-symbol.png` ve `target-lock.json` **değişmedi**.
- `target-symbol-6x.png`: 229×231 → 1374×1386 px; LANCZOS interpolasyon ve hafif netleştirme.
- `manifest.json`: kaynak/çıktı SHA-256 ve işleme parametreleri.
- Bu ayrı bir inceleme türevidir; yeni hedef, onaylı üretim logosu veya SVG değildir.
- Yeniden çizim, yapay zekâyla detay üretimi, renk/palet seçimi ve tipografi yok.
- İnterpolasyon kayıp ayrıntıları geri getirmez; yalnız büyük boyutta sunumu iyileştirir.

Tekrar üretim: `python3 studio/tools/cin-egitim/upscale_target.py`.

## Yeni talimat: yalnız büyütme değil, detay/kalite iyileştirme

Kullanıcı interpolasyonun yeterli olmadığını belirtti. `target-symbol-super-resolution-4x.png` ayrı bir **Real-ESRGAN süper çözünürlük adayıdır** (916×924 px).

- Yerel `realesrgan-x4plus` modeli kenarları ve yüksek frekanslı detayları tahmin eder; metin istemiyle logo çizdirilmedi.
- Kaynak ve hedef kilidi hâlâ aynen korunur. Tipografi, SVG ve tasarım geliştirme yok.
- Model, kaynakta belirsiz detayları tahmin ettiği için ince doku/kenarlarda değişiklik olabilir; çıktı otomatik onaylı/kanonik değildir.
- `super-resolution-manifest.json`: kaynak, çıktı, executable ve model hash'leri; açık yöntem ve sınırlama.
- `super-resolution-comparison.png`, `super-resolution-detail.png`: kaynak/önceki interpolasyon/yeni SR karşılaştırmaları.
- Grafik odaklı `x4plus-anime` geçici olarak incelendi fakat yüzeyleri daha fazla düzleştirip pagodaya kabartmalı kenarlar eklediği için kullanılmadı. Genel `x4plus` daha az stilize sonucu nedeniyle seçildi.

Tekrar üretim: `python3 studio/tools/cin-egitim/super_resolve_target.py --tool-dir <official-portable-tool-directory>`.
