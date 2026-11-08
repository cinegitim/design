# Brandstudio — bütün üretimler için dosya-düzeyi indeks ve emeklilik protokolü

Durum: **Envanter ve karar hazırlığı. Henüz hiçbir içerik emekli edilmedi veya taşınmadı.**
Çalışma dalı: `feat/exhaustive-production-index-20261026`. Referans taraması: `cinegitim/design`, `main` Git ağaç SHA'sı `1caa29645737d0f2c57ef240d75c7e424bae2d3c` (2026-10-26).

## İndeksin kapsamı ve doğrulaması

- `docs/inventory/snapshot.json`: tam **3.500 Git blob**; satır başına kaynak yol, Git blob SHA-1, byte uzunluğu. 2.250 `docs/`, 1.055 `brands/`, diğerleri sistem kodu.
- `catalog.js`: **her dosyayı bir ve yalnız bir inceleme grubuna** yerleştiren kategori ve durum sınıflayıcısı. Dosya türü/rolü (`editable-source`, `render`, `manifest`, `version`, `dependency` vb.) ve sürüm izleri de korunur.
- `index.html`: marka, kategori, tasarım seçicisinde görünürlük, ön inceleme statüsü ve dosya yolu filtreleri; grup bazında tüm dosya ve hash ayrıntıları, karar önerisi dışa aktarımı. Tamamen statik ve ücretsizdir.
- Açık sayfa, GitHub `main` ağacına ulaşabiliyorsa **güncel ağacı** okur; ulaşamıyorsa eksiksiz sabit snapshot'a döner. Güncel ağaç ve snapshot SHA'sı UI'da açıkça gösterilir.
- Visual Editor seçicisi başlangıçta **27 paket** listeler; bu indeks daha geniş bir alanı kapsar. Bazı sürümler aynı inceleme grubuna bağlandığı için envanterde eşleştirilmiş grup sayısı 27'den az olabilir.
- Git blob SHA **Git'in içerik nesne kimliğidir**, SHA-256 değildir. Bağımsız arşiv taşıma doğrulamasında hem kaynak Git hash'i hem de dosya içeriği SHA-256 doğrulanmalıdır.

## Sınıflar

- **İlk arşiv adayı:** eski aşama/deneme/geçici yaratıcı üretim, henüz insan kararı yok.
- **Tek tek incelenecek:** basım, kampanya, son sürüm veya diğer çıktılar; bağlantı ve onay araştırması gerekiyor.
- **Üretim / gözden geçirme:** hali hazırda sunulan içerik, doğrudan sosyal medya yayın onayı anlamına gelmez.
- **Korumalı kaynak:** marka kimliği, manifesto/karar, onaylı logo, paylaşılan bağımlılıklar ve çalışan sistem.

Bu kurallar **tahmindir**, insanın vermiş olduğu bir onay veya nihai emeklilik kararı değildir. Özellikle `brands/asyada-egitim/assets` ve `brands/cin-egitim/assets` içindeki kilitli kimlik kaynakları, ortak logo varyantları, tipografi kaynakları, manifestler ve bağımlılık yapıları korunur. Aynı içerik birden fazla yolda bulunabilir; sadece SHA eşitliği silme izni vermez.

## Emeklilikten önce karar akışı

1. Envanter ekranından markaya göre filtrele; aile + bütün v1/v2/v3 + final ve PNG/SVG/HTML/ZIP/manifest ilişkilerini kontrol et.
2. Hangi **inceleme gruplarının ve varsa hangi sürümlerinin** pasifleşeceğine karar ver. Gerekirse bir grubun içinden yalnızca tek sürüm seçilir; toplu karar yüzünden referanslar kaybolamaz.
3. Canlı çalışma alanı, editör seçicisi ve dağıtılan `docs/` kaynakları arasındaki referansları denetle. Korumalı kaynakları veya aktif tasarımın kullandığı bir bağımlılığı emeklilik kümesine dahil etme.
4. Seçilen çıktıları ayrı GitHub arşiv deposuna, **kaynak yolunu, kaynak commit'ini, git blob SHA'sını, SHA-256 dosya özetini ve bağlı manifestlerini** koruyarak kopyala. Hedef repo adı/erişim politikasına karar verilmeden otomatik oluşturma.
5. Hedef depodaki **dosya sayısı, içerik boyutu ve checksum** doğrulanıp arşiv PR'ı birleşmeden **kaynak dosyalarını silme**.
6. Doğrulamadan sonra, kaynak repo içindeki sadece karar verilmiş ürün ID'lerini `retirement-decisions.json` üzerinden ana seçici ve çalışma alanlarından kaldır. Gerekiyorsa kamu URL'lerinde çalışan eski bağlantılara yönlendirme bırak.
7. Etkilenen marka galerilerini, arşivdeki tüm çıktıları, görselleri, mobil kırılımları, Cloudflare/GitHub Pages ve editörün kaynak/media erişimlerini test et. Her değişiklik PR + üç denetim + yayın sonrası kontrol ile tamamlanır.
8. Yanlış karar durumunda arşivdeki commit/hash ile kaynak yola **geri yükleme** ve ürünün yeniden etkinleştirilmesi ayrı PR ile yapılır.

**Bu sürümde henüz uygulanmayan işler:** hedef arşiv deposunun oluşturulması, dosya taşınması, ana seçiciden ürünlerin gizlenmesi ve URL yönlendirmeleri. Bunlar kullanıcı hangi üretimlerin emekli edileceğini belirledikten sonra gerçekleştirilecektir.

## Kapsam sınırı

Git `main` üzerindeki *halihazırda erişilebilir blob dosyalarını* eksiksiz kapsar. Git geçmişinden silinmiş dosyalar, otomatik oluşturulmuş ancak hiç commit edilmemiş dosyalar, yerel tarayıcının `localStorage` sürümleri, özel OpenCode/Work çalışma klasörleri ve bağlantısız dış servislerdeki görseller bu 3.500 sayısına dahil değildir. Böyle kayıtların bulunması için ikinci bir tarihsel/depolama taraması gerekir.
