# Çin Eğitim — izolasyon mimarisi ve yön araştırması

**Tarih:** 2026-10-08
**Branch:** `publish/cin-egitim-identity`
**Durum:** ÜÇ YON PENDİK · HİÇBİR ŞEY KANONİKLEŞTİRİLMEDİ

---

## Karar 1 — Tam izolasyon

Çin Eğitim, Asya'da Eğitim ile **aynı çalışma disiplinini** paylaşır, hiçbir varlığı,
aracı, kararı veya kanonik dosyasını paylaşmaz.

| Katman | Asya'da Eğitim | Çin Eğitim |
|---|---|---|
| Marka klasörü | `brands/asyada-egitim/` | `brands/cin-egitim/` |
| Pano | `docs/asyada-seal/…` | `docs/cin-egitim/` |
| Araç ad alanı | `studio/tools/*.py` | `studio/tools/cin-egitim/*.py` |
| Kilit doğrulayıcısı | `verify_asyada_canonical_lockups.py` | `cin-egitim/verify_cin_canonical_lockups.py` |
| Manifest | `…/assets/lockups/canonical-lockups.json` | `…/assets/lockups/canonical-lockups.json` |
| Karar kayıtları | `decisions/2026-10-0[78]-*.md` | `decisions/2026-10-08-*.md` |
| Doğrulanmış mühür | `v01-canonical.svg` (kilitli) | **yok — henüz seçilmedi** |

Gerekçe: iki müşteri bağımsız çalışır. Birinin onayı, revizyonu veya dosya
değişikliği diğerini hiçbir koşulda etkilememelidir. İki araç da karşılıklı
olarak diğerinin dosyalarını okumaz.

## Karar 2 — Ana sayfa geçişi

`docs/index.html` üzerinde kalıcı bir marka geçişi (`brandbar`). İki marka
arasında geçiş yapar; **ortak varlık kullanmaz, ortak kural uygulamaz.**
Aynı geçiş `docs/cin-egitim/index.html` üzerinde ters yönde bulunur.

Geçişte Çin Eğitim için **tarafsız bir yer tutucu** kullanılır, aday işaretlerden
biri değil. Henüz seçilmiş bir logo yoktur; bir adayı geçişte göstermek seçimi
insanın verdiği bir kararı önceden vermek olurdu.

## Karar 3 — Yeni kimlik, aynı yöntem

Çin Eğitim, Asya'da Eğitim'in kimliğini **taşımaz**. Kendi işareti, paleti,
tipografisi, kilit ailesi ve tasarım dili vardır. Paylaşılan şey yöntemdir:
ölç, kurgula, ölçerek doğrula, insana göster, kilitle.

## Canlı siteden ölçülen mevcut durum

Kaynak: üretim CSS `/_next/static/css/index.Co_vgAiy.css` (214 923 bayt).

- `--primary` `#8f1f2d` · `--accent-foreground` `#741723` · `--accent` `#f7ecee`
- `--navy` `#3a1720` · `--foreground` `#20252b` · `--background` `#ffffff`
- `--muted` `#f2f3f4` · `--muted-foreground` `#626970`
- `--border` `#e3e5e7` · `--input` `#dfe2e5`
- `--default-font-family: Arial, Helvetica, sans-serif` ← tarayıcı varsayılanı
- Logo: `cinegitim-logo.png`, PNG 120×116, SHA-256 `0b53aa17feb…`

Logo görsel denetimi: pagoda siluetleri + kırmızı fırça hilal (Japonya okunuyor)
+ kurt + gri dağlar = dört ayrı fikir, tek fikir yok. 120 px'te çatı hatları
~6 px. Favicon boyutu, tek renk varyantı ve güvenli alan kuralı mevcut değil.
Nihai izlenim: turizm acentesi.

## Sunulan üç yön

| Yön | Kavram | Gramer | Küçülme riski |
|---|---|---|---|
| **A · KAYIT / THE REGISTER** | Resmî kayıt insani navigasyona dönüşür | Sıkı modüler grid, saç teli kurallar, tablo rakamları | **En zayıf** — 24px altında ızgara okunmuyor |
| **B · KALEM / THE SINGLE STROKE** | Mürekkep hareket ekonomisi; tek kararlı çizgi | Hareket + boşluk, ızgara dışı asimetri | **Orta** — 40px altında kılavuz kopuyor; oynat düğmesi riski |
| **C · KOORDİNAT / THE INTERSECTION** | İki koordinat çerçevesi, tek ortak eksen | Koordinat ağı, tırnaklar, ölçülmüş koordinatlar | **En güçlü** — 24px'e kadar üç bileşen de korunuyor |

## Üretim disiplini

- Vektör öncelikli: işaretler gerçek SVG geometrisi, 120 birimlik ızgara üzerinde.
- Görsel üretim çağrısı: **0**
- Kanonikleştirilen dosya: **0** — `brand.json`, manifest ve kilit yok.
- Panolardaki kelime-marka canlı yazı tipiyledir ve **önizleme** olarak
  etiketlenmiştir; üretimde dışa çizilmiş yol (outline path) olarak teslim edilir.
- Panolar deterministik olarak üretilir:
  `python3 studio/tools/cin-egitim/build_direction_boards.py`

## Bulunan ve düzeltilen kusurlar

Görsel denetimle bulundu, ölçümle doğrulandı:

1. **İşaret 120 birimde çiziliyordu, 40 birimlik yer ayrılmıştı** → tüm yatay
   kilitlerde metin işaretin üstüne biniyordu. İşaret artık rolün gerçek
   boyutuna ölçekleniyor.
2. **D-04 yalnız Türkçe taşıması gerekirken** "small" alt dize eşleşmesi
   işe yaramadı; İngilizce satır kırık halde çıkıyordu. Artık varyant kimliğiyle
   eşleşiyor.
3. **C-03, Asya'da Eğitim'in mühür en-boy oranını (370) kullanıyordu** → işaret
   ezik çıkıyordu. Artık markanın kendi oranı kullanılıyor.
4. **P-01'de merkezleme 40 birim kayıktı.**
5. **A yönünde orta hücre dolduruluyordu** → ızgara değil **nişangâh** okunuyordu.
   Köşe hücreye geçirildi.
6. **B yönünün alt kenarı aşağı kavisleniyordu** → vuruş değil **yaprak**
   okunuyordu. Karnın artık vuruşun kendi ekseni boyunca dışbükey.
7. `ROOT = parents[2]` bu dizin derinliğinde `studio/`'ya düşüyordu ve tüm ağaç
   yanlış yere yazılıyordu. `parents[3]`.

## Sonraki adım

**İnsan yön seçimi.** Seçim yapılmadan hiçbir varlık kanonikleştirilmez,
kilit dosyası üretilmez, doğrulayıcı çalıştırılmaz.

Seçim sonrası: görsel DNA çıkarımı → sadakat yeniden kurulumu → kaynak/yeniden
kurulum karşılaştırması → **insan logo onayı** → `brand-system.md` (Katman A
görsel DNA + Katman B üretim kuralları) → üretim varlıkları.