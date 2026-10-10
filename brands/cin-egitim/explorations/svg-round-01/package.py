#!/usr/bin/env python3
"""Package existing review files; no generation or tracing."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

BUNDLE = Path(__file__).resolve().parent
ROOT = BUNDLE.parents[3]
PUBLIC = ROOT / "docs/cin-egitim/svg-round-01"


def main():
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    names = sorted(list(manifest["files"]) + ["manifest.json", "build.py", "verify.py",
                   "package.py", "README.md", "quality-review.md", "handoff.md", "index.html"])
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copyfile(BUNDLE / name, PUBLIC / name)
    package = PUBLIC / "svg-round-01.zip"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (BUNDLE / name).read_bytes())
    record = {"status": "REVIEW_ONLY", "package": package.name,
              "sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
              "bytes": package.stat().st_size, "members": names}
    for folder in (BUNDLE, PUBLIC):
        (folder / "delivery.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
