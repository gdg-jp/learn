# Auth Service Runbook

Internal runbook for authentication incidents.

Escalate to Identity Platform when:

- SSO login is unavailable for all users of a Premier or Enterprise customer.
- SAML signature validation errors begin after IdP certificate rotation.
- Multiple tenants in the same region report authentication failures.

Attach tenant ID, IdP provider, certificate fingerprint, sanitized SAML error, affected user count, and incident correlation.

Do not share backend cache keys, log excerpts, or internal service names with customers.
