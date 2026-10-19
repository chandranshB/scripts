# scripts

A collection of small command-line scripts for downloading media, cleaning duplicate files, organizing folders, and syncing Git repositories.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Bash-GNU-green?style=flat-square)](https://www.gnu.org/software/bash/)
[![Batch](https://img.shields.io/badge/Batch-Windows-informational?style=flat-square)](https://learn.microsoft.com/)

Tags: `automation` `python` `bash` `batch` `downloader` `deduplication` `organizer` `yt-dlp` `telethon`

---

## Setup

Install Python packages:

```bash
pip install yt-dlp rich telethon python-dotenv tqdm
```

Optional tools:
- Linux: `sudo apt install megatools torsocks tor` (for `mega-tor-downloader.sh`)
- Windows: Git installed and in PATH (for `repo-clone.bat`)

---

## Scripts

### advaita.py
Finds duplicate files in a directory using SHA-256 hashes and lets you delete or move them.
```bash
python advaita.py
# or specify a path:
python advaita.py /path/to/folder
```

### organizer.py
Sorts files from a messy folder into categorized folders (`Images`, `Videos`, `Documents`, etc.).
```bash
python organizer.py
```

### YTDownloader.py
Downloads YouTube videos, audio, or entire playlists with quality selection. Automatically installs missing dependencies and FFmpeg.
```bash
python YTDownloader.py
```

### Telegram Group Downloader.py
Downloads photos, videos, audio, and documents from any Telegram group or channel into organized folders.
```bash
python "Telegram Group Downloader.py"
```
Requires `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) (saved in a `.env` file or entered when prompted).

### adwaita-telegram.py
Scans a Telegram group or forum topic for duplicate file uploads and lets admins delete them to save chat space.
```bash
python adwaita-telegram.py
```

### mega-tor-downloader.sh
Downloads public MEGA folders on Linux and rotates Tor exit IPs when download limits are reached.
```bash
bash mega-tor-downloader.sh -u "MEGA_FOLDER_URL" -d "/path/to/save"
```

### repo-clone.bat
Windows tool to copy files from one Git repository to another, commit them, and push changes to remote.
```cmd
repo-clone.bat
```
