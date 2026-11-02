# Brandstudio 3.0 — Modüler Çok-Ajanlı Tasarım Sistemi (Tasarım Şartnamesi)

**Tarih:** 2026-11-02  
**Durum:** APPROVED — 2026-11-02 tarihinde kullanıcı yaklaşım B'yi ve bu teknik şartnameyi onayladı. P1 uygulama planı ayrıca incelenir.  
**Kapsam:** `cinegitim/design` deposundaki mevcut Brandstudio sisteminin kesintisiz, aşamalı dönüşümü.  
**Dayanak:** 2026-11-02 salt okunur depo/Cloudflare incelemesi; `AGENTS.md`, `studio/production/`, `studio/work/`, `studio/cloud/`, `studio/cloudflare-brandstudio/`, `studio/brandstudio/`, `studio/workflow/PUBLISHING.md`, `brands/`, `docs/visual-editor/`, `.opencode/`, `.agents/`.

## 1. Amaç ve kullanıcının seçimi

Kullanıcı, Brandstudio'yu tek bir coding aracı veya modeline bağlı olmadan, birden fazla coding aracı/ajanın birlikte üretim yapabileceği; yaratıcı kalitesi yüksek, görsel olarak düzenlenebilir, teknik olarak doğrulanabilir, maliyet ve RAM/disk kullanımı kontrollü bir tasarım otomasyon sistemine dönüştürmek istiyor.

Değerlendirilen yaklaşımlar:
- **A — Mevcut yapıyı parça parça güçlendirme:** En az geçiş riski; fakat tekrar eden yolları ve ajanların farklı çalışma biçimlerini ortak sözleşmeye bağlamaz.
- **B — Modüler ortak çekirdek + değiştirilebilir executor adaptörleri (SEÇİLDİ):** Bugünkü GitHub/Cloudflare/marka kimliğini korur, bağımsız yürütücüleri standart iş ve teslim sözleşmelerine bağlar. Biraz kurulum ve geçiş disiplini gerektirir.
- **C — Sürekli açık tam otonom ajan kümesi:** Daha fazla otomasyon; ancak maliyet, güvenlik, bakım ve yanlış yayın riski yaratır. Şimdilik uygulanmaz.

**Tasarım kararı:** B, talep üzerine çalışan (*on-demand*), varsayılan olarak tek yürütücülü, kolay devredilebilir bir iş hattıyla başlar. Paralellik yalnız bağımsız işler için ve açıkça seçilince açılır. Bu bir yeni platform yazma projesi değil, mevcut bileşenleri ortak protokolle birleştirme projesidir.

## 2. Mevcut durum ve tespitler

- `AGENTS.md` ortak politika; `.opencode/` özgün ajan/komut/skill adaptörleri; `.agents/skills/` Work/Codex adaptörleri. `studio/production/router.py` ve `routes.json` zaten araç-kabiliyet temelli **read-only** aday yönlendirme yapıyor. `candidate-not-benchmarked` statüsü gerçek skorlamanın bulunmadığını doğru biçimde gösteriyor.
- `studio/cloud/` sabit üretim tarifi ve kaynak denetimi; GitHub Actions `audit / submitted-files` **render yapmadan** teslim edilen dosyaları denetliyor. Bu denetim estetik ya da piksel doğrulaması değildir.
- `studio/brandstudio/`, `studio/cloudflare-brandstudio/` ve `docs/visual-editor/` mevcut Cloudflare yönetici oturumu, editör revizyonları, yayınlanan statik dosyalar ve yedekleri içeriyor. `studio/publication-tracker/` yalnız isteğe bağlı yayın denetimi yapıyor. Çalışan sistemi değiştirmek ilk aşamanın konusu değil.
- `brands/asyada-egitim` onaylı H-02/V-01 kimliğine sahip; aynı adı andıran `brands/asya-egitim` farklı markadır. Asya'da Eğitim'in tam kanonik `brand-system.md` dosyası mevcut değil; eksiklik yeni onay varmış gibi kapatılamaz.
- 2026-11-02 Git tree incelemesinde 3.631 blob dosyanın toplam çalışma-ağacı boyutu yaklaşık 2,065 GB; ikili varlıklar yaklaşık %97,7; aynı blob SHA'ları farklı yollarla tekrar eden kopyaların **çalışma ağacında** yaklaşık 816 MB'lık fazladan yer kaplama potansiyeli var. Bu hesap Git'in fiziksel depoda aynı oranda tasarruf sağlayacağı veya güvenle silinebilecek byte miktarı anlamına gelmez.
- Canlı Cloudflare hesabında ilgili Workers/D1 ve Git bağlantılı Pages görüldü; `brandstudio-pages-git` üretim dağıtımı başarılı, publication Worker Cron listesi boş. `brandstudio-asyadaegitim` ayrı Pages projesi ve bazı eski belgeler/manuel deployment hedefleri ile mevcut statik origin arasındaki fark kontrollü envanter gerektiriyor.

