# &#x20;**HoneyShield NEXUS** <img width="1000" height="300" alt="image" src="https://github.com/user-attachments/assets/e181de0f-3c36-48ab-8207-05ca8ae2cb9f" />




#### &#x20;**Overview**



HoneyShield Nexus is an interactive deception-driven Cyber Range as a Service (CRaaS) simulation platform built using Python and Flask.

The platform simulates a realistic SSH intrusion lifecycle inside a controlled honeypot environment, allowing defenders, students, and researchers to observe attacker behavior, deception mechanisms, MITRE ATT\&CK technique mapping, IOC generation, and automated incident reporting.
HoneyShield Nexus is designed as a lightweight cyber range for cybersecurity training, attack simulation, and forensic analysis.







### &#x20;**Features**



1. Simulated Attack Chain
* &#x20;Reconnaissance (Port / Service Scan)
* &#x20;SSH Brute Force
* &#x20; Shell Access
* &#x20;Command Execution Simulation
* &#x20;Honeytoken Trigger
* &#x20;Automated Sinkhole / Containment



2 Honeypot Environment

* SSH terminal session
* &#x20;Deception-based credential baiting
* Controlled adversary interaction
* &#x20;Behavioral telemetry generation



3 Defensive Analytics

* \- Alert Queue
* \- Network State Monitoring
* \- MITRE ATT\&CK Technique Mapping
* \- Threat Intelligence Profiling
* \- IOC Forensic Artifact Generation



4\. Reporting

* \- Professional PDF Incident Report Export
* \- Human-readable forensic summary
* \- Threat actor classification
* \- Analyst review notes





#### 

#### **Tech Stack**

\- Python
\- Flask
\- HTML / CSS / JavaScript
\- Chart.js
\- ReportLab (PDF generation)





#### 

#### &#x20;**MITRE ATT\&CK Techniques Simulated**

\- T1595 – Active Scanning
\- T1110 – Brute Force
\- T1078 – Valid Accounts
\- T1083 – File and Directory Discovery
\- T1552 – Unsecured Credentials







#####  How to Run



Install dependencies:



pip install flask reportlab



Run:



python app.py



Open:



http://127.0.0.1:5000







## Architecture

```text
Attacker
   ↓
Recon Scan
   ↓
SSH Honeypot
   ↓
HoneyShell Session
   ↓
Honeytoken Trigger
   ↓
Detection Engine
   ↓
MITRE Mapping
   ↓
IOC + Threat Intel
   ↓
PDF Report Export
```
## Future Scope
- Analyst interaction controls
- Multi-scenario attack library
- Containerized network emulation
- SIEM integration
- Threat hunting dashboards

