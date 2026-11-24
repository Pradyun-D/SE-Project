# Software Requirements Specification (SRS)
## Account Aggregator Integration Module
**Organization Scale:** FinTech Startup  
**Document Version:** 1.0.0  
**Status:** Approved for Development  

---

## 1. Executive Summary & Request Analysis

### 1.1 Document Overview
This Software Requirements Specification (SRS) defines the functional, security, privacy, and compliance requirements for the Account Aggregator (AA) integration module. The system enables customers to discover linked savings accounts using PAN and Date of Birth (DOB) under strict consent management, audit logging, and ephemeral data handling policies.

### 1.2 Request Analysis Summary
The initial system request requires:
> *"Users should link savings accounts and fetch financial statements using PAN and DOB with consent management, audit logging, and secure data retention."*

Based on rigorous regulatory evaluation against Reserve Bank of India (RBI) Master Directions, ReBIT guidelines, and Sahamati standards, the scope has been formalized into distinct, testable requirements, risk controls, and architectural decision frameworks.

---

## 2. Stakeholder Concerns & Assumptions

### 2.1 Stakeholder Concerns
* **Regulator (RBI / ReBIT):** Strict adherence to zero persistent storage of sensitive personal identifiable information (PII) such as PAN and DOB, mandatory inclusion of all statutory consent attributes, and verifiable audit trails.
* **Customer:** Transparent, friction-free consent management, absolute control over data sharing via real-time revocation, and assurance that core identity details are never permanently exposed or stored.
* **Security Architect / CISO:** Elimination of plain-text PII in application logs, cryptographic immutability of audit ledgers, and strict ephemeral memory isolation.
* **Compliance Officer / Legal:** Unambiguous alignment with RBI Master Directions on NBFC-Account Aggregators and Data Minimization policies.

### 2.2 System Assumptions
1. **Infrastructure:** The deployment environment operates within a secure cloud VPC adhering to strict network segregation between public-facing API gateways and internal banking connectors.
2. **External Dependencies:** Financial Information Providers (FIPs) and Financial Information Users (FIUs) maintain compliant, secure APIs supporting TLS 1.3 and mutual TLS (mTLS) where mandated by the AA ecosystem.
3. **Legacy Decoupling:** The legacy CRM storing historical customer KYC profiles is completely isolated from the AA discovery pipeline to prevent accidental PII persistence.

---

## 3. Detected Conflicts & Resolution Questions

During requirements analysis, potential structural conflicts were evaluated and resolved:
* **Conflict Resolution 1 (Logging vs. PII Minimization):** *Conflict:* Centralized logging frameworks naturally capture raw HTTP request payloads containing PAN and DOB. *Resolution:* Enforced mandatory upstream log interception and masking filters (FR-AA-002) prior to log persistence, satisfying auditability without violating zero-plaintext storage rules.
* **Conflict Resolution 2 (Batch vs. Event-Driven Propagation):** *Conflict:* Legacy systems rely on batch processing queues which conflict with real-time revocation mandates. *Resolution:* Mandated event-driven webhook architecture for immediate consent revocation propagation (FR-AA-004).

---

## 4. Functional & Non-Functional Requirements

| Requirement ID | Title | Category | Priority | Regulations / Citations | Risk Controls |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-AA-001** | PAN and DOB Secure Account Discovery | Functional | Must Have | ReBIT Guidelines - PAN/DOB Account Discovery (Page 2) | RC-SEC-01, RC-COMP-02 |
| **FR-AA-002** | Masked Logging for Discovery Identifiers | Security | Must Have | ReBIT Guidelines - PAN/DOB Account Discovery (Page 2) | RC-SEC-02 |
| **FR-AA-003** | Informed Consent Artefact Generation | Functional | Must Have | RBI Master Direction - NBFC-AA Directions 2016 (Page 10) | RC-COMP-03 |
| **FR-AA-004** | Customer Consent Revocation Mechanism | Functional | Must Have | RBI Master Direction (Page 10); Sahamati Guidelines (Page 17) | RC-OPS-01 |
| **FR-AA-005** | Consent Artefact Auditability & Verifiability | Non-Functional | Must Have | RBI Master Direction - NBFC-AA Directions 2016 (Page 10) | RC-AUD-01 |

---

## 5. User Stories, Use Cases, and Acceptance Criteria

