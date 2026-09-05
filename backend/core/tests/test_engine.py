"""Unit tests for the pure deterministic game-theory engine.

Executes purely via Python standard library unittest (Zero-Dependency).
"""

from datetime import datetime, timedelta, timezone
import unittest

from backend.core.engine import BallotInput, GameTheoryEngine, RoundInput
from backend.core.rules_config import DebateRules


class TestGameTheoryEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = DebateRules()
        self.engine = GameTheoryEngine(self.rules)
        self.now = datetime.now(timezone.utc)

    def test_reject_unverified_claims(self) -> None:
        """Submission without citations must fail the Evidence Gate."""
        payload = RoundInput(
            text="Argument without any sources.",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        is_valid, reason = self.engine.validate_round(payload)
        self.assertFalse(is_valid)
        self.assertIn("Evidence Gate", reason)

    def test_accept_valid_round(self) -> None:
        """Submission meeting word limit and citations must pass."""
        payload = RoundInput(
            text="Logical refutation with evidence: https://example.com/study",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=2),
        )
        is_valid, _ = self.engine.validate_round(payload)
        self.assertTrue(is_valid)

    def test_forfeit_on_timeout(self) -> None:
        """Exceeding timeout limit must trigger a forfeit."""
        payload = RoundInput(
            text="Valid argument https://example.com",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=49),
        )
        is_valid, reason = self.engine.validate_round(payload)
        self.assertFalse(is_valid)
        self.assertIn("Forfeit", reason)

    def test_ballot_scoring_with_penalties(self) -> None:
        """Algebraic score must increment positives and deduct fallacy penalties."""
        ballot = BallotInput(
            better_evidence="PRO",
            better_refutation="PRO",
            logical_consistency="CON",
            pro_ad_hominem=True,  # Penalty: -1
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=True,   # Penalty: -1
        )
        pro_score, con_score = self.engine.calculate_ballot_scores(ballot)
        # PRO: 2 positives - 1 penalty = 1
        # CON: 1 positive - 1 penalty = 0
        self.assertEqual(pro_score, 1)
        self.assertEqual(con_score, 0)

    def test_zero_sum_elo_transfer(self) -> None:
        """Net Elo rating transfer must be zero-sum."""
        pro_elo = 1200
        con_elo = 1200
        new_pro, new_con = self.engine.calculate_zero_sum_elo(pro_elo, con_elo, pro_won=True)

        pro_delta = new_pro - pro_elo
        con_delta = con_elo - new_con

        self.assertEqual(pro_delta, con_delta)
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)


if __name__ == "__main__":
    unittest.main()
