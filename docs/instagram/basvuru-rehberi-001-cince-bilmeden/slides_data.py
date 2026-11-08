# -*- coding: utf-8 -*-
"""Shared slide-definition data and helpers for the six-slide carousel.

Exact locked copy lives here and nowhere else. No paraphrase, no omissions.
"""
import base64, hashlib, json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/private/var/folders/3j/ffljsl_s66n94xjq7zdv8hb80000gn/T/opencode/basvuru-rehberi-001')
BUNDLE = 'docs/instagram/basvuru-rehberi-001-cince-bilmeden'
ASSETS = HERE / 'assets'
PHOTOS = HERE / 'photos'
SOURCE = HERE / 'source'
FINAL = HERE / 'final'
ORIGINALS = HERE / 'originals'
W, H = 1080, 1350

BRAND_RED, INK, PAPER = '#BD2120', '#1D2027', '#F7F3E9'
CHINA_RED = '#DE2910'
GOLD_IMP, GOLD_BRIGHT, IVORY = '#D9A441', '#F3C64D', '#F4E8D3'
SEAL_SHA = '8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a'
CANON = ROOT / 'brands/asyada-egitim/assets/lockups/canonical-lockups.json'
JOST_SRC = ROOT / 'brands/asyada-egitim/explorations/wordmark-ref/weight-study/sources/Jost-VF.ttf'
CJK_SRC = Path(__file__).resolve().parent / 'assets' / 'SongtiSC-CJK-subset.ttf'

L1 = 'assets/Jost-VF.ttf'
C1 = 'assets/SongtiSC-CJK-subset.ttf'

# ---------------------------------------------------------------- exact copy
# Each slide: the exact Turkish copy split at spaces only where a line break
# is required. Joining with a single space reproduces the locked text.
COPY = {
 '01-cover': [
   'BAŞVURU REHBERİ / 001',
   'Çince bilmiyorum.',
   "Çin'de okuyabilir miyim?",
   'Evet.',
   "Çin'de İngilizce lisans, yüksek lisans ve doktora programları var.",
 ],
 '02-fields': [
   'LİSANS / İNGİLİZCE EĞİTİM',
   "Çin'de İngilizce hangi bölümleri okuyabilirsin?",
   'Mühendislik · Bilgisayar ve Yazılım',
   'İşletme · Finans · Ekonomi',
   'Tıp · Sağlık Bilimleri',
   'Sosyal Bilimler · Uluslararası İlişkiler',
   'Mimarlık · Tasarım',
   'Ve çok daha fazlası.',
   'Programların öğretim dili üniversiteye ve bölüme göre değişir.',
 ],
 '03-atlas': [
   'LİSANS / NEREDE OKUYABİLİRSİN?',
   'Pekin, Şanghay, Hangzhou...',
   'PEKİN ·', 'TSINGHUA UNIVERSITY',
   'Bilim ve Mühendislik',
   'ŞANGHAY ·', 'SHANGHAI UNIVERSITY',
   'Finans · Uluslararası Ticaret · Dijital Pazarlama',
   'HANGZHOU ·', 'ZHEJIANG UNIVERSITY',
   'Tıp (İngilizce MBBS)',
   'Suzhou, Ningbo ve başka şehirlerde de',
   'İngilizce program seçenekleri var.',
 ],
 '04-masters': [
   'YÜKSEK LİSANS / İNGİLİZCE EĞİTİM',
   "Lisansı Türkiye'de bitirdin.",
   "Çin'de yüksek lisans yapabilir misin?",
   'Evet. İngilizce programlar var.',
   'SHANGHAI UNIVERSITY',
   'Finans · Uluslararası İşletme',
   'TSINGHUA UNIVERSITY',
   'Küresel Yönetişim',
   'FUDAN UNIVERSITY',
   'Kamu Politikası',
   'Başka üniversitelerde de İngilizce programlar var.',
 ],
 '05-doctorate': [
   'DOKTORA / İNGİLİZCE EĞİTİM',
   'Çince bilmeden doktora yapabilir misin?',
   'Evet. İngilizce doktora programları da var.',
   'SHANGHAI UNIVERSITY',
   'Küresel Çalışmalar · Finans · Malzeme Bilimi',
   'FUDAN UNIVERSITY',
   'Uluslararası Politika · Matematik',
   'Sunulan alanlar bununla sınırlı değil.',
   'Araştırma alanı, danışman ve kabul koşulları programa göre değişir.',
 ],
 '06-dossier': [
   'BAŞVURU REHBERİ / 001',
   "Çin'de üniversiteye başvurmak için diploma yetmiyor.",
   'Başvuruda istenebilen belgeler:',
   'Pasaport',
   'Diploma ve', 'transkript',
   'İngilizce yeterlilik', 'belgesi',
   'Akademik sınav', 'sonuçları',
   'Niyet veya', 'araştırma planı',
   'Akademik', 'referanslar',
   'Mali durum', 'belgesi',
   'Ve programa göre daha fazlası.',
   'Bazı üniversiteler mülakat, adli sicil belgesi ve resmî',
   'çeviri de istiyor.',
   'Program seçimi ve başvuru dosyanı birlikte hazırlayalım.',
   'Ücretsiz ön görüşme',
 ],
}

