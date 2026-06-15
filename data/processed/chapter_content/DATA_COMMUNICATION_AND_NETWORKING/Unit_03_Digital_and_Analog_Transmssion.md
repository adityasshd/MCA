# Unit 03 Digital and Analog Transmssion

## Summary

| Scheme     | Description                                           | Advantages                           | Disadvantages                         |
|------------|-------------------------------------------------------|--------------------------------------|----------------------------------------|
| NRZ        | Non-Return-to-Zero                                    | Simple                                | Baseline Wandering                    |
| NRZ-L      | Level-based                                          | Simple                                | Baseline Wandering                    |
| NRZ-I      | Inverted                                              | Better sync than NRZ-L               | Baseline Wandering                    |
| RZ         | Returns to zero                                       | Reduces baseline wandering           | High bandwidth, Complexity            |
| Manchester | Transition in the middle                             | Good sync, no DC bias                | Bandwidth inefficient                 |
| Differential Manchester | Transition at start and middle             | Good sync, no DC bias                | Bandwidth inefficient                 |
| Concept               | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| Manchester Encoding  | Ensures no DC component and baseline wandering                             |
| Bipolar Schemes      | Use three voltage levels (positive, negative, zero)                        |
| Data Communication   | Combines analog and digital signals to achieve full communication          |
| Modulation Techniques| ASK, FSK, PSK are methods to convert digital to analog signals              |
| Baud vs Bit Rate     | Bit rate is generally greater than or equal to baud rate                   |
| Carrier Signal       | High-frequency signal used for modulation                                 |

---

## Core Concepts & Topics

## Unit 03 Digital and Analog Transmssion

## Core Concepts & Topics

```markdown
## Unit 03: Digital and Analog Transmission

## Objectives
- Represent digital data using digital signals.
- Learn schemes for transmitting data digitally.
- Understand digital-to-analog conversions.
- Gain knowledge about various modulation techniques.

## Digital Transmission

## 3.1 Digital-to-Digital Transmission
Digital data can be represented using digital signals through **line coding**, **block coding**, and **scrambling**.

## Key Concepts:
- **Signal Element vs Data Element**: 
  - A **data element** represents a piece of information (e.g., a bit).
  - A **signal element** is the carrier of the data, defined as the shortest unit of a digital signal over time.
- **Ratio (r)**: Number of data elements per signal element.
  - $ r = \frac{\text{Number of data elements}}{\text{Number of signal elements}} $
- **Data Rate vs Signal Rate**:
  - **Data rate** = Bits per second (bps)
  - **Signal rate** = Baud (unit of signal elements per second)

## Common Characteristics:
- **Baseline Wandering**: Caused by long strings of 0s or 1s leading to difficulty in decoding.
- **DC Component**: Constant voltage levels create low-frequency components, problematic for certain systems like phone lines.
- **Self-Synchronization**: Timing information embedded in the signal ensures accurate decoding.
- **Error Detection**: Encoding schemes should detect transmission errors.
- **Immunity to Noise**: Encoding schemes should minimize interference effects.
- **Complexity**: Simpler schemes are preferred due to lower implementation cost.

## 3.2 Line Coding Schemes

Line coding schemes are classified into three types:

| Category       | Description |
|----------------|-------------|
| **Unipolar**   | All signal levels are on one side of the time axis. |
| **Bipolar**    | Uses both positive and negative voltage levels. |
| **Polar**      | Combines bipolar and unipolar schemes. |

## Unipolar Schemes
- **NRZ (Non-Return-to-Zero)**:
  - Positive voltage = Bit 1
  - Zero voltage = Bit 0
  - No return to zero in the middle of the bit.
  - **Subtypes**:
    - **NRZ-L (Level)**: Voltage level indicates bit value.
    - **NRZ-I (Invert)**: Transition occurs when the bit is 1, no transition when bit is 0.
- **Disadvantages**: Susceptible to baseline wandering and lack of synchronization.

## Return to Zero (RZ)
- Uses three levels: positive, negative, and zero.
- Signal returns to zero in the middle of each bit.
- **Disadvantages**: Higher bandwidth and complexity compared to NRZ.

## Biphase (Manchester & Differential Manchester)
- **Manchester**:
  - Each bit is split into two halves.
  - Voltage changes at the middle of the bit for synchronization.
  - Bit 1 → Transition from -V to +V
  - Bit 0 → Transition from +V to -V
- **Differential Manchester**:
  - Always has a transition at the middle of the bit.
  - Bit value is determined at the beginning of the bit.
  - Bit 0 → Transition at start
  - Bit 1 → No transition at start

## Diagrams and Flowcharts

```text
+-------------------------------+
|       Line Coding              |
+-------------------------------+
| Unipolar                      |
|   - NRZ (Non-Return-to-Zero)  |
|   - NRZ-L                     |
|   - NRZ-I                     |
+-------------------------------+
| Bipolar                       |
|   - RZ (Return to Zero)       |
+-------------------------------+
| Polar                         |
|   - Manchester               |
|   - Differential Manchester   |
+-------------------------------+
```

```text
+-------------------------------+
|          NRZ                  |
+-------------------------------+
| Bit 1 -> +V                   |
| Bit 0 -> 0V                   |
+-------------------------------+
|     Baseline Wandering        |
| (Long sequences of 0s or 1s)  |
+-------------------------------+
```

```text
+-------------------------------+
|         Manchester           |
+-------------------------------+
| Bit 1: -V to +V at mid-bit    |
| Bit 0: +V to -V at mid-bit    |
+-------------------------------+
| Provides Sync and no DC Bias  |
+-------------------------------+
```

```text
+-------------------------------+
|    Differential Manchester    |
+-------------------------------+
| Always has a transition at    |
| the middle of the bit         |
| Bit 0: Transition at start    |
| Bit 1: No transition at start |
+-------------------------------+
```

## Diagram: Phase Shift Keying (PSK)

```text
        |
        v
     _________
    |         |
    |   0°    | <--- 0
    |_________|
        |
        v
     _________
    |         |
    |   180°  | <--- 1
    |_________|
