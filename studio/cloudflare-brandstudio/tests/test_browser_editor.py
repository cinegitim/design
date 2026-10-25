"""Static browser editor must remain no-cost and source-preserving."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]

class BrowserEditorTests(unittest.TestCase):
    def setUp(self):
        self.editor=(ROOT/"docs/visual-editor/browser/index.html").read_text(encoding="utf-8")
        self.gateway=(ROOT/"docs/visual-editor/index.html").read_text(encoding="utf-8")
    def test_gateway_offers_cloudflare_safe_browser_editor(self):
        self.assertIn('href="browser/"',self.gateway)
        self.assertIn("target.searchParams.set('product',product)",self.gateway)
        self.assertIn("location.replace(target.href)",self.gateway)
        self.assertNotIn('id="open-editor"',self.gateway)
        self.assertNotIn("127.0.0.1:8765",self.gateway)
    def test_editor_is_read_only_to_any_remote_server(self):
        self.assertIn("localStorage.setItem",self.editor)
        self.assertIn("showDirectoryPicker",self.editor)
        self.assertIn("getDirectoryHandle('versions'",self.editor)
        self.assertNotIn("method:'POST'",self.editor)
        self.assertNotIn("method: 'POST'",self.editor)
        self.assertNotIn("api.github.com",self.editor)
        self.assertNotIn("R2.put",self.editor)
    def test_version_is_append_only_and_authorized_by_dialog(self):
        self.assertIn("getDB()",self.editor)
        self.assertIn("$('dialog').showModal()",self.editor)
        self.assertIn("updated={versions:(db.versions||[]).concat(item)}",self.editor)
        self.assertIn("localStorage.setItem(key,JSON.stringify(updated))",self.editor)
        self.assertIn("v1",self.editor)
        self.assertIn("25 sürüm sınırı",self.editor)
    def test_source_is_provenance_preserved(self):
        self.assertIn("'../../instagram/'+slug+'/source/'",self.editor)
        self.assertIn("sandbox=\"allow-same-origin\"",self.editor)
        self.assertIn("doc.querySelector('.slide').dataset.slideIndex",self.editor)
        self.assertIn("data-edit-index",self.editor)
        self.assertIn("var(--paper)",self.editor)

if __name__=="__main__": unittest.main()
