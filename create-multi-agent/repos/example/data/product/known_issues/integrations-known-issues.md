# Integrations Known Issues

Known issue INT-188: CRM webhook queues in us-west1 may build backlog when downstream CRM endpoints return sustained 429 responses. Workaround: reduce import batch size, confirm endpoint 2xx responses, and request replay after queue age recovers.
