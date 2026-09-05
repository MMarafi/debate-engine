# System Architecture & Deterministic State Protocol

This document defines the formal protocol specification, state transitions, mathematical invariants, and engine contract for the Debate-Engine platform. All external application layers (Django, FastAPI, CLI, or foreign-language ports) MUST strictly conform to these invariants without implementing domain business logic outside `backend/core/`.

---

## 1. Deterministic State Machine (Round Lifecycle)

The lifecycle of a round and its parent debate is governed by a finite state machine (FSM). State transitions occur solely based on deterministic triggers:

* **PENDING:** Matchmaking established; waiting for turn start timestamp.
* **ACTIVE:** Round text submission active.
  * *Timeout (48h):* Transitions to `FORFEIT`. The forfeiting party is assessed a loss via `calculate_zero_sum_elo` (using `MatchOutcome.PRO_WIN` or `MatchOutcome.CON_WIN` in favor of the active opponent).
* **EVALUATING:** Round validated (`is_valid == True`). Judge ballots are masked and collected silently.
  * *Quorum Timeout (24h):* If active ballots are strictly below `MIN_JUDGES` (3), transitions to `VOID` (No-Contest). Rating invariant: **Zero Elo delta shift**.
  * Quorum Reached (3 <= N <= 5): Transitions to `EVALUATED`.
* **EVALUATED:** Ballots unmasked; algebraic scores aggregated.
* **CONCLUDED:** Final debate round completed; Elo shifts committed to persistent storage.

---

## 2. Attention Verification Protocol (Deterministic Extraction)

To eliminate random voting and bot automation without relying on external PRNGs or network calls, the verification token MUST be derived deterministically from the submitted text payload.

### Mathematical Definition:

1. Let the raw text of `RoundInput` be processed into a sequence of characters $C = [c_1, c_2, \dots, c_m]$ and an array of whitespace-separated, lower-cased words $W = [w_0, w_1, \dots, w_{L-1}]$.

2. Compute the deterministic pseudo-hash index $H$:
   $$H = \sum_{i=1}^{m} \left( \text{ord}(c_i) \times 31^{m - i} \right)$$
   *(Or in lightweight cumulative form:)*
   $$H = \sum_{c \in C} \text{ord}(c)$$
   
4. The pseudo-random target index $K$ is bounded over word count $L$:
   $$K = \left( \sum_{c \in C} \text{ord}(c) \times 31 \right) \pmod L$$

5. The expected verification token is: `expected_attention_token` = $w_K$

6. The application layer prompts the judge with an objective comprehension challenge:
   > "Enter word number `K + 1` from the opponent's text body."

---

## 3. Strict Boundary Contracts (Engine Input / Output)

The application layer interacts with `backend/core/engine.py` purely as a stateless, pure functional engine.

### Round Submission Gate
* **Input:** `RoundInput(text: str, turn_start_time: datetime, submission_time: datetime)`
* **Output:** `ValidationResult(is_valid: bool, error_code: ValidationErrorCode, current_value: int, limit_value: int)`
* **Rule:** No database IDs or presentation fields inside `RoundInput`. Timestamps must be UTC-aware (`timezone.utc`).

### Ballot Evaluation Gate
* **Input:** `BallotInput(better_evidence, better_refutation, logical_consistency, pro_ad_hominem, pro_straw_man, con_ad_hominem, con_straw_man, attention_check_response, expected_attention_token)`
* **Output:** `tuple[int, int]` -> `(pro_score, con_score)`
* **Rule:** Engine raises `ValueError` if `validate_ballot(ballot).is_valid == False`.

### Elo Rating Adjustment Gate
* **Input:** `(pro_elo: int, con_elo: int, outcome: MatchOutcome)`
* **Output:** `tuple[int, int]` -> `(new_pro_elo, new_con_elo)`
* **Conservation Invariant:** $\Delta_{\text{PRO}} + \Delta_{\text{CON}} = 0$ (Total rating sum strictly preserved).

---

## 4. Architectural Conformance Matrix

| Operational Concern | Responsible Layer | Allowed Actions | Strictly Prohibited Actions |
| :--- | :--- | :--- | :--- |
| **Input Validation** | `backend/core/` | Returning structured codes (`ValidationErrorCode`) and raw numeric limits. | Emitting localized human text strings or relying on local system timezones. |
| **Attention Token Derivation** | `backend/core/` | Executing deterministic mathematical extraction over text. | Calling unseeded random modules (`random.choice`) or external APIs. |
| **Concealed Judging (Blind Auditing)** | `debates/api/` | Filtering out ballot records until debate state reaches `EVALUATED`. | Exposing peer evaluations through serializers during `EVALUATING` state. |
| **Rating Recalculation** | `debates/services/` | Extracting stored Elo, feeding into engine, and persisting new values. | Writing ad-hoc Elo adjustment logic inside views, serializers, or models. |

---

## 5. Architectural Rules for Contributors

1. **Zero-Dependency Rule:** `backend/core/` shall NEVER import Django, PostgreSQL ORM, or packages outside the Python Standard Library. Violating PRs will be rejected.
2. **Plumbing Isolation:** Database models in `backend/debates/` are strictly adapters (Hexagonal Architecture) mapping database columns to Core Dataclasses.
3. **Audit Immutability:** Ballots cast during `EVALUATING` are write-only. Read endpoints MUST conceal ballot rows until the status transitions to `EVALUATED`.
