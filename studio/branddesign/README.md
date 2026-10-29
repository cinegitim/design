# Branddesign — Asya’da Eğitim Cloudflare altyapı grubu

Bu dizin **Branddesign** sistemine ait Cloudflare kaynaklarının tek envanter noktasıdır. Cloudflare hesabında fiziksel klasör bulunmadığından kaynakların adları ve bağlantıları `manifest.json` dosyasından izlenir. Kaynak kodu yeniden kopyalanmaz; halihazırdaki `studio/cloudflare-brandstudio/`, `docs/visual-editor/` ve `functions/visual-editor/` dizinleri esas alınır.

**Hedef:** `info@asyadaegitim.com` Cloudflare hesabı (`5f90104db6f24a941c04e974e250cb67`).

**Editör:** https://studio.asyadaegitim.com/visual-editor/browser/

**Kaynak:** `iakfiratt@gmail.com` hesabında eski kaynaklar sıfır veri kaybı doğrulanana kadar korunur. Aktif Bavul v2 kaydının dört geçmiş anı yeni Durable Object worker başlangıcına taşındı. Eski iki D1'in şeması aktarılmıştır fakat kaynak hesapta günlük D1 kota 7500 nedeniyle satırlar alınamamıştır. Bunlar TAM taşınmadan kaynak arşivler silinmeyecektir.

**Yayın:** GitHub `cinegitim/design` kod deposudur. Asya’da Eğitim'deki Pages projesi oluşturuldu, ancak Cloudflare'ın GitHub kurulumunda 8000011 hatası nedeniyle yeni hesabın GitHub bağlantısını yeniden yetkilendirmek gerekir. Bu yapılıncaya kadar yalnızca markalı Cloudflare Worker adresi üzerinden GitHub Pages'deki mevcut onaylı statik içerik proxy edilir. Tek editör ve özel kayıt API'si Asya’da Eğitim hesabında barındırılır.

**Güvenlik:** Yönetici Access kuralı yalnızca `info@asyadaegitim.com` ve `iakfiratt@gmail.com` e-postaları için; API tarafında Access JWT imzası da doğrulanır. Ücretsiz Cloudflare planı ilkedir; ücretli otomatik geçiş veya R2 açılmaz.

**Sınırlar:** Asya’da Eğitim'in `website`, `asya-imza-akis-v2` ve diğer mevcut Worker'ları, DNS ve sözleşme verileri bu göç kapsamında değiştirilmez.
