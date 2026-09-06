# Engineering Roadmap & Upcoming Specifications

This document tracks completed architectural milestones, active implementation phases, integrity safeguards, mechanism-design specifications, and application-layer roadmaps for Debate-Engine.

---

## 1. Core Logic & Deterministic Mechanics (`backend/core/`)

### [Completed] Baseline Engine Constitution (v1.0)
* **Status:** 100% test coverage suite implemented and sealed (`backend/core/tests/test_engine.py`).
* **Deterministic Attention Protocol:** Derives challenge verification tokens deterministically via string summation hashing (`extract_attention_challenge`).
* **Symmetric Half-Up Rounding:** Eliminates Banker's Rounding biases to preserve absolute zero-sum Elo conservation ($\Delta_{\text{PRO}} + \Delta_{\text{CON}} = 0$).
* **Timezone & Monotonic Time Guards:** Enforces non-negative duration and rejects mixed aware/naive datetime payloads.
* **Unified Tokenizer:** Single source of truth for concision gates, stripping punctuation while retaining word boundaries.
* **Constitutional Lifecycle:** Fully specified state transitions in `DEBATE_FLOW.md` and user manual in `HOW_IT_WORKS.md`.

---

### [Active Milestone] Mechanism Design & Flexible Schema Architecture (v2.0)

To guarantee that honesty and evidence-based rigor remain the strictly dominant strategy (Nash Equilibrium) while allowing dynamic rubric adjustments without core code modifications, the engine transitions to an abstract vector-evaluation architecture.

#### 1. Debater Nash Equilibrium (Truth-Seeking Dominant Strategy)
* **Asymmetric Fallacy Penalty:** Enforce strict mathematical asymmetry where fallacy deductions exceed positive debate rewards ($|\text{Penalty}| > |\text{Reward}|$). The debater's expected utility is modeled as: $U_{\text{debater}} = \mathbb{E}[\text{Elo Gain}] - C(\text{Fallacy Detection}) - C(\text{Unverified Claims})$.
* **Point-by-Point Inline Commitment:** Failure to address an opponent's thesis segment triggers an automatic dropped argument deduction, removing rhetorical evasion from the action space.

#### 2. Judge Nash Equilibrium (Peer Prediction & Bayesian Truth Serum)
* **Attention Gate:** Proof of Effort verification; failure to supply the deterministic token silently drops the ballot.
* **Judge Calibration Rating (Peer Prediction):** Evaluators receive a dynamic reliability weight ($W_j$) updated via quadratic scoring / Brier metrics against the verified independent quorum: `Score_Quorum = Σ(W_j · V_j)`.
* **Outlier Penalty:** Judges deviating significantly from verifiable textual benchmarks face automated weight depreciation, dismantling the Keynesian Beauty Contest dynamic and eliminating lazy random voting.

#### 3. Schema-Agnostic Rubric Decoupling
Decouple hardcoded boolean fields like `better_evidence` and `pro_ad_hominem` into declarative criteria data contracts evaluated via linear algebra:

* **Rubric Specification (`RubricSpec`):** Versioned schema manifest containing an immutable tuple of `QuestionDefinition` entities.
* **Question Definition (`QuestionDefinition`):** Specifies `key` (e.g., `"evidence"`, `"ad_hominem"`), `category` (`MERIT` | `PENALTY`), `weight` (integer scalar), and `target` (`PRO` | `CON` | `COMPARATIVE`).
* **Generic Ballot (`GenericBallot`):** Carries the deterministic `attention_token` alongside an open response map of type `dict[str, bool]`.
* **Vector Dot Product Evaluation:** Calculated as `Score_PRO = V_PRO · W_PRO` and `Score_CON = V_CON · W_CON`.
* **Core Invariant:** The engine processes dynamic rubrics and arbitrary question counts without modifying calculation signatures or importing external numerical libraries.

---

## 2. Structural Architecture & Engine Evolution Matrix

| Dimension | Baseline Engine (v1.0) | Decoupled Mechanism Engine (v2.0) |
| :--- | :--- | :--- |
| **Rubric Structure** | Hardcoded 5-axis schema (`BallotInput`) | Dynamic criteria vector (`dict[str, bool]`) |
| **Fallacy Weighting** | Symmetric deduction ($1 - 1 = 0$) | Asymmetric deterrence ($|\text{Penalty}| > |\text{Reward}|$) |
| **Judge Reliability** | Binary pass/fail on attention token | Proof-of-Effort + Peer Prediction Calibration |
| **Score Calculation** | Conditional scalar matching | Matrix dot-product ($\mathbf{V} \cdot \mathbf{W}$) |
| **Extensibility** | Requires codebase modification | Configurable via declarative schema definitions |

---

## 3. Backend & Persistence Layer (Django / PostgreSQL / Celery)

### Database Models & Core Adapters
* **Target:** Implement PostgreSQL schemas strictly aligned with `DEBATE_FLOW.md` transitions and decoupled rubric specifications.
* **Components:**
  * **Relational Models:** `DebateMatch`, `DebateRound`, `RubricConfig`, and `JudgeBallot` enforcing relational constraints and immutable audit logs.
  * **Domain Adapters:** Pure transformation mappers converting ORM instances into frozen dataclasses (`RoundInput`, `GenericBallot`, `RubricSpec`).
  * **Celery Automation:** Deterministic workers executing 48-hour turn forfeits, 24-hour quorum evaluations, and rating commits.

---

## 4. Security, Anti-Collusion & Integrity Verification

### Anti-Collusion & Sybil Resistance
* **Randomized Blind Allocation:** Blind assignment of evaluators from an active pool upon queue check-in to prevent coordinated voting rings.
* **Judge Quarantine:** Require a minimum threshold of completed, undisputed debates or an account maturation period before unlocking judging capabilities.

### Blind Auditing (Result Concealment)
* REST API endpoints (`GET /debates/{id}/ballots/`) strictly conceal peer evaluations until the debate state transitions to `EVALUATED`.
* Ballots remain masked until quorum constraints ($3 \le N \le 5$) are met.

### Evidence Quality Gate (Asynchronous URL Check)
* Celery background worker performs asynchronous `HTTP HEAD/GET` requests to enforce `HTTP 200 OK` status before committing the round to evaluation.
* Domain blacklist filtering URL-shorteners, content aggregators, and spam farms.

---

## 5. Frontend & Presentation Layer (Next.js)

### Inline Refutation & Paragraph-Level Pairing
* Deconstruct opponent rounds into inspectable thesis/claim segments.
* Render parallel input containers next to each claim.
* Dynamically tag empty or skipped claims with an explicit visual badge (`[Unrebutted / لم يتم الرد]`) to enforce refutation parity before submission.

### BiDi & Neutral Display
* Full RTL (Arabic) and LTR (English) layout compatibility using CSS logical properties.
* Strict language-agnostic error mapping translating `ValidationErrorCode` to localized client alerts.