## 3. Başarı tanımı, kapsam dışı ve kırmızı çizgiler

### Başarı
1. Aynı örnek brief, OpenCode veya Work/Codex yoluyla, aynı sürümlü **TaskSpec** ve **OutputManifest** sözleşmesini kullanarak, editlenebilir kaynak + gerçek render + doğrulama kanıtı üretmeli.
2. Görev el değiştirdiğinde yeni ajan önceki sohbet belleğini veya yerel cache'i zorunlu olarak gerektirmemeli. Yeterli referanslar ve gerçek SHA'lar handoff belgesinde bulunmalı.
3. Yeni üretimler yalnız ilgili kaynakları çekebilmeli; değişmemiş slaytlar mümkünse tekrar render edilmemeli; doğrulama yeni çıktı ile kaydedilen önceki çıktıyı ayrıştırmalı.
4. Mevcut katalog, editör sürümleri, yayın kanıtları, kimlik dosyaları, şifreli yedekler ve tarihi PR'lar kaybolmamalı.
5. Varsayılan işletim: **yeni ücretli servis yok; sürekli agent/VM yok; ölçülmeyen maliyet/performance iddiası yok**. Maliyet sınırı aşılacaksa otomatik API/fallback/retry yerine fail-closed.

### Kapsam dışı (ilk sürüm)
- Otomatik sosyal medya gönderisi, insan yerine estetik/logo onayı, editör/auth sisteminin sıfırdan yazılması.
- Evrensel her coding aracının otomatik uzaktan çalıştırılabileceği vaadi, mevcut olmayan erişim anahtarları/connector'ların kullanımı.
- Eski `brands/` ve `docs/` dosyalarını silmek, git geçmişini yeniden yazmak, R2 veya ücretli Cloudflare tarayıcı renderını zorunlu kılmak.
- ChatGPT'nin normal sohbet oturumunda bir Codex/Work/OpenCode ajanını görünmez biçimde başlatabileceği varsayımı.

### Değişmez kapılar
- Kurumsal onaylı SVG'lerin byte/manifest hash bütünlüğü; H-02 varsayılan, V-01/ilgili tam varyantlar ancak mevcut kullanım ilkelerine göre. C-03/D-04 yeni uygulamalarda kullanılmaz.
- Ajanın başarılı CI veya PR merge'i **görsel onay**, **kimlik onayı** ya da **sosyal paylaşım izni** değildir.
- Her üretim kendi branch/checkout'unda; exact-head CI ve mevcut PUBLISHING.md kuralı korunur. Açık kullanıcı hold'u her türlü otomatik birleşmeden üstündür.
- Yayımlanmamış özel brief'ler, erişim anahtarları, tokenlar ve kişisel dosyalar kamuya açık GitHub/Pages'a taşınmaz.
- Otomatik ücretli servis/fallback, kendiliğinden abonelik veya fatura üretimi yok.

## 4. Hedef sistem sınırları

```text
Kullanıcı / Brandstudio Control Center (mevcut site üstüne kademeli)
  → Job Planner (read-only: TaskSpec + capability probe + izinler)
  → Executor Adapter (OpenCode | Codex | ChatGPT Work | Antigravity | opsiyonel)
  → Handoff / Git branch & PR / artifact manifest
  → Ortak Production Core (kimlik, HTML/CSS/SVG, Chromium render, QA)
  → Kalite kapıları → kullanıcı kreatif kararı
  → onaylı teknik teslim/Pages doğrulama
  → sosyal yayın ANCAK ayrı açık yetkiyle; yayın denetimi ise isteğe bağlı
```

**Control plane:** Başlangıçta mevcut `studio/production/` içindeki salt-okunur router ve `studio/work/` handoff'ları. Merkez sürekli açık bir daemon veya yeni ücretli API değildir. Durum için mevcut GitHub branch/PR + editör revizyon kayıtları yeterlidir; yeni D1 tablosu ancak kalıcı görev kuyruğu zorunluluğu kanıtlanırsa eklenir.

