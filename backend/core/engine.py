"""Pure deterministic game-theory engine.

Implements input validation, rubric evaluation, and zero-sum Elo updates.
Strictly relies on the Python Standard Library (Zero-Dependency).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re

from .rules_config import DebateRules


class ValidationErrorCode(str, Enum):
  """Language-agnostic validation error codes."""

  NONE = "NONE"
  TIMEOUT_EXCEEDED = "ERR_TIMEOUT_EXCEEDED"
  WORD_LIMIT_EXCEEDED = "ERR_WORD_LIMIT_EXCEEDED"
  MISSING_EVIDENCE = "ERR_MISSING_EVIDENCE"
  FAILED_ATTENTION_CHECK = "ERR_FAILED_ATTENTION_CHECK"


class WinnerSide(str, Enum):
  """Explicit verdict states for positive rubric dimensions."""

  PRO = "PRO"
  CON = "CON"
  TIED = "TIED"


class MatchOutcome(float, Enum):
  """Explicit outcome states for deterministic rating calculations."""

  PRO_WIN = 1.0
  DRAW = 0.5
  CON_WIN = 0.0


@dataclass(frozen=True)
class ValidationResult:
  """Decoupled validation outcome carrying numbers and codes instead of text."""

  is_valid: bool
  error_code: ValidationErrorCode = ValidationErrorCode.NONE
  current_value: int = 0
  limit_value: int = 0


@dataclass(frozen=True)
class RoundInput:
  """Decoupled payload representing a round submission."""

  text: str
  turn_start_time: datetime
  submission_time: datetime


@dataclass(frozen=True)
class BallotInput:
  """Decoupled payload representing a judge's silent boolean ballot."""

  better_evidence: WinnerSide
  better_refutation: WinnerSide
  logical_consistency: WinnerSide
  pro_ad_hominem: bool
  pro_straw_man: bool
  con_ad_hominem: bool
  con_straw_man: bool
  attention_check_response: str = ""
  expected_attention_token: str = ""


class GameTheoryEngine:
  """Deterministic rule evaluator and rating calculator."""

  def __init__(self, rules: DebateRules = DebateRules()) -> None:
    self.rules = rules
    # Standard Library regex enforcing valid protocol and domain structure
    self.url_pattern = re.compile(
        r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*"
    )

  def validate_round(self, round_data: RoundInput) -> ValidationResult:
    """Validates round submission returning structured numeric data and codes."""
    # 1. Timeout Check (Forfeit Rule)
    time_elapsed = int(
        (
            round_data.submission_time - round_data.turn_start_time
        ).total_seconds()
    )
    max_allowed_seconds = self.rules.ROUND_TIMEOUT_HOURS * 3600

    if time_elapsed > max_allowed_seconds:
      return ValidationResult(
          is_valid=False,
          error_code=ValidationErrorCode.TIMEOUT_EXCEEDED,
          current_value=time_elapsed // 3600,
          limit_value=self.rules.ROUND_TIMEOUT_HOURS,
      )

    # 2. Concision Check (Word Count Gate)
    words_count = len(round_data.text.strip().split())
    if words_count > self.rules.MAX_ROUND_WORDS:
      return ValidationResult(
          is_valid=False,
          error_code=ValidationErrorCode.WORD_LIMIT_EXCEEDED,
          current_value=words_count,
          limit_value=self.rules.MAX_ROUND_WORDS,
      )

    # 3. Evidence Gate (Mandatory External Citation)
    urls_found = len(self.url_pattern.findall(round_data.text))
    if urls_found < self.rules.MIN_EVIDENCE_URLS:
      return ValidationResult(
          is_valid=False,
          error_code=ValidationErrorCode.MISSING_EVIDENCE,
          current_value=urls_found,
          limit_value=self.rules.MIN_EVIDENCE_URLS,
      )

    return ValidationResult(is_valid=True)

  def validate_ballot(self, ballot: BallotInput) -> ValidationResult:
    """Validates judge ballot against attention checks and integrity rules."""
    if ballot.expected_attention_token:
      submitted = ballot.attention_check_response.strip().lower()
      expected = ballot.expected_attention_token.strip().lower()
      if submitted != expected:
        return ValidationResult(
            is_valid=False,
            error_code=ValidationErrorCode.FAILED_ATTENTION_CHECK,
        )

    return ValidationResult(is_valid=True)

  def calculate_ballot_scores(self, ballot: BallotInput) -> tuple[int, int]:
    """Calculates algebraic round scores for PRO and CON debaters."""
    validation = self.validate_ballot(ballot)
    if not validation.is_valid:
      raise ValueError(
          f"Cannot calculate scores for invalid ballot: {validation.error_code}"
      )

    pro_score = 0
    con_score = 0

    # Positive criteria evaluation using explicit constitution rewards
    criteria_map = [
        (ballot.better_evidence, self.rules.EVIDENCE_REWARD),
        (ballot.better_refutation, self.rules.REFUTATION_REWARD),
        (ballot.logical_consistency, self.rules.LOGICAL_CONSISTENCY_REWARD),
    ]

    for winner, reward in criteria_map:
      if winner == WinnerSide.PRO:
        pro_score += reward
      elif winner == WinnerSide.CON:
        con_score += reward

    # Fallacy penalty deductions
    if ballot.pro_ad_hominem:
      pro_score -= self.rules.AD_HOMINEM_PENALTY
    if ballot.pro_straw_man:
      pro_score -= self.rules.STRAW_MAN_PENALTY

    if ballot.con_ad_hominem:
      con_score -= self.rules.AD_HOMINEM_PENALTY
    if ballot.con_straw_man:
      con_score -= self.rules.STRAW_MAN_PENALTY

    return pro_score, con_score

  def calculate_zero_sum_elo(
      self, pro_elo: int, con_elo: int, outcome: MatchOutcome
  ) -> tuple[int, int]:
    """Calculates zero-sum Elo rating shifts between participants.

    Args:
        pro_elo: Current rating of the PRO participant.
        con_elo: Current rating of the CON participant.
        outcome: Strict MatchOutcome instance (PRO_WIN, DRAW, or CON_WIN).
    """
    if not isinstance(outcome, MatchOutcome):
      raise TypeError("outcome must be an instance of MatchOutcome Enum.")

    expected_pro = 1.0 / (1.0 + 10.0 ** ((con_elo - pro_elo) / 400.0))

    # Symmetric point delta shift
    delta = round(self.rules.ELO_K_FACTOR * (outcome.value - expected_pro))

    new_pro_elo = pro_elo + delta
    new_con_elo = con_elo - delta

    return new_pro_elo, new_con_elo
