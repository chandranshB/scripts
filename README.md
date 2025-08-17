# My Scripts 📦

Welcome\! This is a friendly collection of powerful, easy-to-use scripts designed to automate everyday tasks. Whether you're a developer or just someone who wants to get things done faster, you'll find something useful here.

Think of these as digital tools that can organize your files, clean up duplicates, download media, and more, all with a few simple commands.

## ⭐ Why Trust These Scripts?

It's smart to be careful about running scripts from the internet. Here’s why you can trust the ones in this collection:

  * **Transparent and Open Source:** The code is not hidden. You can open any script file in a simple text editor to see exactly what it does. There are no secrets.
  * **No Data Collection:** These scripts run on your computer and your computer alone. They do not collect or send any of your personal information anywhere.
  * **Focused on the Task:** Each script is designed to do one job and do it well. They don't include extra, unnecessary features that could compromise your security.

## 🚀 Getting Started: The Basics

Most of these scripts use **Python**, a popular and safe programming language. A couple are for specific operating systems. Here’s what you might need before you start.

1.  **Install Python (For `.py` scripts):** If you don't have it, download Python from the official website [python.org](https://www.python.org/). During installation, **make sure to check the box that says "Add Python to PATH"**.
2.  **Install Git (For `repo-clone.bat`):** If you're a Windows user and want to use the repository cloner, install Git for Windows from [git-scm.com](https://git-scm.com/download/win).
3.  **Open a Terminal (or Command Prompt):** This is the application you'll use to run the scripts.
      * **Windows:** Press the Windows Key, type `cmd` or `powershell`, and press Enter.
      * **macOS/Linux:** Look for an application called "Terminal".

-----

## 🛠️ The Scripts Explained

Here’s a simple guide for each script, what it does, and how to use it.

### ✨ `advaita.py` (Finds Duplicate Files on Your PC)

Frees up disk space by finding and helping you remove duplicate files in any folder.

  * **Who it's for:** All users (Windows, macOS, Linux).
  * **How to Use It:**
    1.  Open your terminal in the same folder as the script.
    2.  Run one of the following commands:
        ```bash
        # Scan the current folder
        python advaita.py

        # Or, scan a specific folder
        python advaita.py "/path/to/your/folder"
        ```
    3.  The script will show you how much space can be saved and ask if you want to **delete** the duplicates, **move** them to a "duplicates" folder, or **skip**.

### 📂 `organizer.py` (Organizes Your Messy Folders)

Automatically sorts files into categorized folders (like `Images`, `Videos`, `Documents`) to clean up clutter.

  * **Who it's for:** All users (Windows, macOS, Linux).
  * **How to Use It:**
    1.  Run the script in your terminal: `python organizer.py`
    2.  Follow the prompts to enter the **folder you want to clean up** and the **folder where you want to save the organized files**.
    3.  Choose how to structure the new folders (e.g., keep the original folder layout or flatten everything).

### 🎬 `YTDownloader.py` (YouTube Video & Audio Downloader)

A powerful tool to download YouTube videos or just the audio from them. It even installs its own dependencies\!

  * **Who it's for:** All users (Windows, macOS, Linux).
  * **How to Use It:**
    1.  Run the script in your terminal: `python YTDownloader.py`
    2.  The first time you run it, it will automatically check for and install anything it needs.
    3.  Follow the on-screen menu to choose whether you want to download a video, audio, or a whole playlist, and select your desired quality.

### 📲 Telegram Scripts

These scripts help you manage and download media from Telegram.

**Before You Start:** You'll need an **API ID** and **API Hash** to use these. You can get them for free from Telegram's official site: [my.telegram.org](https://my.telegram.org).

#### `adwaita-telegram.py` (Finds Duplicate Files in Telegram)

Scans a Telegram group you're an admin in and helps you find and delete duplicate file uploads to clean up the chat.

  * **Required Library:** `pip install telethon tqdm`
  * **How to Use It:**
    1.  Run the script: `python adwaita-telegram.py`
    2.  Enter your API credentials and the group link when prompted.
    3.  Choose whether to delete duplicates as they are found or review them all at the end.

#### `Telegram Group Downloader.py` (Downloads All Media from a Group)

Downloads every photo, video, and document from any Telegram group or channel you have access to.

  * **Required Libraries:** `pip install telethon python-dotenv`
  * **How to Use It:**
    1.  Run the script: `python "Telegram Group Downloader.py"`
    2.  Enter your API credentials (if not saved in a `.env` file), the group link, and how many files you want to download at once.

### 🕵️ `mega-tor-downloader.sh` (Anonymous MEGA Downloader)

Downloads files from MEGA.nz folders anonymously using the Tor network. This helps bypass download limits by automatically getting a new IP address.

  * **Who it's for:** Linux users.
  * **Before You Start:** You need to install some tools first.
    ```bash
    sudo apt update && sudo apt install megatools torsocks tor
    ```
  * **How to Use It:**
    1.  Run the script in your terminal: `bash mega-tor-downloader.sh`
    2.  Follow the prompts to enter the **MEGA folder URL** and where you want to save the files.

### 📜 `repo-clone.bat` (Copies a Git Repository)

A simple tool for developers that mirrors one Git repository to another. It’s like a "copy-paste" for entire code projects.

  * **Who it's for:** Windows users.
  * **How to Use It:**
    1.  Double-click the `repo-clone.bat` file.
    2.  Follow the prompts to enter the **source URL**, **destination URL**, and a short message describing the copy (a "commit message").

-----

## 🔬 How They Work: The Technology Behind the Scripts

Curious about what makes these scripts tick? Here’s a simple breakdown.

  * **`advaita.py` & `adwaita-telegram.py` (The Duplicate Finders):**
    These scripts don't waste time comparing every file. Instead, they use a smart two-step process.

    1.  **Step 1: Check the Size.** First, they group together all files that have the exact same size. This is a super-fast way to know which files *might* be duplicates.
    2.  **Step 2: Create a "Fingerprint".** For files with the same size, the script calculates a unique digital fingerprint (called a "SHA-256 hash"). If the fingerprints match, the files are 100% identical. The oldest file is kept, and the newer ones are marked for deletion.

  * **`organizer.py` (The File Organizer):**
    This script works like a librarian for your files. It reads the extension of each file (e.g., `.jpg`, `.pdf`) and checks it against a list of categories. Based on the category, it creates the right folder and moves the file there.

  * **`mega-tor-downloader.sh` & `repo-clone.bat` (The Automators):**
    These are shell scripts, which are simple lists of commands for your computer to run in order. They automate tools you could run yourself, like `git` or `megadl`, but save you from having to type them out one by one. The MEGA downloader is special because it also restarts the Tor service to give you a new identity and bypass download limits.

  * **`YTDownloader.py` & `Telegram Group Downloader.py` (The Downloaders):**
    These use official or well-regarded libraries (`yt-dlp` and `Telethon`) to communicate with YouTube and Telegram. They use a technique called **asynchronous downloading**, which means they can start downloading multiple files at the same time without waiting for each one to finish. This makes the whole process much, much faster.
