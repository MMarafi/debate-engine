# RFC 001: Game-Theoretic Incentive Design & Adversarial Resilience
*Status: RATIFIED / PRODUCTION-READY SPECIFICATION (v3.0)*  
*Target Engine: Debate-Engine Core v2.0*  

---

## 1. Design Philosophy & Adversarial Threat Model

The engine implements an **Incentive-Compatible Mechanism Design** resilient against strategic, sybil, and automated collusion. The architecture assumes an adversarial environment where participants utilize large language models (LLMs), automated latency sleeps, and coordination during off-peak matchmaking hours. Truthfulness, empirical sourcing, dialectical integrity, and uncorrupted auditing must remain the **strictly dominant strategy** across all rational action profiles.

---

## 2. Dual-Ledger Debater Architecture & Nash Equilibrium Bounds

| Evaluation Ledger | Skill Rating (`Elo Rating`) | Behavioral Integrity (`Reputation Score`) |
| :--- | :--- | :--- |
| **Domain Scope** | Measures dialectical skill and argument potency | Measures empirical honesty and procedural compliance |
| **Mathematical Nature** | Zero-Sum Invariant ($\Delta\text{PRO} + \Delta\text{CON} = 0$) | Non-Zero-Sum state metric ($R \in [0, 100.0]$) |
| **Matchmaking Impact** | Pairs competitors within equivalent skill tiers | Acts as an eligibility gatekeeper (`Gatekeeper`) |
| **Fallacy Deterrence** | Direct round point deduction ($C_f = -3$) | Severe, persistent deduction ($\Delta R = -10.0$) |

---

### A. Strict Equilibrium Bound on Reputation Sensitivity ($\gamma$)
The debater utility function balances expected rating progression against behavioral integrity loss:

$$U_{\text{debater}} = \mathbb{E}[\Delta\text{Elo}] + \gamma \cdot \mathbb{E}[\Delta R] - C(\text{Dropped}) - C(\text{MissingEvidence})$$

To eliminate the incentive for a debater to deploy a deceptive, high-impact fallacy to secure an Elo win, the engine enforces the **Strict Anti-Defection Equilibrium Condition**:

$$\gamma \ge \frac{2 \cdot K_{\max}}{\vert{}\Delta R_{\text{penalty}}\vert{}}$$

* Under standard engine parameters ($K_{\max} = 32$, $\vert{}\Delta R_{\text{penalty}}\vert{} = 10.0$):
  $$\gamma \ge \frac{64}{10} = 6.4$$
* **Equilibrium Invariant:** Even if a fallacy guarantees a victory ($+K_{\max}$), the expected net utility is strictly negative ($\Delta U \le 32 - 6.4 \times 10 = -32 < 0$), destroying the economic viability of strategic deception.

---

### B. Anti-Abandonment Bound
To prevent debaters from timing out to shield their reputation when caught in fallacies:

$$\vert{}\Delta R_{\text{timeout}}\vert{} > \vert{}\Delta R_{\text{penalty}}\vert{}$$

* **Timeout Penalty:** Forfeit loss committed to the Elo ledger PLUS an immediate deterministic deduction of **`-15.0` reputation points**.
* **Equilibrium Property:** Engaging and concluding a round strictly dominates intentional abandonment.

---

### C. Sybil-Resistant Rehabilitation & Opponent Entropy
To defeat collusive reputation farming via automated text generators (LLMs) during low-traffic hours:

1. **Unique Opponent Entropy Filter:**
   * Clean-round recovery credit ($+0.5$ reputation) requires pairwise interaction entropy:
   $$\text{Pairwise Match Interval} \ge 30\text{ Days}$$
   * If debater PRO and CON have matched within the rolling 30-day window, $\Delta R_{\text{clean}} = 0.0$.
2. **Textual Complexity Gate:**
   * In addition to length ($L \ge 200$ words), the submission must pass a deterministic compression-ratio entropy floor ($H_{\text{text}} \ge 0.45$ via standard library `zlib`) to block degenerate token stuffing.
3. **Cooling-Off Quarantine:**
   * Accounts falling below $R_t < 50.0$ face an unbypassable **14-day write-lock** ($\Delta t = 14\text{d}$) followed by mandatory canary-evaluated audit benchmarks.

---

## 3. Judge Nash Equilibrium & Micro-Quorum Mechanism Design

### A. Correlated Agreement (CA) Mechanism for Micro-Quorums ($3 \le N \le 5$)
Given that Robust Bayesian Truth Serum (RBTS) exhibits high discretization noise when $N \in [3, 5]$, the engine replaces RBTS with the **Small-Quorum Correlated Agreement (CA) Scoring Rule**.

For each criterion $k$, each judge $j$ submits an endorsement $x_{j, k} \in \{0, 1\}$. Evaluator alignment is calculated pairwise against peer responses without self-influence:

1. **Leave-One-Out Consensus Mean:**
   $$\bar{x}_{-j, k} = \frac{1}{N - 1} \sum_{i \ne j} x_{i, k}$$

