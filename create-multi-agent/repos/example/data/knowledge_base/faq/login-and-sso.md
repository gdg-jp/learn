# Login and SSO FAQ

Customers using SAML SSO should confirm that their IdP metadata, signing certificate, ACS URL, and audience URI match the AcmeDesk tenant settings.

If users cannot log in after an IdP certificate rotation, ask the administrator to upload the updated metadata XML or metadata URL in AcmeDesk. The customer can then retry in a new browser session.

Customer-safe guidance:

- Confirm when the IdP certificate was rotated.
- Ask whether all users or only a subset are affected.
- Request the SAML error message or a sanitized SAML trace.
- Avoid sharing internal tenant IDs, cache names, or backend service logs.
