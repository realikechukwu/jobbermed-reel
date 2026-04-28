# JobberMed Weekly Reel Automation Process

## Comprehensive Plan

1. Keep the existing Remotion app as the renderer and avoid changing composition, timing, data consumption, audio playback, or scene logic.
2. Add a production asset-generation script that runs in CI. It will fetch JobberMed jobs, normalize the current `job_title`/`job_type` field names, choose three usable jobs, write `public/weekly-jobs.json`, generate `script.txt`, and generate `public/voiceover.mp3`.
3. Add an email delivery script that checks the rendered MP4 size before sending. It will refuse to send files over 18MB so Gmail attachment encoding does not push the message over the practical limit.
4. Add Python requirements needed by the automation scripts.
5. Add a GitHub Actions workflow that runs every Wednesday at 9am Europe/London, can also be run manually, installs dependencies, generates assets, renders the reel, checks/compresses the output, sends the email, and uploads workflow artifacts for debugging.
6. Run local syntax and project checks without calling external APIs, because secrets are not available locally in this workspace.

## Step 1 - Repo Audit

What I did:
- Inspected the top-level project files, `package.json`, `.gitignore`, and current git status.
- Confirmed the Remotion app already reads `public/weekly-jobs.json` and plays `public/voiceover.mp3`.
- Confirmed there is no production automation outside `validate_pipeline.py`; the current app itself does not generate scripts or audio.

Challenges:
- The worktree already contains many uncommitted changes from the Remotion replacement and later visual/data edits. I left those intact and treated them as user-requested existing work.
- A generated `build/` folder exists locally but is ignored.

Bypass:
- I am adding automation around the existing app instead of restructuring current Remotion source files.

Residual issues:
- You still need to commit the current Remotion app state together with the new automation files.

## Step 2 - Asset Generation Script

What I did:
- Added `scripts/generate_reel_assets.py`.
- The script fetches jobs from `https://jobbermed.com/data/master_jobs.json` by default.
- It normalizes JobberMed's current fields, including `job_title` for the reel title and `job_type` for the employment type.
- It selects three usable jobs, writes `public/weekly-jobs.json`, generates `script.txt`, and generates `public/voiceover.mp3`.
- It supports environment overrides for `JOBS_URL`, `JOB_COUNT`, `REEL_TIMEZONE`, `OPENAI_SCRIPT_MODEL`, `OPENAI_TTS_MODEL`, and `OPENAI_TTS_VOICE`.
- It has a `--skip-openai` mode for local smoke tests that only fetches jobs and writes the weekly JSON.

Challenges:
- The original validator used `title` and `type`, but the live JobberMed endpoint uses `job_title` and `job_type`.
- The Remotion app consumes `public/weekly-jobs.json`, while the validator wrote to `data/weekly-jobs.json`.

Bypass:
- The new production script writes directly to `public/weekly-jobs.json` and keeps fallbacks for older field names.
- I used standard-library HTTP fetching so the only required Python package for generation is the OpenAI SDK.

Residual issues:
- The script needs `OPENAI_API_KEY` in GitHub Secrets before full generation can run.
- Job selection is deterministic: it prefers jobs with deadlines, then newest posted jobs. If you want editorial/random selection later, that should be a deliberate change.

## Step 3 - Gmail Delivery Script

What I did:
- Added `scripts/send_reel_email.py`.
- The script reads `out/jobbermed-reel.mp4` by default.
- It checks the raw MP4 size before sending and fails if the video is over 18MB.
- It sends through Gmail SMTP using `GMAIL_USER`, `GMAIL_APP_PASSWORD`, and `MAIL_TO`.
- It supports optional overrides: `MAIL_FROM`, `MAIL_SUBJECT`, `MAIL_BODY`, `SMTP_HOST`, `SMTP_PORT`, `REEL_VIDEO_PATH`, and `MAX_ATTACHMENT_MB`.

Challenges:
- Gmail allows 25MB for personal-account attachments, but email MIME encoding increases attachment size. Sending a raw file close to 25MB can fail after encoding.

Bypass:
- I set the automation guard to 18MB. This gives enough headroom for encoding overhead and keeps the workflow behavior predictable.

Residual issues:
- You need to create a Gmail App Password and add it as `GMAIL_APP_PASSWORD` in GitHub Secrets.
- If the output remains above 18MB after compression, the email step will fail instead of silently sending a Drive link.

## Step 4 - GitHub Actions Workflow and Requirements

What I did:
- Added `requirements.txt` with the OpenAI Python SDK dependency.
- Added `.github/workflows/weekly-reel.yml`.
- The workflow runs on a schedule every Wednesday at 9am Europe/London and also supports manual `workflow_dispatch` runs.
- The workflow installs Node and Python dependencies, ensures the Remotion browser is available, generates weekly assets, renders the reel, compresses it with `ffmpeg`, verifies it is under 18MB, sends it by Gmail, and uploads artifacts for debugging.

Challenges:
- A 45-second 1080x1920 MP4 can exceed Gmail's practical attachment budget if rendered at high bitrate.
- Email attachment encoding adds overhead, so targeting Gmail's 25MB limit directly is risky.

Bypass:
- The workflow renders a raw Remotion MP4 first, then re-encodes to H.264/AAC with a conservative bitrate target and checks the resulting file against an 18MB hard limit before sending.
- Artifacts are uploaded with `if: always()` so you can inspect generated data/audio/video when a later step fails.

Residual issues:
- You must add these GitHub Actions secrets before the scheduled run can work: `OPENAI_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, and `MAIL_TO`.
- If the render still exceeds 18MB, reduce the workflow's `-b:v 2800k` value, for example to `2400k`.

## Step 5 - Local Validation

What I did:
- Ran Python syntax checks:
  - `python -m py_compile scripts/generate_reel_assets.py scripts/send_reel_email.py validate_pipeline.py`
- Ran the existing Remotion project check:
  - `npm run lint`
- Added `__pycache__` to `.gitignore` because Python syntax checks create local cache folders.

Challenges:
- I could not safely run the full workflow locally because it requires real GitHub/Gmail/OpenAI secrets and would regenerate live assets.
- Running the full render/email path locally would also send an email, which should only happen after you add the intended secrets.

Bypass:
- I limited local validation to syntax, TypeScript, and ESLint checks.
- The workflow includes `workflow_dispatch`, so after you push and add secrets you can manually trigger one test run before waiting for Wednesday.

Residual issues:
- The first real end-to-end test should be a manual GitHub Actions run.
- Confirm the sent attachment lands in Gmail and remains under 18MB after GitHub's render/compression environment runs it.
- Your git status still includes prior uncommitted Remotion replacement files and root assets; review and commit the complete intended state.
