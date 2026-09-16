"""
Automated CRM and Claims Management Note Generator.
Produces industry-standard SOAP claim notes, Guidewire ClaimCenter ready snippets, and Salesforce FSC logs.
"""

from typing import List
from datetime import datetime
from core.models import ClaimExtraction, QAScorecard, RedFlagItem, CRMNotes


class CRMGenerator:
    """Generates structured, copy-paste ready documentation for carrier claims platforms."""

    def generate(
        self,
        extraction: ClaimExtraction,
        scorecard: QAScorecard,
        red_flags: List[RedFlagItem],
        agent_id: str = "AGT-1029",
        call_id: str = "CALL-AUTO-001"
    ) -> CRMNotes:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Executive Summary
        exec_summary = (
            f"Call handled on {now_str} regarding {extraction.call_reason}. "
            f"Policy: {extraction.insurance_number}, Insured: {extraction.claimant_name}. "
            f"Incident: {extraction.cause} at {extraction.location}. "
            f"Damages reported: {', '.join(extraction.damages) if extraction.damages else 'None reported'}. "
            f"QA Audit Score: {scorecard.overall_score}% ({'PASS' if scorecard.is_passing else 'FAIL'}). "
            f"Active Red Flags: {len(red_flags)}."
        )

        # 2. SOAP Components
        # S: Subjective (What the caller reported)
        soap_s = (
            f"Caller {extraction.claimant_name} contacted claims department to report {extraction.call_reason}. "
            f"Caller stated that on {extraction.incident_date} at approximately {extraction.incident_time}, "
            f"{extraction.cause}. Reported damages to vehicle/property: {', '.join(extraction.damages) if extraction.damages else 'N/A'}. "
            f"Injuries: {extraction.injury_details}."
        )

        # O: Objective (Verified details & recorded facts)
        police_txt = f"Yes (Report #{extraction.police_report_number})" if extraction.police_report_filed else "No / Unconfirmed"
        drivers_txt = ", ".join(extraction.driver_names) if extraction.driver_names else "Unspecified"
        soap_o = (
            f"• Policy Number: {extraction.insurance_number}\n"
            f"• Verified Claimant: {extraction.claimant_name}\n"
            f"• Date of Loss: {extraction.incident_date} ({extraction.incident_time})\n"
            f"• Location of Loss: {extraction.location}\n"
            f"• Drivers/Parties Identified: {drivers_txt}\n"
            f"• Police Report: {police_txt}\n"
            f"• Quoted Deductible: {extraction.deductible}\n"
            f"• Recorded Line Disclosure: {'DELIVERED' if scorecard.recording_disclosure_passed else 'MISSED (COMPLIANCE ISSUE)'}\n"
            f"• KYC Authentication: {'VERIFIED' if scorecard.kyc_verified_passed else 'UNAUTHENTICATED'}"
        )

        # A: Assessment (Adjuster evaluation & risk flags)
        rf_txt = "\n".join([f"  - [{rf.severity}] {rf.title}: {rf.description}" for rf in red_flags]) if red_flags else "  - None detected"
        soap_a = (
            f"Preliminary Liability / Fault: {extraction.fault_indication}.\n"
            f"QA Audit Score: {scorecard.overall_score}/100.0 (Pass Status: {'PASSED' if scorecard.is_passing else 'NEEDS REMEDIATION'}).\n"
            f"Customer Sentiment Trend: {scorecard.customer_sentiment_start} -> {scorecard.customer_sentiment_end} ({scorecard.customer_sentiment_trend}).\n"
            f"Risk & Red Flags Detected ({len(red_flags)}):\n{rf_txt}"
        )

        # P: Plan (Next steps & assignments)
        action_items = [
            f"Assigned claim inspection task to field / virtual appraiser for: {', '.join(extraction.damages) if extraction.damages else 'Inspection'}",
            f"Request official police report {f'({extraction.police_report_number})' if extraction.police_report_number else ''} from local jurisdiction",
            "Send digital proof of loss upload portal link to insured email/SMS",
            "Follow up with policyholder within 24 business hours with coverage confirmation"
        ]
        if any(rf.category == "FRAUD_SIU" for rf in red_flags):
            action_items.append("URGENT: Submit SIU referral package for driver statement & physical vehicle examination.")
        if any(rf.category == "LEGAL_ESCALATION" for rf in red_flags):
            action_items.append("CRITICAL: Alert Claims Supervisor and Legal Defense team due to litigation threats.")

        soap_p = "\n".join([f"{i+1}. {item}" for i, item in enumerate(action_items)])

        # Guidewire ClaimCenter Format
        gw_format = f"""=== GUIDEWIRE CLAIMCENTER NOTE ===
TOPIC: FNOL Intake & Call Summary
CLAIM / POLICY: {extraction.insurance_number}
CALL ID: {call_id} | AGENT: {agent_id} | DATE: {now_str}
CONFIDENTIALITY: Internal Claims Adjuster & QA File

1. EXECUTIVE SUMMARY:
{exec_summary}

2. SUBJECTIVE (INSURED STATEMENT):
{soap_s}

3. OBJECTIVE (RECORD OF LOSS):
{soap_o}

4. ASSESSMENT (COVERAGE & QA AUDIT):
{soap_a}

5. PLAN OF ACTION:
{soap_p}
=================================="""

        # Salesforce Financial Services Cloud Format
        sf_format = f"""[SFDC INTERACTION LOG]
Type: Inbound Claim Service Call
Subject: {extraction.call_reason} - {extraction.claimant_name}
Policy: {extraction.insurance_number} | QA Score: {scorecard.overall_score}%
Resolution Status: {'Escalated' if red_flags else 'Assigned to Adjuster'}

-- Summary --
{exec_summary}

-- Key Data --
Incident Date: {extraction.incident_date}
Location: {extraction.location}
Damages: {', '.join(extraction.damages)}
Police Report: {police_txt}

-- Next Actions --
{soap_p}
"""

        return CRMNotes(
            executive_summary=exec_summary,
            soap_subjective=soap_s,
            soap_objective=soap_o,
            soap_assessment=soap_a,
            soap_plan=soap_p,
            action_items=action_items,
            guidewire_formatted=gw_format,
            salesforce_formatted=sf_format
        )
