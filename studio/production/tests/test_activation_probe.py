"""Read-only activation readiness checks."""
import sys
import tempfile
import unittest
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION))
from activation_probe import REQUIRED_FILES, inspect  # noqa: E402


class ActivationProbeTests(unittest.TestCase):
    def build(self, root):
        for relative in REQUIRED_FILES.values():
            file = root / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("placeholder", encoding="utf-8")
        (root / "AGENTS.md").write_text(
            "studio/production/BOOTSTRAP.md\n"
            ".agents/skills/production-router/SKILL.md\n",
            encoding="utf-8",
        )
        (root / ".agents/skills/production-router/SKILL.md").write_text(
            "---\nname: production-router\ndescription: Brandstudio routing\n---\n",
            encoding="utf-8",
        )

    def test_repo_ready_but_live_not_claimed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            result = inspect(root, executable_lookup=lambda cmd: None)
            self.assertTrue(result["repository_readiness"]["ready_for_repo_skill_discovery"])
            self.assertFalse(result["live_validation"]["automatic_activation_verified"])
            self.assertIsNone(result["host_inventory"]["active_model_verified"])

    def test_missing_skill_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            (root / ".agents/skills/production-router/SKILL.md").unlink()
            self.assertFalse(inspect(root, executable_lookup=lambda _: None)[
                "repository_readiness"]["ready_for_repo_skill_discovery"])

    def test_missing_root_trigger_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            (root / "AGENTS.md").write_text("No production rules\n")
            self.assertFalse(inspect(root, executable_lookup=lambda _: None)[
                "repository_readiness"]["root_trigger_declared"])

    def test_executable_only_inventory_not_active_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            out = inspect(root, executable_lookup=lambda cmd: "/bin/example")
            self.assertTrue(out["host_inventory"]["executables_present"]["codex"])
            self.assertIsNone(out["host_inventory"]["active_executor"])
            self.assertIsNone(out["host_inventory"]["active_model_verified"])


if __name__ == "__main__":
    unittest.main()
