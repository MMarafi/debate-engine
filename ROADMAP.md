# Engineering Roadmap & Upcoming Specifications

This document tracks completed architectural milestones, active implementation phases, integrity safeguards, and application-layer specifications for Debate-Engine.

---

## 1. Core Logic & Deterministic Mechanics (backend/core/)

### [Completed] Deterministic Core Engine & Constitution
* **Status:** 100% test coverage suite implemented and sealed (`backend/core/tests/test_engine.py`).
* **Deterministic Attention Protocol:** Derives challenge verification tokens deterministically via string summation hashing (`extract_attention_challenge`).
* **Symmetric Half-Up Rounding:** Eliminates Banker's Rounding biases to preserve absolute zero-sum Elo conservation ($\Delta_{\text{PRO}} + \Delta_{\text{CON}} = 0$).
* **Timezone & Monotonic Time Guards:** Enforces non-negative duration and rejects mixed aware/naive datetime payloads.
* **Unified Tokenizer:** Single source of truth for concision gates, stripping punctuation while retaining word boundaries.
* **Constitutional Lifecycle:** Fully specified state transitions in `DEBATE_FLOW.md` and user manual in `HOW_IT_WORKS.md`.

### Fallacy Calibration & Boundary Edge Cases
* **Objective:** Minimize subjective interpretation of Ad Hominem and Straw Man penalties across independent evaluators.
* **Mechanism:** Formalize strict boolean boundary definitions in verification schemas to assist peer judges.

---

## 2. Backend & Persistence Layer (Django / PostgreSQL / Celery)

### [Active Milestone] Database Models & Core Adapters
* **Target:** Implement PostgreSQL schemas aligned with `DEBATE_FLOW.md` transitions.
* **Components:**
  * **Relational Models:** `DebateMatch`, `DebateRound`, and `JudgeBallot` enforcing strict foreign keys and timestamp immutability.
  * **Domain Adapters:** Pure transformation bridges mapping ORM records into immutable dataclasses (`RoundInput`, `BallotInput`).
  * **Celery Automation:** Scheduled tasks executing automated forfeits (48h round timeout) and match cancellation (24h quorum timeout).
 
 ---

## 3. Security, Anti-Collusion & Integrity Verification

### Anti-Collusion & Sybil Resistance
* **Objective:** Prevent coordinated voting rings and biased judging blocs.
* **Mechanisms:**
  * **Randomized Blind Assignment:** Judges cannot select specific debates; evaluations are assigned stochastically from an active pool upon queue check-in.
  * **Judge Gating & Quarantine:** Require a minimum threshold of completed, undisputed debates or an account maturation period before unlocking judging capabilities.

### Blind Auditing (Result Concealment)
* **Objective:** Prevent conformity bias and front-running by masking other judges' assessments.
* **Mechanisms:**
  * API endpoints (`GET /debates/{id}/ballots/`) restrict read permissions on active ballots until round status transitions to `EVALUATED`.
  * Ballots remain cryptographically masked until the judge quorum (`MIN_JUDGES = 3` to `MAX_JUDGES = 5`) is fully finalized.

### Evidence Quality Gate (Asynchronous URL Check)
* **Objective:** Counter link-stuffing tactics (submitting dead or spam URLs).
* **Mechanisms:**
  * Celery background worker performs asynchronous `HTTP HEAD/GET` requests to enforce `HTTP 200 OK` status before committing the round to evaluation.
  * Integration layer domain blacklist (filtering link shorteners and link-farming domains).

---

## 4. Frontend & Presentation Layer (Next.js)

### Inline Refutation & Paragraph-Level Pairing
* **Objective:** Eliminate Gish Gallop and rhetorical evasion by forcing point-by-point counterarguments.
* **Mechanisms:**
  * Deconstruct opponent rounds into inspectable thesis/claim segments.
  * Render parallel input containers next to each claim.
  * Dynamically tag empty or skipped claims with an explicit visual badge (`[Unrebutted / لم يتم الرد]`) prior to payload submission.

### BiDi & Neutral Display
* Implement clean LTR (English) and RTL (Arabic) typography and layouts using CSS logical properties.
* Add bilingual interface localization (Arabic / English) with dynamic locale switching.
* Map engine error codes (`ValidationErrorCode`) directly to localized user-facing alerts.
