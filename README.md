# Debate-Engine

> An open-source, deterministic debate engine driven by game theory, zero-sum Elo rating, and pure-logic constraints.

Debate-Engine is a minimalist, structured, round-based debate framework. It replaces human content moderation with deterministic code-level constraints, aligning participant incentives using principles of game theory and Nash equilibrium to enforce polite, evidence-backed, and succinct discourse.

> **Design & Philosophy Questions?** Read our [Frequently Asked Questions (FAQ)](FAQ.md) for deep-dives into our anti-conformity judging model, Elo rating mechanics, and procedural gates.

---

## Core Philosophy

Traditional discourse platforms incentivize sensationalism and rhetorical evasion. Debate-Engine enforces pure logic:

* **Constraints over Moderation:** Enforce constructive rules at write-time rather than relying on reactive moderation.
* **Deterministic Scoring:** Silent, boolean-only judge rubrics evaluated algebraically without free-form subjective commentary.
* **Skin in the Game:** Zero-sum Elo rating updates that penalize logical fallacies, unverified claims, and evasive arguments.
* **Text-Only Discipline:** Zero multimedia overhead to maintain focus, reduce hosting costs, and ensure lightweight performance.

---

## Game-Theoretic Incentive Matrix

| Target | Enforced Constraint | Nash Equilibrium Effect |
| :--- | :--- | :--- |
| **Debaters** | Zero-Sum Elo rating system | Participants meticulously avoid fallacies; a single misstep sacrifices reputation points. |
| **Evidence** | Mandatory URL validation gate | Code rejects submissions without verified external sources, eliminating unsubstantiated assertions. |
| **Concision** | Strict word count limit (e.g., 800 words/round) | Eliminates rhetorical padding and forces concentrated counterarguments. |
| **Punctuality** | Deterministic timeout forfeit (48h limit) | Eliminates filibustering; missing a round forfeits the debate automatically. |
| **Judges** | 5-Question boolean rubric | Judges submit independent, silent boolean ballots covering logic and sourcing. No judge is penalized for dissenting votes, upholding the principle that majority consensus is not proof of truth. |

---

## The 5-Question Silent Rubric

Judges do not write reviews. They submit an algebraic ballot covering five fundamental axes:

1. **Evidence & Sourcing (+1):** Did the debater provide verifiable sources rather than raw assertion?
2. **Direct Refutation (+1):** Did the debater dismantle the opposing core thesis rather than shifting goalposts?
3. **Logical Consistency (+1):** Did the debater maintain internally consistent premises without self-contradiction?
4. **Ad Hominem Penalty (-1):** Did the debater attack the opponent's person rather than the argument?
5. **Straw Man Penalty (-1):** Did the debater distort the opponent's argument to attack an invented premise?

$$\text{Round Score} = \sum (\text{Positive Criteria}) - \sum (\text{Fallacy Penalties})$$

---

## Technical Stack & Architectural Rules

The platform is decoupled into a modular architecture:

* **Backend:** Python / Django LTS
* **Frontend:** Next.js (Minimalist, readable typography)
* **Database:** PostgreSQL
* **Infrastructure:** 100% Docker-contained development environment
* **Internationalization & BiDi:** Built-in support for RTL (Arabic) and LTR (English) layouts using CSS logical properties and decoupled translation keys.

### Strict Architecture Rule: Zero-Dependency Core
The game-theory engine (`backend/core/`) **must have zero external third-party dependencies**. It relies strictly on the Python Standard Library (`re`, `dataclasses`, `datetime`, `math`). Web frameworks (Django) and database queries are completely banned inside the core engine logic.

---

## Local Development (Docker-First)

Ensure you have [Docker Desktop](https://www.docker.com/) installed.

```bash
# 1. Clone the repository
git clone https://github.com/MMarafi/debate-engine.git
cd debate-engine

# 2. Configure environment variables
cp .env.example .env

# 3. Spin up all containers
docker compose up --build

```

Access services locally:
* **Frontend:** `http://localhost:3000`
* **Django API & Admin:** `http://localhost:8000`

---

## Code Quality & Standards

All contributions must pass strict automated gates:
* **Style:** Strict adherence to PEP 8 and PEP 257.
* **Linting & Formatting:** Validated with `ruff check .` and `ruff format .`.
* **Testing:** 100% deterministic test coverage for all game-theory modules.

---

## Documentation & FAQ

For architectural rationales, game-theory derivations, and answers to common operational questions, consult the **[Frequently Asked Questions (FAQ)](FAQ.md)**.

---

## License

Debate-Engine is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. Any modifications hosted as a network service must remain public, transparent, and open-source.