2. **Strictly Proper Quadratic Alignment Score:**
   $$\text{Score}_{\text{align}, j} = 1 - \frac{1}{K} \sum_{k=1}^K (x_{j, k} - \bar{x}_{-j, k})^2$$

3. **Multiplicative Exponential Weight Update:**
   $$\text{Penalty}_{\text{dev}, j} = 1 - \text{Score}_{\text{align}, j}$$

   $$W_j^{(t+1)} = W_j^{(t)} \cdot \exp\left(-\eta \cdot \text{Penalty}_{\text{dev}, j}\right)$$

* Eliminates geometric mean division-by-zero singularities and artificial Laplace distortion ($\epsilon$).
* Truthful reporting of observable dialectical facts strictly maximizes alignment payoff against independent peers.

---

### B. Fault-Tolerant Weighted Canary Audit (Supreme Quorum)
To dismantle the 1-of-3 canary veto vulnerability, slashing thresholds are parameterized over **Canary Weight Aggregation**:

* A pseudo-random sampling gate flags $10\%$ of finished quorums for blind canary auditing by 3 benchmark evaluators ($W_c \ge 2.0$).
* Let $W_{\text{agree}}$ be the cumulative weight of canary judges confirming an evaluative infraction by the peer quorum:

$$\text{Canary Agreement Ratio} = \frac{\sum_{c=1}^3 W_c \cdot \mathbf{I}(\text{Violation}_c)}{\sum_{c=1}^3 W_c}$$

* **Tiered Slashing Schedule:**
  $$\text{Slashing Action} =    \begin{cases}    \text{No Penalty}, & \text{if Ratio} < 0.67 \quad (\text{Dissent / Ambiguous}) \\   W_j \leftarrow W_j \times 0.60 \quad (\text{Partial Slashing } 40\%), & \text{if } 0.67 \le \text{Ratio} < 1.00 \quad (\text{Weighted Supermajority}) \\   W_j \leftarrow W_j \times 0.20 \quad (\text{Full Slashing } 80\% + \text{Quarantine}), & \text{if Ratio} = 1.00 \quad (\text{Unanimous Breach})   \end{cases}$$

* **Security Invariant:** A single compromised or errant canary judge cannot block slashing against a demonstrably collusive quorum.

---

### C. Active Cognitive Proof of Effort (Anti-AFK & Evidence Sanitization)

1. **Semantic Anchor Challenge:**
   * Judges must map the speaker's refutation to the exact argument premise from 3 deterministically generated candidate anchors.
   * **Failure Rule:** Incorrect anchor mapping silently aborts ballot persistence (`ProofOfEffort = 0`). The 120-second dwell time serves only as an auxiliary bounds check.

2. **Evidence Path Validation (Anti-Ghost URL Gate):**
   * To prevent hollow domain stuffing (`https://google.com` or `https://wikipedia.org`), URLs must include specific resource paths:
   ```python
   # Requires protocol, valid domain, non-empty path, and excludes trailing punctuation
   URL_REGEX = r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s.,;:!?)]+"
   ```
   * Submissions citing generic root domains without content paths fail write-time validation.

---

## 4. Ratified Parameter Matrix (v3.0 Production Standard)

| Parameter | Identifier | Value | Justification |
| :--- | :--- | :--- | :--- |
| **Reputation Sensitivity Bound** | $\gamma$ | **`6.4`** | Enforces `γ ≥ 2·K_max / |ΔR_penalty|`; blocks Elo/Reputation arbitrage. |
| **Fallacy Round Deduction** | $C_f$ | `-3` | Ensures negative round score expected payoff. |
| **Fallacy Reputation Penalty** | $\Delta R_{\text{penalty}}$ | `-10.0` | Direct subtraction from eligibility ledger. |
| **Timeout / Forfeit Penalty** | $\Delta R_{\text{timeout}}$ | `-15.0` | Strictly dominates strategic abandonment. |
| **Entropy Opponent Window** | $\Delta t_{\text{match}}$ | **`30 Days`** | Blocks off-peak pairwise collusion and sybil farming. |
| **Textual Entropy Floor** | $H_{\text{text}}$ | **`0.45`** | Bounded compression ratio blocking repetitive token stuffing. |
| **Quarantine Cooldown Lock** | $\Delta t_{\text{lock}}$ | `14 Days` | Eliminates economic returns on automated bot recycling. |
| **Canary Slashing Supermajority** | $\theta_{\text{canary}}$ | **`0.67 (2/3 Weighted)`** | Eliminates single-auditor veto vulnerability. |
| **Primary Proof of Effort** | `PoE_Primary` | **Semantic Anchor Binding** | Requires cognitive reading; immune to AFK sleep scripts. |
| **Evidence Path Invariant** | `URL_REGEX` | Non-empty path required | Prevents root-domain ghost citations. |
| **Dynamic Quarantine Floor** | $\tau$ | `μ_W - 2σ_W` | Isolates statistically aberrant evaluators adaptively. |


```
