# Çin Eğitim — zeminli sosyal profil serisi

Request: existing approved logo, background-filled social profile pictures, circular options and browser-friendly backgrounds, published on the Çin Eğitim design gallery.

Sources: brand.json, assets/lockups/canonical-lockups.json (2026-10-14 selection), and decisions/2026-10-10-symbol-svg-lock.md. No full brand-system approval is inferred. This application spec derives only from those selected assets.

- Exact canonical symbol SHA-256: 1cc1808947d8f7f759ebb9956a715d535bb4fcc985d3f85194d4eaf1a85c7381. Path data, transforms, stroke, fill-rule and aspect ratio remain unchanged.
- White: #FFFFFF background, original #BF0C1A brush ring / #202020 pagoda.
- Red: #BF0C1A background, #FFFFFF complete symbol; negative white is an existing mono-white logo-family colour variant.
- Dark: #141414 background (existing D-04 dark avatar source), #BF0C1A brush ring / #FFFFFF pagoda (existing D-04 dark variant).
- Profile exports: 1080×1080 square opaque backgrounds for social upload. Circle exports have a filled disk, with transparency only outside the disk. Do not upload a transparent-circle PNG when a platform expects an opaque square.
- Symbol viewport: 68% of canvas height, centred, original 916:924 ratio. Bounding rectangle remains inside the circular crop. Favicon uses the same placement at 64×64.
- No wordmark inside tiny avatars. Gallery uses selected Source Serif 4 SemiBold 600 + Manrope; downloadable avatar art contains no fonts.
- Production: local macOS stdlib Python + installed librsvg 2.63.0 deterministic vector rasterization. This is a new native SVG recipe, not a claim that the pinned Linux/Chromium campaign recipe ran. setup.sh refused the local Python 3.14 runtime; no dependencies or model APIs installed.
- New applications are reviewable outputs; publishing the gallery does not label them human-approved or post them to social accounts.

User correction (2026-10-15): replace the cream/ivory background with pure #FFFFFF. White is also an existing logo-family palette token. This revision supersedes series 01 for public profile downloads; red/dark variants are retained.
