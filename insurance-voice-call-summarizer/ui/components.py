"""
Reusable Streamlit UI Components for Insurance Voice Call Summarizer.
"""

import streamlit as st
import pandas as pd
import altair as alt
from typing import List
from core.models import (
    Utterance,
    ClaimExtraction,
    QAScorecard,
    RedFlagItem,
    CRMNotes
)


def render_header():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">
            <span>🛡️</span> Insurance Voice Call Summarization & Audit Platform
        </div>
        <div class="header-subtitle">
            AI-powered speech analytics, structured claim extraction, regulatory compliance scoring, and automated CRM file notes.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(scorecard: QAScorecard, red_flags: List[RedFlagItem], extraction: ClaimExtraction):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        pass_badge = (
            '<span class="kpi-badge-pass">PASSING</span>'
            if scorecard.is_passing
            else '<span class="kpi-badge-fail">REMEDIATION NEEDED</span>'
        )
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">QA Audit Score</div>
            <div class="kpi-value">{scorecard.overall_score}%</div>
            <div style="margin-top: 6px;">{pass_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        critical_count = sum(1 for rf in red_flags if rf.severity == "CRITICAL")
        rf_color = "#b91c1c" if red_flags else "#15803d"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Red Flags</div>
            <div class="kpi-value" style="color: {rf_color};">{len(red_flags)}</div>
            <div style="margin-top: 6px; font-size: 12px; color: #64748b;">
                {critical_count} Critical Priority
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        disclosure_status = (
            '<span class="kpi-badge-pass">DELIVERED</span>'
            if scorecard.recording_disclosure_passed
            else '<span class="kpi-badge-fail">MISSED</span>'
        )
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Call Recording Consent</div>
            <div class="kpi-value" style="font-size: 20px; padding-top: 8px;">{disclosure_status}</div>
            <div style="margin-top: 8px; font-size: 12px; color: #64748b;">Statutory Rule</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Customer Sentiment Trend</div>
            <div class="kpi-value" style="font-size: 22px;">{scorecard.customer_sentiment_trend}</div>
            <div style="margin-top: 6px; font-size: 12px; color: #64748b;">
                Start: {scorecard.customer_sentiment_start} → End: {scorecard.customer_sentiment_end}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_sentiment_trajectory(turns: List[Utterance]):
    """Renders turn-by-turn sentiment wave line chart."""
    sentiment_map = {"Negative": -1, "Neutral": 0, "Positive": 1}
    data = []
    for i, t in enumerate(turns):
        data.append({
            "Turn": i + 1,
            "Speaker": t.speaker,
            "Time (s)": t.start_time or (i * 5),
            "SentimentScore": sentiment_map.get(t.sentiment, 0),
            "SentimentLabel": t.sentiment,
            "Excerpt": t.text[:60] + "..." if len(t.text) > 60 else t.text
        })

    if not data:
        st.info("No turns available for sentiment curve.")
        return

    df = pd.DataFrame(data)
    
    chart = alt.Chart(df).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("Turn:Q", title="Turn Sequence"),
        y=alt.Y(
            "SentimentScore:Q",
            title="Sentiment Trajectory",
            scale=alt.Scale(domain=[-1.2, 1.2]),
            axis=alt.Axis(
                values=[-1, 0, 1],
                labelExpr="datum.value == 1 ? 'Positive' : datum.value == -1 ? 'Negative' : 'Neutral'"
            )
        ),
        color=alt.Color("Speaker:N", scale=alt.Scale(domain=["Agent", "Customer"], range=["#16a34a", "#0284c7"])),
        tooltip=["Turn", "Speaker", "SentimentLabel", "Excerpt"]
    ).properties(height=220, title="Turn-by-Turn Conversational Sentiment Dynamics")

    st.altair_chart(chart, use_container_width=True)


def render_transcript_turns(turns: List[Utterance]):
    st.markdown("### 🎙️ Audio-Synced Conversation Transcript")
    st.caption("Inspect speaker turns with timestamps and localized sentiment tags.")

    for i, turn in enumerate(turns):
        speaker_class = "turn-agent" if turn.speaker.lower() == "agent" else "turn-customer"
        badge_class = (
            "badge-pos" if turn.sentiment == "Positive"
            else "badge-neg" if turn.sentiment == "Negative"
            else "badge-neu"
        )
        time_str = f"[{int(turn.start_time or 0)//60:02d}:{int(turn.start_time or 0)%60:02d}]"
        
        st.markdown(f"""
        <div class="{speaker_class}">
            <div class="turn-speaker">
                <span><strong>{time_str} {turn.speaker}</strong></span>
                <span class="{badge_class}">{turn.sentiment}</span>
            </div>
            <div class="turn-text">{turn.text}</div>
        </div>
        """, unsafe_allow_html=True)


