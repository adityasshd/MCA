# Unit 12 Application layer – services and protocols

## Summary

| Topic               | Key Points                                                                 |
|--------------------|----------------------------------------------------------------------------|
| Telnet             | Virtual terminal service, uses client-server model, supports various modes |
| FTP                | File transfer protocol, uses two TCP connections, supports different data structures |
| E-mail             | Core internet service, includes composition, transfer, reporting, display, and disposition |
| POP3 vs IMAP3      | Pop3 downloads messages, IMAP manages messages on server                   |
| Concept                  | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| Download Requirement    | Must download to read                                                       |
| Partial Preview         | Can preview before full download                                           |
| Organisation            | Direct organisation allowed on the mail server                             |
| Backup Mechanism        | Multiple backups for recovery                                              |
| Editing                 | Local edits vs. online sync                                                 |
| Content Scan            | Allowed before upload                                                      |

---

## Keywords

- Telnet
- FTP
- E-mail
- POP3
- IMAP3
- DNS
- HTTP
- TCP
- UDP
- MIME
- SMTP

---

## Core Concepts & Topics

## Unit 12 Application layer – services and protocols

## Core Concepts & Topics

```markdown

## Overview
This study guide covers key concepts related to the **Application layer** of the OSI model, focusing on **services and protocols** such as **Telnet**, **FTP**, **E-mail**, **POP3**, **IMAP3**, and **DNS**. The aim is to provide a clear understanding of these protocols' roles, functions, and differences.

## 1. Telnet

## What is Telnet?
- **Definition**: A protocol that provides virtual terminal services using the **TCP/IP** suite.
- **Use Case**: Enables communication between devices on a network.
- **Model**: Operates under a **client-server model**.
  
## Telnet Commands

| Character | Decimal | Binary     | Meaning |
|----------|---------|------------|--------|
| WILL     | 251     | 11111011   | Offer to enable |
| WON'T   | 252     | 11111100   | Reject to enable |
| DO       | 253     | 11111101   | Approve to enable |
| DON'T    | 254     | 11111110   | Disapprove to enable |

## Telnet Operational Modes

| Mode         | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| Default Mode | Client echoes input locally, submits upon end of line                      |
| Character Mode | Each character is transmitted immediately                               |
| Line Mode    | Client handles line editing (echo, erase, etc.)                           |

## 2. File Transfer Protocol (FTP)

## Definition
- An **application-layer protocol** used to transfer files between **local and remote systems**.
- Runs on **TCP** and utilizes **two connections**:
  - **Control Connection**
  - **Data Connection**

## Control Connection
- Used to exchange **control information** (user credentials, commands).
- Listens on **Port 21**.

## Data Connection
- Transmits actual **file data**.
- Listens on **Port 20**.

## FTP Session Process

1. **Control Link Established**: Client connects to the server via Port 21.
2. **Commands Sent**: User issues commands (`USER`, `PASS`, `CWD`, `RETR`, etc.).
3. **Data Link Established**: Server opens a new connection (Port 20) to transfer data.
4. **Session Management**: Control link remains open throughout the session.

## FTP Data Structures

| Type              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| File Structure    | File is treated as a stream of bytes                                      |
| Record Structure  | Files are structured into records                                         |
| Page Structure    | Files are split into indexed pages                                        |

## Common FTP Commands & Responses

| Command  | Description                                 | Response Code |
|---------|---------------------------------------------|---------------|
| USER     | Specifies the user ID                        | 200            |
| PASS     | Provides the password                       | 200            |
| CWD      | Changes working directory                   | 200            |
| RMD      | Removes a directory                         | 200            |
| MKD      | Creates a directory                         | 200            |
| RETR     | Retrieves a file                            | 225            |
| STOR     | Stores a file                               | 225            |
| LIST     | Lists files in the current directory        | 225            |
| QUIT     | Terminates the session                      | 221            |

## 3. Email

## Overview
- A core internet service enabling **formatted message exchange** between users globally.
- Supports **text, images, audio, and video**.
- **Sender** and **Receiver** roles exist.

## Components of an Email System

| Component           | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| User Agent (UA)    | Interface for sending/receiving messages                                  |
| Message Transfer Agent (MTA) | Responsible for transferring messages across networks             |
| Mailbox            | Storage location for received emails                                     |
| Spool File         | Temporary storage for outgoing messages                                   |

## Email Services

| Service         | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| Composition      | Creating and formatting messages                                          |
| Transfer         | Sending messages from sender to receiver                                  |
| Reporting        | Notifications about message delivery status                                |
| Displaying       | Presenting messages in a user-friendly format                              |
| Disposition      | Actions taken by the receiver (save, delete, etc.)                         |

## 4. POP3 and IMAP3

## Definitions

- **POP3 (Post Office Protocol)**: Downloads messages from the server to the client.
- **IMAP (Internet Message Access Protocol)**: Allows browsing and managing messages on the server.

## Key Differences

| Feature                  | POP3                             | IMAP                             |
|--------------------------|----------------------------------|----------------------------------|
| Purpose                  | Download and delete messages     | Browse and manage messages       |
| Port Numbers             | 110 / 995 (SSL)                  | 143 / 993 (SSL)                  |
| Server-Side Storage     | No (messages deleted after retrieval) | Yes (messages remain on server) |
| Multi-Device Support     | Limited                          | Full support                     |
| Search Functionality     | Not supported                    | Supported                        |
| Offline Access          | Possible                         | Limited                          |

## Example Use Cases

- **POP3**: Ideal for users who want to store messages locally and not on the server.
- **IMAP**: Suitable for users requiring real-time access to messages from multiple devices.

## Self-Assessment
Complete the following questions to test your understanding:
1. Which protocol is used for secure email transmission?
2. In what mode does Telnet allow for full line editing?
3. What is the primary function of an MTA in the email system?

## Answers
1. **SMTP** (Simple Mail Transfer Protocol)
2. **Line Mode**
3. **Message Transfer Agent (MTA)** transfers emails from one system to another.

## 2. Domain Name System (DNS)

## Overview
- **Purpose**: Converts human-readable domain names into IP addresses.
- **Hierarchical Structure**:
  - Root name servers
  - Top-Level Domains (TLDs)
  - Authoritative name servers
- **Types of Domains**:
  1. Generic Domains: `.com`, `.edu`, `.mil`, `.org`, `.net`
  2. Country Code Domains: `.in`, `.us`, `.uk`
  3. Inverse Domains: IP to domain mapping

## DNS Hierarchy

| Level             | Function                                                                 |
|------------------|--------------------------------------------------------------------------|
| Root Name Server | Provides initial direction to TLD servers                                |
| TLD Server       | Manages high-level domains like `.com`, `.org`                           |
| Authoritative    | Contains specific IP address mappings for domains                       |

## DNS Records
- Stored in a **tree-like format**
- Includes **time-to-live (TTL)** values and other metadata

## Name Resolution Process

| Step               | Action                                                                 |
|--------------------|----------------------------------------------------------------------|
| Client Request     | Browser requests domain resolution                                   |
| Name Server Query  | Queries DNS to resolve domain name to IP address                      |
| IP Address Return | Returns IP address to client for further communication                |

## 3. World Wide Web (WWW)

## Overview
- **Definition**: A system of interlinked hypertext documents accessible via the Internet.
- **Launch**: Initiated by Tim Berners-Lee at CERN in 1989.
- **Key Components**:
  - **Web Server**: Hosts web pages
  - **HTML**: Defines document structure
  - **HTTP**: Transfers data between browser and server

## Features of WWW
| Feature                   | Description                                                                 |
|--------------------------|------------------------------------------------------------------------------|
| HyperText                | Uses markup language (HTML)                                                  |
| Cross-Platform           | Works across various operating systems                                       |
| Distributed              | No central control                                                           |
| Open Standards           | Based on open standards and open-source                                    |
| Dynamic & Interactive    | Supports real-time interaction                                               |
| Web 2.0                 | Emphasizes user-generated content and social media                          |

## Web Architecture

| Component              | Role                                                                 |
|------------------------|----------------------------------------------------------------------|
| Uniform Resource Locator (URL) | Identifies location of resources                                      |
| HTTP                    | Defines communication protocol between client and server              |
| HTML                    | Structures and formats web pages                                      |

## 4. Hypertext Transfer Protocol (HTTP)

## Overview
- **Definition**: Protocol for transmitting hypertext over the Internet.
- **Creator**: Tim Berners-Lee
- **Versions**:
  - **HTTP/0.9**: Initial version (1991)
  - **HTTP/1.0**: Introduced in 1996 (RFC 1945)
  - **HTTP/1.1**: Updated in 1997 (RFC 2068), later revised in 1999 (RFC 2616)
  - **HTTP/2**: Released in 2015 (RFC 7540)
  - **HTTP/3**: Based on QUIC protocol (Google developed)

## Characteristics of HTTP
| Feature               | Description                                                                 |
|----------------------|------------------------------------------------------------------------------|
| IP-Based Communication | Transmits data between client and server                                    |
| Stateless             | No persistent session between client and server                            |
| Connection-Less      | No memory of previous interactions                                         |
| Client-Server Model   | Client makes request, server responds                                      |

## How HTTP Works

| Step                         | Description                                                                 |
|------------------------------|------------------------------------------------------------------------------|
| User Input                   | Enters URL in browser                                                     |
| DNS Lookup                   | Resolves domain name to IP address                                         |
| HTTP Request                 | Browser sends request to server                                            |
| Server Response              | Server processes request and sends back data                               |
| Connection Closure          | Connection ends after data transfer                                        |

## Advantages
- **Versatile Data Support**: Supports text, images, videos, etc.
- **Easy Integration**: Simple to implement and integrate with other services
- **Scalable Architecture**: Designed for large-scale usage

## Final Summary Table

| Topic                     | Main Focus                                                                 |
|--------------------------|----------------------------------------------------------------------------|
| Email Systems            | Access, organisation, backup, and handling mechanisms                      |
| DNS                      | Conversion of domain names to IP addresses, hierarchy, and resolution     |
| WWW                      | Structure, components (HTML, HTTP), features, and architecture            |
| HTTP                     | Definition, versions, characteristics, and working mechanism              |

```

