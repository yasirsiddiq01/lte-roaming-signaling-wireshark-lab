
from pathlib import Path
from datetime import datetime
import subprocess
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RUN_PROJECT_FILE = PROJECT_ROOT / "run_project.py"

SESSION_SUMMARY_FILE = PROJECT_ROOT / "reports" / "session_summary.csv"
SIGNALING_ISSUES_FILE = PROJECT_ROOT / "reports" / "signaling_issues.csv"

WIRESHARK_FILTERS_FILE = PROJECT_ROOT / "docs" / "wireshark_filters.md"
TROUBLESHOOTING_CHECKLIST_FILE = PROJECT_ROOT / "docs" / "roaming_troubleshooting_checklist.md"


st.set_page_config(
    page_title="LTE Roaming Signaling Troubleshooting Lab",
    layout="wide",
)


def rerun_app():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def run_pipeline():
    result = subprocess.run(
        [sys.executable, str(RUN_PROJECT_FILE)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    output_parts = []

    if result.stdout:
        output_parts.append(result.stdout)

    if result.stderr:
        output_parts.append("STDERR:\n" + result.stderr)

    output = "\n".join(output_parts)

    return result.returncode == 0, output


def read_csv_file(path):
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not read CSV file: {path.name}. Error: {exc}")
        return pd.DataFrame()


def read_markdown_file(path):
    if not path.exists():
        return "File not found."

    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Could not read Markdown file: {path.name}. Error: {exc}"


def count_failed_sessions(session_df):
    if session_df.empty or "session_status" not in session_df.columns:
        return 0

    return int((session_df["session_status"] == "FAIL").sum())


def count_critical_issues(issues_df):
    if issues_df.empty or "severity" not in issues_df.columns:
        return 0

    return int((issues_df["severity"] == "CRITICAL").sum())


def get_last_updated_text(path):
    if not path.exists():
        return "Last report updated: not available"

    modified_time = path.stat().st_mtime
    last_updated = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
    return f"Last report updated: {last_updated}"


def render_pipeline_output():
    if "pipeline_message" not in st.session_state:
        return

    if st.session_state.get("last_pipeline_success"):
        st.success(st.session_state["pipeline_message"])
    else:
        st.error(st.session_state["pipeline_message"])

    with st.expander("Pipeline Output", expanded=False):
        st.code(st.session_state.get("last_pipeline_output", ""))


def render_issue_charts(issues_df):
    if issues_df.empty:
        st.warning("No signaling issue data available.")
        return

    if "issue_type" in issues_df.columns:
        st.write("Issues by Type")
        issue_counts = issues_df["issue_type"].value_counts().reset_index()
        issue_counts.columns = ["issue_type", "count"]
        st.bar_chart(issue_counts.set_index("issue_type"))

    if "severity" in issues_df.columns:
        st.write("Issues by Severity")
        severity_counts = issues_df["severity"].value_counts().reset_index()
        severity_counts.columns = ["severity", "count"]
        st.bar_chart(severity_counts.set_index("severity"))


st.title("LTE Roaming Signaling Troubleshooting Lab")

st.write(
    "Interactive dashboard for a simulated LTE roaming signaling integration lab. "
    "The app analyzes attach, Diameter authentication, GTP session setup, APN, latency, "
    "partner configuration, and charging-trigger flows."
)

st.divider()

with st.sidebar:
    st.header("Pipeline Control")

    run_button = st.button("Run Signaling Analysis")

    st.divider()

    st.header("Project Files")
    st.write(f"Session summary: `{SESSION_SUMMARY_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Signaling issues: `{SIGNALING_ISSUES_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Wireshark filters: `{WIRESHARK_FILTERS_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Checklist: `{TROUBLESHOOTING_CHECKLIST_FILE.relative_to(PROJECT_ROOT)}`")


if run_button:
    with st.spinner("Running signaling analyzer..."):
        success, output = run_pipeline()

    st.session_state["last_pipeline_output"] = output
    st.session_state["last_pipeline_success"] = success

    if success:
        st.session_state["pipeline_message"] = "Pipeline completed successfully."
    else:
        st.session_state["pipeline_message"] = "Pipeline failed."

    rerun_app()


render_pipeline_output()

session_df = read_csv_file(SESSION_SUMMARY_FILE)
issues_df = read_csv_file(SIGNALING_ISSUES_FILE)

st.subheader("System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Sessions", len(session_df))

with col2:
    st.metric("Failed Sessions", count_failed_sessions(session_df))

with col3:
    st.metric("Signaling Issues", len(issues_df))

with col4:
    st.metric("Critical Issues", count_critical_issues(issues_df))

st.caption(get_last_updated_text(SESSION_SUMMARY_FILE))

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Session Summary",
        "Signaling Issues",
        "Issue Charts",
        "Wireshark Filters",
        "Troubleshooting Checklist",
    ]
)

with tab1:
    st.subheader("Session Summary")

    if session_df.empty:
        st.warning("No session summary found. Click 'Run Signaling Analysis' first.")
    else:
        st.dataframe(session_df, use_container_width=True)

with tab2:
    st.subheader("Signaling Issues")

    if issues_df.empty:
        st.warning("No signaling issues found. Click 'Run Signaling Analysis' first.")
    else:
        st.dataframe(issues_df, use_container_width=True)

with tab3:
    st.subheader("Issue Charts")
    render_issue_charts(issues_df)

with tab4:
    st.subheader("Wireshark Filters")
    st.markdown(read_markdown_file(WIRESHARK_FILTERS_FILE))

with tab5:
    st.subheader("Roaming Troubleshooting Checklist")
    st.markdown(read_markdown_file(TROUBLESHOOTING_CHECKLIST_FILE))

