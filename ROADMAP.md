# Engineering Roadmap & Upcoming Specifications

This document tracks upcoming architectural features, integrity safeguards, and application-layer milestones for Debate-Engine.

---

## 1. Core Logic Enhancements (backend/core/)

### Attention Checks (Anti-Random Voting Gate)
* **Objective:** Ensure judges actively read submissions rather than casting random boolean votes.
* **Mechanism:** Add an immutable verification field to `BallotInput`.
* **Behavior:** The engine rejects or invalidates ballots failing an objective reading check prior to algebraic score calculation.

---

## 2. Backend & Application Layer (Django / API)

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
