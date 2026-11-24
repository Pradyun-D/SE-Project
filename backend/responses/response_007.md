# Software Requirements Specification (SRS) & SDLC Blueprint: Regulated Account Aggregator Project

## 1. Executive Summary & Document Overview

This Software Requirements Specification (SRS) governs the engineering, compliance, and governance lifecycle for the medium-scale Regulated FinTech Account Aggregator initiative. The core functionality enables customers to link savings accounts and fetch financial statements securely using Permanent Account Number (PAN) and Date of Birth (DOB), underpinned by strict consent management, immutable audit logging, and zero-persistence data retention policies.

Given the high regulatory criticality and severe consequences of non-compliance, this document merges business needs, regulatory constraints, technical functional requirements, quality gaps, and a deterministic Software Development Life Cycle (SDLC) strategy.

---

## 2. Derived SDLC Factors & Model Ranking

The project profile exhibits high regulatory oversight, stringent privacy constraints, and complex legacy touchpoints. The deterministic SDLC ranking model establishes the baseline execution framework.

### 2.1 Derived SDLC Factors
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
* **Need for Formal Verification:** Medium
* **Consequences of System Failure:** High

### 2.2 Ranked SDLC Model Suitability
1. **V-Model (95% Suitability):** Selected as the primary execution framework due to its rigid verification and validation phases mapped directly against regulatory specifications.
2. **Spiral (90% Suitability):** Highly suitable for risk-driven iterative mitigation of complex legacy integration hurdles.
3. **DevSecOps (70% Suitability):** Applicable for automated pipeline security gates, though secondary to formal V-Model verification requirements.
4. **Agile-V-Model Hybrid (70% Suitability):** Balances structured regulatory sign-offs with iterative development sprints.
5. **Waterfall (70% Suitability):** Provides rigid sequential controls but lacks flexibility for complex cryptographic and UI consent refinements.
6. **Agile (50% Suitability):** Least suitable as a standalone model due to insufficient formal verification gates required by banking regulators.

---

## 3. Functional Requirements

The system must satisfy strict statutory frameworks, including ReBIT Guidelines, RBI Master Directions, and Sahamati Customer Consent Design Guidelines.

