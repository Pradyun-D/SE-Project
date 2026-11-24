# Software Requirements Specification (SRS)

## 1. Introduction

This Software Requirements Specification (SRS) documents the functional and non-functional requirements for a regulated FinTech project that enables users to link savings accounts and fetch financial statements using PAN and DOB, with consent management, audit logging, and secure data retention. This document is intended for use by stakeholders, developers, and compliance officers to ensure alignment with regulatory expectations and technical feasibility.

---

## 2. Scope

The scope of this project includes:

- Enabling users to link their savings accounts using PAN and DOB.
- Fetching financial statements from linked accounts.
- Implementing consent management mechanisms for data usage.
- Maintaining audit logs of all user interactions.
- Ensuring secure data retention practices in accordance with applicable regulations.

The project is designed for a medium-scale organization and must comply with relevant financial and data protection regulations.

---

## 3. Functional Requirements

### 3.1 Requirement Overview (REQ-001)

**Title:** Requirement overview  
**Description:** Users should link savings accounts and fetch financial statements using PAN and DOB with consent management, audit logging, and secure data retention.  
**Category:** Functional  
**Priority:** Must Have  
**Citation:** General Context  

**Acceptance Criteria:**
- Given the requirement, when implemented, then it is testable.

---

### 3.2 Consent Management

- Users must provide explicit consent for the use of their PAN and DOB in account linking and financial statement retrieval.
- Consent must be opt-in, with clear mechanisms for opt-out, revocation, and withdrawal.
- Consent records must be stored securely and auditable.

**Citation:** Quality Analysis – Missing Aspects

---

### 3.3 Audit Logging

- All user actions related to account linking and financial statement retrieval must be logged.
- Logs must include:
  - User ID
  - Time of action
  - IP address
  - Action type (e.g., link, retrieve, revoke)
  - Status (success/failure)
- Logs must be stored securely and retained for a minimum of 5 years, in accordance with data protection regulations.

**Citation:** Quality Analysis – Missing Aspects

---

### 3.4 Secure Data Retention

- Financial data and user information must be retained securely for a minimum of 5 years.
- Data retention policies must align with relevant data protection laws (e.g., GDPR, CCPA).
- Data must be encrypted at rest and in transit.

**
