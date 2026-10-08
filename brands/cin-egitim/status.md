# Brand Status — Çin Eğitim (operational state)

- Workflow stage: **yön araştırması** (3 direction boards built)
- Brand identity: **YOK** — henüz seçilmedi, kilitlenmedi
- Production work allowed: **HAYIR** — hiçbir varlık kanonik değil
- Canonical logo: **yok** · Canonical lockups: **yok** · Manifest: **yok**
- Current next action: **insan yön seçimi** (A / B / C)
- Branch: `publish/cin-egitim-identity`
- Isolation: `brands/cin-egitim/` · `docs/cin-egitim/` · `studio/tools/cin-egitim/`
  — Asya'da Eğitim ile hiçbir dosya paylaşılmıyor

## Directions under review

| Yön | İşaret | Durum |
|---|---|---|
| A · KAYIT / THE REGISTER | Mühür halkası + kayıt ızgarası, bir köşe hücre dolu | PENDING |
| B · KALEM / THE SINGLE STROKE | Basınçla başlayıp bırakılan tek vuruş + kısa kılavuz | PENDING |
| C · KOORDİNAT / THE INTERSECTION | İki çerçeve, tek ortak eksen, dolu kesişim | PENDING |

## Production rules for this brand (active now)

1. **Hiçbir aday işaret kanonik değildir.** Seçim öncesi üretimde kullanılamaz.
2. **Görsel üretim çağrısı: 0.** Vektör öncelikli çalışılır.
3. Panolardaki kelime-marka **önizlemedir**; üretimde dışa çizilmiş yol olarak
   teslim edilir, böylece istemci makinesinde yazı tipi değişimi olamaz.
4. Doğrulanmış doğrulayıcı **yok** — kanonik manifest gelene kadar çalıştırılamaz.

## Live-site audit

Tam ölçüm: `brands/cin-egitim/brand-brief.md` ve
`decisions/2026-10-08-isolation-architecture.md`.

## Once a direction is selected

1. Görsel DNA çıkarımı (ölçülen geometri + renk + tipografi kuralları)
2. Sadakat yeniden kurulumu — outline path wordmark, gerçek font konturlarından
3. Kaynak/yeniden kurulum karşılaştırması
4. **İnsan logo onayı** — bu olmadan kilitlenmez
5. `brands/cin-egitim/brand-system.md` (Katman A görsel DNA + Katman B üretim kuralları)
6. Kilit ailesi üretimi + `cin-egitim/verify_cin_canonical_lockups.py` doğrulayıcısı
7. `brand.json`, manifest, SHA kaydı

## Rebuild the boards

```sh
python3 studio/tools/cin-egitim/build_direction_boards.py
```

Deterministiktir, görsel üretim çağrısı yapmaz, hiçbir şeyi kanonikleştirmez.