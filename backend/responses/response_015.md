# Software Requirements Specification & SDLC Framework
**Project:** Regulated FinTech Savings Account Linker & Statement Fetcher  
**Organization Scale:** Startup  
**Document Classification:** Internal / Regulatory Engineering  

---

## 1. Executive Summary & Request Analysis

### 1.1 Request Analysis Summary
This specification defines the functional, non-functional, security, and governance requirements for a regulated FinTech capability that enables users to link savings accounts and fetch financial statements. The baseline user journey relies on Primary Account Number (PAN) and Date of Birth (DOB) authentication, backed by explicit consent management, comprehensive audit logging, and secure data retention controls.

### 1.2 Extracted Requirement Baseline
* **REQ-001 (Requirement Overview):** Users should link savings accounts and fetch financial statements using PAN and DOB with consent management, audit logging, and secure data retention.
  * **Category:** Functional
  * **Priority:** Must Have
  * **Citation:** General Context
  * **Acceptance Criteria:** Given the requirement, When implemented, Then it is testable.

---

## 2. Stakeholder Concerns & Assumptions

### 2.1 Stakeholder Concerns
* **Compliance & Legal Officers:** Need unambiguous evidence of explicit user consent, strict adherence to regional data privacy laws (e.g., DPDP Act, RBI directives), and immutable audit trails for all data access.
* **Information Security Team:** Require military-grade encryption (in transit and at rest) for sensitive identifiers (PAN, DOB) and financial statements, alongside strict zero-trust access controls.
* **Engineering & Operations:** Need robust error handling and fallback workflows for third-party banking API failures or invalid credential entries, coupled with clear data retention and purge schedules.
* **End Users:** Demand a frictionless, transparent onboarding experience with immediate visibility into what data is shared, who accesses it, and how to revoke consent.

### 2.2 Assumptions
1. External banking networks or account aggregators are available via secure APIs for account discovery and statement retrieval.
2. Users possess valid PAN documents and verifiable DOB records matching institutional KYC databases.
3. The host cloud infrastructure provides cryptographic key management services (KMS) capable of satisfying regional regulatory encryption standards.

---

## 3. Quality Gaps, Conflicts & Clarification Questions

### 3.1 Quality Gaps
* **Ambiguity Score:** 0.85 (High ambiguity requiring rigorous boundary definition).
* **Missing Aspects:**
  * Specific consent mechanism and revocation workflow.
  * Data retention duration and secure deletion/purge policies for PAN, DOB, and financial statements.
  * Regulatory compliance scope (e.g., RBI, GDPR, DPDP Act).
  * Error handling for failed account linking and invalid PAN/DOB combinations.
  * Authentication and authorization mechanisms for accessing financial statements.
  * Audit log retention period, immutability requirements, and auditable events scope.

### 3.2 Detected Conflicts & Resolution Questions
* *Detected Conflicts:* None explicitly recorded in structural analysis; however, the high ambiguity score points toward latent friction between rapid startup feature delivery and rigid regulatory verification timelines.
* *Clarification Questions:*
  1. What is the exact user consent flow and how must consent revocation be handled by the system?
  2. How long must PAN, DOB, and fetched financial statements be retained, and what encryption standards are required at rest and in transit?
  3. Which specific regulatory frameworks (e.g., RBI guidelines, DPDP Act) govern the data handling and consent capture?
  4. What are the fallback mechanisms or error flows when account linking fails or external banking APIs are unreachable?
  5. What events must be recorded in the audit log, and who has access to view or export these logs?

---

## 4. Requirements Specification

### 4.1 Functional Requirements
* **FR-01 (Account Linking & Verification):** The system shall accept user PAN and DOB inputs to discover and link associated savings accounts via secure institutional integrations.
* **FR-02 (Statement Retrieval):** The system shall fetch financial statements for linked accounts upon explicit user request and active authorization.
* **FR-03 (Consent Capture & Revocation):** The system shall capture cryptographically verifiable, granular user consent prior to data fetching and provide an immediate mechanism for consent revocation.

