# Unit 01 Number System

## Summary

This unit provides a foundational understanding of number systems, emphasizing the classification of numbers, arithmetic operations, and problem-solving techniques involving factors and multiples. Key topics include:

- **Types of Numbers**: Natural, Whole, Integers, Even, Odd, Prime, Composite, etc.
- **Arithmetic Operations**: Multiplication, Division, with focus on shortcuts and properties.
- **Divisibility Rules**: Various tests to check divisibility of numbers.
- **Square Numbers**: Understanding squares and their significance.
- **HCF & LCM**: Different methods to compute Highest Common Factor and Least Common Multiple using prime factorization and other algorithms.

---

## Keywords

- Natural Numbers
- Whole Numbers
- Integers
- Even Numbers
- Odd Numbers
- Prime Numbers
- Composite Numbers
- Divisibility
- HCF
- LCM
- Distributive Law

---

## Core Concepts & Topics

## Unit 01 Number System

## Core Concepts & Topics

## Topic 1: Classification of Numbers

## 1.1 Odd and Even Numbers
| Type         | Definition                                                                 | Examples                     |
|--------------|-----------------------------------------------------------------------------|------------------------------|
| **Even**     | Numbers divisible by 2                                                      | 2, 6, 8, 10                  |
| **Odd**      | Numbers not divisible by 2                                                  | 1, 3, 5, 7                   |

> Note: All even numbers end in 0, 2, 4, 6, or 8.

## 1.2 Prime Numbers
| Property             | Description                                                                 | Examples                         |
|----------------------|-----------------------------------------------------------------------------|----------------------------------|
| **Definition**       | A number > 1 with exactly two distinct factors: 1 and itself               | 2, 3, 5, 7, 11, 13, ...         |
| **Up to 100**        | 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 |
| **Key Notes**        | 1 is neither prime nor composite                                           |                                  |
|                      | 2 is the only even prime number                                             |                                  |
|                      | There are 25 primes between 1 and 100                                      |                                  |

## 1.3 Composite Numbers
| Property             | Description                                                                 | Examples                     |
|----------------------|-----------------------------------------------------------------------------|------------------------------|
| **Definition**       | Numbers > 1 that are not prime                                              | 4, 6, 8, 9, 10, 12           |
| **Key Notes**        | All composite numbers have more than two factors                            |                              |

## Topic 2: Co-Primes and HCF
| Term    | Definition                                                                 | Example                    |
|---------|-----------------------------------------------------------------------------|----------------------------|
| **Co-Primes** | Two numbers whose Highest Common Factor (HCF) is 1                        | (2, 3), (4, 5), (7, 9)     |

> Note: Co-prime numbers do not have to be prime themselves.

## Topic 3: Rational Numbers
| Term          | Definition                                                                 | Examples                         |
|---------------|-----------------------------------------------------------------------------|----------------------------------|
| **Rational Number** | A number that can be expressed as $ \frac{p}{q} $ where $ p, q \in \mathbb{Z}, q

## 1. Multiplication Using Distributive Law

## 1.1 Key Concepts

The distributive law allows us to break down multiplication problems into simpler parts for easier computation:

- **a x (b + c)** = **a x b + a x c**
- **a x (b - c)** = **a x b - a x c**

This method helps simplify complex multiplication operations by transforming them into sums or differences that are easier to compute.

## 1.2 Examples of Distributive Law

| Problem | Solution |
|--------|----------|
| 567958 x 99999 | 567958 x (100000 - 1) = 56795800000 - 567958 = 56795232042 |
| 978 x 184 + 978 x 816 | 978 x (184 + 816) = 978 x 1000 = 978000 |

These examples demonstrate how breaking down large numbers using the distributive property simplifies the calculation process.

## 2. Multiplying by Powers of 5

## 2.1 Rule

To multiply a number by $5^n$:
1. Add $n$ zeros to the end of the number.
2. Divide the resulting number by $2^n$.

**Example:**  
$$ 975436 \times 625 = 975436 \times 5^4 = 9754360000 \div 16 = 609647600 $$

## 3. Multiplying by Numbers Containing Repeated Nines (e.g., 9, 99, 999)

## 3.1 Rule

To multiply a number by $10^n - 1$:
1. Add $n$ zeros to the end of the number.
2. Subtract the original number from the result obtained in step 1.

**Examples:**

| Problem | Solution |
|--------|----------|
| 3893 × 99 | 389300 - 3893 = 385407 |
| 4327 × 999 | 4327000 - 4327 = 4322673 |
| 5863 × 9999 | 58630000 - 5863 = 58624137 |

This technique significantly reduces the complexity of

## I. Understanding LCM and HCF

