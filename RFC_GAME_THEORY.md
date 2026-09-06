# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: RATIFIED / TARGET SPECIFICATION*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is to establish an **Incentive-Compatible Mechanism Design** where strict truthfulness, empirical evidence submission, and rigorous text auditing form the **strictly dominant strategy** for all participants. Any strategic deviation—such as fallacy deployment, evasion, lazy auditing, or partisan bias—deterministically minimizes a participant's expected utility.

---

## 2. Debater Nash Equilibrium

### A. Debater Utility Function
Each debater seeks to maximize expected zero-sum Elo rating shifts:

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] - C(\text{Fallacy}) - C(\text{Dropped}) - C(\text{MissingEvidence})$$

Where:
* $\mathbb{E}[\Delta\text{Elo}]$: Expected zero-sum Elo payoff.
* $C(\dots)$: Deterministic point deductions evaluated across round criteria.

---

### B. Fallacy Deterrence Bound (Mathematical Proof)
Let a debater decide whether to deploy a deceptive fallacy yielding potential strategic merit $\Delta M \in \{1, 2\}$, detected by peer evaluators with probability $p \in (0, 1]$, and penalized by cost $C_f$:

$$\mathbb{E}[\Delta U] = (1 - p) \cdot \Delta M - p \cdot C_f < 0 \implies C_f > \left(\frac{1 - p}{p}\right) \Delta M$$

Under worst-case evaluation noise where $p \approx 0.5$ and $\Delta M = 2$:

$$C_f > \left(\frac{1 - 0.5}{0.5}\right) \cdot 2 = 2.0$$

Setting $C_f = 3$ establishes strict dominance: even under high evaluation noise, the expected value of deploying a fallacy is strictly negative ($\mathbb{E}[\Delta U] < 0$).

---

### C. Equilibrium Invariants

| Defection Strategy | Deterministic Deterrent Mechanism | Nash Equilibrium Outcome |
| :--- | :--- | :--- |
| **Fallacy Deployment (Ad Hominem / Straw Man)** | Asymmetric penalty multiplier: $C_f = -3$ per infraction vs. $+1$ per positive merit. | The expected utility is strictly negative ($\mathbb{E}[\Delta U] < 0$); dominant strategy is **zero fallacy deployment**. |
| **Rhetorical Evasion (Dropped Targets)** | Unrebutted claims trigger an automatic dropped-argument deduction. | Point leakage minimization enforces **point-by-point refutation**. |
| **Gish Gallop (Flooding)** | Strict concision ceiling: 800 tokens maximum per round. | Volumetric saturation fails write-time validation; dominant strategy is **dense, concentrated reasoning**. |
| **Unsubstantiated Assertions** | External evidence gate: minimum 1 verifiable URL required. | Code rejects submissions missing citations; dominant strategy is **mandatory sourcing**. |

---

## 3. Judge Nash Equilibrium

### A. The Evaluator Trilemma
Without programmatic incentives, peer evaluation degrades via three vectors:
1. **Lazy Voting:** Submitting arbitrary ballots to minimize reading effort.
2. **Partisan Bias:** Siding with ideological alignment over argumentative rigor.
3. **Keynesian Beauty Contest:** Voting based on anticipated peer consensus rather than empirical truth.

---

### B. Peer Prediction Mechanism & Continuous Quorum Consensus
Evaluator utility is strictly tied to reading verification and consensus alignment:

$$U_{\text{judge}} = \text{ProofOfEffort} \times \left( \text{BaseCredit} + W_j \cdot \text{Alignment}(\mathbf{V}_j, \mathbf{V}^*) \right)$$

1. **Proof of Effort Gate:**
   * Attention token derived deterministically from the payload. Incorrect submission discards the ballot silently ($\text{ProofOfEffort} = 0$).

2. **Continuous Weighted Quorum Vector ($\mathbf{V}^*$):**
   To eliminate step-function discontinuity and collusive coordination, the quorum consensus preserves continuous coordinates in $[0, 1]^K$ across all $N$ judges ($3 \le N \le 5$):

   $$\mathbf{V}^*_k = \frac{\sum_{j=1}^N W_j \cdot v_{j, k}}{\sum_{j=1}^N W_j}, \quad \forall k \in \{1, \dots, K\}$$

3. **Multiplicative Weight Calibration:**
   Deviation is measured using the Mean Squared Brier Penalty across $K$ dimensions:

   $$\text{Penalty}_{\text{dev}, j} = \frac{1}{K} \sum_{k=1}^K (v_{j, k} - \mathbf{V}^*_k)^2$$

   Evaluator weight updates follow an exponential decay formulation with learning rate $\eta = 0.15$:

   $$W_j^{(t+1)} = W_j^{(t)} \cdot \exp\left(-\eta \cdot \text{Penalty}_{\text{dev}, j}\right)$$

   * Preserves non-negativity ($W_j > 0$) without boundary clipping artifacts.
   * Judges whose calibrated weight drops below $\tau = 0.45$ are automatically quarantined from the evaluation pool.
   * **Equilibrium Outcome:** Sincere, objective text auditing is the unique payoff-maximizing strategy.

---

## 4. Ratified Mathematical Parameters

* **Fallacy Penalty ($C_f$):** **`-3`** (Guarantees negative expected utility even when detection probability $p \approx 0.5$).
* **Quorum Representation:** **Continuous Vector Space $[0, 1]^K$** (Prevents collusive step-function coordination).
* **Calibration Learning Rate ($\eta$):** **`0.15`** (Smooth convergence preventing volatile weight swings).
* **Quarantine Threshold ($\tau$):** **`0.45`** (Disqualifies judges performing near random chance).
