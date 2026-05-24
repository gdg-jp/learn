# Security and Privacy Redaction

Never include the following in customer-facing text:

- Internal tenant IDs or account IDs.
- Full SAML assertions or raw access tokens.
- Certificate private keys or webhook secrets.
- Backend service log lines.
- Internal incident timeline entries.
- Employee personal data beyond the support contact already known to the customer.

Internal escalation notes may include sanitized identifiers and links to internal systems.
