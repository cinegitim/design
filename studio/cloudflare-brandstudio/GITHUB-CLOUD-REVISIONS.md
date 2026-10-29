# Brandstudio — tek editör ve güvenli otomatik kayıt (2026-10-29)

## Kullanıcı deneyimi

**Tek editör:** https://studio.asyadaegitim.com/visual-editor/browser/

Eski `cinegitim.github.io/design/visual-editor/` ve `/browser/` bağlantıları otomatik olarak tek Cloudflare editörüne yönlendirilir. GitHub Pages kaynak tasarımlar ve halka açık galeriler için durur; ayrı bir editör değildir.

**Giriş:** Cloudflare Access, yalnızca kişisel Cloudflare hesabının onaylı e-postası için izinlidir. Oturum süresi 168 saattir. Yeni sayfa açıldığında yeniden GitHub token girilmez; oturum gerektiğinde Cloudflare hesabıyla yenilenir. Access uygulaması tüm `/visual-editor` yolunu ve kayıt API'sini korur.

**Düzenleme:** Her değişiklik yaklaşık 1,4 saniyelik sakinleşmeden sonra otomatik kaydedilir. Görünür durumlar: Kaydedilecek, Kaydediliyor, Kaydedildi, Kaydedilemedi. Yalnızca sunucu Durable Objects kaydını onaylarsa Kaydedildi denir. İnternet/çakışma sorunlarında geçici kurtarma anı tarayıcıda kalır, başarılı bulut kaydı diye gösterilmez.

**Sürümler:** Aynı v2 üzerine yazmak yeni v3 açmaz. `+ Yeni sürüm` isteğe bağlıdır; önceki anlar geri yüklenebilir. PNG ve JPEG doğrudan indirilir.

## Mimari ve güvenlik

- Tek editör origin `studio.asyadaegitim.com`; Asya’da Eğitim Cloudflare `brandstudio-edge` Worker custom domain. Statik varlıklar geçici olarak `cinegitim.github.io/design` üzerinden proxy edilir.
- Pages Functions: `functions/visual-editor/api/revisions.js`, GET/POST `/visual-editor/api/revisions`.
- Cloudflare Access Asya’da Eğitim `Asyada Egitim Brandstudio` organizasyonudur; yalnız `info@asyadaegitim.com` ve `iakfiratt@gmail.com` yöneticileri yetkilendirilir.
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

## 29 Ekim 2026 — Asya’da Eğitim Cloudflare hesabına göç

Hedef hesabımız `info@asyadaegitim.com` (`5f90104db6f24a941c04e974e250cb67`). Kaynak kişisel hesabımız `iakfiratt@gmail.com` (`b462aa1499215378fe7f671a788c8a3c`). Bütün Cloudflare varlıklarının mantıksal envanteri `studio/branddesign/manifest.json` dosyasında tutulur. Kod ve onaylı tasarımlar `cinegitim/design` deposunda kalır.

Hedefte `brandstudio-edge` (tek origin `studio.asyadaegitim.com`), `brandstudio-editor-store` (Durable Object), `brandstudio-stage` (D1), `brandstudio-editor` (D1), Zero Trust Access kuruluşu/IdP/uygulaması ve `brandstudio-asyadaegitim` adlı ayrı Pages projesi oluşturuldu. Son etkin Bavul v2 belgesi, dört aktif tarihçe anı ve mevcut kayıt revizyonu yeni DO worker'ın başlangıç verisine işlendi.

Kaynak iki D1'in tabloları ve şemaları hedefte kuruldu; kaynak hesabın D1 günlük kota hatası (`7500`) nedeniyle içlerindeki satırların karşılaştırmalı aktarımı tamamlanmadı. D1 dışa aktarım işleri üretildi, ancak çıktı SQL dosyalarının hedefe alınması henüz doğrulanmadı. Bunun için kaynaklar silinmez.

Cloudflare Pages GitHub kurulumunda `8000011` hatası olduğundan, hedefte Pages projesinin GitHub entegrasyonu ayrıca yeniden yetkilendirilecek. Bu süreçte `brandstudio-edge` Worker, onaylı statik dosyaları GitHub Pages'den sunan geçiş köprüsüdür. Kayıt API'si ve saklama DO'su Asya’da Eğitim Cloudflare hesabındadır. GitHub Actions yalnız manuel çalışır ve kişisel hesabın eski deploy tokenını kullanmaz; yeni hedef token ayrı adla yapılandırılmalıdır.

Kaynak Cloudflare bileşenleri, güvenli kayıt yazma testleri ve veri eşitliği tamamlanana kadar korunur. Eski hesapta `brandstudio-` ile başlamayan hiçbir kaynağa müdahale edilmez.
