"""
Insurance Voice Call Summarization & Compliance Audit System.
Main Streamlit Application.
"""

import json
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt

from core.config import (
    BASE_DIR,
    SAMPLE_CALLS_FILE,
    SAMPLE_AUDIO_DIR,
    QA_PASSING_SCORE,
    SUPPORTED_AUDIO_EXTENSIONS
)
from core.models import Utterance, CallAuditRecord
from core.analyzer import InsuranceCallAnalyzer
from core.audio_transcriber import AudioTranscriber
from ui.styles import CUSTOM_CSS
from ui.components import (
    render_header,
    render_kpi_cards,
    render_sentiment_trajectory,
    render_transcript_turns,
    render_claim_entities_table,
    render_compliance_checklist,
    render_red_flags_list,
    render_crm_notes_view
)

# Configure Streamlit page
st.set_page_config(
    page_title="Insurance Voice Call Summarization",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def load_sample_calls():
    if SAMPLE_CALLS_FILE.exists():
        with open(SAMPLE_CALLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def main():
    render_header()

    sample_calls = load_sample_calls()
    transcriber = AudioTranscriber()

    # Sidebar Controls
    with st.sidebar:
        st.markdown("### ⚙️ Ingestion & Engine Settings")

        input_mode = st.radio(
            "Select Call Source:",
            ["Pre-loaded Benchmark Calls", "Upload Audio File (.wav/.mp3)", "Paste Custom Transcript"],
            index=0
        )

        st.markdown("---")
        st.markdown("### 🧠 Analysis Provider")
        provider = st.selectbox(
            "AI Engine:",
            ["Local NLP & Rule Engine (Offline/No Keys)", "Gemini API", "OpenAI API"],
            index=0
        )

        api_key = ""
        if "Gemini" in provider:
            api_key = st.text_input("Gemini API Key:", type="password", placeholder="AIzaSy...")
        elif "OpenAI" in provider:
            api_key = st.text_input("OpenAI API Key:", type="password", placeholder="sk-...")

        st.markdown("---")
        st.caption(f"QA Passing Threshold: **{QA_PASSING_SCORE}%**")

    # Determine input data based on mode
    active_turns = []
    active_audio_path = None
    call_title = "Inbound Claim Call"
    scenario_type = "Auto FNOL"
    call_id = "CALL-AUTO-001"

    if input_mode == "Pre-loaded Benchmark Calls":
        call_options = {c["title"]: c for c in sample_calls}
        selected_title = st.selectbox(
            "📂 Choose an Insurance Call Scenario:",
            list(call_options.keys()),
            index=0
        )
        selected_call = call_options[selected_title]
        call_id = selected_call["id"]
        call_title = selected_call["title"]
        scenario_type = selected_call.get("scenario_type", "Claim")

        # Map turns to Utterance objects
        active_turns = [
            Utterance(
                speaker=t["speaker"],
                start_time=t.get("start_time"),
                end_time=t.get("end_time"),
                text=t["text"],
                sentiment=t.get("sentiment", "Neutral")
            )
            for t in selected_call.get("transcript", [])
        ]

        # Audio file path
        audio_filename = selected_call.get("audio_filename")
        if audio_filename:
            potential_audio = SAMPLE_AUDIO_DIR / audio_filename
            if potential_audio.exists():
                active_audio_path = str(potential_audio)

    elif input_mode == "Upload Audio File (.wav/.mp3)":
        st.markdown("#### 📤 Upload Recorded Call Audio")
        
        test_audio_dir = BASE_DIR / "test_audio_uploads"
        test_wavs = sorted(list(test_audio_dir.glob("*.wav"))) if test_audio_dir.exists() else []

        st.info(
            f"💡 **Test Audio Files Available:** You can drag & drop your own audio files below, or pick from our pre-generated library located at:\n\n"
            f"`{test_audio_dir}`"
        )

        upload_source = st.radio(
            "Upload Method:",
            ["Choose from Test Audio Library", "Browse / Drag & Drop File from Computer"],
            horizontal=True
        )

        if upload_source == "Choose from Test Audio Library" and test_wavs:
            options = {w.name.replace("_", " ").replace(".wav", "").title(): w for w in test_wavs}
            selected_sample = st.selectbox("🎧 Select a Test Audio File to Analyze:", list(options.keys()))
            chosen_file = options[selected_sample]
            active_audio_path = str(chosen_file)
            call_title = f"Test Audio: {selected_sample}"
            call_id = f"CALL-{chosen_file.stem[:10].upper()}"

            with st.spinner("Processing audio & transcript..."):
                try:
                    active_turns = transcriber.transcribe_audio(active_audio_path)
                    st.success(f"Loaded: `{chosen_file.name}` ({chosen_file.stat().st_size // 1024} KB)")
                except Exception as exc:
                    st.error(str(exc))
                    active_turns = []

        else:
            uploaded_file = st.file_uploader(
                "Choose a call recording (.wav, .mp3, .m4a):",
                type=["wav", "mp3", "m4a"]
            )
            if uploaded_file:
                temp_path = SAMPLE_AUDIO_DIR / f"temp_{uploaded_file.name}"
                SAMPLE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                active_audio_path = str(temp_path)
                st.success(f"Uploaded audio: `{uploaded_file.name}` ({len(uploaded_file.getbuffer())} bytes)")

                with st.spinner("Transcribing audio with speech model..."):
                    try:
                        active_turns = transcriber.transcribe_audio(active_audio_path)
                        call_title = f"Uploaded Call: {uploaded_file.name}"
                        call_id = f"CALL-UPLOAD-{uploaded_file.name[:6].upper()}"
                    except Exception as exc:
                        st.error(str(exc))
                        active_turns = []

    else:
        st.markdown("#### ✍️ Paste Call Transcript")
        sample_paste = """[00:01] Agent: Thank you for calling Apex Mutual. This call is recorded for quality. My name is Mark.
[00:07] Customer: Hi Mark, I had an accident this afternoon. Someone backed into my car at the mall parking lot.
[00:15] Agent: I am sorry to hear that. Could you verify your policy number and address please?
[00:21] Customer: Yes, policy PA-1049281, 123 Oak Street.
[00:27] Agent: Verified. Fraud warning: false claims carry penalties. Any damages or injuries?
[00:35] Customer: No injuries. My front bumper and right headlight are cracked.
[00:41] Agent: Understood. An adjuster will contact you within 24 hours to schedule an inspection."""
        raw_text = st.text_area("Paste conversation transcript below:", value=sample_paste, height=220)
        if raw_text.strip():
            active_turns = transcriber.parse_raw_transcript(raw_text)
            call_title = "User Pasted Transcript"
            call_id = "CALL-CUSTOM-999"

    if not active_turns:
        st.warning("Please select or provide a conversation transcript to analyze.")
        return

    # Run Analysis Engine
    engine_name = "gemini" if "Gemini" in provider else ("openai" if "OpenAI" in provider else "local")
    analyzer = InsuranceCallAnalyzer(api_key=api_key, provider=engine_name)
    audit_record: CallAuditRecord = analyzer.analyze_call(
        turns=active_turns,
        call_id=call_id,
        title=call_title,
        scenario_type=scenario_type,
        audio_path=active_audio_path,
        caller_name=(selected_call.get("caller_name") if input_mode == "Pre-loaded Benchmark Calls" else None),
        policy_number=(selected_call.get("policy_number") if input_mode == "Pre-loaded Benchmark Calls" else None),
        location=(selected_call.get("location") if input_mode == "Pre-loaded Benchmark Calls" else None),
        incident_date=(selected_call.get("incident_date") if input_mode == "Pre-loaded Benchmark Calls" else None),
        incident_time=(selected_call.get("incident_time") if input_mode == "Pre-loaded Benchmark Calls" else None),
    )

    # Top KPI Dashboard
    render_kpi_cards(
        scorecard=audit_record.qa_scorecard,
        red_flags=audit_record.red_flags,
        extraction=audit_record.claim_extraction
    )

    # Audio Playback Banner (if audio exists)
    if active_audio_path and os.path.exists(active_audio_path):
        st.markdown("---")
        ac1, ac2 = st.columns([1, 2])
        with ac1:
            st.markdown("🔊 **Call Audio Recording Player**")
            with open(active_audio_path, "rb") as af:
                st.audio(af.read(), format="audio/wav")
        with ac2:
            st.markdown(f"**Call ID:** `{audit_record.call_id}` | **Policy:** `{audit_record.claim_extraction.insurance_number}` | **Insured:** {audit_record.claim_extraction.claimant_name}")
            st.caption(f"Audio File: `{Path(active_audio_path).name}` | Duration: ~{int(audit_record.duration_seconds)}s | Agent: `{audit_record.agent_id}`")

    st.markdown("---")

    # Main Tabbed Interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎙️ Audio & Transcript",
        "📋 Claim Details",
        "🛡️ QA & Compliance",
        f"🚩 Red Flags ({len(audit_record.red_flags)})"
    ])

    with tab1:
        render_sentiment_trajectory(audit_record.transcript_turns)
        render_transcript_turns(audit_record.transcript_turns)

    with tab2:
        render_claim_entities_table(audit_record.claim_extraction)

    with tab3:
        render_compliance_checklist(audit_record.qa_scorecard)

    with tab4:
        render_red_flags_list(audit_record.red_flags)


if __name__ == "__main__":
    main()
