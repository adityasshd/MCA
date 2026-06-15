# Unit 02 Data and Signals

## Summary

| Feature             | Analog Signal                      | Digital Signal                      |
|---------------------|------------------------------------|-------------------------------------|
| **Values**          | Infinite                          | Limited (Discrete)                  |
| **Representation**  | Continuous                        | Discrete                            |
| **Signal Shape**    | Smooth curve                      | Step-like                          |
| **Usage**           | Audio, video, sensors             | Computer data, text                 |
| **Transmission**    | More susceptible to noise         | Less susceptible to noise           |

---

## Core Concepts & Topics

## Unit 02 Data and Signals

## Core Concepts & Topics

## Overview
This study guide covers key concepts related to **Data and Signals** in networking, focusing on **Physical Layer Functions**, **Signal Classification**, **Transmission Modes**, **Transmission Impairments**, and **Network Protocols & Standards**.

## 1. Major Functions of the Physical Layer

## Key Points:
- The **physical layer** is responsible for moving data via **electromagnetic signals** through a **transmission medium**.
- It handles **signal strength**, **frequency allocation**, and **analog/digital signal representation**.
- The transmission medium could be **wireless**, **optical fiber**, or **coaxial cable**.

## 2. Signal Classifications

## 2.1 Analog vs. Digital Signals

| Type         | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| **Analog**   | Continuous signal with **infinite values** (e.g., voice, temperature).     |
| **Digital**  | Discrete signal with **limited values** (e.g., binary data: 0 and 1).      |

> ✅ **Analog Data**: Continuous and unbroken.
> ✅ **Digital Data**: Discrete and broken into units (bits).

## 2.2 Types of Signals

## a) **Periodic Signals**
- Repeat after a fixed period.
- Example: Sine wave.

## b) **Non-Periodic Signals**
- Don't repeat in a fixed pattern.
- Example: Random noise.

## 3. Transmission Modes

## 3.1 Definition
Transmission mode determines the **directionality** of data flow between devices.

## 3.2 Types of Transmission Modes

| Mode       | Description                                                                                   |
|------------|------------------------------------------------------------------------------------------------|
| **Simplex** | One-way communication (e.g., radio broadcasting).                                             |
| **Half-Duplex** | Two-way communication, but **only one direction at a time** (e.g., walkie-talkie).          |
| **Full-Duplex** | Simultaneous two-way communication (e.g., telephone call).                                  |

## 4. Transmission Impairments

## 4.1 Definition
Impairments affect the quality of signals during transmission. They include:

- **Attenuation**: Loss of signal strength due to distance.
- **Distortion**: Change in signal shape due to interference.
- **Noise**: Unwanted random variations in the signal.

## 4.2 Causes of Impairments

| Cause        | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| **Attenuation** | Energy loss over distance. Used **amplifiers** to compensate.              |
| **Distortion**  | Signal shape changes due to varying propagation speeds of different frequencies. |
| **Noise**       | External interference (e.g., background static).                           |

## 5. Network Protocols & Standards

## 5.1 Definition
Protocols define rules for **data exchange** and **error handling** between devices.

## 5.2 Components of a Protocol

| Component         | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Syntax**        | Format of data exchanged.                                                  |
| **Semantics**     | Meaning of data exchanged.                                                 |
| **Timing**        | Timing of data exchange (e.g., sequence, synchronization).               |

## 6. Essential Network Performance Metrics

| Metric            | Description                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------|
| **Bandwidth**     | Maximum data transmission rate available.                                                      |
| **Throughput**    | Actual data transfer rate experienced.                                                         |
| **Latency**       | Time taken for a packet to travel from source to destination.                                 |
| **Packet Loss**   | Percentage of data packets that fail to reach their destination.                              |
| **Retransmission** | Number of times data packets are resent due to loss or corruption.                            |
| **Availability**  | Uptime of the network (percentage of time it's operational).                                   |
| **Connectivity**  | Ability of devices to communicate with each other.                                              |

## Diagram: Transmission Modes

```text
+-----------------------+
|     Simplex          |
|                      |
|   [Sender] → [Receiver]  |
+-----------------------+

+-----------------------+
|  Half-Duplex         |
|                      |
|   [Sender] ↔ [Receiver]  |
| (Alternating)        |
+-----------------------+

+-----------------------+
|   Full-Duplex        |
|                      |
|   [Sender] ↔ [Receiver]  |
| (Simultaneous)       |
+-----------------------+
```

## Key Formulas

## 1. Bit Rate
$$ \text{Bit Rate} = \frac{\text{Number of Bits}}{\text{Time (seconds)}} $$

## 2. Baud Rate
$$ \text{Baud Rate} = \frac{\text{Number of Symbols}}{\text{Time (seconds)}} $$

## 3. Channel Capacity
$$ C = 2 \times \text{Bandwidth} \times \text{Propagation Delay} $$

## Review & Practice Questions

1. Define the role of the physical layer in data communication.
2. Explain the difference between analog and digital signals.
3. List and describe the three main types of transmission modes.
4. What are the common causes of transmission impairments?
5. Why is understanding network performance metrics important?

---
