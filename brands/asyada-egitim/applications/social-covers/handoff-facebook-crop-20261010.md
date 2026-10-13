# Facebook desktop crop correction — 2026-10-10

- **Executor:** OpenCode; isolated task branch `publish/opencode-facebook-cover-crop-20261010`.
- **Trigger:** Human-provided screenshot of the live Facebook Page after v04 upload.
- **Finding:** The visible desktop cover measured approximately 1920×696 in the screenshot (~2.76:1). The previous 16:9 upload had unnecessary vertical canvas; Facebook center-cropped it to a much wider display frame. Key text remained visible, but the upload geometry did not match the actual page preview.
- **Correction:** Desktop export is now 1702×617 (2×, ~2.76:1) with the same composition positioned directly in the visible frame; the divider reaches the bottom as in the reference screenshot. Existing mobile export stays 1704×710 (2.4:1).
- **Source conflict:** Meta Help Center currently says desktop 16:9 and mobile 2.4:1, and separately lists 851×315 as a fastest-loading example. Those statements conflict with each other and with the supplied desktop screenshot. This application follows the user's actual account screenshot for desktop, not a universal-spec claim; viewport/account UI may vary.
- **Identity:** Exact D-04/light manifest-listed SVG; canonical lockup and seal hashes unchanged.
- **Inspection:** New PNG read and visually inspected against the supplied screenshot. Desktop crop, slogan, country list and left profile-photo overlap zone reviewed.
- **Status:** Application-only crop adjustment; not a canonical template change.
