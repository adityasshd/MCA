# Unit 11 Transport layer - congestion control and QoS

## Summary

| Concept | Summary |
|--------|---------|
| **Traffic Descriptors** | Define key metrics like average, peak, and burst rates. |
| **Traffic Profiles** | Classify traffic patterns into steady, volatile, and bursty. |
| **Congestion Control** | Includes prevention (open loop) and removal (closed loop) strategies. |
| **QoS** | Enhances user experience through prioritization and resource allocation. |
| **Traffic Shaping** | Manages data flow to prevent congestion and ensure fairness. |

---

## Keywords

- | Term | Explanation |
- |------|-------------|
- | **Congestion Control** | Methods to manage network overload. |
- | **QoS** | Quality of Service: Ensures performance standards for different data flows. |
- | **Traffic Descriptor** | Metrics used to characterize data flow. |
- | **Traffic Profile** | Classification of data flow patterns. |
- | **Traffic Shaping** | Techniques to regulate data rate and prevent congestion. |

---

## Core Concepts & Topics

## Unit 11 Transport layer - congestion control and QoS

## Core Concepts & Topics

```markdown

## Overview
This unit focuses on **Transport Layer** concepts related to **Congestion Control** and **Quality of Service (QoS)**. It explores how networks handle varying types of data traffic, the challenges posed by congestion, and the techniques used to optimize network performance and ensure consistent service delivery.

## Self-Assessment

1. **True/False**: Congestion management and QoS are independent concepts.  
   ✅ False – They are closely related and mutually reinforcing.

2. **Multiple Choice**: Which of the following is a method of traffic shaping?  
   A) Token bucket algorithm  
   B) IP fragmentation  
   C) Error correction  
   D) All of the above  

   ✅ A) Token bucket algorithm

3. **Short Answer**: Explain how a selective repeat window helps in reducing congestion compared to Go Back N.

   > **Answer**: Selective repeat sends only the missing packets instead of resending all packets after a loss, thereby reducing redundant transmissions and minimizing congestion.

## **Table of Contents**

| Topic | Description |
|------|-------------|
| Introduction | Overview of congestion and QoS |
| Traffic Management Techniques | Leaky Bucket and Token Bucket Algorithms |
| Resource Reservation | Importance of resource allocation |
| Admission Control | Process of flow acceptance |
| Review Questions | Practice questions for understanding concepts |
| Self-Assessment | Multiple choice questions for self-evaluation |

## **1. Introduction to Congestion and QoS**

## **Congestion**
- **Definition**: A network becomes congested when packets experience delays significantly larger than the propagation delay.
- **Effects**:
  - Performance degradation
  - Increased latency
  - Potential packet loss
- **Extreme Congestion**: When packets fail to reach their destination, it results in infinite delay.

## **QoS (Quality of Service)**
- **Purpose**: Ensures consistent performance for different types of traffic.
- **Key Components**:
  - Bandwidth allocation
  - Latency control
  - Error handling
- **Model Used**: Integrated Services (focuses on resource reservation)

## **2. Traffic Management Techniques**

## **Leaky Bucket Algorithm**
- **Function**: Limits the data rate by enforcing a constant output rate.
- **Operation**:
  - Packets are stored in a FIFO queue.
  - A fixed number of packets are removed per clock tick.
- **Use Case**:
  - Prevents bursty traffic from overwhelming the network.
  - Helps in congestion avoidance.

## **Token Bucket Algorithm**
- **Function**: Allows bursts of data transmission up to a certain limit.
- **Operation**:
  - Tokens are added to the bucket at a fixed rate.
  - Each data unit removes one token.
  - Bucket can accumulate tokens during periods of inactivity.
- **Advantages**:
  - Supports bursty traffic without dropping packets.
  - Provides more flexibility compared to the leaky bucket.

## **Comparison Table**

| Feature                | Leaky Bucket            | Token Bucket              |
|-----------------------|-------------------------|---------------------------|
| Burst Handling        | Not allowed             | Allowed                   |
| Idle Time Credit      | No                      | Yes                       |
| Output Rate           | Fixed                   | Variable                  |
| Use Case              | Traffic Shaping         | Rate Limiting             |

## **3. Resource Reservation**

- **Purpose**: Allocates resources like bandwidth, buffer, and CPU time before data transmission.
- **Benefits**:
  - Improves QoS
  - Ensures predictable performance
- **Implementation**: Integrated Services model focuses heavily on resource reservation.

## **4. Admission Control**

- **Process**:
  - Routers/switches evaluate flow requirements.
  - Check if available resources (bandwidth, buffer, CPU) can accommodate new flows.
  - Accept or reject the flow accordingly.
- **Significance**:
  - Prevents over-subscription of network resources.
  - Maintains stability and fairness.

## **5. Review Questions**

1. Explain the general principles of congestion.
2. What do you understand by QoS? Describe the basic QoS structure.
3. Discuss the following two algorithms:
   a. Leaky Bucket  
   b. Token Bucket
4. What are two types of congestion control? Where is congestion control implemented in each case?
5. Explain all traffic shaping techniques.
6. Write down techniques to improve quality of service.
7. Difference between token bucket and leaky bucket algorithm.

## **6. Self-Assessment**

## **Multiple Choice Questions**

1. The technique in which a congested node stops receiving data from the immediate upstream node or nodes is called as:
   a. Explicit signalling  
   b. Back pressure  
   c. Implicit signalling  
   d. Redundant signals  
   ✅ **Answer: b**

2. A leaky bucket algorithm shapes bursty traffic into fixed-rate traffic by averaging the:
   a. Data rate  
   b. Average rate  
   c. Traffic rate  
   d. Traffic shaping  
   ✅ **Answer: b**

3. Two classes of services have been defined for:
   a. Integrated services  
   b. Quality data services  
   c. Technical services  
   d. Protocol services  
   ✅ **Answer: a**

4. In open-loop congestion control, policies are applied to:
   a. Prevent congestion  
   b. Discard congestion  
   c. Maximize congestion  
   d. Eliminate congestion  
   ✅ **Answer: a**

5. A mechanism to control the amount and the rate of the traffic sent to the network is called:
   a. Traffic congestion  
   b. Traffic flow  
   c. Traffic control  
   d. Traffic shaping  
   ✅ **Answer: d**

6. Scheduling is done by:
   a. Weighted fair queuing  
   b. FIFO  
   c. Random  
   d. LIFO  
   ✅ **Answer: d**

7. Which of the following is a congested control algorithm:
   a. The leaky bucket  
   b. Token bucket  
   c. Resource reservation  
   d. All of above  
   ✅ **Answer: d**

8. In Congestion Control, the packet is put at the end of the input queue while waiting to be:
   a. checked  
   b. entered  
   c. read  
   d. interpret  
   ✅ **Answer: a**

9. Integrated Services is based on flow-based Quality of Service model designed for:
   a. CPU  
   b. Data Node  
   c. IP  
   d. Traffic Shaping  
   ✅ **Answer: c**

10. The token bucket can easily be implemented with a counter, initialized by:
    a. 0  
    b. 1  
    c. -1  
    d. -2  
    ✅ **Answer: a**

11. In Congestion, to define the maximum data rate of the traffic we use:
    a. Average Data Packet  
    b. Peak Data Rate  
    c. Packet Data Rate  
    d. Average Data Rate  
    ✅ **Answer: b**

12. In Congestion, the maximum burst size normally refers to the maximum length of time the traffic is generated at the:
    a. Average Rate  
    b. Packet Rate  
    c. Protocol Rate  
    d. Peak Rate  
    ✅ **Answer: d**

## **7. Further Readings**

- Achyut S Godbole and Atul Kahate, *Web Technologies*, Tata McGraw Hill.
- Andrew S. Tanenbaum, *Computer Networks*, Prentice Hall.
- Behrouz A. Forouzan, Sophia Chung Fegan, *Data Communications and Networking*, McGraw-Hill Companies.
- Douglas Comer, *Computer Networks and Internets with Internet Applications*, 4th Edition, Prentice Hall.
- Ferguson P., Huston G., *Quality of Service: Delivering QoS on the Internet and in Corporate Networks*, John Wiley & Sons, Inc., 1998.
- J. D. Spragins, *Telecommunications Protocols and Design*, Addison Wesley.
- McDysan, David E. and Darren L. Spohn, *ATM Theory and Applications*, McGraw-Hill Osborne Media, 1998.
- Nassar, Daniel J., *Ethernet and Token Ring Optimization*, iUniverse.com, 2000.
- Spurgeon, Charles E., *Ethernet, The Definitive Guide*, O’Reilly & Associates, 2000.
- William A Shay, *Understanding Communication and Networks*, 3rd Edition, Thomson Press.

--- 

Let me know if you need further clarification or additional study materials!

## Review & Practice Questions

1. What are the key differences between open-loop and closed-loop congestion control?
2. How does a bursty traffic profile differ from a steady-bitrate profile?
3. Why is the peak data rate an important parameter in network design?
4. What is the purpose of traffic shaping, and how does it help in congestion management?
5. List and briefly explain three QoS metrics.

---
