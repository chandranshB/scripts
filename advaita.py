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
        {Colors.YELLOW}--- by chandransh ---{Colors.RESET}
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

def find_duplicates(scan_directory):
    """
    Finds and processes duplicate files in the given directory.
    
    Returns a tuple: (number of duplicates found, total space freed/moved).
    """
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
                    size = os.path.getsize(filepath)
                    files_by_size[size].append(filepath)
            except OSError:
                continue

    print(f"\n{Colors.GREEN}✔  Scanned {file_count} files.{Colors.RESET}")

    # --- Pass 2: Hash files for groups with potential duplicates ---
    files_by_hash = defaultdict(list)
    potential_duplicates = {size: paths for size, paths in files_by_size.items() if len(paths) > 1}
    
    if not potential_duplicates:
        print(f"\n{Colors.GREEN}✅ No files with identical sizes found. The directory is clean!{Colors.RESET}")
        return 0, 0

    print(f"{Colors.BOLD}Pass 2: Found {Colors.YELLOW}{len(potential_duplicates)}{Colors.RESET}{Colors.BOLD} groups of files with identical sizes. Now checking content...{Colors.RESET}")
    
    for size, paths in potential_duplicates.items():
        for filepath in paths:
            file_hash = get_file_hash(filepath)
            if file_hash:
                files_by_hash[file_hash].append(filepath)

    # --- Filter for actual duplicates (more than one file per hash) ---
    actual_duplicates = [paths for paths in files_by_hash.values() if len(paths) > 1]
    
    if not actual_duplicates:
        print(f"\n{Colors.GREEN}✅ All files with same size have unique content. No duplicates found!{Colors.RESET}")
        return 0, 0

    # --- Process duplicates ---
    total_dupes_found = sum(len(paths) - 1 for paths in actual_duplicates)
    total_space_processed = 0
    
    print(f"\n{Colors.RED}{Colors.BOLD}💥 Found {total_dupes_found} duplicate file(s) in {len(actual_duplicates)} set(s).{Colors.RESET}")
    
    duplicates_folder = os.path.join(scan_directory, 'duplicates')

    for i, dup_set in enumerate(actual_duplicates):
        dup_set.sort()
        original = dup_set[0]
        dupes_to_process = dup_set[1:]
        
        print("\n" + f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Duplicate Set {i+1}/{len(actual_duplicates)}{Colors.RESET}")
        print(f"  {Colors.GREEN}[Original] {original}{Colors.RESET}")
        for dup in dupes_to_process:
            print(f"  {Colors.RED}[Duplicate] {dup}{Colors.RESET}")
        
        while True:
            prompt = (f"\n{Colors.CYAN}Choose an action: (D)elete duplicates, "
                      f"(M)ove to 'duplicates' folder, (S)kip? {Colors.RESET}").strip()
            action = input(prompt).lower().strip()
            
            if action in ['d', 'delete']:
                for filepath in dupes_to_process:
                    try:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        total_space_processed += file_size
                        print(f"  {Colors.RED}🗑️  Deleted: {filepath}{Colors.RESET}")
                    except OSError as e:
                        print(f"  {Colors.RED}❌ Error deleting {filepath}: {e}{Colors.RESET}")
                break
                
            elif action in ['m', 'move']:
                try:
                    os.makedirs(duplicates_folder, exist_ok=True)
                    for filepath in dupes_to_process:
                        file_size = os.path.getsize(filepath)
                        shutil.move(filepath, os.path.join(duplicates_folder, os.path.basename(filepath)))
                        total_space_processed += file_size
                        print(f"  {Colors.BLUE}➡️  Moved: {filepath}{Colors.RESET}")
                except (OSError, shutil.Error) as e:
                    print(f"  {Colors.RED}❌ Error moving files: {e}{Colors.RESET}")
                break
                
            elif action in ['s', 'skip']:
                print(f"  {Colors.YELLOW}⏩ Skipping this set...{Colors.RESET}")
                break
            else:
                print(f"  {Colors.RED}Invalid choice. Please enter D, M, or S.{Colors.RESET}")
    
    return total_dupes_found, total_space_processed


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

    dupes, space = find_duplicates(scan_dir)
    
    print("\n" + f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}🎉 Scan Complete!{Colors.RESET}")
    print(f"Total duplicates processed: {Colors.BOLD}{dupes}{Colors.RESET}")
    if space > 0:
        space_mb = space / (1024 * 1024)
        print(f"Total space recovered/moved: {Colors.BOLD}{space_mb:.2f} MB{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