**Data plane:** Ajanlar kendi ortamlarında kod, görsel kaynak ve render üretir. Cloudflare Worker içinde AI görüntü üretimi, Chromium veya terminal çalıştırılacağı varsayılmaz. GitHub kaynak/inceleme tarihçesi ve Cloudflare yetkili editör/derleme/yayın yüzeyleri ayrı kalır.

**Otorite zinciri:** `AGENTS.md` → marka `brand.json` / insan kararı / kanonik logo manifesti → uygulama spesifikasyonu + seçilen style → TaskSpec → yürütücü/provenance → teknik QA. Bir adapter marka veya onay otoritesi olamaz.

## 5. Ortak görev ve teslim sözleşmeleri

İlk iş, `studio/production/` altında **sürüm 1, JSON Schema ile doğrulanan**, küçük ve provider-bağımsız sözleşmeleri tanımlamak. Yapısal örnek (gerçek değerler iş anında doldurulur):

```json
{
  "schema_version": 1,
  "task_id": "brandstudio-unique-task-id",
  "brand_slug": "asyada-egitim",
  "category": "instagram-carousel",
  "brief_ref": "private-or-approved-reference",
  "base_sha": "40-char-commit-sha",
  "output_ref": "docs/instagram/example-family/v2",
  "style_id": null,
  "required_capabilities": ["filesystem", "browser-render"],
  "allowed_executors": ["opencode", "codex", "chatgpt-work"],
  "max_parallel": 1,
  "budget": {"currency": "USD", "new_paid_api": false, "image_calls_max": 0, "auto_retry": false},
  "approval": {"creative": "pending", "brand_identity": "inherit-approved-assets", "social_publish": false}
}
```

- `task_id` benzersiz; aynı task tekrar gönderildiğinde var olan kayıt üzerine körlemesine yazılmaz. `base_sha` kaynak snapshot'ını sabitler.
- `brief_ref` açık metin bir GitHub path olmak **zorunda değildir**; özel brief için yalnız erişim kontrollü referans kullanılır.
- `allowed_executors` listeye yazıldı diye kullanıma hazır sayılmaz; gerçek capability probe sonucu gerekir. `chatgpt-chat` için sadece gerçekten erişilebilir modül eylemleri.
- `budget` çağrı harcama sayacını tahminle doldurmaz; adapter mümkünse gerçek kota/maliyet telemetrisi verir, bilinmiyorsa `unknown` olarak işaretler. Sıfır yeni ücretli API varsayılandır.
- `output_ref` güvenli, kayıtlı repo alt yoludur; path traversal/uydurulmuş marka reddedilir.

Her executor için `CapabilityReport` (observed/unknown, evidence, generated_at, host), `TaskReceipt` (task, executor, branch, input SHA, changed files, actual tools, failures, returned refs) ve `OutputManifest` (editable source, original media, exact copy, source citations, selected canonical lockup + SHA, render outputs + dimensions + SHA, QA evidence, review state) gerekir. `output_ref` URL değil depo yolu; dış asset URL'si ayrıca allowlist ve kaynak belgesi ister.

**Durum makinesi:** `draft → ready → assigned → producing → prepared → technical_verified → creative_review → accepted → delivered`; herhangi üretim aşamasından `blocked` / `cancelled`; kreatif değişiklik `revision_requested` ile yeni immutable revizyona geçer. GitHub merge ile `creative_review` veya `accepted` otomatik oluşmaz. Sosyal medya `published` durumu yalnız ayrı, doğrulanmış kanıt kaydıdır. Geçişler kullanıcı/ajan aktörüne, timestamp'e ve kanıt ref'ine bağlı olmalı; geçersiz atlamalar testte reddedilmeli.

## 6. Ajan adapter'ları ve iş paylaşımı

**Adapter sözleşmesi:** `probe()` ortamda gerçekten mevcut araçları ve erişimi bildirir; `prepare(TaskSpec)` salt okunur uygunluk/preflight kontrolü yapar; `execute(TaskSpec)` ancak ilgili ortam ve açık yetki uygunsa üretime geçer; `handoff(TaskReceipt)` kalıcı dosya/SHA/PR verisini paketler; `verify(OutputManifest)` kanıtları denetler. Bu sözleşmeler her araçta aynı API'ye sihirli erişim varsaymaz; CLI, Work connector veya operatör destekli adaptörler farklı transport kullanabilir.

