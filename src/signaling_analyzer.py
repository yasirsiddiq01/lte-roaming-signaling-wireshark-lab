from pathlib import Path
import csv
from collections import defaultdict


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "mock_roaming_signaling_events.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
ISSUES_FILE = REPORTS_DIR / "signaling_issues.csv"
SUMMARY_FILE = REPORTS_DIR / "session_summary.csv"

EXPECTED_APN = "iot.sateliot"
ALLOWED_ROAMING_PARTNERS = {"VODAFONE_UK", "ORANGE_FR", "TELEFONICA_ES"}
LATENCY_WARNING_MS = 1000

REQUIRED_EVENTS = [
    "ATTACH_REQUEST",
    "AUTH_REQUEST",
    "AUTH_RESPONSE",
    "CREATE_SESSION_REQUEST",
    "CREATE_SESSION_RESPONSE",
    "CHARGING_TRIGGER",
]


def load_events():
    with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def group_by_session(events):
    sessions = defaultdict(list)

    for event in events:
        sessions[event["session_id"]].append(event)

    return sessions


def add_issue(issues, session_id, issue_type, severity, interface, protocol, description, recommendation):
    issues.append(
        {
            "session_id": session_id,
            "issue_type": issue_type,
            "severity": severity,
            "interface": interface,
            "protocol": protocol,
            "description": description,
            "recommendation": recommendation,
        }
    )


def analyze_session(session_id, events):
    issues = []

    event_types = {event["event_type"] for event in events}
    vpmn = events[0]["vpmn"]
    apn = events[0]["apn"]

    failed_events = [
        event for event in events
        if event["result_code"].upper() not in {"OK", "SUCCESS"}
    ]

    high_latency_events = [
        event for event in events
        if int(event["latency_ms"]) > LATENCY_WARNING_MS
    ]

    if vpmn not in ALLOWED_ROAMING_PARTNERS:
        add_issue(
            issues,
            session_id,
            "ROAMING_PARTNER_NOT_ALLOWED",
            "CRITICAL",
            "S6a",
            "DIAMETER",
            f"Visited network {vpmn} is not configured as an allowed roaming partner.",
            "Check roaming agreement, partner configuration, and Diameter routing rules.",
        )

    if apn != EXPECTED_APN:
        add_issue(
            issues,
            session_id,
            "APN_MISMATCH",
            "HIGH",
            "S11/S8",
            "GTPv2",
            f"Session used APN {apn}, expected {EXPECTED_APN}.",
            "Verify APN configuration between operator, roaming partner, and packet core.",
        )

    for required_event in REQUIRED_EVENTS:
        if required_event not in event_types:
            add_issue(
                issues,
                session_id,
                "MISSING_SIGNALING_EVENT",
                "HIGH",
                "Multiple",
                "Multiple",
                f"Required event {required_event} is missing.",
                "Check the signaling trace and identify where the procedure stopped.",
            )

    for event in failed_events:
        add_issue(
            issues,
            session_id,
            "FAILED_SIGNALING_EVENT",
            "HIGH",
            event["interface"],
            event["protocol"],
            f"{event['event_type']} failed with result {event['result_code']}.",
            "Inspect packet trace around the failed event and verify peer configuration.",
        )

    for event in high_latency_events:
        add_issue(
            issues,
            session_id,
            "HIGH_SIGNALING_LATENCY",
            "MEDIUM",
            event["interface"],
            event["protocol"],
            f"{event['event_type']} latency is {event['latency_ms']} ms.",
            "Check IP connectivity, routing path, roaming hub/IPX latency, and peer response time.",
        )

    summary = {
        "session_id": session_id,
        "subscriber_imsi": events[0]["subscriber_imsi"],
        "hpmn": events[0]["hpmn"],
        "vpmn": vpmn,
        "apn": apn,
        "event_count": len(events),
        "issue_count": len(issues),
        "session_status": "PASS" if not issues else "FAIL",
    }

    return issues, summary


def write_csv(path, rows, fieldnames):
    REPORTS_DIR.mkdir(exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not INPUT_FILE.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    events = load_events()
    sessions = group_by_session(events)

    all_issues = []
    all_summaries = []

    for session_id, session_events in sessions.items():
        issues, summary = analyze_session(session_id, session_events)
        all_issues.extend(issues)
        all_summaries.append(summary)

    write_csv(
        ISSUES_FILE,
        all_issues,
        [
            "session_id",
            "issue_type",
            "severity",
            "interface",
            "protocol",
            "description",
            "recommendation",
        ],
    )

    write_csv(
        SUMMARY_FILE,
        all_summaries,
        [
            "session_id",
            "subscriber_imsi",
            "hpmn",
            "vpmn",
            "apn",
            "event_count",
            "issue_count",
            "session_status",
        ],
    )

    print(f"Analyzed {len(sessions)} roaming sessions.")
    print(f"Found {len(all_issues)} signaling/integration issues.")
    print(f"Issue report written to {ISSUES_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Session summary written to {SUMMARY_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()