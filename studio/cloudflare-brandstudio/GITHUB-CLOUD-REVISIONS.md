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
- Aktif kayıt sistemi: `brandstudio-editor-store` SQLite-backed Durable Object (`BRANDSTUDIO_OBJECTS` Pages binding). Ürün başına tutarlı ve atomik kayıt. D1 tabloları sadece eski geçiş arşivi olarak korunur; günlük kayıtta kullanılmaz.
- GitHub `cinegitim/design` kodun, onaylı logoların ve yayımlanmış kaynakların arşividir; editörün kullanıcısından GitHub PAT istenmez. Önceki `brandstudio-editor-history` dalı silinmez. Bavul v1/v2 tarihi D1'e taşındı.
- Ücretsiz Cloudflare Pages/D1/Access altyapısı tercih edilmiştir; R2, Workers AI ve ücretli render kullanılmaz. Ücretsiz kota aşımı için otomatik ücretli yükseltme yapılmaz.
- Üretim kaynak HTML'si ve kanonik logo değiştirilmez; editör kaydı sosyal medyada otomatik yayın değildir.

## Canlı doğrulama

CI, API sözdizimi, statik güvenlik ve arayüz testleri; canlıda Access reddi / yetkili erişim, geçmişi okuma, v2 değişikliği, yenileme, eski ana dönüş, PNG/JPEG, kullanıcı girişini yeniden istemeyen ikinci sekme ve GitHub Pages yönlendirmesi kontrol edilmelidir. Yetkili oturum test edilmeden uçtan uca kayıt kesin başarılı kabul edilmez.

## 29 Ekim 2026 D1 ücretsiz kota kesintisi

29 Ekim'de kişisel Cloudflare hesabındaki hesap-geneli D1 satır-okuma ücretsiz kotası doldu (Cloudflare hata 7500). Bavul v2 tarayıcıdaki dört düzenleme, GitHub arşivine silmeden `emergency-recovery-20261029133229502` anı olarak kurtarıldı (commit `3fb09e50a645d7662ba099e7d01c169a6cdb5800`). İlk Durable Object GET işlemi public GitHub arşivinden o son durumu yükler; mevcut Chrome sekmesinin beklediği `legacy-v2` revizyonunu koruyarak ilk POST'un kayıp üretmeden geçmesini sağlar. Sonrasında tüm GET ve POST işlemleri JWT-doğrulanmış Pages Functions üzerinden nesne depolamaya gider. Başka oturumda eşzamanlı yazma karşılaştırmalı revizyonla reddedilir. D1, yeni editör kayıtlarının çalışma zamanı bağımlılığı değildir.

Durable Objects Workers Free planındaki ayrı kotalara bağlıdır; limit aşılırsa ücretli yükseltme yapılmaz, hata ve kurtarma durumu gösterilir. Cloudflare Workers/DO tüketimi ayrıca izlenmelidir.
