# My Scripts 📦

Welcome\! This is a collection of simple, powerful scripts designed to automate common tasks, even if you're not a programmer.

-----

## What You'll Find Here

  * **For Windows Users:**
      * `repo-clone.bat`: Mirrors one Git repository to another.
  * **For Linux Users:**
      * `mega-tor-downloader.sh`: Downloads from MEGA.nz anonymously, bypassing rate limits.
  * **For All Users (Windows, macOS, Linux):**
      * `advaita.py`: Finds and removes duplicate files on your computer.
      * `adwaita-telegram.py`: Finds and removes duplicate files within a Telegram group.
      * `organizer.py`: Organizes files into folders based on their type (Images, Videos, etc.).
      * `Telegram Group Downloader.py`: Downloads all media from a Telegram group or channel.

-----

## The Scripts Explained

Here’s a simple guide for each script.

### ✨ `advaita.py` (Local File Duplicate Finder)

Scans a folder on your computer, finds all duplicate files, and helps you clean them up to free up space.

**How to Use It:**

1.  Open your terminal or command prompt.
2.  Run the script, optionally providing a path to scan. If no path is given, it scans the current folder.
    ```bash
    # Scan the current folder
    python advaita.py

    # Scan a specific folder
    python advaita.py /path/to/your/folder
    ```
3.  After the scan, it will show how much space can be saved and ask if you want to **delete** the duplicates, **move** them to a "duplicates" folder, or **skip**.

### 📲 `adwaita-telegram.py` (Telegram Duplicate Finder)

Scans a Telegram group or topic, finds duplicate file uploads, and lets you delete them to clean up the chat.

**Before You Start:**

  * You'll need an **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org).
  * Install the required library: `pip install telethon tqdm`

**How to Use It:**

1.  Run the script: `python adwaita-telegram.py`
2.  Enter your Telegram API credentials and the group link when prompted.
3.  Choose your action: delete duplicates as they are found, or review them all at the end before deleting.
4.  If the group has topics, you can choose to scan a specific topic or the entire group.

### 📂 `organizer.py` (File Organizer)

Moves files from a source directory to a destination, sorting them into categorized folders (e.g., `Images`, `Videos`, `Documents`).

**How to Use It:**

1.  Run the script: `python organizer.py`
2.  Enter the path to the **source directory** you want to organize.
3.  Enter the path to the **destination directory** where the organized folders will be created.
4.  Choose how to handle the folder structure:
      * **`f` (Flatten):** All files go directly into category folders (e.g., `Images/`).
      * **`r` (Retain):** The original folder structure is kept inside the category folders.
      * **A number (e.g., `1`, `2`):** Retains a specific number of parent folder levels.

### 🕵️ `mega-tor-downloader.sh` (For Linux)

Downloads files from MEGA.nz public folders using the Tor network to protect your privacy and automatically get a new IP address to bypass download limits.

**Before You Start:**

  * Install required tools: `sudo apt update && sudo apt install megatools torsocks tor`

**How to Use It:**

1.  Run the script in your terminal: `bash mega-tor-downloader.sh`
2.  The script will prompt you for the **MEGA folder URL** and the **destination directory**.
3.  Alternatively, use flags: `bash mega-tor-downloader.sh -u <MEGA_URL> -d <DEST_DIR>`
      * The script now features improved logging, error checking, and will intelligently retry only the downloads that failed.

### 📜 `repo-clone.bat` (For Windows)

Mirrors one Git repository to another. A simple "copy-paste" for entire code repositories.

