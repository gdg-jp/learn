from __future__ import annotations

import argparse

from acmedesk_support import build_escalation_brief

SAMPLE_CASES = {
    "case-a": (
        "Contoso administrator reports that all employees cannot log in with SAML SSO. "
        "They updated the IdP certificate yesterday. This is a Premier support customer. "
        "Check prior cases, known incidents, SLA, first response, and escalation plan."
    ),
    "case-b": (
        "Globex says this month's invoice is higher than the contract amount. "
        "They increased seat count last month but cannot understand the invoice line items. "
        "Check historical tickets and contract information, then draft a response."
    ),
    "case-c": (
        "Initech reports that CRM webhook delivery is delayed by more than 30 minutes. "
        "There is business impact, and they want to know whether this is a known incident "
        "or a customer-specific configuration problem."
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic AcmeDesk sample case.")
    parser.add_argument("case", choices=sorted(SAMPLE_CASES))
    args = parser.parse_args()
    print(build_escalation_brief(SAMPLE_CASES[args.case]))


if __name__ == "__main__":
    main()
