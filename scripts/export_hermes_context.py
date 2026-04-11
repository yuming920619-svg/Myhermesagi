#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

HOME = Path.home()
REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = REPO_ROOT / "hermes-context"

SOURCES = {
    "SOUL.md": HOME / ".hermes" / "SOUL.md",
    "USER.md": HOME / ".hermes" / "memories" / "USER.md",
    "MEMORY.md": HOME / ".hermes" / "memories" / "MEMORY.md",
}


def mask_email(text: str) -> str:
    return re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[redacted-email]",
        text,
    )


def mask_telegram_user_id(text: str) -> str:
    return re.sub(
        r"(Telegram user ID is )\d+( for Hermes gateway allowlist\.)",
        r"\1[redacted-telegram-id]\2",
        text,
    )


def mask_github_tokens(text: str) -> str:
    patterns = [
        r"github_pat_[A-Za-z0-9_]+",
        r"\bghp_[A-Za-z0-9]+\b",
        r"\bgho_[A-Za-z0-9]+\b",
        r"\bghu_[A-Za-z0-9]+\b",
        r"\bghs_[A-Za-z0-9]+\b",
        r"\bghr_[A-Za-z0-9]+\b",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "[redacted-github-token]", text)
    return text


def sanitize(text: str) -> str:
    text = mask_email(text)
    text = mask_telegram_user_id(text)
    text = mask_github_tokens(text)
    return text


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    exported = []
    for name, source in SOURCES.items():
        if not source.exists():
            continue
        content = source.read_text(encoding="utf-8")
        sanitized = sanitize(content)
        target = TARGET_DIR / name
        target.write_text(sanitized, encoding="utf-8")
        exported.append(target)

    readme = TARGET_DIR / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Hermes Context Snapshots\n\nPublic sanitized snapshots exported from ~/.hermes/.\n",
            encoding="utf-8",
        )

    for path in exported:
        print(path)


if __name__ == "__main__":
    main()