**İlk gerçek uygulama:** OpenCode + Work/Codex. Antigravity mevcut candidate profiliyle korunur fakat otomatik yürütme gerçek denemeye kadar `manual-handoff` düzeyindedir. ChatGPT normal chat, sadece görünür/gerçekte etkin araçlarını kullanır. Claude Code gibi gelecek kanallar ayrı opt-in adapter dosyası ve testle eklenebilir. Bir araç/kota düştüğünde otomatik pahalı alternatif yok; kullanıcıya alternatif uygun kanal önerilir.

**İş rolleri:** Kreatif yön (görsel gramer/brief), araştırma ve doğrulama (ilk kaynaklar, tarih/burs/fiyat), tasarım/kod (editlenebilir HTML/CSS/SVG), render (tam boyut), bağımsız QA (logo, metin, geometri, teknik görsel) ve teslim (PR/CI/Pages). Rollerin hepsine ayrı ajan çalıştırmak zorunlu değil; önce tek agent rol sırasını uygular. İki paralel iş ancak dosya yazım alanları ayrık, aynı kanonik dosyada edit yok ve görev başı kaynak kotası açık ise yapılır.

**Çakışma:** task branch ve output dizini tek writer; base/main SHA değişirse yeniden baz/PR inceleme; aynı marka/token veya katalog dosyasına eşzamanlı yazma lease/ayrı PR ile seri hale getirilir. Fail-closed; force-push yok.

## 7. Ortak tasarım üretim ve kalite yolu

1. Kategoriyi/markayı çöz; onaylı brand referanslarını küçük kapsamda oku. Style ailesi ayrı bir seçenek; review-only stil kanonik olmaz.
2. İçerik faktlarını birincil/son güncel kaynaklarla doğrula; sıralama, burs, kur dönüşümü ve son başvuru tarihi renderdan önce kaynak ve zaman damgasıyla tutulur. Kaynak yoksa kesin iddia yaratılmaz.
3. Kurumsal metni, raster içine yazdırmadan HTML/SVG olarak üret; fotoğraf/illüstrasyon yalnız ayrı katman. Onaylı logoyu tam SVG'den sonradan yerleştir.
4. Sabit sürümlü gerçek Chromium/Playwright ortamında render et; salt görüntü-gen sonucu editlenebilir karusel yerine geçmez. Daha önceki `studio/cloud/` render tarifi referans alınır; Mac'e sabit path kullanan tarihi `studio/engine/render.py` sessizce genel motor ilan edilmez.
5. **Doğrulama iki katmanlı:** CI'de değişmez kaynak/manifest/hash/ölçü/URL/secret/brand doğrulamaları; gerçek görüntünün açıldığı ortamda screenshot-piksel incelemesi (taşma, kapalı metin, logo alanı, okunabilirlik, görsel yoğunluk), gerekirse referans ile diff. Piksel ve estetik kararları salt metadata ile doğrulanmış sayılmaz.
6. Eski slaytlarla birebir aynı kaynak+asset+renderer hash'i varsa kontrollü render cache kullanılabilir; font/OS/Chromium farkında önceki PNG kimliği garanti edilmez. Cache hit/miss provenance kaydına girer. Önce cache olmadan doğru üretim baseline'ı gerekir.
7. Revizyon yeni ID/manifest ile yaşar; v1 özgün dosyalar ve editör cloud revisionları korunur. Önizleme/onay ile GitHub merge ve sosyal paylaşım birbirinden ayrı durumlardır.

### Kalite kontrol kabul örnekleri
- Marka slug benzerliği `asya-egitim` ↔ `asyada-egitim` ile kaynağı karıştırma girişimi durdurulur.
- Logo SHA yanlış/retired varyant; ölçü/clearspace ihlali → blok.
- Render edilmiş 1080×1350 görsel ile yalnız kaynak HTML arasında fark → blok veya açık inceleme.
- Tarihi geçmiş burs verisi → içerik incelemesi, yayın otomatik olmaz.
- CI başarı + estetik red → tasarım hâlâ review'da; yayınlanmış iddiası yok.
- Connector yok, rate limit, credential yok, cloud budget yetersiz → ücretli fallback veya otomatik retry yok; TaskReceipt `blocked` gerekçesiyle tamamlanır.

## 8. Depolama, performans ve maliyet

