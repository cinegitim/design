# Brandstudio — ortak tarayıcı editörü

## Nasıl açılır
https://cinegitim.github.io/design/visual-editor/browser/

Üstteki arama/seçiciden yayımlanmış tasarımı seçin. Düzenleme, silme, gruplama, taşıma, font, fotoğraf, SVG metin içerikleri ve HTML/CSS/JPEG/PNG/SVG sürüm çıktıları tarayıcıda gerçekleştirilir. Farklı ürünler için `brandstudio:browser:<productId>` anahtarı ile birbirinden bağımsız yerel sürümler tutulur. Arşiv JSON'ları ayrıca dışa aktarılıp içe alınabilir; buluta düzenleme gönderilmez.

## Bütün eski ve gelecekteki ürünlerin otomatik keşfi
- Katalog `docs/visual-editor/browser/catalog.json` içinde mevcut public kaynaklarla önceden doldurulur.
- Açılışta GitHub'ın **public, read-only** repository tree endpoint'i alınabilirse katalog otomatik güncellenir; rate limit, çevrimdışılık veya ağ hatasında statik snapshot kullanılır.
- Cloudflare Pages'in mevcut statik free-only deploy paketleyicisi, her deploy anında tüm `docs/` dosyalarından snapshot'ı otomatik yeniden oluşturur.
- Yeni HTML kaynakları: `docs/<kategori>/<ürün>/source/*.html` ya da `editable/*.html`. Bunlar kaynak katmanları korunarak açılır; 25 sayfaya kadar tek paket.
- SVG içeren kaynak HTML: metin, seçilebilir gruplar ve görsel nesneler tarayıcıda ayrı seçilebilir. HTML dışına/tuval dışına çıkıldığında nesneler kaybolmaz.
- Tek başına resim varlıkları: `docs/` altındaki yayımlanmış PNG, JPG/JPEG, WebP veya SVG. 25 dosyalık paketler halinde kataloglanır. PNG/JPEG içindeki pikseller gerçek yazı katmanları değildir; tüm görsel nesnesi üzerinde çalışılır.
- Hazır `.slide` kaynaklarında eski carousel-01-v3 anahtarları ve eski sürüm arşivleri korunur.
- Genel HTML tekil tasarımlar (roll-up, banner vb.) kendi ölçüleriyle normalize edilir ve kaynak dosyalar değiştirilmeden düzenlenir.

## Düzenlenebilir tasarımların seçimi

Katalog **çalışma dosyalarına** odaklanır. `source/*.html`, `editable/*.html` ve gerçekten üretilmiş bağımsız baskı tasarımları birer ürün olarak açılır; çok sayfalı üretimlerin tüm sayfaları aynı üründe görünür. Katman kaynakları olmayan nihai PNG/JPEG/SVG çıktılar görsel olarak açılır. `typography-round-01/direction-a.html` gibi **tasarım yönü karşılaştırmaları**, test/inceleme panoları, fotoğraf orijinalleri, fontlar, ara renderlar ve logo kaynak depoları tamamlanmış tasarım olarak listelenmez. Böylece başka bir ürünü açtığınızda karşılaştırma sitesi değil, seçilen gerçek çalışma açılır.

Eski `/visual-editor/?product=...` adresleri tarayıcı editörüne yönlendirilir; localhost üzerinde ikinci bir editör açma seçeneği siteden kaldırılmıştır. Yeni bir üretim çıktısının ayrı katmanlarla açılabilmesi için gerçek HTML/CSS/SVG kaynaklarının yayımlanması gerekir. Render edilmiş tek parça bir görselin var olmayan katmanları geri üretilemez.

## Sınırlar ve korumalar
Bu işlem yalnızca yayımlanmış görsellere erişir; özel git dalına, yerel Mac dosyasına ve henüz commit edilmemiş tasarıma otomatik erişim yoktur. Dışa aktarım HTML/CSS ve JSON'dur; PNG ekran görüntüsü veya PSD/PDF'nin orijinal katmanlarını editör kendiliğinden yeniden oluşturmaz. Raster-only içeriklerde var olmayan yazı katmanları uydurulmaz. Kaynak SVG, kabul edilmiş logo/lockup içeriği ve özgün render arşivleri korunur. Otomatik GitHub commit'i veya ücretli Cloudflare servisi yoktur. Kaydettiğiniz tarayıcı sürümleri, aynı tarayıcının kendi depolamasındadır.

## Üreticiler için
Her teslimatın gerçek düzenlenebilir kaynaklarını da yayımlayın. `AGENTS.md` ve `studio/production/BOOTSTRAP.md` üretim sözleşmesinin ilgili paragraflarını okuyun. Yeni bir ürün için ek editör JS'ı, manuel kayıt veya ücretli backend kurulmaz.

## Ortak tasarım dili seçimi (GitHub sözleşmesi)

Visual Editor sağdaki **Tasarım dili ve varyasyonlar** panelini açın. Kategori → kayıtlı tasarım dili → alt varyasyon → kanonik logo ve isteğe bağlı ince ayarları seçin. Mevcut sürümü görsel olarak otomatik değiştirmez; sonraki üretimin *niyet kaydıdır*. Kullanılabilir tek aile şu anda `asyada-egitim / instagram-carousel / editorial-campaign v0.1.1` olup **review-only** statüsündedir. Kayıtlı dört preset vardır; diğer kategoriler açıkça “stil yok” gösterilir. H-02/P-01 SVG dosyaları, Jost ve kurumsal renkler GitHub kanonik sözleşmesiyle eşleşir.

**Seçimi sürüme kaydet**, editörün mevcut Cloudflare Durable Object sürüm durumuna `designStyle` bilgisini ekler. Otomatik kayıt, çakışma (409), geçmişe dönüş, arşiv içe/dışa aktarma ve 26 sürüm sınırı aynen geçerlidir. Kaydetme yalnız Cloudflare'da başarılı dönüş aldıktan sonra “✓ Kaydedildi” der. Önceki sürümlerde `designStyle` bulunmayabilir; bu normaldir ve stil tahmini yapılmaz. Cloudflare Access ve mevcut ayrı admin oturumu gereklidir.

**GitHub üretim fişi ↓** yalnızca `*-production-brief.json` indirir; GitHub'a doğrudan commit/PR göndermez, böyle bir iddiada bulunmaz. Sonraki adımda görev alan ajan bu fişi `studio/production/style_pack.py` ile doğrular, kendi GitHub dalında düzenlenebilir HTML/CSS/SVG ve gerçek sürüm PR kaydını oluşturur. Böylece bulut taslağı ile doğrulanmış GitHub üretim sürümü karıştırılmaz. İnsan kreatif onayı ve sosyal medya yayın izni bağımsızdır; sadece stil seçilmesi hiçbir şeyi yayınlamaz.

Şu anda otomatik GitHub PR gönderen bir sunucu işlevi mevcut değildir; bu yetki ayrıca, sunucuda saklanan yetkili kimlikle ve geri alınabilir bir iş akışıyla kurulacaktır. Erişim korumalı `studio.asyadaegitim.com` editörü ile herkese açık `pages.dev`/GitHub Pages statik tasarım kaynaklarını birbirine karıştırmayın.
