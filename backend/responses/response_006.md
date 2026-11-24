# Software Requirements Specification (SRS) & Engineering Architecture
## Regulated FinTech Project: Savings Account Linking & Statement Fetching via Account Aggregator Framework

---

## 1. Document Control & Executive Summary

* **Project Scope:** Customer savings account linking, PAN/DOB-based account discovery, informed electronic consent management, immutable audit logging, and secure data retrieval.
* **Organization Scale:** Medium
* **Primary Regulatory Frameworks:** Reserve Bank of India (RBI) Master Directions, ReBIT Guidelines, Sahamati Design Standards.
* **Architecture Standard:** V-Model (Deterministic SDLC Ranking Baseline: 95%).

---

## 2. Software Requirements Specification (SRS)

### Requirement REQ-AA-001: Secure PAN and DOB Handling for Account Discovery
* **Category:** Security
* **Priority:** Must Have
* **Dimensions:** Security, Privacy, Compliance
* **Description:** Ensure PAN and DOB provided by the customer for account discovery are never stored or logged in plain text. They must be masked if logged and immediately purged post-discovery.
* **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]
* **Organisational Policies:** Data Minimization & Retention Policy
* **Risk Controls:** Zero Plaintext PII Storage, Automated Data Purging Routine
* **Legacy Constraints:** Legacy logging frameworks capturing unmasked request payloads
* **Acceptance Criteria:** Given a customer provides PAN and DOB for account discovery, When the discovery API executes, Then the PAN and DOB values are used exclusively for discovery, never stored in the database, and any operational logs mask the sensitive values entirely.
* **Human Approval Checkpoint:** Data Privacy Officer & Information Security Head

### Requirement REQ-AA-002: Informed Consent Artefact Generation and Management
* **Category:** Compliance
* **Priority:** Must Have
* **Dimensions:** Business, Compliance, Auditability
* **Description:** Capture explicit, informed electronic consent containing customer identity, requested financial information nature, purpose, recipient identity, notification URLs, and validity dates.
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Customer Consent Governance Policy
* **Risk Controls:** Digital Signature Verification, Consent Artefact Immutability
* **Legacy Constraints:** Monolithic consent storage without cryptographic verification
* **Acceptance Criteria:** Given a user initiates account linking and data sharing, When the consent screen is presented and agreed to, Then a digitally signed electronic consent artefact containing all mandatory attributes is successfully generated, logged, and verifiable.
* **Human Approval Checkpoint:** Compliance Officer & Legal Counsel

### Requirement REQ-AA-003: Consent Revocation and Granular Control
* **Category:** Functional
* **Priority:** Must Have
* **Dimensions:** Business, Privacy, Availability
* **Description:** Provide customers with an intuitive mechanism to revoke consent for information sharing at any time, including granular revocation for specific parts of information, triggering fresh consent updates to FIPs.
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Customer Rights & Data Control Policy
* **Risk Controls:** Real-time FIP Notification on Revocation, Immediate Data Access Termination
* **Legacy Constraints:** Batch-based consent status propagation systems
* **Acceptance Criteria:** Given an active consent artefact, When the user initiates revocation via the app, Then data access is immediately terminated, and a fresh consent artefact reflecting the revocation is shared with the relevant FIP.
* **Human Approval Checkpoint:** Head of Product & Customer Operations Lead

### Requirement REQ-AA-004: Transparent and Positive Friction Consent UI Design
* **Category:** Functional
* **Priority:** Should Have
* **Dimensions:** Business, Technical, Operational
* **Description:** Implement a user-friendly consent flow with plain-language terms, FIP date range visibility, security indicators, red-flag signals for unusual access frequencies, and deliberate swipe-to-grant interactions.
* **Regulations:** [Sahamati Customer Consent Design Guidelines | LOCATION: Page 34]
* **Organisational Policies:** UX Accessibility & Transparency Standard
* **Risk Controls:** Dark Pattern Prevention Checks, Informed Decision Verification
* **Legacy Constraints:** Legacy UI components lacking swipe interactions and anomaly highlighting
* **Acceptance Criteria:** Given a user reaches the final consent stage, When the terms and access frequency are displayed, Then any anomalous access frequency triggers a visible warning signal, and the user must perform a swipe gesture to provide deliberate permission.
* **Human Approval Checkpoint:** UX Director & Compliance Head

