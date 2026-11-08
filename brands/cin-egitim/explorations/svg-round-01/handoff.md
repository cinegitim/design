# Studio task handoff

- Request / scope: Son SR PNG'den yalnız sembol SVG; kullanıcı onayı/kilidi; ana sayfa/Çin Eğitim sayfası yerleşimi; ardından kullanıcı ana sayfa hero'sunun derli toplu ve UI kullanılabilirliğinin artırılmasını ve canlıya alınmasını istedi. Tipografi yok.
- Executor: OpenCode / macOS; Potrace + librsvg + Pillow. Image/LLM raster çağrısı: 0.
- Brand: `cin-egitim`; reference kilidi ve kanonik sembol `brand.json` ile hash-locked. Asya'da Eğitim varlıkları değişmedi.
- Branch / base main SHA: `publish/cin-egitim-svg-candidate` / `a7af288a77a32032e2f83383b4e3c48595cb4463`.
- Round: `brands/cin-egitim/explorations/svg-round-01/`; public mirror `docs/cin-egitim/svg-round-01/`. Web asset exact copy: `docs/cin-egitim/assets/symbol.svg`.
- Input SHA: `56ad9bc59a50a53f44db2c91800a5470868002b70fb692107c4e8e115582bdc7` (son SR PNG). Kaynak hedef SHA: `6177f661a1971b985c2d2e0bb91b995d8df074f5ef9433caef5366f457a76b89`.
- Outputs/hashes: `manifest.json`; package checksum: `delivery.json`.
- Canonical symbol: `brands/cin-egitim/assets/symbol.svg`, SHA in `brand.json` + human decision. Hedef kilidi ayrı korunuyor.
- Checks: task-branch preflight (locked_files_checked: 1), round verifier, genel audit/cloud/work rejection tests; homepage Lighthouse accessibility/best-practices/SEO 100/100/100. 1000 px'te hero yüksekliği 626 px'ten 404 px'e indi; ana logolar/görseller yüklü, yatay overflow yok. Screenshot unavailable, responsive viewport simülasyonu yapılmadı. Exact CI head/run PR'da. Pinned Cloud render çalıştırılmadı; yerel sürümler manifestte.
- Inspected: SR kaynak, tam yan yana karşılaştırma, fırça ve pagoda detayları.
- Human decisions: 2026-10-10'da kullanıcı SVG'yi “Güzel. Bu SVG'yi kitleyelim” diyerek açıkça onayladı ve kilitlenmesini istedi. Sonraki kullanıcı isteği ana sayfa düzenlemesiyle birlikte canlıya yansıtma talep etti; PR #73 için merge/publish izni açıktır.
- Remaining: raster gölgelemesi iki düz renge indi, en ince uçlarda curve-fit farkları; SVG-format bağımsız CI kapsamı henüz yok. Canonical/site asset hash eşitliği round verifier ile korunuyor.
- Delivery: PR #73 user's live-publish authorization received; merge only after latest main/head and exact CI recheck, then verify Pages deployment and live URL/hash.
