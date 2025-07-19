import os
import hashlib
import argparse
import shutil
import sys
from collections import defaultdict

# --- Configuration ---
CHUNK_SIZE = 65536
PROGRESS_INDICATOR_COUNT = 1000

# --- ANSI Color Codes for Terminal Output ---
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

def print_logo():
    """Prints the script's logo and initial information."""
    logo = rf"""
{Colors.CYAN}{Colors.BOLD}
    _       _            _ _        
   / \   __| |_   ____ _(_) |_ __ _ 
  / _ \ / _` \ \ / / _` | | __/ _` |
 / ___ \ (_| |\ V / (_| | | || (_| |
/_/   \_\__,_| \_/ \__,_|_|\__\__,_|
{Colors.RESET}
            {Colors.YELLOW}--- Shandran Edition ---{Colors.RESET}
"""
    print(logo)

def get_file_hash(filepath):
    """Calculates the SHA-256 hash of a file's content."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (IOError, PermissionError) as e:
        print(f"\n{Colors.YELLOW}⚠️  Could not read file '{filepath}': {e}{Colors.RESET}")
        return None

def find_and_process_duplicates(scan_directory):
    """Finds all duplicates and then prompts the user for a single action."""
    print(f"{Colors.BOLD}🚀 Starting scan in '{Colors.MAGENTA}{scan_directory}{Colors.RESET}{Colors.BOLD}'...{Colors.RESET}")
    
    # --- Pass 1: Group files by size ---
    files_by_size = defaultdict(list)
    file_count = 0
    duplicates_folder_path = os.path.normpath(os.path.join(scan_directory, 'duplicates'))

    print("Pass 1: Grouping files by size ", end='')
    for dirpath, _, filenames in os.walk(scan_directory):
        if os.path.normpath(dirpath).startswith(duplicates_folder_path):
            continue
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            file_count += 1
            if file_count % PROGRESS_INDICATOR_COUNT == 0:
                print(f"{Colors.CYAN}.{Colors.RESET}", end='', flush=True)
            try:
                if not os.path.islink(filepath):
                    files_by_size[size].append(filepath) if (size := os.path.getsize(filepath)) else None
            except OSError:
                continue
    print(f"\n{Colors.GREEN}✔ Scanned {file_count} files.{Colors.RESET}")

    # --- Pass 2: Hash files for groups with potential duplicates ---
    files_by_hash = defaultdict(list)
    potential_duplicates = {size: paths for size, paths in files_by_size.items() if len(paths) > 1}
    
    if not potential_duplicates:
        print(f"\n{Colors.GREEN}✅ No files with identical sizes found. The directory is clean!{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Pass 2: Found {Colors.YELLOW}{len(potential_duplicates)}{Colors.RESET}{Colors.BOLD} groups of files with identical sizes. Now checking content...{Colors.RESET}")
    
    for paths in potential_duplicates.values():
        for filepath in paths:
            if file_hash := get_file_hash(filepath):
                files_by_hash[file_hash].append(filepath)

    # --- Filter for actual duplicates ---
    actual_duplicates = [paths for paths in files_by_hash.values() if len(paths) > 1]
    
    if not actual_duplicates:
        print(f"\n{Colors.GREEN}✅ All files with the same size have unique content. No duplicates found!{Colors.RESET}")
        return
        
    # --- Present summary and ask for action ---
    process_duplicates_menu(actual_duplicates, scan_directory)

def process_duplicates_menu(dup_sets, base_dir):
    """Calculates stats, shows a menu, and processes all duplicates at once."""
    total_dupes_to_process = 0
    total_space_to_free = 0
    all_dupe_files = []

    for dup_set in dup_sets:
        # Keep the first file as original, rest are duplicates
        dupes_in_set = sorted(dup_set)[1:]
        total_dupes_to_process += len(dupes_in_set)
        all_dupe_files.extend(dupes_in_set)
        for f in dupes_in_set:
            total_space_to_free += os.path.getsize(f)
            
    space_mb = total_space_to_free / (1024 * 1024)

    # --- Display Summary & Menu ---
    print("\n" + f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}📊 Scan Complete! Duplicate Summary:{Colors.RESET}")
    print(f"   - Found {Colors.BOLD}{total_dupes_to_process}{Colors.RESET} duplicate files across {Colors.BOLD}{len(dup_sets)}{Colors.RESET} sets.")
    print(f"   - Total space occupied by duplicates: {Colors.BOLD}{space_mb:.2f} MB{Colors.RESET}")
    print(f"{Colors.YELLOW}{'-'*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}What would you like to do?{Colors.RESET}")
    print("  [1] Delete all duplicate files")
    print("  [2] Move all duplicates to a 'duplicates' folder")
    print("  [3] Skip and exit")
    
    while True:
        choice = input(f"\nEnter your choice (1-3): {Colors.RESET}").strip()
        if choice in ['1', '2', '3']:
            break
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.RESET}")

    # --- Perform Action ---
    if choice == '1':
        print(f"\n{Colors.RED}{Colors.BOLD}🗑️ Deleting {total_dupes_to_process} duplicate files...{Colors.RESET}")
        for filepath in all_dupe_files:
            try:
                os.remove(filepath)
                print(f"  Deleted: {filepath}")
            except OSError as e:
                print(f"  {Colors.RED}❌ Error deleting {filepath}: {e}{Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ Deletion complete.{Colors.RESET}")

    elif choice == '2':
        duplicates_folder = os.path.join(base_dir, 'duplicates')
        print(f"\n{Colors.BLUE}{Colors.BOLD}➡️ Moving {total_dupes_to_process} duplicate files to '{duplicates_folder}'...{Colors.RESET}")
        os.makedirs(duplicates_folder, exist_ok=True)
        for filepath in all_dupe_files:
            try:
                shutil.move(filepath, os.path.join(duplicates_folder, os.path.basename(filepath)))
                print(f"  Moved: {filepath}")
            except (OSError, shutil.Error) as e:
                print(f"  {Colors.RED}❌ Error moving {filepath}: {e}{Colors.RESET}")
        print(f"\n{Colors.GREEN}✅ Move operation complete.{Colors.RESET}")

    elif choice == '3':
        print(f"\n{Colors.YELLOW}⏩ Skipping. No files were changed.{Colors.RESET}")

if __name__ == "__main__":
    if sys.platform == "win32":
        os.system("")

    print_logo()

    parser = argparse.ArgumentParser(
        description="Advaita: Finds and handles duplicate files based on content.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("directory", nargs='?', default=os.getcwd(), 
                        help="The directory to scan for duplicates.\nDefaults to the current directory if not provided.")
    
    args = parser.parse_args()
    scan_dir = args.directory

    if not os.path.isdir(scan_dir):
        print(f"{Colors.RED}Error: Directory '{scan_dir}' not found.{Colors.RESET}")
        sys.exit(1)

    find_and_process_duplicates(scan_dir)
    
    print("\n" + f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🎉 Operation Finished!{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")