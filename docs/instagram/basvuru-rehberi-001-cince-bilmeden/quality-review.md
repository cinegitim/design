# Görsel kalite inceleme raporu · Başvuru Rehberi / 001

İki tam tema sayfası incelemesi yapılmıştır. İncelemeler gerçek PNG çıktısı
üzerinden (modelin dosyayı görerek) yapılmıştır; prompt'tan veya dosya adından
çıkarım yapılmamıştır.

## İnceleme 1 — ilk render sonrası

Bulunan sorunlar ve yapılan düzeltmeler:

| # | Sorun | Şiddet | Düzeltme |
|---|---|---|---|
| 1 | Slayt 03'te kilitli `Finans · Uluslararası Ticaret · Dijital Pazarlama` satırı hiç yer almıyordu | **Kritik** | Satır eklendi; kopya denetimi bu tür eksiklikleri artık build sırasında durduruyor |
| 2 | Slayt 04'te `Çin'de yüksek` ve `lisans yapabilir misin?` 2,2 px çakışıyordu | Yüksek | Satır aralığı 54 → 62 px |
| 3 | Slayt 06'da komşu kolon etiketleri (İngilizce yeterlilik / Akademik sınav) çakışıyordu | Yüksek | Etiketler iki satıra bölündü (20 px, 26/27 px satır aralığı) |
| 4 | Slayt 02'de `Ve çok daha fazlası.` ile kanonik lockup çakışıyor, dipnot 1320 px güvenli sınırını aşıyordu | Yüksek | Lockup sağ üste alındı; liste 36 px'e büyütülüp yukarı kaydırıldı; dipnot 1300 px taban çizgisine çekildi |
| 5 | Slayt 03 ve 05'te lockup x+w = 1062 px ile 1040 px sınırını aşıyordu | Yüksek | x=712 ve genişlik 300 px; slayt 03 dark yerine light varyant (ink zemin üzerinde doğru varyant) |
| 6 | Slayt 05'te hiç şirket/üniversite fotoğrafı yoktu; SHU ve Fudan yalnızca metin olarak geçiyordu | Yüksek | SHU Ana Kütüphane ve Fudan Guanghua Kulesi fotoğrafları eklendi; Fudan etiketi fotoğrafın altına hizalandı |
| 7 | Slayt 06 belge etiketleri 20 px ile mobilde zor okunuyordu | Orta | Etiketler 22 px'e çıkarıldı |
| 8 | Slayt 03'ün alt yapısı düz ve iki destek fotoğrafı basık kalıyordu | Orta | Atlas yapısı yeniden düzenlendi: iki destek fotoğrafı üstte, baskın merkezî fotoğraf altta daha büyük |

## İnceleme 3 — son kontrol (bu sürüm)

Slayt 03, medya sırasını verilen metin sırasına uyacak şekilde soldan sağa okunan
üç bölüme yeniden düzenlendi (Pekin → baskın merkezî Şanghay → Hangzhou). Böylece
kilitli metnin sırası bozulmadan Shanghai University görsel olarak baskın kaldı.
Bu değişiklik, kopya doğrulama betiğinin bir *sıra* uyuşmazlığını yakalaması
sonucu yapıldı; otomatik denetim olmasaydı sessiz bir içerik yeniden sıralaması
yayınlanacaktı.

- [x] Altı slayt da gerçek 1080×1350 PNG olarak üretildi ve ölçüldü.
- [x] Jost ve Songti SC tamamen gömülü; `document.fonts.check(...)` doğrulandı.
- [x] Metin–metin, metin–lockup, Çince işaret, ikon–etiket çakışması **yok**.
- [x] Kırpılmış veya taşmış metin **yok**; tüm metin kutuları 40–1040 × 40–1310 güvenli alanında.
- [x] Kilitli metnin tamamı birebir ve **verilen sırada** korundu (`exact-copy.json` → PASS, 6/6).
- [x] Üniversite–şehir–program ilişkileri doğru: Tsinghua→Pekin, Shanghai University→Şanghay, Zhejiang→Hangzhou, Fudan ayrı bölümler.
- [x] Kanonik lockup'lar bağlantılı, orantısız (aspect korunmuş), minimum boyutun üzerinde ve çerçevede.
- [x] Her slaytta kırmızı ve altın görsel bir sözlük olarak görünür; altın yalnızca ince çizgi değil, büyük vurgu alanlarında da.
- [x] Slayt başına bir ila iki Çince grafik aygıt; altı slayt aynı süsleme çerçeveyi tekrarlamıyor.
- [x] Zıt slaytlar farklı: 01 mürekkep + ay kapısı, 02 sıcak kâğıt + kafes, 03 foto atlas, 04 mürekkep + kırmızı düzlem, 05 koyu araştırma + daire motifi, 06 klasör formu.
- [x] Mobil önizlemeler (375×469) gerçek PNG'lerden üretildi ve tam boyutta incelendi; tüm etiketler okunur.
- [x] Bağımsız depo denetimi (`studio/cloud/audit.py`) PASS; 5 paketin tamamı.

## Kalan bilinçli sınırlar

- Kırmızı iki tonu (marka kırmızısı `#BD2120` ve Çin kırmızısı `#DE2910`) hiçbir
  slaytta yan yana komşu alanlarda kullanılmaz; marka kırmızısı hero cevap
  kelimesinde ve CTA alt çizgisinde, Çin kırmızısı band/düzlem/klasör formunda.
- Slayt 05'in taban fotoğrafı (Tsinghua Kuantum Bilgi Merkezi) üniversite adı
  taşımaz; araştırma atmosferi olarak kullanılır. SHU ve Fudan fotoğrafları
  kendi adlarının altındadır.
- Fotoğraflar belgesel kampüs görselleridir; ajans çekimi değildir. Krediler
  `caption-and-credits.md` içindedir.

## Durum

**İnsan yaratıcı incelemesi bekleniyor.** Teknik ve tipografik kapılar geçti;
estetik onay ayrı bir insan kararıdır. Instagram'da yayınlanmamıştır.
