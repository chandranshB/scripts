# 📦 My Scripts

A collection of simple, self-contained scripts to streamline common tasks.

---

## 🛠️ Scripts Included

### 1. repo‑clone.bat

Mirrors changes from one Git repo (source) to another (destination).

**Features**

* Clones source & dest into temp folders
* Copies all files (ignoring `.git`)
* Stages, commits, and pushes diffs
* Cleans up temp directories

**Supported OS:** Windows (Tested on Windows 10/11)

**Prerequisites:**
* [Git for Windows](https://git-scm.com/download/win) (must be in your PATH)
* Command Prompt or compatible terminal

**Setup:**
No special setup required. Ensure you have write permissions in the working directory.

**Usage:**
1. Double-click `repo-clone.bat` or run it in Command Prompt:
   ```batch
   repo-clone.bat
   ```
2. Follow the prompts for:
   - Source repository URL
   - Destination repository URL
   - Commit message

---

### 2. download\_media.py

Downloads **all** media from a Telegram group/channel, organizing by type (images, videos, audio, documents, etc.).

**Supported OS:** Windows, Linux, macOS (Tested on Python 3.8+)

**Prerequisites:**
* Python 3.8 or newer
* [Telethon](https://github.com/LonamiWebs/Telethon) and [python-dotenv](https://pypi.org/project/python-dotenv/)
* Telegram API credentials ([get them here](https://my.telegram.org))

**Setup:**
1. Install dependencies:
   ```bash
   pip install telethon python-dotenv
   ```
2. Create a `.env` file in the same directory with:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
   Or export these as environment variables.

**Usage:**
```bash
python3 "Telegram Group Downloader.py"
```
Follow the prompts to enter your group/channel link and set parallel download count.
### 3. mega-tor-downloader.sh

Download files from MEGA public folders using Tor for privacy and to bypass rate limits.

**Supported OS:** Linux (Tested on Ubuntu/Debian)

**Prerequisites:**
* `megadl` (from [megatools](https://megatools.megous.com/))
* `torsocks` and `tor` (install via your package manager)
* `sudo` privileges to manage Tor service

**Setup:**
1. Install required tools:
   ```bash
   sudo apt update
   sudo apt install megatools torsocks tor
   ```
2. Ensure your user can run `sudo systemctl start tor` without password (optional, for smoother automation)

**Usage:**
```bash
bash mega-tor-downloader.sh
```
You can provide options via flags or interactively:
* `-u` MEGA folder URL
* `-d` Destination directory (can be used multiple times)
* `-r` Max retries (default: 10)
* `-w` Wait time between retries (default: 10s)

---

## ⚙️ Prerequisites

* **Windows/macOS/Linux** with Git & Python installed
* **Telethon** for the Python script
* Valid **Telegram API** credentials (`API_ID`, `API_HASH`)

---

## 📂 Repository Layout

```
/ (root)
├─ repo-clone.bat
├─ Telegram Group Downloader.py
├─ mega-tor-downloader.sh
├─ README.md
└─ .gitignore
```

**.gitignore** should include:
```
session.session
telegram_group_media/
mega-tor-logs/
*.log
```

---

## 🚑 Troubleshooting

* **repo-clone.bat**: Ensure `git` is in your PATH and run in a writable directory.
* **Telegram Group Downloader.py**: Verify your `.env` or environment variables are set and your Telegram account has access to the group/channel.
* **mega-tor-downloader.sh**: Make sure all dependencies are installed and you have sudo privileges. Check logs in `~/Downloads/mega-tor-logs/` if downloads fail.

---
# 📦 My Scripts

A collection of simple, self-contained scripts to streamline common tasks.

---

## 🛠️ Scripts Included

### 1. repo‑clone.bat

Mirrors changes from one Git repo (source) to another (destination).

**Features**

* Clones source & dest into temp folders
* Copies all files (ignoring `.git`)
* Stages, commits, and pushes diffs
* Cleans up temp directories

**Supported OS:** Windows (Tested on Windows 10/11)

**Prerequisites:**
* [Git for Windows](https://git-scm.com/download/win) (must be in your PATH)
* Command Prompt or compatible terminal

**Setup:**
No special setup required. Ensure you have write permissions in the working directory.

**Usage:**
1. Double-click `repo-clone.bat` or run it in Command Prompt:
   ```batch
   repo-clone.bat
   ```
2. Follow the prompts for:
   - Source repository URL
   - Destination repository URL
   - Commit message

---

### 2. download\_media.py

Downloads **all** media from a Telegram group/channel, organizing by type (images, videos, audio, documents, etc.).

**Supported OS:** Windows, Linux, macOS (Tested on Python 3.8+)

**Prerequisites:**
* Python 3.8 or newer
* [Telethon](https://github.com/LonamiWebs/Telethon) and [python-dotenv](https://pypi.org/project/python-dotenv/)
* Telegram API credentials ([get them here](https://my.telegram.org))

**Setup:**
1. Install dependencies:
   ```bash
   pip install telethon python-dotenv
   ```
2. Create a `.env` file in the same directory with:
   ```env
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
   Or export these as environment variables.

**Usage:**
```bash
python3 "Telegram Group Downloader.py"
```
Follow the prompts to enter your group/channel link and set parallel download count.
### 3. mega-tor-downloader.sh

Download files from MEGA public folders using Tor for privacy and to bypass rate limits.

**Supported OS:** Linux (Tested on Ubuntu/Debian)

**Prerequisites:**
* `megadl` (from [megatools](https://megatools.megous.com/))
* `torsocks` and `tor` (install via your package manager)
* `sudo` privileges to manage Tor service

**Setup:**
1. Install required tools:
   ```bash
   sudo apt update
   sudo apt install megatools torsocks tor
   ```
2. Ensure your user can run `sudo systemctl start tor` without password (optional, for smoother automation)

**Usage:**
```bash
bash mega-tor-downloader.sh
```
You can provide options via flags or interactively:
* `-u` MEGA folder URL
* `-d` Destination directory (can be used multiple times)
* `-r` Max retries (default: 10)
* `-w` Wait time between retries (default: 10s)

---

## ⚙️ Prerequisites

* **Windows/macOS/Linux** with Git & Python installed
* **Telethon** for the Python script
* Valid **Telegram API** credentials (`API_ID`, `API_HASH`)

---

## 📂 Repository Layout

```
/ (root)
├─ repo-clone.bat
├─ Telegram Group Downloader.py
├─ mega-tor-downloader.sh
├─ README.md
└─ .gitignore
```

**.gitignore** should include:
```
session.session
telegram_group_media/
mega-tor-logs/
*.log
```

---

## 🚑 Troubleshooting

* **repo-clone.bat**: Ensure `git` is in your PATH and run in a writable directory.
* **Telegram Group Downloader.py**: Verify your `.env` or environment variables are set and your Telegram account has access to the group/channel.
* **mega-tor-downloader.sh**: Make sure all dependencies are installed and you have sudo privileges. Check logs in `~/Downloads/mega-tor-logs/` if downloads fail.

---
