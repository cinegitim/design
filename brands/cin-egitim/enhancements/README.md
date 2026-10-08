# Yalnız raster büyütme

Kullanıcı hedefin doğru olduğunu teyit etti ve önce kalitesini artırmamızı istedi.

- Kilitli `../reference/target-symbol.png` ve `target-lock.json` **değişmedi**.
- `target-symbol-6x.png`: 229×231 → 1374×1386 px; LANCZOS interpolasyon ve hafif netleştirme.
- `manifest.json`: kaynak/çıktı SHA-256 ve işleme parametreleri.
- Bu ayrı bir inceleme türevidir; yeni hedef, onaylı üretim logosu veya SVG değildir.
- Yeniden çizim, yapay zekâyla detay üretimi, renk/palet seçimi ve tipografi yok.
- İnterpolasyon kayıp ayrıntıları geri getirmez; yalnız büyük boyutta sunumu iyileştirir.

Tekrar üretim: `python3 studio/tools/cin-egitim/upscale_target.py`.
