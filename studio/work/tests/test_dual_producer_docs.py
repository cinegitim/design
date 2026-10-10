"""Guard shared-producer documentation; does not provision a remote environment."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]

class DualProducerDocs(unittest.TestCase):
    def test_shared_contract_authorizes_both(self):
        text=(ROOT/'AGENTS.md').read_text()
        self.assertIn('Both OpenCode and ChatGPT Work/Codex may design and produce',text)
        self.assertIn('Neither is the exclusive producer',text)
        self.assertIn('do not claim a `session_move`, push or repo connection migrated execution',text)
        self.assertIn('merge without requesting another merge confirmation',text)
        self.assertIn('An explicit instruction to hold a particular PR',text)
        self.assertIn('Never bypass branch protection or use force-push',text)
        self.assertNotIn('No automatic merge, including infrastructure/setup',text)

    def test_public_guide_matches_shared_contract(self):
        text=(ROOT/'docs/cloud/index.html').read_text()
        self.assertIn('OpenCode veya Work/Codex üretir',text)
        self.assertIn('geçici yerel',text)
        self.assertIn('sıfır yerel veri garantisi verilmez',text)
        self.assertNotIn('<h1>Codex üretir.',text)
        self.assertNotIn('Build/render Codex Cloud’da;',text)
        self.assertIn('ücretli VM',text)

    def test_remote_guide_distinguishes_goal_from_activation(self):
        text=(ROOT/'studio/cloud/REMOTE-OPENCODE.md').read_text()
        self.assertIn('https://opencode.ai/v2/docs/cli',text)
        self.assertIn('https://opencode.ai/v2/docs/build/client',text)
        self.assertIn('opencode --server',text)
        self.assertIn('bu mevcut yerel oturumu buluta taşımaz',text)
        self.assertIn('API/connector',text)
        self.assertIn('sıfır-local-byte garantisi',text)

    def test_no_exclusive_codex_recipe_wording(self):
        text=(ROOT/'studio/cloud/README.md').read_text()
        self.assertNotIn('| PNG/SVG/ZIP üretimi | Codex Cloud |',text)
        self.assertIn('OpenCode veya Work/Codex',text)
        self.assertIn('ek merge',text)
        self.assertIn('exact-head zorunlu',text)

if __name__=='__main__': unittest.main()