### 5.1 FR-AA-001: PAN and DOB Secure Account Discovery
* **User Story:** As a customer, I want to use my PAN and Date of Birth to discover my linked savings accounts securely so that my sensitive identity details are not permanently stored by the Account Aggregator.
* **Use Case:**
  * **Actors:** Customer, Account Aggregator (AA), Financial Information Provider (FIP)
  * **Preconditions:** Customer has initiated the account linking flow; secure TLS 1.3 session established.
  * **Main Flow:**
    1. Customer enters PAN and DOB on the AA discovery screen.
    2. System transmits PAN and DOB securely to FIP for discovery.
    3. System receives discovered accounts list from FIP.
    4. System purges PAN and DOB from memory immediately after discovery request completion.
  * **Alternate Flows:** 2a. If FIP validation fails, system prompts customer to re-enter details without logging raw inputs.
  * **Postconditions:** Accounts are displayed to the customer; PAN and DOB are expunged from memory and storage.
* **Acceptance Criteria:**
  * Given a customer enters PAN and DOB for account discovery, When the discovery API call completes, Then the system must not write PAN or DOB in plain text to any database, cache, or log file.

### 5.2 FR-AA-002: Masked Logging for Discovery Identifiers
* **User Story:** As a security auditor, I want diagnostic logs to contain only masked representations of discovery identifiers so that sensitive user data is protected against insider threats.
* **Use Case:**
  * **Actors:** Application Logger, Security Monitoring System
  * **Preconditions:** Log generation hook is triggered during discovery API transaction.
  * **Main Flow:**
    1. Intercept incoming discovery request containing PAN and DOB.
    2. Apply masking function (`XXXXXX1234` for PAN, `XX/XX/YYYY` for DOB).
    3. Write masked payload to secure log store.
* **Acceptance Criteria:**
  * Given an audit log is generated during account discovery, When reviewing log files, Then PAN characters (except last 4) and full DOB must be replaced with masking characters.

### 5.3 FR-AA-003: Informed Consent Artefact Generation and Attributes
* **User Story:** As a customer, I want the consent screen to clearly display purpose, data categories, validity, and recipient details in user-friendly language so that I can make an informed granting decision.
* **Use Case:**
  * **Actors:** Customer, Account Aggregator Consent Engine, Financial Information User (FIU)
  * **Preconditions:** Accounts are successfully discovered.
  * **Main Flow:**
    1. System presents informed consent summary with FI category, data life, fetch type, and revocation callout.
    2. Customer reviews terms using user-friendly terminology and deliberate swipe-to-grant CTA.
    3. Customer approves consent.
    4. System generates cryptographically signed consent artefact containing all mandatory RBI attributes.
  * **Alternate Flows:** 2a. Customer declines consent; session terminates gracefully.
* **Acceptance Criteria:**
  * Given a customer reaches the final consent stage, When the consent artefact is generated, Then it must contain all mandatory attributes including customer identity, information type, purpose, recipient identity, notification URL, creation/expiry dates, and AA digital signature.

### 5.4 FR-AA-004: Customer Consent Revocation Mechanism
* **User Story:** As a customer, I want to revoke permission to share my bank account data at any time via the app so that I retain full control over my financial information.
* **Use Case:**
  * **Actors:** Customer, Account Aggregator, Financial Information Provider (FIP)
  * **Preconditions:** Customer has active granted consent artefacts.
  * **Main Flow:**
    1. Customer navigates to active permissions/consent management screen.
    2. Customer selects specific consent or data attribute to revoke.
    3. Customer confirms revocation action.
    4. System updates consent status to revoked, generates updated consent artefact, and notifies FIP immediately.
* **Acceptance Criteria:**
  * Given an active consent artefact, When a customer triggers consent revocation, Then the system must instantly mark the consent as revoked and successfully transmit the updated artefact to the FIP.

### 5.5 FR-AA-005: Consent Artefact Auditability and Verifiability
* **User Story:** As an external auditor, I want all consent artefacts to be immutably logged and verifiable so that I can validate regulatory compliance during periodic audits.
* **Use Case:**
  * **Actors:** Auditor, Consent Audit System
  * **Preconditions:** Consent lifecycle events (creation, use, revocation) have occurred.
  * **Main Flow:**
    1. Auditor requests verification report for a given consent ID.
    2. System retrieves cryptographic audit log chain.
    3. System verifies digital signatures and timestamps.
    4. System outputs verification report.
  * **Alternate Flows:** 3a. If signature mismatch occurs, system flags an integrity violation alert.
