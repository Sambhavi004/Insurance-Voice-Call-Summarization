# Insurance Voice Call Summarization & Audit System

> **AI-powered platform that listens to customer service and claims calls, transcribes audio, extracts structured claim data, flags compliance and fraud red flags, and automatically generates CRM-ready audit notes.**

---

## 💡 Problem & Value Proposition

Reviewing and auditing hours of insurance customer service and claims calls manually is inefficient, labor-intensive, and error-prone. Claims adjusters and QA auditors often spend 30–40% of their working hours typing notes into core systems (like Guidewire ClaimCenter or Salesforce) and manually checking calls for regulatory compliance.

This project automates the entire post-call and live-audit workflow:
- **Listens to calls**: Audio playback and Whisper speech-to-text with speaker diarization (Agent vs. Customer).
- **Summarizes content**: Extracts structured claim entities (cause, location, damages, drivers, police report, deductible) and executive summaries.
- **Flags red flags**: Automatically flags Special Investigation Unit (SIU) fraud indicators, legal/litigation threats, regulatory violations, and high-churn sentiment flips.
- **Audits quality & compliance**: Evaluates mandatory call recording disclosures, caller authentication (KYC), statutory fraud disclaimers, agent empathy, and script adherence.
- **Stores notes automatically**: Auto-generates industry-standard **SOAP claim notes** (Subjective, Objective, Assessment, Plan) with 1-click export for Guidewire, Duck Creek, and Salesforce FSC.

---

## 🔗 Solution Overview

This project combines call transcription, structured claim extraction, compliance QA, and risk detection in a single insurance call analysis workflow.

---

## 🚀 Key Features

| Capability | Description |
|---|---|
| **Audio Ingestion & Whisper ASR** | Upload `.wav`, `.mp3`, or `.m4a` files. Transcribes turns, estimates timestamps, and alternates Agent/Customer roles. |
| **Interactive Transcript Viewer** | Audio player synced with turn-by-turn dialogue, speaker badges, and sentiment tags (`Positive`, `Neutral`, `Negative`). |
| **Conversational Sentiment Curve** | Interactive Altair chart displaying caller emotional progression from opening to resolution. |
| **Structured Claim Extraction** | Auto-extracts Policy Number, Claimant, Loss Date/Time, Location, Cause, Damages List, Injuries, Police Report status, and Deductible. |
| **QA & Compliance Scorecard** | Dynamic compliance checklist verifying: Mandatory Recording Disclosure, KYC Verification, Statutory Fraud Warning, and SLAs. |
| **Red Flag & Risk Center** | Rule & NLP engine identifying SIU Fraud (settlement rush, story contradictions), Legal Threats, DOI Complaints, and Unauthorized Guarantees. |
| **CRM Claim Notes Generator** | Formats notes in **SOAP format** with ready-to-paste templates for **Guidewire ClaimCenter** and **Salesforce Financial Services Cloud**. |
| **Benchmark Intelligence** | Comparative analytics dashboard displaying pass/fail rates, QA distributions, and red-flag frequency across multiple calls. |
| **Dual AI Provider** | Operates 100% offline out-of-the-box with built-in Local Rule & NLP Engine, plus optional toggles for Gemini API and OpenAI API. |

---

## 📂 Project Structure

```
insurance-voice-call-summarizer/
│
├── README.md                          # Project documentation and quickstart
├── requirements.txt                   # Dependencies (streamlit, whisper, pydantic, etc.)
├── app.py                             # Main Streamlit web application
│
├── core/
│   ├── __init__.py
│   ├── config.py                      # Thresholds, compliance rules, and phrases
│   ├── models.py                      # Pydantic data schemas (ClaimExtraction, QAScorecard, RedFlags)
│   ├── audio_transcriber.py           # Whisper audio processing & speaker turns
│   ├── compliance_evaluator.py        # Regulatory disclosures & QA scoring engine
│   ├── red_flag_detector.py           # SIU fraud, legal escalation, and churn risk detector
│   ├── crm_generator.py               # Auto-generates SOAP & Guidewire/SFDC claim notes
│   └── analyzer.py                    # Master orchestrator (Local NLP + LLM toggle)
│
├── data/
│   ├── sample_calls.json              # 5 pre-loaded realistic insurance calls
│   └── sample_audio/                  # Synthesized .wav voice audio files for demoing
│
├── ui/
│   ├── __init__.py
│   ├── styles.py                      # Clean corporate insurance CSS styling
│   └── components.py                  # Streamlit widgets (KPI cards, wave charts, notes)
│
├── scripts/
│   └── generate_sample_audio.py       # Audio synthesizer using Windows SAPI / PCM wave
│
└── tests/
    ├── test_extraction.py             # Unit tests for models, extraction, and compliance
    └── test_audio_pipeline.py         # Integration tests for all 5 scenario benchmarks
```

