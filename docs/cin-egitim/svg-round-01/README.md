# Çin Eğitim — SVG round 01 (yalnız sembol)

Son SR PNG kullanıldı. Önceki silinmiş denemelerden geometri alınmadı; kilitli hedef/SR kaynağı değişmedi.

- `symbol.svg`: gerçek kübik Bézier yolları; halka ve pagoda/mürekkep zemini ayrı gruplar. Gömülü raster yok, tipografi yok. Şeffaf zemin.
- `symbol-mono.svg`: aynı yolların tek renk inceleme varyantı.
- `symbol-preview.png`, `symbol-2x.png`: gerçek SVG renderları.
- `source-sr.png`: kullanılmış SR kaynağının exact kopyası.
- `source-vs-svg.png`, `detail-brush.png`, `detail-pagoda.png`: gerçek render karşılaştırmaları.
- `manifest.json`: kaynak/çıktı hash'leri, araç sürümleri, parametreler, maske kapsama ölçümleri ve sınırlamalar.

## Tekrar üretim

Pillow + **Potrace 1.16** + `rsvg-convert` gerekir. Potrace: https://potrace.sourceforge.net/ (GPL-2.0-or-later; Peter Selinger). Resmî kaynak geçici yerel dizinde derlendi; dependency/binary/model kopyaları repoya eklenmedi.

```sh
python3 brands/cin-egitim/explorations/svg-round-01/build.py --potrace /path/to/potrace
python3 brands/cin-egitim/explorations/svg-round-01/package.py
python3 brands/cin-egitim/explorations/svg-round-01/verify.py
```

Yerel OpenCode tarifidir; pinned carousel Cloud recipe çalıştırılmadı, Linux byte-identical çıktısı iddia edilmiyor.

## Onay bekliyor / sınırlamalar

Tonal gölgeleme iki düz pigment rengine indirildi. Konturlar, fırça boşlukları ve pagoda açıklıkları SR kaynağından izlenmiştir. İnce uçlarda eşik/curve-fit yorumu vardır; piksel-birebir iddiası yok. SVG kanonikleştirilmedi; otomatik merge yok.

Bu deney `studio/cloud/policy.json` içindeki ayrı `review_only_bundles` kaydındadır. Üretim CI checker'ı yalnız carousel formatını kapsar; kayıt bağımsız SVG-format CI kapsamı değildir. Yerel `verify.py` dosya/SVG yapısını kontrol eder. Genel audit mevcut üretim paketleri/hash anchor'ları ve tracked kaynakları denetler; insan görsel kabulünün yerine geçmez.
