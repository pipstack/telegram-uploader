import asyncio
import os
import sys
from pathlib import Path

from telethon import TelegramClient


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

SESSION_PATH = "/data/telegram"
FILE_DIR = Path("/files")


def progress_callback(current, total):
    percent = current * 100 / total if total else 0

    bar_width = 30
    filled = int(bar_width * current / total) if total else 0
    bar = "█" * filled + "░" * (bar_width - filled)

    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    print(
        f"\r[{bar}] {percent:6.2f}% "
        f"| {current_mb:,.1f} / {total_mb:,.1f} MB",
        end="",
        flush=True,
    )


def resolve_file(file_arg: str) -> Path:
    path = Path(file_arg)

    # Only relative paths are accepted.
    if path.is_absolute():
        raise ValueError("Absolute paths are not allowed. Use a path relative to /files.")

    resolved = (FILE_DIR / path).resolve()

    # Prevent escaping the /files directory using ../
    try:
        resolved.relative_to(FILE_DIR.resolve())
    except ValueError:
        raise ValueError("Path must stay inside /files.")

    return resolved


async def upload_file(file_arg: str):
    try:
        path = resolve_file(file_arg)
    except ValueError as error:
        print(f"✗ {error}")
        return 1

    if not path.exists():
        print(f"✗ File not found: {path.relative_to(FILE_DIR)}")
        return 1

    if not path.is_file():
        print(f"✗ Not a file: {path.relative_to(FILE_DIR)}")
        return 1

    relative_path = path.relative_to(FILE_DIR)

    print(f"📤 Uploading: {relative_path}")
    print()

    async with TelegramClient(SESSION_PATH, API_ID, API_HASH) as client:
        await client.send_file(
            "me",
            str(path),
            force_document=True,
            progress_callback=progress_callback,
        )

    print()
    print()
    print(f"✓ Upload complete: {relative_path}")
    print("📍 Telegram Saved Messages")

    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage: telegram-upload <file>")
        print()
        print("The file path must be relative to /files.")
        print()
        print("Examples:")
        print("  telegram-upload movie.mkv")
        print("  telegram-upload videos/movie.mkv")
        return 1

    return asyncio.run(upload_file(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
