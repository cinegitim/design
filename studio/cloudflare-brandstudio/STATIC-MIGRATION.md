# Cloudflare Pages Git deployment (personal account)

Cloudflare Pages project: brandstudio-migration. Git repository: cinegitim/design; branch main; build command: `python3 studio/cloudflare-brandstudio/build_pages.py`; output: `studio/cloudflare-brandstudio/dist`. Source `docs/` is preserved byte-for-byte, except ZIP archives exceeding Cloudflare Pages' 25 MiB per-asset ceiling; these get explicit 302 redirects to the unchanged GitHub Pages URLs until they are migrated to R2 with verified hashes.

This is a **static-hosting migration** and does not enable private editor writes. A successful Pages deploy must be verified by live HTML/image/font/icon routes and by checking redirects to any missing oversized releases. Full independence requires migrating those ZIPs, authenticated browser editing and persistent renders. Legacy site and DNS stay unchanged until all checks pass.

Cloudflare identity: personal iakfiratt@gmail.com; not Asya'da Eğitim account. The existing personal chat-handoff Worker and D1 are outside scope.
