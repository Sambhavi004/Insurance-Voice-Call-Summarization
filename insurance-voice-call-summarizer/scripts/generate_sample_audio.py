"""
Script to generate sample audio files (.wav) for demoing call playback and Whisper ASR.
Uses Windows Speech Synthesis (SAPI) if available, with a clean PCM wave fallback.
"""

import json
import os
import subprocess
import wave
import math
import struct
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CALLS_FILE = BASE_DIR / "data" / "sample_calls.json"
AUDIO_DIR = BASE_DIR / "data" / "sample_audio"


def generate_sapi_audio(text: str, output_wav: Path) -> bool:
    """Attempts to synthesize spoken voice using Windows SAPI via PowerShell."""
    try:
        # Sanitize text for powershell
        safe_text = text.replace('"', '""').replace("'", "''")
        ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('{str(output_wav)}')
$synth.Speak('{safe_text[:500]}')
$synth.Dispose()
"""
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15
        )
        return output_wav.exists() and output_wav.stat().st_size > 1000
    except Exception as e:
        print(f"[Notice] SAPI synthesis error: {e}")
        return False


def generate_synthetic_pcm_wav(output_wav: Path, duration_seconds: float = 6.0):
    """Fallback generator that creates a clean modulated voice-band PCM .wav file."""
    sample_rate = 16000
    n_samples = int(sample_rate * duration_seconds)
    with wave.open(str(output_wav), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate harmonic speech-formant like tone
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            # 220Hz fundamental + 440Hz harmonic + 880Hz formant with envelope modulation
            envelope = 0.5 * (1.0 + math.sin(2 * math.pi * 3 * t))
            val = envelope * (
                0.5 * math.sin(2 * math.pi * 220 * t) +
                0.3 * math.sin(2 * math.pi * 440 * t) +
                0.2 * math.sin(2 * math.pi * 880 * t)
            )
            val_int = int(max(-32767, min(32767, val * 20000)))
            frames.extend(struct.pack("<h", val_int))
        wav_file.writeframes(frames)


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_CALLS_FILE.exists():
        print(f"Error: {SAMPLE_CALLS_FILE} not found.")
        return

    with open(SAMPLE_CALLS_FILE, "r", encoding="utf-8") as f:
        calls = json.load(f)

    for call in calls:
        filename = call.get("audio_filename", f"{call['id'].lower()}.wav")
        out_path = AUDIO_DIR / filename
        if out_path.exists():
            print(f"Audio already exists: {out_path.name}")
            continue

        transcript_text = " ".join(t["text"] for t in call["transcript"][:3])
        print(f"Generating audio for {call['id']} -> {filename}...")

        success = generate_sapi_audio(transcript_text, out_path)
        if not success:
            print(f"Using PCM wave generator for {filename}...")
            generate_synthetic_pcm_wav(out_path, duration_seconds=8.0)

        print(f"Created: {out_path.name} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
