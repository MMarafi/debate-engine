"""Platform constitution and deterministic rules configuration.

Strictly relies on Python standard library (Zero external dependencies).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DebateRules:
    """Immutable platform constants defining the game-theory constraints."""

    # Concision and timing limits
    MAX_ROUND_WORDS: int = 800
    ROUND_TIMEOUT_HOURS: int = 48
    MIN_EVIDENCE_URLS: int = 1

    # Deterministic token derivation constants
    ATTENTION_HASH_MULTIPLIER: int = 31

    # Positive criteria rewards
    EVIDENCE_REWARD: int = 1
    REFUTATION_REWARD: int = 1
    LOGICAL_CONSISTENCY_REWARD: int = 1

    # Penalty weights
    AD_HOMINEM_PENALTY: int = 1
    STRAW_MAN_PENALTY: int = 1

    # Zero-sum Elo constants
    INITIAL_ELO: int = 1200
    ELO_K_FACTOR: int = 32

    # Judge quorum configuration
    MIN_JUDGES: int = 3
    MAX_JUDGES: int = 5
    JUDGE_QUORUM_TIMEOUT_HOURS: int = 24

    # Round progression limits
    ROUNDS_PER_DEBATER: int = 3
    TOTAL_ROUNDS_LIMIT: int = 6  # 3 rounds Pro + 3 rounds Con
