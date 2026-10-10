# Çin Eğitim — SVG round 01 (yalnız sembol)

Son SR PNG kullanıldı. Önceki silinmiş denemelerden geometri alınmadı; kilitli hedef/SR kaynağı değişmedi. Kullanıcı 2026-10-10 tarihinde `symbol.svg`'yi açıkça onaylayıp kilitlenmesini istedi. Tam kimlik/brand-system onayı değildir.

- `symbol.svg`: gerçek kübik Bézier yolları; halka ve pagoda/mürekkep zemini ayrı gruplar. Gömülü raster yok, tipografi yok. Şeffaf zemin.
- `symbol-mono.svg`: aynı yolların tek renk inceleme varyantı.
- `symbol-preview.png`, `symbol-2x.png`: gerçek SVG renderları.
- `source-sr.png`: kullanılmış SR kaynağının exact kopyası.
- `source-vs-svg.png`, `detail-brush.png`, `detail-pagoda.png`: gerçek render karşılaştırmaları.
- `manifest.json`: kaynak/çıktı hash'leri, araç sürümleri, parametreler, maske kapsama ölçümleri ve sınırlamalar.
- Kilit kaydı: `../../decisions/2026-10-10-symbol-svg-lock.md`; kanonik varlık: `../../assets/symbol.svg`.

## Tekrar üretim

Pillow + **Potrace 1.16** + `rsvg-convert` gerekir. Potrace: https://potrace.sourceforge.net/ (GPL-2.0-or-later; Peter Selinger). Resmî kaynak geçici yerel dizinde derlendi; dependency/binary/model kopyaları repoya eklenmedi.

```sh
python3 brands/cin-egitim/explorations/svg-round-01/build.py --potrace /path/to/potrace
python3 brands/cin-egitim/explorations/svg-round-01/package.py
python3 brands/cin-egitim/explorations/svg-round-01/verify.py
```

Yerel OpenCode tarifidir; pinned carousel Cloud recipe çalıştırılmadı, Linux byte-identical çıktısı iddia edilmiyor.

## Onay ve sınırlamalar

Tonal gölgeleme iki düz pigment rengine indirildi. Konturlar, fırça boşlukları ve pagoda açıklıkları SR kaynağından izlenmiştir. İnce uçlarda eşik/curve-fit yorumu vardır; piksel-birebir iddiası yok. Bu dosyanın SVG varlık kopyası kilitli canonical semboldür; geometriyi değiştirme. Düzeltme istenirse yeni, ayrı inceleme adayı üret ve insan onayı al. Kilit kararı PR'ı otomatik merge etmez.

Round klasörü kilit kararının görsel inceleme kaydıdır; production bundle değildir. Üretim CI checker'ı yalnız carousel formatını kapsar. `python3 studio/work/preflight.py --root . --brand cin-egitim` kilitli SVG hash'ini ve karar kaydının varlığını denetler; `verify.py` bu round'un dosya/SVG yapısını ve kanonik kopya eşitliğini kontrol eder. Genel audit mevcut üretim paketleri/hash anchor'ları ve tracked kaynakları denetler; insan görsel kabulünün yerine geçmez.
