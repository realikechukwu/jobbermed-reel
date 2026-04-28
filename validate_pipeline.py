#!/usr/bin/env python3
"""
JobberMed Reel Pipeline Validator
Run: python validate_pipeline.py
Tests each component before you build the full automation.
"""

import os
import json
import subprocess
import sys
import time
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JOBS_URL = os.getenv("JOBS_URL", "https://jobbermed.com/data/master_jobs.json")

# ── Colours for terminal output ──────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}")
def info(msg):  print(f"  {CYAN}→{RESET} {msg}")
def header(msg):print(f"\n{BOLD}{YELLOW}[ {msg} ]{RESET}")

def first_present(job, keys, default=""):
    for key in keys:
        value = job.get(key)
        if value:
            return value
    return default

# ── Test 1: Environment ───────────────────────────────────────────────────────
def test_environment():
    header("TEST 1: Environment & Dependencies")
    passed = True

    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        ok("OPENAI_API_KEY found")
    else:
        fail("OPENAI_API_KEY missing or malformed in .env")
        passed = False

    # Check Python packages
    for pkg in ["openai", "requests", "dotenv"]:
        try:
            __import__(pkg if pkg != "dotenv" else "dotenv")
            ok(f"Python package '{pkg}' available")
        except ImportError:
            fail(f"Python package '{pkg}' not installed — run: pip install {pkg}")
            passed = False

    # Check Node.js (needed for Remotion later)
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        ok(f"Node.js available: {result.stdout.strip()}")
    else:
        fail("Node.js not found — install from nodejs.org")
        passed = False

    # Check npm
    result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        ok(f"npm available: {result.stdout.strip()}")
    else:
        fail("npm not found")
        passed = False

    return passed

# ── Test 2: Job Fetching ──────────────────────────────────────────────────────
def test_job_fetching():
    header("TEST 2: Job Fetching from JobberMed")
    import requests

    try:
        info(f"Fetching from {JOBS_URL}")
        response = requests.get(JOBS_URL, timeout=10)
        response.raise_for_status()
        jobs = response.json()

        # Handle both list and dict response shapes
        job_list = jobs if isinstance(jobs, list) else jobs.get("jobs", [])

        if not job_list:
            fail("Jobs endpoint returned empty list")
            return False, []

        ok(f"Fetched {len(job_list)} jobs successfully")

        # Pick 3 with deadlines if possible
        with_deadline = [j for j in job_list if j.get("deadline") or j.get("closingDate")]
        pool = with_deadline if len(with_deadline) >= 3 else job_list
        selected = random.sample(pool, min(3, len(pool)))

        ok(f"Selected {len(selected)} jobs for reel")
        for i, job in enumerate(selected, 1):
            title    = first_present(job, ["job_title", "title", "position", "role", "name"], "Unknown Title")
            company  = first_present(job, ["company", "organisation", "organization"], "Unknown")
            location = first_present(job, ["location"], "Nigeria")
            deadline = first_present(job, ["deadline", "closingDate", "closing_date"], "Open")
            jtype    = first_present(job, ["job_type", "type", "employmentType", "employment_type"], "Full-time")
            info(f"  Job {i}: {title} | {company} | {location} | Closes {deadline}")

        # Save for next steps
        weekly = {
            "weekOf": time.strftime("%Y-%m-%d"),
            "jobs": [
                {
                    "title":    first_present(j, ["job_title", "title", "position", "role", "name"], "Healthcare Job Opening"),
                    "company":  first_present(j, ["company", "organisation", "organization"], ""),
                    "location": first_present(j, ["location"], "Nigeria"),
                    "deadline": first_present(j, ["deadline", "closingDate", "closing_date"], "Open"),
                    "type":     first_present(j, ["job_type", "type", "employmentType", "employment_type"], "Full-time")
                }
                for j in selected
            ]
        }
        Path("data").mkdir(exist_ok=True)
        with open("data/weekly-jobs.json", "w") as f:
            json.dump(weekly, f, indent=2)
        ok("Saved data/weekly-jobs.json")
        return True, weekly["jobs"]

    except Exception as e:
        fail(f"Job fetch failed: {e}")
        return False, []