```

> This diagram represents **Binary PSK** where a **0°** phase corresponds to a '0' and **180°** phase corresponds to a '1'.

## Conclusion

Understanding the principles of **Manchester encoding**, **bipolar schemes**, **modulation techniques**, and **data communication systems** is essential for grasping how data is efficiently and reliably transmitted over modern networks. These concepts underpin the functionality of **modems**, **telecom infrastructure**, and **wireless communication protocols**.
```

```markdown

## Overview

This study guide provides a comprehensive review of key concepts related to **Digital and Analog Transmission** covered in Chapter 3. Topics include modulation types, conversion techniques, transmission methods, and relevant terminology.

## 1. Fundamental Concepts

## Definition of Circuit
- A **circuit** is a path between two or more points used to carry signals.
- It can be **physical** (e.g., wires) or **wireless**.
- A **network** consists of multiple circuits involving intermediate switches.

## Virtual Circuit
- A **virtual circuit** is a **logical path** chosen from available **physical paths** between points.

## Multiplexing
- **Multiplexing** combines multiple channels for transmission over a common path.
- Techniques include:
  - **FDM (Frequency Division Multiplexing)**: Combines multiple channels based on frequency.
  - **TDM (Time Division Multiplexing)**: Allocates time slots for each channel.

## 2. Digital vs. Analog Transmission

## Bandwidth Requirements
- **Digital transmission** requires a **low-pass channel with high bandwidth**.
- **Analog transmission** uses **bandpass channels**.

## Conversion Methods
- **Digital to Analog**: Used when converting digital data to analog signals.
- **Analog to Analog**: Involves techniques like **amplitude**, **frequency**, and **phase modulation**.

## 3. Modulation Techniques

## Types of Modulation
| Modulation Type | Description |
|------------------|-------------|
| **ASK (Amplitude Shift Keying)** | Varies the amplitude of the carrier wave. |
| **FSK (Frequency Shift Keying)** | Changes the frequency of the carrier wave. |
| **PSK (Phase Shift Keying)** | Alters the phase of the carrier wave. |
| **QAM (Quadrature Amplitude Modulation)** | Combines both amplitude and phase modulation. |

> ✅ **Note:** These are all forms of **digital-to-analog conversion**.

## 4. Multiple Choice Questions & Answers

## Question 12: Minimum Bandwidth Requirement
- **Answer:** `a. ASK` and `b. PSK`

## Question 13: Bit Rate = Four Times Baud Rate
- **Answer:** `c. PSK`

## Question 14: Bit Rate = Three Times Baud Rate
- **Answer:** `d. None of the above`

## Question 15: Bit Rate = Half the Baud Rate
- **Answer:** `d. None of the above`

## Question 16: Conversion Type
- **Answer:** `b. digital-to-analog`

## Question 17: Process Description
- **Answer:** `a. Digital–to-analog`

## 5. Summary Table

| Term | Explanation |
|------|-------------|
| **Baud Rate** | Number of times per second the signal can change state (from "1" to "0"). |
| **Bit Rate** | Rate at which bits are transmitted (measured in bits/sec). |
| **Modulation** | Technique to translate low-frequency signals to higher frequency for transmission. |
| **Multiplexing** | Combining multiple signals for simultaneous transmission over a single channel. |
| **Modems** | Devices that convert analog and digital signals (modulator/demodulator). |

## 6. Keywords and Definitions

| Term | Explanation |
|------|-------------|
| **Amplitude Modulation (AM)** | Modulates the amplitude of the carrier wave. |
| **Frequency Modulation (FM)** | Modulates the frequency of the carrier wave. |
| **Phase Modulation (PM)** | Modulates the phase of the carrier wave. |
| **ASK** | Amplitude varies to represent data. |
| **FSK** | Frequency varies to represent data. |
| **PSK** | Phase varies to represent data. |
| **QAM** | Combines both amplitude and phase variations. |
| **TDM (Time Division Multiplexing)** | Divides time into slots for each channel. |
| **FDM (Frequency Division Multiplexing)** | Divides frequency spectrum into separate channels. |
| **WDM (Wavelength Division Multiplexing)** | Uses different wavelengths in fiber optics. |
| **Crossbar Switch** | Simplest form of **space division switching**. |

## 7. Diagram: Modulation Comparison

```text
+-------------------+        +-------------------+
|     Digital      |--------|    Analog         |
|   Data / Signal  |        |   Carrier Wave   |
+-------------------+        +-------------------+
          ^                           ^
          |                           |
          v                           v