---

## 🎙️ Pre-Loaded Benchmark Scenarios

The system includes 5 realistic insurance calls:
1. **Auto Collision FNOL (`CALL-AUTO-001`)**: Rear-end collision on Elm Street. Police report `PD-2026-8941`. High agent compliance, clear subrogation path, QA Score: **95% (PASS)**.
2. **Homeowners Water Loss (`CALL-HOME-002`)**: Burst copper supply pipe, 2 inches of standing water in finished basement. Urgent emergency restoration dispatched, QA Score: **90% (PASS)**.
3. **Suspicious Crash (`CALL-SUSP-003`)**: High-pressure demand for cash payout without inspection, shifting driver timeline, avoided police. **SIU Fraud Red Flags & Critical Alert Triggered**.
4. **Billing & Renewal Dispute (`CALL-DISP-004`)**: Unexplained rate increase, agent misses mandatory recording disclosure and acts dismissive. Customer threatens DOI regulatory complaint & attorney. **Non-Compliant (FAIL)**.
5. **Commercial Liability (`CALL-COMM-005`)**: Customer slip-and-fall at hardware store, injury transport to hospital, store surveillance video preserved, QA Score: **90% (PASS)**.

---

## ⚡ Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Audio Assets (Pre-configured)
To generate or refresh the demo `.wav` audio files:
```bash
python scripts/generate_sample_audio.py
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*All 11 unit and integration tests validate deterministic execution in < 0.05 seconds.*

---

## 📋 Example Generated SOAP Note (Guidewire Ready)

```text
=== GUIDEWIRE CLAIMCENTER NOTE ===
TOPIC: FNOL Intake & Call Summary
CLAIM / POLICY: PA-8392019
CALL ID: CALL-AUTO-001 | AGENT: AGT-2041 | DATE: 2026-09-09 14:32:00
CONFIDENTIALITY: Internal Claims Adjuster & QA File

1. EXECUTIVE SUMMARY:
Call handled regarding First Notice of Loss (Auto Collision Claim). Policy: PA-8392019, Insured: Sarah Jenkins. Incident: Rear-end collision at traffic stoplight at Intersection of Elm Street and 4th Avenue. Damages reported: Rear bumper smashed, Cracked rear tail light, Trunk lid dented and jammed. QA Audit Score: 95.0% (PASS). Active Red Flags: 0.

2. SUBJECTIVE (INSURED STATEMENT):
Caller Sarah Jenkins contacted claims department to report First Notice of Loss (Auto Collision Claim). Caller stated that on Today (Sept 9, 2026) at approximately 8:30 AM, Rear-end collision at traffic stoplight. Reported damages to vehicle/property: Rear bumper smashed, Cracked rear tail light, Trunk lid dented and jammed. Injuries: Mild neck stiffness / prospective whiplash noted.

3. OBJECTIVE (RECORD OF LOSS):
• Policy Number: PA-8392019
• Verified Claimant: Sarah Jenkins
• Date of Loss: Today (Sept 9, 2026) (8:30 AM)
• Location of Loss: Intersection of Elm Street and 4th Avenue
• Drivers/Parties Identified: Sarah Jenkins, Robert Davis
• Police Report: Yes (Report #PD-2026-8941)
• Quoted Deductible: $500 Comprehensive/Collision
• Recorded Line Disclosure: DELIVERED
• KYC Authentication: VERIFIED

4. ASSESSMENT (COVERAGE & QA AUDIT):
Preliminary Liability / Fault: Adverse party likely at-fault (rear-end impact).
QA Audit Score: 95.0/100.0 (Pass Status: PASSED).
Customer Sentiment Trend: Negative -> Positive (Improved).
Risk & Red Flags Detected (0):
  - None detected

5. PLAN OF ACTION:
1. Assigned claim inspection task to field / virtual appraiser for: Rear bumper smashed, Cracked rear tail light, Trunk lid dented and jammed
2. Request official police report (PD-2026-8941) from local jurisdiction
3. Send digital proof of loss upload portal link to insured email/SMS
4. Follow up with policyholder within 24 business hours with coverage confirmation
==================================
```
