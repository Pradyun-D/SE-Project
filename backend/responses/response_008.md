# Software Requirements Specification (SRS) & SDLC Blueprint
**Project:** Regulated FinTech Account Aggregator Integration  
**Organization Scale:** Medium  
**Document Architecture:** Documentation Architecture Office  

---

## 1. Executive Summary & Document Scope

This Software Requirements Specification defines the technical, functional, security, and compliance requirements for linking savings accounts and fetching financial statements using PAN, Date of Birth (DOB), and strict consent management mechanisms. 

Targeted at a medium-scale financial institution operating within a strictly regulated ecosystem, this project handles highly sensitive consumer financial data. Consequently, this document captures mandatory functional behaviors, quality gaps, derived Software Development Life Cycle (SDLC) parameters, and structured human approval checkpoints required to guarantee regulatory alignment and risk mitigation.

---

## 2. Requirements Baseline

The system requirements are derived from established regulatory guidelines, organizational policies, and industry design standards. Each requirement specifies its operational boundaries, risk controls, and validation criteria.

### Functional Requirements

*   **FR-AA-001: PAN and DOB Account Discovery Input Handling**
    *   **Category:** Functional | **Priority:** Must Have
    *   **Dimensions:** Business, Technical, Security, Privacy, Compliance
    *   **Description:** System must collect PAN and DOB strictly for the purpose of account discovery and prevent storage or plain-text logging of these sensitive fields.
    *   **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | Page 2]
    *   **Organisational Policies:** Data Minimisation and Zero-Retention Policy
    *   **Risk Controls:** Data Leakage Prevention, Regulatory Non-Compliance Penalty Avoidance
    *   **Legacy Constraints:** Legacy CRM systems logging payloads by default must be decoupled.
    *   **Human Approval Checkpoint:** Data Privacy Officer & Chief Information Security Officer (CISO)
    *   **Acceptance Criteria:** Given a user inputs PAN and DOB for account discovery, When the discovery payload is processed, Then PAN and DOB must not be persisted in any database or cache, and When logs are generated, Then PAN and DOB values must be completely masked or omitted.

*   **FR-AA-002: Consent Artefact Generation and Transparency Display**
    *   **Category:** Functional | **Priority:** Must Have
    *   **Dimensions:** Business, Compliance, Auditability, Technical
    *   **Description:** System must generate a valid electronic consent artefact containing identity of the customer, requested financial information, purpose, recipients, notification URLs, creation/expiry dates, and digital signature, presented transparently to the user.
    *   **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | Page 10]
    *   **Organisational Policies:** Informed Customer Consent Policy
    *   **Risk Controls:** Unauthorized Data Access Prevention, Consent Dispute Mitigation
    *   **Legacy Constraints:** Legacy front-ends lacking rich UI elements for consent metadata display.
    *   **Human Approval Checkpoint:** Compliance Head & Legal Counsel
    *   **Acceptance Criteria:** Given a user initiates statement fetching, When the consent screen is rendered, Then all mandatory attributes including purpose, data categories, validity period, and recipient details must be clearly displayed, and When consent is granted, Then an immutable digitally signed consent artefact must be created.

*   **FR-AA-003: Consent Revocation and Partial Revocation Mechanism**
    *   **Category:** Functional | **Priority:** Must Have
    *   **Dimensions:** Business, Privacy, Compliance, Technical
    *   **Description:** System must provide customers with an explicit functionality to revoke consent entirely or partially for specific parts of information, triggering updated consent dissemination to Financial Information Providers (FIPs).
    *   **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | Page 10]
    *   **Organisational Policies:** User Rights & Data Control Policy
    *   **Risk Controls:** Over-collection Risk, Regulatory Breach Risk
    *   **Legacy Constraints:** Batch-based consent propagation models requiring refactoring for real-time revocation.
    *   **Human Approval Checkpoint:** Product Head & Compliance Officer
    *   **Acceptance Criteria:** Given an active consent artefact, When a customer triggers consent revocation via the application UI, Then the system must immediately invalidate the artefact, generate a fresh consent artefact, share it with the FIP, and halt ongoing data fetches.

