# Görsel QA · Tsinghua Atlası V2

**Durum:** yaratıcı öz inceleme tamamlandı; insan yaratıcı incelemesi bekleniyor.

## Görsel inceleme kaydı

Yedi 1080×1350 PNG ve 324×405 mobil çıktılar gerçek görsel girdileri olarak incelendi; temas sayfası ve V1–V2 karşılaştırması da görüntülendi. Son düzenlemeden sonra kapak ve kapanış dipnotları kaldırıldı; tüm yedi slayt yeniden render edildi.

| Slayt | Kontrol / bulgu |
|---|---|
| 01 · Kapak | Başlık, başvuru yılı ve düzen belirgin; fotoğraf ve tipografi dengeli. P-01/light özgün SVG olarak 376 px genişlikte; manifest’in 352 px minimumunu karşılar. Alt bilgi alanı sade bırakıldı. |
| 02 · QS alanları | Altı alan iki sütunlu tabloda; rank numaraları, anlamlı konu ikonları ve alan adları ayrışıyor. Eşit 7 gösterimi açık. Fotoğraf alt yazısı ve kaynak notu küçük tutulmuştur; inceleme için tam boy PNG mevcuttur. |
| 03 · Küresel sıralamalar | Üç kuruluş/edisyon ayrı kartlarda; 14 / 11 / 6 hiyerarşik olarak okunuyor. Metodoloji uyarısı sayfanın altına alındı. |
| 04 · Programlar + dil | Üç resmi program adı ayrı satırlarda. HSK 5+ şartı yalnızca Çince–İngilizce programlara bağlandı; tamamen İngilizce programlar için Çince belgesi gerekmediği ayrı blokta. İlk denemedeki taşan uyarı satırı iki satıra bölündü; son metin kutularında taşma yok. |
| 05 · Takvim | 20 Kasım 2026 ve 28 Şubat 2027 tarihleri, 17.00 ve Pekin saati birlikte. İlk görüntülemede ay adı/gün rakamı çakışması bulundu ve ay/yıl hizası düzeltildi; son render’da iki tarih arasında çakışma yok. Program kılavuzu uyarısı daha küçük ama görünür. |
| 06 · Ücret + burs | ¥30.000, ¥100.000, yaklaşık %45, ¥800 ve ¥800/yıl ayrı seviyelerde. “Seçili programlar” kapsamı ve 2026 kohortu notu korunuyor; çok küçük dipnot mobil ölçekte ikincil bilgi. |
| 07 · CTA | Spor fotoğrafındaki insan figürü sağda bırakılarak metin için koyu sol alan ayrıldı; CTA butonu belirgin, alt alan fotoğrafla açık bırakıldı. P-01/dark özgün SVG olarak 360 px genişlikte ve 352 px minimumun üzerindedir. |

## Mobil kontrol ve teknik sınırlar

- 324×405’de ana başlıklar, sıralama değerleri, tarihler, ücretler, burs yüzdesi ve CTA kontrast/hiyerarşi açısından kontrol edildi. Kaynak ve metodoloji notları küçük ekranda ikincil bilgidir.
- 375×469 önizlemeleri de üretildi. Her iki ölçekte kırpma ve taşma kontrol edildi.
- 324×405 karelerin tamamı gerçek ölçüsünde `mobile-324-contact-sheet.png` üzerinde yan yana sunulur; `mobile-324/` içinde her slayt ayrıca tekil PNG olarak bulunur.
- Chromium render raporu Jost yüklenmesini, her bağlı görselin decode edilmesini ve düzenlenebilir metin satırlarının artboard içinde kalmasını doğrular. Son raporda taşan metin yoktur.
- PNG’ler 1080×1350 RGB’dir ve sRGB profili paketleme doğrulamasında gömülür. Kanonik lockup ve photo license hash/source doğrulaması ayrıca çalıştırılır.
- V1 karşılaştırma sayfası farkları gösterir; V1 dosyaları silinmemiş veya yeniden yazılmamıştır.

**Sonraki adım:** insan yaratıcı incelemesi.
