# Software Requirements Specification & SDLC Framework
**Project:** Account Aggregator Framework â Savings Account Linking & Statement Fetching  
**Organization Scale:** Enterprise  
**Document Class:** Regulated FinTech Technical & Compliance Architecture  

---

## 1. Executive Summary & Scope

This Software Requirements Specification (SRS) establishes the technical, security, and compliance baseline for integrating savings account linking and financial statement fetching via PAN and DOB, backed by consent management, immutable audit logging, and secure data retention. Designed for an enterprise scale FinTech deployment, this document synthesizes regulatory mandates, organizational policies, and risk controls into structured software requirements.

---

## 2. System Requirements

### 2.1 REQ-AA-001: Secure PAN and DOB Handling for Account Discovery
* **Category:** Security | **Priority:** Must Have
* **Dimensions:** Security, Privacy, Compliance, Technical
* **Description:** PAN and DOB values provided by the customer for account discovery must not be stored or logged in plain text. They must be strictly ephemeral, used solely for the account discovery process, and securely masked if any operational logging is required.
* **Regulations:** [ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]
* **Organisational Policies:** Zero-Persistence PII Policy
* **Risk Controls:** PII Leakage Prevention, Cryptographic Masking
* **Legacy Constraints:** Legacy core systems caching raw payload requests
* **Evidence & Citation:** `[ReBIT Guidelines - PAN/DOB Account Discovery | LOCATION: Page 2]`
* **Human Approval Checkpoint:** Data Privacy Officer sign-off on discovery logging and zero-persistence architecture review.
* **Acceptance Criteria:** Given a customer inputs PAN and DOB for account discovery, When the discovery API processes the request, Then the raw PAN and DOB values are purged from memory immediately after execution, and Any logs generated contain only masked representations (e.g., ABCDE****F, YYYY).

### 2.2 REQ-AA-002: Informed Consent Artefact Generation and Attribute Validation
* **Category:** Functional | **Priority:** Must Have
* **Dimensions:** Business, Compliance, Technical, Auditability
* **Description:** Generate electronic consent artefacts containing customer identity, financial info requested, purpose, recipients, notification URLs, validity dates, and digital signatures. Ensure transparent display of terms in user-friendly terminology prior to consent grant.
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Standard Consent Management Policy
* **Risk Controls:** Unauthorized Data Access Prevention, Non-Repudiation Controls
* **Legacy Constraints:** Monolithic consent stores requiring schema update for modern metadata
* **Evidence & Citation:** `[RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]`, `[Sahamati Customer Consent Design Guidelines | LOCATION: Page 34]`
* **Human Approval Checkpoint:** Compliance Head approval of the electronic consent artefact schema and legal wording.
* **Acceptance Criteria:** Given a user initiates account linking and data sharing, When the consent artefact is created, Then it includes all mandatory statutory attributes (identity, purpose, recipient, validity, digital signature) and is logged, auditable, and verifiable.

### 2.3 REQ-AA-003: Customer Consent Revocation and Granular Control
* **Category:** Functional | **Priority:** Must Have
* **Dimensions:** Business, Privacy, Operational, Compliance
* **Description:** Provide customers with an intuitive, accessible mechanism to revoke consent at any timeâincluding partial revocation for specific information types or accountsâtriggering immediate notification and fresh consent distribution to Financial Information Providers (FIPs).
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Customer Data Rights Policy
* **Risk Controls:** Over-sharing Risk Mitigation, Automated Revocation Propagation
* **Legacy Constraints:** Batch-based downstream notification pipelines
* **Evidence & Citation:** `[RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]`, `[Sahamati Customer Consent Design Guidelines | LOCATION: Page 1]`
* **Human Approval Checkpoint:** Operations Lead validation of real-time revocation propagation to FIP integration pipelines.
* **Acceptance Criteria:** Given an active consent artefact exists, When the user revokes consent or parts of it via the app interface, Then a fresh consent artefact is instantly generated, shared with the FIP, and data access ceases immediately.

