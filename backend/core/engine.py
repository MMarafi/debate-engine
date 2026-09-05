"""Pure deterministic game-theory engine.

Implements input validation, rubric evaluation, and zero-sum Elo updates.
Strictly relies on the Python Standard Library (Zero-Dependency).
"""

from dataclasses import dataclass
from datetime import datetime
import re

from .rules_config import DebateRules


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

    def validate_round(self, round_data: RoundInput) -> tuple[bool, str]:
        """Validates round submission against timeout, word count, and citation gates."""
        # 1. Timeout Check (Forfeit Rule)
        time_elapsed = (
            round_data.submission_time - round_data.turn_start_time
        ).total_seconds()
        max_allowed_seconds = self.rules.ROUND_TIMEOUT_HOURS * 3600

        if time_elapsed > max_allowed_seconds:
            return (
                False,
                f"Forfeit: Submission exceeded the {self.rules.ROUND_TIMEOUT_HOURS}h deadline.",
            )

        # 2. Concision Check (Word Count Gate)
        words_count = len(round_data.text.strip().split())
        if words_count > self.rules.MAX_ROUND_WORDS:
            return (
                False,
                f"Exceeded word limit: {words_count}/{self.rules.MAX_ROUND_WORDS} words.",
            )

        # 3. Evidence Gate (Mandatory External Citation)
        urls_found = len(self.url_pattern.findall(round_data.text))
        if urls_found < self.rules.MIN_EVIDENCE_URLS:
            return (
                False,
                f"Evidence Gate: Must contain at least {self.rules.MIN_EVIDENCE_URLS} valid URL source.",
            )

        return True, ""

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
