"""Comprehensive deterministic unit tests for GameTheoryEngine.

Strictly relies on the Python Standard Library unittest module.
Enforces 100% coverage across rules, boundaries, and mathematical invariants.
"""

from datetime import datetime, timedelta, timezone
import unittest

try:
    from backend.core.engine import (
        BallotInput,
        GameTheoryEngine,
        MatchOutcome,
        RoundInput,
        ValidationErrorCode,
        WinnerSide,
    )
    from backend.core.rules_config import DebateRules
except ModuleNotFoundError:
    from core.engine import (
        BallotInput,
        GameTheoryEngine,
        MatchOutcome,
        RoundInput,
        ValidationErrorCode,
        WinnerSide,
    )
    from core.rules_config import DebateRules


class TestGameTheoryEngine(unittest.TestCase):
    """Rigorous verification suite for core engine logic and boundary cases."""

    def setUp(self) -> None:
        """Initializes the test suite with standard rules and UTC clock."""
        self.rules = DebateRules()
        self.engine = GameTheoryEngine(rules=self.rules)
        self.now = datetime.now(timezone.utc)

    # 1. Attention Challenge Derivation (Extraction Protocol)

    def test_extract_attention_challenge_determinism(self) -> None:
        """Same input text must produce identical word index and token every execution."""
        sample_text = "Logic and empirical evidence must drive structured debate: https://example.com"
        idx1, token1 = GameTheoryEngine.extract_attention_challenge(sample_text)
        idx2, token2 = GameTheoryEngine.extract_attention_challenge(sample_text)

        self.assertEqual(idx1, idx2)
        self.assertEqual(token1, token2)
        self.assertIsInstance(idx1, int)
        self.assertTrue(token1.isalnum())

    def test_extract_attention_challenge_strips_punctuation(self) -> None:
        """Verification token must not contain attached commas, dots, or colons."""
        text_with_punctuation = "First, second. Third: fourth! https://source.org"
        _, token = GameTheoryEngine.extract_attention_challenge(text_with_punctuation)
        self.assertRegex(token, r"^\w+$")

    def test_extract_attention_challenge_raises_on_empty_text(self) -> None:
        """Derivation on text lacking valid word tokens raises ValueError."""
        with self.assertRaises(ValueError):
            GameTheoryEngine.extract_attention_challenge("!!! :::: ---")

    def test_attention_challenge_preserves_human_token_order(self) -> None:
        """Tokens with surrounding commas or quotes must match human visual word indexing."""
        sample_text = 'The "premise", clearly, holds true: https://example.com'
        idx, token = GameTheoryEngine.extract_attention_challenge(sample_text)
        tokens = GameTheoryEngine.tokenize_words(sample_text)
        self.assertEqual(tokens[idx - 1], token)

    # 2. Round Validation Gates & Exact Boundaries

    def test_validate_round_success(self) -> None:
        """Valid submission adhering to time, word limits, and citations."""
        payload = RoundInput(
            text="Valid argument supported by evidence: https://example.com/source",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.NONE)

    def test_validate_round_exact_deadline_boundary_passes(self) -> None:
        """Submission at the exact final second of the allowed window passes."""
        exact_deadline = self.now + timedelta(hours=self.rules.ROUND_TIMEOUT_HOURS)
        payload = RoundInput(
            text="Valid submission at boundary: https://example.com/source",
            turn_start_time=self.now,
            submission_time=exact_deadline,
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)

    def test_validate_round_timeout_by_single_second_fails(self) -> None:
        """Submission late by a single second must return TIMEOUT_EXCEEDED."""
        one_second_late = self.now + timedelta(
            hours=self.rules.ROUND_TIMEOUT_HOURS, seconds=1
        )
        payload = RoundInput(
            text="Late argument: https://example.com/source",
            turn_start_time=self.now,
            submission_time=one_second_late,
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.TIMEOUT_EXCEEDED)
        self.assertGreater(result.current_value, result.limit_value)

    def test_validate_round_word_count_exact_boundary_passes(self) -> None:
        """Submission with exactly the max word limit passes."""
        exact_text = "word " * (self.rules.MAX_ROUND_WORDS - 1) + "https://example.com/source"
        payload = RoundInput(
            text=exact_text,
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertTrue(result.is_valid)

    def test_validate_round_word_limit_exceeded(self) -> None:
        """Submission exceeding word count limit must return WORD_LIMIT_EXCEEDED."""
        overflow_text = (
            "word " * (self.rules.MAX_ROUND_WORDS + 1)
            + "https://example.com/source"
        )
        payload = RoundInput(
            text=overflow_text,
            turn_start_time=self.now,
            submission_time=self.now + timedelta(hours=1),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.WORD_LIMIT_EXCEEDED)

    def test_validate_round_empty_whitespace_text_fails(self) -> None:
        """Whitespace or empty text fails the external evidence gate."""
        payload = RoundInput(
            text="   \n\t  \r\n  ",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=5),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.MISSING_EVIDENCE)

    def test_validate_round_broken_url_pattern_fails(self) -> None:
        """Invalid or incomplete URLs lacking domain dot structure fail."""
        payload = RoundInput(
            text="Attempting bypass with broken schemes: http:// https:// ftp://fake",
            turn_start_time=self.now,
            submission_time=self.now + timedelta(minutes=5),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.MISSING_EVIDENCE)

    def test_validate_round_mixed_timezone_awareness_fails_gracefully(self) -> None:
        """Comparing naive and timezone-aware timestamps returns INVALID_DATETIME without crashing."""
        naive_start = datetime(2026, 1, 1, 12, 0, 0)
        aware_submission = datetime(2026, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        payload = RoundInput(
            text="Valid argument text with evidence: https://example.com",
            turn_start_time=naive_start,
            submission_time=aware_submission,
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.INVALID_DATETIME)

    def test_validate_round_submission_before_turn_start_fails(self) -> None:
        """Submission timestamp occurring before turn start returns INVALID_DATETIME."""
        payload = RoundInput(
            text="Premature submission: https://example.com",
            turn_start_time=self.now,
            submission_time=self.now - timedelta(seconds=5),
        )
        result = self.engine.validate_round(payload)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.INVALID_DATETIME)

    def test_word_count_ignores_standalone_punctuation_bullets(self) -> None:
        """Standalone bullets like '*' or '-' must not inflate the core word limit count."""
        raw_text = "* First point - second point * https://example.com"
        tokens = GameTheoryEngine.tokenize_words(raw_text)
        self.assertEqual(len(tokens), 5)
        self.assertNotIn("*", tokens)
        self.assertNotIn("-", tokens)

    # 3. Attention Checks & Ballot Verification Gates

    def test_validate_ballot_unconditional_when_no_token_expected(self) -> None:
        """Ballot without an expected token passes validation by default."""
        ballot = BallotInput(
            better_evidence=WinnerSide.PRO,
            better_refutation=WinnerSide.PRO,
            logical_consistency=WinnerSide.PRO,
            pro_ad_hominem=False,
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=False,
        )
        result = self.engine.validate_ballot(ballot)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.NONE)

    def test_validate_ballot_matching_attention_token_passes(self) -> None:
        """Attention check passes with whitespace and case insensitivity."""
        ballot = BallotInput(
            better_evidence=WinnerSide.PRO,
            better_refutation=WinnerSide.TIED,
            logical_consistency=WinnerSide.PRO,
            pro_ad_hominem=False,
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=False,
            attention_check_response="  DebateLogic42  ",
            expected_attention_token="debatelogic42",
        )
        result = self.engine.validate_ballot(ballot)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_code, ValidationErrorCode.NONE)

    def test_validate_ballot_mismatched_attention_token_fails(self) -> None:
        """Mismatched attention response must return FAILED_ATTENTION_CHECK."""
        ballot = BallotInput(
            better_evidence=WinnerSide.PRO,
            better_refutation=WinnerSide.TIED,
            logical_consistency=WinnerSide.PRO,
            pro_ad_hominem=False,
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=False,
            attention_check_response="RandomClick",
            expected_attention_token="DebateLogic42",
        )
        result = self.engine.validate_ballot(ballot)
        self.assertFalse(result.is_valid)
        self.assertEqual(
            result.error_code, ValidationErrorCode.FAILED_ATTENTION_CHECK
        )

    def test_calculate_ballot_scores_raises_on_invalid_ballot(self) -> None:
        """Calculation must reject an invalid ballot with ValueError."""
        invalid_ballot = BallotInput(
            better_evidence=WinnerSide.PRO,
            better_refutation=WinnerSide.CON,
            logical_consistency=WinnerSide.TIED,
            pro_ad_hominem=False,
            pro_straw_man=False,
            con_ad_hominem=False,
            con_straw_man=False,
            attention_check_response="WrongToken",
            expected_attention_token="RequiredToken",
        )
        with self.assertRaises(ValueError):
            self.engine.calculate_ballot_scores(invalid_ballot)

    # 4. Silent Ballot Scoring & Negative Preservations

    def test_calculate_ballot_scores_clean_win(self) -> None:
        """PRO sweeps all positive criteria with zero fallacies."""
        ballot = BallotInput(
            better_evidence=WinnerSide.PRO,
            better_refutation=WinnerSide.PRO,
            logical_consistency=WinnerSide.PRO,
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

    def test_calculate_ballot_scores_negative_penalties_preserved(self) -> None:
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

    # 5. Zero-Sum Elo Invariants & Outcomes

    def test_calculate_zero_sum_elo_pro_wins(self) -> None:
        """PRO win yields symmetric delta conservation."""
        pro_elo, con_elo = 1200, 1200
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.PRO_WIN
        )
        delta_pro = new_pro - pro_elo
        delta_con = con_elo - new_con

        self.assertEqual(delta_pro, delta_con)
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)
        self.assertEqual(delta_pro, round(self.rules.ELO_K_FACTOR * 0.5))

    def test_calculate_zero_sum_elo_draw(self) -> None:
        """Draw between equally rated participants yields zero shift."""
        pro_elo, con_elo = 1200, 1200
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.DRAW
        )
        self.assertEqual(new_pro, pro_elo)
        self.assertEqual(new_con, con_elo)

    def test_calculate_zero_sum_elo_con_wins(self) -> None:
        """CON victory symmetrically penalizes PRO and preserves rating sum."""
        pro_elo, con_elo = 1300, 1100
        new_pro, new_con = self.engine.calculate_zero_sum_elo(
            pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.CON_WIN
        )
        self.assertEqual(new_pro + new_con, pro_elo + con_elo)
        self.assertLess(new_pro, pro_elo)
        self.assertGreater(new_con, con_elo)

    def test_calculate_zero_sum_elo_invalid_outcome_type_raises(self) -> None:
        """Passing non-MatchOutcome instance must strictly raise TypeError."""
        with self.assertRaises(TypeError):
            self.engine.calculate_zero_sum_elo(1200, 1200, outcome=1.0)  # type: ignore


if __name__ == "__main__":
    unittest.main()