- **İlk adım salt okunur inventory:** SHA/size/path/kullanım bağımlılık haritası; hangi dosyanın referanslandığı, Pages bundle'a girip girmediği, Git tarihçesindeki rolü ölçülür. Tekrarlı dosya var diye silinmez.
- **Yeni üretimler için** paylaşılan asset library + hash referansı; Pages build sırasında gerektiğinde byte-koruyan yayın kopyası oluşturma. Tarihi içerik dokunulmaz. Depo geçmişinin büyüklüğü, checkout working tree, Pages upload byte ve CDN indirme ayrı metriklerdir.
- Büyük ZIP'ler için mevcut GitHub Release/Pages yönlendirme sistemi veya mevcut ücretsiz kapasite; yeni R2 otomatik açılmaz. Asset taşıma ancak izole pilot, eski URL yönlendirme/hashes ve rollback sonrası.
- Hız için reusable layout bileşenleri, kapsamlı sparse/partial checkout, cold archive ve yalnız değişen slaytları render etme. Dosya kopyası, CPU süresi, RAM, ağ ve model token tüketimi ayrı ölçülür. `README-LEAN-ENGINE.md` içindeki varsayımsal 300–400 token/6–10 sn değerleri benchmark olmadan SLA sayılmaz.
- **Varsayılan:** aynı anda 1 tasarım işi; kullanıcı iki bağımsız iş için izin verirse 2; task başına image/model çağrı sayacı isteğe göre; otomatik retry ve cron kapalı (mevcut onaylı şifreli yedekleme planını değiştirmez). Ücretsiz Cloudflare alt sınırlarını aşma riski hesabın güncel planıyla ayrıca kontrol edilir.

## 9. Kontrol paneli ve kullanıcı akışı (kademeli)

İlk ürün mevcut `studio.asyadaegitim.com` panelini yeniden yazmak değil, küçük bir **Görevler** görünümü eklemek. Her görev kartında: iş adı/marka, durum, hangi executor, mevcut kaynak/revizyon, oluşan görsel önizlemeler, son başarılı denetim ve varsa PR/engelleyici. Temel eylemler: **Hazırla**, **Uygun kanala devret**, **Önizle**, **Revizyon iste**, **Kreatif onayla**. Her eylem gerçekten çalıştığı kanala bağlanmalı; sembolik/no-op düğmeler yok. Cloudflare Worker yalnız oturumlu düşük maliyetli okuma/kayıt/intent yönlendirme yapmalı; render modelini veya yerel OpenCode'u çalıştırıyormuş gibi görünmemeli.

Yeni kontrol merkezi için ilk etapta ayrı D1 task veritabanı, WebSocket, Queue veya scheduled worker gerekmez. Gerçek ihtiyaç/ölçüm çıkarsa ayrı aşama olarak önerilir. Mevcut editor revision + publication proof yüzeylerine izinsiz yazılmaz.

## 10. Güvenlik ve mahremiyet

- En az yetki; okuma, branch oluşturma, PR açma, Cloudflare editörüne yazma ve sosyal yayın izni ayrı; otomatik iş atama yeni yetki yaratmaz.
- Public GitHub'a secret, erişim URL'si, cookie, özel brief, kurum içi fotoğraf veya mülkiyeti sınırlı materyal aktarımı yok. Connector hata raporları da secret maskeler.
- Task receipt'lerde model gerçek kimliği/araç kullanılabilirliği gözlemlenmediyse `unknown`. Harcama/tokens `measured` ve `estimated` olarak ayrı.
- Eski 365 günlük oturum yaklaşımına geçiş içinde müdahale yok; ayrı güvenlik değerlendirmesinde oturum süresi/iptal/cihaz listesi ve backup restore testi ele alınır.
- Cloudflare erişimi başka uygulamaların (imza sistemi, şirket sitesi vb.) kaynaklarına dokunma yetkisi anlamına gelmez.

## 11. Aşamalı dağıtım ve bağımsız başarı kapıları

**P0 — Şartname ve kontrollü baseline (bu belge):** Sistem envanteri, authority matrix, mevcut PR/main/Cloudflare kaynak snapshot'ı, pilot karusel ve başlangıç performans verisi. Üretim kodu ve canlı servis değişmez. Kullanıcının bu şartnameyi onaylaması uygulama kapısıdır.

**P1 — Ortak sözleşmeler ve read-only orkestrasyon:** JSON Schema, TaskSpec/CapabilityReport/Receipt/Manifest doğrulayıcı; mevcut router'ın geriye uyumlu schema adaptörü; uygun/uygunsuz executor senaryoları; yeni secret ve servis yok. Test: Aynı brief iki executor için tutarlı route/guard sonucu.

