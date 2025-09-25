Video Manager

Video Manager is a Python GUI application to download YouTube videos and split videos into chapters. It uses PyQt5 for the UI, yt-dlp for downloads, and moviepy/ffmpeg for splitting.

Features

- YouTube downloader: Choose resolution and download with yt-dlp.
- Video splitter: Split by chapter timestamps into separate files.
- Simple PyQt5 interface with progress display.
- YouTube uploader: Upload videos to your channel with title, description, tags, privacy, and category. OAuth flow supported.
  - Optional: choose a thumbnail image (JPG/PNG/GIF) to set after the upload completes.
  - Optional: load uploader fields from a YAML file.

Requirements

- Python 3.10+
- FFmpeg installed and on PATH (required for splitting)

Quick Start

1) Install dependencies

```bash
pip install -r requirements.txt
```

2) Run from source

```bash
python video_manager.py
```

3) Optional: Install as a CLI

```bash
pip install .
video_manager
```

Usage Notes

- YouTube Downloader: Enter URL, pick resolution, select download path, then Download.
- Video Splitter: Select input video, provide a chapters text file, choose output folder, then Split.
- YouTube Uploader: Provide video file, title, description, tags, category, privacy, and a Google `credentials.json` to authorize uploads to your channel.
  - Optionally select a thumbnail image to be set for the uploaded video.
  - Optionally click "Load YAML…" to prefill fields from a YAML config. Supported keys: `video`, `title`, `description`, `tags` (list or comma string), `category` (name or numeric ID), `privacy` (public/unlisted/private), `creds` (or `credentials`), and `thumbnail`.

YAML Example

```yaml
video: /path/to/video.mp4
title: My Video Title
description: |
  Multiline description here.
tags: [python, demo, upload]
category: Science & Technology  # or 28
privacy: unlisted
creds: /path/to/credentials.json
thumbnail: /path/to/thumb.jpg
```

Chapters File Format

```
00:00:00 Chapter 1
00:05:30 Chapter 2
00:10:00 Chapter 3
00:15:30 End
```

Each line is HH:MM:SS followed by a space and the title.

Project Structure

```
.
├── icons/
├── __init__.py
├── __version__.py
├── create_deb_package.sh
├── README.md
├── requirements.txt
├── setup.py
├── video_editor.py
├── video_manager.py
├── video_splitter.py
└── youtube_downloader.py
```

Packaging (.deb)

The script create_deb_package.sh builds a Debian package using PyInstaller. Ensure FFmpeg is available and adjust dependencies/paths as needed.

License

MIT License. See headers in source files.

Contributing

Issues and PRs are welcome.

YouTube API Setup

- Create a Google Cloud project and enable the “YouTube Data API v3”.
- Create OAuth 2.0 Client Credentials (Desktop App) and download `credentials.json`.
- In the app’s Uploader, select your `credentials.json`. On first upload, a browser window opens to authorize. A token is saved under `~/.video_manager/youtube_token.json` for reuse.
- Scope requested: `https://www.googleapis.com/auth/youtube.upload`.
