# Escalation Policy

Escalate when the case has one or more of the following:

- SEV1 or SEV2 customer impact.
- Premier customer with all-user login outage.
- Webhook delay over 30 minutes with business workflow impact.
- Active incident correlation requiring engineering confirmation.
- Billing discrepancy that requires ledger correction or invoice regeneration.

Recommended teams:

- Authentication, SAML, IdP certificates: Identity Platform.
- SCIM provisioning: Identity Platform.
- Webhooks, CRM integrations, queue latency: Integrations Platform.
- Invoice, seat true-up, contract mismatch: Billing Operations.
- Dashboard latency: Application Performance.

Attach only relevant diagnostic information. Do not attach raw secrets, full SAML assertions, customer personal data, or unrelated logs.
