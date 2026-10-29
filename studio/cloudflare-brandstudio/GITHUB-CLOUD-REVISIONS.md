# Brandstudio — tek editör ve güvenli otomatik kayıt (2026-10-29)

## Kullanıcı deneyimi

**Tek editör:** https://brandstudio-migration.pages.dev/visual-editor/browser/

Eski `cinegitim.github.io/design/visual-editor/` ve `/browser/` bağlantıları otomatik olarak tek Cloudflare editörüne yönlendirilir. GitHub Pages kaynak tasarımlar ve halka açık galeriler için durur; ayrı bir editör değildir.

**Giriş:** Cloudflare Access, yalnızca kişisel Cloudflare hesabının onaylı e-postası için izinlidir. Oturum süresi 168 saattir. Yeni sayfa açıldığında yeniden GitHub token girilmez; oturum gerektiğinde Cloudflare hesabıyla yenilenir. Access uygulaması tüm `/visual-editor` yolunu ve kayıt API'sini korur.

**Düzenleme:** Her değişiklik yaklaşık 1,4 saniyelik sakinleşmeden sonra otomatik kaydedilir. Görünür durumlar: Kaydedilecek, Kaydediliyor, Kaydedildi, Kaydedilemedi. Yalnızca sunucu D1 kaydını onaylarsa Kaydedildi denir. İnternet/çakışma sorunlarında geçici kurtarma anı tarayıcıda kalır, başarılı bulut kaydı diye gösterilmez.

**Sürümler:** Aynı v2 üzerine yazmak yeni v3 açmaz. `+ Yeni sürüm` isteğe bağlıdır; önceki anlar geri yüklenebilir. PNG ve JPEG doğrudan indirilir.

## Mimari ve güvenlik

- Cloudflare Pages `brandstudio-migration` tek UI origin.
- Pages Functions: `functions/visual-editor/api/revisions.js`, GET/POST `/visual-editor/api/revisions`.
- Cloudflare Access organizasyonu `Brandstudio Personal`; uygulama `Brandstudio Editor` yalnız kişisel e-posta için Allow. IdP `Personal Cloudflare Login` yalnız hesap üyelerine izin verir.
- Functions Access JWT `Cf-Access-Jwt-Assertion` imzasını JWKS üzerinden RS256 ile doğrular, `iss`, `aud`, `exp`, `iat` ve e-posta eşleşmesini kontrol eder. Yetkisiz talepler reddedilir; header varlığı tek başına güven sayılmaz.
- Same-origin POST, özel başlık, JSON biçimi, ürün kimliği, durum yapısı ve dosya büyüklüğü kontrolleri vardır. Yanlış beklenen sürüm etag'i ile yazma atomik CAS tarafından engellenir.
- Ayrı D1 veritabanı `brandstudio-editor`, tablo `editor_documents`; veri JSON'unda tüm sürüm anları saklanır. En çok 240 geçmiş anı / yaklaşık 950 KB belge. Eski `brandstudio-stage` veritabanına dokunulmaz.
- GitHub `cinegitim/design` kodun, onaylı logoların ve yayımlanmış kaynakların arşividir; editörün kullanıcısından GitHub PAT istenmez. Önceki `brandstudio-editor-history` dalı silinmez. Bavul v1/v2 tarihi D1'e taşındı.
- Ücretsiz Cloudflare Pages/D1/Access altyapısı tercih edilmiştir; R2, Workers AI ve ücretli render kullanılmaz. Ücretsiz kota aşımı için otomatik ücretli yükseltme yapılmaz.
- Üretim kaynak HTML'si ve kanonik logo değiştirilmez; editör kaydı sosyal medyada otomatik yayın değildir.

## Canlı doğrulama

CI, API sözdizimi, statik güvenlik ve arayüz testleri; canlıda Access reddi / yetkili erişim, geçmişi okuma, v2 değişikliği, yenileme, eski ana dönüş, PNG/JPEG, kullanıcı girişini yeniden istemeyen ikinci sekme ve GitHub Pages yönlendirmesi kontrol edilmelidir. Yetkili oturum test edilmeden uçtan uca kayıt kesin başarılı kabul edilmez.
