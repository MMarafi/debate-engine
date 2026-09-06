# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: RATIFIED / PRODUCTION-READY SPECIFICATION (v2.3)*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is to engineer an **Incentive-Compatible Mechanism Design** where strict truthfulness, empirical sourcing, dialectical integrity, and uncorrupted textual auditing form the **strictly dominant strategy** for all participants. Any deviation—such as rhetorical fallacies, tactical abandonment, evasion, lazy auditing, herd conformity, sybil collusion, or partisan bias—deterministically reduces a participant's expected utility across dual evaluation ledgers.

---

## 2. Dual-Ledger Debater Architecture & Anti-Exploit Protocols

The debater evaluation engine separates competitive standing from ethical behavior across two distinct ledgers:

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

### C. Sybil-Resistant Rehabilitation Farming
To prevent collusive accounts from farming reputation recovery in low-friction private matches:

* **Queue Invariant:** Rehabilitation credit ($+0.5$ reputation points per clean round) is granted **exclusively in Ranked Random Matchmaking**. Direct-challenge or unranked matches yield zero reputation recovery.
* **Minimum Textual Density Gate:** The submitted text must contain at least **200 words** ($L \ge 200$) to trigger clean-round recovery, preventing low-effort filler text from farming trust.
* **Cap Ceiling:** Total reputation cannot exceed the initial baseline:

$$R_{t+1} = \min\left(100.0, \, R_t + \sum \text{CleanRoundBonus} - \sum \text{Penalties}\right)$$

* **Gating Rules:**
  * **Elite Queue Lockout:** Users with $R_t < 75.0$ are barred from high-tier competitive pools.
  * **Automated Quarantine:** If $R_t < 50.0$, write permissions are suspended until completing interactive logical fallacy modules.

---

## 3. Judge Nash Equilibrium & Tripartite Canary Consensus

### A. Regularized Robust Bayesian Truth Serum (Micro-Quorums $3 \le N \le 5$)
To prevent division-by-zero singularities and explosive information bonuses caused by malicious peer predictions ($y_j \to 0$), the engine applies Laplace smoothing ($\epsilon = 0.05$):

$$\text{Score}_{\text{info}, j} = \sum_{k=1}^K \ln\left(\frac{\bar{x}_k + \epsilon}{\bar{y}_k + \epsilon}\right) \cdot \mathbf{I}(x_{j, k} = 1)$$

$$\text{Score}_{\text{pred}, j} = -\alpha \sum_{k=1}^K (y_{j, k} - \bar{x}_k)^2$$

Where:
* $\bar{x}_k$: Quorum average endorsement for criterion $k$.
* $\bar{y}_k$: Geometric mean of peer predictions regularized by $\epsilon$.
* $\epsilon = 0.05$: Prevents mathematical collapse under adversarial inputs.

---

### B. Anti-Collusion via Tripartite Canary Quorum (Supreme Audit)
To eliminate false-positive slashing caused by a single infallible expert's error:

1. **Spot-Audit Sampling:** $10\%$ of completed quorums are routed into the verification pipeline.
2. **Tripartite Canary Quorum:** The audit panel consists of **three independent benchmark judges** ($W_c \ge 2.0$).
3. **Unanimous Slashing Threshold:** Weight slashing of the standard quorum majority occurs **strictly if and only if all three Canary judges achieve 100% unanimous consensus** against the standard quorum's decision:

$$\text{Slashing Triggered} \iff \sum_{c=1}^3 \mathbf{I}(\text{Canary}_c = \text{Consensus}_{\text{Canary}}) = 3 \quad \land \quad \text{Consensus}_{\text{Canary}} \ne \mathbf{V}^*_{\text{Quorum}}$$

* **Slashing Severity:** Slashing reduces the deviant majority's calibration weights by 80%:

$$W_j \leftarrow W_j \times 0.20 \quad (\text{Immediate Pool Quarantine})$$

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

3. **Dynamic Quarantine Floor ($\tau_t$):**
   $$\tau_t = \max\left(0.30, \, \mu_W - 2\sigma_W\right)$$

---

## 4. Ratified Mathematical Parameters (v2.3 Production Baseline)

| Parameter | Identifier | Value | Justification |
| :--- | :--- | :--- | :--- |
| **Fallacy Round Deduction** | $C_f$ | `-3` | Ensures strictly negative expected round payoff. |
| **Fallacy Reputation Penalty** | $\Delta R_{\text{penalty}}$ | `-10.0` | Severe deterrent directly affecting matchmaking eligibility. |
| **Timeout / Forfeit Penalty** | $\Delta R_{\text{timeout}}$ | **`-15.0`** | Prevents tactical abandonment to shield reputation. |
| **Rehabilitation Increment** | $\Delta R_{\text{clean}}$ | `+0.5` | Asymmetric slow recovery enforcing long-term compliance. |
| **Rehabilitation Preconditions** | `Rehab_Reqs` | **Ranked Match + $\ge 200$ words** | Eliminates sybil collusive reputation farming. |
| **Laplace Smoothing Regularizer** | $\epsilon$ | `0.05` | Prevents RBTS denominator collapse in micro-quorums. |
| **Audit Sampling Frequency** | $P_{\text{audit}}$ | `0.10` | Dismantles small-quorum sybil collusion economics. |
| **Canary Audit Panel** | `Audit_Size` | **3 Canary Judges (100% Unanimous)** | Eliminates false-positive slashing from single-auditor error. |
| **Canary Slashing Penalty** | $\text{Slash}_{\text{ratio}}$ | `0.20 (80% drop)` | Immediate quarantine for collusive or negligent judges. |
| **Minimum Reading Time** | $T_{\text{min}}$ | `120s` | Physiological human reading ceiling for 800-word payloads. |
| **Calibration Learning Rate** | $\eta$ | `0.15` | Smooth multiplicative calibration damping noise. |
| **Dynamic Quarantine Floor** | $\tau$ | `\mu_W - 2\sigma_W` | Adapts dynamically to debate complexity without systemic drift. |
| **URL Regex Pattern** | `URL_GATE` | Strict Exclusion | Excludes trailing punctuation: `(?:\/[^\s.,;:!?)]*)?`. |
