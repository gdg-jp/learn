# Identity Provider Integration Runbook

For IdP metadata changes, verify the metadata URL, entity ID, ACS URL, certificate fingerprint, and signing algorithm.

If the metadata was updated less than 24 hours ago and AcmeDesk still validates the previous fingerprint, request cache refresh by Identity Platform.
