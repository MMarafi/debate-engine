"""Deterministic unit tests for the pure game-theory engine.

Strictly relies on the Python Standard Library unittest module.
"""

from datetime import datetime, timedelta, timezone
import unittest

from backend.core.engine import (
    BallotInput,
    GameTheoryEngine,
    RoundInput,
    ValidationErrorCode,
)
from backend.core.rules_config import DebateRules


class TestGameTheoryEngine(unittest.TestCase):
    """Test suite ensuring absolute determinism across all engine constraints."""

    def setUp(self) -> None:
        self.rules = DebateRules()
        self.engine = GameTheoryEngine(rules=self.rules)
        self.now = datetime.now(timezone.utc)

    # 1. Validation Gates (Timeout, Concision, Evidence)

    def test_validate_round_success(self) -> None:
        """Valid submission adhering to time, word limits, and evidence."""
        payload = RoundInput(
            text="Valid argument supported by evidence: https://example.com/source",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.NONE)

    def test_validate_round_timeout_forfeit(self) -> None:
        """Submission exceeding the deadline must return TIMEOUT_EXCEEDED."""
        payload = RoundInput(
            text="Late argument: https://example.com",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=self.rules.ROUND_TIMEOUT_HOURS + 1),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.TIMEOUT_EXCEEDED)
        self.assertGreater(result.current_value, result.limit_value)

    def test_validate_round_word_limit_exceeded(self) -> None:
        """Submission exceeding word count limit must return WORD_LIMIT_EXCEEDED."""
        overflow_text = "word " * (self.rules.MAX_ROUND_WORDS + 1) + "https://example.com"
        payload = RoundInput(
            text=overflow_text,
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.WORD_LIMIT_EXCEEDED)
        self.assertGreater(result.current_value, result.limit_value)

    def test_validate_round_missing_evidence(self) -> None:
        """Submission lacking required URL citations must return MISSING_EVIDENCE."""
        payload = RoundInput(
            text="Plausible sounding argument completely lacking external citation.",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.MISSING_EVIDENCE)
        self.assertEqual(result.current_value, 0)
        self.assertEqual(result.limit_value, self.rules.MIN_EVIDENCE_URLS)

    # 2. Silent Ballot Scoring (Positive Criteria vs Fallacies)

    def test_calculate_ballot_scores_clean_win(self) -> None:
        """PRO sweeps all positive criteria with zero fallacies."""
        ballot = BallotInput(
            better_evidence="PRO",
            better_refutation="PRO",
            logical_consistency="PRO",
            pro_ad_hominem=False,
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=False,
        )
        pro_score, con_score = self.engine.calculate_ballot_scores(ballot)
        expected_pro = (
            self.rules.EVIDENCE_REWARD
            + self.rules.REFUTATION_REWARD
            + self.rules.LOGICAL_CONSISTENCY_REWARD
        )
        self.assertEqual(pro_score, expected_pro)
        self.assertEqual(con_score, 0)

    def test_calculate_ballot_scores_fallacy_penalties(self) -> None:
        """Penalties for fallacies must algebraically deduct from debater score."""
        ballot = BallotInput(
            better_evidence="TIED",
            better_refutation="CON",
            logical_consistency="PRO",
            pro_ad_hominem=True,  # Penalty applied
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=True,   # Penalty applied
        )
        pro_score, con_score = self.engine.calculate_ballot_scores(ballot)
        
        # PRO: 1 (consistency) - 1 (ad hominem) = 0
        self.assertEqual(
            pro_score,
            self.rules.LOGICAL_CONSISTENCY_REWARD - self.rules.AD_HOMINEM_PENALTY,
        )
        # CON: 1 (refutation) - 1 (straw man) = 0
        self.assertEqual(
            con_score,
            self.rules.REFUTATION_REWARD - self.rules.STRAW_MAN_PENALTY,
        )

    # 3. Zero-Sum Elo Rating Shifts

    def test_calculate_zero_sum_elo_equal_ratings(self) -> None:
        """Win between equally rated opponents yields exact symmetric delta."""
        pro_elo, con_elo = 1200, 1200
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, pro_won=True
        )
        delta_pro = new_pro - pro_elo
        delta_con = con_elo - new_con
        
        # Zero-sum property: gained points equal lost points
        self.assertEqual(delta_pro, delta_con)
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)
        self.assertEqual(delta_pro, round(self.rules.ELO_K_FACTOR * 0.5))

    def test_calculate_zero_sum_elo_upset(self) -> None:
        """Lower rated debater beating a higher rated debater gains larger delta."""
        pro_elo, con_elo = 1000, 1400  # PRO is heavy underdog
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, pro_won=True
        )
        delta = new_pro - pro_elo
        
        # Underdog upset delta must be greater than half K-factor
        self.assertGreater(delta, self.rules.ELO_K_FACTOR // 2)
        # Rating conservation invariant
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)


if __name__ == "__main__":
    unittest.main()