* **Acceptance Criteria:**
  * Given any consent artefact lifecycle transaction, When queried by an auditor, Then the system must provide verifiable cryptographic proof of its integrity, creation date, and usage history.

---

## 6. Traceability Matrix

| Req ID | Regulatory Source / Citation | Stakeholder | Risk Control | Acceptance Test ID |
| :--- | :--- | :--- | :--- | :--- |
| **FR-AA-001** | ReBIT Guidelines - PAN/DOB Account Discovery \| Page 2, clauses (b), (c), (d) | Regulator (RBI/ReBIT) | RC-SEC-01 | TC-AA-001 |
| **FR-AA-002** | ReBIT Guidelines - PAN/DOB Account Discovery \| Page 2, clause (b) | Security Architect | RC-SEC-02 | TC-AA-002 |
| **FR-AA-003** | RBI Master Direction - NBFC-AA Directions 2016 \| Page 10, clause 6.3 | Regulator (RBI) | RC-COMP-03 | TC-AA-003 |
| **FR-AA-004** | RBI Master Direction - NBFC-AA Directions 2016 \| Page 10, clause 6.6 | Customer | RC-OPS-01 | TC-AA-004 |
| **FR-AA-005** | RBI Master Direction - NBFC-AA Directions 2016 \| Page 10, clause 6.7 | Auditor | RC-AUD-01 | TC-AA-005 |

*Traceability Coverage:* **100%** (All functional and security requirements map cleanly to regulatory citations, risk controls, and validation test cases).

---

## 7. Quality Gaps & Clarification Questions

### 7.1 Identified Quality Gaps
* **Data Retention Timelines:** Specific data retention periods for fetched financial statements and audit logs require precise statutory alignment.
* **Intermittent Network Resiliency:** Fallback workflows and retry logic for network timeouts between the Account Aggregator and FIPs need formal definition.
* **Encryption Standards:** Cryptographic algorithms (e.g., AES-256-GCM) and Key Management Service (KMS) parameters for data-at-rest storage require explicit documentation.

### 7.2 Clarification Questions for Governance Review
1. What are the mandatory data retention periods for fetched financial statements and consent audit logs according to applicable regulatory guidelines?
2. How should the system handle intermittent timeouts or connection drops from FIPs during the financial statement fetch process?
3. What specific encryption standards (e.g., AES-256) and key management infrastructure must be used for storing financial statements at rest?

---

## 8. SDLC Decision Framework & Process Architecture

### 8.1 Comparison of Candidate Models

| Candidate Model | Suitability Score | Rationale & Trade-offs |
| :--- | :--- | :--- |
| **Agile-V-Model Hybrid with DevSecOps** | **95%** | **Selected.** Combines startup delivery velocity with rigorous V-Model compliance testing and automated DevSecOps PII controls. |
| **V-Model** | 82% | High regulatory alignment, but rigid and slow for startup product evolution and third-party API adaptations. |
| **DevSecOps** | 80% | Excellent for automated security pipelines, but lacks formal governance and legal sign-off workflows. |
| **Agile** | 65% | High velocity for UI/UX, but poses unacceptable compliance risks regarding zero-plaintext PII persistence. |
| **Waterfall** | 45% | Excessive lead times and zero adaptability; entirely unviable for modern fintech integration ecosystems. |

### 8.2 Selected Model Rationale
Given the startup context requiring rapid market entry alongside catastrophic regulatory risks (RBI/ReBIT compliance, zero plaintext PII storage, and immutable consent verification), the **Agile-V-Model Hybrid with Built-in DevSecOps** provides the ideal balance of iterative agility and rigorous compliance assurance.

---

## 9. Ordered SDLC Workflow Phases & Governance Gates

### Phase 1: Regulatory Requirements & Threat Modeling
* **Sequence:** 1
* **Objective:** Translate RBI Master Directions and ReBIT guidelines into precise architectural specifications, threat models, and compliance traceability matrices.
* **Activities:** Perform STRIDE threat modeling on account discovery/consent flows; define ephemeral memory handling specs; establish traceability matrix.
* **Roles:** Compliance Officer, Security Architect, Senior Software Architect, Product Manager.
* **Inputs:** RBI Master Direction - NBFC-AA Directions 2016, ReBIT Guidelines, Startup Objectives.
* **Deliverables:** Regulatory Traceability Matrix, Threat Model Report, Data Minimization Architecture Blueprint.
* **Security Controls:** RC-SEC-01 (Ephemeral memory), RC-COMP-02 (Zero plaintext storage design).
* **Compliance Checkpoints:** Legal and Compliance review of consent attribute definitions.
* **Validation Gates:** Architecture Review Board sign-off on decoupling legacy CRM from AA discovery pipeline.
* **Human Approval Checkpoint:** Compliance Officer sign-off on ephemeral data flow architecture review.

