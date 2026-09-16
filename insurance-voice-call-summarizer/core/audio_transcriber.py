"""
Audio Transcription and Speaker Turn Pipeline.
Handles audio ingestion (.wav, .mp3), Whisper transcription, speaker role tagging, and sentiment analysis.
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from core.models import Utterance


class AudioTranscriber:
    """Manages audio file loading, speech recognition, and conversation turn extraction."""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._whisper_model = None

    def _get_whisper_model(self):
        if self._whisper_model is None:
            try:
                import whisper
                self._whisper_model = whisper.load_model(self.model_name)
            except Exception as e:
                print(f"[Warning] Could not load Whisper model '{self.model_name}': {e}")
                self._whisper_model = None
        return self._whisper_model


    def transcribe_audio(self, audio_file_path: str) -> List[Utterance]:
        """
        Transcribes audio using Whisper if available and raises a clear error if it fails.
        This intentionally avoids silently substituting synthetic transcript text.
        """
        path = Path(audio_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        model = self._get_whisper_model()
        last_error = None

        if model is not None:
            try:
                result = model.transcribe(str(path))
                raw_segments = result.get("segments", [])
                if raw_segments:
                    return self._segments_to_utterances(raw_segments)

                full_text = (result.get("text") or "").strip()
                if full_text:
                    return [
                        Utterance(
                            speaker="Customer",
                            start_time=0.0,
                            end_time=max(2.5, len(full_text.split()) * 0.4),
                            text=full_text,
                            sentiment=self.detect_turn_sentiment(full_text),
                        )
                    ]

                raise ValueError("Whisper returned no usable transcription text.")
            except Exception as e:
                last_error = e
                print(f"[Warning] Whisper transcription failed for '{path.name}': {e}")

        # Fallback if audio file has an accompanying .txt transcript
        fallback_txt = path.with_suffix(".txt")
        if fallback_txt.exists():
            with open(fallback_txt, "r", encoding="utf-8") as f:
                return self.parse_raw_transcript(f.read())

        error_message = (
            "Whisper transcription failed. Please upload a clean audio recording and ensure "
            "ffmpeg and the Whisper model are installed correctly."
        )
        raise RuntimeError(error_message) from last_error

    def _segments_to_utterances(self, segments: list) -> List[Utterance]:
        """Maps Whisper raw segments to structured Utterance objects with speaker roles."""
        utterances = []
        # First turn is typically Agent greeting
        current_speaker = "Agent"

        for i, seg in enumerate(segments):
            text = seg.get("text", "").strip()
            if not text:
                continue

            # Heuristic speaker turn alternation if gap > 0.8s or question/answer pattern
            if i > 0:
                prev_text = segments[i-1].get("text", "").strip()
                prev_end = segments[i-1].get("end", 0.0)
                curr_start = seg.get("start", 0.0)
                
                # Check turn shift triggers
                is_question = prev_text.endswith("?") or any(w in prev_text.lower() for w in ["what", "how", "when", "where", "can you", "could you"])
                silence_gap = (curr_start - prev_end) > 0.8

                if is_question or silence_gap:
                    current_speaker = "Customer" if current_speaker == "Agent" else "Agent"

            sentiment = self.detect_turn_sentiment(text)
            utterances.append(Utterance(
                speaker=current_speaker,
                start_time=round(seg.get("start", 0.0), 1),
                end_time=round(seg.get("end", 0.0), 1),
                text=text,
                sentiment=sentiment
            ))

        return utterances

    def parse_raw_transcript(self, raw_text: str) -> List[Utterance]:
        """
        Parses transcripts formatted like:
        [00:04] Agent: Thank you for calling...
        Customer: Hi I had an accident...
        """
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
        utterances: List[Utterance] = []
        current_time = 0.0

        for line in lines:
            # Check for timestamp pattern like [00:15] or [01:23]
            time_match = re.match(r"^\[(\d{1,2}):(\d{2})\]\s*(.*)", line)
            speaker = "Customer"
            text = line
            start_t = current_time

            if time_match:
                mins, secs = int(time_match.group(1)), int(time_match.group(2))
                start_t = mins * 60 + secs
                text = time_match.group(3)

            # Check for Speaker prefix like "Agent:" or "Customer:" or "Alex:"
            speaker_match = re.match(r"^(Agent|Customer|Representative|Caller|Insured|Adjuster):\s*(.*)", text, re.IGNORECASE)
            if speaker_match:
                raw_speaker = speaker_match.group(1).capitalize()
                speaker = "Agent" if raw_speaker in ["Agent", "Representative", "Adjuster"] else "Customer"
                text = speaker_match.group(2)

            sentiment = self.detect_turn_sentiment(text)
            end_t = start_t + max(2.5, len(text.split()) * 0.4)
            current_time = end_t + 0.5

            utterances.append(Utterance(
                speaker=speaker,
                start_time=round(start_t, 1),
                end_time=round(end_t, 1),
                text=text.strip(),
                sentiment=sentiment
            ))

        return utterances

    @staticmethod
    def detect_turn_sentiment(text: str) -> str:
        """Heuristic sentiment scorer for an utterance."""
        t_low = text.lower()
        negative_signals = [
            "accident", "crash", "damage", "hurt", "injured", "pain", "terrible", "awful",
            "frustrated", "upset", "angry", "lawyer", "attorney", "sue", "unacceptable",
            "ridiculous", "complaint", "ruined", "broken", "burst", "leaking", "stolen",
            "hit", "whiplash", "refuse", "cancel"
        ]
        positive_signals = [
            "thank you", "thanks", "great", "helpful", "appreciate", "relieved", "glad",
            "perfect", "sounds good", "excellent", "understand", "wonderful"
        ]

        pos_count = sum(1 for w in positive_signals if w in t_low)
        neg_count = sum(1 for w in negative_signals if w in t_low)

        if neg_count > pos_count:
            return "Negative"
        elif pos_count > neg_count:
            return "Positive"
        return "Neutral"
