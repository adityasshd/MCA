# Unit 06 Data link layer – error control and flow control

## Summary

- **Block coding** adds redundant bits to detect and correct errors.
- There are three main types of errors: **single-bit**, **multi-bit**, and **burst errors**.
- **Redundancy checks** (e.g., VRC, LRC) help detect errors during transmission.
- **Error detection** identifies if errors exist, while **error correction** attempts to fix them.
- **Flow control** prevents overwhelming the receiver by managing data rates.
A computer network connects multiple devices using communication channels to exchange data. The main goal is to enable resource sharing, communication, and data transfer between computers.
Both models describe how data travels across networks but differ in structure and usage.
Protocols define the rules for data transmission. Common protocols include:

- **HTTP** – Hypertext Transfer Protocol (web browsing)
- **FTP** – File Transfer Protocol
- **SMTP** – Simple Mail Transfer Protocol
- **DNS** – Domain Name System
- **TCP** – Transmission Control Protocol
- **UDP** – User Datagram Protocol

> ⚠️ Note: In *Remote Access for Cisco Networks*, the focus is often on **Cisco-specific protocols** such as **SSH**, **Telnet**, and **SNMP**.
Network security ensures confidentiality, integrity, and availability of data.
Different types of networks serve various purposes depending on size, scope, and connectivity.

| Type | Description |
|------|-------------|
| LAN | Local Area Network (within a small area) |
| WAN | Wide Area Network (covers large geographic areas) |
| MAN | Metropolitan Area Network (city-wide coverage) |
| PAN | Personal Area Network (devices within a short range) |