## Overview
This study guide covers key concepts related to the application layer of networking including HTTP, DNS, FTP, Email protocols, and others. The goal is to provide a structured understanding of how these services operate within the context of the Internet and network communications.

## 1. Hypertext Transfer Protocol (HTTP)

## Advantages
| Advantage | Description |
|----------|-------------|
| Efficient Connection Management | Fewer connections mean minimal usage of memory and CPU. |
| Reduced Network Congestion | Fewer TCP connections lead to less network congestion. |
| Low Latency | Handshaking occurs once per session, reducing future request overhead. |
| Request/Response Pipelining | HTTP supports pipelining to enhance performance. |

## Disadvantages
| Disadvantage | Description |
|-------------|-------------|
| High Power Consumption | Requires significant energy due to constant communication. |
| Insecurity | No built-in encryption; requires HTTPS for security. |
| Not Mobile-Friendly | Excessively chatty nature makes it unsuitable for mobile devices. |
| Limited Data Exchange | Insecure nature limits true data exchange capabilities. |
| Server Lockout | Server waits for complete data before freeing up the connection. |

## 2. Domain Name System (DNS)

- **Function**: Translates human-readable domain names into IP addresses.
- **Structure**:
  - Hierarchical naming system.
  - Global distribution of DNS servers.
- **Process**:
  - Resolver converts domain names to IP addresses using recursive queries.

