# Local preservation audit — cloud handover

The old working folder was inspected without deletion. Its **242 ignored + 11
untracked = 253 files** are classified in `local-preservation.json` against the
GitHub baseline commit recorded there.

- **14 files copied intact**, comprising **12 byte-unique creative/documentary
  files** and 2 duplicates kept to make one exploration folder complete.
- **208 duplicate files** map to exact tracked repository paths/hashes.
- **1 legacy ZIP** contains 83 creative entries already tracked and 2 Finder
  metadata entries. Every creative ZIP entry has an exact checksum mapping.
- **30 runtime/metadata/cache files** remain outside public GitHub: preview server
  records/logs can expose temporary URLs/IPs/local paths. They are not creative outputs.
- Additionally, 11 accidentally tracked Python bytecode files in the current repo
  were removed from **Git tracking only**; no local source/work was deleted.

Preserved locations:
- `studio/archive/migration-20261001/`: historical workspace instructions / brief template.
- `brands/asyada-egitim/archive/historical-share-gallery/original.html`: exact
  historical gallery HTML bytes. Its relative links are historical, not repointed;
  imagery mapping is in the checksum manifest. This is an archival document, not
  a new live/current presentation or identity approval.
- `brands/asyada-egitim/explorations/instagram-profile-circle/`: complete 11-file
  unapproved exploration. No promotion into approved assets.

The migration audit verifies preserved copies plus duplicate bytes in the
recorded Git history. Referenced live files may later evolve without losing that
archival baseline. Raw local runtime logs and the redundant ZIP are not uploaded.

**Preservation is not cutover.** Codex Cloud account activation, actual Linux
production smoke test and any raster connector test remain separate. Keep the
old working folder until those checks and human review pass. This audit is not
a backup of every machine file, OpenCode session database or account credential.