*   **FR-AA-004: Interactive Informed Consent UX with Positive Friction (Swipe CTA)**
    *   **Category:** Functional | **Priority:** Should Have
    *   **Dimensions:** Business, Technical, Availability
    *   **Description:** System must incorporate user-friendly terminology, red-flag indicators for unusual frequency/validity, and deliberate interaction design (such as swipe-to-grant) to ensure informed consent.
    *   **Regulations:** [Sahamati Customer Consent Design Guidelines | Page 34], [Sahamati Customer Consent Design Guidelines | Page 1]
    *   **Organisational Policies:** UX Accessibility and Transparency Guidelines
    *   **Risk Controls:** Dark Pattern Mitigation, Informed Consent Verification
    *   **Legacy Constraints:** Standard button-click components needing extension to support swipe gestures.
    *   **Human Approval Checkpoint:** UX Lead & Product Manager
    *   **Acceptance Criteria:** Given the final permission step of the consent flow, When unusual access frequencies are detected, Then a red-flag warning must be displayed, and When the user grants permission, Then a deliberate swipe action must be required to complete authorisation.

### Non-Functional Requirements

*   **NFR-AA-001: Auditable and Verifiable Electronic Consent Logging**
    *   **Category:** Auditability | **Priority:** Must Have
    *   **Dimensions:** Security, Auditability, Compliance
    *   **Description:** All electronic consent artefacts, access events, and revocation actions must be capable of being securely logged, audited, and verified against tampering.
    *   **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | Page 10]
    *   **Organisational Policies:** Information Security Audit and Logging Policy
    *   **Risk Controls:** Non-Repudiation Control, Tamper-evident Audit Trail
    *   **Legacy Constraints:** Centralised log servers requiring append-only write constraints.
    *   **Human Approval Checkpoint:** Head of Information Security
    *   **Acceptance Criteria:** Given any consent lifecycle event (creation, usage, modification, revocation), When the event occurs, Then it must be written to an immutable audit store with cryptographic signatures, and When audited, Then the audit trail must be fully verifiable.

---

## 3. Quality Analysis & Gaps

An evaluation of the requirements baseline indicates a current ambiguity score of **0.45**, reflecting several unaddressed operational and technical gaps that must be resolved prior to system implementation.

### Identified Missing Aspects
1. **Financial Statement Data Retention:** The retention duration and secure automated purging mechanisms for fetched financial statements are currently unspecified.
2. **Operational Resilience:** Error handling protocols, fallback logic, API timeouts, and retry mechanisms with Financial Information Providers (FIPs) are absent.
3. **Cryptographic Standards:** Specific cryptographic algorithms, key management architecture (e.g., HSM usage), and cipher standards for protecting data-at-rest and audit logs are undefined.

### Open Clarification Questions
* What is the exact regulatory or business retention period for the fetched financial statements, and how should secure purging be executed?
* What are the fallback and error handling protocols when a Financial Information Provider (FIP) is unreachable during account discovery or statement fetching?
* Which cryptographic standards (e.g., AES-256, RSA-2048, HSM-backed keys) must be used for protecting data at rest and cryptographic audit signatures?

---

## 4. Derived SDLC Factors & Model Selection

### Derived SDLC Factors
The project's architectural constraints, security risks, and regulatory mandates produce the following system-level factors:
*   **Requirement Stability:** High
*   **Regulatory Criticality:** High
*   **Security Risk:** High
*   **Project Complexity:** High
*   **System Size:** Medium
*   **Legacy System Dependence:** High
*   **Frequency of Expected Changes:** Medium
*   **Need for Continuous Delivery:** Medium
*   **Stakeholder Availability:** Medium
*   **Testing and Documentation Requirements:** Medium
*   **Budget and Schedule Constraints:** Medium
*   **Need for Formal Verification:** Medium
*   **Consequences of System Failure:** High

### Ranked SDLC Model Recommendations
Based on the deterministic factor analysis, the execution framework is ranked below:

1.  **V-Model** (Suitability: **95%**) â *Deterministic factor-based baseline.* Ideal due to high regulatory criticality, high failure consequences, and strong emphasis on formal verification and structured validation gates.
2.  **Spiral** (Suitability: **90%**) â *Deterministic factor-based baseline.* Suitable given high complexity and security risk, though heavier on overhead than the V-Model.
3.  **DevSecOps** (Suitability: **70%**) â *Deterministic factor-based baseline.* Provides robust security integration but tempered by legacy dependence and rigid regulatory upfront documentation needs.
4.  **Agile-V-Model Hybrid** (Suitability: **70%**) â *Deterministic factor-based baseline.* Balances structured compliance with iterative front-end UI enhancements.
5.  **Waterfall** (Suitability:
