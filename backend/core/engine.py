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
    """Decoupled validation outcome carrying numbers and codes instead of text.

    Attributes:
        is_valid: Boolean indicating whether the validation check passed.
        error_code: Standardized error code from ValidationErrorCode enum.
        current_value: The observed metric value (e.g., word count, elapsed hours).
        limit_value: The configured threshold value associated with the metric.
    """

    is_valid: bool
    error_code: ValidationErrorCode = ValidationErrorCode.NONE
    current_value: int = 0
    limit_value: int = 0


@dataclass(frozen=True)
class RoundInput:
    """Decoupled payload representing a round submission.

    Attributes:
        text: Raw submission content containing arguments and evidence URLs.
        turn_start_time: UTC timestamp marking when the round turn opened.
        submission_time: UTC timestamp marking when the round was submitted.
    """

    text: str
    turn_start_time: datetime
    submission_time: datetime


@dataclass(frozen=True)
class BallotInput:
    """Decoupled payload representing a judge's silent boolean ballot.

    Attributes:
        better_evidence: Winning side on empirical proof quality.
        better_refutation: Winning side on rebuttal and argument deconstruction.
        logical_consistency: Winning side on coherence and internal logic.
        pro_ad_hominem: True if PRO committed a personal attack deduction.
        pro_straw_man: True if PRO committed a straw man distortion deduction.
        con_ad_hominem: True if CON committed a personal attack deduction.
        con_straw_man: True if CON committed a straw man distortion deduction.
        attention_check_response: Token entered by the evaluator during audit.
        expected_attention_token: Deterministic challenge token derived from round text.
    """

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
        """Initializes the engine with immutable configuration rules.

        Args:
            rules: Instance of DebateRules specifying thresholds and multipliers.
        """
        self.rules = rules
        # Standard Library regex enforcing valid protocol and domain structure
        self.url_pattern = re.compile(
            r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*"
        )

    @staticmethod
    def extract_attention_challenge(text: str) -> tuple[int, str]:
        """Derives deterministic verification index and word token from raw text.

        Uses the character summation of the text as a pseudo-random seed to pick
        a verifiable target word.

        Args:
            text: Raw input text from the completed round.

        Returns:
            tuple[int, str]: A pair containing:
                - human_word_index_1_based: 1-indexed word position for human prompt.
                - target_token: Normalized lowercase word expected as verification.

        Raises:
            ValueError: If text contains no alphanumeric Unicode words.
        """
        words = re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
        if not words:
            raise ValueError("Cannot derive attention token from empty or non-word text.")

        num_words = len(words)
        char_sum = sum(ord(c) for c in text)
        target_index = (char_sum * 31) % num_words

        expected_token = words[target_index]
        human_index = target_index + 1

        return human_index, expected_token

    def validate_round(self, round_data: RoundInput) -> ValidationResult:
        """Validates round submission returning structured numeric data and codes.

        Evaluates submission window, whitespace word bounds, and evidence citations.

        Args:
            round_data: RoundInput instance containing text and timestamps.

        Returns:
            ValidationResult: Result object containing validity flag and error code.
        """
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

        words_count = len(round_data.text.strip().split())
        if words_count > self.rules.MAX_ROUND_WORDS:
            return ValidationResult(
                is_valid=False,
                error_code=ValidationErrorCode.WORD_LIMIT_EXCEEDED,
                current_value=words_count,
                limit_value=self.rules.MAX_ROUND_WORDS,
            )

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
        """Validates judge ballot against attention checks and integrity rules.

        Args:
            ballot: BallotInput instance containing judge assessments and verification tokens.

        Returns:
            ValidationResult: Result object indicating pass or attention check failure.
        """
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
        """Calculates algebraic round scores for PRO and CON debaters.

        Sums positive criteria rewards and subtracts fallacy deductions.

        Args:
            ballot: Validated BallotInput instance.

        Returns:
            tuple[int, int]: (pro_score, con_score) algebraic totals.

        Raises:
            ValueError: If the submitted ballot fails validation constraints.
        """
        validation = self.validate_ballot(ballot)
        if not validation.is_valid:
            raise ValueError(
                f"Cannot calculate scores for invalid ballot: {validation.error_code}"
            )

        pro_score = 0
        con_score = 0

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

        Enforces rating conservation where point gains strictly equal point deductions
        ($\\Delta_{\\text{PRO}} + \\Delta_{\\text{CON}} = 0$).

        Args:
            pro_elo: Current Elo rating of the PRO participant.
            con_elo: Current Elo rating of the CON participant.
            outcome: MatchOutcome enum instance representing the match result.

        Returns:
            tuple[int, int]: Updated ratings (new_pro_elo, new_con_elo).

        Raises:
            TypeError: If outcome is not an instance of MatchOutcome.
        """
        if not isinstance(outcome, MatchOutcome):
            raise TypeError("outcome must be an instance of MatchOutcome Enum.")

        expected_pro = 1.0 / (1.0 + 10.0 ** ((con_elo - pro_elo) / 400.0))
        delta = round(self.rules.ELO_K_FACTOR * (outcome.value - expected_pro))

        new_pro_elo = pro_elo + delta
        new_con_elo = con_elo - delta

        return new_pro_elo, new_con_elo
