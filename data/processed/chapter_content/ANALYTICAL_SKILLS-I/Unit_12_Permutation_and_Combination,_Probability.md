# Unit 12 Permutation and Combination, Probability

## Summary

| Concept                         | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| **IPv4 Addressing**           | 32-bit addresses classified into Classes A, B, C with limited availability. |
| **Inclusion-Exclusion**       | Used to count elements in union sets by adding individual counts and subtracting overlaps. |
| **Tree Diagrams**            | Visual tool to represent sequences of choices and calculate outcomes.          |
| **Permutations**              | Arrangements of elements where order matters. Formula: $P(n, r)$             |
| **Combinations**              | Selections of elements where order does not matter. Not covered in detail here. |
| Topic               | Description |
|---------------------|-------------|
| Counting Principles | Rules like product, sum, subtraction, and division |
| Permutations        | Arrangements of objects |
| Combinations       | Selections of objects |
| Probability         | Measuring chances of events |
| Bayes’ Theorem      | Updating probabilities with new information |
- Understand permutations vs combinations.
- Use constraints wisely in calculations.
- Know how to calculate sample spaces and probabilities.
- Be able to apply conditional probability and Bayes' Theorem.

---

## Keywords

- | Term | Description |
- |------|-------------|
- | Product Rule | Principle for calculating total outcomes in sequential processes |
- | Sum Rule | Principle for adding outcomes from mutually exclusive cases |
- | Tree Diagrams | Visual representation of multi-step processes |
- | Permutations | Ordered arrangements of objects |
- | Combinations | Unordered selections of objects |
- | Probability | Measure of the likelihood of an event |
- | Bayes’ Rule | Formula for updating probabilities based on new evidence |
- Basics of counting
- Product rule
- Sum rule
- Subtraction rule
- Tree diagram
- Division rule
- Combination
- Deck of cards
- Pigeonhole principle

---

## Core Concepts & Topics

## Unit 12 Permutation and Combination, Probability

## Core Concepts & Topics

