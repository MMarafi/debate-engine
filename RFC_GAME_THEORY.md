# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: RATIFIED / PRODUCTION-READY SPECIFICATION (v2.4)*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is to engineer an **Incentive-Compatible Mechanism Design** where strict truthfulness, empirical sourcing, dialectical integrity, and uncorrupted textual auditing form the **strictly dominant strategy** for all participants. Any strategic deviation—such as rhetorical fallacies, tactical abandonment, evasion, lazy auditing, herd conformity, sybil collusion, or partisan bias—deterministically reduces a participant's expected utility across dual evaluation ledgers.

---

## 2. Dual-Ledger Debater Architecture & Anti-Exploit Protocols

| Dimension | Skill Rating (`Elo Rating`) | Behavioral Integrity (`Reputation Score`) |
| :--- | :--- | :--- |
| **Primary Objective** | Measures dialectical skill and argument potency | Measures empirical honesty and rule compliance |
| **Mathematical Nature** | Zero-Sum ($\Delta\text{PRO} + \Delta\text{CON} = 0$) | Non-Zero-Sum state ledger ($R \in [0, 100]$) |
| **Matchmaking Role** | Pairs competitors with equivalent skill tiers | Acts as an access gatekeeper (`Gatekeeper`) |
| **Fallacy Impact** | Reduces round win probability algebraically | Direct deduction from reputation pool |

---

### A. Debater Utility Function

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] + \gamma \cdot \mathbb{E}[\Delta R] - C(\text{Dropped}) - C(\text{MissingEvidence})$$

Where:
* $\mathbb{E}[\Delta\text{Elo}]$: Zero-sum skill rating payoff.
* $R$: Integrity index governing platform permissions and queue tiers.
* $\gamma$: Utility scaling coefficient weighting reputation against rank.

---

### B. Anti-Abandonment Bound: Closing Tactical Timeouts
To prevent debaters from deliberately abandoning matches (`Timeout`) to shield their reputation from detected fallacies:

$$|\text{Penalty}_{\text{Timeout}}| > |\text{Penalty}_{\text{Fallacy}}|$$

* **Fallacy Deduction:** $-10.0$ reputation points per verified fallacy.
* **Forfeit / Timeout Penalty:** Assessed as a forfeit loss via `calculate_zero_sum_elo` PLUS a deterministic deduction of **`-15.0` reputation points**.
* **Equilibrium Invariant:** Completing the debate round (even with flawed arguments) strictly Pareto-dominates silent abandonment.

---

### C. Sybil-Resistant Rehabilitation Farming & Economic Quarantine
To prevent collusive accounts from farming reputation recovery or bypassing suspensions at zero marginal cost:

* **Queue Invariant:** Rehabilitation credit ($+0.5$ reputation points per clean round) is granted **exclusively in Ranked Random Matchmaking**. Direct-challenge or unranked matches yield zero reputation recovery.
* **Minimum Textual Density Gate:** The submitted text must contain at least **200 words** ($L \ge 200$) to trigger clean-round recovery.
* **Economic & Time-Locked Quarantine ($R_t < 50.0$):**
  * Automatic write-permission revocation.
  * **Mandatory Cooling-Off Lock:** Account remains frozen for a non-negotiable **14-day deterministic lock** ($\Delta t_{\text{lock}} = 14\text{d}$) regardless of quiz completion, destroying the economic return on automated bot deployment.
  * **Proof of Calibration:** Reinstatement requires completing 5 consecutive canary-verified audit ballots with $100\%$ accuracy, proving active evaluative effort.

---

## 3. Judge Nash Equilibrium & Hardened Small-Quorum Mechanics

### A. Leave-One-Out Robust Bayesian Truth Serum (LOO-RBTS)
To eliminate self-influence in micro-quorums ($3 \le N \le 5$) where a judge's own ballot inflates the consensus, all aggregations strictly utilize **Leave-One-Out (LOO)** formulations.

For judge $j$ evaluating criterion $k$:
1. **Leave-One-Out Endorsement Mean ($\bar{x}_{-j, k}$):**
   $$\bar{x}_{-j, k} = \frac{1}{N - 1} \sum_{i \ne j} x_{i, k}$$
2. **Leave-One-Out Geometric Mean Prediction ($\bar{y}_{-j, k}$):**
   $$\bar{y}_{-j, k} = \exp\left(\frac{1}{N - 1} \sum_{i \ne j} \ln(y_{i, k} + \epsilon)\right) - \epsilon$$

#### 1. Information Score (Scoring Unexpected Truthfulness):
$$\text{Score}_{\text{info}, j} = \sum_{k=1}^K \ln\left(\frac{\bar{x}_{-j, k} + \epsilon}{\bar{y}_{-j, k} + \epsilon}\right) \cdot (x_{j, k} - y_{j, k})$$

* **Incentive Compatibility Proof:** Because $\bar{x}_{-j, k}$ and $\bar{y}_{-j, k}$ are calculated independently of judge $j$'s inputs, judge $j$ cannot inflate the ratio by altering their own endorsement ($x_{j, k}$). Truth-telling strictly maximizes expected payoff.

