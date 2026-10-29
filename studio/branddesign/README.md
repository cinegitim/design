# Branddesign — Asya’da Eğitim Cloudflare altyapı grubu

Bu dizin **Branddesign** sistemine ait Cloudflare kaynaklarının tek envanter noktasıdır. Cloudflare hesabında fiziksel klasör bulunmadığından kaynakların adları ve bağlantıları `manifest.json` dosyasından izlenir. Kaynak kodu yeniden kopyalanmaz; halihazırdaki `studio/cloudflare-brandstudio/`, `docs/visual-editor/` ve `functions/visual-editor/` dizinleri esas alınır.

**Hedef:** `info@asyadaegitim.com` Cloudflare hesabı (`5f90104db6f24a941c04e974e250cb67`).

**Editör:** https://studio.asyadaegitim.com/visual-editor/browser/

**Kaynak:** `iakfiratt@gmail.com` hesabında eski kaynaklar sıfır veri kaybı doğrulanana kadar korunur. Aktif Bavul v2 kaydının dört geçmiş anı yeni Durable Object worker başlangıcına taşındı. Eski iki D1'in şeması aktarılmıştır fakat kaynak hesapta günlük D1 kota 7500 nedeniyle satırlar alınamamıştır. Bunlar TAM taşınmadan kaynak arşivler silinmeyecektir.

**Yayın:** GitHub `cinegitim/design` kod deposudur. Asya’da Eğitim'deki Pages projesi oluşturuldu, ancak Cloudflare'ın GitHub kurulumunda 8000011 hatası nedeniyle yeni hesabın GitHub bağlantısını yeniden yetkilendirmek gerekir. Bu yapılıncaya kadar yalnızca markalı Cloudflare Worker adresi üzerinden GitHub Pages'deki mevcut onaylı statik içerik proxy edilir. Tek editör ve özel kayıt API'si Asya’da Eğitim hesabında barındırılır.

**Güvenlik:** Yönetici Access kuralı yalnızca `info@asyadaegitim.com` ve `iakfiratt@gmail.com` e-postaları için; API tarafında Access JWT imzası da doğrulanır. Ücretsiz Cloudflare planı ilkedir; ücretli otomatik geçiş veya R2 açılmaz.

**Sınırlar:** Asya’da Eğitim'in `website`, `asya-imza-akis-v2` ve diğer mevcut Worker'ları, DNS ve sözleşme verileri bu göç kapsamında değiştirilmez.

## Admin hesabı ve güvenilen bilgisayarlar (hazırlık)

**Durum:** Kod PR dalında test ediliyor; canlı Cloudflare gateway eski Access yapılandırmasıyla çalışıyor. Admin geçişi henüz etkin değil.

- Kullanıcı adı: `adminasya`; şifrenin kendisi bu depoya **asla** eklenmez.
- Yeni Cloudflare Worker: `brandstudio-admin-auth`. SQLite-backed private Durable Object her bilgisayar/tarayıcı oturumunun rastgele 256-bit oturum anahtarının yalnız SHA-256 karmasını saklar.
- `brandstudio-edge` Worker yalnızca `ADMIN_PBKDF2_SALT` ve `ADMIN_PBKDF2_HASH` adlı şifreli Cloudflare **Secret** değişkenlerinden parola doğrular. Şifre PBKDF2-SHA256 ile 210.000 tur hashlenir. Salt ve doğrulayıcı GitHub'da yayımlanmaz.
- Her tarayıcıda ilk kez oturum açılır; `__Host-branddesign_session` çerezi `Secure; HttpOnly; SameSite=Lax; Path=/`, 365 gün süreli ve bitmeden son 30 günde otomatik yenilenir. Çerez silinirse veya farklı tarayıcı kullanılırsa yeniden giriş gerekir. IP/fingerprint ile gizli cihaz izlemesi yapılmaz.
- Login: `GET /admin/login` ve `POST /admin/login`, yetkisiz sayfalarda girişe yönlendirme, `GET /admin/session` oturum doğrulaması, `POST /admin/logout` oturumu geçersiz kılma. Brute force en fazla 6 başarısız giriş / 15 dakika / kaynak IP.
- Özel kayıt API'si ve editördeki statik dosyalar aynı oturum denetiminden geçer. Yeni özel oturum kontrolü doğrulanmadan eski Cloudflare Access uygulaması silinmez.

**Etkinleştirme denetimi:** (1) İki Cloudflare Secret değerinin mevcut olduğunu doğrula; (2) özel auth Worker ve bağlantılarını kontrol et; (3) gateway'i yayımla; (4) `/admin/login` üzerinde gerçek kullanıcı oturum testi, kalıcı çerez, anonim API = 401, yetkili API GET/POST ve mevcut Bavul geçmişi eşitliği; (5) ancak bundan sonra eski `studio.asyadaegitim.com/visual-editor` Access uygulamasını kaldır; (6) tekrar anonim/oturumlu test. Giriş başarısızsa Cloudflare JWT gateway'ini geri yayımla. Login başarısız durumda sistemi korumasız bırakma.
