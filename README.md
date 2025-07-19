# My Scripts 📦

Welcome\! This is a collection of simple scripts designed to help you with common tasks, even if you're not a programmer.

-----

## What You'll Find Here

  * **For Windows Users:**
      * `repo-clone.bat`: A tool to copy everything from one code repository to another.
  * **For Linux Users:**
      * `mega-tor-downloader.sh`: A script to download files from MEGA.nz anonymously.
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

-----

## 🔬 How They Work: The Technology Behind the Scripts

Curious about what makes these scripts tick? Here’s a breakdown of the technologies and algorithms they use.

### `repo-clone.bat`

This script is a **Windows Batch Script**, which is a simple yet powerful way to automate tasks on Windows.

  * **Core Technology:** It uses the command-line version of **Git** (`git.exe`) to perform all the repository operations.
  * **Algorithm:**
    1.  **User Input:** It prompts the user for the source and destination repository URLs and a commit message, storing them in variables.
    2.  **Clone Repos:** It uses `git clone` to download both the source and destination repositories into temporary folders (`src_temp`, `dest_temp`).
    3.  **File Mirroring:** The `robocopy` command is used to mirror the files from the source temporary folder to the destination temporary folder. The `/MIR` option ensures that the destination is an exact copy, and `/XD .git` excludes the Git history from the copy.
    4.  **Commit and Push:** It navigates into the destination's temporary folder and uses standard Git commands (`git add .`, `git commit -m`, and `git push`) to save the changes and upload them to the remote repository.
    5.  **Cleanup:** Finally, it removes the temporary folders to clean up the workspace.

### `Telegram Group Downloader.py`

This script uses the **Python** programming language and a powerful library for interacting with Telegram.

  * **Core Technology:**
      * **Telethon:** This is a Python library that allows you to programmatically access Telegram's API, just like a real user.
      * **Asyncio:** This is a Python framework for writing **asynchronous code**. It allows the script to start multiple downloads at the same time without waiting for each one to finish, which dramatically speeds up the process.
  * **Algorithm:**
    1.  **Initialization:** The script loads your API credentials and establishes a connection to Telegram using the `TelegramClient`.
    2.  **Get Entity:** It takes the group/channel link you provide and uses `client.get_entity()` to find the correct chat.
    3.  **Iterate Messages:** It uses `client.iter_messages()` to loop through every message in the chat's history.
    4.  **Categorize and Download:** For each message that contains media, it determines the type of media (image, video, audio, etc.) by checking its **MIME type**. It then creates a corresponding folder (e.g., `images`, `videos`) and downloads the file into it.
    5.  **Parallel Downloads:** Instead of downloading one by one, it creates a "task" for each download and runs them in parallel using `asyncio.gather()`, up to the limit you set. This makes the process much faster.

### `mega-tor-downloader.sh`

This is a **Bash script**, which is a command language for the Linux operating system. It combines several command-line tools to achieve its goal.

  * **Core Technology:**
      * **`megatools`:** A set of command-line tools for interacting with MEGA.nz. This script specifically uses `megadl` to handle the downloads.
      * **Tor:** A service that routes your internet traffic through a network of relays to anonymize your connection. This helps bypass MEGA's download quotas, which are based on your IP address.
      * **`torsocks`:** A tool that forces any application (in this case, `megadl`) to use the Tor network for its internet connection.
      * **`systemctl`:** The standard Linux command for controlling services, used here to start and restart the Tor service to get a new IP address.
  * **Algorithm:**
    1.  **Initialization:** The script starts the Tor service using `sudo systemctl start tor`.
    2.  **Retry Loop:** It enters a loop that will run up to a maximum number of retries (default is 10).
    3.  **Get New IP:** At the start of each attempt, it restarts the Tor service (`sudo systemctl restart tor`) to get a new IP address from the Tor network.
    4.  **Download Attempt:** It then runs the `megadl` command wrapped in `torsocks` to download the files from the provided MEGA URL to the specified destination.
    5.  **Check for Success:** After each attempt, it checks the exit code of the download command. If the code is `0` (success), it celebrates and exits. If it fails, it waits for a few seconds before starting the next attempt in the loop.
    6.  **Logging:** All output from the download process is saved to a log file for later inspection if something goes wrong.

### `advaita.py`

This script uses an efficient, two-pass approach to find duplicate files without having to compare every file against every other file.

  * **Core Technology:**
      * **`os.walk`:** A Python function that "walks" through a directory tree, making it easy to visit every file in a folder and its subfolders.
      * **`hashlib`:** A Python library that implements various secure hash algorithms. This script uses **SHA-256**, a cryptographic hash function that produces a unique "fingerprint" for any given piece of data. If two files have the same SHA-256 hash, they are virtually certain to be identical.
  * **Algorithm:**
    1.  **Pass 1: Group by Size:** The script first walks through the entire directory and groups all files by their **size**. This is very fast and acts as a first filter, since files with different sizes cannot be duplicates.
    2.  **Pass 2: Group by Hash:** For any group of files that have the same size, the script then calculates the **SHA-256 hash** of each file's content. It then groups the files by their hash.
    3.  **Identify Duplicates:** Any group of files that have the same hash are confirmed to be duplicates of each other.
    4.  **User Action:** The script summarizes how many duplicates were found and how much space they occupy. It then presents a menu asking the user whether to delete the duplicates, move them to a separate folder, or do nothing.
    5.  **Execution:** Based on the user's choice, it performs the selected file operations (delete or move) on all the identified duplicate files, keeping one original copy of each file untouched.
