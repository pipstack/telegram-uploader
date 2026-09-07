# Telegram Uploader

A lightweight Docker-based command-line utility for uploading files to your Telegram Saved Messages using the Telegram user API and Telethon.

No Telegram bot is required.

## Features

- Upload files to Telegram Saved Messages
- Uses the Telegram user API
- No Telegram Bot Token required
- Supports nested directories
- Relative file paths only
- Prevents path traversal outside the upload directory
- Read-only file mount
- Persistent Telegram session
- Upload progress bar
- Runs as a non-root user
- One-shot Docker workflow
- Lightweight Python-based image

## How It Works

```text
Host
 │
 ├── files/
 │    └── your-file
 │
 ▼
Docker container
 │
 ├── /files  (read-only)
 │
 └── /data   (persistent session)
 │
 ▼
Telethon
 │
 ▼
Telegram API
 │
 ▼
Telegram Saved Messages
```

Files are read from the host `files/` directory and uploaded directly to the authenticated Telegram account's Saved Messages.

The Telegram session is stored in `data/` and persists between container runs.

## Requirements

- Docker
- Docker Compose
- A Telegram account
- Telegram API ID
- Telegram API Hash

Create Telegram API credentials from:

https://my.telegram.org/

This project does not require a Telegram Bot Token.

## Installation

Clone the repository:

```bash
git clone https://github.com/duefix/telegram-uploader.git
cd telegram-uploader
```

Create the environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
nano .env
```

Add your Telegram API credentials:

```env
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
```

Keep `.env` private.

## First Run

Create the runtime directories if they do not already exist:

```bash
mkdir -p files data
```

Place a file inside `files/`.

For example:

```text
files/
└── movie.mkv
```

Run:

```bash
docker compose run --rm telegram-uploader movie.mkv
```

On the first run, Telethon will authenticate your Telegram account.

After successful authentication, the session is stored at:

```text
data/telegram.session
```

Future runs reuse this session.

Treat the session file as sensitive data.

## Uploading Files

Upload a file from the root of `files/`:

```bash
docker compose run --rm telegram-uploader movie.mkv
```

Upload a PDF:

```bash
docker compose run --rm telegram-uploader document.pdf
```

Upload a file from a nested directory:

```text
files/
└── videos/
    └── episode.mkv
```

Run:

```bash
docker compose run --rm telegram-uploader videos/episode.mkv
```

The supplied path is always relative to `files/`.

## Upload Progress

The uploader displays a progress bar while sending the file:

```text
📤 Uploading: movie.mkv

[██████████████████████████████] 100.00% | 100.0 / 100.0 MB

✓ Upload complete: movie.mkv
📍 Telegram Saved Messages
```

## Security

### No Telegram Bot Required

This project uses the Telegram user API through Telethon.

It does not require:

- Telegram Bot Token
- Chat ID
- Telegram Bot API

Files are sent to the authenticated user's Saved Messages.

### Relative Paths Only

Absolute paths are rejected.

For example:

```bash
docker compose run --rm telegram-uploader /etc/passwd
```

Results in:

```text
✗ Absolute paths are not allowed. Use a path relative to /files.
```

### Path Traversal Protection

The uploader prevents paths from escaping the `/files` directory.

For example:

```bash
docker compose run --rm telegram-uploader ../etc/passwd
```

Results in:

```text
✗ Path must stay inside /files.
```

### Read-Only File Mount

The host `files/` directory is mounted read-only:

```yaml
volumes:
  - ./files:/files:ro
```

The container can read files for uploading but cannot modify them through the `/files` mount.

### Non-Root Container

The application runs as a dedicated non-root user:

```text
uploader
```

The Docker image does not run the application as root.

### Credentials

Telegram API credentials are provided through environment variables.

They are not stored in the Docker image.

Do not commit `.env` to a public repository.

### Telegram Session

After authentication, Telethon creates:

```text
data/telegram.session
```

This session represents the authenticated Telegram account.

Protect it like a sensitive credential.

Do not publish or share the session file.

## Configuration

The default Compose configuration is:

```yaml
services:
  telegram-uploader:
    image: duefix/telegram-uploader:1.0.0

    stdin_open: true
    tty: true

    env_file:
      - .env

    volumes:
      - ./files:/files:ro
      - ./data:/data
```

The container is designed to run as a short-lived job.

There is no long-running service to keep running.

## Docker Image

The published image is available on Docker Hub:

```text
duefix/telegram-uploader
```

Pull the image manually:

```bash
docker pull duefix/telegram-uploader:1.0.0
```

The recommended way to use the project is through Docker Compose.

## Building Locally

If you want to build the image yourself instead of using the published image:

```bash
docker build -t telegram-uploader:local ./app
```

Then change the image in `compose.yaml`:

```yaml
image: telegram-uploader:local
```

Run:

```bash
docker compose run --rm telegram-uploader movie.mkv
```

## Project Structure

```text
telegram-uploader/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── uploader.py
│   └── .dockerignore
├── data/
│   └── telegram.session
├── files/
│   └── your-files-here
├── .env
├── .env.example
├── .gitignore
├── compose.yaml
└── README.md
```

### `app/`

Contains the application source code and Docker build files.

### `data/`

Stores the persistent Telegram session.

This directory should remain private and is excluded from Git and Docker build context.

### `files/`

Place files to be uploaded here.

The directory is mounted into the container as `/files` in read-only mode.

### `.env`

Contains Telegram API credentials.

This file is intentionally excluded from Git and Docker build context.

### `.env.example`

Template showing the required environment variables without containing real credentials.

## Container Lifecycle

This is a one-shot upload utility.

```text
docker compose run --rm
        │
        ▼
Container starts
        │
        ▼
Application validates the path
        │
        ▼
File is uploaded
        │
        ▼
Upload completes
        │
        ▼
Container exits
```

The `--rm` option removes the temporary container after it exits.

The Telegram session remains available because `data/` is mounted from the host.

## Common Errors

### File Not Found

```text
✗ File not found: movie.mkv
```

Make sure the file exists inside the `files/` directory.

Check:

```bash
ls -lh files/
```

### Absolute Path

```text
✗ Absolute paths are not allowed. Use a path relative to /files.
```

Use a path relative to `files/`.

Correct:

```bash
docker compose run --rm telegram-uploader movie.mkv
```

Incorrect:

```bash
docker compose run --rm telegram-uploader /home/user/movie.mkv
```

### Path Traversal

```text
✗ Path must stay inside /files.
```

The supplied path attempted to leave the `files/` directory.

### Authentication Problems

Make sure the Telegram API credentials in `.env` are correct:

```env
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
```

If the session becomes invalid, remove the local session file and authenticate again:

```bash
rm -f data/telegram.session
```

Then run the uploader again.

Only remove the session file if you intentionally want to authenticate again.

## Important Notes

- Files must be placed inside `files/`.
- File paths must be relative to `files/`.
- Telegram API credentials are required.
- A Telegram Bot Token is not required.
- Files are uploaded to Telegram Saved Messages.
- The Telegram session is stored locally in `data/`.
- Keep `.env` private.
- Keep `data/telegram.session` private.
- The `files/` mount is read-only.
- The container runs as a non-root user.
- The container is intended to be used as a short-lived upload job.

## License

MIT License