def render_claim_entities_table(extraction: ClaimExtraction):
    st.markdown("### 📋 Structured Claim Information")
    st.caption("Key claim details extracted from the call for review and documentation.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"""
        **Policy & Claimant**
        - **Policy Number:** `{extraction.insurance_number}`
        - **Insured / Claimant Name:** {extraction.claimant_name}
        - **Drivers Identified:** {', '.join(extraction.driver_names) if extraction.driver_names else 'N/A'}
        - **Call Reason:** {extraction.call_reason}
        """)

        st.markdown(f"""
        **Incident Mechanics**
        - **Date of Loss:** {extraction.incident_date}
        - **Time of Loss:** {extraction.incident_time}
        - **Location:** {extraction.location}
        - **Cause of Incident:** {extraction.cause}
        """)

    with c2:
        police_status = "✅ Filed" if extraction.police_report_filed else "❌ No / Not Filed"
        if extraction.police_report_number:
            police_status += f" (`#{extraction.police_report_number}`)"

        injuries_status = "⚠️ Reported" if extraction.injuries_reported else "✅ None Reported"

        st.markdown(f"""
        **Loss & Liability Assessment**
        - **Police Report:** {police_status}
        - **Injuries:** {injuries_status} ({extraction.injury_details})
        - **Inferred Fault Status:** {extraction.fault_indication}
        - **Policy Deductible:** {extraction.deductible}
        """)

        st.markdown("**Reported Damages / Impacted Items:**")
        if extraction.damages:
            for d in extraction.damages:
                st.markdown(f"- 🔧 {d}")
        else:
            st.markdown("- *None noted*")

    st.markdown("---")
    st.markdown(f"**Executive Incident Summary:**")
    st.info(extraction.summary)


def render_compliance_checklist(scorecard: QAScorecard):
    st.markdown("### 🛡️ QA & Compliance Scorecard")
    st.caption("Carrier script adherence, mandatory disclosure auditing, and agent soft skills evaluation.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Empathy & Active Listening", f"{scorecard.empathy_score}%")
    col2.metric("Professionalism & Tone", f"{scorecard.professionalism_score}%")
    col3.metric("Script Adherence", f"{scorecard.script_adherence_score}%")

    st.markdown("#### Mandatory Compliance Rules")
    for check in scorecard.detailed_checks:
        icon = "✅" if check.passed else "❌"
        status_text = "PASSED" if check.passed else f"FAILED ({check.score_impact:+.0f} pts)"
        with st.expander(f"{icon} {check.name} — {status_text}", expanded=not check.passed):
            st.markdown(f"**Audit Rule Details:** {check.explanation}")
            if check.evidence:
                st.markdown(f"""
                <div class="quote-box">
                    <strong>Transcript Evidence:</strong> "{check.evidence}"
                </div>
                """, unsafe_allow_html=True)
            elif not check.passed:
                st.error("No evidence found in transcript. Agent missed required mandatory statement.")


def render_red_flags_list(red_flags: List[RedFlagItem]):
    st.markdown("### 🚩 Red Flag & Risk Management Center")
    st.caption("Automated detection of Special Investigation Unit (SIU) fraud indicators, regulatory risks, and legal threats.")

    if not red_flags:
        st.success("✅ No critical red flags or compliance violations identified on this call.")
        return

    for rf in red_flags:
        card_class = (
            "red-flag-card-critical" if rf.severity == "CRITICAL"
            else "red-flag-card-high" if rf.severity == "HIGH"
            else "red-flag-card-medium"
        )
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; font-size: 15px;">[{rf.id}] {rf.title}</span>
                <span style="font-size: 12px; font-weight: 700; background: rgba(0,0,0,0.08); padding: 2px 8px; border-radius: 4px;">
                    {rf.severity} • {rf.category}
                </span>
            </div>
            <div style="font-size: 13.5px; margin-bottom: 6px; color: #1e293b;">{rf.description}</div>
            <div class="quote-box">
                <strong>Transcript Quote:</strong> "{rf.evidence_quote}"
            </div>
            <div style="margin-top: 8px; font-size: 13px; font-weight: 600; color: #0f172a;">
                🎯 Recommended Action: <span style="font-weight: 400;">{rf.recommended_action}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_crm_notes_view(crm_notes: CRMNotes):
    st.markdown("### 📝 CRM & Claim File Notes Generator")
    st.caption("Industry standard SOAP notes formatted for Guidewire ClaimCenter, Duck Creek, or Salesforce.")

    t1, t2, t3 = st.tabs(["Guidewire ClaimCenter", "Salesforce FSC", "SOAP Structure"])

    with t1:
        st.text_area("Guidewire Ready Format (Copy to ClaimCenter)", crm_notes.guidewire_formatted, height=360)
        st.download_button(
            label="💾 Download Guidewire Note (.txt)",
            data=crm_notes.guidewire_formatted,
            file_name="guidewire_claim_note.txt",
            mime="text/plain"
        )

    with t2:
        st.text_area("Salesforce FSC Format (Copy to Activity Log)", crm_notes.salesforce_formatted, height=360)
        st.download_button(
            label="💾 Download Salesforce Log (.txt)",
            data=crm_notes.salesforce_formatted,
            file_name="salesforce_interaction_log.txt",
            mime="text/plain"
        )

    with t3:
        st.markdown(f"**Subjective (Insured Statement):**\n\n{crm_notes.soap_subjective}")
        st.markdown(f"**Objective (Verified Records):**\n\n{crm_notes.soap_objective}")
        st.markdown(f"**Assessment (Audit & Liability):**\n\n{crm_notes.soap_assessment}")
        st.markdown(f"**Plan (Action Items):**\n\n{crm_notes.soap_plan}")
