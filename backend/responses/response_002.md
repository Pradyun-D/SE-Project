# Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for a mobile application feature that enables customers to connect their bank accounts through an Account Aggregator. The feature allows customers to discover accounts using PAN and date of birth, select which accounts to link, grant and revoke consent for sharing financial information, and fetch account balances and recent statements. It also includes audit logging, status tracking, and notification mechanisms.

### 1.2 Scope

The scope of this feature includes:

- **Account Discovery**: Using PAN and DOB to identify customer accounts.
- **Account Linking**: Allowing customers to choose which accounts to link.
- **Consent Management**: Granting and revoking consent for data sharing.
- **Data Fetching**: Retrieving account balances and recent statements.
- **Status Tracking**: Displaying the status of each linked account.
- **Notifications**: Alerting customers of changes in consent or data fetch status.
- **Audit Logging**: Maintaining a record of consent actions and data access.
- **Error Handling**: Managing failed or delayed responses.

### 1.3 Applicable Standards and Regulations

This feature must comply with the following regulatory frameworks:

- **RBI Master Direction - NBFC-AA Directions 2016** (Pages 9–12)
- **RBI NBFC-AA Directions 2025** (Page 15)
- **ReBIT Guidelines - PAN/DOB Account Discovery** (Page 1)
- **Sahamati Customer Consent Design Guidelines** (Page 19)

These documents outline the legal and regulatory obligations for the Account Aggregator, including data protection, consent management, and secure data flow.

---

## 2. System Overview

### 2.1 System Description

The system is a mobile application feature that allows customers to connect their bank accounts via an Account Aggregator. The feature is designed to be secure, compliant, and user-friendly, ensuring that customer data is protected and that all actions are transparent and auditable.

### 2.2 System Components

- **Mobile Application**: The user-facing interface for account discovery, linking, and data fetching.
- **Account Aggregator Backend**: Handles account discovery, consent management, and data sharing.
- **Financial Information Providers (FIPs)**: Banks and financial institutions that provide account data.
- **Audit Log System**: Tracks all consent actions and data access events.
- **Notification System**: Sends alerts to customers regarding changes in account status or consent.

### 2.3 System Constraints

- **Regulatory Compliance**: Must adhere to the RBI and ReBIT guidelines.
- **Security**: Data must be encrypted and stored securely.
- **Performance**: Must handle multiple banks and large-scale user data.
- **Scalability**: Must support future expansion of financial information providers.
- **Reliability**: Must handle failed or delayed responses with appropriate error handling.

---

## 3. Functional Requirements

### 3.1 Account Discovery

- **Functionality**: Allow customers to discover accounts using PAN and DOB.
- **Input Parameters**: PAN, DOB, and at least one strong identifier (e.g., mobile number).
- **Output**: List of accounts associated with the customer.
- **Compliance**: Must follow the ReBIT Guidelines for PAN/DOB account discovery.

### 3.2 Account Linking

- **Functionality**: Enable customers to select which accounts to link.
- **Input Parameters**: Selected accounts from the discovery list.
- **Output**: Confirmation of successful linking.
- **Compliance**: Must ensure that no unauthorized access to customer credentials occurs.

### 3.3 Consent Management

- **Functionality**: Allow customers to grant and revoke consent for sharing financial information.
- **Input Parameters**: Consent form, authentication method (e.g., biometric, password).
- **Output**: Consent status update and audit log entry.
- **Compliance**: Must follow the RBI NBFC-AA Directions 2025, which require explicit consent for data sharing.

### 3.4 Data Fetching

- **Functionality**: Retrieve account balances and recent statements.
- **Input Parameters**: Selected accounts and consent status.
- **Output**: Account balance and statement data.
- **Compliance**: Must ensure that data is transferred securely and only as permitted by the consent artifact.

### 3.5 Status Tracking

- **Functionality**: Display the current status of each linked account.
- **Input Parameters**: Linked account details.
- **Output**: Account status (e.g., active, pending, revoked).
- **Compliance**: Must ensure that status changes are logged and notified to the customer.

### 3.6 Notifications

- **Functionality**: Notify customers of changes in consent or data fetch status.
- **Input Parameters**: Status change event.
- **Output**: Push notification or in-app alert.
- **Compliance**: Must ensure that notifications are timely and secure.

### 3.7 Audit Logging

- **Functionality**: Maintain a log of all consent actions and data access events.
- **Input Parameters**: Consent action, data access event, timestamp.
- **Output**: Audit log entries for review and compliance audits.
- **Compliance**: Must follow the RBI NBFC-AA Directions 2025, which require maintaining logs of information sharing requests.

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **Response Time**: Must handle failed or delayed responses with appropriate error handling.
- **Scalability**: Must support multiple banks and large-scale user data.

### 4.2 Security

- **Data Protection**: Ensure that customer data is encrypted and stored securely.
- **Authentication**: Implement strong authentication methods (e.g., biometric, password).
- **Access Control**: Ensure that access to customer information is based on consent-based authorization.

### 4.3 Availability

- **System Availability**: Must be available 24/7 to support customer needs.
- **Disaster Recovery**: Implement disaster risk management and business continuity plans.

### 4.4 Usability

- **User Interface**: Provide a clear and intuitive interface for account discovery, linking, and consent management.
- **Accessibility**:
