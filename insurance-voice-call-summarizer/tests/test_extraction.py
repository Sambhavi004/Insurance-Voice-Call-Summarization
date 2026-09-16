"""
Unit tests for Insurance Voice Call Summarizer & Audit System.
"""

import os
import tempfile
import unittest
from core.models import Utterance, ClaimExtraction, QAScorecard, RedFlagItem
from core.compliance_evaluator import ComplianceEvaluator
from core.red_flag_detector import RedFlagDetector
from core.crm_generator import CRMGenerator
from core.audio_transcriber import AudioTranscriber
from core.analyzer import InsuranceCallAnalyzer


class TestInsuranceSummarizer(unittest.TestCase):

    def setUp(self):
        self.evaluator = ComplianceEvaluator()
        self.red_flag_detector = RedFlagDetector()
        self.crm_generator = CRMGenerator()
        self.transcriber = AudioTranscriber()
        self.analyzer = InsuranceCallAnalyzer()

    def test_compliant_call_evaluation(self):
        turns = [
            Utterance(speaker="Agent", text="Thank you for calling Apex Insurance. This call is recorded for quality.", sentiment="Positive"),
            Utterance(speaker="Customer", text="Hi, I need to report a car accident.", sentiment="Neutral"),
            Utterance(speaker="Agent", text="I am so sorry to hear that. Could you verify your policy number and address for security verification?", sentiment="Positive"),
            Utterance(speaker="Customer", text="Policy PA-10293, 100 Main St.", sentiment="Positive"),
            Utterance(speaker="Agent", text="Verified. Note that submitting false information is insurance fraud. What happened?", sentiment="Neutral"),
            Utterance(speaker="Customer", text="Another car hit my rear bumper.", sentiment="Negative"),
            Utterance(speaker="Agent", text="An adjuster will reach out within 24 hours to inspect the vehicle.", sentiment="Positive")
        ]

        scorecard = self.evaluator.evaluate(turns)
        self.assertTrue(scorecard.recording_disclosure_passed)
        self.assertTrue(scorecard.kyc_verified_passed)
        self.assertTrue(scorecard.fraud_warning_passed)
        self.assertTrue(scorecard.is_passing)
        self.assertGreaterEqual(scorecard.overall_score, 80.0)

    def test_non_compliant_call_penalties(self):
        # Call without recording disclosure and dismissive agent
        turns = [
            Utterance(speaker="Agent", text="Yeah what do you need?", sentiment="Neutral"),
            Utterance(speaker="Customer", text="My rates doubled without notice!", sentiment="Negative"),
            Utterance(speaker="Agent", text="Calm down, you should have known rates increase.", sentiment="Negative"),
            Utterance(speaker="Customer", text="You are being rude! I will cancel all my policies!", sentiment="Negative")
        ]

        scorecard = self.evaluator.evaluate(turns)
        self.assertFalse(scorecard.recording_disclosure_passed)
        self.assertFalse(scorecard.is_passing)
        self.assertLess(scorecard.overall_score, 60.0)

    def test_red_flag_detection(self):
        turns = [
            Utterance(speaker="Agent", text="This call is recorded. What happened?", sentiment="Neutral"),
            Utterance(speaker="Customer", text="I wrecked my car. Settle this today without inspection and send me a check today because I need cash right now.", sentiment="Negative"),
            Utterance(speaker="Customer", text="If you don't wire the money I will have my lawyer sue you in court!", sentiment="Negative"),
            Utterance(speaker="Customer", text="I'm also reporting you to the insurance commissioner!", sentiment="Negative")
        ]

        flags = self.red_flag_detector.detect(turns)
        categories = [f.category for f in flags]
        severities = [f.severity for f in flags]

        self.assertIn("FRAUD_SIU", categories)
        self.assertIn("LEGAL_ESCALATION", categories)
        self.assertIn("CRITICAL", severities)

    def test_crm_note_generation(self):
        extraction = ClaimExtraction(
            call_reason="First Notice of Loss",
            cause="Rear-end collision",
            insurance_number="PA-882910",
            claimant_name="Alice Smith",
            incident_date="Sept 9, 2026",
            incident_time="9:00 AM",
            location="Market St & 5th Ave",
            damages=["Rear bumper", "Tail light"],
            police_report_filed=True,
            police_report_number="PD-9921",
            summary="Alice Smith reported rear-end collision."
        )
        scorecard = QAScorecard(overall_score=95.0, is_passing=True, recording_disclosure_passed=True, kyc_verified_passed=True)
        red_flags = []

        notes = self.crm_generator.generate(extraction, scorecard, red_flags)

        self.assertIn("Alice Smith", notes.executive_summary)
        self.assertIn("PA-882910", notes.soap_objective)
        self.assertIn("GUIDEWIRE CLAIMCENTER NOTE", notes.guidewire_formatted)
        self.assertIn("[SFDC INTERACTION LOG]", notes.salesforce_formatted)
        self.assertGreater(len(notes.action_items), 0)

    def test_transcript_parsing(self):
        raw_text = """[00:03] Agent: Good morning, this call is recorded.
[00:08] Customer: Hi, someone backed into my fender in the driveway."""

        turns = self.transcriber.parse_raw_transcript(raw_text)
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0].speaker, "Agent")
        self.assertEqual(turns[1].speaker, "Customer")
        self.assertEqual(turns[0].start_time, 3.0)

    def test_transcription_failure_does_not_return_fake_sample(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(b"fake audio data")
            temp_path = tmp.name

        try:
            self.transcriber._whisper_model = None
            with self.assertRaises(RuntimeError):
                self.transcriber.transcribe_audio(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
