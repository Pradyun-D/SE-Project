# Software Requirements Specification & SDLC Framework
**Project:** Regulated FinTech Savings Account Linker & Statement Fetcher  
**Role:** Documentation Architect  
**Organization Scale:** Startup  
**Document Status:** Final / Baseline  

---

## 1. Executive Summary & Request Analysis Summary

This Software Requirements Specification (SRS) establishes the baseline requirements, quality parameters, compliance controls, and Software Development Life Cycle (SDLC) governance model for the Regulated FinTech savings account linking and statement fetching platform. 

The initial request specified that users should be able to link savings accounts and fetch financial statements using Permanent Account Number (PAN) and Date of Birth (DOB), supported by explicit consent management, comprehensive audit logging, and secure data retention mechanisms. Due to the high ambiguity and regulatory exposure inherent in processing Personally Identifiable Information (PII) and financial records, this document structures the requirements into enforceable engineering specifications while identifying critical quality gaps and resolution frameworks.

---

## 2. Stakeholder Concerns & Assumptions

### 2.1 Stakeholder Concerns
*   **End Users / Customers:** Concerned with the privacy, confidentiality, and security of their sensitive financial data and PII (PAN, DOB); desire a frictionless account linking experience and straightforward consent revocation.
*   **Compliance & Legal Officers:** Concerned with adherence to statutory data protection regulations, financial regulatory guidelines regarding statement retrieval, and verifiable audit trails.
*   **Engineering & Architecture:** Concerned with secure integration protocols (e.g., Account Aggregator frameworks), encryption standards, rate-limiting to prevent brute-force attacks on PII, and precise data retention/purging policies.
*   **Executive / Startup Leadership:** Concerned with time-to-market, risk mitigation against regulatory penalties, and maintaining robust security postures without inflating operational overhead.

### 2.2 Assumptions
1.  Third-party verification services (such as official Account Aggregators or KYC bureaus) are available and accessible via secure APIs for validating PAN and DOB.
2.  Users possess valid PAN and DOB credentials issued by official national registries.
3.  The underlying cloud infrastructure supports Advanced Encryption Standard (AES-256) at rest and Transport Layer Security (TLS 1.3) in transit.
4.  Startup operations will scale cloud resources dynamically to handle spikes in statement retrieval requests.

---

## 3. Detected Conflicts and Resolution Questions

*   *Conflict Status:* No direct logical contradictions were detected in the initial functional scope; however, severe **quality gaps** exist regarding regulatory boundaries, retention timelines, and consent lifecycles.
*   *Resolution Framework:* The following clarification questions must be formally addressed by product and legal stakeholders to close quality gaps prior to production deployment:
    1. **Data Retention:** What is the exact data retention period required for financial statements and audit logs under applicable statutory frameworks?
    2. **Regulatory Mapping:** Which specific regulatory frameworks (e.g., RBI Account Aggregator guidelines, DPDP Act, GDPR) govern this implementation?
    3. **Consent Revocation:** How should consent revocation impact previously fetched financial statements (immediate purge vs. retention for legal hold)?
    4. **Encryption Standards:** What are the exact cryptographic requirements for storing and processing PAN and DOB data elements?
    5. **Security / Rate-Limiting:** What is the maximum allowed failure rate and lockout policy for incorrect PAN/DOB verification attempts to prevent enumeration attacks?

---

## 4. Functional and Non-Functional Requirements

### 4.1 Functional Requirements
*   **REQ-001 (Requirement Overview):** Users shall link savings accounts and fetch financial statements using PAN and DOB, accompanied by consent management, audit logging, and secure data retention. *(Source: General Context)*
*   **REQ-002 (Identity Verification):** The system shall validate user-submitted PAN and DOB against authorized verification endpoints prior to initiating account discovery.
*   **REQ-003 (Consent Collection):** The system shall capture explicit, granular, and time-bound user consent prior to fetching financial statements or linking accounts.
*   **REQ-004 (Statement Retrieval):** The system shall retrieve financial statements via secure, authorized third-party APIs upon successful verification and active consent.