# Supplied locked copy, complete. Slide 06 line 15 "Asya'da Eğitim" is delivered
# by the approved canonical lockup (D-04/dark) as an <image>, never retypeset,
# so it is absent from COPY and from the SVG copy group by design.
SUPPLIED = {
 '01-cover': [
   'BAŞVURU REHBERİ / 001',
   'Çince bilmiyorum.',
   "Çin'de okuyabilir miyim?",
   'Evet.',
   "Çin'de İngilizce lisans, yüksek lisans ve doktora programları var.",
 ],
 '02-fields': None,
 '03-atlas': [
   'LİSANS / NEREDE OKUYABİLİRSİN?',
   'Pekin, Şanghay, Hangzhou...',
   'PEKİN · TSINGHUA UNIVERSITY',
   'Bilim ve Mühendislik',
   'ŞANGHAY · SHANGHAI UNIVERSITY',
   'Finans · Uluslararası Ticaret · Dijital Pazarlama',
   'HANGZHOU · ZHEJIANG UNIVERSITY',
   'Tıp (İngilizce MBBS)',
   'Suzhou, Ningbo ve başka şehirlerde de İngilizce program seçenekleri var.',
 ],
 '04-masters': [
   'YÜKSEK LİSANS / İNGİLİZCE EĞİTİM',
   "Lisansı Türkiye'de bitirdin. Çin'de yüksek lisans yapabilir misin?",
   'Evet. İngilizce programlar var.',
   'SHANGHAI UNIVERSITY',
   'Finans · Uluslararası İşletme',
   'TSINGHUA UNIVERSITY',
   'Küresel Yönetişim',
   'FUDAN UNIVERSITY',
   'Kamu Politikası',
   'Ve çok daha fazlası.',
 ],
 '05-doctorate': [
   'DOKTORA / İNGİLİZCE EĞİTİM',
   'Çince bilmeden doktora yapabilir misin?',
   'Evet. İngilizce doktora programları da var.',
   'SHANGHAI UNIVERSITY',
   'Küresel Çalışmalar · Finans · Malzeme Bilimi',
   'FUDAN UNIVERSITY',
   'Uluslararası Politika · Matematik',
   'Ve çok daha fazlası.',
   'Araştırma alanı, danışman ve kabul koşulları programa göre değişir.',
 ],
 '06-dossier': [
   'BAŞVURU REHBERİ / 001',
   "Çin'de üniversiteye başvurmak için diploma yetmiyor.",
   'Başvuruda istenebilen belgeler:',
   'Pasaport', 'Diploma ve transkript', 'İngilizce yeterlilik belgesi',
   'Akademik sınav sonuçları', 'Niyet veya araştırma planı',
   'Akademik referanslar', 'Mali durum belgesi',
   'Ve programa göre daha fazlası.',
   'Bazı üniversiteler mülakat, adli sicil belgesi ve resmî çeviri de istiyor.',
   'Program seçimi ve başvuru dosyanı birlikte hazırlayalım.',
   'Ücretsiz ön görüşme',
   "Asya'da Eğitim",
 ],
}

# --------------------------------------------------------------- lockup plan
# Canonical colour variants follow the approved naming:
#   'light' -> #1D2027 letterforms  -> LIGHT backgrounds (ink wordmark)
#   'dark'  -> #F7F3E9 letterforms  -> DARK  backgrounds (paper wordmark)
# Slide 06 uses the primary horizontal lockup H-02 for a proper closing
# signature (D-04 is the small-use digital variant and is too weak there).
LOCKUP = {
 '01-cover':    ('D-04/dark',   [66, 1176], 340),
 '02-fields':   ('D-04/light',  [714, 44], 300),
 '03-atlas':    ('D-04/dark',   [674, 1176], 340),
 '04-masters':  ('D-04/dark',   [66, 1176], 340),
 '05-doctorate':('D-04/dark',   [674, 1176], 340),
 '06-dossier':  ('H-02/light',  [276, 1108], 528),
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def font_css() -> str:
    """Embed Jost and the CJK subset so rendering never depends on the host."""
    jost = base64.b64encode(JOST_SRC.read_bytes()).decode()
    cjk = base64.b64encode(CJK_SRC.read_bytes()).decode()
    return (f"@font-face{{font-family:Jost;src:url(data:font/ttf;base64,{jost}) "
            f"format('truetype');font-weight:100 900;font-style:normal;}}"
            f"@font-face{{font-family:SongCJK;src:url(data:font/ttf;base64,{cjk}) "
            f"format('truetype');font-weight:400;font-style:normal;}}"
            "text{font-synthesis:none;}")


def prepare_assets() -> dict:
    """Copy canonical manifest, font, CJK subset and lockups into assets/."""
    for d in (ASSETS, SOURCE, FINAL, ORIGINALS, HERE / 'mobile'):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(JOST_SRC, ASSETS / 'Jost-VF.ttf')
    if CJK_SRC != ASSETS / 'SongtiSC-CJK-subset.ttf':
        shutil.copy2(CJK_SRC, ASSETS / 'SongtiSC-CJK-subset.ttf')
    shutil.copy2(CANON, ASSETS / 'canonical-lockups.json')
    recs = {r['canonical_lockup_id']: r for r in json.loads(CANON.read_text())['records']}
    lk = ASSETS / 'lockups'
    lk.mkdir(exist_ok=True)
    for sid, (lid, _, _) in LOCKUP.items():
        rec = recs[lid]
        shutil.copy2(ROOT / rec['canonical_file_path'],
                     lk / Path(rec['canonical_file_path']).name)
    return recs
