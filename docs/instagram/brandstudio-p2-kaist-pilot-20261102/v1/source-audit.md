# KAIST V2 · Brandstudio P2 kaynak incelemesi

**Yürütme kanalı:** ChatGPT metin sohbeti + bağlı GitHub aracı (`chatgpt-chat`). **Bu çalışma OpenCode ya da ChatGPT Work çalıştırması değildir.**

**Durum:** P2 aktarımı için kaynak envanteri; tasarım üretimi, piksel incelemesi veya kreatif onay **değil**. Canlı tasarım dosyaları değiştirilmedi. Otomatik görüntü üretimi, ücretli API ve sosyal yayımlama kullanılmadı.

## Sabit kaynaklar

| Kaynak | Git blob SHA-1 |
| --- | --- |
| Ana depo görevi açılırkenki HEAD | `f44b775d9e52b736facf6d57706ffbf2b0e6ab69` (commit SHA-1) |
| `docs/instagram/kaist-tech-track-2027-001/v2/manifest.json` | `d4893dbb5f226d01d00bb57414ab67ea88fe3a99` |
| `docs/instagram/kaist-tech-track-2027-001/v2/source/03.html` | `c81d962850bfcaaf7da97179b05724f6538ba997` |
| `docs/instagram/kaist-tech-track-2027-001/v2/source/06.html` | `66d45715c882a60098f2139b760e1b2af52580c0` |

Git blob SHA-1 değerleri GitHub ağaç verisinden gözlendi; **içerik SHA-256'sı veya gerçek piksel denetimi yerine geçmez.**

## Kaynakta görülen tasarım kararları

- **3. slayt:** KAIST International Undergraduate Scholarship için `₩350.000` aylık destek ve `≈ 260 USD / AY` karşılığı 30.10.2026 tarihli yaklaşık değer olarak yazılmış. Sekiz dönem harç muafiyeti, sağlık sigortası desteği, `GPA 2,7 / 4,3` devam koşulu ve yaşam giderlerinin tamamını karşılamayabileceği uyarısı yer alıyor.
- **6. slayt:** Güz 2027 başvurusu için `14 OCAK 2027`, `10 KASIM 2026` açılış tarihi ve Türkiye saatiyle `12.00` metinleri var. Referans mektubunun ayrı teslim tarihinin kontrol edilmesi notu bulunuyor.
- İki slayt da onaylı H-02 imzasına `../../assets/h02-primary-horizontal-dark.svg` üzerinden referans veriyor.
- Kaynak V2 manifesti `in-review`, `creative_approved:false`, `social_published:false` durumunda. Altı düzenlenebilir HTML ve altı JPEG dışa aktarım listeleniyor.

Bu notlar **kaynakta ne yazıldığının tespitidir**; burs miktarlarının, kurun ve tarihlerinin güncelliği bağımsız olarak doğrulanmadı. Bu pilot hiçbir öğrenciye yayınlanacak bilgiye dönüştürülmemeli.

## Bir sonraki, gerçek OpenCode/Codex görevinde yapılacaklar

1. `publish/chatgpt-chat-brandstudio-p2-kaist-20261102` dalının değişmediğini ve kaynak HEAD'ini bağımsız GitHub/git komutuyla gözle.
2. Mevcut `studio/work/ephemeral.py` ile kendi **yeni ve bağımsız** çalışma dizinini oluşturarak yalnız bu sabit SHA'dan ayrılan bir görev dalı aç; önceki ajan dalına yazma.
3. Yeni, ayrı bir pilot çıktı alt dizininde en az bir gerçek düzenlenebilir HTML/CSS tasarımı üretmeden render/QA tamamlandı olarak işaretleme. Mevcut V2 HTML/JPEG'lerini güncelleme.
4. Gerçek ajan çalıştırma günlüklerini ve somut üretilen dosya SHA-256 değerlerini al, kanıtları P1 `TaskReceipt` ve P2 `HandoffEnvelope` ile eşleştir.
5. İnsan kreatif onayı ayrı kalacak; Instagram ve Cloudflare yayın eylemleri yasak.

## Güvenlik ve kapsam

Tek yürütücü, yeni ücretli API yok, `image_calls_max:0`, otomatik tekrar yok. Bu notun yazarı/kanalı `chatgpt-chat` olarak **bildirilmiştir**; GitHub araç eylemi bu sohbet içerisinde gözlendi, ancak bağımsız gerçek host attestation sağlanmadı. OpenCode/Work için **tamamlandı damgası yok**.
