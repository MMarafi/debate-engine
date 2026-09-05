# How It Works: User & Platform Guide (HOW_IT_WORKS.md)

Welcome to the deterministic debate platform. This platform is governed strictly by mathematical rules, game theory, and zero-bias automation. There are no human moderators, no subjective appeals, and no hidden algorithms.

---

## 1. The Debater Experience

### Step 1: Starting a Debate
* **Creating a Match:** You choose a proposition topic and state your position: Affirmative (`PRO`) or Negative (`CON`).
* **Matchmaking:** The system pairs you with an opponent of similar skill (Elo rating).
* **The Countdown Begins:** As soon as your opponent accepts, Round 1 opens immediately for the `PRO` debater.

### Step 2: Writing & Submitting Your Round
Every round you submit must pass three mandatory automated gates:
1. **The Clock (48 Hours):** You have exactly 48 hours to post your argument. If the timer hits zero, the system registers an immediate **forfeit** and awards the win to your opponent.
2. **The Concision Gate (Max 800 Words):** Your text cannot exceed 800 words. Bullet points and punctuation do not count against your limit, but excessive text will be rejected immediately.
3. **The Evidence Gate (Min 1 URL):** Pure assertions are not allowed. You must include at least one valid external source link (`https://...`).

> **System Feedback:** If your round violates word limits or lacks evidence, the system rejects the submission with a clear error code. **Your 48-hour clock does not pause while you fix it.**

### Step 3: Match Progression
A complete debate consists of **6 strictly alternating turns** (3 for PRO, 3 for CON):
* **Round 1:** PRO Opening Statement
* **Round 2:** CON Rebuttal & Cross-Argument
* **Round 3:** PRO Defense & Deepening
* **Round 4:** CON Defense & Counter-Refutation
* **Round 5:** PRO Final Summary
* **Round 6:** CON Closing Defense

---

## 2. The Judge Experience

### Step 1: Blind Evaluation & The Attention Test
* **No Bias:** Judges evaluate rounds anonymously without knowing debater identities or current scores.
* **The Proof of Reading (Attention Check):** Before your ballot is accepted, the system will prompt:  
  *"Enter word #K from the debater's text."*  
  This confirms you read the submission. If you fail this check, your ballot is discarded silently.

### Step 2: Silent Balloting
Judges evaluate three positive criteria and two logical fallacy penalties:
* **Positive Merits (+1 point each):**
  * Better Empirical Evidence
  * Better Refutation Quality
  * Stronger Logical Consistency
* **Fallacy Deductions (-1 point each):**
  * *Ad Hominem* (Personal attacks against the opponent)
  * *Straw Man* (Distorting or misrepresenting the opponent's argument)

### Step 3: The 24-Hour Quorum
* A round requires **3 to 5 independent judges** (always an odd number to prevent mathematical ties).
* Judges have **24 hours** to complete the audit.
* If fewer than 3 valid ballots are collected within 24 hours, the match is marked as **VOID** to protect debater ratings from inadequate judging.

---

## 3. How the Match Ends & Ratings Update

### Final Score Determination
When all 6 rounds are completed, the system calculates the algebraic sum of all verified ballots:
* **Winner:** The side with the higher algebraic score across all rounds.
* **Tie:** If points are perfectly equal, the match is recorded as a Draw.

### The Zero-Sum Rating (Elo) Guarantee
* Every point gained by the winner is exactly deducted from the loser ($\Delta_{\text{PRO}} + \Delta_{\text{CON}} = 0$).
* The system uses strict symmetric rounding: no rating points are created or destroyed.
* If a match is canceled due to judge timeout (`VOID`), **no Elo ratings change**.
