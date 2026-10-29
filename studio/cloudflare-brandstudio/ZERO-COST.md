# Zero-charge design contract — Brandstudio

## Absolute preference: fail closed, never silently bill

Brandstudio may use **Cloudflare Pages Free**, **Workers Free** and **D1 Free**
only. It must refuse work / report quota exhaustion instead of upgrading,
billing for overages, or switching to a paid feature. Do not infer that the
user's broader Cloudflare account has a zero-dollar cap.

**R2 is deliberately unused:** no R2 binding, bucket, client, object or
upload is created by Brandstudio. The account's R2 subscription might still
exist, but it is outside this repository. Cloudflare's budget alerts are
**notifications only**, not spend-blocking controls. If absolutely no R2
exposure is acceptable, cancel the R2 subscription in Cloudflare Billing
after verifying no other applications rely on it. No cancellation was
performed in code.

## Safe architecture

| Feature | Backend | Guard |
| --- | --- | --- |
| Published HTML/CSS/typographic SVG/fonts | Cloudflare Pages Free | max 19,000 files; max 25 MiB/file; max 1.4 GB output (self-imposed) |
| Very large downloadable historical ZIPs | Existing GitHub Pages | explicit 302 redirect; no Cloudflare R2 traffic |
| Catalog / tiny optional editor states | D1 Free, *once authenticated* | no writes until Access/owner authorization and quota tests pass |
| APIs / health | Workers Free | current mode read-only; Cloudflare fail-closed quota |
| Instagram PNG render | User's browser / existing prompt runner | Cloudflare paid Browser Rendering and Images forbidden |
| AI production | ChatGPT/other user-selected model | no automatic Workers AI billing |
| Revisions | Local/editor JSON or protected D1 later | no server write in current deployment |

Pages Free: 500 builds/month (1 concurrent), max 20,000 assets, max 25 MiB/file;
we enforce a lower file count and total payload as a conservative self-limit.
Workers Free: 100k requests/day; at exhaustion requests stop rather than
upgrading. D1 Free: query limits fail at exhaustion; no monetary overage on
that plan. These guarantees require actually staying on the respective Free
plans; account plan details were not verifiable through the current OAuth
connection.

## Prevent accidental regression

\`python3 studio/cloudflare-brandstudio/check_free_only.py\` and CI assert:
- R2, Workers AI, paid Browser Rendering and other variable-cost bindings
  are not configured;
- no Worker mutation routes or file-writing primitives;
- source export file size, count and total bytes have conservative caps;
- no auto-deploy storm until free build quotas are independently confirmed;
- lack of D1 access is an error, not a fallback to a billable backend.

A human-approved design or paid-plan change never follows automatically.
Revising the safety policy must be a separate explicit PR. Production DNS is
not switched automatically.

## Current external limitation

R2 subscription activation can enable usage-based billing independently
of the Brandstudio code. The repository checks do not control account-wide
billing (including the existing chat-handoff Worker and any unrelated
services). Cloudflare billing budget alerts **do not** pause or cap usage.
Their OAuth connector also cannot read the account's actual billing usage.
For truly zero financial exposure, use only non-billable free plans and
disable usage-billed services at the account level. R2 currently has no
buckets/objects in this account.

References:
- https://developers.cloudflare.com/r2/pricing/
- https://developers.cloudflare.com/billing/manage/budget-alerts/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/d1/platform/pricing/
- https://developers.cloudflare.com/pages/platform/limits/

## Güncelleme — 29 Ekim 2026: GitHub yetkili bulut düzenleme arşivi

Önceki bölümlerde anlatılan **yerel JSON/kayıt akışı** hâlâ isteğe bağlı yedektir; artık tek seçenek değildir. Tarayıcı editörü ayrıca doğrudan GitHub API üzerinden `brandstudio-editor-history` dalına, kullanıcı tarafından açıkça girilen yalnızca bu repo için Contents:write izni olan bir token ile yazabilir. Token sadece sekme belleğinde tutulur. **Buluta kaydet** mevcut v1/v2 vb. editör düzenlemesinin üzerine kaydeder; her kayıt anlık snapshot ile zaman damgalı geri yükleme günlüğü oluşturur. **+ Yeni sürüm** isteğe bağlıdır. Kaynak HTML ve onaylı logoların `main` sürümlerine dokunulmaz. Bulut dalı herkese açık depodadır. Detay: [GITHUB-CLOUD-REVISIONS.md](GITHUB-CLOUD-REVISIONS.md).

PNG/JPEG görsel çıktıları ücretsiz olarak, tarayıcıda paketlenmiş `html2canvas` ile üretilir; görüntü kalitesi yayımlanmadan önce kontrol edilmelidir. Cloudflare Worker ve D1 yazma API'leri **hâlâ kapalıdır**; GitHub'a doğrudan yazmak Cloudflare'da ücretli kaynak tüketmez.
