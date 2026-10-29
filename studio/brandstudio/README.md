# Brandstudio — Asya’da Eğitim Cloudflare altyapı grubu

Bu dizin **Brandstudio** sistemine ait Cloudflare kaynaklarının tek envanter noktasıdır. Cloudflare hesabında fiziksel klasör bulunmadığından kaynakların adları ve bağlantıları `manifest.json` dosyasından izlenir. Kaynak kodu yeniden kopyalanmaz; halihazırdaki `studio/cloudflare-brandstudio/`, `docs/visual-editor/` ve `functions/visual-editor/` dizinleri esas alınır.

**Hedef:** `info@asyadaegitim.com` Cloudflare hesabı (`5f90104db6f24a941c04e974e250cb67`).

**Editör:** https://studio.asyadaegitim.com/visual-editor/browser/

**Kaynak:** `iakfiratt@gmail.com` hesabında eski kaynaklar sıfır veri kaybı doğrulanana kadar korunur. Aktif Bavul v2 kaydının dört geçmiş anı yeni Durable Object worker başlangıcına taşındı. Eski iki D1'in şeması aktarılmıştır fakat kaynak hesapta günlük D1 kota 7500 nedeniyle satırlar alınamamıştır. Bunlar TAM taşınmadan kaynak arşivler silinmeyecektir.

**Yayın:** GitHub `cinegitim/design` kod deposudur. Asya’da Eğitim'deki Pages projesi oluşturuldu, ancak Cloudflare'ın GitHub kurulumunda 8000011 hatası nedeniyle yeni hesabın GitHub bağlantısını yeniden yetkilendirmek gerekir. Bu yapılıncaya kadar yalnızca markalı Cloudflare Worker adresi üzerinden GitHub Pages'deki mevcut onaylı statik içerik proxy edilir. Tek editör ve özel kayıt API'si Asya’da Eğitim hesabında barındırılır.

**Güvenlik:** Yönetici girişi `adminasya` uygulama hesabıyla yapılır. Önceki Cloudflare Access uygulaması, yeni oturumlar ve API doğrulandıktan sonra kaldırılmıştır. Bağımsız ve gizli Durable Object oturumları kullanılır. Ücretsiz Cloudflare planı ilkedir; ücretli otomatik geçiş veya R2 açılmaz.

**Sınırlar:** Asya’da Eğitim'in `website`, `asya-imza-akis-v2` ve diğer mevcut Worker'ları, DNS ve sözleşme verileri bu göç kapsamında değiştirilmez.

## Admin hesabı ve güvenilen bilgisayarlar (canlı)

**Durum:** `studio.asyadaegitim.com` üzerinden giriş canlıda doğrulandı. Ücretsiz Workers'ın 10 ms CPU sınırı nedeniyle PBKDF2 türetme tarayıcıda yapılır; sunucu tek kullanımlık nonce/HMAC imzasını ve kullanıcı adını doğrular. Giriş parolası ağ üzerinden sunucuya iletilmez.

- Kullanıcı adı: `adminasya`; şifrenin kendisi bu depoya **asla** eklenmez.
- Yeni Cloudflare Worker: `brandstudio-admin-auth`. SQLite-backed private Durable Object her bilgisayar/tarayıcı oturumunun rastgele 256-bit oturum anahtarının yalnız SHA-256 karmasını saklar.
- `brandstudio-edge` Worker `ADMIN_PBKDF2_SALT` ve `ADMIN_PBKDF2_HASH` adlı Cloudflare **Secret** değişkenlerini kullanır. PBKDF2-SHA256 210.000 tur tarayıcıda hesaplanır; sunucu yalnız kısa süreli ve bir kez geçerli HMAC doğrulama kanıtını kontrol eder. Salt açık, türetilmiş anahtar gizlidir. Hiçbir parola veya doğrulayıcı GitHub'da yayımlanmaz.
- Her tarayıcıda ilk kez oturum açılır; `__Host-brandstudio_session` çerezi `Secure; HttpOnly; SameSite=Lax; Path=/`, 365 gün süreli ve bitmeden son 30 günde otomatik yenilenir. Çerez silinirse veya farklı tarayıcı kullanılırsa yeniden giriş gerekir. IP/fingerprint ile gizli cihaz izlemesi yapılmaz.
- Login: `GET /admin/login` ve `POST /admin/login`, yetkisiz sayfalarda girişe yönlendirme, `GET /admin/session` oturum doğrulaması, `POST /admin/logout` oturumu geçersiz kılma. Brute force en fazla 6 başarısız giriş / 15 dakika / kaynak IP.
- Özel kayıt API'si ve editördeki statik dosyalar aynı oturum denetiminden geçer. Eski Cloudflare Access uygulaması güvenli doğrulamadan sonra kaldırılmıştır.

**Canlı doğrulama:** İlk admin girişi başarılı; tekrar yüklemede oturum devam ediyor; anonim API 401; yetkili API GET 200; aynı Bavul v2 durumuyla idempotent POST 200 ve `unchanged:true`; dört tarihçe anı ve revizyon kimliği değişmeden korundu. Eski Access uygulaması silindi. Kaynak kişisel Cloudflare hesabının D1 arşiv göçü ayrı ve henüz beklemede.

**Oturum sürekliliği:** Daha önce tanınan cihazların eski `__Host-branddesign_session` çerezleri geçiş sırasında otomatik olarak `__Host-brandstudio_session` biçimine yükseltilir. Mevcut Durable Object kimliği korunur, kayıtlar taşınmaz veya sıfırlanmaz.
