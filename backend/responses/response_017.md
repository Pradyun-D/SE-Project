# Software Requirements Specification & SDLC Framework
**Project:** Regulated Account Aggregator FinTech Platform  
**Classification:** Restricted / Enterprise Regulatory Compliance  
**Document Version:** 1.0.0  

---

## 1. Executive Summary & Request Analysis

This document serves as the formal Software Requirements Specification (SRS) and Software Development Life Cycle (SDLC) blueprint for an enterprise-grade financial technology platform. The system enables customers to discover savings accounts via Financial Information Providers (FIPs) using Permanent Account Number (PAN) and Date of Birth (DOB), manage consent artifacts through positive friction workflows, fetch financial statements, and execute real-time consent revocations.

### Request Analysis Summary
* **Domain:** Regulated Open Banking & Account Aggregation (RBI, ReBIT, Sahamati guidelines).
* **Primary Capabilities:** Ephemeral PAN/DOB processing, secure masked logging, informed consent generation, positive friction UX (swipe-to-authorize & red-flag warnings), and instant consent revocation propagation.
* **Organizational Scale:** Enterprise (demanding high availability, immutable audit logging, strict data minimization, and multi-tier human approval checkpoints).

---

## 2. Stakeholder Concerns & Analysis

| Stakeholder | Primary Concerns | Mitigating Design / Control |
| :--- | :--- | :--- |
| **Customer** | Data privacy, transparency of shared data, prevention of accidental/malicious consent. | Ephemeral memory handling of PAN/DOB, red-flag anomaly warnings, swipe-to-authorize positive friction. |
| **Regulator (RBI/ReBIT)** | Strict adherence to data minimization, zero plaintext PII storage, mandatory consent attributes, and auditability. | RC-SEC-01, RC-COMP-01, WORM storage compliance, immutable audit logs. |
| **Security Architect** | Log injection, PII leakage in SIEM tools, unauthorized access to sensitive endpoints. | RC-SEC-05 (regex log scrubber), ephemeral memory boundaries, SIEM drop filters. |
| **Product Manager** | User adoption, smooth onboarding friction balance, rapid integration with external FIPs. | Agile-V-Model hybrid workflow allowing iterative UX refinement backed by rigid compliance gates. |
| **Operations / FIP** | Webhook availability, revocation propagation SLAs (<5s), queue retry resilience. | 99.9% FIP webhook SLA monitoring, automated exponential backoff retry queues. |

---

## 3. Assumptions & Constraints

1. **Ephemeral Processing Assumption:** Core banking systems and FIP interfaces accept tokenized discovery queries without persisting identity inputs on disk.
2. **Immutable Storage Constraint:** Consent databases must support Write-Once-Read-Many (WORM) storage mechanics to satisfy regulatory non-repudiation mandates.
3. **Network Constraints:** FIP inbound webhook handlers must maintain 99.9% uptime to receive real-time consent revocation notices.
4. **Data Minimization:** PAN and DOB are utilized exclusively in transit and ephemeral memory during discovery and are purged immediately post-response.

---

## 4. Detected Conflicts & Resolution Questions

* **Conflict Analysis:** No blocking architectural conflicts were detected between regulatory mandates (ReBIT/RBI) and enterprise security policies. Both enforce strict zero-plaintext PII storage and data minimization.
* **Open Clarification Questions:**
  1. What are the explicit data retention durations and automated purge schedules for fetched financial statements and audit logs?
  2. What specific file formats (JSON vs. XML) and cryptographic standards must be supported when fetching financial statements from FIPs?
  3. What are the exact event metadata requirements for audit logging to satisfy regulatory inspection mandates?

---

## 5. Functional & Non-Functional Requirements

### FR-DIS-001: PAN and DOB Account Discovery
* **Category:** Functional / Security
* **Priority:** Must Have
* **Description:** System shall use customer-provided PAN and DOB exclusively for discovering linked bank accounts via FIPs without storing these values.
* **Regulations:** ReBIT Guidelines - PAN/DOB Account Discovery Clause 2(c), 2(d)
* **Risk Controls:** `RC-SEC-01` (Ephemeral memory processing for PII), `RC-COMP-02` (Zero plaintext storage of PAN/DOB)
* **Acceptance Criteria:** Given a customer enters PAN and DOB, When the discovery API is executed, Then the FIP returns matching accounts, and When processing completes, Then PAN and DOB are completely purged from storage and logs.

