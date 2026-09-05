"""Deterministic unit tests for the pure game-theory engine.

Strictly relies on the Python Standard Library unittest module.
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
        text="Late argument: https://example.com/source",
        turn_start_time=self.now,
        submission_time=self.now
        + timedelta(hours=self.rules.ROUND_TIMEOUT_HOURS + 1),
    )
    result = self.engine.validate_round(payload)
    self.assertFalse(result.is_valid)
    self.assertEqual(result.error_code, ValidationErrorCode.TIMEOUT_EXCEEDED)
    self.assertGreater(result.current_value, result.limit_value)

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

  # 2. Attention Check & Ballot Validation Gates

  def test_validate_ballot_without_attention_check(self) -> None:
    """Ballot without an expected token must pass validation unconditionally."""
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

  def test_validate_ballot_attention_check_success(self) -> None:
    """Ballot matching the attention token passes."""
    ballot = BallotInput(
        better_evidence=WinnerSide.PRO,
        better_refutation=WinnerSide.CON,
        logical_consistency=WinnerSide.TIED,
        pro_ad_hominem=False,
        pro_straw_man=False,
        con_ad_hominem=False,
        con_straw_man=False,
        attention_check_response="  SampleToken  ",
        expected_attention_token="sampletoken",
    )
    result = self.engine.validate_ballot(ballot)
    self.assertTrue(result.is_valid)
    self.assertEqual(result.error_code, ValidationErrorCode.NONE)

  def test_validate_ballot_attention_check_failure(self) -> None:
    """Mismatched attention response must return FAILED_ATTENTION_CHECK."""
    ballot = BallotInput(
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
    result = self.engine.validate_ballot(ballot)
    self.assertFalse(result.is_valid)
    self.assertEqual(
        result.error_code, ValidationErrorCode.FAILED_ATTENTION_CHECK
    )

  def test_calculate_ballot_scores_raises_on_invalid_ballot(self) -> None:
    """Calculation must raise ValueError if ballot fails validation."""
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

  # 3. Silent Ballot Scoring (Positive Criteria vs Fallacies)

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

  def test_calculate_ballot_scores_fallacy_penalties(self) -> None:
    """Penalties for fallacies must algebraically deduct from debater score."""
    ballot = BallotInput(
        better_evidence=WinnerSide.TIED,
        better_refutation=WinnerSide.CON,
        logical_consistency=WinnerSide.PRO,
        pro_ad_hominem=True,
        pro_straw_man=False,
        con_ad_hominem=False,
        con_straw_man=True,
    )
    pro_score, con_score = self.engine.calculate_ballot_scores(ballot)
    self.assertEqual(
        pro_score,
        self.rules.LOGICAL_CONSISTENCY_REWARD - self.rules.AD_HOMINEM_PENALTY,
    )
    self.assertEqual(
        con_score,
        self.rules.REFUTATION_REWARD - self.rules.STRAW_MAN_PENALTY,
    )

  # 4. Zero-Sum Elo Rating Shifts

  def test_calculate_zero_sum_elo_equal_ratings_win(self) -> None:
    """Win between equally rated opponents yields symmetric delta."""
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
    """Draw between equally rated opponents results in zero point shift."""
    pro_elo, con_elo = 1200, 1200
    new_pro, new_con = self.engine.calculate_zero_sum_elo(
        pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.DRAW
    )
    self.assertEqual(new_pro, pro_elo)
    self.assertEqual(new_con, con_elo)

  def test_calculate_zero_sum_elo_upset(self) -> None:
    """Lower rated debater beating a higher rated debater gains larger delta."""
    pro_elo, con_elo = 1000, 1400
    new_pro, new_con = self.engine.calculate_zero_sum_elo(
        pro_elo=pro_elo, con_elo=con_elo, outcome=MatchOutcome.PRO_WIN
    )
    delta = new_pro - pro_elo

    self.assertGreater(delta, self.rules.ELO_K_FACTOR // 2)
    self.assertEqual(new_pro + new_con, pro_elo + con_elo)


if __name__ == "__main__":
  unittest.main()
