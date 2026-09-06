# System Architecture & Deterministic State Protocol

This document defines the formal protocol specification, state transitions, mathematical invariants, game-theoretic mechanism design, and engine contract for the Debate-Engine platform. All external application layers (Django, FastAPI, Next.js, CLI, or foreign-language ports) MUST strictly conform to these invariants without implementing domain business logic outside `backend/core/`.

---

## 1. Deterministic State Machine (Round Lifecycle)

The lifecycle of a round and its parent debate is governed by a finite state machine (FSM). State transitions occur solely based on deterministic triggers:

* **PENDING:** Matchmaking established; waiting for turn start timestamp.
* **ACTIVE:** Round text submission active.
  * *Timeout (48h):* Transitions to `FORFEIT`. The forfeiting party is assessed a loss via `calculate_zero_sum_elo` (using `MatchOutcome.PRO_WIN` or `MatchOutcome.CON_WIN` in favor of the active opponent).
* **EVALUATING:** Round validated (`is_valid == True`). Judge ballots are masked and collected silently.
  * *Quorum Timeout (24h):* If active valid ballots are strictly below `MIN_JUDGES` (3), transitions to `VOID` (No-Contest). Rating invariant: Zero Elo delta shift.
  * *Quorum Reached (3 <= N <= 5):* Transitions to `EVALUATED`.
* **EVALUATED:** Ballots unmasked; judge reliability weights calibrated; algebraic scores aggregated via matrix dot products.
* **CONCLUDED:** Final debate round completed; zero-sum Elo shifts committed to persistent storage.

---

## 2. Game-Theoretic Mechanism Design & Nash Equilibrium

The engine implements strict incentive compatibility (Truth-Telling Mechanism) to ensure that honesty, empirical rigor, and objective judgment form the strictly dominant strategy for all participants.

### Debater Equilibrium (Incentive Compatibility)
The debater utility function balances rating advancement against verified dialectical infractions:

`U_debater = E[ΔElo] - C(Fallacies) - C(Dropped Arguments) - C(Unsubstantiated Claims)`

* **Asymmetric Fallacy Penalty:** The magnitude of negative deductions strictly exceeds positive scoring increments (|Penalty| > |Reward|). A participant cannot net positive points by combining valid evidence with personal attacks (`Ad Hominem`) or distortions (`Straw Man`).
* **Point-by-Point Commitment:** Dropping an opponent's refutation target automatically concedes refutation points, eliminating rhetorical evasion from the action space.
* **Zero-Sum Elo Conservation:** All skill rating adjustments preserve absolute parity (ΔPRO + ΔCON = 0), preventing rating inflation.

### Judge Equilibrium (Peer Prediction & Calibration)
Judges operate under an independent blind evaluation model designed to eliminate Keynesian Beauty Contest dynamics and sybil collusion:

`U_judge = ProofOfEffort(Token) × (W_j · BrierScore(V_j, V_Quorum))`

* **Proof of Effort (Attention Gate):** Evaluators must supply the deterministically extracted text token. Failing the check silently discards the ballot (`U_judge = 0`).
* **Peer Prediction Calibration (W_j):** Each judge maintains a cumulative reliability weight (W_j >= 0). Upon quorum resolution, an evaluator's response vector (V_j) is measured against the quorum vector (V_Quorum). High statistical deviation penalizes the judge's reputation weight, aligning individual utility with objective truth rather than random voting or ideological bias.

---

## 3. Attention Verification Protocol (Deterministic Extraction)

To eliminate random voting and bot automation without relying on external PRNGs or network calls, the verification token MUST be derived deterministically from the submitted text payload.

### Mathematical Definition:
1. Let the raw text of `RoundInput` be processed into a sequence of characters `C = [c_1, c_2, ..., c_m]` and an array of whitespace-separated, lower-cased words `W = [w_0, w_1, ..., w_{L-1}]`.
2. Compute the deterministic pseudo-hash index `H`:

`H = Σ ord(c) for c in C`

3. The pseudo-random target index `K` is bounded over word count `L`:

`K = (Σ ord(c) × 31) mod L`

4. The expected verification token is: `expected_attention_token = w_K`
5. The presentation layer prompts the judge with an objective comprehension challenge:
   > "Enter word number `K + 1` from the opponent's text body."

---

## 4. Schema-Agnostic Rubric Decoupling & Linear Evaluation

To decouple the scoring logic from hardcoded questions and allow arbitrary dialectical criteria, rubrics are formalized as declarative data schemas evaluated via linear algebra.

