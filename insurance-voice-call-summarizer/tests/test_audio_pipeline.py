"""
Integration tests validating the 5 benchmark insurance call scenarios.
"""

import json
import unittest
from pathlib import Path
from core.config import SAMPLE_CALLS_FILE
from core.models import Utterance
from core.analyzer import InsuranceCallAnalyzer


class TestSampleCallsScenarios(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analyzer = InsuranceCallAnalyzer()
        with open(SAMPLE_CALLS_FILE, "r", encoding="utf-8") as f:
            cls.calls = json.load(f)

    def test_sample_calls_count(self):
        self.assertEqual(len(self.calls), 5)

    def test_scenario_1_auto_fnol(self):
        call = self.calls[0]
        turns = [Utterance(**t) for t in call["transcript"]]
        record = self.analyzer.analyze_call(
            turns,
            call_id=call["id"],
            scenario_type=call["scenario_type"],
            caller_name=call.get("caller_name"),
            policy_number=call.get("policy_number")
        )

        self.assertTrue(record.qa_scorecard.is_passing)
        self.assertTrue(record.qa_scorecard.recording_disclosure_passed)
        self.assertEqual(record.claim_extraction.police_report_filed, True)
        self.assertEqual(record.claim_extraction.police_report_number, "PD-2026-8941")
        self.assertEqual(record.claim_extraction.claimant_name, "Sarah Jenkins")
        self.assertEqual(record.claim_extraction.insurance_number, "PA-8392019")

    def test_benchmark_names_and_policy_numbers_are_unique(self):
        unique_claimants = set()
        unique_policies = set()

        for call in self.calls:
            turns = [Utterance(**t) for t in call["transcript"]]
            record = self.analyzer.analyze_call(
                turns,
                call_id=call["id"],
                scenario_type=call["scenario_type"],
                caller_name=call.get("caller_name"),
                policy_number=call.get("policy_number")
            )
            unique_claimants.add(record.claim_extraction.claimant_name)
            unique_policies.add(record.claim_extraction.insurance_number)

        self.assertEqual(len(unique_claimants), len(self.calls))
        self.assertEqual(len(unique_policies), len(self.calls))

    def test_scenario_2_homeowners_water(self):
        call = self.calls[1]
        turns = [Utterance(**t) for t in call["transcript"]]
        record = self.analyzer.analyze_call(turns, call_id=call["id"], scenario_type=call["scenario_type"])

        self.assertTrue(record.qa_scorecard.is_passing)
        self.assertIn("water", record.claim_extraction.cause.lower())
        self.assertGreaterEqual(record.qa_scorecard.empathy_score, 85.0)

    def test_scenario_3_suspicious_crash(self):
        call = self.calls[2]
        turns = [Utterance(**t) for t in call["transcript"]]
        record = self.analyzer.analyze_call(turns, call_id=call["id"], scenario_type=call["scenario_type"])

        # Must have SIU fraud red flags
        siu_flags = [rf for rf in record.red_flags if rf.category == "FRAUD_SIU"]
        self.assertGreater(len(siu_flags), 0)
        critical_flags = [rf for rf in record.red_flags if rf.severity == "CRITICAL"]
        self.assertGreater(len(critical_flags), 0)

    def test_scenario_4_billing_dispute(self):
        call = self.calls[3]
        turns = [Utterance(**t) for t in call["transcript"]]
        record = self.analyzer.analyze_call(turns, call_id=call["id"], scenario_type=call["scenario_type"])

        # Agent omitted recording disclosure and was rude
        self.assertFalse(record.qa_scorecard.recording_disclosure_passed)
        self.assertFalse(record.qa_scorecard.is_passing)
        # Customer threatened lawyer / insurance commissioner
        esc_flags = [rf for rf in record.red_flags if rf.category == "LEGAL_ESCALATION"]
        self.assertGreater(len(esc_flags), 0)

    def test_scenario_5_commercial_liability(self):
        call = self.calls[4]
        turns = [Utterance(**t) for t in call["transcript"]]
        record = self.analyzer.analyze_call(turns, call_id=call["id"], scenario_type=call["scenario_type"])

        self.assertTrue(record.qa_scorecard.recording_disclosure_passed)
        self.assertTrue(record.claim_extraction.injuries_reported)


if __name__ == "__main__":
    unittest.main()
