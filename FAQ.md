# Frequently Asked Questions (FAQ)

### Governance & Game-Theory Design

#### Why does the platform reject majority vote and peer consensus scoring for judges?
Truth and logical validity are not democratic. Rewarding judges based on peer consensus introduces a **Keynesian Beauty Contest** dynamic, where evaluators vote based on what they expect the majority to choose rather than analyzing arguments objectively. It also creates a severe vulnerability to groupthink and coordinated voting blocs (Sybil attacks). The platform relies exclusively on **independent, blind ballots** where judges evaluate verifiable criteria without exposure to peer influence or majority alignment.

#### How are round winners determined?
Judges never cast a subjective "winner takes all" ballot. Instead, they complete an algebraic rubric scoring discrete dimensions:
* **Positive Dimensions (+1 each):** Superior Empirical Evidence, Effective Refutation, and Internal Logical Consistency.
* **Fallacy Deductions (-1 each):** Ad Hominem attacks and Straw Man distortions.

The debater with the higher aggregated score across all independent ballots wins the round.

#### How does the rating system work?
The engine implements a pure **Zero-Sum Elo Rating** algorithm ($K=32$):
* Any rating points gained by the victor are deducted in equal measure from the loser.
* Upsets (a lower-rated debater defeating a higher-rated opponent) yield higher point shifts, ensuring rapid skill calibration and zero point inflation.

#### How does the platform prevent random or automated judge voting?
The system utilizes a deterministic **Attention Verification Challenge**. The core engine derives a secret word challenge based on the hash of round characters. An evaluator must provide the token corresponding to an arbitrary, human-indexed position in the text before their ballot is accepted by `calculate_ballot_scores`. Ballots failing this verification are rejected automatically prior to any algebraic aggregation.

---

### Procedural & Input Gates

#### Why is there a strict 800-word limit per round?
To structurally eliminate the **Gish Gallop** tactic—an adversarial debating technique where a participant floods the exchange with superficial arguments to overwhelm their opponent. Strict concision forces debaters to extract and defend only their most rigorous premises.

#### What happens if a debater misses the 48-hour turn window?
The debate immediately terminates under the **Deterministic Forfeit Rule**. The active participant is awarded an automatic win via disqualification, and the non-responsive party incurs a zero-sum Elo forfeit penalty without requiring peer adjudication.

#### Why is at least one external URL mandatory per submission?
To differentiate substantive empirical claims from rhetorical assertions. Submissions missing an authoritative source citation fail the automated input gate (`ERR_MISSING_EVIDENCE`) and cannot be committed to the debate ledger.

#### Why is Inline Refutation handled in the frontend rather than the core engine?
Paragraph-level pairing and tagging dropped arguments (e.g., `[Unrebutted / لم يتم الرد]`) is a structural presentation concern, not an algebraic game-theory invariant. Keeping UI parsing and visual reconstruction in the Next.js and adapter layers preserves the zero-dependency purity of `backend/core/`, allowing the mathematical engine to evaluate submissions purely on length, evidence integrity, and scoring metrics.

---

### Technical Architecture

#### Why is the core engine isolated without framework dependencies?
The game-theory engine (`backend/core/`) is designed to be deterministic and timeless. By relying strictly on the Python Standard Library, the platform guarantees mathematical reproducibility, prevents framework lock-in, and allows the validation logic to execute consistently across any environment.
