# RFC 001: Game-Theoretic Incentive Design & Nash Equilibrium
*Status: RATIFIED / TARGET SPECIFICATION (v2.1)*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy

The objective is to engineer an **Incentive-Compatible Mechanism Design** where strict truthfulness, empirical sourcing, and uncorrupted textual auditing form the **strictly dominant strategy** for all participants. Any deviation—such as rhetorical fallacies, evasive omissions, lazy auditing, herd conformity, or partisan bias—deterministically reduces a participant's expected utility.

---

## 2. Debater Nash Equilibrium

### A. Debater Utility Function
Each debater seeks to maximize expected zero-sum Elo rating shifts:

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] - C(\text{Fallacy}) - C(\text{Dropped}) - C(\text{MissingEvidence})$$

Where:
* $\mathbb{E}[\Delta\text{Elo}]$: Expected zero-sum Elo rating payoff.
* $C(\dots)$: Deterministic point deductions evaluated across round criteria.

---

### B. Fallacy Deterrence Bound (Mathematical Proof)
Let a debater decide whether to deploy a deceptive fallacy yielding potential strategic merit $\Delta M \in \{1, 2\}$, detected by peer evaluators with probability $p \in (0, 1]$, and penalized by cost $C_f$:

$$\mathbb{E}[\Delta U] = (1 - p) \cdot \Delta M - p \cdot C_f < 0 \implies C_f > \left(\frac{1 - p}{p}\right) \Delta M$$

Under worst-case evaluation noise where $p \approx 0.5$ and $\Delta M = 2$:

$$C_f > \left(\frac{1 - 0.5}{0.5}\right) \cdot 2 = 2.0$$

Setting $C_f = 3$ establishes strict dominance: even under elevated evaluation noise, the expected value of deploying a fallacy is strictly negative ($\mathbb{E}[\Delta U] < 0$).

---

### C. Equilibrium Invariants

| Defection Strategy | Deterministic Deterrent Mechanism | Nash Equilibrium Outcome |
| :--- | :--- | :--- |
| **Fallacy Deployment (Ad Hominem / Straw Man)** | Asymmetric penalty multiplier: $C_f = -3$ per infraction vs. $+1$ per positive merit. | Expected utility is strictly negative ($\mathbb{E}[\Delta U] < 0$); dominant strategy is **zero fallacy deployment**. |
| **Rhetorical Evasion (Dropped Targets)** | Unrebutted claims trigger an automatic dropped-argument deduction. | Point leakage minimization enforces **point-by-point refutation**. |
| **Gish Gallop (Flooding)** | Strict concision ceiling: 800 tokens maximum per round. | Volumetric saturation fails write-time validation; dominant strategy is **dense, concentrated reasoning**. |
| **Unsubstantiated Assertions** | External evidence gate: minimum 1 verifiable URL required, parsed with strict trailing punctuation exclusion: `https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s.,;:!?)]*)?`. | Code rejects submissions missing citations; dominant strategy is **mandatory sourcing**. |

---

## 3. Judge Nash Equilibrium

### A. The Evaluator Trilemma & Keynesian Beauty Contest
Without programmatic counter-incentives, peer evaluation degrades through three vectors:
1. **Lazy Voting:** Submitting low-effort ballots to maximize speed.
2. **Partisan Bias:** Favoring ideological alignment over dialectical rigor.
3. **Keynesian Beauty Contest:** Voting for the anticipated majority opinion rather than empirical truth to protect consensus scores.

---

### B. Anti-Collusive Evaluation Mechanism (Robust Bayesian Truth Serum)
To dismantle herd conformity and align self-interest with honest evaluation, the engine incorporates the principles of **Robust Bayesian Truth Serum (RBTS)** adapted for small quorums ($3 \le N \le 5$):

Each judge $j$ submits two discrete inputs per criterion $k$:
1. **Endorsement ($x_{j, k} \in \{0, 1\}$):** Objective determination of criterion presence.
2. **Peer Prediction ($y_{j, k} \in [0, 1]$):** Predicted fraction of peer judges endorsing the criterion.