### FR-SEC-002: Secure Masked Logging of Sensitive Discovery Inputs
* **Category:** Security / Auditability
* **Priority:** Must Have
* **Description:** System shall ensure PAN and DOB are never logged in plain text and are only logged in masked formats if audit or debugging demands traceability.
* **Regulations:** ReBIT Guidelines - PAN/DOB Account Discovery Clause 2(b)
* **Risk Controls:** `RC-SEC-05` (Regex-based log scrubber for PII interception)
* **Acceptance Criteria:** Given application processes PAN and DOB, When logs are generated, Then no plain text PAN or DOB strings exist in the log storage, and Only masked representations are present.

### FR-CON-003: Informed Consent Artefact Generation with Mandatory Attributes
* **Category:** Compliance / Business
* **Priority:** Must Have
* **Description:** System shall generate a comprehensive electronic consent artefact containing customer identity, financial info requested, purpose, recipients, notification URL, creation/expiry dates, and AA digital signature.
* **Regulations:** RBI Master Direction - NBFC-AA Directions 2016 Clause 6.3
* **Risk Controls:** `RC-COMP-01` (Digital signature integrity validation)
* **Acceptance Criteria:** Given a customer initiates data sharing, When consent is granted, Then a signed electronic consent artefact containing all 7 mandatory RBI attributes is successfully generated and logged.

### FR-UI-004: Positive Friction Swipe-to-Authorize and Red Flag Educational Warnings
* **Category:** Functional / Performance
* **Priority:** Must Have
* **Description:** System shall provide user-friendly terminology, red flag warnings for unusual data access frequencies, and a swipe-to-authorize CTA to ensure deliberate customer consent.
* **Regulations:** Sahamati Customer Consent Design Guidelines (Page 34, Page 1)
* **Risk Controls:** `RC-OPS-01` (UX friction validation against automated malicious consent scripts)
* **Acceptance Criteria:** Given permission frequency exceeds normal patterns, When consent screen loads, Then a red flag warning is displayed, and When the user swipes to authorize, Then the authorization payload is successfully transmitted.

### FR-REV-005: Consent Revocation and FIP Notification
* **Category:** Functional / Compliance
* **Priority:** Must Have
* **Description:** System shall provide customers a functionality to revoke consent to obtain information at any time (including partial or full revocation), and upon revocation, immediately share a fresh consent artefact with the FIP.
* **Regulations:** RBI Master Direction - NBFC-AA Directions 2016 Clause 6.6
* **Risk Controls:** `RC-COMP-03` (Revocation propagation SLA enforcement < 5 seconds)
* **Acceptance Criteria:** Given an active consent artefact, When the customer invokes revocation, Then the consent status is updated immediately, and A fresh consent artefact is successfully transmitted to the FIP.

---

## 6. User Stories & Use Cases

### User Story 1 (Discovery):
> *"As a customer, I want to discover my savings accounts using my PAN and DOB so that I can link them to the Account Aggregator securely."*
* **Use Case (UC-01):** Customer enters PAN/DOB in UI $\rightarrow$ AA transmits securely to FIP $\rightarrow$ FIP returns account list $\rightarrow$ AA displays accounts $\rightarrow$ PAN/DOB purged from memory.
* **Alternate Flow:** If discovery fails, display error message without exposing PAN/DOB values in logs.

### User Story 2 (Security Logging):
> *"As a security architect, I want PAN and DOB log entries to be masked so that unauthorized personnel cannot view sensitive PII in log aggregation systems."*
* **Use Case (UC-02):** Application captures discovery request $\rightarrow$ Log interceptor applies masking (`XXXXXX1234`) $\rightarrow$ Masked log written to SIEM.
* **Alternate Flow:** Unmasked string detected $\rightarrow$ Interceptor halts write and triggers security alert.

### User Story 3 (Consent):
> *"As a customer, I want to review all terms, data types, and validity periods before granting consent so that I maintain complete transparency and control over my data."*
* **Use Case (UC-03):** System displays informed consent screen $\rightarrow$ Customer reviews and executes swipe gesture $\rightarrow$ Digitally signed consent artifact generated.

### User Story 4 (UI Friction):
> *"As a customer, I want to be warned if an app requests unusual access frequencies and use a swipe gesture to authorize so that I am protected from accidental or malicious data sharing."*
* **Use Case (UC-04):** UI evaluates permissions $\rightarrow$ Anomaly detected (e.g., hourly frequency) $\rightarrow$ Red flag warning displayed $\rightarrow$ Swipe gesture triggers consent creation API.

