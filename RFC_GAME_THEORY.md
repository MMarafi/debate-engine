# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: RATIFIED / TARGET SPECIFICATION (v2.2)*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is to engineer an **Incentive-Compatible Mechanism Design** where strict truthfulness, empirical sourcing, dialectical integrity, and uncorrupted textual auditing form the **strictly dominant strategy** for all participants. Any deviation—such as rhetorical fallacies, evasive omissions, lazy auditing, herd conformity, sybil collusion, or partisan bias—deterministically reduces a participant's expected utility across dual evaluation ledgers.

---

## 2. Dual-Ledger Debater Architecture & Nash Equilibrium

To prevent structural point deflation in zero-sum rating pools while preserving severe behavioral deterrence, the debater evaluation engine is decoupled into two independent ledgers:

| Dimension | Skill Rating (`Elo Rating`) | Behavioral Integrity (`Reputation Score`) |
| :--- | :--- | :--- |
| **Primary Objective** | Measures dialectical skill and argument potency | Measures empirical honesty and rule compliance |
| **Mathematical Nature** | Zero-Sum ($\Delta\text{PRO} + \Delta\text{CON} = 0$) | Non-Zero-Sum state ledger ($R \in [0, 100]$) |
| **Matchmaking Role** | Pairs competitors with equivalent skill tiers | Acts as an access gatekeeper (`Gatekeeper`) |
| **Fallacy Impact** | Reduces round win probability algebraically | Direct and persistent deduction from reputation pool |

---

### A. Debater Utility Function

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] + \gamma \cdot \mathbb{E}[\Delta R] - C(\text{Dropped}) - C(\text{MissingEvidence})$$

Where:
* $\mathbb{E}[\Delta\text{Elo}]$: Zero-sum skill rating payoff.
* $R$: Integrity index governing platform permissions and queue tiers.
* $\gamma$: Utility scaling coefficient weighting reputation against rank.

---

### B. Match Resolution vs. Reputation Updates

1. **Algebraic Round Outcome (Zero-Sum Invariant):**
   * Fallacy deductions ($C_f = -3$) depress algebraic points within round ballots to decide round winners.
   * Total match outcome is converted to standard discrete signals ($W \in \{1.0, 0.5, 0.0\}$).
   * Elo transfer is strictly zero-sum; point deductions never deflate the macro-rating economy:

$$\Delta\text{Elo}_{\text{PRO}} + \Delta\text{Elo}_{\text{CON}} = 0$$

2. **Reputation Ledger Update ($R_t$):**
   * Independently of win/loss outcomes, each debater's reputation pool updates post-match:

$$R_{t+1} = \min\left(100.0, \, R_t + \sum \text{CleanRoundBonus} - \sum \text{FallacyPenalty}\right)$$

   * **Violation Penalty:** $-10.0$ reputation points per verified fallacy.
   * **Rehabilitation Credit:** $+0.5$ reputation points per completely fallacy-free round.

3. **Reputation Gating Invariants:**
   * **Elite Queue Lockout:** Users with $R_t < 75.0$ are barred from high-tier competitive pools regardless of Elo rating.
   * **Automated Quarantine:** If $R_t < 50.0$, write access is automatically suspended until completing interactive fallacy-deconstruction modules.

---

## 3. Judge Nash Equilibrium & Quorum Hardening

### A. Regularized Robust Bayesian Truth Serum (Micro-Quorums $3 \le N \le 5$)
To prevent division-by-zero singularities and explosive information bonuses caused by malicious or outlier peer predictions ($y_j \to 0$), the engine applies Laplace smoothing ($\epsilon = 0.05$):

$$\text{Score}_{\text{info}, j} = \sum_{k=1}^K \ln\left(\frac{\bar{x}_k + \epsilon}{\bar{y}_k + \epsilon}\right) \cdot \mathbf{I}(x_{j, k} = 1)$$