```markdown
## Unit 12: Permutation and Combination, Probability

## Overview
This unit introduces fundamental principles of counting and probability. Key topics include the product and sum rules, tree diagrams, permutations, combinations, and Bayes' Rule. These concepts form the basis for solving complex counting and probabilistic problems in mathematics and computer science.

## Objectives
After completing this unit, learners should be able to:

- Understand the basics of counting.
- Apply the **Product Rule** and **Sum Rule** in various counting scenarios.
- Use **Tree Diagrams** to represent and solve counting problems.
- Differentiate between **Permutations** and **Combinations**.
- Calculate probabilities using **Bayes’ Rule**.
- Solve real-world problems involving counting and probability.

## Additional Notes

## Key Concepts Recap
- **IPv4 Limitation:** Only about 3.7 billion addresses available due to class limitations.
- **Bit String Problems:** Use inclusion-exclusion and tree diagrams for complex counting scenarios.
- **Permutations:** Order-sensitive arrangements with formulas derived from the product rule.

This guide provides a structured overview of key concepts in combinatorics and their real-world applications, particularly focusing on IPv4 addressing, inclusion-exclusion, tree diagrams, and permutations. Each section builds upon foundational principles to support deeper understanding and problem-solving skills.

## **Study Guide: Permutation and Combination**

## 📌 Table of Contents

| Topic | Description |
|------|-------------|
| Permutations | Ordered arrangements of elements |
| Combinations | Unordered selections of elements |
| Basic Principles | Counting principles like multiplication and addition |
| Probability | Concept and calculation of chances |
| Types of Events | Definitions and classifications |
| Algebra of Events | Set operations related to events |

## 🔢 1. Permutations

## 📌 Definition
Permutations refer to the number of **ordered** selections of $ r $ elements from a set of $ n $ elements. 

$$
P(n, r) = \frac{n!}{(n - r)!}
$$

## 📌 Key Points
- $ P(n, 0) = 1 $
- $ P(n, n) = n! $
- Example: $ P(100, 3) = 100 \cdot 99 \cdot 98 = 970{,}200 $

## ✅ Examples
- **Example 4**: Ways to select 3 prize winners from 100 contestants → $ P(100, 3) $
- **Example 5**: Medals awarded to top 3 runners from 8 → $ P(8, 3) $
- **Example 6**: Saleswoman's tour starting from fixed city → $ 7! $

## 🧮 2. Combinations

## 📌 Definition
Combinations refer to the number of **unordered** selections of $ r $ elements from a set of $ n $ elements.

$$
C(n, r) = \binom{n}{r} = \frac{n!}{r!(n - r)!}
$$

## 📌 Key Points
- $ C(n, r) = C(n, n - r) $
- If $ r > n $, $ C(n, r) = 0 $
- Example: $ C(4, 3) = 4 $

## ✅ Examples
- **Example 8**: Committees of 3 from 4 students → $ C(4, 3) $
- **Example 7**: Permutations containing "ABC" → Treat "ABC" as a block

## 📜 3. Basic Principles of Counting

| Principle | Description | Formula |
|----------|-------------|---------|
| Multiplication | If one task can be done in $ m $ ways and another in $ n $, then combined tasks can be done in $ m \times n $ ways | $ m \times n $ |
| Addition | If one task can be done in $ m $ ways and another in $ n $, and they are mutually exclusive, then total ways = $ m + n $ | $ m + n $ |

## 📈 4. Probability

## 📌 Definition
Probability measures the likelihood of an event occurring.

$$
\text{Probability of Event } A = \frac{\text{Number of Favorable Outcomes}}{\text{Total Number of Outcomes}}
$$

## 📌 Terms
- **Random Experiment**: Outcome cannot be predicted with certainty
- **Sample Space ($ S $)**: Set of all possible outcomes
- **Event**: Subset of the sample space

## ✅ Examples
- **Coin Toss**: $ S = \{H, T\} $
- **Die Roll**: $ S = \{1, 2, 3, 4, 5, 6\} $
- **Two Dice**: $ S = \{(1,1), (1,2), ..., (6,6)\} $

## 🧩 5. Types of Events

| Type | Description | Example |
|------|-------------|---------|
| **Simple Event** | Single outcome | Rolling a 3 on a die |
| **Compound Event** | Multiple outcomes | Getting a sum of 7 with two dice |
| **Equally Likely Events** | Equal probability | Rolling a fair die |
| **Exhaustive Events** | Covers all outcomes | Coin toss outcomes (Head or Tail) |
| **Mutually Exclusive Events** | Cannot happen together | Rolling a 3 and a 4 on a single die |
| **Independent Events** | One does not affect the other | Two coin flips |
| **Dependent Events** | One affects the other | Drawing cards without replacement |

## ⚖️ 6. Algebra of Events

Let $ A $ and $ B $ be two events:

| Notation | Meaning | Description |
|---------|--------|-------------|
| $ A \cup B $ | Union | Either $ A $ or $ B $ or both |
| $ A \cap B $ | Intersection | Both $ A $ and $ B $ |
| $ A^c $ | Complement | Not $ A $ |
| $ A \setminus B $ | Difference | $ A $ but not $ B $ |
| $ A \oplus B $ | Symmetric Difference | $ A $ or $ B $, but not both |

## 🧠 Summary Table

| Concept | Formula | Notes |
|--------|--------|-------|
| Permutation | $ P(n, r) = \frac{n!}{(n-r)!} $ | Order matters |
| Combination | $ C(n, r) = \frac{n!}{r!(n-r)!} $ | Order doesn't matter |
| Probability | $ P(A) = \frac{|A|}{|S|} $ | Ratio of favorable over total |
| Independent Events | $ P(A \cap B) = P(A) \cdot P(B) $ | No effect on each other |
| Dependent Events | $ P(A \cap B) = P(A) \cdot P(B|A) $ | One affects the other |

## 📌 Diagram: Venn Diagram of Events

```text
       A
     /   \
    /     \
   /_______\
  |        |
  |  A∩B   |
  |        |
  \_______/
   B