> 📌 Reference: For more details, visit [GeeksforGeeks - Types of Networks](https://www.geeksforgeeks.org/types-of-networks/).
Data can be transmitted through different media and methods.
Remote access allows users to connect to resources from afar. This is critical in modern computing environments.
Understanding performance metrics helps evaluate network efficiency.

| Metric | Definition |
|--------|------------|
| Bandwidth | Maximum data rate of a communication channel |
| Latency | Time delay in transmitting data |
| Throughput | Actual data transferred per unit time |
| Jitter | Variation in latency between packets |
| Packet Loss | Percentage of lost data packets |

---

## Keywords

- Block Coding
- Error Detection
- Error Correction
- Redundancy Check
- Parity Bit
- Cyclic Redundancy Check (CRC)
- Checksum
- Flow Control
- Stop-and-Wait Protocol
- Sliding Window Protocol

---

## Core Concepts & Topics

## Unit 06 Data link layer – error control and flow control

## Core Concepts & Topics

```markdown

## Overview
This study guide covers key concepts related to **error control** and **flow control** in the **data link layer**. It includes detailed explanations about **block coding**, **error detection and correction mechanisms**, **framing techniques**, and **redundancy checks**.

## References

- Notes provided by Lovely Professional University.
- Network Fundamentals: A Top-Down Approach by James Kurose and Keith Ross.
```

## **Study Guide: Data Link Layer - Error Control and Flow Control**

## Overview
This study guide covers the **Data Link Layer** with a focus on **error control**, **flow control**, and **reliable transmission mechanisms** like **Stop-and-Wait ARQ**, **Go-Back-N ARQ**, and **Selective Repeat ARQ**. These concepts are essential for understanding reliable data communication in networks.

## Key Concepts:
| Term | Description |
|------|-------------|
| Node | A device connected to a network (e.g., PC, server) |
| Link | Physical or logical connection between nodes |
| Protocol | Set of rules governing data exchange |
| Topology | Arrangement of nodes and links in a network |

## 🌐 2. OSI Model & TCP/IP Model

## OSI Model Layers:
| Layer | Name | Function |
|-------|------|---------|
| 1 | Physical | Transmits raw bit stream over physical medium |
| 2 | Data Link | Handles error detection and correction |
| 3 | Network | Routes packets between different networks |
| 4 | Transport | Ensures end-to-end data delivery |
| 5 | Session | Manages sessions between applications |
| 6 | Presentation | Translates data formats |
| 7 | Application | Provides user services like email and file transfer |

## TCP/IP Model Layers:
| Layer | Name | Function |
|-------|------|---------|
| 1 | Link | Physical and data link layer combined |
| 2 | Internet | Routing and IP addressing |
| 3 | Transport | End-to-end data delivery (TCP/UDP) |
| 4 | Application | User-facing services (HTTP, FTP, etc.) |

## 📡 3. Communication Protocols

## 🔒 4. Network Security

## Key Concepts:
- **Firewalls**: Monitor and control incoming/outgoing traffic
- **Encryption**: Protects data during transit (e.g., SSL/TLS)
- **Authentication**: Verifies identity before granting access
- **Authorization**: Grants appropriate permissions after authentication

> 💡 *Remote Access* introduces additional security concerns such as **secure remote login**, **data interception**, and **intrusion prevention systems**.

## 🧩 5. Types of Networks

## 🧭 6. Data Transmission

## Transmission Modes:
| Mode | Description |
|------|-------------|
| Simplex | One-way communication (e.g., radio broadcast) |
| Half-duplex | Two-way communication, one at a time (e.g., walkie-talkies) |
| Full-duplex | Simultaneous two-way communication (e.g., phone calls) |

## Transmission Media:
- **Guided Media**: Twisted pair, coaxial cable, fiber optics
- **Unguided Media**: Radio waves, microwaves, satellite

## 🛠️ 7. Remote Access Techniques

## Common Remote Access Methods:
| Method | Description |
|--------|-------------|
| SSH | Secure Shell protocol for secure remote login |
| Telnet | Unencrypted remote terminal access |
| RDP | Remote Desktop Protocol (Windows) |
| VNC | Virtual Network Computing (remote desktop sharing) |
| IPSec | Encrypts data at the network layer |

> ✅ *Bill Burton's book emphasizes the importance of **security** in remote access, particularly using **SSH** and **IPSec**.

## 📈 8. Network Performance Metrics

## 📖 9. Additional Resources

## References

| Resource | Description |
|----------|-------------|
| [GeeksforGeeks - Computer Network Tutorials](https://www.geeksforgeeks.org/computer-network-tutorials/) | Comprehensive tutorials covering all aspects of networking |
| *Remote Access for Cisco Networks* by Bill Burton | Focuses on securing remote connections and managing Cisco devices |
| *Computer Networks and Internet* by Rajneesh Agrawal and Bharat Bhushan Tiwari | Detailed theoretical and practical approach to networking fundamentals |

## 📌 Final Notes

- **Understand the OSI vs TCP/IP model** to grasp how data flows across networks.
- **Master common protocols** such as HTTP, FTP, SMTP, DNS, and TCP/UDP.
- **Focus on security** when dealing with remote access and network management.
- Use **diagrams and flowcharts** to visualize network structures and processes.

```text
        +-------------------+
        |    Application   |
        +-------------------+
                |
                v
        +-------------------+
        |   Transport      |
        +-------------------+
                |
                v
        +-------------------+
        |     Network      |
        +-------------------+
                |
                v
        +-------------------+
        |   Data Link       |
        +-------------------+
                |
                v
        +-------------------+
        |    Physical      |
        +-------------------+
```

This simple diagram illustrates the layers of the OSI model and their relationship.

Let me know if you'd like this guide in PDF format or want to explore specific sub-topics in more detail!

## Review & Practice Questions

1. Define **block coding** and explain its purpose.
2. List the types of errors that occur during data transmission.
3. Explain the difference between **error detection** and **error correction**.
4. What is a **parity check**, and how does it work?
5. Describe the role of **flow control** in data communication.

---.
1. What is the data link protocol?
2. What advantages does Selective Repeat sliding window protocol offer over Go Back N protocol?
3. What is the purpose of flow control?
4. How does a finite state machine model perform protocol verification?
5. What are different data link protocols available? Why has PPP become popular?
6. Explain error detection techniques.
7. Explain Hamming code with an example.

---