### User Story 5 (Revocation):
> *"As a customer, I want to revoke consent at any time via my AA or FIU app so that data sharing stops immediately."*
* **Use Case (UC-05):** Customer selects 'Revoke Consent' $\rightarrow$ Central registry updates status to 'Revoked' $\rightarrow$ Fresh consent artifact generated and transmitted to FIP within 5-second SLA.

---

## 7. Requirement-to-Source / Control / Test Traceability Matrix

| Requirement ID | Regulatory Source Citation | Stakeholder | Risk Control | Acceptance Test ID | Human Approval Checkpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-DIS-001** | ReBIT Guidelines, Page 2, Sec 2(c), 2(d) | Regulator | `RC-SEC-01`<br>`RC-COMP-02` | `TC-DIS-001` | Compliance Officer review during quarterly PII audit. |
| **FR-SEC-002** | ReBIT Guidelines, Page 2, Sec 2(b) | Security Architect | `RC-SEC-05` | `TC-SEC-002` | CISO sign-off on SIEM log redaction rules. |
| **FR-CON-003** | RBI Master Direction, Page 10, Sec 6.3 | Regulator | `RC-COMP-01` | `TC-CON-003` | Legal & Compliance Head verification of consent payload. |
| **FR-UI-004** | Sahamati Guidelines, Pages 1 & 34 | Customer | `RC-OPS-01` | `TC-UI-004` | UX Lead and Product Manager approval of consent layout. |
| **FR-REV-005** | RBI Master Direction, Page 10, Sec 6.6 | Regulator | `RC-COMP-03` | `TC-REV-005` | Operations Manager review of failed revocation retry queues. |

---

## 8. SDLC Decision Framework & Model Comparison

### Candidate Models Evaluation
1. **Agile-V-Model Hybrid (Recommended - Score: 95%):** Combines upfront compliance engineering gates and V-Model traceability with Agile sprint delivery for complex UI and integration layers.
2. **V-Model (Score: 85%):** Strong on verification and compliance, but inflexible for modern API ecosystems and dynamic UX iteration.
3. **DevSecOps (Score: 80%):** Excellent for pipeline security and log scrubbing automation, but lacks standalone governance for formal banking sign-offs.
4. **Agile (Score: 45%):** Too fluid for WORM storage and zero-plaintext PII mandates where architecture must precede coding.
5. **Waterfall (Score: 40%):** Prohibitive delays for external partner integrations and webhook handling.

---

## 9. Selected SDLC Model: Agile-V-Model Hybrid

### Ordered Workflow Phases

#### Phase 1: Regulatory Requirements & Security Architecture
* **Objective:** Establish baseline security, data minimization policies, compliance traceability matrices, and cryptographic models for PAN/DOB ephemeral processing.
* **Activities:** Deconstruct regulatory guidelines into traceable controls; architect ephemeral memory boundaries (`RC-SEC-01`); design WORM consent schemas; specify regex log scrubbers (`RC-SEC-05`).
* **Roles:** Senior Software Architect, Security Architect, Legal & Compliance Head, Product Manager.
* **Inputs:** ReBIT Guidelines Clause 2(b,c,d), RBI Master Direction Clause 6.3/6.6, Sahamati UX Guidelines.
* **Deliverables:** System Security Architecture Document, Regulatory Traceability Matrix, Data Minimization Specification.
* **Security & Privacy Controls:** `RC-SEC-01`, `RC-COMP-01`.
* **Compliance Checkpoints:** Legal & Compliance Head review of consent payload schemas.
* **Validation Gates:** Architecture Threat Modeling (STRIDE) review for PII leakage vectors.
* **Human Approval Checkpoint:** **CISO and Legal & Compliance Head sign-off.**

#### Phase 2: Secure Core & Integration Design
* **Objective:** Design robust API contracts, FIP discovery channels, consent generation engines, and immutable audit logging mechanisms.
* **Activities:** Develop OpenAPI specs for AA/FIP integration; design log interception pipelines; establish consent revocation queue architecture; design swipe-to-authorize wireframes.
* **Roles:** Integration Architect, Backend Lead, UX Lead, Security Engineer.
* **Inputs:** System Security Architecture Document, Regulatory Traceability Matrix.
* **Deliverables:** API Interface Contracts, UI/UX Consent Flow Wireframes, Log Interceptor Specification.
* **Security & Privacy Controls:** `RC-SEC-05`, `RC-COMP-02`.
* **Compliance Checkpoints:** CISO sign-off on SIEM log redaction rules.
* **Validation Gates:** API Security Review & Contract Testing validation.
* **Human Approval Checkpoint:** **UX Lead and Product Manager approval of consent screen layout.**

