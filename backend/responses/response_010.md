# Software Requirements Specification & SDLC Framework
## FinTech Project: User Account Statement Access with Consent and Audit Logging
**Organization Scale:** Medium  
**Document Status:** Final / Authorized  

---

## 1. Document Overview & Executive Summary

This Software Requirements Specification (SRS) defines the functional, security, and auditability requirements for implementing secure customer account statement viewing, consent management, and immutable audit logging within a regulated FinTech framework. 

Operating under rigorous compliance mandatesâincluding the **RBI Master Direction - NBFC-AA Directions 2016 & 2025**, the **MeitY Electronic Consent Framework v1.1**, and **Sahamati Design Guidelines**âthis project requires a structured, highly disciplined Software Development Life Cycle (SDLC). 

---

## 2. System Requirements Specification (SRS)

The requirements are categorized into functional, security, and auditability domains. Each entry outlines its priority, underlying regulations, organizational policies, risk controls, legacy constraints, evidence citations, and formal acceptance criteria.

### 2.1 Functional Requirements

#### FR-AA-001: Consent Record and History Viewer
* **Category:** Functional
* **Priority:** Must Have
* **Dimensions:** Business, Compliance, Auditability
* **Regulations:** `RBI Master Direction - NBFC-AA Directions 2016` (Citation: *RBI Master Direction - NBFC-AA Directions 2016 | Page 13*)
* **Organisational Policies:** Data Transparency and Customer Rights Policy v2.1
* **Risk Controls:** `RC-CONSENT-01`: Unauthorized access prevention via Multi-Factor Authentication (MFA)
* **Legacy Constraints:** Legacy consent database stores stringified payloads requiring schema migration for historical retrieval.
* **Human Approval Checkpoint:** Chief Compliance Officer (CCO) sign-off on customer-facing audit dashboard UI flow.
* **Acceptance Criteria:** Given a registered user navigates to the consent management section, when they request their consent history, then the system displays all active, withdrawn, and expired consents along with the associated FIU identifiers and data scopes.

#### FR-AA-002: Customer-Friendly Consent and Revocation Flow
* **Category:** Functional
* **Priority:** Must Have
* **Dimensions:** Business, Privacy, User-Experience
* **Regulations:** `Sahamati Customer Consent Design Guidelines` (Citation: *Sahamati Customer Consent Design Guidelines | Page 34*)
* **Organisational Policies:** Informed Consent UX Standard
* **Risk Controls:** `RC-CONSENT-02`: Mandatory explicit consent capture preventing implicit opt-ins
* **Legacy Constraints:** Monolithic frontend framework limits complex custom gesture integration (swipe-to-confirm).
* **Human Approval Checkpoint:** Head of Product and UX Lead approval on consent screen wireframes and terminology.
* **Acceptance Criteria:** Given a user is onboarding to share financial information with an FIU, when they review the consent request parameters (purpose, FI category, data life, and frequency), then the UI presents red flags for unusual parameters and requires a deliberate swipe action to grant or decline permission.

---

### 2.2 Security Requirements

#### SEC-AA-003: Secure Data Exchange and Storage Lifecycle Enforcement
* **Category:** Security
* **Priority:** Must Have
* **Dimensions:** Security, Privacy, Technical
* **Regulations:** 
  * `MeitY Electronic Consent Framework v1.1` (Citation: *MeitY Electronic Consent Framework v1.1 | Page 5*)
  * `RBI Master Direction - NBFC-AA Directions 2016`
* **Organisational Policies:** 
  * Information Security Encryption Standard v4.0
  * Data Retention and Purging Policy
* **Risk Controls:** 
  * `RC-SEC-01`: End-to-end payload encryption using digital signatures and TLS 1.3
  * `RC-SEC-02`: Automated data purging routines upon consent expiry
* **Legacy Constraints:** Legacy backend batch processor runs daily, potentially delaying immediate post-revocation data purging.
* **Human Approval Checkpoint:** Chief Information Security Officer (CISO) sign-off on cryptographic architecture and secure container specification.
* **Acceptance Criteria:** Given a data transfer session is initiated via a signed consent artifact, when data flows between FIP and FIU, then the transmission is encrypted using approved ciphers, and any stored consumer data is automatically purged upon reaching its defined data life limit.

---

### 2.3 Auditability Requirements

