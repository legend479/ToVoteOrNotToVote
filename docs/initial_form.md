## 🗳️ **Survey Design: *To Vote or Not To Vote — A 3-Minute Reflection on Civic Choices***

**Intro Text:**
“This short survey explores how people decide whether or not to vote. It’s not a test — just your honest thoughts. There are no right or wrong answers, only your perspective.”

---

### **Q1. Emotional Priming / Contextual Anchor**

> “When you hear the word *election*, which feeling comes closest?”

* Excitement
* Curiosity
* Indifference
* Frustration
* Distrust

🧭 **Parameter:** Contextual affective baseline → influences all subsequent perception weighting.
🎯 **Model mapping:** Contextual affect control variable

---

### **Q2. Voting Frequency**

> “How often do you vote when you are eligible?”

* Always
* Often
* Sometimes
* Rarely
* Never

🧭 **Parameter:** Behavioral anchor
🎯 **Model mapping:** Dependent variable (vote / not vote)

---

### **Q3. Effort–Benefit Trade-off**

> “If voting took you an extra 20 minutes of travel, would you still do it?”

* Definitely yes
* Probably yes
* Not sure
* Probably not
* Definitely not

🧭 **Parameter:** Perceived logistical cost vs. civic benefit
🎯 **Model mapping:** Effort–reward elasticity

---

### **Q4. Perceived Impact (Instrumental Utility)**

> “Imagine your preferred candidate trailing by a few hundred votes. Would you feel your single vote matters?”

* Yes, definitely
* Maybe somewhat
* Not really
* Not at all

🧭 **Parameter:** Perceived efficacy / marginal impact
🎯 **Model mapping:** Instrumental utility

---

### **Q5. Civic Identity and Moral Duty**

> “To what extent do you agree: *Voting is part of being a responsible citizen.*”

* Strongly agree
* Agree
* Neutral
* Disagree
* Strongly disagree

🧭 **Parameter:** Civic identity utility
🎯 **Model mapping:** Moral utility

---

### **Q6. Emotional Reward (Psychological Utility)**

> “After voting, I usually feel…”

* Proud and satisfied
* Relieved or calm
* Neutral
* Like it didn’t matter
* Regretful or skeptical

🧭 **Parameter:** Intrinsic emotional payoff
🎯 **Model mapping:** Psychological utility

---

### **Q7. Trust and Fairness (Institutional Cost Modifier)**

> “How confident are you that votes are counted fairly in your area?”

* Very confident
* Somewhat confident
* Unsure
* Somewhat doubtful
* Very doubtful

🧭 **Parameter:** Institutional trust / perceived fairness
🎯 **Model mapping:** Systemic confidence modifier

---

### **Q8. Social Influence**

> “Most people I know usually vote.”

* Strongly agree
* Agree
* Neutral
* Disagree
* Strongly disagree

🧭 **Parameter:** Social conformity / peer norm utility
🎯 **Model mapping:** Social pressure predictor

---

### **Q9. Perceived Information Load (Cognitive Cost)**

> “Before an election, I find it hard to decide whom to vote for because I lack clear information.”

* Strongly agree
* Agree
* Neutral
* Disagree
* Strongly disagree

🧭 **Parameter:** Information cost / decision fatigue
🎯 **Model mapping:** Cognitive cost

---

### **Q10. Disillusionment (Moral Cost)**

> “Sometimes I feel that all politicians are the same, so voting makes no real difference.”

* Strongly agree
* Agree
* Neutral
* Disagree
* Strongly disagree

🧭 **Parameter:** Cynicism cost / perceived futility
🎯 **Model mapping:** Moral disutility

---

### **Q11. Counterfactual Trade-off (Choice Elasticity)**

> “If voting could be done securely online in 2 minutes, would you be more likely to vote?”

* Definitely yes
* Probably yes
* Not sure
* Probably not
* Definitely not

🧭 **Parameter:** Sensitivity of participation to reduced cost
🎯 **Model mapping:** Effort elasticity

---

### **🆕 Q12. Electoral Competitiveness Perception (Pivotal Utility)**

> “If you knew the upcoming election in your area was expected to be very close, would that make you more likely to vote?”

* Definitely yes
* Probably yes
* Not sure
* Probably not
* Definitely not

🧭 **Parameter:** Competitiveness sensitivity / pivotal motivation
🎯 **Model mapping:** Overconfidence–competitiveness interaction term

---

### **🆕 Q13. Incentive Preference — Monetary or Recognition-Based Nudge**

> “Which of the following would make you more likely to vote (choose the most motivating)?”

* A chance to win a small monetary reward (e.g., local prize lottery for voters)
* A ‘Voter ID badge’ or digital certificate recognizing participation
* Social media acknowledgment or a ‘Voter’ badge for your profile
* Nothing — I’d vote anyway
* None of these would make a difference

🧭 **Parameter:** Incentive salience (extrinsic vs. identity-based motivation)
🎯 **Model mapping:** Nudge-type preference elasticity (Monetary vs. Social Identity utility)

---

### **Q14. Reflective Prompt (Qualitative Insight)**

> “In your own words, what one change would make you more likely to vote?”
> *(Short text response)*

🧭 **Parameter:** Free-form capture of unmodeled latent variables (affective, contextual, systemic)
🎯 **Model mapping:** Qualitative coding for emergent motivational drivers

---

## **Parameter–Question Mapping Table**

| **Model Component**    | **Sub-variable**                         | **Question No.** | **Type**        | **Variable Use**         |
| ---------------------- | ---------------------------------------- | ---------------- | --------------- | ------------------------ |
| **Dependent Variable** | Voting frequency                         | Q2               | Categorical     | Logistic target          |
| **Utility (Positive)** | Civic duty / identity                    | Q5               | Likert          | Predictor                |
|                        | Emotional satisfaction                   | Q6               | Ordinal         | Predictor                |
|                        | Perceived efficacy                       | Q4               | Ordinal         | Predictor                |
|                        | Competitiveness / pivotal motivation     | Q12              | Ordinal         | Predictor                |
| **Utility (Negative)** | Effort/time cost                         | Q3               | Ordinal         | Predictor                |
|                        | Cognitive/informational cost             | Q9               | Likert          | Predictor                |
|                        | Disillusionment                          | Q10              | Likert          | Predictor                |
| **Contextual Factors** | Trust in system                          | Q7               | Likert          | Modifier                 |
|                        | Peer/social norm                         | Q8               | Likert          | Modifier                 |
|                        | Emotional baseline toward elections      | Q1               | Categorical     | Interaction term         |
|                        | Sensitivity to reduced cost (elasticity) | Q11              | Ordinal         | Behavioral elasticity    |
| **Nudge Preference**   | Monetary vs. social identity incentive   | Q13              | Multiple choice | Nudge design calibration |
| **Qualitative Factor** | Emergent explanatory themes              | Q14              | Text            | Thematic coding          |

---


