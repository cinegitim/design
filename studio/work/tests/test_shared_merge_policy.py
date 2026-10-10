"""Check proposed repository sources agree; never merge or alter a live session."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class SharedMergePolicyTests(unittest.TestCase):
    def test_operational_sources_no_longer_require_another_confirmation(self):
        paths = ['AGENTS.md', 'README.md', 'studio/workflow/PUBLISHING.md',
                 'studio/work/README.md', 'studio/work/EPHEMERAL.md',
                 'studio/cloud/README.md', 'studio/cloud/ACTIVATION.md',
                 '.agents/skills/brand-studio/SKILL.md',
                 '.agents/skills/cloud-delivery/SKILL.md',
                 '.opencode/agents/brand-director.md', '.opencode/skills/brand-studio/SKILL.md',
                 '.github/pull_request_template.md']
        paths += [f'.opencode/commands/{name}.md' for name in
                  ('brand', 'brand-new', 'brand-apply', 'brand-refine', 'brand-explore', 'brand-share')]
        stale = ['Wait for explicit authorization to merge that PR',
                 'Never merge any work without explicit user authorization',
                 'Only after explicit authorization to merge that PR',
                 "wait for the user's explicit authorization to merge that PR",
                 'leave PR open until the user explicitly authorizes',
                 'leave the PR open until merge authorization',
                 'No automatic merge, including infrastructure/setup']
        for path in paths:
            with self.subTest(path=path):
                text = (ROOT/path).read_text()
                for phrase in stale:
                    self.assertNotIn(phrase, text)

    def test_protection_creative_and_runtime_boundaries_remain(self):
        contract = (ROOT/'AGENTS.md').read_text()
        agent = (ROOT/'.opencode/agents/brand-director.md').read_text()
        workflow = (ROOT/'studio/workflow/PUBLISHING.md').read_text()
        self.assertIn('Never bypass branch protection or use force-push', contract)
        self.assertIn('Human creative gates and locked-artwork rules are unchanged', contract)
        self.assertIn('An explicit instruction to hold a particular PR', contract)
        self.assertIn('do not override higher-priority instructions already', agent)
        self.assertIn('--match-head-commit', workflow)
        self.assertIn('Never force-push', workflow)
        self.assertIn('Cleanup supports OPEN', workflow)


if __name__ == '__main__':
    unittest.main()
