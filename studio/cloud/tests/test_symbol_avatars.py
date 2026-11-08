"""Independent avatar rejection cases; synthetic PNGs, no renderer or producer."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile
import zlib

here = Path(__file__).resolve()
engine = here.parents[1]/'audit.py'
if not engine.exists():
    engine = here.parents[3]/'audit.py'
spec = importlib.util.spec_from_file_location('avatar_audit', engine)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

def chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)

class AvatarTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.base=self.root/'avatars'
        self.base.mkdir()
        canonical='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g fill="#202020"><path d="M10 10 L90 90"/></g></svg>'
        (self.root/'canonical.svg').write_text(canonical)
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080"><rect width="1080" height="1080" fill="#FAF7F2"/><svg id="canonical-mark" viewBox="0 0 100 100" x="216" y="216" width="648" height="648"><g fill="#202020"><path d="M10 10 L90 90"/></g></svg></svg>'
        (self.base/'avatar.svg').write_text(svg)
        (self.base/'avatar.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1080,1080,8,2,0,0,0))+chunk(b'IDAT',b'x')+chunk(b'IEND',b''))
        self.contract={'path':'avatars','format':'symbol-avatars','required_files':[], 'manifest':'manifest.json',
                       'canonical_logo_file':'canonical.svg','canonical_logo_sha256':A.digest(self.root/'canonical.svg'),
                       'exports':[{'id':'light','dimensions':[1080,1080],'shape':'square','background':'#FAF7F2','symbol_fills':['#202020']}]}
        self.manifest={'canonical_logo_sha256':self.contract['canonical_logo_sha256'],'package_file':'avatars.zip',
                       'exports':[{'id':'light','svg_file':'avatar.svg','png_file':'avatar.png'}]}
        self.package()

    def tearDown(self):
        self.temp.cleanup()

    def package(self):
        rec=self.manifest['exports'][0]
        rec['svg_sha256']=A.digest(self.base/'avatar.svg')
        rec['png_sha256']=A.digest(self.base/'avatar.png')
        (self.base/'manifest.json').write_text(json.dumps(self.manifest))
        with zipfile.ZipFile(self.base/'avatars.zip','w') as z:
            for name in ['manifest.json','avatar.svg','avatar.png']:
                z.write(self.base/name,name)

    def change(self, before, after):
        p=self.base/'avatar.svg'
        p.write_text(p.read_text().replace(before,after))
        self.package()

    def test_valid_bundle(self):
        self.assertEqual(A.audit_symbol_avatars(self.root,self.contract)['exports'],1)

    def test_changed_geometry_even_with_updated_hash(self):
        self.change('M10 10 L90 90','M10 10 L80 80')
        with self.assertRaisesRegex(A.AuditError,'geometry changed'): A.audit_symbol_avatars(self.root,self.contract)

    def test_transparent_or_incomplete_background(self):
        self.change('width="1080" height="1080" fill=', 'width="1000" height="1080" fill=')
        with self.assertRaisesRegex(A.AuditError,'background'): A.audit_symbol_avatars(self.root,self.contract)

    def test_unapproved_colour(self):
        self.change('fill="#202020"','fill="#000000"')
        with self.assertRaisesRegex(A.AuditError,'colour'): A.audit_symbol_avatars(self.root,self.contract)

    def test_active_content(self):
        self.change('</svg></svg>', '</svg><script/></svg>')
        with self.assertRaisesRegex(A.AuditError,'active SVG'): A.audit_symbol_avatars(self.root,self.contract)

    def test_crop_safety(self):
        self.change('x="216" y="216" width="648" height="648"', 'x="40" y="40" width="1000" height="1000"')
        with self.assertRaisesRegex(A.AuditError,'safe size'): A.audit_symbol_avatars(self.root,self.contract)

    def test_zip_has_identical_manifest(self):
        self.manifest['title']='Changed after packaging'
        (self.base/'manifest.json').write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(A.AuditError,'stale member'): A.audit_symbol_avatars(self.root,self.contract)

if __name__ == '__main__':
    unittest.main()
