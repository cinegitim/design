#!/usr/bin/env python3
"""Promote the human-approved Asya'da Eğitim lockups to canonical assets.

This copies the exact approved 0-alignment artwork from the final review, only
replacing review/pending metadata with production metadata. It never retypesets,
refits, redraws, smooths, recolours beyond the approved source variant, or edits
canonical seal geometry.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/asyada-seal/final-lockups/assets"
DEST = ROOT / "brands/asyada-egitim/assets/lockups"
DOC = ROOT / "docs/asyada-seal/canonical-lockups"
SEAL = ROOT / "brands/asyada-egitim/assets/v01-canonical.svg"
BRAND_JSON = ROOT / "brands/asyada-egitim/brand.json"
MANIFEST = DEST / "canonical-lockups.json"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BRAND_ID = "asyada-egitim"
SEAL_SHA = "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a"
WORDMARK_SHA = "668c0026043cf6ab2496c67feca152da37ad8348d2b6641a354a841b58e375f3"
APPROVAL_DATE = "2026-10-08"
VARIANTS = {
    "P-01": {"name": "Primary stacked", "source": "P-01", "min_px": 352, "min_mm": 75, "usage": "Default stacked brand signature for covers, formal pages, profile pages and centered layouts.", "format": "bilingual_three_line"},
    "H-02": {"name": "Primary horizontal", "source": "H-02", "min_px": 528, "min_mm": 110, "usage": "Wide mastheads, website headers, institutional documents and horizontal signatures.", "format": "bilingual_three_line"},
    "C-03": {"name": "Compact", "source": "C-03", "min_px": 448, "min_mm": 95, "usage": "Tighter bilingual horizontal uses such as email mastheads and constrained lockup areas.", "format": "bilingual_three_line"},
    "D-04": {"name": "Small-use digital", "source": "D-04", "min_px": 200, "min_mm": 45, "usage": "Small digital signatures and mobile navigation; Turkish only by approval; use seal-only below this size.", "format": "turkish_two_line_only"},
    "F-05": {"name": "Formal bilingual", "source": "F-05", "min_px": 352, "min_mm": 75, "usage": "Formal documents, certificates and ceremonial layouts with centered crest emphasis.", "format": "bilingual_three_line"},
}
COLORS = {
    "light": {"source": "light", "description": "Full colour for light or paper backgrounds"},
    "dark": {"source": "dark", "description": "Full colour reversed lettering for dark backgrounds"},
    "monochrome": {"source": "mono-ink", "description": "One-colour ink version for monochrome production on light backgrounds"},
}

def sha_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def rel(path: Path) -> str: return path.relative_to(ROOT).as_posix()
def clean_name(s: str) -> str: return re.sub(r"[^a-z0-9\-\.]+", "", s.lower().replace(" / ", "-").replace(" ", "-"))

def strip_review_metadata(root: ET.Element, canonical_id: str, variant: dict, color: str, source_path: Path) -> None:
    for child in list(root):
        if child.tag in {f"{{{NS}}}title", f"{{{NS}}}metadata"}:
            root.remove(child)
    root.set("role", "img")
    root.set("aria-labelledby", canonical_id.replace("/", "-") + "-title")
    title = ET.Element(f"{{{NS}}}title", {"id": canonical_id.replace("/", "-") + "-title"})
    title.text = f"Asya'da Eğitim — {variant['name']} — {color} — approved canonical lockup"
    meta = ET.Element(f"{{{NS}}}metadata")
    meta.text = json.dumps({
        "brand_id": BRAND_ID,
        "canonical_lockup_id": canonical_id,
        "status": "APPROVED / CANONICAL",
        "human_approval_date": APPROVAL_DATE,
        "source_wordmark_sha256": WORDMARK_SHA,
        "canonical_seal_sha256": SEAL_SHA,
        "typography": {"turkish": {"family": "Jost", "weight": 550}, "english": {"family": "Jost", "weight": 350}},
        "approved_alignment": 0,
        "geometry_change_from_approved_review_asset": False,
        "image_generation": False,
    }, ensure_ascii=False, sort_keys=True)
    root.insert(0, meta); root.insert(0, title)

def copy_clean_svg(variant_id: str, color: str, spec: dict, color_spec: dict) -> dict:
    source = SRC / f"{spec['source']}-{color_spec['source']}-0.svg"
    root = ET.fromstring(source.read_bytes())
    canonical_id = f"{variant_id}/{color}"
    strip_review_metadata(root, canonical_id, spec, color, source)
    data = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    filename = f"{variant_id.lower()}-{clean_name(spec['name'])}-{color}.svg"
    out = DEST / filename; out.write_bytes(data)
    return {
        "brand_id": BRAND_ID, "variant_id": variant_id, "variant_name": spec["name"], "color_variant": color,
        "canonical_lockup_id": canonical_id, "canonical_file_path": rel(out), "sha256": sha_bytes(data),
        "source_review_path": rel(source), "source_review_sha256": sha_bytes(source.read_bytes()),
        "canonical_seal_sha256": SEAL_SHA,
        "typography": {"turkish": {"family": "Jost", "weight": 550, "source": "Approved outlined paths from tr550-en350-wordmark.svg"}, "english": {"family": "Jost", "weight": 350, "source": "Approved outlined paths from tr550-en350-wordmark.svg"}, "apostrophe": "Original approved red vector apostrophe from selected outlined source", "runtime_font_dependency": False},
        "provenance": {"source_wordmark_path": "docs/asyada-seal/typography-weights/assets/tr550-en350-wordmark.svg", "source_wordmark_sha256": WORDMARK_SHA, "source_final_review_asset": rel(source), "approved_review_page": "docs/asyada-seal/final-lockups/index.html"},
        "approved_alignment": 0, "alignment_scope": "0 for both horizontal and stacked/vertical compositions",
        "human_approval_date": APPROVAL_DATE, "status": "APPROVED / CANONICAL",
        "minimum_supported_display_size": {"screen_width_px": spec["min_px"], "print_width_mm": spec["min_mm"]},
        "format": spec["format"],
        "usage_rules": [
            spec["usage"],
            "Use this complete SVG as a locked artwork unit; do not reconstruct from separate seal and text geometry.",
            "Allow proportional scaling and positioning only; never stretch, crop, recolour outside the approved colour variant, perspective-warp, trace, smooth or retypeset.",
            "Respect the embedded clearspace and minimum size. If the space cannot hold an approved lockup, use another approved variant or flag the constraint.",
            "Image models may generate backgrounds only; composite this exact SVG afterward and record canonical_lockup_id, canonical_lockup_sha256 and canonical_seal_sha256.",
        ] + (["D-04 is Turkish only; do not add English text."] if variant_id == "D-04" else ["Bilingual lockup uses the shared 881-unit three-line measure."]),
        "contrast_caveats": ["Red apostrophe on dark background is intentionally retained from approval; use monochrome only when a one-colour high-contrast signature is required.", "Fine English line depends on normal antialiasing at minimum size; do not disable antialiasing or shrink below minimum."],
    }

def make_gallery(records: list[dict], manifest_sha: str) -> None:
    cards=[]
    for variant_id, spec in VARIANTS.items():
        cards.append(f'<section class="variant" id="{variant_id}"><div class="variant-head"><p class="eyebrow">{variant_id}</p><h2>{spec["name"]}</h2><p>{spec["usage"]}</p><p class="meta">Minimum: {spec["min_px"]}px / {spec["min_mm"]}mm · Alignment: 0 · Status: APPROVED / CANONICAL</p></div><div class="modes">')
        for color in COLORS:
            rec=next(r for r in records if r["variant_id"]==variant_id and r["color_variant"]==color)
            svg=(ROOT/rec["canonical_file_path"]).read_text()
            cards.append(f'<figure class="mode {color}"><div class="mark">{svg}</div><figcaption>{color}<br><code>{Path(rec["canonical_file_path"]).name}</code><br><span>{rec["sha256"][:16]}…</span></figcaption></figure>')
        cards.append('</div></section>')
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Asya'da Eğitim — Canonical logo lockups</title><style>
:root{{--paper:#F7F3E9;--ink:#1D2027;--red:#BD2120;--line:#d9d1bf}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}}main{{max-width:1220px;margin:auto;padding:48px 28px 90px}}h1{{font-size:clamp(42px,7vw,82px);line-height:1.02;letter-spacing:-.055em;margin:0 0 22px;max-width:11ch}}h2{{font-size:32px;margin:0;letter-spacing:-.035em}}.eyebrow{{font:11px/1.4 ui-monospace,monospace;letter-spacing:.1em;color:#6a645a;text-transform:uppercase}}.status{{border-block:1px solid var(--ink);padding:16px 0;margin:34px 0;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}.status b{{color:var(--red);font:12px ui-monospace,monospace;letter-spacing:.04em}}.variant{{border-top:1px solid var(--ink);margin-top:54px;padding-top:28px}}.variant-head{{display:grid;grid-template-columns:280px 1fr;gap:36px;align-items:start}}.meta{{font-size:13px;color:#625d53}}.modes{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:26px}}figure{{margin:0;border:1px solid var(--line);padding:20px;background:#ece7dc}}figure.dark{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}figure.monochrome{{background:#fffdf7}}.mark{{height:300px;display:grid;place-items:center}}.mark svg{{width:100%;height:100%;max-height:280px}}figcaption{{font-size:12px;color:#6a645a}}figure.dark figcaption{{color:#d9d1bf}}code{{font-size:11px;overflow-wrap:anywhere}}a{{color:inherit}}@media(max-width:780px){{main{{padding:30px 16px 70px}}.variant-head{{grid-template-columns:1fr}}.modes{{grid-template-columns:1fr}}.mark{{height:240px}}}}</style></head><body><main>
<p class="eyebrow">ASYA'DA EĞİTİM / CANONICAL ASSET GALLERY</p><h1>Approved logo lockups.</h1><p>These are the only approved unified Asya'da Eğitim lockup SVGs. Use each as a complete artwork unit; do not reassemble, redraw or re-typeset.</p><div class="status"><b>APPROVED / CANONICAL</b><span>Human approval date: {APPROVAL_DATE} · Manifest SHA-256: <code>{manifest_sha}</code></span></div>
{''.join(cards)}
<section class="variant"><p class="eyebrow">Verification</p><h2>Production gate</h2><p>Run <code>python3 studio/tools/verify_asyada_canonical_lockups.py</code>. Every final branded output must record <code>canonical_lockup_id</code>, <code>canonical_lockup_sha256</code> and <code>canonical_seal_sha256</code>.</p><p><a href="../../assets/lockups/canonical-lockups.json">Canonical manifest</a> · <a href="../../assets/lockups/verification-result.json">Latest verification result</a> · <a href="../final-lockups/">Archived final approval review</a></p></section>
</main></body></html>'''
    (DOC/"index.html").write_text(html)

def update_brand_json(records:list[dict], manifest_sha:str)->None:
    data=json.loads(BRAND_JSON.read_text())
    data["canonicalLockups"]={"locked":True,"status":"APPROVED / CANONICAL","approvedOn":APPROVAL_DATE,"manifest":rel(MANIFEST),"manifestSha256":manifest_sha,"sourceReview":"docs/asyada-seal/final-lockups/","canonicalSealSha256":SEAL_SHA,"typography":{"turkish":"Jost 550","english":"Jost 350","runtimeFonts":False},"approvedAlignment":{"horizontal":0,"stackedVertical":0},"approvedVariants":sorted(VARIANTS.keys()),"approvedColorVariants":sorted(COLORS.keys()),"usageGate":"Run studio/tools/verify_asyada_canonical_lockups.py before publishing; use only manifest-listed complete SVGs.","outputManifestRequired":["canonical_lockup_id","canonical_lockup_sha256","canonical_seal_sha256"],"records":[{"canonical_lockup_id":r["canonical_lockup_id"],"path":r["canonical_file_path"],"sha256":r["sha256"]} for r in records]}
    req=set(data.get("outputManifestRequired",[])); req.update(["canonical_logo_sha256","canonical_lockup_id","canonical_lockup_sha256","canonical_seal_sha256"]); data["outputManifestRequired"]=sorted(req)
    BRAND_JSON.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")

def main()->None:
    if sha_bytes(SEAL.read_bytes())!=SEAL_SHA: raise SystemExit("Canonical seal hash mismatch; stop.")
    DEST.mkdir(parents=True,exist_ok=True); DOC.mkdir(parents=True,exist_ok=True)
    records=[copy_clean_svg(variant_id,color,spec,color_spec) for variant_id,spec in VARIANTS.items() for color,color_spec in COLORS.items()]
    manifest={"brand_id":BRAND_ID,"status":"APPROVED / CANONICAL","human_approval_date":APPROVAL_DATE,"canonical_seal_path":rel(SEAL),"canonical_seal_sha256":SEAL_SHA,"typography":{"turkish":{"family":"Jost","weight":550},"english":{"family":"Jost","weight":350},"provenance":"Approved final-lockups review; glyphs are outlined paths."},"approved_alignment":{"horizontal":0,"stacked_vertical":0},"common_measure":{"bilingual_three_line_width_units":881,"applies_to":["P-01","H-02","C-03","F-05"]},"d_04_rule":"TURKISH ONLY. Do not add English text.","allowed_operations":["proportional scaling","positioning","approved colour variant selection"],"forbidden_operations":["redraw","retype","font substitution","image model lettering","distortion","cropping","perspective transform","unapproved recolouring","reconstructing from separate seal and text geometry"],"final_output_manifest_required":["canonical_lockup_id","canonical_lockup_sha256","canonical_seal_sha256"],"records":records}
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    manifest_sha=sha_bytes(MANIFEST.read_bytes()); manifest["manifest_sha256_sidecar"]=manifest_sha
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
    manifest_sha=sha_bytes(MANIFEST.read_bytes())
    (DEST/"canonical-lockups.sha256").write_text(f"{manifest_sha}  canonical-lockups.json\n")
    update_brand_json(records,manifest_sha); make_gallery(records,manifest_sha)
    # Sync production gallery assets for Pages; canonical source remains brands/assets/lockups.
    (DOC/"assets").mkdir(parents=True,exist_ok=True)
    for r in records:
        (DOC/"assets"/Path(r["canonical_file_path"]).name).write_bytes((ROOT/r["canonical_file_path"]).read_bytes())
    (DOC/"assets"/"canonical-lockups.json").write_bytes(MANIFEST.read_bytes())
    try:
        (DOC/"assets"/"verification-result.json").write_bytes((DEST/"verification-result.json").read_bytes())
    except FileNotFoundError:
        pass
    # Rewrite gallery links to local production copies (Pages-safe, no ../../ traversal).
    g=DOC/"index.html"; gt=g.read_text()
    gt=gt.replace('../../assets/lockups/canonical-lockups.json','assets/canonical-lockups.json')
    gt=gt.replace('../../assets/lockups/verification-result.json','assets/verification-result.json')
    g.write_text(gt)
    print(json.dumps({"canonical_asset_directory":rel(DEST),"records":len(records),"manifest":rel(MANIFEST),"manifest_sha256":manifest_sha},indent=2))
if __name__=="__main__": main()