### 4.2 Non-Functional Requirements
*   **NFR-001 (Data Security):** All PII (including PAN and DOB) and financial statements shall be encrypted at rest using AES-256 and in transit using TLS 1.3.
*   **NFR-002 (Auditability):** Every action involving consent creation, consent revocation, account linking, and statement access shall generate an immutable audit log entry.
*   **NFR-003 (Availability & Performance):** Account linking and statement retrieval workflows shall complete within standard SLA thresholds (under 5 seconds for verification, under 30 seconds for bulk statement generation) with 99.9% uptime.

---

## 5. User Stories, Use Cases, and Acceptance Criteria

### 5.1 User Stories
*   **US-01 (Account Linking):** *As a bank customer, I want to link my savings account using my PAN and DOB so that I can easily consolidate and view my financial position within the app.*
*   **US-02 (Consent Management):** *As a privacy-conscious user, I want to review and revoke my consent for data access at any time so that I retain full control over my financial information.*

### 5.2 Use Cases
*   **UC-01: Link Savings Account & Fetch Statements**
    *   *Actor:* End User
    *   *Preconditions:* User is registered and authenticated on the platform.
    *   *Main Flow:*
        1. User enters PAN and DOB.
        2. System presents a detailed consent agreement detailing data usage.
        3. User provides explicit consent.
        4. System verifies credentials against the verification bureau.
        5. System queries connected financial institutions for savings accounts.
        6. User selects accounts to link and requests statements.
        7. System fetches statements, stores them securely, and logs the transaction.
    *   *Postconditions:* Account is linked, statements are available to the user, and an audit log is recorded.

### 5.3 Acceptance Criteria
*   **AC-001 (General):** Given the requirement, when implemented, then it is testable. *(Source: REQ-001)*
*   **AC-002 (Verification Failure):** Given an invalid PAN or DOB combination, when submitted, then the system rejects the input, logs the failed attempt, and restricts further attempts after 3 consecutive failures.
*   **AC-003 (Consent Revocation):** Given an active consent state, when the user triggers consent revocation, then data fetching ceases immediately and associated access tokens are invalidated.

---

## 6. Requirement-to-Source/Control/Test Traceability View

| Req ID | Title | Source / Citation | Security / Compliance Control | Test Case ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | Requirement Overview | General Context | AES-256 Encryption, TLS 1.3 | TC-001 (End-to-end integration test) | Baseline |
| **REQ-002** | Identity Verification | General Context | Rate-limiting, PII Masking | TC-002 (PAN/DOB validation test) | Baseline |
| **REQ-003** | Consent Collection | General Context | Immutable Audit Logging | TC-003 (Consent lifecycle test) | Baseline |
| **REQ-004** | Statement Retrieval | General Context | Secure Data Retention Policies | TC-004 (Statement fetch verification) | Baseline |

---

## 7. Quality Gaps and Clarification Summary

*   **Current Traceability Coverage:** 20.0% (Reflecting high ambiguity score of 0.85).
*   **Identified Gaps:**
    *   Specific error handling and rate-limiting thresholds for PAN/DOB failures.
    *   Exact data retention periods and automated purging protocols.
    *   Regulatory mapping (e.g., DPDP Act, RBI directives).
    *   Granular consent lifecycle workflows (revocation, renewal).
    *   Standardized integration protocols for Account Aggregators.

---

## 8. SDLC Decision Framework & Process Governance

### 8.1 Candidate Model Comparison

| Model Name | Suitability (%) | Rationale |
| :--- | :--- | :--- |
| **Agile-V-Model Hybrid** | **85%** | **Combines iterative delivery with formal verification and compliance gates.** (Selected) |
| **DevSecOps** | 78% | Strong continuous security and delivery controls, but requires mature automation pipelines. |
| **V-Model** | 74% | Strong traceability and verification discipline, but lacks agility for rapid startup feature iterations. |

### 8.2 Decision Rationale
The **Agile-V-Model Hybrid** has been selected as the primary SDLC model. For a regulated FinTech startup, this model provides the necessary flexibility to iterate rapidly on user experience (Agile) while enforcing rigid validation gates, security compliance checkpoints, and traceability (V-Model) required for handling sensitive PII and financial statements.

---

## 9. Selected SDLC Model: Agile-V-Model Hybrid Workflow

### 9.1 Ordered Phases & Activities
