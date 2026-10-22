#!/usr/bin/env python3
"""Read-only repository skill-discovery and activation readiness probe.

A passing result proves file-layout readiness, NOT that any agent actually
selected a skill, identified its active model, or used a model call.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = {
    "root-instructions": "AGENTS.md",
    "production-skill": ".agents/skills/production-router/SKILL.md",
    "production-bootstrap": "studio/production/BOOTSTRAP.md",
    "route-config": "studio/production/routes.json",
    "route-script": "studio/production/router.py",
    "shared-brand-method": ".opencode/skills/brand-studio/SKILL.md",
}


def inspect(root: Path, *, executable_lookup=shutil.which) -> dict:
    """Inspect only local file paths and available command names; no subprocess."""
    files = {name: (root / path).is_file()
             for name, path in REQUIRED_FILES.items()}
    rule = root / "AGENTS.md"
    rule_text = rule.read_text(encoding="utf-8") if files["root-instructions"] else ""
    skill = root / ".agents/skills/production-router/SKILL.md"
    skill_text = skill.read_text(encoding="utf-8") if files["production-skill"] else ""
    trigger = (
        "studio/production/BOOTSTRAP.md" in rule_text
        and ".agents/skills/production-router/SKILL.md" in rule_text
    )
    frontmatter = (skill_text.startswith("---\n")
                   and "\nname: production-router\n" in skill_text
                   and "\ndescription:" in skill_text)
    commands = {cmd: bool(executable_lookup(cmd))
                for cmd in ("python3", "codex", "opencode", "agy")}
    ready = all(files.values()) and trigger and frontmatter
    return {
        "mode": "read-only-activation-probe",
        "repository_readiness": {
            "files": files,
            "root_trigger_declared": trigger,
            "shared_skill_manifest_present": frontmatter,
            "ready_for_repo_skill_discovery": ready,
        },
        "host_inventory": {
            "executables_present": commands,
            "active_executor": None,
            "active_model_verified": None,
        },
        "live_validation": {
            "codex": "not-run",
            "opencode": "not-run",
            "antigravity": "not-run",
            "chatgpt": "not-run",
            "automatic_activation_verified": False,
        },
        "notes": [
            "Installed executables do not prove active runtime or accessible agent tools.",
            "Skill discovery by file layout does not prove implicit skill invocation.",
            "ChatGPT Project Instructions and connected GitHub access require a separate setup.",
            "No model call, image generation, write, telemetry, or publication occurred.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = inspect(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["repository_readiness"]["ready_for_repo_skill_discovery"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
