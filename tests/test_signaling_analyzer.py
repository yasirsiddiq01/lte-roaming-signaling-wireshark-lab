from pathlib import Path
import sys
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from signaling_analyzer import analyze_session


def make_event(
    session_id="S_TEST",
    event_type="ATTACH_REQUEST",
    result_code="OK",
    latency_ms="50",
    vpmn="VODAFONE_UK",
    apn="iot.sateliot",
    interface="S1AP",
    protocol="S1AP",
):
    return {
        "session_id": session_id,
        "timestamp_utc": "2026-05-31T10:00:00Z",
        "subscriber_imsi": "214010123456789",
        "hpmn": "SATELIOT_ES",
        "vpmn": vpmn,
        "interface": interface,
        "protocol": protocol,
        "event_type": event_type,
        "result_code": result_code,
        "latency_ms": latency_ms,
        "apn": apn,
        "notes": "test event",
    }


class TestSignalingAnalyzer(unittest.TestCase):

    def test_apn_mismatch_is_detected(self):
        events = [
            make_event(event_type="ATTACH_REQUEST", apn="wrong.apn"),
            make_event(event_type="AUTH_REQUEST", apn="wrong.apn"),
            make_event(event_type="AUTH_RESPONSE", apn="wrong.apn"),
            make_event(event_type="CREATE_SESSION_REQUEST", apn="wrong.apn"),
            make_event(event_type="CREATE_SESSION_RESPONSE", apn="wrong.apn"),
            make_event(event_type="CHARGING_TRIGGER", apn="wrong.apn"),
        ]

        issues, summary = analyze_session("S_APN", events)
        issue_types = [issue["issue_type"] for issue in issues]

        self.assertIn("APN_MISMATCH", issue_types)
        self.assertEqual(summary["session_status"], "FAIL")

    def test_unknown_roaming_partner_is_detected(self):
        events = [
            make_event(event_type="ATTACH_REQUEST", vpmn="UNKNOWN_MNO"),
            make_event(event_type="AUTH_REQUEST", vpmn="UNKNOWN_MNO"),
            make_event(event_type="AUTH_RESPONSE", vpmn="UNKNOWN_MNO"),
            make_event(event_type="CREATE_SESSION_REQUEST", vpmn="UNKNOWN_MNO"),
            make_event(event_type="CREATE_SESSION_RESPONSE", vpmn="UNKNOWN_MNO"),
            make_event(event_type="CHARGING_TRIGGER", vpmn="UNKNOWN_MNO"),
        ]

        issues, summary = analyze_session("S_UNKNOWN", events)
        issue_types = [issue["issue_type"] for issue in issues]

        self.assertIn("ROAMING_PARTNER_NOT_ALLOWED", issue_types)
        self.assertEqual(summary["session_status"], "FAIL")

    def test_high_signaling_latency_is_detected(self):
        events = [
            make_event(event_type="ATTACH_REQUEST"),
            make_event(event_type="AUTH_REQUEST", latency_ms="2500", interface="S6a", protocol="DIAMETER"),
            make_event(event_type="AUTH_RESPONSE"),
            make_event(event_type="CREATE_SESSION_REQUEST"),
            make_event(event_type="CREATE_SESSION_RESPONSE"),
            make_event(event_type="CHARGING_TRIGGER"),
        ]

        issues, summary = analyze_session("S_LATENCY", events)
        issue_types = [issue["issue_type"] for issue in issues]

        self.assertIn("HIGH_SIGNALING_LATENCY", issue_types)
        self.assertEqual(summary["session_status"], "FAIL")

    def test_missing_signaling_event_is_detected(self):
        events = [
            make_event(event_type="ATTACH_REQUEST"),
            make_event(event_type="AUTH_REQUEST"),
            make_event(event_type="AUTH_RESPONSE"),
        ]

        issues, summary = analyze_session("S_MISSING", events)
        issue_types = [issue["issue_type"] for issue in issues]

        self.assertIn("MISSING_SIGNALING_EVENT", issue_types)
        self.assertEqual(summary["session_status"], "FAIL")

    def test_successful_session_passes(self):
        events = [
            make_event(event_type="ATTACH_REQUEST"),
            make_event(event_type="AUTH_REQUEST"),
            make_event(event_type="AUTH_RESPONSE"),
            make_event(event_type="CREATE_SESSION_REQUEST"),
            make_event(event_type="CREATE_SESSION_RESPONSE"),
            make_event(event_type="CHARGING_TRIGGER"),
        ]

        issues, summary = analyze_session("S_PASS", events)

        self.assertEqual(len(issues), 0)
        self.assertEqual(summary["session_status"], "PASS")


if __name__ == "__main__":
    unittest.main()