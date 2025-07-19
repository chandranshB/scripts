# My Scripts 📦

Welcome\! This is a collection of simple scripts designed to help you with common tasks, even if you're not a programmer.

-----

## What You'll Find Here

  * **For Windows Users:**
      * `repo-clone.bat`: A tool to copy everything from one code repository to another.
  * **For Linux Users:**
      * `mega-tor-downloader.sh`: A script to download files from MEGA.nz anonymously without download limits.
  * **For All Users (Windows, macOS, Linux):**
      * `Telegram Group Downloader.py`: A program to download all media from a Telegram group or channel.
      * `advaita.py`: A tool to find and remove duplicate files on your computer.

-----

## Getting Started: What You Need

Before you begin, make sure you have the right tools for the job.

  * **For the Python Scripts (`.py` files):**
      * You'll need **Python** installed. If you don't have it, you can get it from the [official Python website](https://www.python.org/downloads/).
  * **For the Windows Script (`.bat` file):**
      * You'll need **Git for Windows**. You can download it from [git-scm.com](https://git-scm.com/download/win).
  * **For the Linux Script (`.sh` file):**
      * You will need to install a few tools using your system's package manager. The script will guide you through this.

-----

## The Scripts Explained

Here’s a simple guide for each script.

### 📜 `repo-clone.bat` (For Windows)

This script helps you mirror one Git repository to another. Think of it as a "copy-paste" for code repositories.

**How to Use It:**

1.  **Download:** Save the `repo-clone.bat` file to your computer.
2.  **Run It:** Double-click the file to open a command prompt window.
3.  **Follow the Prompts:**
      * It will ask for the **source repository URL** (where you're copying from).
      * Then, it will ask for the **destination repository URL** (where you're pasting to).
      * Finally, type a **commit message** (a short note about what you're copying).

The script will handle all the technical steps for you and will clean up after itself when it's done.

### 📥 `Telegram Group Downloader.py` (For Windows, macOS, and Linux)

This script lets you download all the photos, videos, and other files from a Telegram group or channel.

**Before You Start:**

  * **Get Your Telegram API Credentials:** You'll need an **API ID** and **API Hash** from Telegram. You can get these by following the instructions at [my.telegram.org](https://my.telegram.org).
  * **Install Required Packages:** Open your terminal (Command Prompt on Windows, Terminal on macOS/Linux) and type the following command:
    ```bash
    pip install telethon python-dotenv
    ```
  * **Create a `.env` File:** In the same folder where you saved the script, create a new file named `.env`. Inside this file, add your API credentials like this:
    ```
    API_ID=your_api_id
    API_HASH=your_api_hash
    ```
    Replace `your_api_id` and `your_api_hash` with the credentials you got from Telegram.

**How to Use It:**

1.  **Run the Script:** Open your terminal, navigate to the folder where you saved the files, and run the script with this command:
    ```bash
    python "Telegram Group Downloader.py"
    ```
2.  **Follow the Prompts:**
      * Enter the **link to the Telegram group or channel**.
      * Choose how many **downloads you want to run at the same time** (a number between 1 and 10 is good).

The script will create a new folder and save all the media files there, neatly organized by type (images, videos, etc.).

### 🕵️ `mega-tor-downloader.sh` (For Linux)

This script downloads files from MEGA.nz public folders through the Tor network, which helps protect your privacy and avoid download limits.

**Before You Start:**

  * **Install Required Tools:** Open your terminal and run this command to install the necessary software:
    ```bash
    sudo apt update && sudo apt install megatools torsocks tor
    ```

**How to Use It:**

1.  **Run the Script:** Open your terminal and run the script with this command:
    ```bash
    bash mega-tor-downloader.sh
    ```
2.  **Interactive Mode:** The script will ask you for:
      * The **MEGA folder URL**.
      * The **destination directory** where you want to save the files.

You can also run the script with options like this:

```bash
bash mega-tor-downloader.sh -u <MEGA_URL> -d <DEST_DIR>
```

If a download fails, the script will automatically try again a few times. All download activity is logged for troubleshooting.

### ✨ `advaita.py` (For Windows, macOS, and Linux)

This script scans a folder, finds all the duplicate files, and helps you clean them up to free up space.

**How to Use It:**

1.  **Run the Script:** Open your terminal and run the script. You can either scan the current directory or specify a path:
      * To scan the current folder:
        ```bash
        python advaita.py
        ```
      * To scan a different folder:
        ```bash
        python advaita.py /path/to/your/folder
        ```
2.  **Choose What to Do:** After scanning, the script will show you a summary of the duplicates it found and give you three choices:
      * **Delete** all the duplicate files.
      * **Move** all the duplicates to a new "duplicates" folder.
      * **Skip** and do nothing.

The script will show you how much space you can save and wait for your choice before making any changes.