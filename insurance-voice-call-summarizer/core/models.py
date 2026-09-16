"""
Pydantic Data Models for Insurance Voice Call Summarization & Audit System.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Utterance(BaseModel):
    """A single speaker turn in the conversation."""
    speaker: str = Field(description="Speaker label, e.g. Agent or Customer")
    start_time: Optional[float] = Field(default=None, description="Start time in seconds")
    end_time: Optional[float] = Field(default=None, description="End time in seconds")
    text: str = Field(description="Spoken text in this turn")
    sentiment: str = Field(default="Neutral", description="Sentiment: Positive, Neutral, or Negative")


class ClaimExtraction(BaseModel):
    """
    Structured extraction of claim and incident parameters.
    Based on Microsoft OpenAI Insurance prompt pattern with extended FNOL entities.
    """
    call_reason: str = Field(default="Unknown", description="Primary call reason or line of inquiry")
    cause: str = Field(default="Not specified", description="Cause or mechanics of the loss/incident")
    driver_names: List[str] = Field(default_factory=list, description="Names of drivers or primary actors")
    insurance_number: str = Field(default="N/A", description="Policy or claim tracking number")
    claimant_name: str = Field(default="N/A", description="Name of policyholder or reporting caller")
    incident_date: str = Field(default="Unknown", description="Date of loss/incident")
    incident_time: str = Field(default="Unknown", description="Time of loss/incident")
    location: str = Field(default="Not specified", description="Accident or property loss location")
    damages: List[str] = Field(default_factory=list, description="List of physical damages or financial losses")
    injuries_reported: bool = Field(default=False, description="Whether any bodily injury was reported")
    injury_details: str = Field(default="None reported", description="Details of injuries if any")
    police_report_filed: Optional[bool] = Field(default=None, description="Whether police responded or a report was filed")
    police_report_number: Optional[str] = Field(default=None, description="Police incident/report number")
    fault_indication: str = Field(default="Undetermined", description="Reported or inferred fault/liability status")
    deductible: str = Field(default="Unspecified", description="Policy deductible mentioned")
    summary: str = Field(default="", description="A concise, factual executive summary of the claim details")


class ComplianceCheck(BaseModel):
    """Individual QA or compliance checklist verification item."""
    name: str
    passed: bool
    score_impact: float
    evidence: Optional[str] = None
    explanation: str


class QAScorecard(BaseModel):
    """Quality Assurance and regulatory compliance evaluation."""
    overall_score: float = Field(default=100.0, description="Overall QA score between 0 and 100")
    is_passing: bool = Field(default=True, description="Whether the call meets the QA threshold")
    recording_disclosure_passed: bool = Field(default=False, description="Mandatory call recording notice given")
    kyc_verified_passed: bool = Field(default=False, description="Policyholder identity properly authenticated")
    fraud_warning_passed: bool = Field(default=False, description="Mandatory statutory fraud advisory delivered")
    empathy_score: float = Field(default=85.0, description="Customer empathy and de-escalation score (0-100)")
    professionalism_score: float = Field(default=90.0, description="Tone, active listening, and professionalism (0-100)")
    script_adherence_score: float = Field(default=85.0, description="Adherence to standard carrier FNOL script")
    customer_sentiment_start: str = Field(default="Neutral", description="Initial caller sentiment")
    customer_sentiment_end: str = Field(default="Neutral", description="Concluding caller sentiment")
    customer_sentiment_trend: str = Field(default="Stable", description="Sentiment direction: Improved, Worsened, or Stable")
    detailed_checks: List[ComplianceCheck] = Field(default_factory=list)


class RedFlagItem(BaseModel):
    """An alert or risk flag identified during the call audit."""
    id: str
    category: str = Field(description="FRAUD_SIU, LEGAL_ESCALATION, COMPLIANCE_BREACH, COVERAGE_DISPUTE")
    severity: str = Field(description="CRITICAL, HIGH, MEDIUM, or LOW")
    title: str
    description: str
    evidence_quote: str = Field(description="Verbatim excerpt from the call transcript")
    recommended_action: str = Field(description="Recommended action for claims adjuster or QA manager")


class CRMNotes(BaseModel):
    """Auto-generated claim notes formatted for CRM & Claims systems."""
    executive_summary: str
    soap_subjective: str = Field(description="S: What caller reported/stated")
    soap_objective: str = Field(description="O: Verified facts, policy #, damages, police report")
    soap_assessment: str = Field(description="A: Adjuster evaluation, coverage status, liability, fraud score")
    soap_plan: str = Field(description="P: Next steps, required documents, deadlines, SLA")
    action_items: List[str] = Field(default_factory=list)
    guidewire_formatted: str = Field(default="", description="Ready to paste into Guidewire ClaimCenter")
    salesforce_formatted: str = Field(default="", description="Ready to paste into Salesforce FSC")


class CallAuditRecord(BaseModel):
    """Complete audit record for a single customer service or claim call."""
    call_id: str
    title: str
    scenario_type: str = Field(default="General", description="Auto FNOL, Homeowners, Suspicious, Dispute, etc.")
    timestamp: str
    duration_seconds: float = 0.0
    caller_phone: str = "N/A"
    agent_id: str = "AGT-1029"
    audio_path: Optional[str] = None
    transcript_turns: List[Utterance] = Field(default_factory=list)
    full_transcript_text: str = ""
    claim_extraction: ClaimExtraction = Field(default_factory=ClaimExtraction)
    qa_scorecard: QAScorecard = Field(default_factory=QAScorecard)
    red_flags: List[RedFlagItem] = Field(default_factory=list)
    crm_notes: CRMNotes = Field(default_factory=lambda: CRMNotes(
        executive_summary="", soap_subjective="", soap_objective="", soap_assessment="", soap_plan=""
    ))
