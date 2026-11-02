"""Pure v1 contract validation with fail-closed repository path rules.

No network, credentials, files created, or provider execution. Errors never echo
a caller's possibly sensitive document values.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError, SchemaError

from . import SCHEMA_PATHS

_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_FORMAT = FormatChecker()
# These similarly named identities are explicitly different. Do not silently
# assign output of one to the other, including on sparse checkouts.
_KNOWN_DISTINCT_BRANDS = {
    "asyada-egitim": {"asya-egitim"},
    "asya-egitim": {"asyada-egitim"},
}
_ROOTS = {"docs", "studio", "brands"}


def _repo_path(value: str, root: Path, allowed_roots: set[str]) -> None:
    if not isinstance(value, str) or len(value) > 400 or "\\" in value or "?" in value or "#" in value:
        raise ValueError("Invalid repository path")
    parts = value.split("/")
    if len(parts) < 2 or parts[0] not in allowed_roots or any(
        not _COMPONENT.fullmatch(part) or part in (".", "..") for part in parts
    ):
        raise ValueError("Invalid repository path")
    current = Path(root).resolve()
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Repository path contains symlink")
    if not current.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("Repository path escapes root")


def _validate_json_schema(kind: str, document: dict) -> None:
    if kind not in SCHEMA_PATHS:
        raise ValueError("Unknown contract kind")
    if not isinstance(document, dict):
        raise ValueError("Contract must be an object")
    try:
        schema = json.loads(SCHEMA_PATHS[kind].read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=_FORMAT).validate(document)
    except (ValidationError, SchemaError, OSError, ValueError) as exc:
        raise ValueError("Invalid " + kind + " contract") from None


def validate_document(kind: str, document: dict, *, root: Path) -> None:
    """Validate schema and local-safe semantics; no state changes."""
    _validate_json_schema(kind, document)
    root = Path(root)
    if kind == "task":
        slug = document["brand_slug"]
        category = document["category"]
        if not _SAFE_ID.fullmatch(slug):
            raise ValueError("Invalid brand identifier")
        if category != "new-identity":
            brand_file = root / "brands" / slug / "brand.json"
            if not brand_file.is_file() or brand_file.is_symlink():
                raise ValueError("Unregistered task brand")
        try:
            categories = json.loads((root / "studio" / "production" / "routes.json").read_text(encoding="utf-8"))["categories"]
        except (OSError, ValueError, KeyError):
            raise ValueError("Routing configuration unavailable") from None
        if category not in categories:
            raise ValueError("Unknown task category")
        _repo_path(document["output_ref"], root, {"docs"})
        for distinct in _KNOWN_DISTINCT_BRANDS.get(slug, set()):
            if distinct in document["output_ref"].split("/"):
                raise ValueError("Output path belongs to distinct brand")
        brief = document["brief_ref"]
        if brief.startswith("repo:"):
            _repo_path(brief[5:], root, _ROOTS)
        elif not brief.startswith("private:"):
            raise ValueError("Invalid brief reference")
        if document["max_parallel"] == 2 and not document["approval"]["parallel_approved"]:
            raise ValueError("Parallel execution requires human approval")
    elif kind == "task-receipt":
        for value in document["changed_paths"]:
            _repo_path(value, root, _ROOTS)
    elif kind == "output-manifest":
        for value in document["editable_sources"]:
            _repo_path(value, root, {"docs"})
        for item in document["renders"]:
            _repo_path(item["path"], root, {"docs"})
    elif kind == "capability-report":
        # A reported capability can be unsubstantiated; advisory must block it.
        pass


def validate_bundle(
    task: dict,
    capability: dict | None,
    receipt: dict | None,
    manifest: dict | None,
    *,
    root: Path,
) -> None:
    """Check references shared among portable records."""
    validate_document("task", task, root=root)
    for kind, doc in (("capability-report", capability), ("task-receipt", receipt), ("output-manifest", manifest)):
        if doc is not None:
            validate_document(kind, doc, root=root)
    if capability is not None and capability["executor"] not in task["allowed_executors"]:
        raise ValueError("Executor is not allowed")
    if receipt is not None:
        if receipt["task_id"] != task["task_id"] or receipt["base_sha"] != task["base_sha"]:
            raise ValueError("Task receipt mismatch")
        if receipt["executor"] not in task["allowed_executors"]:
            raise ValueError("Task receipt executor not allowed")
        if capability is not None and capability["executor"] != receipt["executor"]:
            raise ValueError("Receipt and capability executor mismatch")
    if manifest is not None:
        if manifest["task_id"] != task["task_id"]:
            raise ValueError("Output manifest task mismatch")
        prefix = task["output_ref"].rstrip("/") + "/"
        for path in list(manifest["editable_sources"]) + [render["path"] for render in manifest["renders"]]:
            if not path.startswith(prefix):
                raise ValueError("Output artifact outside task subtree")