## Definition and Concept
- **LCM (Least Common Multiple)**: The smallest positive integer that is divisible by each of the given numbers.
- **HCF (Highest Common Factor)**: The largest positive integer that divides each of the given numbers without leaving a remainder.

## II. Methods for Finding LCM and HCF

## A. Prime Factorization Method

## Steps:
1. Express each number as a product of its prime factors.
2. For LCM: Take the highest power of each prime factor appearing in the factorizations.
3. For HCF: Take the lowest power of each prime factor common to all numbers.

## Example:
Find the LCM of 32, 48, 60, and 320.

**Prime Factorization:**
- $ 32 = 2^5 $
- $ 48 = 2^4 \times 3 $
- $ 60 = 2^2 \times 3 \times 5 $
- $ 320 = 2^6 $

**LCM Calculation:**
$$
\text{LCM} = 2^6 \times 3 \times 5 = 64 \times 3 \times 5 = 960
$$

## B. Division Method

## Steps:
1. Write the given numbers in a line.
2. Divide by a common prime factor that divides at least two of the numbers.
3. Repeat the process with the new set of numbers until no common factors remain.
4. Multiply all the divisors and the remaining numbers to get the LCM.

## Example:
Find the LCM of 12, 15, 20, and 54.

**Division Process:**

Numbers:       12   15   20   54
Divide by 2 →    6   15   10   27
Divide by 3 →    2    5    5    9
No more common factors
**LCM Calculation:**
$$
\text{LCM} = 2 \times 3 \times 2 \times 5 \times 5 \times 9 = 540
$$

## III. Special Cases and Notes

## A. LCM and HCF of Decimals

## Steps:
1. Equalize the number of decimal places by adding zeros where necessary.
2. Compute LCM/HCF of the resulting whole numbers.
3. Adjust the decimal point in the result to match the original numbers' precision.

## Example:
Find the LCM of 1.2, 0.24, and 6

## Topic Overview
This study guide focuses on understanding how to find the **unit place digit** of large powers using modular arithmetic. We will explore patterns in the units digits of powers for specific digits and apply these patterns to simplify complex calculations.

## Key Concepts

## Understanding Units Digits
The **units digit** of a number is the digit in the one's place. For example, the units digit of 4657233 is 3.

When raising a number to a power, the **units digit repeats in cycles**. This property allows us to simplify finding the units digit of very large exponents.

## Patterns in Units Digits for Powers

| Digit | Pattern | Cycle Length |
|-------|---------|--------------|
| 2     | 2, 4, 8, 6 | 4            |
| 3     | 3, 9, 7, 1 | 4            |
| 4     | 4, 6        | 2            |
| 5     | 5           | 1            |
| 6     | 6           | 1            |
| 7     | 7, 9, 3, 1 | 4            |
| 8     | 8, 4, 2, 6 | 4            |
| 9     | 9, 1        | 2            |

These patterns help us determine the units digit without calculating the entire power.

## Steps to Determine the Units Digit

1. **Identify the base digit**: Take the last digit of the number being raised to a power.
2. **Find the pattern length** for that digit (cycle length).
3. **Divide the exponent by the cycle length**:
   - Use the **remainder** of this division.
4. **Use the remainder to index into the pattern**:
   - If the remainder is 0, use the last element of the pattern.
   - Otherwise, use the element at the position equal to the remainder.

## Example Problems and Solutions

| Problem Number | Input | Solution | Answer |
|----------------|-------|----------|--------|
| Example 39     | 4657233^33 | Units digit = 2; Power = 33 <br> Step 1: 33 ÷ 4 → Remainder = 1 <br> Step 2: 2^1 = 2 | 2 |
| Example 40     | 4657333^33 | Units digit = 3; Power = 33 <br> Step 1: 33 ÷ 4 → Remainder = 1 <br> Step 2: 3^1 = 3 | 3 |
|

---

## Self-Assessment Checklist

| Skill | Mastery Level | Notes |
|------|---------------|-------|
| Classify numbers into categories | ✅ | Understand differences between natural, whole, integers, etc. |
| Apply multiplication shortcuts | ✅ | Use mental math strategies for quick computation |
| Explain distributive law | ✅ | Demonstrate knowledge of how multiplication distributes over addition |
| Perform division accurately | ✅ | Show proficiency in dividing large numbers using rules |
| Test divisibility by common divisors | ✅ | Apply divisibility rules effectively |
| Compute HCF and LCM using multiple methods | ✅ | Practice prime factorization and Euclidean algorithm |
| Solve problems using number system concepts | ✅ | Apply learned principles to solve real-world scenarios |

## Review & Practice Questions

1. What is the difference between natural numbers and whole numbers?
2. Define prime and composite numbers with examples.
3. Explain the distributive property of multiplication.
4. List the divisibility rules for 2, 3, 5, and 10.
5. How do you find the HCF of two?

---
