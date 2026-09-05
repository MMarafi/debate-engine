# Contributing to Debate-Engine

Thank you for your interest in contributing to **Debate-Engine**. To prevent architectural debt, ensure complete determinism, and maintain long-term stability, all contributors must strictly adhere to the following architectural rules and quality standards.

---

## 1. Architectural Invariants (Non-Negotiable)

### The Zero-Dependency Rule (`backend/core/`)
The core game-theory engine lives in `backend/core/` and represents the deterministic constitution of the platform.
* **Standard Library Only:** Must rely strictly on the Python Standard Library (`re`, `math`, `dataclasses`, `datetime`, `enum`).
* **Zero External Dependencies:** Importing web frameworks (`django`, `rest_framework`), database libraries, network clients (`requests`, `httpx`), or utility packages inside `backend/core/` is **strictly prohibited**.
* **Decoupled Data Types:** The core engine operates exclusively on native Python data structures and `@dataclass(frozen=True)` types. It must never accept, reference, or query Django ORM models directly.
* **Pure Determinism:** Core logic functions must be pure, idempotent, and reproducible. No disk I/O, unseeded randomness, network calls, or non-deterministic state mutations.
* **Framework-Agnostic Core:** The engine in `backend/core/` must remain completely unaware of the web delivery mechanism (HTTP/Django/Next.js) and persistence layers (SQL/PostgreSQL). It operates strictly as a standalone domain library.
* **Strict Language-Agnostic Outputs:** The core engine must never return localized text or user-facing prose. All outputs consist strictly of deterministic numeric values, boolean flags, or standardized enum error codes (`ValidationResult`, `ValidationErrorCode`, `WinnerSide`, `MatchOutcome`). Text translation and bidirectional localization (RTL/LTR) are exclusively delegated to external presentation layers.
* **Protocol & Matrix Conformance:** All implementations and external adapters must strictly comply with the contracts defined in `SPECIFICATION.md`. Any Pull Request violating the Architectural Conformance Matrix will be rejected automatically.

---

## 2. Behavioral Specifications & Constraints

Contributors implementing application logic or adapters must respect these engine behaviors:
* **Word Counting & URLs:** Every whitespace-separated token—including external evidence URLs—counts toward `MAX_ROUND_WORDS`. URL verification requires valid domain structure (`https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`).
* **Attention Verification:** The verification token is derived deterministically via `GameTheoryEngine.extract_attention_challenge`. External APIs must prompt the judge with the 1-based index without exposing the expected token.
* **Ballot Validity Gate:** Score calculations require valid ballots. Submitting invalid ballots to `calculate_ballot_scores` raises `ValueError`.
* **Zero-Sum Elo Conservation:** All rating calculations require explicit `MatchOutcome` enums and preserve total points ($\Delta_{\text{PRO}} + \Delta_{\text{CON}} = 0$).

---

## 3. Environment & Containerization

* **Docker-First Environment:** Local development and testing must run inside Docker containers.
* **No Host Dependencies:** Never introduce workflows requiring contributors to install specific system binaries directly on their host machines.
* **Verification via Compose:** All commands, migrations, linting, and testing must be fully reproducible via `docker compose`.

---

## 4. Code Quality & Standards

Before opening a Pull Request, ensure your code passes all automated gates:

* **Style Guides:** Adhere strictly to PEP 8 (code style) and PEP 257 (docstrings).
* **Type Annotations:** All new Python functions, dataclasses, and methods must include explicit type hints.
* **Linting and Formatting:** Validated using ruff:
  * `docker compose exec backend ruff check . --fix`
  * `docker compose exec backend ruff format .`
* **Deterministic Test Coverage:** 100% test coverage across rules, boundaries, and mathematical invariants is mandatory for any modifications to `backend/core/`:
  * `docker compose exec backend python -m unittest discover -s core/tests -p "test_*.py"`

---

## 5. Development Workflow

1. **Fork and Branch:** Fork the repository and create a descriptive feature branch:
   * `git checkout -b feature/isolated-feature-name`
2. **Implement:** Implement changes following the architectural constraints and `SPECIFICATION.md`.
3. **Verify:** Verify that all automated tests and Ruff linters pass cleanly within Docker.
4. **Pull Request:** Open a Pull Request referencing the related issue, explicitly stating the intent and architectural impact of the change.
  