### Phase 2: Secure Design & Cryptographic Architecture
* **Sequence:** 2
* **Objective:** Design the cryptographic consent engine, immutable audit ledger, masked logging interceptors, and real-time revocation webhook architecture.
* **Activities:** Design cryptographic signing mechanism for informed consent artefacts; architect append-only immutable storage for audit trails (RC-AUD-01); implement log masking interceptors.
* **Roles:** Security Architect, Cryptography Specialist, Backend Lead.
* **Inputs:** Regulatory Traceability Matrix, Data Minimization Architecture Blueprint.
* **Deliverables:** Low-Level Design (LLD) Document, Cryptographic Key Management Plan, Log Sanitization Regex Specification.
* **Security Controls:** RC-SEC-02 (Masking PII in Application Logs), RC-AUD-01 (Immutable Consent Ledger design).
* **Compliance Checkpoints:** CISO review of cryptographic key lifecycles and hashing mechanisms.
* **Validation Gates:** Static Code Analysis configuration for PII detection.
* **Human Approval Checkpoint:** Security Lead review of log sanitization regex/code and CISO approval of audit trail immutability controls.

### Phase 3: Iterative Implementation & DevSecOps Integration
* **Sequence:** 3
* **Objective:** Implement functional modules within secure, automated CI/CD pipelines incorporating SAST, DAST, and secret scanning.
* **Activities:** Develop PAN/DOB secure account discovery service with strict in-memory purging; implement informed consent artefact generation; develop instant consent revocation webhook propagation; integrate automated SAST/container scanning.
* **Roles:** Full-Stack Developers, DevSecOps Engineer, QA Engineer.
* **Inputs:** Low-Level Design (LLD) Document, Cryptographic Key Management Plan.
* **Deliverables:** Microservice Source Code, CI/CD Pipeline Configurations, Unit and Integration Test Suites.
* **Security Controls:** RC-SEC-01 (Ephemeral memory code implementation), automated secret scanning.
* **Compliance Checkpoints:** Automated compliance gate verifying zero unmasked PII in test assertion logs.
* **Validation Gates:** 100% unit test coverage on core consent state machine and ephemeral memory purging routines.
* **Human Approval Checkpoint:** Operations Lead validation of webhook delivery success rates and Engineering Lead code review sign-off.

### Phase 4: Rigorous Verification, Penetration Testing & Audit
* **Sequence:** 4
* **Objective:** Execute comprehensive V-Model acceptance testing, cryptographic verification audits, penetration testing, and negative testing for PII leakage.
* **Activities:** Execute test cases TC-AA-001 through TC-AA-005; conduct third-party penetration testing focusing on memory dumps and log inspection; verify immutable consent ledger cryptographic chain integrity.
* **Roles:** QA Lead, External Auditor / Pen Tester, Compliance Officer.
* **Inputs:** Deployed Staging Environment, Acceptance Test Plan.
* **Deliverables:** Test Execution Report, Penetration Testing Vulnerability Assessment Report, Cryptographic Audit Verification Report.
* **Security Controls:** RC-COMP-02 (Zero plaintext storage verification testing), RC-COMP-03 (Mandatory Consent Attribute Verification).
* **Compliance Checkpoints:** Independent audit of consent artefact attributes against RBI Master Directions.
* **Validation Gates:** Zero critical or high security vulnerabilities; 100% pass rate on regulatory compliance test cases.
* **Human Approval Checkpoint:** Legal and Compliance sign-off on consent UI copy, artefact attributes, and final audit verification report.

### Phase 5: Production Deployment & Continuous Monitoring
* **Sequence:** 5
* **Objective:** Promote verified artefacts to production with strict segregation of duties, continuous security monitoring, and immutable log oversight.
* **Activities:** Execute blue-green production deployment with automated smoke tests; activate continuous security monitoring and real-time log anomaly alerts; establish ongoing compliance monitoring for revocation webhook latency.
* **Roles:** Release Manager, SRE / Infrastructure Engineer, Security Operations Center (SOC