#### Phase 3: Iterative Agile Sprint Development
* **Objective:** Build core discovery APIs, secure logging, consent generation, UI friction components, and revocation dispatchers in iterative sprints.
* **Activities:** Implement ephemeral PAN/DOB processing (`FR-DIS-001`); code log scrubber interceptors (`FR-SEC-002`); build consent artefact generator (`FR-CON-003`); develop swipe UI and anomaly warnings (`FR-UI-004`); implement revocation engine (`FR-REV-005`).
* **Roles:** Full Stack Developers, Frontend Engineers, DevSecOps Engineers, Scrum Master.
* **Inputs:** API Interface Contracts, UI/UX Wireframes, Log Interceptor Specification.
* **Deliverables:** Increment 1 (Discovery & Logging), Increment 2 (Consent & UI), Increment 3 (Revocation Dispatcher).
* **Security & Privacy Controls:** Automated SAST/Secret Scanning, `RC-SEC-01`.
* **Compliance Checkpoints:** Sprint review code walk-throughs focusing on PII handling.
* **Validation Gates:** Unit Test Coverage > 90%; automated static analysis zero-vulnerability gate.
* **Human Approval Checkpoint:** **Product Owner and Tech Lead sprint demo and code review sign-off.**

#### Phase 4: V-Model Rigorous Verification & Compliance Audit
* **Objective:** Execute comprehensive verification mapped directly to regulatory requirements, penetration testing, and compliance audits.
* **Activities:** Execute test cases `TC-DIS-001` through `TC-REV-005`; perform external penetration testing and vulnerability assessments.
* **Roles:** QA Engineers, Penetration Testers, Compliance Auditors, Security Architect.
* **Inputs:** Completed Software Increments, Regulatory Traceability Matrix.
* **Deliverables:** Comprehensive Test Execution Report, Penetration Testing & VA Report, Compliance Verification Sign-off Package.
* **Security & Privacy Controls:** `RC-OPS-01`, `RC-COMP-03`.
* **Compliance Checkpoints:** Compliance Officer review during quarterly PII handling audit.
* **Validation Gates:** End-to-end integration and regulatory test suite 100% pass rate; zero high/critical vulnerabilities.
* **Human Approval Checkpoint:** **Compliance Officer and CISO formal verification sign-off.**

#### Phase 5: Release, Deployment & Continuous Monitoring
* **Objective:** Deploy to production environment with strict deployment gates, activate SIEM log drop monitors, and establish continuous operational oversight.
* **Activities:** Deploy containerized microservices; configure production SIEM drop filters; establish 24/7 monitoring of FIP webhook availability; configure automated daily reviews of failed revocation retry queues.
* **Roles:** DevSecOps Engineers, SREs, Operations Manager, SOC.
* **Inputs:** Compliance Verification Sign-off Package, Production Release Candidate.
* **Deliverables:** Production Deployment Artefacts, Live SIEM & Log Scrubber Monitoring Dashboards, Operations Runbook.
* **Security & Privacy Controls:** `RC-SEC-05` active regex sink, WORM storage monitoring.
* **Compliance Checkpoints:** Post-deployment regulatory compliance verification scan.
* **Validation Gates:** Smoke test suite execution against production endpoints; webhook handshake verification with FIP partners.
* **Human Approval Checkpoint:** **Change Advisory Board (CAB) and Operations Manager final deployment authorization.**

---

## 10. Master Human Approval Checkpoints Summary

1. **Phase 1 Approval:** Chief Information Security Officer (CISO) and Legal & Compliance Head sign-off on Architecture and PII Policies.
2. **Phase 2 Approval:** UX Lead and Product Manager approval of consent screen layout and positive friction workflows.
3. **Phase 3 Approval:** Product Owner and Tech Lead sprint demo and code review sign-off.
4. **Phase 4 Approval:** Compliance Officer and CISO formal verification sign-off on test evidence and PII handling audit.
5. **Phase 5 Approval:** Change Advisory Board (CAB) and Operations Manager final deployment authorization.
