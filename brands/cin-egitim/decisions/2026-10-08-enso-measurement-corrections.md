# Çin Eğitim — enso düzeltmeleri: hangi hipotez test edildi, hangisi düştü

**Tarih:** 2026-10-08
**Durum:** İNSAN ONAYI BEKLENİYOR · KANONİKLEŞTİRİLMEDİ

Bu oturumda enso üzerinde dört varsayım test edildi. **Üçü düştü.** Hepsinin
gerekçesi koda da yazıldı; kanıtsız "düzeltme" yok.

---

## 1. "Merkez kutu ortasından alınıyor, bu hata" — DÜŞTÜ

Kutu ortası, kırık bir çemberde teorik olarak yanlıştır. En küçük kare daire
uydurması denendi.

| Merkez | Yay | IoU |
|---|---|---|
| kutu (tohum) | dar | **0.8852** |
| en küçük kare uydurması | dar | 0.8792 |

Deneme merkezi yalnız 4.4/5.9 piksel kaydırdı. İlk denemede görülen 31 piksel
sapma, işlenmiş profil üzerinde yapılan ayrı ve hatalı bir ölçümdü.
Yay genişletmesi de boşluğun içine 82 derece interpolasyonlanmış geometri
eklediği için IoU'yu düşürdü. Tohum korundu.

## 2. "Testere dişi kuru fırça gürültüsü, daha fazla yumuşatma siler" — DÜŞTÜ

Alt solda 59.5 piksellik ani sıçrama vardı. Altı yumuşatma kombinasyonu ölçüldü
(w3p3 … w9p13):

| Pencere / geçiş | IoU | En sıçrama |
|---|---|---|
| w3 p3 | **0.8758** | 59.5 |
| w5 p5 | 0.8741 | 59.5 |
| w7 p7 | 0.8720 | 59.5 |
| w9 p13 | 0.8709 | 59.5 |

Hiçbiri sıçramayı kaldırmadı, hepsi IoU'yu düşürdü. w3 p3 korundu.

Ama sonradan sıçramanın **nerede** olduğu bulununca (79°, konum 356/687) ve
o bölge kaynaktan kırpılarak görüldüğünde, varsayımın kendisi çürüdü:
sıçrama gürültü değil, **ölçüm hatasıydı**. Aşağıdaki 4. madde.

## 3. "Yakın parçaları birleştirince gövde bütünleşir" — DÜŞTÜ

| Varyant | IoU |
|---|---|
| en uzun parça | **0.8709** |
| 1.35× yakınlıkla birleştir | 0.8422 |
| 1.8× yakınlıkla birleştir | 0.8379 |

Birleştirme kötüleştirdi.

## 4. "59.5 piksellik sıçrama ibrısım bölgesinin kırıntısı" — DOĞRU

Kaynağın o bölgesi kırpılarak görüldü. Kaynakta darbe **üç dala ayrılıp
eriyor** (fırça mürekkebini bitiriyor). Yeniden kurulumda ise iç kenarda
merdiven basamağı ve köşe kesik bir blok oluşuyordu — yani kusur kaynağın
karakteri değil, ölçümün kırıntı seçmesiydi.

Asıl bulgu: **önceki 57°–313° yayının büyük kısmında kırmızı yoktur.**

| | Yay | Ölçülen | Tahmin edilen |
|---|---|---|---|
| önce | 57°–313° (256°) | 174 | **82** |
| şimdi | 65°–288° (223°) | 211 | **13** |

223°'lik yay ışın taramasıyla bulundu: 288°'den sonra kırmızı yok. Yay artık
elle seçilmiyor, **ölçülüyor**.

Buna ek olarak parça seçimi "en uzun" yerine **sürekliliğe** çevrildi: birden
fazla parça varsa, önceki açının orta yarıçapına en yakın olanı alınır. Darbe
sürekli bir yoldur; kırıntı değil devamı izlenir.

## Uç kapakları — gerçek kusur, düzeltildi

`catmull_path` **kapalı** döngüyü yumuşatıyordu; yumuşatma iki uç kapağını da
kapsıyor, köşeleri yuvarlayınca kapakları ince kıvrık bir tele dönüştürüyordu
(800px'de görüldü: sağ üstte ve sağ altta iğne).

- `catmull_open` eklendi: dış kenar ileri yumuşatılır, **düz çizgiyle**
  kapatılır, iç kenar geri yumuşatılır, düz çizgiyle kapanır.
- Sivrilme artık sıfıra **inmiyor**: medyan kalınlığın %22'sine iner ve düz /
  açılı bir kesmeyle kapanır. Sıfıra inen sivrilme 16px'te leke oluşuyordu.

## IoU'nun bu oturumdaki yeri — sınırı

IoU **kaynağa sadakati** ölçer. Bu oturumda alınan karar ise kuru fırça
dokusunu bilinçli olarak **düşürmek**. Doku düşürme kararını IoU ile yargılamak,
ölçtüğün şeyle hedeflediğin şeyi karıştırmaktır.

Bu yüzden: **çekirdek gövdede (107°–263°) IoU sadakat ölçütüdür; uçlarda
görsel denetim ölçüttür.** 16px ve altı için ayrı varyant zorunludur ve
boyut merdiveni bunu doğruladı.

---

## Kalan kusurlar — onay öncesi bilinmesi gerekenler

1. **Üst uçta küçük bir çengel/kıçık var** (saat 1 yönü). Yay sonunun artık
   kalıntısı.
2. **Enso sol altta zemine değme noktasında hafif testere kenar** ve küçük
   beyaz takıl. Kaynak ıbrısımının sınırında.
3. **Enso kaynağa göre daha kalın ve daha düzgün.** Kaynaktaki değişken
   genişlik ve incelen kuyruklar düşürüldüğü için. Doğru yönde ama jest
   zayıfladı; kompozisyon içerdi biraz sıkıyor.
4. **16px'te marka çöküyor.** Enso ince bir şeride, çadır okunmayan bir
   lekeye dönüşüyor. Ayrı küçük boyut varyantı zorunlu.

Görsel üretim çağrısı: **0** · Kanonikleştirilen dosya: **0**