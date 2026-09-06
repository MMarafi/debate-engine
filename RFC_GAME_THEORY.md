# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: DRAFT / IN REVIEW*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is not to moralize discourse, but to engineer an **Incentive-Compatible Mechanism Design** where strict truthfulness, rigorous evidence production, and objective evaluation form the **strictly dominant strategy** for all participants. Any deviation—such as rhetorical fallacies, evasive omissions, evaluation fatigue, or ideological bias—deterministically reduces a participant's expected utility.

---

## 2. Debater Nash Equilibrium

### A. Debater Utility Function
Each debater seeks to maximize expected zero-sum Elo rating shifts:

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] - C(\text{Fallacy}) - C(\text{Dropped}) - C(\text{MissingEvidence})$$

Where:
* $\mathbb{E}[\Delta\text{Elo}]$: Expected zero-sum Elo rating payoff.
* $C(\dots)$: Point penalties deducted directly from the round score.

---

### B. Strict Equilibrium Invariants

| Defection Strategy | Deterministic Deterrent Mechanism | Nash Equilibrium Outcome |
| :--- | :--- | :--- |
| **Fallacy Deployment (Ad Hominem / Straw Man)** | Asymmetric penalty multiplier: $-2$ deduction per infraction vs. $+1$ per merit point. | Committing a fallacy wipes out the yield of two verified arguments; the strictly dominant strategy is **zero fallacy deployment**. |
| **Rhetorical Evasion (Dropped Targets)** | Unrebutted claims trigger an automatic dropped-argument deduction. | Direct point-by-point refutation minimizes point leakage; the dominant strategy is **inline target deconstruction**. |
| **Gish Gallop (Argument Flooding)** | Strict concision ceiling: 800 tokens maximum per round. | Volumetric flooding is mathematically rejected; the dominant strategy is **dense, concentrated reasoning**. |
| **Unsubstantiated Assertions** | External evidence gate: minimum 1 verifiable URL required. | Submissions missing verified citations fail write-time validation; the dominant strategy is **mandatory sourcing**. |

---

## 3. Judge Nash Equilibrium

### A. The Evaluator Trilemma
Without programmatic incentives, peer evaluation degrades through three vectors:
1. **Lazy Voting:** Submitting low-effort, arbitrary ballots to minimize time investment.
2. **Partisan Bias:** Siding with ideological alignment over argumentative rigor.
3. **Keynesian Beauty Contest:** Voting based on anticipated peer consensus rather than empirical merit.

---

### B. Peer Prediction Mechanism & Calibration Engine
To align self-interest with honest text auditing, evaluator utility is formalized as:

$$U_{\text{judge}} = \text{ProofOfEffort} \times \left( \text{BaseCredit} + W_j \cdot \text{Alignment}(\mathbf{V}_j, \mathbf{V}_{\text{Quorum}}) \right)$$

1. **Proof of Effort Gate:**
   * An attention token is extracted deterministically from the submission payload.
   * Supplying an incorrect token drops the ballot silently without credit or tally impact ($\text{ProofOfEffort} = 0$).

2. **Cumulative Calibration Weight ($W_j$):**
   * Evaluators initialize with a baseline weight $W_j = 1.0$.
   * Ballots are submitted through a blind, independent quorum ($3 \le N \le 5$).
   * Upon quorum resolution, the engine derives the weighted consensus vector ($\mathbf{V}_{\text{Quorum}}$).

3. **Calibration Metric & Outlier Penalty:**
   * Deviation from the independent quorum vector is penalized using a quadratic Brier metric:

   $$\text{Penalty}_{\text{dev}} = \|\mathbf{V}_j - \mathbf{V}_{\text{Quorum}}\|^2$$

   * Biased or stochastic votes diverge from verified peers, triggering:
     * Linear weight depreciation: $W_j \leftarrow W_j - \eta \cdot \text{Penalty}_{\text{dev}}$
     * Decreasing influence in future rounds, culminating in automated disqualification when $W_j$ drops below threshold $\tau$.
   * **Equilibrium Outcome:** The utility-maximizing strategy is **thorough submission reading and unbiased criteria scoring**.

---

## 4. Open Parameters & Mathematical Calibration

* [ ] **Parameter 1: Fallacy Penalty Ratio**
  * Retain $Reward = +1$ vs. $Penalty = -2$, or escalate to $-3$ to guarantee absolute deterrence against high-risk rhetorical gambits?
* [ ] **Parameter 2: Weighted Quorum Resolution Equation ($\mathbf{V}_{\text{Quorum}}$)**
  * Implement weighted majority rounding: $\text{round}\left(\frac{\sum W_j V_j}{\sum W_j}\right)$ or preserve continuous confidence intervals?
* [ ] **Parameter 3: Disqualification Threshold ($\tau$)**
  * Establish the lower bound for $W_j$ before revoking evaluation queue access (e.g., $W_j < 0.4$).
