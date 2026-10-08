# Çin Eğitim — sadeleştirilmiş mark: ilk deneme REDDEDİLDİ

**Tarih:** 2026-10-08
**Durum:** REDDEDİLDİ · KANONİKLEŞTİRİLMEDİ · YENİDEN YAPILACAK

---

## Konu

Canlı logodaki ayrıntılı shanshui içeriği, paylaşılan "Concept 03" panosundaki
sadeleştirmeye uygun hâle getirilecek. Pano, aynı enso + çadır işaretini
kullanıyor; uzak dağ silsilesini ve kuş sürüsünü atıyor.

## Ne denendi

Enso için ölçülmüp vektörleştirilmiş hâli kullanılarak, iç kurgu
(3 katlı çadır + mürekkep zemini) **sıfırdan kurgusal SVG geometrisi olarak**
yazıldı. `studio/tools/cin-egitim/build_simplified_mark.py`.

## Sonuç — kabul edilemez

| Sorun | Gözlemlenen |
|---|---|
| Çadır ölçeği | Enso'ya göre çok küçük; iç boşluğun çoğunu boş bırakıyor |
| Çadır konumu | Zemine oturmuyor, aralarında boşluk var |
| Çatı profilleri | Katlar ayrı "lens" parçalarına düştü, aralarında boşluk; yapı okunmuyor |
| Zemin | Kopuk, yumuşak kubbe — mürekkep kütlesi değil |
| Saçak kıvrımı | Aşırı ince ve wisp yönünde, yapıyı zayıflatıyor |

## Neden başarısız — kök neden

Çadır **yazarak** üretildi. Bu yanlış yöntemdi.

Kaynaktaki çadır zaten yetkin bir el çizimi: üç kat, doğru kırık saçak
oranları, doğru gövde inceliği. Panonun yaptığı sadeleştirme, çadırı yeniden
çizmek değil — **yalnızca çevresindeki gürültüyü atmak**.

Ayrıca iki farklı nesne iki farklı yöntem ister:

- **Enso** → değişken genişlikli fırça darbesi. Radyal ölçüm + yeniden kurulum
  doğru yöntem; kuru fırça dokusu düşürüldü çünkü 16px'te üretilemez.
- **Çadır ve zemin** → düz **silüetler**. Sınırları temiz, içleri boş. Bunlar
  izlemeye uygundur; elle kurgulamaya değildir. Ders: izlemenin nerede doğru,
  nerede çöp ürettiği nesnenin geometrisinden gelir, alışkanlıktan değil.

## Doğru yol (uygulanmadı)

1. Enso → mevcut ölçülmüş yeniden kurulum (IoU 0.8852) olduğu gibi
2. Çadır + zemin → 862px kaynaktan **silüet izleme** (marching squares +
   Douglas-Peucker sadeleştirme), kuşlar ve uzak dağlar maskelenerek çıkarılır
3. Kırmızı uç pırıltısı → kaynağa sadık kalır
4. Sonuç: pano sadeliği + kaynak çizim kalitesi

## Enso hakkında geri alınan bir "düzeltme"

Bu oturumda enso merkezinin kutu ortasından alınması hata sayıldı ve iki geçişli
en küçük kare daire uydurmasıyla düzeltilmeye çalışıldı.

**Bulgu yanlıştı.** Dört kombinasyon ölçüldü:

| Merkez | Yay | IoU |
|---|---|---|
| kutu (tohum) | dar | **0.8852** |
| uydurulan | dar | 0.8792 |
| kutu (tohum) | geniş | düşük (boşluğa geometri eklüyor) |
| uydurulan | geniş | düşük |

En küçük kare uydurması merkezi yalnızca 4.4/5.9 piksel kaydırdı ( sandığım 31
piksel kayma, işlenmiş profil üzerinde yapılan ayrı bir denemeydi). Tohum
merkez + dar yay **ölçümle kazanan** seçenek; geri alındı ve gerekçesi
`build_enso.py` içine yazıldı.

## Durum

Kanonikleştirilen dosya: **0**. Görsel üretim çağrısı: **0**.
Bu deneme arşivde korunur; üretimde kullanılamaz.