#### 2. Prediction Calibration (Quadratic Scoring Rule):
$$\text{Score}_{\text{pred}, j} = -\alpha \sum_{k=1}^K (y_{j, k} - \bar{x}_{-j, k})^2$$

---

### B. Dynamic Tiered Slashing (Fault-Tolerant Canary Quorum)
To dismantle the single-point-of-failure vulnerability (where 1 corrupted Canary prevents all penalties), the audit panel adopts a **Tiered Threshold Consensus**:

* A spot-audit triggers across $10\%$ of finished matches, reviewed by 3 independent canary judges ($W_c \ge 2.0$).
* Let $M_{\text{agree}}$ be the number of canary judges who conclude that the standard quorum majority committed an evaluative violation:

$$\text{Slashing Action} = 
\begin{cases} 
\text{No Penalty}, & \text{if } M_{\text{agree}} \le 1 \quad (\text{Ambiguous / Dissent}) \\
W_j \leftarrow W_j \times 0.60 \quad (\text{Partial Slashing } 40\%), & \text{if } M_{\text{agree}} = 2 \quad (\text{Supermajority Violation}) \\
W_j \leftarrow W_j \times 0.20 \quad (\text{Full Slashing } 80\% + \text{Quarantine}), & \text{if } M_{\text{agree}} = 3 \quad (\text{Unanimous Violation})
\end{cases}$$

* **Property:** A single rogue canary cannot block enforcement; a 2-of-3 supermajority still penalizes collusive quorums, while unanimous agreement guarantees total quarantine.

---

### C. Cognitive Proof of Effort (Semantic Rebuttal Binding)
Relying on a latency timer ($T_{\text{min}} = 120\text{s}$) is vulnerable to simple execution sleep delays. Therefore, cognitive verification is promoted to an **absolute gating invariant**:

1. **Semantic Rebuttal Challenge:**
   * Judges are presented with a deterministically hashed set of 3 candidate argument quotes from the opponent's prior turn.
   * Judges must identify the exact premise targeted by the current speaker's rebuttal.
2. **Gating Invariant:**
   * **Failure to identify the correct semantic anchor drops the ballot completely** (`ProofOfEffort = 0`). The ballot is discarded from quorum aggregation and yields zero rewards.
3. **Passive Latency Check:** $T_{\text{min}} = 120\text{s}$ remains only as a secondary sanity filter, not the primary proof.

---

### D. Multiplicative Weight Calibration & Dynamic Quarantine

1. **Leave-One-Out Consensus Distance:**
   $$\text{Penalty}_{\text{dev}, j} = \frac{1}{K} \sum_{k=1}^K (x_{j, k} - \bar{x}_{-j, k})^2$$

2. **Multiplicative Exponential Weight Update:**
   $$W_j^{(t+1)} = W_j^{(t)} \cdot \exp\left(-\eta \cdot \text{Penalty}_{\text{dev}, j}\right)$$

3. **Dynamic Quarantine Floor ($\tau_t$):**
   $$\tau_t = \max\left(0.30, \, \mu_W - 2\sigma_W\right)$$

---

## 4. Ratified Mathematical Parameters (v2.4 Final Baseline)

| Parameter | Identifier | Value | Justification |
| :--- | :--- | :--- | :--- |
| **Fallacy Round Deduction** | $C_f$ | `-3` | Ensures strictly negative expected round payoff. |
| **Fallacy Reputation Penalty** | $\Delta R_{\text{penalty}}$ | `-10.0` | Severe deterrent directly affecting matchmaking eligibility. |
| **Timeout / Forfeit Penalty** | $\Delta R_{\text{timeout}}$ | `-15.0` | Strictly dominates tactical abandonment. |
| **Quarantine Cooldown Lock** | $\Delta t_{\text{lock}}$ | **`14 Days`** | Destroys economic incentive for automated sybil recycling. |
| **RBTS Consensus Metric** | $\bar{x}_{-j, k}$ | **Leave-One-Out (LOO)** | Eliminates self-influence and herding in small quorums. |
| **Laplace Smoothing Regularizer**| $\epsilon$ | `0.05` | Regularizes geometric mean and avoids singular log limits. |
| **Audit Sampling Frequency** | $P_{\text{audit}}$ | `0.10` | Random spot-auditing over completed debate quorums. |
| **Canary Slashing Consensus** | `Canary_Tier` | **Tiered (2/3 = -40%, 3/3 = -80%)** | Eliminates single-auditor veto vulnerability. |
| **Primary Proof of Effort** | `PoE_Primary` | **Semantic Rebuttal Binding** | Enforces cognitive reading comprehension; cannot be bypassed by sleep delays. |
| **Calibration Learning Rate** | $\eta$ | `0.15` | Multiplicative decay damping parameter. |
| **Dynamic Quarantine Floor** | $\tau$ | `\mu_W - 2\sigma_W` | Adaptive baseline isolating statistically aberrant judges. |
| **URL Regex Pattern** | `URL_GATE` | Strict Exclusion | Excludes trailing punctuation: `(?:\/[^\s.,;:!?)]*)?`. |
