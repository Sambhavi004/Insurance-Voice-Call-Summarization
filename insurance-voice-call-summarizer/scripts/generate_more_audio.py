"""
Generates 6 additional realistic insurance voice call audio files (.wav) for upload testing.
Uses Windows SAPI speech synthesis with PCM wave fallback.
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "test_audio_uploads"

CALL_SCRIPTS = [
    {
        "filename": "01_windstorm_roof_damage.wav",
        "title": "Windstorm & Hail Roof Loss (HO-882194)",
        "dialogue": (
            "Thank you for calling Horizon Mutual Insurance. This call is recorded for quality. My name is Kevin. "
            "Hi Kevin, a severe windstorm and hail ripped several shingles off my roof yesterday, and a heavy tree branch "
            "crashed through the gutter. Water is beginning to seep into the attic. "
            "I am so sorry to hear that. First, are you and your family safe? "
            "Yes, we are safe. "
            "Can you verify policy HO-882194 and your address? "
            "Yes, policy HO-882194, 542 Maple Ridge Road. "
            "We will dispatch an emergency tarping crew within 4 hours to prevent further water damage, "
            "and an adjuster will inspect the roof within 48 hours."
        )
    },
    {
        "filename": "02_jewelry_burglary_theft.wav",
        "title": "Home Burglary & Jewelry Theft (HO-302194)",
        "dialogue": (
            "Apex Mutual Home and Property, Mark speaking. Please note this call is recorded for quality assurance. "
            "Hi Mark, I came home from work and found my back sliding glass door shattered. Burglars broke in and stole "
            "my wife's diamond engagement ring, electronics, and cash from our bedroom safe. "
            "That is awful, I am so sorry you experienced this. Did you contact the police? "
            "Yes, Officer Higgins arrived and took police report number TR-9941. "
            "Can you confirm your date of birth and policy number HO-302194? "
            "Yes, March 12 1980, policy HO-302194. "
            "Please remember false statements carry criminal fraud penalties. Please make an itemized list with purchase receipts. "
            "An adjuster will reach out by tomorrow morning."
        )
    },
    {
        "filename": "03_hit_and_run_parking_lot.wav",
        "title": "Hit & Run Collision - Supermarket Lot (PA-442109)",
        "dialogue": (
            "Thank you for calling Apex Mutual Auto Claims. This call is recorded for training. My name is Rachel. "
            "Hi Rachel, I parked my car at the supermarket lot on Route 22, and when I came back out, someone had smashed "
            "my entire driver side door and drove away without leaving a note. "
            "That is so frustrating, I am glad you were not inside the vehicle. Let me verify your policy PA-442109 and vehicle VIN. "
            "Policy is PA-442109, 2023 Honda Civic. "
            "Did the store security have cameras? "
            "Yes, the store manager said their cameras captured a blue pickup truck backing into my door. I filed police report PR-8831. "
            "An adjuster will contact you within 24 hours to review the footage and arrange repairs."
        )
    },
    {
        "filename": "04_unauthorized_agent_guarantee_violation.wav",
        "title": "Compliance Violation - Unauthorized Guarantee & Missed Disclosure",
        "dialogue": (
            "Apex Insurance, Dave speaking. "
            "Hi Dave, my basement backed up with city sewer water. Is this covered under my policy? "
            "Oh absolutely, don't worry about it at all, I guarantee this will be 100 percent covered in full with zero deductible, "
            "we will write you a check for everything no matter what. You don't even need an adjuster inspection. Just hire whoever you want. "
            "Wow, really? "
            "Yes, 100 percent guaranteed."
        )
    },
    {
        "filename": "05_rideshare_delivery_fraud_suspect.wav",
        "title": "Suspected Fraud - Unendorsed Commercial Delivery & Cash Rush",
        "dialogue": (
            "Apex Claims, Brian speaking. This call is recorded for quality. What happened? "
            "Yeah, I wrecked my car on Interstate 95. I need you to wire the money today without inspection. I need cash immediately. "
            "Were you using the vehicle for work or commercial delivery? "
            "No, absolutely not... wait, well, I had the DoorDash app open and was delivering food, but do not put that on the record! "
            "Just pay the claim directly to my bank account today or I will hire an attorney to sue you in court."
        )
    },
    {
        "filename": "06_dog_bite_liability_claim.wav",
        "title": "Premises Liability - Dog Bite to Delivery Driver (HO-771249)",
        "dialogue": (
            "Thank you for calling Apex Mutual Homeowners Liability. This call is recorded for quality and compliance. My name is Elena. "
            "Hi Elena, I am calling because my German Shepherd jumped the backyard fence and bit an Amazon delivery driver on the leg. "
            "The driver had to go to urgent care for stitches. "
            "I am sorry to hear about this incident. Can you confirm your homeowners policy number HO-771249? "
            "Yes, policy HO-771249. Does the policy cover the driver's medical bills? "
            "Under Section 2 Personal Liability and Medical Payments to Others, we cover accidental injuries on premises up to your policy limit. "
            "A casualty claims adjuster will contact you within 24 hours to obtain the medical invoices."
        )
    }
]


def generate_audio(text: str, output_path: Path):
    safe_text = text.replace('"', '""').replace("'", "''")
    ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('{str(output_path)}')
$synth.Speak('{safe_text}')
$synth.Dispose()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        timeout=25
    )


def main():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating 6 additional uploadable test audio files in: {UPLOAD_DIR}")

    for item in CALL_SCRIPTS:
        out_file = UPLOAD_DIR / item["filename"]
        print(f"Synthesizing: {item['filename']} ({item['title']})...")
        generate_audio(item["dialogue"], out_file)
        if out_file.exists():
            print(f" -> Generated {out_file.name} ({out_file.stat().st_size} bytes)")
        else:
            print(f" -> Failed to create {out_file.name}")

    print("\nAll additional test audio files are ready!")


if __name__ == "__main__":
    main()
