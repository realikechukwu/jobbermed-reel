#!/usr/bin/env python3
"""Send the rendered JobberMed reel as a Gmail attachment."""

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_PATH = ROOT / "out" / "jobbermed-reel.mp4"
DEFAULT_MAX_MB = 18.0


def log(message: str) -> None:
    print(f"[email] {message}", flush=True)


def parse_recipients(value: str) -> list[str]:
    recipients = [item.strip() for item in value.replace(";", ",").split(",")]
    return [item for item in recipients if item]


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def build_message(
    sender: str,
    recipients: list[str],
    subject: str,
    body: str,
    video_path: Path,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    content_type, _ = mimetypes.guess_type(video_path.name)
    if content_type:
        maintype, subtype = content_type.split("/", 1)
    else:
        maintype, subtype = "video", "mp4"

    message.add_attachment(
        video_path.read_bytes(),
        maintype=maintype,
        subtype=subtype,
        filename=video_path.name,
    )
    return message


def send_message(message: EmailMessage, user: str, password: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    log(f"Connecting to {smtp_host}:{smtp_port}")
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
        smtp.login(user, password)
        smtp.send_message(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default=os.getenv("REEL_VIDEO_PATH", str(DEFAULT_VIDEO_PATH)))
    parser.add_argument("--max-mb", type=float, default=float(os.getenv("MAX_ATTACHMENT_MB", DEFAULT_MAX_MB)))
    parser.add_argument(
        "--subject",
        default=os.getenv("MAIL_SUBJECT", "JobberMed Weekly Reel"),
    )
    parser.add_argument(
        "--body",
        default=os.getenv(
            "MAIL_BODY",
            "Attached is this week's JobberMed Weekly Reel.",
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_path = Path(args.video).resolve()
    if not video_path.exists():
        raise RuntimeError(f"Video file not found: {video_path}")

    size_mb = video_path.stat().st_size / (1024 * 1024)
    log(f"Video size: {size_mb:.2f}MB")
    if size_mb > args.max_mb:
        raise RuntimeError(
            f"Video is {size_mb:.2f}MB, above the {args.max_mb:.2f}MB email limit"
        )

    user = require_env("GMAIL_USER")
    password = require_env("GMAIL_APP_PASSWORD")
    recipients = parse_recipients(require_env("MAIL_TO"))
    sender = os.getenv("MAIL_FROM", user).strip() or user

    message = build_message(
        sender=sender,
        recipients=recipients,
        subject=args.subject,
        body=args.body,
        video_path=video_path,
    )
    send_message(message, user, password)
    log(f"Sent {video_path.name} to {', '.join(recipients)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"[email] ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
