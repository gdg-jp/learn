# Webhook Delivery Troubleshooting

Use this checklist for delayed webhook delivery:

1. Confirm affected endpoints and event types.
2. Check delivery delay, retry count, response codes, and queue age.
3. Ask whether the customer recently changed endpoint secrets, firewall rules, or CRM rate limits.
4. Correlate with active integration incidents and regional queue alerts.
5. Escalate to Integration Platform if delay exceeds 30 minutes with business impact.

Customer-safe workaround:

- Reduce batch imports if the CRM is throttling.
- Keep endpoints returning 2xx quickly and process work asynchronously.
- Request replay after the queue is healthy.
