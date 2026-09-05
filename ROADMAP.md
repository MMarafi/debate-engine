# Engineering Roadmap & Upcoming Specifications

This document tracks completed architectural milestones, upcoming features, integrity safeguards, and application-layer milestones for Debate-Engine.

---

## 1. Core Logic Status & Enhancements (backend/core/)

### [Completed] Deterministic Attention Protocol
* **Status:** Implemented in `GameTheoryEngine` with 100% test coverage.
* **Mechanism:** Derives an immutable verification challenge token deterministically via string summation hashing.
* **Specification:** Formalized in `SPECIFICATION.md` and enforced via pure standard-library constraints.

### Fallacy Calibration & Strict Definitions
* **Objective:** Minimize subjective interpretations of Ad Hominem and Straw Man penalties across independent evaluators.
* **Mechanism:** Provide strict, unambiguous boolean evaluation predicates and boundary edge-case definitions within core verification schemas.

---

## 2. Backend & Application Layer (Django / API)

### Argument Aggregation & Serialization Adapter
* **Objective:** Serve as the translation bridge between segmented frontend refutations and the deterministic core engine.
* **Mechanisms:**
  * Ingest structured blocks from the client, automatically appending standardized indicators (e.g., `[Unrebutted / لم يتم الرد]`) for abandoned arguments.
  * Compile structured refutations into standard round text payloads to feed directly into `GameTheoryEngine.validate_round`.

### Anti-Collusion & Sybil Resistance
* **Objective:** Prevent coordinated voting rings and biased judging blocs.
* **Mechanisms:**
  * **Randomized Blind Assignment:** Judges cannot select specific debates; evaluations are assigned stochastically from an active pool upon queue check-in.
  * **Judge Gating & Quarantine:** Require a minimum threshold of completed, undisputed debates or an account maturation period before unlocking judging capabilities.

### Evidence Quality Gate (Link Verification)
* **Objective:** Counter link-stuffing tactics (e.g., submitting dead or irrelevant URLs).
* **Mechanisms:**
  * Asynchronous HTTP HEAD/GET health check to enforce `HTTP 200 OK` status and reject dead links prior to round submission.
  * Integration layer domain blacklist (excluding link shorteners and link-farming domains).

### Blind Auditing (Result Concealment)
* **Objective:** Prevent conformity bias and front-running by masking other judges' assessments.
* **Implementation:** 
  * API endpoints (`GET /debates/{id}/ballots/`) must restrict read permissions on active ballots until the round status transitions to `EVALUATED`.
  * Ballots remain masked until the judge quorum (`MIN_JUDGES` to `MAX_JUDGES`) is fully committed.

### Django Scaffolding & Database Models
* Setup `manage.py` and application configuration under `backend/config/`.
* Design relational models for Users, Debates, Rounds, and Ballots with strict foreign key constraints.
* Implement database migrations matching the PostgreSQL schema.

---

## 3. Frontend & Presentation Layer (Next.js)

### Inline Refutation & Paragraph-Level Pairing
* **Objective:** Eliminate Gish Gallop and evasion by forcing point-by-point counter-arguments.
* **Mechanisms:**
  * Deconstruct opponent rounds into inspectable thesis/claim segments.
  * Render parallel input containers next to each claim.
  * Dynamically tag empty or skipped claims with a explicit visual badge (`[Unrebutted / لم يتم الرد]`) prior to payload submission.

### BiDi & Neutral Display
* Implement clean LTR (English) and RTL (Arabic) rendering using CSS logical properties.
* Add bilingual interface localization (Arabic / English) with dynamic locale switching.
* Map engine error codes (`ValidationErrorCode`) to localized user-facing alerts.
