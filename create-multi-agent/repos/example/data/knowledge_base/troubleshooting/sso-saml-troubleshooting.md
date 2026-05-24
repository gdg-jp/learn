# SAML SSO Troubleshooting

Use this checklist for SSO login failures:

1. Identify whether all users or a subset are affected.
2. Confirm the IdP, certificate rotation time, and metadata URL.
3. Compare the SAML issuer, ACS URL, audience URI, and certificate fingerprint.
4. Check whether an active authentication incident affects the customer's region.
5. For Premier customers with all-user outage, escalate to Identity Platform.

Internal-only checks:

- Verify tenant SSO cache freshness.
- Check auth service validation logs for signature mismatch.
- Do not include raw SAML assertions in customer replies.
