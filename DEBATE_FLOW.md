# Deterministic Debate Lifecycle & State Machine

This document specifies the strict state transitions, protocol boundaries, and deterministic lifecycle of a debate match on the platform. It serves as the single source of truth for database modeling, Celery tasks, and ORM-to-Core adapters.

---

## 1. High-Level State Transitions

| Current State | Trigger / Event | Next State | Condition / Guard |
| :--- | :--- | :--- | :--- |
| **CREATED** | Opponent accepts challenge | **ONGOING** | Elo snapshot recorded; PRO Round 1 opens. |
| **ONGOING** | Active debater submits turn | **VALIDATING_ROUND** | submission_time captured in UTC. |
| **VALIDATING_ROUND** | Validation passes | **AWAITING_JUDGING** | Payload meets monotonic, word, and URL rules. |
| **VALIDATING_ROUND** | Validation fails | **ONGOING** | Submission rejected; 48h clock continues. |
| **ONGOING** | Turn timer exceeds 48 hours | **RESOLVED** | Forfeit triggered; opponent declared winner. |
| **AWAITING_JUDGING** | Quorum reached (3-5 ballots) | **EVALUATING_BALLOTS** | All accepted ballots passed attention check. |
| **AWAITING_JUDGING** | Quorum timer exceeds 24 hours | **VOID** | Fewer than 3 valid ballots; match canceled. |
| **EVALUATING_BALLOTS** | Scores aggregated & Rounds < 6 | **ONGOING** | Active debater toggles; next 48h clock opens. |
| **EVALUATING_BALLOTS** | Scores aggregated & Rounds == 6 | **RESOLVED** | Final algebraic winner declared; Elo updated. |

---

## 2. Phase-by-Phase Specification

### Phase 1: Initiation & Matchmaking (`CREATED`)
* **Challenge Creation:**
  * A debater initiates a proposition topic.
  * Initial roles (`PRO` and `CON`) are established or randomized.
  * Both debaters have immutable current Elo ratings recorded at match start.
* **Match Confirmation:**
  * The match transitions to `ONGOING` as soon as the opposing debater accepts.
  * Turn counter starts at `Round 1`, active side set to `PRO`.
  * The turn opening timestamp (`turn_start_time`) is captured in UTC.

---

### Phase 2: Round Progression (`ONGOING`)
The debate consists of strictly alternating turns up to a constitutional ceiling of **6 total rounds** (3 rounds for PRO, 3 rounds for CON).

* Round 1: PRO Opening Argument
* Round 2: CON Cross-Examination / Rebuttal
* Round 3: PRO Defense / Elaboration
* Round 4: CON Defense / Counter-Refutation
* Round 5: PRO Closing Argument
* Round 6: CON Closing Argument

#### Turn Invariants:
* **Clock Verification:**
  * Debater has a strict window of `ROUND_TIMEOUT_HOURS` (48 hours).
  * If `current_time > turn_start_time + 48h`, the active debater forfeits immediately.
* **Deterministic Round Validation:**
  * Payload is mapped into `RoundInput(text, turn_start_time, submission_time)`.
  * Evaluated by `GameTheoryEngine.validate_round()`:
    * **Monotonic & Timezone Guard:** Must be UTC-aware and submission_time >= turn_start_time.
    * **Word Limit:** <= 800 clean tokens via `tokenize_words()`.
    * **Evidence:** Contains >= 1 structured URL matching regex.
  * **On Failure:** The submission is rejected; the clock does NOT pause.
 
---

### Phase 3: Silent Peer-Review Quorum (`AWAITING_JUDGING`)
Upon every valid round submission, the system generates a silent peer-review challenge for independent, blind evaluators.

* **Attention Challenge Generation:**
  * The system executes `GameTheoryEngine.extract_attention_challenge(round_text, rules)`.
  * Yields `(human_index, target_token)`.
  * Evaluator is prompted: *"To audit this round, enter word #[human_index] of the submission."*
* **Quorum Rules:**
  * Minimum judges: `MIN_JUDGES = 3`.
  * Maximum judges: `MAX_JUDGES = 5` (strictly odd numbers for deterministic algebraic tie-breaking).
  * Quorum timeout: `JUDGE_QUORUM_TIMEOUT_HOURS = 24`.
* **Ballot Processing (`EVALUATING_BALLOTS`):**
  * Each judge submits independent boolean evaluations:
    * Evidence Quality, Refutation Quality, Logical Consistency (`PRO` / `CON` / `TIED`).
    * Binary penalty flags: Ad Hominem, Straw Man.
    * Attention token response.
  * Evaluated via `GameTheoryEngine.calculate_ballot_scores()`. Invalid attention tokens drop the ballot completely.
* **Quorum Resolution:**
  * **Quorum Met within 24h:** Aggregated scores are finalized for the round. If round < 6, the turn advances to the next debater (`ONGOING`).
  * **Quorum Failed after 24h:** If fewer than 3 valid ballots are collected, the match moves to `VOID`.

---

### Phase 4: Resolution & Zero-Sum Elo Update (`RESOLVED` / `VOID`)

The debate terminates under one of three deterministic conditions:

| Termination Cause | Final State | Outcome Calculation | Elo Adjustment (Delta_PRO, Delta_CON) |
| :--- | :--- | :--- | :--- |
| **All 6 Rounds Completed** | `RESOLVED` | Algebraic sum of all valid judge ballots across all rounds. | Calculated via `calculate_zero_sum_elo`. Delta_PRO + Delta_CON = 0. |
| **Turn Timeout (Delta_t > 48h)** | `RESOLVED` | Default Forfeit: Non-defaulting debater wins with `MatchOutcome = 1.0`. | Standard Elo transfer calculated; forfeiter penalized. |
| **Quorum Failure (Delta_t > 24h)** | `VOID` | Match canceled due to audit breakdown. | No ratings changed (Delta_PRO = 0, Delta_CON = 0). |

#### Final Rating Invariant:
When resolving a winner:
* If Score_PRO > Score_CON => MatchOutcome.PRO_WIN (1.0)
* If Score_CON > Score_PRO => MatchOutcome.CON_WIN (0.0)
* If Score_PRO == Score_CON => MatchOutcome.DRAW (0.5)

Updates strictly apply symmetric half-up rounding to conserve zero-sum point distribution:

Raw Shift Calculation:
Raw_Delta = K * (Actual_Score - Expected_Score)

Symmetric Half-Up Rounding:
If Raw_Delta >= 0:
    Delta = floor(Raw_Delta + 0.5)
Else:
    Delta = ceil(Raw_Delta - 0.5)

Zero-Sum Conservation:
New_Elo_PRO = Elo_PRO + Delta
New_Elo_CON = Elo_CON - Delta
Delta_PRO + Delta_CON = 0