### Rubric Specification Schemas
* **Criterion Category:** Distinguishes between positive contributions and negative deductions:
  * `MERIT`: Positively weighted dialectical contribution (+weight).
  * `PENALTY`: Negative deduction for logical or behavioral infractions (-weight).
* **Criterion Target:** Defines the evaluation scope:
  * `PRO`: Applies exclusively to affirmative debater performance.
  * `CON`: Applies exclusively to negative debater performance.
  * `COMPARATIVE`: Relative evaluation comparing both debaters directly.

### Algebraic Evaluation Invariants
Given a `RubricSpec` containing `M` defined criteria, each ballot response map is transformed into discrete binary vectors (`V_PRO`, `V_CON`) multiplied against configured weight vectors (`W_PRO`, `W_CON`):

`Score_PRO = V_PRO · W_PRO`

`Score_CON = V_CON · W_CON`

---

## 5. Strict Boundary Contracts (Engine Input / Output)

The application layer interacts with `backend/core/engine.py` purely as a stateless, functional library.

### Round Submission Gate
* **Input:** `RoundInput(text: str, turn_start_time: datetime, submission_time: datetime)`
* **Output:** `ValidationResult(is_valid: bool, error_code: ValidationErrorCode, current_value: int, limit_value: int)`
* **Boundary Rules:** No database IDs, ORM entities, or presentation fields inside `RoundInput`. Timestamps must be UTC-aware (`timezone.utc`).

### Decoupled Ballot Evaluation Gate
* **Input:** `(ballot: GenericBallotInput, rubric: RubricSpec)`
  * `GenericBallotInput`: Contains `responses: dict[str, bool]`, `attention_check_response: str`, and `expected_attention_token: str`.
  * `RubricSpec`: Contains `version: str` and `questions: tuple[QuestionDefinition, ...]`.
* **Output:** `tuple[int, int]` representing algebraic `(pro_score, con_score)`.
* **Boundary Rules:** Engine raises `ValueError` if `validate_ballot(ballot).is_valid == False` or if required rubric keys are missing from `responses`.

### Zero-Sum Rating Adjustment Gate
* **Input:** `(pro_elo: int, con_elo: int, outcome: MatchOutcome)`
* **Output:** `tuple[int, int]` representing `(new_pro_elo, new_con_elo)`.
* **Conservation Invariant:** `ΔPRO + ΔCON = 0` enforced via symmetric half-up rounding:

`Raw_Shift = K × (Actual - Expected)`

`Delta = floor(Raw_Shift + 0.5) if Raw_Shift >= 0 else ceil(Raw_Shift - 0.5)`

---

## 6. Architectural Conformance Matrix

| Operational Concern | Responsible Layer | Allowed Actions | Strictly Prohibited Actions |
| :--- | :--- | :--- | :--- |
| **Input Validation** | `backend/core/` | Emitting structured validation codes (`ValidationErrorCode`) and limits. | Emitting localized human text strings or relying on local system timezones. |
| **Attention Token Derivation** | `backend/core/` | Executing deterministic mathematical extraction over text. | Calling unseeded random modules (`random.choice`) or external network APIs. |
| **Rubric Definition** | `debates/services/` or Database | Passing declarative `RubricSpec` instances into the core engine. | Hardcoding domain criteria or scoring multipliers directly inside API views. |
| **Concealed Judging** | `debates/api/` | Filtering out ballot records until debate state transitions to `EVALUATED`. | Exposing peer evaluations through serializers during `EVALUATING` state. |
| **Rating Recalculation** | `debates/services/` | Extracting stored Elo, invoking core engine functions, and committing new values. | Writing ad-hoc Elo adjustment logic inside views, serializers, or models. |

---

## 7. Architectural Rules for Contributors

1. **Zero-Dependency Rule:** `backend/core/` shall NEVER import Django, PostgreSQL ORM, or packages outside the Python Standard Library (`dataclasses`, `datetime`, `enum`, `math`, `re`).
2. **Plumbing Isolation:** Database models in `backend/debates/` are strictly adapters (Hexagonal Architecture) mapping persistence rows to immutable Core Dataclasses.
3. **Audit Immutability:** Ballots cast during `EVALUATING` are write-only. Read endpoints MUST conceal ballot rows until the status transitions to `EVALUATED`.
4. **Pure Determinism:** Given identical inputs (`RoundInput`, `GenericBallotInput`, `RubricSpec`), core engine functions must return identical mathematical results across any execution runtime.