#### 1. Information Score (Rewarding the "Surprisingly Common"):
Evaluators who identify subtle dialectical violations or strong empirical proofs that lazy evaluators miss receive an information bonus when their endorsement frequency exceeds aggregate prediction:

$$\text{Score}_{\text{info}, j} = \sum_{k=1}^K \ln\left(\frac{\bar{x}_k}{\bar{y}_k}\right) \cdot \mathbf{I}(x_{j, k} = 1)$$

* Where $\bar{x}_k$ is the quorum average endorsement and $\bar{y}_k$ is the geometric mean of peer predictions.
* **Property:** Honest reporting Pareto-dominates coordination around superficial consensus.

#### 2. Prediction Calibration (Quadratic Scoring Rule):
Evaluators are scored on how accurately they forecast quorum distribution, penalizing arbitrary guessing:

$$\text{Score}_{\text{pred}, j} = -\alpha \sum_{k=1}^K (y_{j, k} - \bar{x}_k)^2$$

---

### C. Multi-Vector Proof of Effort (Anti-Scripting Gate)
To prevent automated headless browser exploits and trivial scraping of deterministic hash tokens, proof of effort is guarded by two mandatory invariants:

1. **Deterministic Minimum Reading Bound ($T_{\text{min}}$):**
   * Reading latency is measured strictly between ballot presentation ($t_{\text{open}}$) and ballot submission ($t_{\text{sub}}$).
   * For an 800-word submission, human physiological ceiling bounded at 300 WPM requires:
   $$\Delta t = t_{\text{sub}} - t_{\text{open}} \ge 120\text{ seconds}$$
   * Submissions submitted with $\Delta t < T_{\text{min}}$ are dropped silently.

2. **Quote-Target Semantic Binding:**
   * Judges must select the exact rebuttal anchor referenced by the debater from 3 deterministically hashed excerpts. Scripting requires full natural language semantic parsing rather than reading a single index token.

---

### D. Multiplicative Weight Calibration & Dynamic Quarantining

1. **Continuous Weighted Quorum Vector ($\mathbf{V}^*$):**
   $$\mathbf{V}^*_k = \frac{\sum_{j=1}^N W_j \cdot x_{j, k}}{\sum_{j=1}^N W_j}, \quad \forall k \in \{1, \dots, K\}$$

2. **Multiplicative Exponential Weight Update:**
   $$\text{Penalty}_{\text{dev}, j} = \frac{1}{K} \sum_{k=1}^K (x_{j, k} - \mathbf{V}^*_k)^2$$

   $$W_j^{(t+1)} = W_j^{(t)} \cdot \exp\left(-\eta \cdot \text{Penalty}_{\text{dev}, j}\right)$$

3. **Dynamic Quarantining Threshold ($\tau_t$):**
   Instead of a static threshold, an evaluator is quarantined if their reliability falls beyond two standard deviations from the active judge population mean:

   $$\tau_t = \max\left(0.30, \, \mu_W - 2\sigma_W\right)$$

   * Eliminates systemic drift and adapts to debate complexity.

---

## 4. Ratified Parameter Matrix

| Parameter | Identifier | Value | Justification |
| :--- | :--- | :--- | :--- |
| **Fallacy Penalty** | $C_f$ | `-3` | Negative expected utility under $p \approx 0.5$ worst-case detection noise. |
| **Merit Weight** | $M_v$ | `+1` | Unit reward baseline for verified evidence and point-by-point refutation. |
| **Minimum Reading Time** | $T_{\text{min}}$ | `120s` | Physiological human reading ceiling for 800-word payloads. |
| **Learning Rate** | $\eta$ | `0.15` | Smooth multiplicative calibration damping noise. |
| **Quarantine Cutoff** | $\tau$ | `Dynamic (\mu - 2\sigma)` | Adapts dynamically to debate dialectical difficulty. |
| **URL Regex Pattern** | `URL_GATE` | Strict Exclusion | Excludes trailing punctuation: `(?:\/[^\s.,;:!?)]*)?`. |
