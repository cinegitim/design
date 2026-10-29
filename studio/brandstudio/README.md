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

## Şifreli GitHub dış yedekleri

Cloudflare `brandstudio-edge` Worker'ında `BRANDSTUDIO_BACKUP_KEY` adlı rastgele 256 bit gizli anahtar saklanır. Yalnızca GitHub'ın resmî OIDC imzası doğrulanmış `cinegitim/design` deposunun `main` dalındaki `.github/workflows/brandstudio-offsite-backup.yml` işi, `/internal/backup?product=...` uç noktasını çağırabilir. Worker, Durable Objects belgesini dışarı göndermeden **AES-256-GCM** ile şifreler. İlgili uç nokta anonim istekler için HTTP 401 döndürür; tasarımın düz JSON'u bu uç noktadan verilmez.

GitHub Actions şifrelenmiş dosyaları yalnızca `brandstudio-editor-history` **arşiv dalına** `docs/visual-editor/browser/cloud-offsite-encrypted/` altına yazar. Aynı revizyon kaydedilmişse yeni commit oluşturmaz. Varsayılan zamanlama günde iki kez, UTC 05.17 ve 17.17'dir; elle `workflow_dispatch` ile de tetiklenebilir. Workflow OIDC, kısa ömürlü JWT ile çalışır; kullanıcı admin şifresi, uzun ömürlü PAT veya Cloudflare API tokenı GitHub Secrets içine konmaz.

**Çok önemli:** Bu GitHub deposu herkese açıktır. Yalnız şifrelenmiş veriler taşınır. Yedek anahtar dosyası GitHub'a yüklenmez; kullanıcının çevrimdışı saklaması gerekir. Anahtar kaybolursa Cloudflare hesabı da kullanılamadığında dış yedekleri çözmek mümkün olmayacaktır.

Çevrimdışı geri yükleme komutu (Node 22 veya üzeri): `node studio/brandstudio/backup/decrypt.mjs <sifreli-yedek.enc.json> <kurtarma-anahtari.txt> <cikti.json>`. Üretilen çıktı, aktif depolamaya kendi kendine yazılmaz; önce doğrulanır ve gerektiğinde kontrollü olarak içe aktarılır.

Canlı devreye alma kontrolü: GitHub Actions'ın ilk başarılı `archive` çalışması, `brandstudio-editor-history` dalına şifreli Bavul yedeği yazılması, aynı SHA için tekrar çalıştırmada commit oluşmaması, anonim /internal/backup -> 401. Bunlar tamamlanmadan dış yedekleme doğrulandı olarak işaretlenmez.

## 29 Ekim 2026 — Canlı yedek doğrulamaları

- GitHub Actions yedekleme çalışması: https://github.com/cinegitim/design/actions/runs/40957072762 — **başarılı**.
- `brandstudio-editor-history` dalında `docs/visual-editor/browser/cloud-offsite-encrypted/instagram-creative-breakout-bavul-001.enc.json` dosyası oluşturuldu ve kontrol edildi. Şifrelenmiş dosyanın revizyonu `0882e066-d82d-4d31-9d9f-5aac06b3b2ca` ve biçimi `brandstudio-aes256gcm-v1`.
- Yeni D1 `editor_revision_backups` tablosunda Bavul v2 dört geçmiş anı için bir snapshot ve ayrı test ürününün üç gerçek değişiklik/geri yükleme revizyonu doğrulandı. Düzenlemeler DO'da aynı kalıyor.
- Admin oturumu, canlı editör ve kayıt API'si başarılı. Anonim `/internal/backup` isteği 401 döndürdü.
- GitHub repo `cinegitim/design` public olduğu için dış yedekler sadece şifreli dosyalardan oluşur. Kullanıcıya verilen rastgele 256-bit kurtarma anahtarı **GitHub'a konmamıştır**.

## Son Cloudflare Pages–GitHub bağlantısı

Cloudflare API, hedef `brandstudio-asyadaegitim` Pages projesine `cinegitim/design` Git kaynağı bağlama denemesinde `8000011` döndürdü. Bu hata hedef hesabın Pages Git kurulumunun yeniden GitHub'da yetkilendirilmesini gerektiriyor. Cloudflare'ın Direct Upload proje türü mevcutsa, bu proje sonradan Git-entegre türe çevrilemez: Git yetkilendirmesi sonrasında **ayrı bir Git-entegre Pages projesi** oluşturulmalıdır. Otomatik build'ler ücretsiz kota için başlangıçta kapatılmalıdır.

Bu işlem tamamlanana kadar `studio.asyadaegitim.com` Worker'ı, GitHub Pages statik tasarımları güvenli geçiş olarak sunar; uygulama oturumu ve kayıtları yalnız Asya’da Eğitim Cloudflare hesabındadır. Eski kişisel hesabın `brandstudio-migration` Pages, Worker, D1, DO ve Access kaynakları **silinmez**. Yeni Pages kaynağı yayımlanıp aynı tasarım/baskı/oturum/kayıt testlerini geçtikten ve güncel tam yedekler doğrulandıktan sonra yalnızca Brandstudio kaynakları temizlenir; diğer kişisel Cloudflare uygulamaları korunur.
