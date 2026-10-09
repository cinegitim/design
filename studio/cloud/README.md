# Brand Studio — Codex üretir, GitHub denetler

## Mimari

**GitHub kaynaklar → Codex Cloud üretim → kaynak/çıktı PR'ı → bağımsız dosya denetimi
→ insan görsel onayı → main → mevcut GitHub Pages yayını.**

| Görev | Nerede? |
|---|---|
| Brief, skill, marka sistemi, tarifler, fontlar, orijinaller ve tarihçe | GitHub repo |
| Tasarım, görsel araçlar, build/render, PNG/SVG/ZIP üretimi | Codex Cloud |
| SHA-256, kaynak/manifest, boyut, kanonik logo, paket, olası secret kontrolleri | GitHub Actions |
| Estetik/fidelity onayı, yeni kanonik logo kararı | İnsan |
| Onaylı/incelemelik çıktıların web sunumu | Mevcut Pages; Instagram'a otomatik gönderim yok |

Actions **render/build yapmaz**, üretici scriptleri import etmez, LLM/image API
çağırmaz ve OpenAI API anahtarı istemez. Python standart kütüphanesiyle teslim
dosyalarını okur. Pages'in mevcut deployment mekanizması değişmez.

## Başlangıç ve komutlar

Hesap bağlantısı için [ACTIVATION.md](ACTIVATION.md). Ortamın yayımlanması ve gerçek
Codex Cloud testleri hesap sahibi tarafından yapılmalıdır; repo hazırlığı bunu kanıtlamaz.

```sh
bash studio/cloud/setup.sh          # Kurulum; kampanya üretmez
bash studio/cloud/doctor.sh         # Codex'te araç/headless browser smoke testi
bash studio/cloud/build.sh launch-creative-02  # Yalnız istenmiş çıktı revizyonunda
python3 studio/cloud/audit.py --root .        # Salt okunur denetim; render yok
python3 -m unittest discover -s studio/cloud/tests -v
```

Python 3.12 / Node 22; Python üretim paketleri sabit sürümlü requirements,
Playwright npm lockfile ile kurulur. `librsvg2-bin` Linux dağıtım paketidir;
versiyonu doctor çıktısında kaydedilir. OS/font rasterizasyonu platformlar arasında
byte-identical çıktı garantilemez. Eski Mac çıktıları bu göçte yeniden üretilmez.

İlk taşınabilir tarif: `launch-creative-02`. Diğer tarihsel build'ler repoda korunur;
hepsinin Linux uyumluluğu bu kurulumla kendiliğinden kanıtlanmış değildir.
Eski OpenCode pluginleri/model isimleri Codex'e kurulu connector sayılmaz.

## Denetim kapsamı / yeni teslim kaydı

`policy.json` aktif teslimleri kaydeder. Başlangıçta son beşli carousel kayıtlıdır;
eski çalışmalar arşiv niteliğindedir. Yeni üretim bundle'ını aynı PR'da ekleyin.
Carousel-format bundle için manifest, slides, editable SVG/HTML, font, üretim
scriptleri, orijinaller, PNG, önizleme ve kaynak ZIP bulunmalıdır. Checker actual
hash, PNG yapısı/boyutu, görünür SVG metni, tam kanonik SVG referansı, minimum logo
boyutu, paket içerikleri ve yerel asset bağlantılarını denetler.

PR denetimi mevcut checker ve policy'yi **base commit'ten** alır; yeni teslimler
PR policy'sinden eklenebilir ama önceki kayıtlar sessizce çıkarılamaz. İlk kurulum
PR'ında base'de checker yoktur: bootstrap head checker kullanılır, bu istisna
logda görünür. Sonraki checker/policy değişiklikleri güvenlik/altyapı incelemesi ister.

Üreticinin render raporunu bağımsız render yerine saymayın: audit rapor tutarlılığını
okur, **rasterdaki logo pikselinin gerçekten doğru olduğunu, OCR doğruluğunu,
estetik kaliteyi veya tarifin birebir çalıştırıldığını kanıtlamaz**. Kaynakları
manifestle beraber değiştirerek elde edilen yeni çıktı teknik olarak tutarlı
olabilir; insanın önce/sonra görsel incelemesi yine gerekir.

Secret taraması bilinen credential örüntülerini ve riskli dosya adlarını denetler;
tam DLP/secret güvenlik garantisi değildir. GitHub secret scanning uygunsa ayrıca
açık tutulmalıdır. Hiçbir credential'ı loga veya repoya yazmayın.

## Koruma ve kalıcılık

Onaylı seal/lockup aileleri bağımsız hash anchor ile korunur. Aktif teslim dizininde
kopyalanmış canonical SVG'ler de exact hash ile denetlenir. Tarihsel experimental
W/smooth/weight-study çalışmaları korunur ama üretimde kullanılmaz.

GitHub kalıcı kaynaktır. Cloud task state ve CI artifact'leri geçicidir. Benzersiz
orijinal, editable source ve teslimi commit edin; büyük dağıtım paketlerinde Release
ve checksum indeksini birlikte kullanın. Arşivlenen eski yerel çalışma bir üretim
onayı veya yeni kanonik sistem değildir. Yerel dosyalar cutover kanıtlanmadan silinmez.