**P2 — Gerçek iki yürütücü pilotu ve handoff:** OpenCode ve Work/Codex, aynı küçük test brief için ayrı branch ve aynı OutputManifest üretir; hata/çakışma/capability unavailable davranışları ölçülür. Üretim kabul edilmeden önce gerçek browser render ve replay kanıtı gerekir.

**P3 — Üretim ve görsel QA standardizasyonu:** Tek pilot görsel ailede exact pixel/render + metin/geo/logo QA ve selective-render cache; eski v1/v2 korunur. Geçişi desteklemeyen eski üretimler legacy olarak görünmeye devam eder.

**P4 — Hafif görev paneli:** Mevcut yetkili panelde görev listesi ve gerçek durumlar; manuel üretim/handoff butonları; auth/CSRF/rol testleri, adım geri alınabilir. Task'ı başlatamayan executor için sahte otomasyon gösterilmez.

**P5 — Depolama/işletim optimizasyonu:** SHA bağımlılık raporu, salt okunur kullanımdaki tekrar ölçümü, bir yeni ürün ailesinde asset dedup pilotu, disk/network/render ölçümleri. Tarihi varlık silinmez; eski URL/karşılaştırma testlerinden sonra ayrı arşiv kararı verilir.

P1–P5 her biri ayrı şartname alt konusu, ayrı testli PR, ayrı geri alma yolu ve ayrıca kararlaştırılacak uygulama planıyla ilerler. Uygulamanın sırası P1 → P2 → P3 → P4 → P5; özellikle dosya temizliği ilk aşamada yapılmaz.

## 12. Göç, gözlemlenebilirlik ve rollback

- İlk sürüm shadow/advisory: mevcut `studio/production/router.py`, editör, Cloudflare Worker'ları, yayın takip sistemi çalışmaya devam eder; yeni task parser yalnız önerir.
- Her yeni task için kısa JSONL özet: task_id, executor, ölçülen toplam işlem süresi, tool call sayısı biliniyorsa, render boyutu/SHA, cache ve hata. Gizli prompt metni kaydetmez; ayrıntı yetkili workspace'te kalır.
- Başarılı iki farklı executor pilotu + geçerli visual QA + exact-head CI + canlı karşılaştırmalı doğrulama olmadan varsayılan üretim hattı yeni çekirdeğe değiştirilmez.
- Feature toggle `legacy` / `v3-advisory` / `v3-active`; başarısız koşulda önceki çalışan yöntem açık kalır. Dağıtım Cloudflare varsayılan origin'ini değiştirmek zorunda değildir.
- Hata durumunda task durdurulur; branch, çıktılar, orijinaller, cloud revision geçmişi, offsite backups korunur. Rollback artefaktı SHA ile ilişkilidir.

## 13. Builder self-check — iş sahiplerine açık kalan kararlar

Tasarım şu mevcut dosyaları referans alır: `studio/production/router.py`, `studio/production/routes.json`, `studio/production/BOOTSTRAP.md`, `studio/work/handoff-template.md`, `studio/cloud/audit.py`, `studio/cloud/policy.json`, `studio/workflow/PUBLISHING.md`, `studio/cloudflare-brandstudio/build_pages.py`, `docs/visual-editor/browser/`, `studio/brandstudio/manifest.json`.

Geliştirici varsayılanları: Python stdlib+JSON Schema destekleyecek test edilen validator, Node 22/Playwright mevcut sabit sürümlü runtime, GitHub PR taşıyıcı, Cloudflare yalnız mevcut ücretsiz API ve yetkili UI. Yeni dependency seçimi ve versiyon sabitlemesi P1 planında test edilecek; ücretli bağımlılık yok.

**Kullanıcı onayına sunulan tek mimari karar:** Öncelik mevcut marka üretim sisteminin bütünlüğü ve mevcut panelin devamlılığıdır; yeni görev arayüzü P4'e ertelenir. Kullanıcı görsel paneli P2'den önce isterse fazların sırası değişir ve tasarım yeniden gözden geçirilir.

**Onay kaydı:** Kullanıcı 2026-11-02 tarihinde “Onaylıyorum” diyerek bu mimariyi onayladı. P1 test-odaklı uygulama planı ayrı incelenir; uygulama kodu kendi izole PR'larında doğrulanır.
