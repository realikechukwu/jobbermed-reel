#!/usr/bin/env python3
"""Generate weekly JobberMed reel data, narration script, and voiceover."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
WEEKLY_JOBS_PATH = PUBLIC_DIR / "weekly-jobs.json"
SCRIPT_PATH = ROOT / "script.txt"
VOICEOVER_PATH = PUBLIC_DIR / "voiceover.mp3"

DEFAULT_JOBS_URL = "https://jobbermed.com/data/master_jobs.json"
DEFAULT_TIMEZONE = "Europe/London"


def log(message: str) -> None:
    print(f"[generate] {message}", flush=True)


def first_present(job: dict[str, Any], keys: list[str], default: str = "") -> str:
    for key in keys:
        value = job.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            value = value.strip()
        if value:
            return str(value)
    return default


def parse_date(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return None


def fetch_jobs(url: str) -> list[dict[str, Any]]:
    log(f"Fetching jobs from {url}")
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    jobs = payload if isinstance(payload, list) else payload.get("jobs", [])
    if not isinstance(jobs, list) or not jobs:
        raise RuntimeError("Jobs endpoint returned no jobs")

    log(f"Fetched {len(jobs)} jobs")
    return [job for job in jobs if isinstance(job, dict)]


def normalize_job(job: dict[str, Any]) -> dict[str, str]:
    return {
        "title": first_present(
            job,
            ["job_title", "title", "position", "role", "name"],
            "Healthcare Job Opening",
        ),
        "company": first_present(
            job,
            ["company", "organisation", "organization"],
            "JobberMed Partner",
        ),
        "location": first_present(job, ["location"], "Nigeria"),
        "deadline": first_present(
            job,
            ["deadline", "closingDate", "closing_date"],
            "Open",
        ),
        "type": first_present(
            job,
            ["job_type", "type", "employmentType", "employment_type"],
            "Full-time",
        ),
        "_date_posted": first_present(job, ["date_posted", "postedDate", "posted_date"]),
    }


def select_jobs(raw_jobs: list[dict[str, Any]], count: int) -> list[dict[str, str]]:
    normalized = [normalize_job(job) for job in raw_jobs]
    usable = [job for job in normalized if job["title"] and job["company"]]
    if len(usable) < count:
        raise RuntimeError(f"Only found {len(usable)} usable jobs; need {count}")

    def sort_key(job: dict[str, str]) -> tuple[int, datetime, datetime]:
        posted = parse_date(job.get("_date_posted", "")) or datetime.min
        deadline = parse_date(job.get("deadline", "")) or datetime.max
        has_deadline = 0 if job.get("deadline") and job["deadline"] != "Open" else 1
        return (has_deadline, -posted.toordinal(), deadline)

    selected = sorted(usable, key=sort_key)[:count]
    for job in selected:
        job.pop("_date_posted", None)

    log("Selected jobs:")
    for index, job in enumerate(selected, start=1):
        log(
            f"{index}. {job['title']} | {job['company']} | "
            f"{job['location']} | {job['deadline']}"
        )

    return selected


def current_week_of(timezone_name: str) -> str:
    now = datetime.now(timezone.utc).astimezone(ZoneInfo(timezone_name))
    return now.date().isoformat()


def write_weekly_jobs(jobs: list[dict[str, str]], timezone_name: str) -> None:
    weekly = {
        "weekOf": current_week_of(timezone_name),
        "jobs": jobs,
    }
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    WEEKLY_JOBS_PATH.write_text(json.dumps(weekly, indent=2) + "\n", encoding="utf-8")
    log(f"Wrote {WEEKLY_JOBS_PATH.relative_to(ROOT)}")


def build_job_lines(jobs: list[dict[str, str]]) -> str:
    return "\n".join(
        [
            (
                f"{index}. {job['title']} at {job['company']} in "
                f"{job['location']}. Deadline: {job['deadline']}. "
                f"Type: {job['type']}."
            )
            for index, job in enumerate(jobs, start=1)
        ]
    )


def generate_script(client: Any, jobs: list[dict[str, str]], model: str) -> str:
    prompt = f"""You are writing a 45-second Instagram Reel voiceover for JobberMed.

Jobs:
{build_job_lines(jobs)}

Requirements:
- Warm, direct Nigerian healthcare career-advisor tone.
- Mention all three job titles clearly.
- Mention the most useful location or deadline detail for each job.
- End with: Follow @jobbermed for weekly alerts and tap the link in bio.
- Around 120 to 145 words.
- Return only the spoken narration. No labels, headings, bullets, markdown, or emojis."""

    log(f"Generating voiceover script with {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=360,
        temperature=0.75,
    )
    script = response.choices[0].message.content
    if not script:
        raise RuntimeError("OpenAI returned an empty script")

    script = script.strip()
    SCRIPT_PATH.write_text(script + "\n", encoding="utf-8")
    log(f"Wrote {SCRIPT_PATH.relative_to(ROOT)} ({len(script.split())} words)")
    return script


def generate_voiceover(
    client: Any,
    script: str,
    model: str,
    voice: str,
) -> None:
    log(f"Generating voiceover with {model}, voice={voice}")
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=script,
        response_format="mp3",
    )
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    response.stream_to_file(str(VOICEOVER_PATH))

    size_mb = VOICEOVER_PATH.stat().st_size / (1024 * 1024)
    if size_mb <= 0:
        raise RuntimeError("Voiceover file is empty")
    log(f"Wrote {VOICEOVER_PATH.relative_to(ROOT)} ({size_mb:.2f}MB)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs-url", default=os.getenv("JOBS_URL", DEFAULT_JOBS_URL))
    parser.add_argument("--count", type=int, default=int(os.getenv("JOB_COUNT", "3")))
    parser.add_argument("--timezone", default=os.getenv("REEL_TIMEZONE", DEFAULT_TIMEZONE))
    parser.add_argument(
        "--script-model",
        default=os.getenv("OPENAI_SCRIPT_MODEL", "gpt-4o-mini"),
    )
    parser.add_argument("--tts-model", default=os.getenv("OPENAI_TTS_MODEL", "tts-1"))
    parser.add_argument("--tts-voice", default=os.getenv("OPENAI_TTS_VOICE", "nova"))
    parser.add_argument(
        "--skip-openai",
        action="store_true",
        help="Only fetch and write public/weekly-jobs.json; useful for local smoke tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_jobs = fetch_jobs(args.jobs_url)
    selected_jobs = select_jobs(raw_jobs, args.count)
    write_weekly_jobs(selected_jobs, args.timezone)

    if args.skip_openai:
        log("Skipping OpenAI script and voiceover generation")
        return 0

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required")

    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    script = generate_script(client, selected_jobs, args.script_model)
    generate_voiceover(client, script, args.tts_model, args.tts_voice)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"[generate] ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
