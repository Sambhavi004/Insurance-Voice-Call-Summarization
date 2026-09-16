"""
Red Flag and Risk Detection Engine.
Identifies potential fraud (SIU triggers), compliance infractions, legal escalation, and coverage disputes.
"""

import re
from typing import List
from core.models import Utterance, RedFlagItem


class RedFlagDetector:
    """Scans conversation utterances for risk patterns and policy triggers."""

    def detect(self, turns: List[Utterance]) -> List[RedFlagItem]:
        flags: List[RedFlagItem] = []
        flag_counter = 1

        agent_turns = [t for t in turns if t.speaker.lower() == "agent"]
        customer_turns = [t for t in turns if t.speaker.lower() == "customer"]
        all_text = " ".join(t.text for t in turns).lower()

        # 1. SIU / Fraud Indicators: Rushed settlement / Bypass inspection
        rush_patterns = [
            (r"(cash payout|send me a check today|skip the inspection|settle this today without inspection|direct cash|wire the money)",
             "CRITICAL",
             "Suspicious Settlement Pressure",
             "Caller is exerting urgent pressure for an immediate cash payment or asking to waive physical vehicle/property inspection.",
             "Flag for Special Investigation Unit (SIU). Mandate in-person independent appraisal before issuing any payment.")
        ]

        # 2. Inconsistent timeline / Driver identity ambiguity
        story_inconsistency_patterns = [
            (r"(actually.*was driving|my cousin.*no wait|i wasn't driving|changed my mind.*story|wasn't really sure when)",
             "HIGH",
             "Driver Identity / Incident Contradiction",
             "Transcript indicates contradictory or shifting statements regarding the driver or timeline of loss.",
             "Obtain signed recorded statement from all reported occupants and request cell phone records / telematics.")
        ]

        # 3. Commercial use on personal auto policy
        unendorsed_commercial = [
            (r"(delivering food|doordash|uber eats|rideshare|lyft|instacart|commercial delivery)",
             "HIGH",
             "Potential Unendorsed Commercial Use",
             "Loss occurred while vehicle was potentially engaged in commercial delivery or rideshare without verified endorsement.",
             "Verify whether active livery/commercial app was online at time of collision. Cross-check TNC endorsement rider.")
        ]

        # 4. Avoidance of Police Report in major collision
        police_avoidance = [
            (r"(didn't call the police|avoided calling cops|no police.*settle between us|police weren't called)",
             "MEDIUM",
             "Absence of Official Police Report",
             "Parties chose not to summon law enforcement despite notable vehicular damage or third-party involvement.",
             "Require scene photos, dashcam footage, and independent third-party driver statement.")
        ]

        # 5. Legal Threats & Attorney Involvement
        legal_threats = [
            (r"(my lawyer|call an attorney|contacting my attorney|lawsuit|taking you to court|sue you|bad faith)",
             "CRITICAL",
             "Legal Escalation / Attorney Representation Threat",
             "Caller explicitly threatened litigation, retention of legal counsel, or bad faith allegations.",
             "Route claim file immediately to Senior Claims Specialist or Legal Defense Liaison. Restrict informal communications.")
        ]

        # 6. Regulatory Complaint (DOI / Insurance Commissioner)
        regulatory_complaints = [
            (r"(insurance commissioner|department of insurance|state board|file a regulatory complaint)",
             "HIGH",
             "DOI Regulatory Complaint Threat",
             "Customer stated intent to report the insurer or claims handler to the state Department of Insurance.",
             "Alert Customer Relations & Compliance Quality Manager. Ensure strict adhere to statutory response deadlines.")
        ]

        # 7. Agent Unauthorized Coverage Guarantee
        unauthorized_promise = [
            (r"(i guarantee this will be 100% covered|don't worry.*definitely covered|we will pay everything in full no matter what)",
             "CRITICAL",
             "Agent Unauthorized Coverage Guarantee",
             "Customer service agent prematurely promised full indemnification prior to adjuster review or policy limit verification.",
             "Manager coaching required. Add disclaimer addendum to file reserving carrier rights under the policy contract.")
        ]

        # 8. Churn / Threat to cancel entire book of business
        cancellation_threats = [
            (r"(cancel all my policies|moving all my accounts|switching to another insurance|dropping you guys)",
             "HIGH",
             "Imminent Policy Cancellation / High Churn Risk",
             "Customer expressed clear intent to cancel policy portfolio due to dissatisfaction.",
             "Initiate VIP Retention or Escalation Specialist workflow within 2 business hours.")
        ]

        # Run pattern scans across utterances
        all_rules = [
            ("FRAUD_SIU", rush_patterns),
            ("FRAUD_SIU", story_inconsistency_patterns),
            ("COVERAGE_DISPUTE", unendorsed_commercial),
            ("FRAUD_SIU", police_avoidance),
            ("LEGAL_ESCALATION", legal_threats),
            ("LEGAL_ESCALATION", regulatory_complaints),
            ("COMPLIANCE_BREACH", unauthorized_promise),
            ("LEGAL_ESCALATION", cancellation_threats)
        ]

        for category, rule_list in all_rules:
            for pattern, severity, title, desc, rec_action in rule_list:
                for turn in turns:
                    match = re.search(pattern, turn.text, re.IGNORECASE)
                    if match:
                        flags.append(RedFlagItem(
                            id=f"RF-{flag_counter:03d}",
                            category=category,
                            severity=severity,
                            title=title,
                            description=desc,
                            evidence_quote=turn.text.strip(),
                            recommended_action=rec_action
                        ))
                        flag_counter += 1
                        break  # One flag per rule per call

        # Check for extreme negative sentiment flips
        consecutive_negatives = 0
        for t in customer_turns:
            if t.sentiment == "Negative":
                consecutive_negatives += 1
            else:
                consecutive_negatives = 0
            if consecutive_negatives >= 3:
                flags.append(RedFlagItem(
                    id=f"RF-{flag_counter:03d}",
                    category="LEGAL_ESCALATION",
                    severity="HIGH",
                    title="Prolonged Customer Distress & Hostility",
                    description="Customer exhibited sustained negative sentiment for multiple consecutive exchanges.",
                    evidence_quote=t.text.strip(),
                    recommended_action="Execute warm transfer or schedule senior supervisor de-escalation callback."
                ))
                flag_counter += 1
                break

        return flags
