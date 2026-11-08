# Visual Editor · İçerik ve ortak tarz gezinmesi

Kullanıcının onayladığı beş aşama: **Ana kategori → İçerik alt kategorisi → Ortak tarz → Tarz çeşitlemesi → Tekil ürün**. Marka bu ağacın üstünde, kaynak v1/v2/v3 ve Cloudflare kayıtları ise ürünün içinde durur.

## Tek katalog, iki yol

- **İçeriğe göre**: Karuseller → Üniversite Tanıtımları → Data Atlas → Metrik Atlası → ilgili ürünler.
- **Tarza göre**: Data Atlas → Metrik Atlası → Üniversite Tanıtımları / Burs Rehberleri / Şehir ve Öğrenci Yaşamı → ilgili ürünler.
- Stil, kendine ait kanonik `style.json` ile sadece bir kez tanımlanır; kategori/ürün bağlantıları bu kimliği referans alır. Yeni bir alt kategori oluşturmak yeni bir tarz kopyalamayı gerektirmez. Aynı ürün farklı doğrulanmış kaynak sürümlerinde farklı tarzlar kullanabilir ve her iki tarafta görünebilir; dosyalar veya ürün kimlikleri kopyalanmaz.

## Mevcut kaynakların görevleri

- `docs/visual-editor/browser/product-groups.json`: ürün aileleri, sürümleri, mevcut yayın kanıtları ve arşiv; **değişmedi**.
- `docs/visual-editor/browser/navigation-classification.json`: 18 mevcut ürünün içeriksel ana/alt kategorileri ve gelecekte üretilebilecek tarzlar için **öneriler**. Bu öneriler eski kaynak tasarımının gerçekten aynı tarzda olduğunu ispatlamaz.
- `docs/visual-editor/browser/style-registry.json`: mevcut kaynak-manifest bağlantıları; ayrı kategori altlarında ortak tarz kimlikleri.
- `docs/visual-editor/browser/catalog-navigation.js`: bu üç veri kaynağını birleştiren, yalnızca okuyan, marka/alt kategori/tarz/çeşitleme ve sürüm bağlantılarının tutarlılığını kontrol eden indeks.
- `docs/visual-editor/browser/catalog-navigator-ui.js`: içeriğe veya tarza göre gezinme, filtre, sıralama ve mevcut ürünü açma. Editörün asıl tuvali ve kayıt hizmeti değişmez.

## Kesinlik seviyeleri

- **Öneri / future-design**: gelecekte üretilecek bir tasarıma yön veriyor; geçmişin görsel tarzı diye gösterilemez. Başlangıçta 13 karusel için var, 5 diğer ailede tarz önerisi tanımlı değil.
- **Çalışma alanındaki seçim / draft**: yalnızca o anda açılmış Visual Editor sürümünün `state.designStyle` alanında; onay veya GitHub kaynak-sürüm eşleştirmesi değil. Kullanıcı buluta kaydederse ilgili ürünün kendi Cloudflare geçmişinde kalır; başka ürünleri okumak için periyodik istek yapılmaz.
- **Doğrulanmış kaynak sürümü / verified**: isteğe bağlı `confirmedVersions[]` bağlantısı; ilgili ürün ailesi, gerçek kaynak sürüm ID'si, o marka ve ürün formatında kayıtlı tarz/preset ve ayrıca kaynak kanıtı zorunlu. Kaynak PR/commit bağlantısının gerçekten ilgili ürüne ait olduğunu bir insan/denetim süreci kontrol etmeden kayıt eklenmemelidir. Başlangıçta **0**.
- **Tarzı belirlenmemiş**: mevcut kayıtlarda doğrulanmış veya önerilmiş bir tarz bağlantısı yok.

## Ekleme ve geliştirme

Yeni ürün geldiğinde öncelikle `product-groups.json` içindeki benzersiz ürün ve kaynak-sürüm ilişkisini koru, sonra `navigation-classification.json` içinde içerik kategorisini belirt. Kullanıcının açıkça seçmediği veya görsel denetimden geçmeyen tarzı `confirmedVersions` içine ekleme. Yeni tarz gerekiyorsa `brands/<brand>/styles/<format>/<style>/style.json` kaynağını oluştur; iki statik stil kataloğunu `studio/production/style_registry_sync.py --write` ile eşitle ve test et.

Gezinti ek API, Worker, bulut veritabanı, devamlı izleme, model çalıştırma, GitHub yazma, görsel üretim veya otomatik yayın başlatmaz. İçerik ve tarz filtreleri yalnızca tarayıcıda çalışır. Ekrandaki tüm kartlar mevcut kaynak ürüne yönelir; birinci sınıf tasarım sürümleri ve yayın kanıtları önceki mekanizmadadır.
