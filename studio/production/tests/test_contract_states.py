"""Immutable role- and evidence-gated stage transitions."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

class ContractStateTests(unittest.TestCase):
    def test_valid_planner_worker_reviewer_human_sequence(self):
        from contracts.states import next_state
        state = "draft"
        steps = (("ready", "planner", "task:ready"),("assigned", "planner", "task:assigned"),
                 ("producing", "worker", "task:started"),("prepared", "worker", "artifact:sha256"),
                 ("technical_verified", "reviewer", "ci:verified"),("creative_review", "reviewer", "review:opened"),
                 ("accepted", "human", "review:human-approval"),("delivered", "reviewer", "delivery:receipt"))
        for requested, actor, evidence in steps:
            state = next_state(state, requested=requested, actor_role=actor, evidence_ref=evidence)
            self.assertEqual(state, requested)

    def test_skip_and_wrong_actor_rejected(self):
        from contracts.states import next_state
        for current, requested, actor in (("draft","accepted","human"),("creative_review","accepted","worker"),("prepared","delivered","reviewer")):
            with self.assertRaises(ValueError):
                next_state(current, requested=requested, actor_role=actor, evidence_ref="review:proof")

    def test_ci_does_not_approve_creative_or_publish(self):
        from contracts.states import next_state
        for requested, evidence in (("accepted", "ci:success"), ("published", "review:ok")):
            with self.assertRaises(ValueError):
                next_state("creative_review", requested=requested, actor_role="human", evidence_ref=evidence)

    def test_missing_evidence_rejected(self):
        from contracts.states import next_state
        for evidence in (None, "", "  ", "private:secret"):
            with self.assertRaises(ValueError):
                next_state("creative_review", requested="accepted", actor_role="human", evidence_ref=evidence)

    def test_revision_requires_new_task(self):
        from contracts.states import next_state
        self.assertEqual(next_state("creative_review", requested="revision_requested", actor_role="human", evidence_ref="review:reject"), "revision_requested")
        with self.assertRaises(ValueError):
            next_state("revision_requested", requested="producing", actor_role="worker", evidence_ref="task:new")

    def test_blocked_and_cancelled_are_terminal(self):
        from contracts.states import next_state
        for status in ("blocked", "cancelled"):
            self.assertEqual(next_state("producing", requested=status, actor_role="reviewer", evidence_ref="task:reason"), status)
            with self.assertRaises(ValueError):
                next_state(status, requested="accepted", actor_role="human", evidence_ref="review:ok")

if __name__ == "__main__":
    unittest.main()
