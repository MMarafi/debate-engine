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

    better_evidence: str  # "PRO", "CON", or "TIED"
    better_refutation: str
    logical_consistency: str
    pro_ad_hominem: bool
    pro_straw_man: bool
    con_ad_hominem: bool
    con_straw_man: bool


class GameTheoryEngine:
    """Deterministic rule evaluator and rating calculator."""

    def __init__(self, rules: DebateRules = DebateRules()) -> None:
        self.rules = rules
        # Standard Library regex matching valid web URLs
        self.url_pattern = re.compile(r"https?://[^\s]+")

    def validate_round(self, round_data: RoundInput) -> ValidationResult:
        """Validates round submission returning structured numeric data and codes."""
        # 1. Timeout Check (Forfeit Rule)
        time_elapsed = int(
            (round_data.submission_time - round_data.turn_start_time).total_seconds()
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

    def calculate_ballot_scores(self, ballot: BallotInput) -> tuple[int, int]:
        """Calculates algebraic round scores for PRO and CON debaters."""
        pro_score = 0
        con_score = 0

        # Positive criteria evaluation using explicit constitution rewards
        criteria_map = [
            (ballot.better_evidence, self.rules.EVIDENCE_REWARD),
            (ballot.better_refutation, self.rules.REFUTATION_REWARD),
            (ballot.logical_consistency, self.rules.LOGICAL_CONSISTENCY_REWARD),
        ]

        for winner, reward in criteria_map:
            if winner == "PRO":
                pro_score += reward
            elif winner == "CON":
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
        self, pro_elo: int, con_elo: int, pro_won: bool
    ) -> tuple[int, int]:
        """Calculates zero-sum Elo rating shifts between participants."""
        expected_pro = 1.0 / (1.0 + 10.0 ** ((con_elo - pro_elo) / 400.0))
        actual_pro = 1.0 if pro_won else 0.0

        # Point delta shift
        delta = round(self.rules.ELO_K_FACTOR * (actual_pro - expected_pro))

        new_pro_elo = pro_elo + delta
        new_con_elo = con_elo - delta

        return new_pro_elo, new_con_elo
