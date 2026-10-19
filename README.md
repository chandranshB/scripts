# scripts

A collection of standalone automation scripts and command-line utilities for local and remote file deduplication, media downloading, filesystem organization, and Git repository mirroring.

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Shell Script](https://img.shields.io/badge/Shell-Bash-4EAA25?style=flat&logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Batch Script](https://img.shields.io/badge/Windows-Batch-0078D6?style=flat&logo=windows&logoColor=white)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=flat)]()

---

## Repository Topics

Suggested GitHub repository tags for discovery:

`automation` `python` `bash` `batch` `cli` `utilities` `deduplication` `file-organizer` `youtube-downloader` `telegram-downloader` `yt-dlp` `telethon` `tor` `megatools` `git-mirror`

---

## Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Utilities](#utilities)
  - [advaita.py](#advaitapy)
  - [organizer.py](#organizerpy)
  - [YTDownloader.py](#ytdownloaderpy)
  - [Telegram Group Downloader.py](#telegram-group-downloaderpy)
  - [adwaita-telegram.py](#adwaita-telegrampy)
  - [mega-tor-downloader.sh](#mega-tor-downloadersh)
  - [repo-clone.bat](#repo-clonebat)
- [Technical Architecture](#technical-architecture)
  - [Two-Pass Deduplication](#two-pass-deduplication)
  - [Bandwidth-Optimized Partial Hashing](#bandwidth-optimized-partial-hashing)
  - [Tor IP Rotation Mechanism](#tor-ip-rotation-mechanism)
- [Environment and Security](#environment-and-security)

---

## Overview

| Script | Language | OS | Dependencies | Primary Function |
|---|---|---|---|---|
| `advaita.py` | Python | Linux, Windows, macOS | Standard Library | Content-based local file deduplication via SHA-256 |
| `organizer.py` | Python | Linux, Windows, macOS | Standard Library | Extension-based file sorting with custom directory depth |
| `YTDownloader.py` | Python | Linux, Windows, macOS | `yt-dlp`, `rich`, `ffmpeg` | YouTube video, audio, and playlist downloader with auto-dependency installer |
| `Telegram Group Downloader.py` | Python | Linux, Windows, macOS | `telethon`, `python-dotenv` | Concurrent media downloader for Telegram groups and channels |
| `adwaita-telegram.py` | Python | Linux, Windows, macOS | `telethon`, `tqdm` | Remote duplicate file scanner and cleaner for Telegram groups |
| `mega-tor-downloader.sh` | Bash | Linux | `megatools`, `torsocks`, `tor` | Unattended MEGA folder downloader with Tor exit-node rotation |
| `repo-clone.bat` | Batch | Windows | `git`, `robocopy` | Git repository synchronization and mirroring utility |

---

## Prerequisites

### Python Environment

The Python scripts require Python 3.8 or higher. Install required external dependencies using pip:

```bash
# Telegram automation tools
pip install telethon python-dotenv tqdm

# YouTube downloader (also handled automatically on first run by YTDownloader.py)
pip install yt-dlp rich
```

### System Tools

- **Git**: Required for `repo-clone.bat` and version control tasks.
- **Tor and Megatools** (Linux only, for `mega-tor-downloader.sh`):
  ```bash
  sudo apt update && sudo apt install megatools torsocks tor
  ```
- **FFmpeg**: Required for media extraction in `YTDownloader.py` (the script includes platform-specific auto-install routines).

---

## Utilities

### advaita.py

A standalone, content-based duplicate file finder. It detects identical files regardless of file names using a two-pass size and SHA-256 content verification pipeline.

#### Usage

```bash
# Scan the current working directory
python advaita.py

# Scan a target directory
python advaita.py /path/to/directory
```

#### Workflow

1. Scans directory trees while excluding symlinks and any existing `./duplicates` subfolder.
2. Groups candidate files by byte size.
3. Computes chunked SHA-256 hashes only across size-matched candidates.
4. Generates a summary of total duplicate count and reclaimable disk space in megabytes.
5. Displays an interactive action menu:
   - `[1]` Delete duplicate files (retains the first alphabetical file path).
   - `[2]` Move duplicate files into a `./duplicates/` folder.
   - `[3]` Skip and exit without modifying the filesystem.

---

### organizer.py

A filesystem cleanup utility that categorizes files by extension and moves them into organized destination folders.

#### File Categories

- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.m4v`, `.3gp`, `.mpg`, `.mpeg`, `.mkv`, `.wmv`, `.flv`, `.webm`
- **Audio**: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`
- **Documents**: `.pdf`, `.docx`, `.doc`, `.pptx`, `.ppt`, `.xlsx`, `.xls`, `.txt`, `.rtf`, `.odt`
- **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`
- **Code**: `.py`, `.js`, `.html`, `.css`, `.java`, `.c`, `.cpp`, `.sh`
- **Executables**: `.exe`, `.msi`, `.dmg`, `.app`
- **Other**: Unmatched file types

#### Usage

```bash
python organizer.py
```

The script interactively prompts for:
1. **Source path**: Root directory containing files to organize.
2. **Scan scope**: Entire directory tree or a specific subdirectory.
3. **Destination path**: Target directory for sorted categories.
4. **Depth handling**:
   - `f` (Flatten): Relocates all files directly into category root folders (`Destination/Images/file.png`).
   - `r` (Retain): Preserves the full relative subfolder hierarchy inside category folders (`Destination/Images/subfolder/file.png`).
   - `<integer>`: Preserves a specified number of parent directory levels.

---

### YTDownloader.py

A full-featured YouTube media downloader supporting single videos, audio extraction, full playlists, and selective video ranges. Includes an automated dependency manager that detects, installs, and configures missing Python modules and FFmpeg binaries across Windows, Linux, and macOS.

#### Features

- Single video and audio-only extraction.
- Playlist parsing with video range selection (e.g., `1-10`, `1,3,5`, or `all`).
- Quality presets: `best`, `1080p`, `720p`, `480p`, `360p`, `lowest`.
- Automated metadata embedding.
- Self-bootstrapping installer for `yt-dlp`, `rich`, and `ffmpeg`.

#### Usage

```bash
python YTDownloader.py
```

#### Interactive Options

```text
1. Video
2. Audio
3. Playlist
4. Playlist Audio
5. Exit
```

Downloaded files are organized into structured directories under the user's Downloads folder:
- `Downloads/YouTube_Downloads/Videos/`
- `Downloads/YouTube_Downloads/Audio/`
- `Downloads/YouTube_Downloads/Playlists/<Playlist_Title>/`

---

### Telegram Group Downloader.py

An asynchronous media scraper that connects to Telegram channels or groups via the MTProto client (Telethon) and downloads historical media into sorted directories.

#### Requirements

Telegram API credentials (`API_ID` and `API_HASH`) obtained from [my.telegram.org](https://my.telegram.org).

Set these credentials in a `.env` file or provide them interactively:

```env
API_ID=12345678
API_HASH=your_api_hash_here
```

#### Usage

```bash
python "Telegram Group Downloader.py"
```

#### Capabilities

- Resolves public channel links (`t.me/channelname`), invite links (`t.me/+hash`), and private channel links (`t.me/c/<id>/<msg>`).
- Configurable worker pool (1 to 10 parallel downloads via asyncio semaphore).
- MIME-type sorting:
  - `images/`
  - `videos/`
  - `audio/`
  - `documents/`
  - `vcards/`
  - `other/`
- Target directory automatically created as `<group_name>_media/`.

---

### adwaita-telegram.py

A duplicate file auditor and cleaner designed for Telegram groups, channels, and forum topics where administrative deletion privileges are available.

#### Requirements

```bash
pip install telethon tqdm
```

#### Usage

```bash
python adwaita-telegram.py
```

#### Key Capabilities

- **Topic Selection**: Detects forum-enabled supergroups and allows scanning individual topics or the entire chat.
- **Resumable State**: Saves progress to `progress_cache.json`. If a scan is halted or disconnected, rerun the script to resume from the last indexed position.
- **Bandwidth Conservation**: Employs partial content hashing for files larger than 10 MB, avoiding unnecessary bandwidth usage.
- **Cleanup Routine**: Automatically clears cached sessions, temporary hash files, and progress markers when finished.

---

### mega-tor-downloader.sh

A resilient Bash script for downloading public MEGA.nz folders via the Tor network. It prevents transfer interruptions caused by MEGA bandwidth quotas by monitoring transfer status and restarting the Tor daemon to rotate exit IPs upon quota limits.

#### Requirements

```bash
sudo apt update && sudo apt install megatools torsocks tor
```

Ensure the current user has `sudo` privileges to restart the Tor service (`systemctl restart tor`).

#### Syntax

```bash
bash mega-tor-downloader.sh [-u <MEGA_URL>] [-d <DEST_DIR>]... [-r <MAX_RETRIES>] [-w <RETRY_DELAY>] [-h]
```

#### Options

| Flag | Parameter | Description | Default |
|---|---|---|---|
| `-u` | `URL` | Public MEGA folder URL | Prompted if omitted |
| `-d` | `DIR` | Destination directory (can be repeated for multiple targets) | Prompted if omitted |
| `-r` | `N` | Maximum retry attempts per directory | `10` |
| `-w` | `SEC` | Wait interval between retries in seconds | `10` |
| `-h` | None | Display usage information | None |

#### Example

```bash
bash mega-tor-downloader.sh \
  -u "https://mega.nz/folder/example#key" \
  -d "/mnt/storage/downloads" \
  -r 15 \
  -w 20
```

---

### repo-clone.bat

A Windows command script designed to mirror the file tree of a source Git repository to a target Git repository while preserving the target repository's Git history.

#### Workflow

1. Clones the source repository into a temporary workspace (`src_temp`).
2. Clones the destination repository into a separate temporary workspace (`dest_temp`).
3. Executes `robocopy src_temp dest_temp /MIR /XD .git` to mirror all source files into the destination while leaving destination Git configuration untouched.
4. Stages updated files (`git add .`), creates a commit with a user-supplied message, and pushes to remote `HEAD`.
5. Cleans up temporary staging directories upon exit.

#### Usage

Double-click `repo-clone.bat` or run from Command Prompt:

```cmd
repo-clone.bat
```

Prompts for:
1. Source repository URL (accepts formats with or without `https://`).
2. Destination repository URL.
3. Commit message for the synchronized state.

---

## Technical Architecture

### Two-Pass Deduplication

Both `advaita.py` and `adwaita-telegram.py` avoid `O(n^2)` pairwise comparisons by using a two-pass indexing approach:

1. **Pass 1 (Filesystem Metadata Filter)**: Gathers file size metadata across all indexed paths in `O(n)` time. Files with unique sizes are filtered out immediately.
2. **Pass 2 (Cryptographic Hash Verification)**: Computes SHA-256 hashes in 64 KB streaming chunks only for files with identical byte sizes, eliminating false positives from collisions or identical sizes.

```text
Filesystem Scan
      │
      ▼
Group by Size (O(n))
      │
      ├─ Single File Size ────► Unique (Skipped)
      │
      └─ Multiple File Size Match (Candidates)
            │
            ▼
      Compute SHA-256
            │
            ├─ Distinct Hashes ──► Different Content
            │
            └─ Matching Hashes ──► Duplicate Confirmed
```

### Bandwidth-Optimized Partial Hashing

In `adwaita-telegram.py`, downloading multi-gigabyte files across the Telegram MTProto API solely to compare checksums is inefficient. The script implements an adaptive strategy:

- **Files <= 10 MB**: Downloaded locally and hashed with standard SHA-256.
- **Files > 10 MB**: Fetches only the initial 1 MB data chunk via `client.iter_download(media, request_size=1048576)`. The partial SHA-256 checksum combined with the exact byte size provides duplicate detection while consuming less than 1% of the bandwidth required for full downloads.

### Tor IP Rotation Mechanism

`mega-tor-downloader.sh` handles cloud storage rate-limiting:

1. Initiates transfer using `torsocks megadl`.
2. Inspects process exit codes:
   - `0`: Successful transfer.
   - Non-zero: Quota limit or connection error.
3. If an error is detected, the script logs the failure, restarts the Tor system service (`sudo systemctl restart tor`), pauses for `RETRY_DELAY` seconds to establish a new circuit and exit IP, and resumes the transfer.
4. Completed target directories are tracked in memory, ensuring successful downloads are never re-downloaded during retries.

---

## Environment and Security

- **Credential Isolation**: Telegram API credentials (`API_ID`, `API_HASH`) and session tokens (`*.session`) must remain private. Ensure they are stored exclusively in `.env` files.
- **Git Hygiene**: The repository includes a `.gitignore` configured to prevent committing generated files, including:
  - Python bytecode (`__pycache__/`, `*.pyc`)
  - Telegram session state (`*.session`, `progress_cache.json`)
  - Download artifacts (`*_media/`, `duplicates/`)
  - Operating system metadata (`.DS_Store`, `Thumbs.db`)
