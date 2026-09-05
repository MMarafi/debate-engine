"""Boundary and edge-case test suite for GameTheoryEngine.

Strictly relies on the Python Standard Library unittest module.
Ensures mathematical invariants, extreme limits, and negative scoring validity.
"""

from datetime import datetime, timedelta, timezone
import unittest

from backend.core.engine import (
    BallotInput,
    GameTheoryEngine,
    MatchOutcome,
    RoundInput,
    ValidationErrorCode,
    WinnerSide,
)
from backend.core.rules_config import DebateRules


class TestGameTheoryEngineEdgeCases(unittest.TestCase):
    """Rigorous edge-case and boundary verification suite."""

    def setUp(self) -> None:
        self.rules = DebateRules()
        self.engine = GameTheoryEngine(rules=self.rules)
        self.now = datetime.now(timezone.utc)

    # 1. Exact Temporal Boundaries (حدود الوقت الحرجة)

    def test_timeout_exact_boundary_passes(self) -> None:
        """Submission at the exact final microsecond must pass validation."""
        exact_deadline = self.now + timedelta(hours=self.rules.ROUND_TIMEOUT_HOURS)
        payload = RoundInput(
            text="Valid text with citation: https://example.com/source",
            turn_start_time=self.now,
            submission_time=exact_deadline,
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)

    def test_timeout_by_single_second_fails(self) -> None:
        """Submission one second past deadline must be rejected with TIMEOUT_EXCEEDED."""
        one_second_late = self.now + timedelta(
            hours=self.rules.ROUND_TIMEOUT_HOURS, seconds=1
        )
        payload = RoundInput(
            text="Valid text with citation: https://example.com/source",
            turn_start_time=self.now,
            submission_time=one_second_late,
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.TIMEOUT_EXCEEDED)

    # 2. Text & Whitespace Edge Cases (فراغات ونصوص مشوهة)

    def test_validate_round_empty_whitespace_text_fails(self) -> None:
        """Empty or whitespace-only submission must fail evidence check."""
        payload = RoundInput(
            text="   \n\t  \r\n  ",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=5),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.MISSING_EVIDENCE)

    def test_word_count_exact_boundary_passes(self) -> None:
        """Submission with exactly the maximum allowed words must pass."""
        exact_text = "word " * (self.rules.MAX_ROUND_WORDS - 1) + "https://example.com/source"
        payload = RoundInput(
            text=exact_text,
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=10),
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)

    # 3. URL Regex Boundary Checks (اختبارات الروابط الخبيثة أو الوهمية)

    def test_validate_round_invalid_url_pattern_rejected(self) -> None:
        """Broken schemes or URLs lacking domains must fail evidence check."""
        payload = RoundInput(
            text="Attempting bypass with broken links: http:// https:// ftp://fake.com",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=5),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.MISSING_EVIDENCE)

    def test_validate_round_multiple_urls_counted(self) -> None:
        """Multiple valid URLs within the same block are correctly parsed."""
        payload = RoundInput(
            text="Sources: https://example.com/a and https://academic.org/paper",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=5),
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)

    # 4. Negative Scores & Invariants (النقاط السالبة وتناظر Elo)

    def test_ballot_negative_scores_preserved(self) -> None:
        """Committing fallacies without positive merits yields strictly negative scores."""
        ballot = BallotInput(
            better_evidence=WinnerSide.TIED,
            better_refutation=WinnerSide.TIED,
            logical_consistency=WinnerSide.TIED,
            pro_ad_hominem=True,
            pro_straw_man=True,
            con_ad_hominem=False,
            con_straw_man=False,
        )
        pro_score, con_score = self.engine.calculate_ballot_scores(ballot)
        expected_penalty = -(
            self.rules.AD_HOMINEM_PENALTY + self.rules.STRAW_MAN_PENALTY
        )
        self.assertEqual(pro_score, expected_penalty)
        self.assertEqual(con_score, 0)

    def test_calculate_zero_sum_elo_con_wins_preserves_total(self) -> None:
        """CON victory symmetrically penalizes PRO and preserves total rating sum."""
        pro_elo, con_elo = 1300, 1100
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.CON_WIN
        )
        # Zero-Sum Invariant
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)
        self.assertLess(new_pro, pro_elo)
        self.assertGreater(new_con, con_elo)


if __name__ == "__main__":
    unittest.main()