#### AUD-AA-004: Comprehensive Audit Logging of Consent and Data Flows
* **Category:** Auditability
* **Priority:** Must Have
* **Dimensions:** Auditability, Security, Compliance
* **Regulations:** 
  * `MeitY Electronic Consent Framework v1.1` (Citation: *MeitY Electronic Consent Framework v1.1 | Page 5*)
  * `RBI NBFC-AA Directions 2025` (Citation: *RBI NBFC-AA Directions 2025 | Page 13*)
* **Organisational Policies:** Enterprise Audit Trail and Logging Policy
* **Risk Controls:** `RC-AUDIT-01`: Write-once-read-many (WORM) storage for audit logs to prevent alteration
* **Legacy Constraints:** Decentralized log stores across microservices require centralized aggregation infrastructure.
* **Human Approval Checkpoint:** Head of Internal Audit and Data Protection Officer (DPO) validation of log retention and immutability controls.
* **Acceptance Criteria:** Given any consent artifact is generated, modified, or executed, when the event occurs, then a cryptographically signed audit log containing the timestamp, entity IDs, and signature service provider details is immutably recorded.

---

## 3. Quality Analysis & Gaps

An evaluation of the requirements baseline identified an ambiguity score of **0.35** and verified that the system specification is incomplete in specific operational areas. The following gaps must be managed via engineering assumptions and change control procedures:

* **Audit Retention Duration:** Specific retention period duration for audit logs and statement data copies must be bound to enterprise policy maximums during detailed design.
* **Batch Processor Latency:** Operational procedures and SLAs are required for handling legacy backend batch processor delays during immediate post-revocation data purging.
* **Gesture Fallback:** A fallback accessible UI interaction must be provided to replace the swipe-to-confirm gesture for users operating on unsupported legacy frontend devices.

---

## 4. Derived SDLC Analysis & Methodology Ranking

Due to high regulatory criticality, high security risk, and strict compliance needs, the deterministic SDLC analysis establishes the **V-Model** as the primary methodology.

### 4.1 Methodology Suitability Rankings
1. **V-Model:** `99%` â Deterministic factor-based baseline (Selected)
2. **Spiral:** `90%` â Deterministic factor-based baseline
3. **Agile-V-Model Hybrid:** `85%` â Deterministic factor-based baseline
4. **DevSecOps:** `70%` â Deterministic factor-based baseline
5. **Waterfall:** `70%` â Deterministic factor-based baseline
6. **Agile:** `50%` â Deterministic factor-based baseline

### 4.2 Derived SDLC Factors
* **Requirement Stability:** High
* **Regulatory Criticality:** High
* **Security Risk:** High
* **Project Complexity:** High
* **System Size:** Medium
* **Legacy System Dependence:** High
* **Frequency of Expected Changes:** Medium
* **Need for Continuous Delivery:** Medium
* **Stakeholder Availability:** Medium
* **Testing and Documentation Requirements:** Medium
* **Budget and Schedule Constraints:** Medium
* **Need for Formal Verification:** High
* **Consequences of System Failure:** High

---

## 5. Custom Workflow Phases

The project lifecycle is divided into six sequential, rigorously verified phases matching the V-Model architecture:

### Phase 1: Requirements Analysis and Regulatory Decomposition
* **Objective:** Deconstruct RBI Master Directions, MeitY Electronic Consent Framework, and Sahamati standards into rigorous functional and security baselines.
* **Activities:**
  * Requirements mapping against RBI NBFC-AA Directions 2016 and 2025.
  * Legacy constraint analysis (consent database schema migration, monolithic frontend gesture limits).
  * Formalize cryptographic specifications (TLS 1.3, digital signatures, WORM storage).
* **Deliverables:** System Requirements Specification (SRS), Regulatory Traceability Matrix (RTM), Legacy Integration Architecture Blueprint.

### Phase 2: High-Level Architecture and Security Design
* **Objective:** Establish end-to-end cryptographic exchange protocols, WORM audit logging infrastructure, and secure container specifications.
* **Activities:**
  * Design end-to-end payload encryption and secure container boundaries.
  * Architect decentralized-to-centralized log aggregation infrastructure.
  * Design UI/UX wireframes conforming to Sahamati customer consent design guidelines.
* **Deliverables:** High-Level Design (HLD) Document, Cryptographic Key Management Architecture, Security Threat Model (STRIDE analysis for RC-SEC-01 and RC-AUDIT-01).

### Phase 3: Detailed Design and Verification Preparation
* **Objective:** Specify component-level logic, database migration schemas, and comprehensive test plans mapped directly to acceptance criteria.
* **Activities:**
  * Detailed database schema design for historical consent retrieval.
  * Specification of automated data purging routines and batch processor
