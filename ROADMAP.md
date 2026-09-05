# Engineering Roadmap & Upcoming Specifications

This document tracks upcoming architectural features, integrity safeguards, and application-layer milestones for Debate-Engine.

---

## 1. Core Logic Enhancements (backend/core/)

### Attention Checks (Anti-Random Voting Gate)
* **Objective:** Ensure judges actively read submissions rather than casting random boolean votes.
* **Mechanism:** Add an immutable verification field to `BallotInput`.
* **Behavior:** The engine rejects or invalidates ballots failing an objective reading check prior to algebraic score calculation.

### Fallacy Calibration & Strict Definitions
* **Objective:** Minimize subjective interpretations of Ad Hominem and Straw Man penalties across independent evaluators.
* **Mechanism:** Provide strict, unambiguous boolean evaluation predicates and boundary edge-case definitions within core verification schemas.

---

## 2. Backend & Application Layer (Django / API)

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

### BiDi & Neutral Display
* Implement clean LTR (English) and RTL (Arabic) rendering using CSS logical properties.
* Add bilingual interface localization (Arabic / English) with dynamic locale switching.
* Map engine error codes (`ValidationErrorCode`) to localized user-facing alerts.
