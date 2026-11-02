"""Read-only, fail-closed P2 pilot acceptance gate.

This gate verifies *repository transport and browser geometry*, not model-host
attestation, complete raster/pixel-diff QA, creative approval, or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from threading import Thread
from urllib.parse import unquote, urlsplit

from contracts.validation import validate_bundle
from handoff.protocol import _envelope, receive, verify

PILOT = "docs/instagram/brandstudio-p2-kaist-pilot-20261102/v1"
SOURCE_BRANCH = "publish/opencode-opencode-p2-kaist-20261102"
WORK_BRANCH = "work/brandstudio-p2-kaist-20261102"
ASSET_PINS = {
    "brands/asyada-egitim/assets/lockups/h-02-primary-horizontal-dark.svg":
        "c9eb55f95a60924f34e6f7b043e81216963441833a4f158ff882d710cc8dd1e7",
    "brands/asyada-egitim/assets/v01-canonical.svg":
        "8f5d46f0302c4cc7e3765d3bfce9445f842dbd92f1e0f8fbe99f9f509c77e11a",
}


class GateError(ValueError):
    """A technical acceptance condition was not met."""


def check_geometry(data: dict, *, require_font: bool = True) -> int:
    """Check actual Chromium DOM measurements, not a CSS/source-code guess."""
    if not isinstance(data, dict) or data.get("width") != 1080 or data.get("height") != 1350:
        raise GateError("P2_RENDER_CANVAS_SIZE")
    sections = data.get("sections")
    if not isinstance(sections, list) or len(sections) != 5:
        raise GateError("P2_RENDER_SECTION_COUNT")
    top = data.get("footer_top")
    bottom = data.get("footer_bottom")
    if not isinstance(top, (int, float)) or not isinstance(bottom, (int, float)) or (
        top < 1000 or bottom > 1351 or bottom < 1348
    ):
        raise GateError("P2_RENDER_FOOTER_BOUNDS")
    for section in sections:
        if not isinstance(section, list) or len(section) != 2 or not all(
            isinstance(x, (int, float)) for x in section
        ) or section[0] < 0 or section[1] <= section[0] or section[1] > top - 4:
            raise GateError("P2_RENDER_OVERFLOW")
    images = data.get("images")
    if not isinstance(images, list) or len(images) != 3 or not all(x is True for x in images):
        raise GateError("P2_RENDER_IMAGE_MISSING")
    if require_font and data.get("font_loaded") is not True:
        raise GateError("P2_RENDER_FONT_MISSING")
    if data.get("external_requests") != 0:
        raise GateError("P2_RENDER_EXTERNAL_RESOURCE")
    return len(sections)


def check_assets(root: Path, expected: dict[str, str] | None = None) -> dict[str, str]:
    """Compare *bytes* of approved SVGs against independently pinned SHA-256."""
    root = Path(root).resolve()
    pins = ASSET_PINS if expected is None else expected
    actual = {}
    for name, digest in pins.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
            raise GateError("P2_CANONICAL_ASSET_MISSING")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha != digest:
            raise GateError("P2_CANONICAL_ASSET_DIGEST")
        actual[name] = sha
    return actual


def check_records(task, source_receipt, work_draft_receipt, target_receipt,
                  work_draft_envelope, final_envelope, source_observation,
                  target_observation, *, root: Path, source_head: str,
                  work_head: str) -> str:
    """Exercise existing P1 validators and P2 state transitions on real records."""
    root = Path(root)
    try:
        validate_bundle(task, None, source_receipt, None, root=root)
        validate_bundle(task, None, work_draft_receipt, None, root=root)
        validate_bundle(task, None, target_receipt, None, root=root)
        _envelope(work_draft_envelope)
        _envelope(final_envelope)
    except (ValueError, KeyError, TypeError) as exc:
        raise GateError("P2_CONTRACT_INVALID") from None

    if (source_receipt["head_sha"] != source_head or
        target_receipt["head_sha"] != work_head or
        work_draft_receipt["head_sha"] is not None or
        work_draft_receipt["executor"] != target_receipt["executor"] or
        work_draft_receipt["branch"] != target_receipt["branch"] or
        work_draft_receipt["base_sha"] != task["base_sha"] or
        work_draft_envelope["status"] != "source_verified" or
        work_draft_envelope["target_observed_via"] != "none" or
        final_envelope["status"] != "received" or
        final_envelope["original_base_sha"] != task["base_sha"] or
        final_envelope["source_head_sha"] != source_head or
        final_envelope["target_branch"] != target_receipt["branch"] or
        final_envelope["source_executor"] != source_receipt["executor"] or
        final_envelope["target_executor"] != target_receipt["executor"] or
        not final_envelope["receipt_ref"].startswith(task["output_ref"].rstrip("/") + "/") or
        source_observation.get("head_sha") != source_head or
        target_observation.get("head_sha") != work_head or
        target_observation.get("base_sha") != source_head or
        final_envelope["source_branch"] != source_observation.get("branch") or
        final_envelope["target_branch"] != target_observation.get("branch")):
        raise GateError("P2_RECEIPT_MISMATCH")
    if any(work_draft_envelope[key] != final_envelope[key] for key in (
        "schema_version", "task_id", "source_executor", "target_executor",
        "source_branch", "source_head_sha", "original_base_sha", "target_branch"
    )):
        raise GateError("P2_ENVELOPE_CONFLICT")
    if source_observation.get("observed_from") not in ("git-remote", "github-connector") or (
        target_observation.get("observed_from") not in ("git-remote", "github-connector")
    ):
        raise GateError("P2_REMOTE_EVIDENCE_MISSING")
    try:
        candidate = dict(final_envelope, status="prepared", observed_via="none",
                         target_observed_via="none")
        observed = verify(candidate, observation=source_observation)
        received = receive(observed, target_observation=target_observation,
                           target_receipt=target_receipt, root=root)
    except (ValueError, KeyError, TypeError):
        raise GateError("P2_TRANSPORT_VALIDATION_FAILED") from None
    if received != final_envelope:
        raise GateError("P2_FINAL_ENVELOPE_MISMATCH")
    if task["approval"]["creative"] != "pending" or task["approval"]["social_publish"]:
        raise GateError("P2_CREATIVE_OR_PUBLISH_APPROVAL_NOT_GRANTED")
    return received["status"]


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True,
                       capture_output=True, timeout=30)
    if p.returncode:
        raise GateError("P2_GIT_VERIFICATION_FAILURE")
    return p.stdout.strip()


def check_git(repo: Path, task: dict, source_head: str, work_head: str) -> None:
    """Check real git refs/ancestry and reject changes outside the pilot subtree."""
    source_ref = "refs/remotes/origin/" + SOURCE_BRANCH
    work_ref = "refs/remotes/origin/" + WORK_BRANCH
    if _git(repo, "rev-parse", "--verify", source_ref) != source_head or (
        _git(repo, "rev-parse", "--verify", work_ref) != work_head
    ):
        raise GateError("P2_GIT_STALE_BRANCH")
    for ancestor, descendant in ((task["base_sha"], source_head),
                                  (source_head, work_head)):
        p = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                            ancestor, descendant], capture_output=True, timeout=30)
        if p.returncode != 0:
            raise GateError("P2_GIT_ANCESTRY")
    paths = _git(repo, "diff", "--name-only", task["base_sha"], work_head).splitlines()
    if not paths or any(not p.startswith(PILOT + "/") for p in paths):
        raise GateError("P2_GIT_FOREIGN_PATHS")


def _instrument(source: str, root_selector: str, section_selector: str,
                footer_selector: str, *, require_font: bool) -> bytes:
    """Augment a served *copy* of the HTML; never mutate project sources."""
    cfg = json.dumps({"root": root_selector, "sections": section_selector,
                      "footer": footer_selector, "font": require_font})
    script = """