```

## ✅ Final Notes

- Always check whether the problem requires **order** (permutations) or **not** (combinations).
- Understand the difference between **mutually exclusive**, **independent**, and **dependent** events.
- Use the **multiplication rule** when making multiple choices sequentially.
- Use the **addition rule** when combining disjoint events.

--- 

Let me know if you'd like a printable version or additional exercises!

## 📌 Topic 1: Mutually Exclusive Events

## 🔷 Definition
Two events are **mutually exclusive** if they cannot both occur at the same time in a single trial of an experiment.

## ✅ Key Points
| Term | Description |
|------|-------------|
| Mutual Exclusivity | If $ A \cap B = \emptyset $, then A and B are mutually exclusive |
| Example 1 | Coin toss: "Head" and "Tail" are mutually exclusive |
| Example 2 | Die roll: Rolling a 1 and rolling a 2 are mutually exclusive |

## 📌 Illustrations

## ❖ Illustration 10
> **Experiment**: Toss a coin  
> **Outcomes**: Head (H), Tail (T)  
> **Observation**: H and T cannot occur together ⇒ Mutually Exclusive Events

## ❖ Illustration 11
> **Experiment 1**: Roll a die  
> **Event A**: Number < 3 → {1, 2}  
> **Event B**: Number > 4 → {5, 6}  
> **Intersection**: $ A \cap B = \emptyset $ ⇒ Mutually Exclusive Events  

> **Experiment 2**: Draw a card from a standard deck  
> **Event A**: Card is Black → {Spades, Clubs}  
> **Event B**: Card is Ace → {Ace of Spades, Ace of Hearts, Ace of Diamonds, Ace of Clubs}  
> **Intersection**: $ A \cap B \neq \emptyset $ ⇒ Not Mutually Exclusive Events

## 📌 Topic 2: Mutually Exclusive and Exhaustive Events

## 🔷 Definition
Events $ A_1, A_2, \ldots, A_n $ are **mutually exclusive and exhaustive** if:

- They cover the entire sample space $ S $
- No two events occur at the same time

$$
\bigcup_{i=1}^n A_i = S \quad \text{and} \quad A_i \cap A_j = \emptyset \text{ for } i \neq j
$$

## 📌 Examples

## ❖ Example 1
> **Experiment**: Roll a die  
> **Event A**: Even number → {2, 4, 6}  
> **Event B**: Odd number → {1, 3, 5}  
> **Union**: $ A \cup B = \{1, 2, 3, 4, 5, 6\} = S $  
> **Intersection**: $ A \cap B = \emptyset $  
> **Conclusion**: Mutually Exclusive and Exhaustive Events

## 📌 Topic 3: Probability

## 🔷 Definitions

| Type | Description |
|------|-------------|
| **Mathematical (Priori)** | Based on logical reasoning, e.g., fair coin or die |
| **Statistical (Empirical)** | Based on experimental data or frequency of outcomes |

## 🔹 Formula
$$
P(A) = \frac{\text{Number of favorable outcomes}}{\text{Total number of outcomes}}
$$

## 📌 Illustrations

## ❖ Illustration 13
> **Experiment**: Toss a coin  
> **Sample Space**: {H, T}  
> **Probability of Tail**: $ P(T) = \frac{1}{2} $

## ❖ Illustration 14
> **Experiment**: Roll a die  
> **Favorable Outcomes for Even Numbers**: {2, 4, 6}  
> **Total Outcomes**: 6  
> **Probability**: $ P(\text{Even}) = \frac{3}{6} = \frac{1}{2} $

## ❖ Illustration 15
> **Experiment**: Draw a card from a deck  
> **Favorable Outcomes for King**: 4  
> **Total Outcomes**: 52  
> **Probability**: $ P(\text{King}) = \frac{4}{52} = \frac{1}{13} $

## 📌 Topic 4: Odds

## 🔷 Odds in Favor and Against

| Term | Formula |
|------|--------|
| **Odds in Favor** | $ \frac{m}{n} $ where $ m $ = favorable outcomes, $ n $ = unfavorable outcomes |
| **Odds Against** | $ \frac{n}{m} $ |

## 📌 Illustrations

## ❖ Illustration 16
> **Experiment**: Roll a die  
> **Favorable Outcome for 3**: 1  
> **Unfavorable Outcomes**: 5  
> **Odds in Favor**: $ \frac{1}{5} $  
> **Odds Against**: $ \frac{5}{1} $

## 📌 Topic 5: Fundamental Theorems of Probability

| Theorem | Description |
|--------|-------------|
| **Theorem 1** | $ P(E) \geq 0 $, $ P(\emptyset) = 0 $, $ P(S) = 1 $ |
| **Theorem 2** | $ P(E \cap F) = 0 $ if mutually exclusive, $ P(E \cup F) = P(E) + P(F) $ |
| **Theorem 3** | If $ E $ and $ F $ are exhaustive and mutually exclusive, $ P(E) + P(F) = 1 $ |
| **Theorem 4** | Complement: $ P(E) + P(\bar{E}) = 1 $ |
| **Theorem 5** | $ P(E - F) = P(E) - P(E \cap F) $ |
| **Theorem 6** | Addition Theorem: $ P(E \cup F) = P(E) + P(F) - P(E \cap F) $ |
| **Theorem 7** | If $ A \subseteq B $, then $ P(A) \leq P(B) $ |
| **Theorem 9** | For three events: $ P(A \cup B \cup C) = P(A) + P(B) + P(C) - P(A \cap B) - P(B \cap C) - P(A \cap C) + P(A \cap B \cap C) $ |

## 📌 Topic 6: Independent Events

## 🔷 Definition
Two events $ A $ and $ B $ are **independent** if the occurrence of one does not affect the probability of the other.

$$
P(A \cap B) = P(A) \cdot P(B)
$$

## 📌 Illustrations

## ❖ Illustration 23
> **Experiment**: Throw two dice  
> **Event A**: Odd number on first die → {1, 3, 5}  
> **Event B**: Multiple of 3 on second die → {3, 6}  
> **Independence Check**: $ P(A) \cdot P(B) = \frac{1}{2} \cdot \frac{1}{3} = \frac{1}{6} $  
> **Result**: Independent Events

## 📌 Topic 7: Bayes' Rule

## 🔷 Formula
$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)}
$$

This allows us to calculate conditional probability using joint probability and marginal probability.

## 📌 Example
> **Scenario**: Machine 1 produces 30% of all parts, Machine 2 produces 70%.  
> **Defect Rate**: Machine 1 has 2% defect rate, Machine 2 has 3% defect rate.  
> **Question**: Given a defective part, what's the probability it came from Machine 1?

## 📌 Summary Table

| Concept | Description |
|--------|-------------|
| **Mutual Exclusivity** | Events cannot occur at the same time |
| **Exhaustiveness** | Events cover the entire sample space |
| **Probability** | Ratio of favorable outcomes to total outcomes |
| **Odds** | Ratio of favorable to unfavorable outcomes |
| **Independent Events** | Occurrence of one does not affect another |
| **Bayes' Rule** | Calculates conditional probability |

## 📌 Notes
- Use **mathematical definitions** when theoretical knowledge is needed.
- Use **empirical methods** when real-world data is available.
- Always verify whether events are **mutually exclusive**, **exhaustive**, or **independent** before applying formulas.

--- 

Let me know if you need this content formatted into PDF or additional illustrations!

## Self-Assessment Answers

1. A  
2. A  
3. B  
4. A  
5. C  
6. A  
7. D  
8. B  
9. C  
10. D  
11. B  
12. B  
13. C  
14. B  
15. B  
16. B  
17. A  
18. D  
19. A  
20. A  
21. D  
22. C  
23. C  
24. B  
25. B  
26. B  
27. A  
28. B  
29. A  
30. B  

--- 

This study guide provides a clear structure for understanding permutation, combination, and probability concepts. Each section builds upon the previous one, ensuring a solid foundation in combinatorics and statistical reasoning.

## Review & Practice Questions

1. Explain the difference between the product rule and the sum rule.
2. How can tree diagrams assist in solving complex counting problems?
3. Provide an example of a permutation and explain why it is relevant.
4. Describe Bayes’ Rule and provide an application scenario.
5. Why is it important to consider restrictions like "at least one digit" in password calculations?
1. Calculate the number of ways to select 5 people out of 10.
2. Find the probability of rolling a sum of 7 with two dice.
3. Determine if two events are independent.
4. Solve using Bayes' Theorem with given data.

Let me know if you need further clarification on any specific concept!

---
