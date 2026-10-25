"""Published browser-editable sources may not reference broken or machine-local media URLs."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[3]
DOCS=(ROOT/"docs").resolve()
REF=re.compile(r"""(?:\b(?:src|href|xlink:href)\s*=\s*["']([^"']+)["']|url\(\s*["']?([^"')\s]+))""",re.I)
MEDIA=re.compile(r"\.(?:png|jpe?g|webp|svg|woff2?|ttf|otf)(?:[?#]|$)",re.I)

class PublishedAssetIntegrityTests(unittest.TestCase):
    def test_every_editable_source_has_resolvable_local_media(self):
        catalog=json.loads((DOCS/"visual-editor/browser/catalog.json").read_text(encoding="utf-8"))
        sources=sorted({path for item in catalog if item["kind"]=="html" for path in item["pages"] if "/source/" in path or "/editable/" in path})
        self.assertGreaterEqual(len(sources),100)
        checked=0
        for rel in sources:
            source=(DOCS/rel).resolve()
            self.assertTrue(source.is_relative_to(DOCS))
            self.assertTrue(source.is_file(),rel)
            content=source.read_text(encoding="utf-8")
            for match in REF.finditer(content):
                href=(match.group(1) or match.group(2)).strip()
                if not MEDIA.search(href) or href.startswith(("data:","#")): continue
                parsed=urlsplit(href)
                if parsed.scheme in ("http","https"):continue
                with self.subTest(source=rel,asset=href):
                    self.assertFalse(parsed.scheme or parsed.netloc,"External or unsafe local media URI")
                    raw=unquote(parsed.path)
                    if raw.startswith("/design/"):
                        resolved=(DOCS/raw.removeprefix("/design/")).resolve()
                    elif raw.startswith("/"):
                        self.fail("Machine-local absolute media path in public source")
                    else:
                        resolved=(source.parent/raw).resolve()
                    self.assertTrue(resolved.is_relative_to(DOCS),"Media path leaves published docs")
                    self.assertTrue(resolved.is_file(),"Published media file is missing")
                checked+=1
        self.assertGreaterEqual(checked,100,"Expected real HTML source media coverage")

if __name__=="__main__":unittest.main()
