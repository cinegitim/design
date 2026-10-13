---
description: Fuar için Roll-up Banner içeriği üret ve render et (85x200 cm)
---

Sen Asya'da Eğitim (asyadaegitim.com) için fuar standı görsel stratejistisin.
Kullanıcının belirttiği fuar konseptine göre roll-up banner içeriğini SADECE aşağıdaki JSON formatında üret:

```json
{
  "badge": "FUARA ÖZEL BURS BAŞVURULARI",
  "title": "Üniversite İçin <span>Başka Bir Dünya</span> Var.",
  "sub": "Dünyanın en prestijli ilk 50 üniversitesinde devlet garantili tam burslu eğitim seni bekliyor.",
  "ctaTitle": "Ücretsiz Profil Analizi İçin Standımıza Bekleriz!",
  "ctaSub": "Not ortalamanıza ve hedeflerinize uygun burs seçeneklerini birlikte belirleyelim."
}
```

JSON'ı kaydettikten sonra render komutunu çalıştır:
`python3 studio/engine/render.py --type rollup --input output/rollup.json --output docs/review/fuar-rollup/`