## 3. HTTP vs HTTPS

| Feature         | HTTP                         | HTTPS                        |
|----------------|------------------------------|------------------------------|
| Security        | No encryption                | Uses TLS for encryption      |
| Port            | Default port 80              | Default port 443             |
| Usage           | General web traffic          | Secure transactions          |

## 4. File Transfer Protocol (FTP)

- **Description**: Standard protocol for file transfers between client and server.
- **Architecture**:
  - Client-server model.
  - Two separate connections: control and data.
- **Modes**:
  - Stream mode (default).
  - Block mode.
  - Compressed mode.

## 5. Electronic Mail (Email)

- **Components**:
  - User Agent (Mail Client)
  - Message Transfer Agent (MTA)
  - Message Store
- **Protocols**:
  - **POP3**: Retrieves emails from the server.
  - **IMAP**: Allows users to manage emails on the server.

## 6. World Wide Web (WWW)

- **Definition**: Information system where documents are accessed through URLs.
- **Features**:
  - Identified by Uniform Resource Locators (URLs).
  - Connected via hyperlinks.
  - Built using HyperText Markup Language (HTML).

## 7. Common Telnet Commands

| Command | Description |
|--------|-------------|
| open   | Establishes a connection to a remote host |
| close  | Closes the current connection |
| quit   | Terminates the Telnet session |

## 8. Review Questions Summary

| Question Number | Topic | Answer |
|----------------|-------|--------|
| 1              | What is FTTP? | Typo likely intended to refer to FTP |
| 2              | Advantages and Disadvantages of HTTP | Refer to the section "Advantages" and "Disadvantages" |
| 3              | Components and Features of WWW | Includes URL, HTML, hyperlinks |
| 4              | Most Commonly Used Telnet Commands | open, close, quit |
| 5              | Explain E-mail and its Components | Sender, recipient, subject, body, attachments |
| 6              | What is DNS? | Explains the process of translating domain names to IP addresses |
| 7              | Hierarchy of DNS | Root, Top-Level Domains (TLD), Second-Level Domains (SLD), Subdomains |
| 8              | Difference Between POP3 and IMAP | POP3 downloads emails; IMAP allows managing emails on the server |

## 9. Self-Assessment Answers

| Question Number | Answer |
|----------------|--------|
| 1              | a. Persistent |
| 2              | a. First |
| 3              | a. Request line |
| 4              | b. Generates on demand by a program or a request from browser |
| 5              | d. All of the mentioned |
| 6              | b. File Transfer Protocol |
| 7              | a. Stream mode |
| 8              | d. Paper |
| 9              | b. DO |
| 10             | c. TCP |
| 11             | c. WhatsApp |
| 12             | c. TCP port number 23 |

## Review & Practice Questions

1. Explain the purpose of Telnet and its operational modes.
2. How does FTP differ from HTTP in terms of operation?
3. Describe the difference between POP3 and IMAP.
4. What role does the SMTP play in the email process?

---
