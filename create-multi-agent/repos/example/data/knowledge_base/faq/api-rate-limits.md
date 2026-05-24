# API Rate Limits FAQ

AcmeDesk enforces API rate limits by tenant, endpoint family, and contracted entitlement.

Customers with bursty integrations should use exponential backoff, avoid retry storms, and monitor `Retry-After` headers.
