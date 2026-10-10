# Görsel QA · Tsinghua Atlası V2

**Durum:** yaratıcı öz inceleme tamamlandı; insan yaratıcı kabulü bekliyor. Tsinghua kurumsal onayı veya Instagram yayını değildir.

## Görsel inceleme kaydı

Yedi 1080×1350 PNG ve 324×405 mobil çıktılar gerçek görsel girdileri olarak incelendi; temas sayfası ve V1–V2 karşılaştırması da görüntülendi. Son düzenlemeden sonra 04. slayt düzeltildi ve tüm yedi slayt yeniden render edildi. Bu bir insan estetik kabulü değildir.

| Slayt | Kontrol / bulgu |
|---|---|
| 01 · Kapak | Başlık, başvuru yılı ve düzen belirgin; fotoğraf ve tipografi dengeli. P-01/light özgün SVG olarak 376 px genişlikte; manifest’in 352 px minimumunu karşılar. Küçük “resmî kaynaklar” notu 324 px’de ikincil bilgidir. |
| 02 · QS alanları | Altı alan iki sütunlu tabloda; rank numaraları, anlamlı konu ikonları ve alan adları ayrışıyor. Eşit 7 gösterimi açık. Fotoğraf alt yazısı ve kaynak notu küçük tutulmuştur; inceleme için tam boy PNG mevcuttur. |
| 03 · Küresel sıralamalar | Üç kuruluş/edisyon ayrı kartlarda; 14 / 11 / 6 hiyerarşik olarak okunuyor. Metodoloji uyarısı sayfanın altına alındı. |
| 04 · Programlar + dil | Üç resmi program adı ayrı satırlarda. HSK 5+ şartı yalnızca Çince–İngilizce programlara bağlandı; tamamen İngilizce programlar için Çince belgesi gerekmediği ayrı blokta. İlk denemedeki taşan uyarı satırı iki satıra bölündü; son metin kutularında taşma yok. |
| 05 · Takvim | 20 Kasım 2026 ve 28 Şubat 2027 tarihleri, 17.00 ve Pekin saati birlikte. İlk görüntülemede ay adı/gün rakamı çakışması bulundu ve ay/yıl hizası düzeltildi; son render’da iki tarih arasında çakışma yok. Program kılavuzu uyarısı daha küçük ama görünür. |
| 06 · Ücret + burs | ¥30.000, ¥100.000, yaklaşık %45, ¥800 ve ¥800/yıl ayrı seviyelerde. “Seçili programlar” kapsamı ve 2026 kohortu notu korunuyor; çok küçük dipnot mobil ölçekte ikincil bilgi. |
| 07 · CTA | Spor fotoğrafındaki insan figürü sağda bırakılarak metin için koyu sol alan ayrıldı; CTA butonu ve bağımsız bilgilendirme notu mevcut. P-01/dark özgün SVG olarak 360 px genişlikte ve 352 px minimumun üzerindedir. CTA görseli henüz gerçek bir bağlantı içermez. |

## Mobil kontrol ve teknik sınırlar

- 324×405’de ana başlıklar, sıralama değerleri, tarihler, ücretler, burs yüzdesi ve CTA kontrast/hiyerarşi açısından kontrol edildi. Kaynak/methodology notları, fotoğraf alt yazıları ve hukuki açıklamalar küçük ekranda ikincil bilgi olarak kalır; gerektiğinde tam boy slayt ve bağlantılı raporlar kullanılmalıdır.
- 375×469 önizlemeleri de üretildi. Her iki ölçekte kırpma ve taşma kontrol edildi.
- 324×405 karelerin tamamı gerçek ölçüsünde `mobile-324-contact-sheet.png` üzerinde yan yana sunulur; `mobile-324/` içinde her slayt ayrıca tekil PNG olarak bulunur.
- Chromium render raporu Jost yüklenmesini, her bağlı görselin decode edilmesini ve düzenlenebilir metin satırlarının artboard içinde kalmasını doğrular. Son raporda taşan metin yoktur.
- PNG’ler 1080×1350 RGB’dir ve sRGB profili paketleme doğrulamasında gömülür. Kanonik lockup ve photo license hash/source doğrulaması ayrıca çalıştırılır.
- V1 karşılaştırma sayfası farkları gösterir; V1 dosyaları silinmemiş veya yeniden yazılmamıştır.

**Görsel onay bekleyen noktalar:** nihai copy/CTA bağlantısı ve tüm küçük açıklamaların marka/iş sahibi tarafından kabulü; bunlar otomatik CI veya bu öz inceleme ile onaylanmış sayılmaz.