$$\text{Score}_{\text{pred}, j} = -\alpha \sum_{k=1}^K (y_{j, k} - \bar{x}_k)^2$$

Where:
* $\bar{x}_k$: Quorum average endorsement for criterion $k$.
* $\bar{y}_k$: Geometric mean of peer predictions regularized by $\epsilon$.
* $\epsilon = 0.05$: Prevents mathematical collapse under adversarial inputs.

---

### B. Sybil Collusion Resistance: Spot-Audit Protocol
To counter sockpuppet rings attempting majority capture in micro-quorums ($N = 3$):

1. **Hidden Audit Invariant:** 
   * A pseudo-random sampling gate flags $10\%$ of completed quorums for deterministic audit verification.
   * Audits are evaluated against high-reputation canary judges ($W_j \ge 2.0$) or pre-verified ground-truth benchmarks.
2. **Slashing Penalty:**
   * If a quorum majority contradicts the verified audit benchmark with statistical significance, the deviant majority's calibration weights are immediately slashed:

$$W_j \leftarrow W_j \times 0.20 \quad (\text{Immediate Quarantine})$$

---

### C. Multi-Vector Proof of Effort
1. **Deterministic Minimum Reading Bound ($T_{\text{min}}$):**
   $$\Delta t = t_{\text{sub}} - t_{\text{open}} \ge 120\text{ seconds}$$
   Submissions faster than physiological reading ceilings are discarded silently.
2. **Quote-Target Semantic Binding:**
   Judges must select the exact rebuttal anchor referenced by the debater from 3 deterministically hashed excerpts.

---

### D. Multiplicative Weight Calibration & Dynamic Quarantine

1. **Continuous Weighted Quorum Vector ($\mathbf{V}^*$):**
   $$\mathbf{V}^*_k = \frac{\sum_{j=1}^N W_j \cdot x_{j, k}}{\sum_{j=1}^N W_j}, \quad \forall k \in \{1, \dots, K\}$$

2. **Multiplicative Exponential Weight Update:**
   $$\text{Penalty}_{\text{dev}, j} = \frac{1}{K} \sum_{k=1}^K (x_{j, k} - \mathbf{V}^*_k)^2$$

   $$W_j^{(t+1)} = W_j^{(t)} \cdot \exp\left(-\eta \cdot \text{Penalty}_{\text{dev}, j}\right)$$

3. **Dynamic Quarantine Threshold ($\tau_t$):**
   $$\tau_t = \max\left(0.30, \, \mu_W - 2\sigma_W\right)$$

---

## 4. Ratified Parameter Matrix

| Parameter | Identifier | Value | Justification |
| :--- | :--- | :--- | :--- |
| **Fallacy Deduction (Round Score)** | $C_f$ | `-3` | Ensures strictly negative expected round payoff. |
| **Fallacy Penalty (Reputation)** | $\Delta R_{\text{penalty}}$ | `-10.0` | Severe deterrent directly hitting queue eligibility. |
| **Rehabilitation Increment** | $\Delta R_{\text{clean}}$ | `+0.5` | Asymmetric slow recovery enforcing long-term compliance. |
| **Laplace Smoothing Regularizer** | $\epsilon$ | `0.05` | Prevents RBTS denominator collapse in micro-quorums. |
| **Spot-Audit Sampling Frequency** | $P_{\text{audit}}$ | `0.10` | Dismantles small-quorum sybil collusion economics. |
| **Minimum Reading Time** | $T_{\text{min}}$ | `120s` | Physiological human reading ceiling for 800-word payloads. |
| **Calibration Learning Rate** | $\eta$ | `0.15` | Smooth multiplicative calibration damping noise. |
| **Dynamic Quarantine Floor** | $\tau$ | `\mu_W - 2\sigma_W` | Adapts dynamically to debate complexity without systemic drift. |
| **URL Regex Pattern** | `URL_GATE` | Strict Exclusion | Excludes trailing punctuation: `(?:\/[^\s.,;:!?)]*)?`. |
