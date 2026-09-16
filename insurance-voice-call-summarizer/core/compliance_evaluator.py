"""
Compliance and Quality Assurance (QA) Evaluator.
Evaluates agent performance, mandatory regulatory disclaimers, KYC, and script adherence.
"""

import re
from typing import List, Tuple
from core.models import Utterance, ComplianceCheck, QAScorecard
from core.config import (
    QA_PASSING_SCORE,
    CRITICAL_COMPLIANCE_PENALTY,
    MODERATE_COMPLIANCE_PENALTY,
    MINOR_COMPLIANCE_PENALTY,
    DISCLOSURE_PHRASES,
    FRAUD_WARNING_PHRASES,
    KYC_VERIFICATION_PHRASES,
    EMPATHY_PHRASES
)


class ComplianceEvaluator:
    """Evaluates call compliance and agent performance against carrier standards."""

    def evaluate(self, turns: List[Utterance]) -> QAScorecard:
        agent_turns = [t for t in turns if t.speaker.lower() == "agent"]
        customer_turns = [t for t in turns if t.speaker.lower() == "customer"]

        full_agent_text = " ".join(t.text for t in agent_turns).lower()
        first_three_agent_text = " ".join(t.text for t in agent_turns[:3]).lower() if agent_turns else ""

        checks: List[ComplianceCheck] = []
        deductions = 0.0

        # 1. Mandatory Call Recording Disclosure
        disclosure_found = False
        disclosure_evidence = None
        for phrase in DISCLOSURE_PHRASES:
            if phrase in first_three_agent_text or phrase in full_agent_text:
                disclosure_found = True
                # Find matching sentence
                for t in agent_turns[:4]:
                    if phrase in t.text.lower():
                        disclosure_evidence = t.text.strip()
                        break
                break

        if disclosure_found:
            checks.append(ComplianceCheck(
                name="Mandatory Call Recording Disclosure",
                passed=True,
                score_impact=0.0,
                evidence=disclosure_evidence or "Recording disclosure verified.",
                explanation="Agent properly notified the caller that the line is recorded/monitored."
            ))
        else:
            deductions += CRITICAL_COMPLIANCE_PENALTY
            checks.append(ComplianceCheck(
                name="Mandatory Call Recording Disclosure",
                passed=False,
                score_impact=-CRITICAL_COMPLIANCE_PENALTY,
                evidence=None,
                explanation="CRITICAL VIOLATION: Agent failed to state mandatory recording disclosure within call opening."
            ))

        # 2. Caller Identity Verification (KYC)
        kyc_found = False
        kyc_evidence = None
        for phrase in KYC_VERIFICATION_PHRASES:
            if phrase in full_agent_text:
                kyc_found = True
                for t in agent_turns:
                    if phrase in t.text.lower():
                        kyc_evidence = t.text.strip()
                        break
                break

        # Fallback KYC check: agent asks for policy number, address, or DOB
        if not kyc_found:
            kyc_pattern = r"(policy number|verify.*address|confirm.*name|date of birth|security code)"
            match = re.search(kyc_pattern, full_agent_text, re.IGNORECASE)
            if match:
                kyc_found = True
                for t in agent_turns:
                    if re.search(kyc_pattern, t.text, re.IGNORECASE):
                        kyc_evidence = t.text.strip()
                        break

        if kyc_found:
            checks.append(ComplianceCheck(
                name="Caller Authentication & KYC",
                passed=True,
                score_impact=0.0,
                evidence=kyc_evidence or "Identity verification questions detected.",
                explanation="Agent verified policyholder identity details prior to discussing claim specifics."
            ))
        else:
            deductions += MODERATE_COMPLIANCE_PENALTY
            checks.append(ComplianceCheck(
                name="Caller Authentication & KYC",
                passed=False,
                score_impact=-MODERATE_COMPLIANCE_PENALTY,
                evidence=None,
                explanation="Identity verification was absent or incomplete before handling claim data."
            ))

        # 3. Statutory Fraud Warning / Disclaimer
        fraud_warning_found = False
        fraud_evidence = None
        for phrase in FRAUD_WARNING_PHRASES:
            if phrase in full_agent_text:
                fraud_warning_found = True
                for t in agent_turns:
                    if phrase in t.text.lower():
                        fraud_evidence = t.text.strip()
                        break
                break

        if not fraud_warning_found:
            fraud_regex = r"(insurance fraud|fraudulent.*claim|false.*fraudulent|fraud.*crime|penalties.*perjury|fraud penalties)"
            if re.search(fraud_regex, full_agent_text):
                fraud_warning_found = True
                for t in agent_turns:
                    if re.search(fraud_regex, t.text.lower()):
                        fraud_evidence = t.text.strip()
                        break

        if fraud_warning_found:
            checks.append(ComplianceCheck(
                name="Statutory Fraud Warning Advisory",
                passed=True,
                score_impact=0.0,
                evidence=fraud_evidence,
                explanation="Agent delivered required statutory warning regarding fraudulent submissions."
            ))
        else:
            # Moderate deduction if missing on claims intake
            deductions += MODERATE_COMPLIANCE_PENALTY
            checks.append(ComplianceCheck(
                name="Statutory Fraud Warning Advisory",
                passed=False,
                score_impact=-MODERATE_COMPLIANCE_PENALTY,
                evidence=None,
                explanation="Required statutory fraud disclosure was not delivered during claim intake."
            ))

        # 4. Clear Next Steps & SLA Timeline
        sla_patterns = [r"within \d+ (hours|days|business days)", r"adjuster will (reach out|contact|inspect|call)", r"next step", r"assigned to"]
        sla_found = False
        sla_evidence = None
        for pattern in sla_patterns:
            if re.search(pattern, full_agent_text):
                sla_found = True
                for t in agent_turns:
                    if re.search(pattern, t.text.lower()):
                        sla_evidence = t.text.strip()
                        break
                break

        if sla_found:
            checks.append(ComplianceCheck(
                name="Clear Next Steps & SLA Communicated",
                passed=True,
                score_impact=0.0,
                evidence=sla_evidence,
                explanation="Agent provided explicit follow-up expectations and operational timelines."
            ))
        else:
            deductions += MINOR_COMPLIANCE_PENALTY
            checks.append(ComplianceCheck(
                name="Clear Next Steps & SLA Communicated",
                passed=False,
                score_impact=-MINOR_COMPLIANCE_PENALTY,
                evidence=None,
                explanation="Agent concluded call without setting clear SLA or follow-up deadline."
            ))

        # 5. Empathy & Active Listening Score
        empathy_hits = sum(1 for phrase in EMPATHY_PHRASES if phrase in full_agent_text)
        customer_distress = any(t.sentiment == "Negative" for t in customer_turns)
        
        if customer_distress and empathy_hits >= 2:
            empathy_score = 95.0
        elif empathy_hits >= 1:
            empathy_score = 85.0
        elif customer_distress and empathy_hits == 0:
            empathy_score = 55.0
            deductions += 10.0
        else:
            empathy_score = 80.0

        # Professionalism & Script Adherence
        unprofessional_flags = ["calm down", "not my problem", "you should have known", "shut up", "i don't care"]
        has_rudeness = any(flag in full_agent_text for flag in unprofessional_flags)
        if has_rudeness:
            professionalism_score = 45.0
            deductions += 25.0
        else:
            professionalism_score = 92.0

        script_adherence = 95.0 if (disclosure_found and kyc_found and sla_found) else 70.0

        # Customer Sentiment Progression
        sentiment_start, sentiment_end, trend = self._calculate_sentiment_trend(customer_turns)

        # Overall Score
        overall_score = max(0.0, min(100.0, 100.0 - deductions))
        is_passing = overall_score >= QA_PASSING_SCORE and disclosure_found

        return QAScorecard(
            overall_score=round(overall_score, 1),
            is_passing=is_passing,
            recording_disclosure_passed=disclosure_found,
            kyc_verified_passed=kyc_found,
            fraud_warning_passed=fraud_warning_found,
            empathy_score=empathy_score,
            professionalism_score=professionalism_score,
            script_adherence_score=script_adherence,
            customer_sentiment_start=sentiment_start,
            customer_sentiment_end=sentiment_end,
            customer_sentiment_trend=trend,
            detailed_checks=checks
        )

    def _calculate_sentiment_trend(self, customer_turns: List[Utterance]) -> Tuple[str, str, str]:
        if not customer_turns:
            return ("Neutral", "Neutral", "Stable")
        
        first_sentiment = customer_turns[0].sentiment
        last_sentiment = customer_turns[-1].sentiment

        sentiment_ranks = {"Negative": 0, "Neutral": 1, "Positive": 2}
        start_rank = sentiment_ranks.get(first_sentiment, 1)
        end_rank = sentiment_ranks.get(last_sentiment, 1)

        if end_rank > start_rank:
            trend = "Improved"
        elif end_rank < start_rank:
            trend = "Worsened"
        else:
            trend = "Stable"

        return (first_sentiment, last_sentiment, trend)