### 4.2 Non-Functional Requirements
* **NFR-01 (Data Security & Cryptography):** All PAN, DOB, and financial statement data shall be encrypted in transit using TLS 1.3 and at rest using AES-256 with keys managed via an isolated KMS.
* **NFR-02 (Audit Immutability):** All security-relevant events, consent transactions, and data access requests shall be recorded in an append-only, tamper-evident audit log retained for the regulatory mandate period.
* **NFR-03 (System Availability & Performance):** Account linking and statement fetching requests shall handle API timeouts gracefully, returning structured error responses within 5 seconds under normal operational load.

---

## 5. User Stories, Use Cases & Acceptance Criteria

### 5.1 User Stories
* **US-01:** *As a bank customer, I want to link my savings account using my PAN and DOB so that I can securely share my financial standing without exposing raw banking passwords.*
* **US-02:** *As a privacy-conscious user, I want to review and revoke my consent at any time so that the platform stops accessing or retaining my financial data.*

### 5.2 Use Cases
* **UC-01: Secure Account Linking & Statement Fetch**
  * **Actor:** End User
  * **Preconditions:** User is authenticated on the platform.
  * **Main Flow:**
    1. User enters PAN and DOB.
    2. System presents explicit consent disclosure text.
    3. User grants consent.
    4. System queries external banking integration to link account and fetch statements.
    5. System stores data securely and logs the transaction.
  * **Alternative Flow (Error):** If PAN/DOB validation fails, system prompts user to verify credentials without exposing internal matching details.

### 5.3 Acceptance Criteria
* **AC-01 (Derived from REQ-001):** Given the requirement for account linking and statement fetching via PAN and DOB with consent management, audit logging, and secure data retention, When implemented, Then every operational pathway is fully testable via automated integration tests.

---

## 6. Requirement-to-Source/Control/Test Traceability View

| Req ID | Description | Source / Citation | Security Control | Test Case Ref |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | Account linking, PAN/DOB verification, statement fetch, consent, audit, retention | General Context | AES-256, TLS 1.3, Append-Only Audit Log | TC-FUNC-001, TC-SEC-001 |
| **FR-01** | PAN/DOB account discovery | Derived from REQ-001 | Credential Masking & Tokenization | TC-FUNC-002 |
| **FR-03** | Consent management & revocation | Derived from REQ-001 | Cryptographic Consent Ledger | TC-COMP-001 |
| **NFR-02** | Audit logging & immutability | Derived from REQ-001 | WORM Storage / Hash-Chained Logs | TC-AUDIT-001 |

*Traceability Coverage Score:* 0.1 (Baseline initialized; pending expansion post-clarification closure).

---

## 7. SDLC Framework & Governance Decision

### 7.1 Candidate Model Comparison
* **Agile-V-Model Hybrid (Recommended - 85% Suitability):** Combines iterative feature delivery with formal verification and compliance gates, ideal for regulated startups balancing speed and governance.
* **DevSecOps (78% Suitability):** Strong continuous security and delivery controls, though lighter on upfront formal verification milestones required for strict banking integration sign-offs.
* **V-Model (74% Suitability):** Excellent traceability and verification discipline, but overly rigid for early-stage startup velocity and rapid pivoting.

### 7.2 Decision Rationale
The **Agile-V-Model Hybrid** was selected as the primary software development lifecycle framework. This decision balances the startup need for rapid, iterative feature rollout with the rigorous verification, auditability, and compliance gates mandated by regulated financial ecosystems.

### 7.3 Custom Workflow Phases & Operational Structure

```
[Requirements & Baseline] ââ> [Iterative Agile Sprint] ââ> [Formal V-Model Verification] ââ> [Release Gate]
```

1. **Phase 1: Requirements Baseline & Threat Modeling**
   * *Activities:* Define functional scope, threat modeling (STRIDE), and compliance mapping.
   * *Roles:* Product Manager, Solution Architect, Compliance Officer.
   * *Inputs:* Business brief, regulatory guidelines.
   * *Deliverables:* Approved SRS, Threat Model.
2. **Phase 2: Iterative Engineering & DevSecOps Implementation**
   * *Activities:* Sprint-based development, automated unit/integration testing, static/dynamic code analysis (SAST/DAST).
   * *Roles:* Frontend/Backend Engineers, DevOps Engineers.
   * *Inputs:* Backlog items, architecture blueprints.
   * *Deliverables:* Incrementally testable microservices
