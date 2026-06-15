# Unit 09 Network layer – routing

## Summary

| Concept                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| **Direct vs. Indirect Delivery** | Direct if sender and receiver are on the same network; Indirect otherwise |
| **Next-Hop Approach**        | Lists only the immediate next hop in the routing table                    |
| **Host-Specific Method**     | Stores full IP address in the routing table                               |
| **Classless Addressing**     | Reduces routing table size by using hierarchical and regional routing     |
| **Static vs. Dynamic Tables** | Static tables are manually configured; Dynamic tables are updated via routing protocols |

---

## Core Concepts & Topics

## Unit 09 Network layer – routing

## Core Concepts & Topics

```markdown

## **Overview**
This study guide covers the essential topics related to the **Network Layer** and **Routing** in Data Communication and Networking. It focuses on key concepts like **Unicast**, **Distance Vector Routing**, **Link State Routing**, **Path Vector Routing**, and **BGP (Border Gateway Protocol)**. Additionally, it explores **Casting** and **Ad-hoc Networks**.

## **1. Objectives**

| Objective | Description |
|----------|-------------|
| Understand what **Unicast Routing** is. | Learn about point-to-point communication in networking. |
| Identify the **three major protocols for unicast routing**. | These include Distance Vector, Link State, and Path Vector Routing. |
| Classify **Routing Algorithms**. | Differentiate between Distance Vector, Link State, and Path Vector algorithms. |

## **2. Introduction**

## **Key Concepts:**
- **IP Protocol**: The primary protocol at the network layer.
- **Logical vs Physical Addresses**: IP uses logical addresses, whereas frames require physical addresses.
- **ARP (Address Resolution Protocol)**: Maps physical addresses to logical ones.
- **ICMP (Internet Control Message Protocol)**: Provides error reporting and diagnostics.

> **Note:** IP lacks flow and error control, so additional protocols are required for robustness.

## **3. Unicast**

## **Definition:**
- **Unicast Routing**: Transmission from a single source to a single destination (point-to-point).
- **Examples**: TCP and HTTP.

## **Types of Routing Protocols:**
- **Intradomain Routing**: Within a specific domain (e.g., institutional network).
- **Interdomain Routing**: Between different domains (e.g., across the internet).

## **4. Distance Vector Routing**

## **Key Characteristics:**
- Each node maintains a **distance vector table** showing the minimum cost to each other node.
- Uses metrics like **hop count**, **cost**, **bandwidth**, etc.
- **Next Hop** is specified in the table to reach the destination.

## **Initialization:**
- Initial tables contain only direct neighbor links.
- Non-neighbors are marked as unreachable (**infinite distance**).

## **Sharing Process:**
- Nodes share only the **first two columns** (Distance & Next Hop) of their routing table.
- Third column (sender name) is added when the table is shared.

## **Updating:**
- When a node receives a table, it applies the following rules:
  1. Apply the cost between itself and the transmitting node.
  2. Use the transmitter’s name as the next hop.
  3. Compare with the existing entries to choose the best path.

## **Update Triggers:**
- **Periodic Updates**: Every 30 seconds.
- **Triggered Updates**: Sent immediately when a change occurs.

## **5. Link State Routing**

## **Key Features:**
- Routers exchange **link-state packets** to build a complete view of the network topology.
- Uses the **Dijkstra Algorithm (SPF)** to compute the shortest path.
- Requires **more memory and processing power** than Distance Vector.

## **Components:**
- **Link State Packet (LSP)**: Contains network topology information.
- **Link State Database (LSDB)**: Stores all LSPs.
- **Routing Table**: List of known routes and interfaces.

## **Advantages:**
- Responds quickly to **topology changes**.
- More secure due to **authentication methods**.
- No **split horizon** strategy required.

## **OSPF (Open Shortest Path First):**
- Developed by IETF.
- Classless protocol supporting **variable-length subnet masks (VLSM)**.
- Uses **Dijkstra's algorithm**.
- Has versions **OSPFv1** and **OSPFv2**, with **v2** being widely used.
- Sets the **protocol field** to **89** in IP headers.

## **6. Path Vector Routing**

## **Definition:**
- Focuses on **path attributes** rather than cost.
- Analyzes the **path to the destination** to ensure **loop freedom**.

## **Key Points:**
- Unlike Distance Vector, it doesn’t use **cost** to select the path.
- Used primarily in **interdomain routing**, especially in **BGP (Border Gateway Protocol)**.

## **7. Border Gateway Protocol (BGP)**

## **Overview:**
- **Interdomain routing protocol** used between autonomous systems (AS).
- Based on **Path Vector** logic.
- Ensures **loop prevention** by tracking the **path taken** to reach a destination.

## **Key Features:**
- Uses **TCP** for transport.
- Supports **policy-based routing**.
- Used by **ISP routers** to exchange routing information.

## **8. Types of Casting in a Computer Network**

| Type | Description |
|------|-------------|
| **Unicast** | One-to-one communication. |
| **Multicast** | One-to-many communication. |
| **Broadcast** | One-to-all communication. |

> **Note:** Casting relates to **data delivery mechanisms**, not directly to routing.

## **9. Routing in Ad-hoc Networks**

## **Definition:**
- **Ad-hoc Networks**: Self-configuring wireless networks without pre-existing infrastructure.
- Routing in ad-hoc networks is **dynamic** and **decentralized**.
- Common protocols: **DSR (Dynamic Source Routing)**, **AODV (Ad-hoc On-Demand Distance Vector)**.

## **Key Challenges:**
- Mobility of nodes.
- Limited bandwidth.
- Dynamic topologies.

## **Summary**

| Topic | Key Concept |
|------|-------------|
| **Unicast** | Point-to-point communication. |
| **Distance Vector** | Uses cost and next-hop info; prone to loops. |
| **Link State** | Builds full network view; efficient for large networks. |
| **Path Vector** | Analyzes path attributes; ensures loop-free routing. |
| **BGP** | Interdomain routing protocol; used between AS. |
| **Casting** | Includes unicast, multicast, and broadcast. |
| **Ad-hoc Networks** | Decentralized, self-configuring networks. |

## **Keywords**

- **Unicast**
- **Distance Vector**
- **Link State**
- **Path Vector**
- **BGP**
- **Casting**
- **Ad-hoc Networks**
- **OSPF**
- **Dijkstra Algorithm**
- **ICMP**
- **ARP**

## **Review Questions**

1. What is **Unicast Routing**?
2. Explain the difference between **Distance Vector** and **Link State** routing.
3. What role does **BGP** play in interdomain routing?
4. Define **Casting** and list its types.
5. Describe how **OSPF** works and why it is preferred over **RIP**.

## **Self-Assessment**

- ✅ Can you explain how **Distance Vector Routing** prevents loops?
- ✅ Can you differentiate between **Link State** and **Path Vector** routing?
- ✅ Are you familiar with **BGP** and its significance in the Internet?

## **Further Reading**

- **RFC Documents** for BGP, OSPF, and RIP.
- **Textbooks on Data Communications** (e.g., *Computer Networking: A Top-Down Approach*).
- Online tutorials on **Distance Vector vs Link State** routing.
- Research papers on **Ad-hoc Networks** and **Mobile IP**.

--- 

Let me know if you'd like this material formatted for presentation slides or interactive quizzes!

```markdown

---

---