**Before You Start:**

  * Install **Git for Windows** from [git-scm.com](https://git-scm.com/download/win).

**How to Use It:**

1.  Double-click the `repo-clone.bat` file.
2.  Follow the prompts to enter the **source URL**, **destination URL**, and a **commit message**.

### 📥 `Telegram Group Downloader.py` (Media Downloader)

Downloads all media (photos, videos, documents) from a Telegram group or channel.

**Before You Start:**

  * Get your **API ID** and **API Hash** from [my.telegram.org](https://my.telegram.org).
  * Install libraries: `pip install telethon python-dotenv`
  * Create a `.env` file with your `API_ID` and `API_HASH` or enter them when prompted.

**How to Use It:**

1.  Run the script: `python "Telegram Group Downloader.py"`
2.  Enter the Telegram group link and the number of parallel downloads.

-----

## 🔬 How They Work: The Technology Behind the Scripts

### `advaita.py` & `adwaita-telegram.py` (Duplicate Finders)

Both scripts use a highly efficient two-pass hashing algorithm to find duplicates without comparing every file to every other file.

  * **Core Technology:**
      * **Python:** The language they are written in.
      * **Hashing (SHA-256):** A cryptographic function that creates a unique, fixed-size "fingerprint" (a hash) for any given piece of data. If two files have the same hash, they are identical.
      * **Telethon (`adwaita-telegram.py`):** A Python library to interact with the Telegram API.
  * **Algorithm:**
    1.  **Pass 1: Group by Size:** First, it finds all files that have the exact same size. This is a quick way to filter out non-duplicates. For the Telegram script, it indexes all file messages in the chat.
    2.  **Pass 2: Group by Hash:** For each group of files with an identical size, it calculates the SHA-256 hash of the file's content. If two files share the same hash, they are confirmed duplicates.
    3.  **Action:** The oldest file is kept, and any newer duplicates are identified for deletion. The script then asks the user for confirmation before making changes. The Telegram script includes a cache to resume progress if interrupted.

### `organizer.py` (File Organizer)

  * **Core Technology:**
      * **`pathlib`:** A modern Python library for handling filesystem paths in an object-oriented way, making path manipulation cleaner and more reliable across different operating systems.
  * **Algorithm:**
    1.  **Categorization:** It uses a dictionary that maps file extensions (e.g., `.jpg`, `.mp4`) to category names (e.g., "Images", "Videos").
    2.  **Traversal:** It recursively walks through every file in the source directory using `rglob('*')`.
    3.  **Path Calculation:** For each file, it determines the new destination path based on its category and the user's choice for folder structure (flatten, retain, or depth).
    4.  **Move:** It creates the necessary destination folders and uses `shutil.move()` to move the file.

### `mega-tor-downloader.sh` & `repo-clone.bat`

These are shell scripts that automate a sequence of command-line tools.

  * **Core Technologies:**
      * **Bash/Batch:** The scripting languages for Linux and Windows, respectively.
      * **Command-Line Tools:** They orchestrate other programs like `git` (for repo-clone) or `megadl`, `torsocks`, and `systemctl` (for the MEGA downloader).
  * **Algorithm (`mega-tor-downloader.sh`):**
    1.  **Retry Loop:** The script operates in a loop that will try to download the files up to a set number of times.
    2.  **IP Rotation:** At the start of each attempt, it restarts the Tor service (`sudo systemctl restart tor`) to obtain a new IP address, which bypasses MEGA's rate limiting.
    3.  **Intelligent Download:** It keeps track of which destination directories have successfully completed their download and only retries the ones that have failed, making it efficient.
    4.  **Execution:** It uses `torsocks` to force the `megadl` download tool to route its traffic through the Tor network.

### `Telegram Group Downloader.py`

  * **Core Technology:**
      * **Telethon & `asyncio`:** It uses the `asyncio` library to perform asynchronous operations. This allows it to start multiple downloads concurrently without waiting for each one to finish, dramatically speeding up the process.
  * **Algorithm:**
    1.  **Iteration:** It loops through every message in a Telegram chat's history.
    2.  **Categorization:** It inspects the **MIME type** of each media file to determine if it's an image, video, audio file, etc.
    3.  **Parallel Download:** It creates a "task" for each media download and runs them in parallel using `asyncio.gather()`, up to the user-defined limit.