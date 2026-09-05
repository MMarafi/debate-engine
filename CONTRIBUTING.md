# Contributing to Debate-Engine

Thank you for your interest in contributing to **Debate-Engine**. To prevent architectural debt, ensure complete determinism, and maintain long-term stability, all contributors must strictly adhere to the following architectural rules and quality standards.

---

## 1. Architectural Invariants (Non-Negotiable)

### The Zero-Dependency Rule (`backend/core/`)
The core game-theory engine lives in `backend/core/` and represents the deterministic constitution of the platform.
* **Standard Library Only:** Must rely strictly on the Python Standard Library (`re`, `math`, `dataclasses`, `datetime`).
* **Zero External Dependencies:** Importing web frameworks (`django`, `rest_framework`), database libraries, network clients (`requests`, `httpx`), or utility packages inside `backend/core/` is **strictly prohibited**.
* **Decoupled Data Types:** The core engine operates exclusively on native Python data structures and `@dataclass` types. It must never accept, reference, or query Django ORM models directly.
* **Pure Determinism:** Core logic functions must be pure and reproducible. No disk I/O, network calls, or non-deterministic state mutations.
* **Framework-Agnostic Core**: The engine in backend/core/ must remain completely unaware of the web delivery mechanism (HTTP/Django/Next.js) and persistence layers (SQL/PostgreSQL). It operates strictly as a standalone domain library.

---

## 2. Environment & Containerization

* **Docker-First Environment:** Local development must be conducted via Docker containers.
* **No Host Dependencies:** Never introduce workflows that require contributors to install specific system packages directly on their host machines.
* **Verification via Compose:** All commands, migrations, linting, and testing must be reproducible using `docker compose`.

---

## 3. Code Quality & Standards

Before opening a Pull Request, ensure your code satisfies all automated checks:

* **Style Guides:** Adhere strictly to **PEP 8** (code style) and **PEP 257** (docstrings).
* **Type Annotations:** All new Python functions and methods must include explicit type hints.
* **Linting & Formatting:** Validated using `ruff`:
  ```bash
  docker compose exec backend ruff check . --fix
  docker compose exec backend ruff format .

  ```
* **Automated Tests:** 100% deterministic test coverage is mandatory for any modifications to the game-theory engine (`backend/core/`):
  ```bash
  docker compose exec backend python -m unittest discover core/tests
  ```

---

## 4. Development Workflow

1. Fork the repository and create a descriptive branch:
   ```bash
   git checkout -b feature/isolated-feature-name
   ```
2. Implement your changes following the architectural constraints.
3. Verify that all automated tests and Ruff linters pass cleanly within Docker.
4. Open a Pull Request referencing the related issue, clearly describing the intent and the architectural impact of the change.