### FR-AA-001: PAN and DOB Masked Logging During Account Discovery
* **Category:** Functional | **Priority:** Must Have
* **Description:** Ensure that PAN and DOB inputs provided by customers during the account discovery process are never logged in plain text. Any logging required for troubleshooting or auditing must store these values exclusively in a securely masked format.
* **Dimensions:** Security, Privacy, Compliance, Auditability
* **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]
* **Organisational Policies:** Data Minimization and Masking Policy
* **Risk Controls:** PII Exposure Prevention Control, Secure Log Management Protocol
* **Legacy Constraints:** Legacy log aggregators that ingest raw request payloads
* **Evidence & Citation:** `[ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]`
* **Human Approval Checkpoint:** Data Privacy Officer and Chief Information Security Officer (CISO)
* **Acceptance Criteria:** Given a user inputs PAN and DOB for account discovery, When the transaction is logged by the application, Then PAN and DOB must be masked (e.g., ABCDE****F, DD/MM/****) in all log sinks.

### FR-AA-002: Restriction of PAN and DOB Usage to Account Discovery Exclusively
* **Category:** Functional | **Priority:** Must Have
* **Description:** Enforce strict system boundaries to ensure that customer PAN and DOB values collected during the discovery phase are used solely for account discovery purposes and not repurposed for profiling, marketing, or secondary processing.
* **Dimensions:** Business, Privacy, Compliance
* **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]
* **Organisational Policies:** Acceptable Data Usage Policy
* **Risk Controls:** Purpose Limitation Access Control
* **Legacy Constraints:** Monolithic user profile databases sharing records across domains
* **Evidence & Citation:** `[ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]`
* **Human Approval Checkpoint:** Compliance Head
* **Acceptance Criteria:** Given PAN and DOB have been successfully utilized for account discovery, When downstream services or analytics engines attempt to query these attributes, Then access must be denied and flagged as a policy violation.

### FR-AA-003: Prohibition of PAN and DOB Storage
* **Category:** Functional | **Priority:** Must Have
* **Description:** Account Aggregators (AAs) and Financial Information Providers (FIPs) must not persist or store PAN and DOB values provided by the customer for the account discovery process.
* **Dimensions:** Security, Privacy, Compliance
* **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]
* **Organisational Policies:** Zero-Persistence PII Policy
* **Risk Controls:** Ephemeral Data Processing Control, Database Persistence Blocking
* **Legacy Constraints:** Default database transaction logging capturing input request bodies
* **Evidence & Citation:** `[ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]`
* **Human Approval Checkpoint:** Chief Privacy Officer
* **Acceptance Criteria:** Given a customer submits PAN and DOB for account discovery, When the discovery API response is returned, Then the database and caches must contain no persistent record of the raw PAN or DOB values.

### FR-AA-004: Transparent and Customer-Friendly Informed Consent Flow
* **Category:** Functional | **Priority:** Must Have
* **Description:** Implement a consent UI and backend flow that clearly displays purpose, FI category, accounts overview, information requested, data life, fetch type, and revocation details using user-friendly terminology, complete with positive friction (swipe-to-grant) and anomaly red flags.
* **Dimensions:** Business, Technical, Compliance
* **Regulations:** Sahamati Customer Consent Design Guidelines, RBI Master Direction - NBFC-AA Directions 2016
* **Organisational Policies:** Customer Transparency & UX Standard
* **Risk Controls:** Informed Consent Verification Control
* **Legacy Constraints:** Legacy UI components lacking swipe-to-grant or dynamic warning flags
* **Evidence & Citation:** `[Sahamati Customer Consent Design Guidelines | LOCATION: Page 34]`
* **Human Approval Checkpoint:** UX Lead and Product Manager
* **Acceptance Criteria:** Given a user reaches the consent review screen, When they view the permissions, Then the app must clearly display the data requested, frequency, date range, red flag warnings for unusual settings, and require a swipe action to authorize.

### FR-AA-005: Mandatory Electronic Consent Artefact Attributes and Revocation
* **Category:** Functional | **Priority:** Must Have
* **Description:** Generate electronic consent artefacts containing customer identity, nature of information, purpose, recipient identity, notification URL, creation/expiry dates, and digital signatures. Provide customers with a functionality to revoke consent entirely or partially at any time.
* **Dimensions:** Technical, Compliance, Auditability
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Consent Management Lifecycle Policy
* **Risk Controls:** Consent Artefact Integrity Check, Revocation Propagation Control
* **Legacy Constraints:** Batch-based consent propagation mechanisms
* **Evidence & Citation:** `[RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]`
* **Human Approval Checkpoint:** Compliance Officer and Legal Counsel
* **Acceptance Criteria:** Given a valid consent is established or revoked, When the action occurs, Then an electronic consent artefact must be generated or updated, capable of being logged, audited, verified, and immediately shared with the FIP upon revocation.

---

## 4. Quality Gaps & Technical Clarifications

The initial quality assessment highlights an incompleteness score with an ambiguity rating of `0.45`. The following gaps require strict engineering mitigation prior to deployment:

1. **Data Retention & Deletion:** Precise retention schedules and automated purging mechanisms for fetched financial statements and audit logs must be codified.
2. **Cryptographic Standards:** Robust encryption protocols (e.g., AES-256 at rest, TLS 1.3 in transit) must govern all financial statement handling.
3. **Brute-Force Mitigations:** Rate-limiting controls and account lockout rules must be instituted for repeated failed PAN/DOB discovery attempts.

---

## 5. Custom Workflow Phases (V-Model Execution)

* **Phase 1: Requirements Analysis & Regulatory Traceability**  
  Analyze statutory, regulatory (ReBIT, RBI Master Directions, Sahamati guidelines), and functional specifications. Establish traceability matrices linking PAN/DOB handling, zero-persistence rules, and consent management features to risk controls.
* **Phase 2: Architectural & Security Design**  
  Design system boundaries, data flow architectures, ephemeral processing handlers, masking components, and cryptographic consent artefact schemas. Integrate legacy isolation layers.
* **Phase 3: Detailed Design & Threat Modeling**  
  Specify component-level logic, data minimization rules