### 2.4 REQ-AA-004: FIP Red Flag Signalling and Swipe-to-Consent Friction
* **Category:** Functional | **Priority:** Should Have
* **Dimensions:** Business, Performance, Technical
* **Description:** Implement positive friction mechanisms such as swipe-to-grant interactions and explicit red flag warnings for unusual consent parameters (e.g., excessively high access frequency) during the final authorization step.
* **Regulations:** [Sahamati Customer Consent Design Guidelines]
* **Organisational Policies:** UX Accessibility and Transparency Standard
* **Risk Controls:** Malicious App Consent Exploitation, Informed Decision Safeguard
* **Legacy Constraints:** Legacy mobile frameworks supporting only standard click buttons
* **Evidence & Citation:** `[Sahamati Customer Consent Design Guidelines | LOCATION: Page 34]`
* **Human Approval Checkpoint:** Head of Product UX and Risk Management review of the friction design implementation.
* **Acceptance Criteria:** Given a user reaches the final consent authorization screen, When an abnormal access frequency or scope is detected, Then a clear warning flag is displayed, and the user must execute a deliberate swipe action to grant permission.

### 2.5 REQ-AA-005: Audit Logging and Verifiable Electronic Consent Trail
* **Category:** Auditability | **Priority:** Must Have
* **Dimensions:** Auditability, Security, Compliance
* **Description:** Ensure every electronic consent artefact creation, usage, modification, and revocation event is immutably logged with cryptographic verification capabilities to satisfy regulatory audit requirements.
* **Regulations:** [RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]
* **Organisational Policies:** Enterprise Audit Trail and Retention Policy
* **Risk Controls:** Non-Repudiation Verification, Regulatory Compliance Audit Readiness
* **Legacy Constraints:** Fragmented application logs across microservices
* **Evidence & Citation:** `[RBI Master Direction - NBFC-AA Directions 2016 | LOCATION: Page 10]`
* **Human Approval Checkpoint:** Chief Information Security Officer (CISO) sign-off on immutable audit store architecture.
* **Acceptance Criteria:** Given any lifecycle event occurs on a consent artefact, When the event is processed, Then an immutable audit log entry is generated containing timestamps, actor identity, digital signatures, and is cryptographically verifiable.

---

## 3. Quality Analysis & Gaps

While the baseline requirements cover core security and functional mechanics, a rigorous evaluation of the initial specification highlights specific quality gaps that must be resolved during technical design and architecture reviews:

* **Ambiguity Score:** `0.45` (Moderate risk of incomplete implementation without specific technical profiles).
* **Identified Quality Gaps:**
  1. *Data Retention & Purging:* Specific data retention periods and automated purging protocols for fetched financial statements and customer data require explicit definition.
  2. *Cryptographic Standards:* Exact encryption algorithms and standards (e.g., AES-256 at rest, TLS 1.3 in transit) for fetched financial statements must be formalised.
  3. *Resilience & Error Handling:* Standardized fallback procedures, retry policies, and timeout handling when FIPs (Financial Information Providers) fail to respond during account discovery or statement fetching need establishment.

---

## 4. SDLC Methodology & Deterministic Ranking

To balance rapid user-facing feature delivery with strict regulatory and cryptographic compliance, a deterministic ranking of Software Development Life Cycle (SDLC) models was conducted for this enterprise project.

### 4.1 Ranked SDLC Evaluation Scores

| SDLC Model | Score (out of 100) | Rationale |
| :--- | :---: | :--- |
| **Agile-V-Model Hybrid** | **96** | **Primary Recommendation:** Combines iterative delivery for user-facing consent management and friction UX (REQs AA-003, AA-004) with rigorous up-front architectural gate controls, security testing, and compliance verification required for PII masking, cryptographic audit trails, and RBI/ReBIT mandates (REQs AA-001, AA-002, AA-005). |
| **DevSecOps** | **90** | Excellent for automated continuous security checks, pipeline compliance gates, and immutability verification, but requires structured upfront regulatory sign-offs for legal wording and data-privacy architectures. |
| **V-Model** | **82** | Strong emphasis on verification and validation traceability matching strict banking regulations, but lacks the flexibility needed for iterative UX refinements and rapid integration with evolving FIP pipelines. |
| **Agile** | **75** | Great for rapid feature development and user interface flows (swipe-to-consent), but risks compliance gaps and insufficient rigor in cryptographic zero-persistence and immutable audit trail design without strict upfront V-Model gating. |
| **Spiral** | **68** | High risk-analysis focus fits security requirements, but excessive overhead and slow iteration
