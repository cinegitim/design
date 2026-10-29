# Brandstudio — GitHub bulut sürümleri (2026-10-29)

## Nerede saklanır?

Tarayıcıdaki çalışmalar **kalıcı değildir**. Bulut yazma modu, `cinegitim/design` deposunda **`brandstudio-editor-history`** dalını ve bu daldaki `docs/visual-editor/browser/cloud/<ürün>.json` dosyasını kullanır. İlk yetkili kayıtta dal otomatik açılır. Her bulut kaydı Git commit'i yaratır ve JSON içindeki geri dönülebilir `history` dizisine tam sürüm durumu, tarih ve kullanıcının değişiklik notu ekler.

**Bu repo herkese açıktır**. Aynı şekilde geçmiş dalı ve taslaklar da halka açıktır; bu alana kişisel bilgiler veya sırlar kaydetmeyin. Buluta kaydetmek Instagram paylaşımı, kaynak HTML'i değiştirmek veya PR onayı yerine geçmez. Üretim `main` dalındaki kaynaklar, onaylı logo ve yayımlanan dosyalar otomatik değişmez. Görüntülenen v1 değişiklikleri orijinal dosya üzerinde yıkıcı düzenleme değil, izlenebilir bir **v1 editör düzenlemesidir**. Orijinal kaynak düz durur ve tek eylemle geri getirilebilir.

## Yetkilendirme

1. GitHub'da ince ayarlı (**fine-grained**) bir kişisel erişim anahtarı oluşturun. Yalnızca `cinegitim/design` deposunu seçin. Depo izinlerinde **Contents: Read and write**, Metadata varsayılan `Read` yeterlidir; admin ve geniş hesap izinleri gereksizdir. GitHub hesabının depoya yazma yetkisi olmalıdır.
2. Anahtarı yalnızca Visual Editor'ün **GitHub erişim anahtarı** alanına girin, ardından **Bağlan** deyin.
3. Token tarayıcıdaki **yalnızca geçerli sayfa belleğinde** saklanır, input temizlenir. Kaynak dosyaya, GitHub'daki tasarım JSON'una, localStorage'a, sessionStorage'a veya Cloudflare'a yazılmaz. Sekme kapanınca tekrar girilir.
4. **Buluta kaydet** seçili vN'nin içeriğini üzerine yazar; eski kayıtlar JSON logunda ve Git commit geçmişinde durur. **+ Yeni sürüm** yalnızca istenirse v(N+1) yaratır. **Geçmişe dön** tarihi state'i tuvale yükler, ardından **Buluta kaydet** yeni bir geçmiş girdisi oluşturur. **Orijinal kaynağa dön** slayt override'larını temizler; onay vermeden kalıcı depoya yazılmaz.

Bulut okunabilir; yeni cihazdan aynı ürün URL'sini açınca bulut vN seçenekleri listelenir. Lokal depoda farklı değişiklikler varsa bunlar silinmez; local ve bulut seçenekleri ayrıca gösterilir. Yazma hatası, yetkisizlik, eşzamanlı değişiklik ya da boyut sınırı başarısızlık olarak raporlanır; sessizce yerel kayıt başarılı denmez.

## PNG / JPEG

**Diğer araçlar → Görsel olarak indir** bölümünden PNG (kayıpsız) veya JPEG (yüksek kalite) seçip **Aktif slaytı indir** deyin. Görüntü aynı sayfada, kullanıcının tarayıcısında `html2canvas 1.4.1` (MIT, repo içine kopyalı) ile üretilir. Çıkış boyutu kaynak slaydın `DESIGN_W × DESIGN_H` ölçüleridir (genellikle 1080 × 1350). Dönüştürme hatalarında sahte dosya üretilmez. PNG/JPEG gerçek görüntülerdir; ancak baskı/Instagram yayımlama öncesi font ve görüntü uyumu kullanıcı tarafından görsel olarak kontrol edilmelidir.

## Sınırlar

- GitHub bulut kaydı Github Contents API üzerinden kullanıcı tarafından açıkça tetiklenir; ücretli Cloudflare servisleri, Access, R2, AI, tarayıcı render servisi veya D1 **yazma** kullanılmaz.
- Bulut dalı herkese açık GitHub deposunda tutulur; çalışma taslağı özel tasarlanmış güvenli veritabanı değildir.
- D1 staging Worker **salt okunur kalır**.
- Her ürün için en çok 240 geçmiş anı ve 950 KB JSON sınırı; sınırda durulur, eski anlar sessizce silinmez. Git commit'leri korunur.
- Eşzamanlı revizyonlar SHA üzerinde çakışırsa yazma başarısızdır; karşılıklı kayıt sessizce ezilmez.
- Yerel v2/v3 kayıtları silinmez, kullanıcı seçerek bulut sürümlerine kaydedebilir.
- Bulut yazma yetkisi için token girişi gereklidir. Bulut kaydı denemesi olmadan kalıcılık iddia edilmez.

## Test

`node --test studio/cloudflare-brandstudio/tests/cloud-editor.test.mjs`