# ── Test 3: Script Generation ─────────────────────────────────────────────────
def test_script_generation(jobs):
    header("TEST 3: GPT Script Generation")
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    job_lines = "\n".join([
        f"- {j['title']} at {j['company']}, {j['location']}. Closes {j['deadline']}"
        for j in jobs
    ])

    prompt = f"""You are a friendly Nigerian healthcare career advisor.
Write a 45-second Instagram Reel voiceover script for these 3 jobs:

{job_lines}

Format:
- Hook (5 sec): attention-grabbing opening line
- Job 1 (10 sec): title, location, one exciting detail
- Job 2 (10 sec): same
- Job 3 (10 sec): same
- CTA (10 sec): follow @jobbermed for weekly alerts, link in bio

Tone: warm, energetic, like a friend tipping you off.
No emojis. Conversational, clear. Approximately 130 words total."""

    try:
        info("Calling GPT-4o-mini...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        script = response.choices[0].message.content.strip()
        ok(f"Script generated ({len(script.split())} words)")

        print(f"\n{CYAN}--- SCRIPT PREVIEW ---{RESET}")
        print(script)
        print(f"{CYAN}----------------------{RESET}\n")

        Path("data").mkdir(exist_ok=True)
        with open("data/script.txt", "w") as f:
            f.write(script)
        ok("Saved data/script.txt")
        return True, script

    except Exception as e:
        fail(f"Script generation failed: {e}")
        return False, ""

# ── Test 4: TTS Generation ────────────────────────────────────────────────────
def test_tts_generation(script):
    header("TEST 4: Text-to-Speech (OpenAI TTS)")
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        info("Generating voiceover with OpenAI TTS (voice: nova)...")
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",       # warm female voice — good for this content
            input=script,
            response_format="mp3"
        )

        Path("public").mkdir(exist_ok=True)
        output_path = Path("public/voiceover.mp3")
        response.stream_to_file(str(output_path))

        size_kb = output_path.stat().st_size / 1024
        ok(f"Voiceover saved to public/voiceover.mp3 ({size_kb:.1f} KB)")

        if size_kb < 5:
            fail("File seems too small — may be empty or corrupt")
            return False

        # Try to play it (macOS / Linux)
        info("Attempting playback (5 seconds)...")
        if sys.platform == "darwin":
            subprocess.run(["afplay", str(output_path)], timeout=10,
                           capture_output=True)
            ok("Played on macOS (afplay)")
        elif sys.platform.startswith("linux"):
            subprocess.run(["aplay", str(output_path)], timeout=10,
                           capture_output=True)
            ok("Played on Linux (aplay)")
        else:
            info("Auto-play not supported on Windows — open public/voiceover.mp3 manually")

        return True

    except Exception as e:
        fail(f"TTS generation failed: {e}")
        return False

# ── Test 5: Remotion Check ────────────────────────────────────────────────────
def test_remotion_setup():
    header("TEST 5: Remotion Environment Check")
    info("Checking if jobbermed-reel directory exists...")

    reel_dir = Path("jobbermed-reel")
    if not reel_dir.exists():
        info("jobbermed-reel/ not found — skipping render test")
        info("Once Codex generates the project, re-run this script")
        info("to do a full render test")
        return None  # Not a failure, just not built yet

    # Check node_modules
    if not (reel_dir / "node_modules").exists():
        info("node_modules not found — running npm install...")
        result = subprocess.run(["npm", "install"], cwd=reel_dir,
                                capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"npm install failed: {result.stderr}")
            return False
        ok("npm install complete")

    # Install Remotion browser
    info("Installing Remotion browser (first time is slow ~200MB)...")
    result = subprocess.run(
        ["npx", "remotion", "install-browser"],
        cwd=reel_dir, capture_output=True, text=True, timeout=300
    )
    if result.returncode == 0:
        ok("Remotion browser ready")
    else:
        fail(f"Browser install failed: {result.stderr[:200]}")
        return False

    # Attempt render
    info("Running test render (this takes ~2-3 minutes)...")
    props_path = Path("../data/weekly-jobs.json").resolve()
    result = subprocess.run([
        "npx", "remotion", "render",
        "src/Root.tsx", "JobberMedReel",
        f"--props={props_path}",
        "--output=../output/reel-test.mp4"
    ], cwd=reel_dir, capture_output=True, text=True, timeout=600)

    if result.returncode == 0:
        output = Path("output/reel-test.mp4")
        if output.exists():
            size_mb = output.stat().st_size / (1024 * 1024)
            ok(f"Render successful: output/reel-test.mp4 ({size_mb:.1f} MB)")
            return True
        else:
            fail("Render exited 0 but no output file found")
            return False
    else:
        fail(f"Render failed:\n{result.stderr[-500:]}")
        return False

# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary(results):
    header("SUMMARY")
    labels = [
        "Environment & Dependencies",
        "Job Fetching",
        "Script Generation",
        "TTS Generation",
        "Remotion Setup"
    ]
    all_passed = True
    for label, result in zip(labels, results):
        if result is True:
            print(f"  {GREEN}✓{RESET} {label}")
        elif result is False:
            print(f"  {RED}✗{RESET} {label}")
            all_passed = False
        else:
            print(f"  {YELLOW}–{RESET} {label} (skipped — not built yet)")

    print()
    if all_passed:
        print(f"{GREEN}{BOLD}All tests passed. Pipeline is ready.{RESET}")
    else:
        print(f"{RED}{BOLD}Some tests failed. Fix above errors before building.{RESET}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}JobberMed Reel Pipeline Validator{RESET}")
    print("=" * 40)

    r1       = test_environment()
    r2, jobs = test_job_fetching()

    if not jobs:
        # Use dummy jobs so remaining tests still run
        jobs = [
            {"title": "Medical Officer", "company": "Test Hospital",
             "location": "Lagos, Nigeria", "deadline": "1 May 2026", "type": "Full-time"},
            {"title": "Registered Nurse", "company": "City Clinic",
             "location": "Abuja, Nigeria", "deadline": "10 May 2026", "type": "Full-time"},
            {"title": "Pharmacist", "company": "HealthPlus",
             "location": "Port Harcourt", "deadline": "15 May 2026", "type": "Full-time"},
        ]
        info("Using dummy jobs for remaining tests")

    r3, script = test_script_generation(jobs)
    r4         = test_tts_generation(script) if script else False
    r5         = test_remotion_setup()

    print_summary([r1, r2, r3, r4, r5])
