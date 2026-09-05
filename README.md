# Debate-Engine

> An open-source, deterministic debate engine driven by game theory, zero-sum Elo rating, and pure-logic constraints.

Debate-Engine is a minimalist, structured, round-based debate framework. It replaces human content moderation with deterministic code-level constraints, aligning participant incentives using principles of game theory and Nash equilibrium to enforce polite, evidence-backed, and succinct discourse.

> **Want to see how it works in practice?** Read our [User & Platform Guide (HOW_IT_WORKS.md)](./HOW_IT_WORKS.md) or dive into the mathematical mechanics in our [Frequently Asked Questions (FAQ.md)](./FAQ.md).

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
| **Concision** | Strict word count limit (800 words/round) | Eliminates rhetorical padding and forces concentrated counterarguments. |
| **Punctuality** | Deterministic timeout forfeit (48h limit) | Eliminates filibustering; missing a round forfeits the debate automatically. |
| **Judges** | Independent Silent Ballots | Evaluators pass deterministic attention checks and submit boolean verdicts. Ties are broken algebraically by an odd quorum (3–5 judges). |

---

## The 5-Question Silent Rubric

Judges submit an algebraic ballot covering five fundamental axes:

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
* **Database:** PostgreSQL
* **Infrastructure:** 100% Docker-contained development environment
* **Zero-Dependency Core:** The game-theory engine (`backend/core/`) relies strictly on the Python Standard Library (`re`, `dataclasses`, `datetime`, `math`). Web frameworks and database queries are strictly prohibited inside core logic.

---

## Local Development & Deterministic Testing

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

### Run 100% Coverage Verification Suite

Execute the core mathematical tests inside the running container:

```bash
docker compose exec backend python -m unittest discover -s core/tests -p "test_*.py"
```

---

## Documentation & Architecture Index

For detailed system designs, lifecycle state machines, and developer guides, consult the reference documentation:

* **[Debate Lifecycle & State Machine (DEBATE_FLOW.md)](./DEBATE_FLOW.md):** Strict finite-state machine transitions, turn sequencing, and forfeit triggers.
* **[User & Platform Guide (HOW_IT_WORKS.md)](./HOW_IT_WORKS.md):** Step-by-step walkthrough for debaters and peer judges.
* **[Architecture & Protocol Specifications (SPECIFICATION.md)](./SPECIFICATION.md):** The deterministic mathematical model, Elo conservation invariants, and scoring state machines.
* **[Contribution Guidelines (CONTRIBUTING.md)](./CONTRIBUTING.md):** Architectural boundaries, zero-dependency rules, and coding standards.
* **[Frequently Asked Questions (FAQ.md)](./FAQ.md):** Rationales behind the anti-conformity judging model and Elo dynamics.
* **[Engineering Roadmap (ROADMAP.md)](./ROADMAP.md):** Planned features, audit enhancements, and presentation layers.

---

## License

Debate-Engine is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