### Requirement REQ-AA-005: Audit Logging and Verification of Electronic Consent
* **Category:** Auditability
* **Priority:** Must Have
* **Dimensions:** Auditability, Security, Compliance
* **Description:** Maintain immutable, cryptographically verifiable audit logs for every creation, access, update, and revocation event associated with electronic consent artefacts.
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Information Security Audit & Logging Policy
* **Risk Controls:** Write-Once-Read-Many (WORM) Log Storage, Tamper-Evident Hash Chains
* **Legacy Constraints:** Fragmented application logs across microservices without centralized aggregation
* **Acceptance Criteria:** Given any lifecycle event of a consent artefact occurs, When the event is processed, Then an immutable audit log entry containing timestamp, actor, and artefact hash is securely recorded and verifiable upon audit.
* **Human Approval Checkpoint:** Chief Information Security Officer (CISO)

---

## 3. Quality Analysis & Gap Identification

An evaluation of the requirements reveals a completion score indicating strict regulatory alignment, but highlights specific gaps requiring engineering mitigation:

* **Ambiguity Score:** 0.35 (Low-Moderate)
* **Identified Quality Gaps:**
  1. *Retention Schedules:* Specific retention timelines for fetched financial statements and audit logs lack precise statutory duration indicators.
  2. *Cryptographic & Transit Standards:* Concrete technical protocols (e.g., AES-256-GCM, TLS 1.3) for statement encryption at rest and in transit are omitted from baseline functional definitions.
  3. *Fallback & Resilience:* Error handling mechanisms during Financial Information Provider (FIP) outages or PAN/DOB discovery failures require formal exception-routing specifications.
* **Clarification Resolutions:**
  * Statement and audit log retention must mirror regulatory guidelines (minimum 5 years or as mandated by RBI/PMLA rules).
  * Data in transit must use TLS 1.3; data at rest must use AES-256 encryption.
  * FIP unavailability must trigger circuit breaker patterns with exponential backoff and user-facing graceful degradation notifications.

---

## 4. Derived SDLC Factors & Methodology Selection

### Derived SDLC Factors
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

### Ranked SDLC Model Evaluation
1. **V-Model (95% Suitability):** Selected as the authoritative lifecycle model. Given the high regulatory criticality, security risk, and formal verification needs of an Account Aggregator implementation, the V-Model ensures rigid alignment between upstream requirements and rigorous testing phases.
2. **Spiral (90% Suitability):** Strong alternative due to risk management focus, but introduces scheduling overhead unnecessary for well-defined regulatory requirements.
3. **DevSecOps / Agile-V-Model Hybrid / Waterfall (70% Suitability):** Balanced compromises that either lack the necessary upfront verification rigor or introduce delivery friction.
4. **Agile (50% Suitability):** Inadequate for high-consequence FinTech systems requiring strict upfront compliance sign-offs and immutable verification gates.

---

## 5. Workflow Phases, Deliverables & Validation Gates

To execute the V-Model architecture successfully, the project follows structured workflow phases mapped to rigorous validation checkpoints:

### Phase 1: Requirements & Regulatory Definition
* **Deliverables:** Approved SRS Document, Regulatory Traceability Matrix (RTM).
* **Validation Gates:** Requirements baseline and evidence approved.
* **Human Approval Checkpoints:** Compliance Officer, Legal Counsel, Product Head.

### Phase 2: System & Security Architecture Design
* **Deliverables:** Threat Model, PII Flow Diagrams, Cryptographic Key Management Plan.
* **Validation Gates:** Security and privacy threat assessment approved.
* **Human Approval Checkpoints:** Chief Information Security Officer (CISO) & Data Privacy Officer.

### Phase 3: Construction & Implementation
* **Deliverables:** Microservice Codebases, Masked Logging Middleware, WORM Log Integrations.
* **Validation Gates:** Static Application Security Testing (SAST) & Peer Code Review Gates.
* **Human Approval Checkpoints:** Lead Architect & Engineering Manager.

### Phase 4: Verification, Compliance & Testing
* **Deliverables:** Unit Test Reports, Integration Test Suites, Consent Artefact Verification Logs, FIP Integration Harness.
* **Validation Gates:** Regulatory mapping and compliance test plan approved.
* **Human Approval Checkpoints:**
