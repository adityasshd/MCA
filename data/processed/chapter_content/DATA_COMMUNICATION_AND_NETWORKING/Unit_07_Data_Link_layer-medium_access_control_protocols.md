# Unit 07 Data Link layer-medium access control protocols

## Summary

| Concept                    | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| Framing                   | Organizing data into frames for reliable transmission                      |
| HDLC                       | Bit-oriented protocol providing reliability, error detection, and flow control |
| PPP                        | Point-to-point protocol offering encapsulation, authentication, and negotiation |
| Random-Access Protocols   | Allow devices to contend for channel access                                |
| Controlled Access         | Centralized method of managing access                                     |
| Channelization Protocols  | Divide the channel into subchannels for parallel communication             |

---

## Keywords

- HDLC
- PPP
- Framing
- Error Correction
- Flow Control
- Medium Access Control
- Random-Access
- Controlled Access
- Channelization

---

## Core Concepts & Topics

## Unit 07 Data Link layer-medium access control protocols

## Core Concepts & Topics

```markdown

## Self-Assessment
1. What is the role of the **flag field** in HDLC?
2. How does PPP differ from HDLC?
3. What are the three types of HDLC frames and their purposes?
4. Explain the concept of **byte stuffing** in PPP.
5. List and briefly describe three random-access protocols.

## Answers for Self-Assessment
1. The **flag field** marks the start and end of a frame and helps synchronize sender and receiver clocks.
2. PPP adds **authentication** and **network protocol negotiation** features not found in HDLC.
3. **I-Frames** carry data, **S-Frames** manage flow/error control, and **U-Frames** handle configuration.
4. **Byte stuffing** prevents flag sequences from being mistaken for frame boundaries.
5. Examples of random-access protocols: **CSMA/CD**, **Aloha**, and **CSMA/CA**.

## Overview
This study guide covers key concepts related to **Medium Access Control (MAC)** protocols in the **Data Link Layer** of the OSI model. These protocols manage how multiple devices share a common communication channel. Topics include **Random Access**, **Controlled Access**, and **Channelization** protocols, along with specific examples such as **ALOHA**, **CSMA**, **CSMA/CD**, **CSMA/CA**, **Reservation**, **Polling**, **Token Passing**, **FDMA**, **TDMA**, and **CDMA**.

## 1. Random Access Protocols

## 1.1 ALOHA
- **Description**: Developed for shared medium (wireless LAN or wired).
- **Types**:
  - **Pure Aloha**
    - Stations transmit whenever ready.
    - If collision occurs, retransmission happens after a random backoff time.
    - Vulnerable Time = 2 × Frame Transmission Time
    - Throughput = $ G e^{-2G} $
    - Maximum Throughput = ~18.4% for $ G = 0.5 $
  - **Slotted Aloha**
    - Time is divided into slots; data can only be sent at the beginning of each slot.
    - Vulnerable Time = Frame Transmission Time
    - Throughput = $ G e^{-G} $
    - Maximum Throughput = ~36.8% for $ G = 1 $

| Feature               | Pure Aloha         | Slotted Aloha      |
|----------------------|--------------------|--------------------|
| Collision Risk       | High               | Lower              |
| Backoff Time         | Random             | Fixed (slot-based) |
| Maximum Throughput   | ~18.4%             | ~36.8%             |

## 1.2 CSMA (Carrier Sense Multiple Access)
- **Description**: Before transmitting, a station checks if the channel is idle.
- **Collision Possibility**: Due to **propagation delay**, even idle channels can cause collisions.
- **Access Methods**:
  - **1-Persistent**: Transmits immediately upon detecting an idle channel.
  - **Non-Persistent**: Waits a random time if the channel is busy.
  - **P-Persistent**: Sends data with probability $ p $ when the channel is idle.
  - **O-Persistent**: Predefined priority determines transmission order.

## 1.3 CSMA/CD (Collision Detection)
- **Description**: Detects collisions by monitoring the channel during transmission.
- **Process**:
  - If a collision is detected, the station stops transmission and waits for a random backoff time before retrying.

## 1.4 CSMA/CA (Collision Avoidance)
- **Description**: Uses acknowledgments to detect collisions.
- **Process**:
  - Sender listens for acknowledgment (ACK) after sending data.
  - If ACK is received → successful transmission.
  - If ACK is missing → collision detected.

## 2. Controlled Access Protocols

## 2.1 Reservation
- **Description**: Stations must reserve time before transmitting.
- **Types of Intervals**:
  - Fixed-Length Interval
  - Variable Frame Data Transfer Time

## 2.2 Polling
- **Description**: Controller polls each station sequentially to check for data.
- **Process**:
  - Controller sends a "poll" message.
  - Only the polled station responds if it has data.
- **Drawbacks**:
  - High overhead due to frequent polling.
  - Reliance on controller's reliability.

## 2.3 Token Passing
- **Description**: Stations pass a **token** around the network.
- **Mechanism**:
  - Token circulates through the network.
  - Only the station holding the token can transmit.
- **Variants**:
  - **Token Ring**: Token passes in a logical ring.
  - **Token Bus**: Token moves in a predefined order on the bus.
- **Issues**:
  - Token duplication or loss.
  - Insertion/removal of stations.

## 3. Channelization Protocols

## 3.1 FDMA (Frequency Division Multiple Access)
- **Description**: Divides the frequency spectrum into separate bands.
- **Features**:
  - Each station gets its own dedicated frequency band.
  - Guard bands prevent interference.

## 3.2 TDMA (Time Division Multiple Access)
- **Description**: Divides time into slots.
- **Features**:
  - Each station is allocated specific time slots.
  - Synchronization required across all stations.
  - Guard bands reduce propagation delay effects.

## 3.3 CDMA (Code Division Multiple Access)
- **Description**: All users share the same frequency band but use unique codes.
- **Features**:
  - Signals are distinguished by unique **code sequences**.
  - Allows simultaneous transmission without interference.
  - Example: Multiple people speaking the same language in a room.

## 4. Summary of Key Concepts

| Concept                   | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| MAC Protocol             | Manages access to a shared communication channel.                           |
| ALOHA                    | Random access protocol with potential for collision.                       |
| CSMA                     | Carrier Sensing mechanism to avoid collisions.                             |
| CSMA/CD                  | Detects collisions during transmission.                                   |
| CSMA/CA                  | Avoids collisions using acknowledgments.                                   |
| Controlled Access        | Includes Reservation, Polling, and Token Passing.                          |
| Channelization           | Allocates bandwidth via Frequency, Time, or Code.                          |
| FDMA/TDMA/CDMA           | Techniques for dividing bandwidth among users.                             |

## 5. Keywords

- **Point-to-Point (PPP)**: Protocol for direct communication between two peers.
- **ALOHA**: Shared medium access with collision possibility.
- **CSMA/CD**: Collision detection during transmission.
- **Controlled Access**: Requires permission from others before transmission.
- **Channelization**: Allocates bandwidth based on time, frequency, or code.

## 6. Self-Assessment Questions

1. ___________ describes the techniques to access a shared communication channel and reliable transmission of data frame in computer communication environment.
2. ___________ does not include any connection setup or release and does not deal with frame recovery due to channel noise.
3. ___________ refers to a reliable transfer of bit streams to the network layer for which the data link layer breaks the bit stream into frames.
4. ___________ controls mismatch between the source and destination.

> **Answer:** 1. MAC 2. ALOHA 3. Data Link Layer 4. Flow Control

--- 

Let me know if you'd like a PDF version or additional practice exercises!

```markdown

## Review & Practice Questions

1. What is the difference between **HDLC** and **SDLC**?
2. Describe the structure of an **HDLC frame**.
3. What is the purpose of the **control field** in HDLC?
4. Explain the process of **byte stuffing** in PPP.
5. What are the key components of the **PPP protocol**?
| Question Number | Topic                             | Answer                                                                 |
|------------------|-----------------------------------|------------------------------------------------------------------------|
| 1                | Data Link Protocol               | Ensures reliable transmission between nodes                         |
| 2                | Categories of Services           | Unacknowledged connectionless service                                |
| 3                | Framing                          | Process of encapsulating data into frames                           |
| 4                | Rate of Data Transmission       | Determines how much data can be transmitted per unit time          |
| 5                | Groups of Access Methods         | Four                                                                  |
| 6                | Time Division                    | TDMA                                                                   |
| 7                | Logical Ring                     | Token Passing                                                         |
| 8                | Collision Detection              | CSMA/CD                                                               |
| 9                | Transmission Strategy            | 1-Persistent                                                          |
| 10               | Reservation Method               | Reservation                                                           |
| 11               | Logical Ring Structure           | Token Passing                                                         |
| 12               | Vulnerable Time                  | Same as propagation time                                              |

---
