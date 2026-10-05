# Figma layer — parallel, isolated

> Bu klasör, brand-studio hattının **görsel uygulama katmanının** Figma ayağıdır.
> İkinci bir source-of-truth **değildir**; sıfırdan AI tasarımı üretme yeri **değildir**.

## Bu katman ne (ve ne değil)

| | |
|---|---|
| **Var** | `brand-system.md`'nin makine-okunur token aynası + Figma dosyasının kuruluş blueprint'i |
| **Var** | Canonical marka dilinin Figma **Variables + Components + Templates** olarak uygulanabilir hâli |
| **Yok** | Bağımsız marka kararı (renk, tip, logo mantığı burada değişmez) |
| **Yok** | AI ile serbest tasarım üretimi (image generation yalnızca *değişken içeriği* doldurur) |
| **Yok** | brand-studio pipeline'ına müdahale ( `/brand*` komutları, brands/, studio/ bu hattan etkilenmez) |

## Kaynak hiyerarşisi ve türetme kuralı

```
brands/<slug>/brand-system.md   ← İNSAN-OKUNUR canonical (tek gerçek kaynak)
        │  (türetilir — asla ters yönde bağımsız düzenlenmez)
        ▼
figma/tokens/<slug>.tokens.json ← MAKINE-OKUNUR ayna (renk, typography,
        │                          spacing, logo geometrisi, motion)
        ▼
Figma dosyası                    ← Variables (Foundations) + Components +
        │                          Templates + Applications
        ▼
Uygulamalar (Figma export / brand-studio applications)
```

**Tek değer kuralı:** Bir değer (renk, ölçü, ağırlık…) yalnızca `brand-system.md`'de yaşar.
Token dosyası ondan **türetilir**. Değer değişecekse önce `brand-system.md` düzenlenir,
token dosyası sonra senkronize edilir. İki yerde elle bağımsız yönetim yoktur.

## Dosya ağacı

```
figma/
├── README.md                      ← bu dosya (boru hattı + kurallar)
├── blueprint.md                   ← Figma dosya kuruluş rehberi
│                                     (Cover / Brand DNA / Foundations / Components /
│                                      Patterns / Templates / Applications / Playground)
└── tokens/
    ├── README.md                  ← token isimlendirme + Figma'ya aktarım adımları
    ├── tokens.schema.json         ← JSON Schema (yapı doğrulama)
    └── asya-egitim.tokens.json    ← ilk gerçek örnek (brand-system.md'den türetildi)
```

## Faz planı

| Faz | İçerik | Durum |
|---|---|---|
| **1** | Token şeması + ilk token dosyası + Figma blueprint | ✅ kurulu |
| **2** | Tokens Studio / Figma Variables sync (yalnızca gerçekten çalışan entegrasyonla) | ⏳ bekliyor |
| **3** | `/figma-sync` komutu — yalnızca Faz 2 kanıtlanınca | ⏳ bekliyor |

Faz 2–3'te **Figma API/otomasyonu veya yeni `/figma-*` komutları, çalışan bir
entegrasyon kanıtlanmadan eklenmez.**

## Figma'ya aktarım (bugün: manuel)

1. Figma'da `figma/blueprint.md` sayfa sırasıyla dosyayı kur: `<slug> — Brand System`.
2. **Tokens Studio for Figma** eklentisini aç → *Import* → `figma/tokens/<slug>.tokens.json`.
   (Eklenti W3C-tarzı `$value`/`$type` formatını okur; gruplar → koleksiyon eşlemesi
   `figma/tokens/README.md`'de.)
3. Variables/Styles'i blueprint'teki **02 Foundations** sayfasında kur; bileşenleri
   **03 Components**'ta token'lara bağla.
4. Şablonları **05 Templates**'te üret; görsel slotları *placeholder* kalır —
   raster yalnızca brand-studio üretiminden gelir.

## İzolasyon kuralları

- Site sayfası: `docs/figma/index.html` — **tamamen izole**: mevcut site nav'ına
  hiç dokunulmaz, sayfa yalnızca doğrudan URL (`/figma/`) ile erişilir.
- Brand-studio hattıyla ortak dosya yok: `figma/` yalnızca `brands/<slug>/brand-system.md`'yi
  **okur** (türetme kaynağı), başka hiçbir şeyi yazmaz/değiştirmez.
- Yayın: brand-studio ile aynı GitHub delivery kuralı (`publish/<topic>` → PR → merge →
  Pages doğrulaması), ayrı topic ile: `publish/figma-*`.