<script>
window.addEventListener('load', async function () {
  try {
    const cfg = CONFIG;
    await document.fonts.ready;
    const images = Array.from(document.images);
    await Promise.all(images.map(i => i.decode().catch(() => null)));
    const root = document.querySelector(cfg.root);
    const footer = document.querySelector(cfg.footer);
    const rect = root.getBoundingClientRect();
    const fb = footer.getBoundingClientRect();
    const sections = Array.from(document.querySelectorAll(cfg.sections));
    const resources = performance.getEntriesByType('resource');
    const metrics = {
      width: Math.round(rect.width), height: Math.round(rect.height),
      footer_top: Math.round(fb.top - rect.top),
      footer_bottom: Math.round(fb.bottom - rect.top),
      sections: sections.map(s => {
        const b = s.getBoundingClientRect();
        return [Math.round(b.top - rect.top), Math.round(b.bottom - rect.top)];
      }),
      images: images.map(i => i.complete && i.naturalWidth > 0),
      font_loaded: cfg.font ? document.fonts.check('16px Jost') : true,
      external_requests: resources.filter(e => new URL(e.name).origin !== location.origin).length
    };
    document.documentElement.setAttribute('data-p2-gate-metrics',
      encodeURIComponent(JSON.stringify(metrics)));
  } catch (_) {
    document.documentElement.setAttribute('data-p2-gate-metrics', 'ERROR');
  }
});
</script>
""".replace("CONFIG", cfg)
    if "</body>" not in source.lower():
        raise GateError("P2_RENDER_HTML_MALFORMED")
    return source.replace("</body>", script + "</body>").encode("utf-8")


def render_one(work_root: Path, relative_html: str, root_selector: str,
               section_selector: str, footer_selector: str,
               *, require_font: bool = True) -> dict:
    """Render a real localhost page in installed Chrome and parse browser DOM."""
    chrome = next((p for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
                   if (p := shutil.which(n))), None)
    if not chrome:
        raise GateError("P2_CHROME_MISSING")
    root = Path(work_root).resolve()
    target = (root / relative_html).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise GateError("P2_RENDER_SOURCE_MISSING")
    payload = _instrument(target.read_text(encoding="utf-8"), root_selector,
                          section_selector, footer_selector, require_font=require_font)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)
        def log_message(self, fmt, *args):
            pass
        def do_GET(self):
            if unquote(urlsplit(self.path).path) == "/" + relative_html:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                super().do_GET()
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/{relative_html}"
        command = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                   "--disable-dev-shm-usage", "--no-first-run", "--disable-extensions",
                   "--disable-background-networking", "--disable-default-apps",
                   "--disable-sync", "--virtual-time-budget=10000", "--dump-dom", url]
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=45, check=False)
        except subprocess.TimeoutExpired:
            raise GateError("P2_RENDER_CHROME_TIMEOUT") from None
        finally:
            server.shutdown()
            thread.join(timeout=5)
    found = re.search(r'data-p2-gate-metrics="([^"]+)"', result.stdout)
    if result.returncode != 0 or not found or found.group(1) == "ERROR":
        raise GateError("P2_RENDER_CHROME_NO_MEASUREMENTS")
    try:
        return json.loads(unquote(html.unescape(found.group(1))))
    except (ValueError, TypeError):
        raise GateError("P2_RENDER_MEASUREMENTS_INVALID") from None


def _load(root: Path, path: str) -> dict:
    p = (root / path).resolve()
    if not p.is_relative_to(root.resolve()) or p.stat().st_size > 256 * 1024:
        raise GateError("P2_INPUT_TOO_LARGE_OR_UNSAFE")
    return json.loads(p.read_text(encoding="utf-8"))


def run(work_root: Path, coordinator_root: Path, git_root: Path,
        source_head: str, work_head: str) -> dict:
    """Run all acceptance gates, returning only supported technical claims."""
    work_root, coordinator_root = Path(work_root).resolve(), Path(coordinator_root).resolve()
    task = _load(coordinator_root, PILOT + "/task.json")
    source_receipt = _load(coordinator_root, PILOT + "/target-receipt.json")
    work_draft = _load(work_root, PILOT + "/work-output/task-receipt.json")
    target_receipt = _load(coordinator_root, PILOT + "/work-target-receipt.json")
    draft_env = _load(work_root, PILOT + "/work-output/handoff-envelope.json")
    final_env = _load(coordinator_root, PILOT + "/work-handoff-envelope.json")
    source_obs = _load(coordinator_root, PILOT + "/work-source-observation.json")
    target_obs = _load(coordinator_root, PILOT + "/work-target-observation.json")
    check_git(Path(git_root), task, source_head, work_head)
    check_records(task, source_receipt, work_draft, target_receipt, draft_env,
                  final_env, source_obs, target_obs, root=work_root,
                  source_head=source_head, work_head=work_head)
    if final_env["receipt_ref"] != PILOT + "/work-target-receipt.json":
        raise GateError("P2_COORDINATOR_RECEIPT_REF_MISMATCH")
    check_assets(work_root)
    work_render = render_one(work_root, PILOT + "/work-output/brand-system-demo.html",
                             ".canvas", ".section", ".footer")
    opencode_render = render_one(work_root, PILOT + "/opencode-output/brand-system-demo.html",
                                 ".demo-root", ".demo-section", ".demo-footer",
                                 require_font=False)
    check_geometry(work_render)
    check_geometry(opencode_render, require_font=False)
    return {
        "git_transport": "verified", "p1_p2_contracts": "valid",
        "canonical_assets_sha256": "verified",
        "work_browser": "1080x1350_geometry_pass",
        "opencode_browser": "1080x1350_geometry_pass",
        "creative_approved": False, "raster_pixel_diff_qa": "not_performed",
        "model_host_attestation": "not_verified", "social_published": False
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ("work-root", "coordinator-root", "git-root", "source-head", "work-head"):
        p.add_argument("--" + flag, required=True)
    a = vars(p.parse_args())
    try:
        print(json.dumps(run(Path(a["work_root"]), Path(a["coordinator_root"]),
                             Path(a["git_root"]), a["source_head"], a["work_head"]),
                         indent=2, sort_keys=True))
        return 0
    except (GateError, ValueError, KeyError, TypeError, OSError) as exc:
        label = str(exc) if isinstance(exc, GateError) else "P2_GATE_INVALID_INPUT"
        print("P2 acceptance BLOCKED: " + label, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
