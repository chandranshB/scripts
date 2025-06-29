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

**Usage**

```batch
repo-clone.bat
```

Follow the prompts for:

1. Source repo URL
2. Destination repo URL
3. Commit message

---

### 2. download\_media.py

Downloads **all** media from a Telegram group/channel into dated subfolders.

**Features**

* Async, fast download via Telethon
* Organizes files by `YYYY-MM-DD` folders
* Prints progress per file and final summary
* Safe: skips messages without media

**Setup**

```bash
pip install telethon
export TG_API_ID=123456
export TG_API_HASH="your_api_hash"
export TG_TARGET_ID=-1001234567890
```

**Usage**

```bash
python download_media.py
```

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
├─ download_media.py
├─ README.md
└─ .gitignore
```

**.gitignore** should include:

```
session.session
telegram_group_media/
```

---

## 🚑 Troubleshooting

* **repo-clone.bat**: ensure `git` is in `PATH` and run in a writable directory.
* **download\_media.py**: verify env vars are set and your Telegram account has access to the target.

---
