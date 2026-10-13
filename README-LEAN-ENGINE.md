# Lean Production Engine v2 (Hızlı & Düşük Tokenlı Üretim Motoru)

Bu versiyon dalı (`lean-production-v2`), var olan karmaşık ve aşırı token tüketen (25.000+ token) pipeline'ı sadeleştirerek, **yüksek hızlı ve son derece düşük maliyetli (~350 token)** bir üretim sistemine dönüştürmek amacıyla oluşturulmuştur.

## 🚀 Temel Avantajlar

| Özellik | Eski Sistem | Lean Engine v2 |
|---|---|---|
| **Token Tüketimi** | ~25.000 – 30.000 token / çıktı | **~300 – 400 token / çıktı** (%98 tasarruf) |
| **Üretim Süresi** | 10 – 15 dakika | **6 – 10 saniye** |
| **Model Kotası** | 2 üretimde kota biter | Sınırsız üretim (küçük/hızlı modellerle dahi kusursuz) |
| **Dosya Kalabalığı** | Her carousel için 8 ayrı script/manifest | Tek bir JSON girdisi, sıfır çöp |
| **Görsel Tutarlılık** | CSS/SVG kayma riski var | Sabit tipografi (Jost), kilitli logo ve kurumsal ızgara |

## 📦 Desteklenen Tasarım Formatları

1. **Instagram Carousel (1080x1350 px):** 4:5 dikey slaytlar (Kapak, Maddeler, Rotalar, CTA).
2. **Fuar Roll-up Banner (85x200 cm):** Yüksek çözünürlüklü fuar standı görseli.
3. **A5 El İlanı (Flyer - 148x210 mm):** Ön ve arka yüz fuar bilgilendirme ve burs tablosu.
4. **Kurumsal Kartvizit (85x55 mm):** Ön yüz iletişim, arka yüz prestij kimliği.

## 🛠 Kullanım

### OpenCode Üzerinden:
OpenCode'da sadece şu komutları kullanabilirsiniz:
- `/hizli-carousel <konu>`
- `/hizli-rollup <konu>`
- `/hizli-flyer <konu>`
- `/hizli-kartvizit <isim, unvan>`

### Doğrudan Terminal / Python ile:
```bash
python3 studio/engine/render.py --type carousel --input studio/engine/sample-carousel.json --output docs/review/sample-carousel/
```

Üretilen tüm tasarımlar doğrudan `docs/review/` altına kaydedilir ve `index.html` önizleme galerisi ile GitHub Pages üzerinden anında görüntülenebilir.
