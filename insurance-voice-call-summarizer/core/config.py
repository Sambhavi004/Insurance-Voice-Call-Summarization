"""
Configuration and constants for Insurance Voice Call Summarization.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_AUDIO_DIR = DATA_DIR / "sample_audio"
SAMPLE_CALLS_FILE = DATA_DIR / "sample_calls.json"

# Audio Settings
SUPPORTED_AUDIO_EXTENSIONS = [".wav", ".mp3", ".m4a", ".ogg", ".flac"]
DEFAULT_WHISPER_MODEL = "base"

# QA & Compliance Thresholds
QA_PASSING_SCORE = 80.0
CRITICAL_COMPLIANCE_PENALTY = 25.0
MODERATE_COMPLIANCE_PENALTY = 15.0
MINOR_COMPLIANCE_PENALTY = 5.0

# Mandatory Disclaimers / Standard Phrases to Audit
DISCLOSURE_PHRASES = [
    "recorded for quality",
    "monitored for quality",
    "call is being recorded",
    "recording this call",
    "call may be monitored",
    "line is recorded"
]

FRAUD_WARNING_PHRASES = [
    "insurance fraud is a crime",
    "false or fraudulent information",
    "subject to criminal penalties",
    "fraudulent claim",
    "penalties of perjury",
    "state fraud warning"
]

KYC_VERIFICATION_PHRASES = [
    "verify your policy number",
    "confirm your date of birth",
    "verify your address",
    "security verification",
    "verify your full name",
    "confirm the vehicle vin"
]

EMPATHY_PHRASES = [
    "so sorry",
    "sorry to hear",
    "sorry you are",
    "glad you are safe",
    "must have been stressful",
    "understand how frustrating",
    "we are here to help",
    "completely understand",
    "take your time",
    "take a deep breath",
    "sorry for the inconvenience"
]

# Risk / Red Flag Categories
RED_FLAG_CATEGORIES = {
    "FRAUD_SIU": "Special Investigation / Fraud Risk",
    "LEGAL_ESCALATION": "Legal Threat & High Churn Risk",
    "COMPLIANCE_BREACH": "Regulatory & Disclosure Violation",
    "COVERAGE_DISPUTE": "Uncovered Loss / Policy Exclusion Dispute"
}

SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