+-------------------+        +-------------------+
|   Modulation     |        | Demodulation      |
|   Techniques     |        | Techniques       |
+-------------------+        +-------------------+
```

## 8. Further Reading

- **Books**
  - Andrew S. Tanenbaum, *Computer Networks*, Prentice Hall.
  - Behrouz A. Forouzan and Sophia Chung Fegan, *Data Communications and Networking*, McGraw-Hill.
  - Rajneesh Agrawal and Bharat Bhushan Tiwari, *Computer Networks and Internet*, Vikas Publication.

- **Online Resources**
  - [GeeksforGeeks - Computer Network Tutorials](https://www.geeksforgeeks.org/computer-network-tutorials/)

## 9. Practice Questions

1. What is the difference between **bit rate** and **baud rate**?
2. Which modulation technique has the highest data rate for a given bandwidth?
3. Explain the concept of **multiplexing** and give an example.
4. What is the purpose of **modems** in communication systems?

## 10. Final Notes

Understanding the relationship between **modulation techniques**, **bandwidth requirements**, and **conversion methods** is crucial in designing efficient communication systems. Familiarizing yourself with terms like **Baud Rate**, **Bit Rate**, **ASK**, **FSK**, **PSK**, and **QAM** will help in analyzing and solving problems related to **Digital and Analog Transmission** effectively.

Let me know if you need further clarification or practice exercises!

---

---
