import os
import shutil
from pathlib import Path

# DEFINE FILE CATEGORIES
# You can easily add or change extensions here for your needs yk...
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
    "Videos": [".mp4", ".mov", ".avi",".m4v",".3gp",".mpg",".mpeg", ".mkv", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
    "Documents": [".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".txt", ".rtf", ".odt"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".sh"],
    "Executables": [".exe", ".msi", ".dmg", ".app"],
}

def get_category(file_path):
    """Returns the category name for a given file extension."""
    extension = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"

def organize_files(source_dir, dest_dir, depth_choice):
    """
    Organizes files from source to destination based on type and folder depth preference.
    """
    source_path = Path(source_dir).resolve()
    dest_path = Path(dest_dir).resolve()

    if not source_path.is_dir():
        print(f"❌ Error: Source directory '{source_path}' not found.")
        return

    # Prevent organizing a directory into itself
    if source_path == dest_path:
        print("❌ Error: Source and destination directories cannot be the same.")
        return
    
    print(f"\nScanning '{source_path}'...")
    print("--------------------------------------------------")

    # Use rglob to recursively find all files
    for file in source_path.rglob('*'):
        if file.is_file():
            category = get_category(file)
            
            # This is the path of the file relative to the source directory
            relative_path = file.relative_to(source_path)

            if depth_choice == 'f': # Flatten
                new_parent_dir = dest_path / category
                new_file_path = new_parent_dir / file.name
            
            elif depth_choice == 'r': # Retain full structure
                new_parent_dir = dest_path / category / relative_path.parent
                new_file_path = new_parent_dir / file.name

            else: # Retain specific depth
                try:
                    depth = int(depth_choice)
                    retained_parts = relative_path.parts[:depth]
                    new_parent_dir = dest_path / category / Path(*retained_parts)
                    new_file_path = new_parent_dir / file.name
                except (ValueError, IndexError):
                    new_parent_dir = dest_path / category
                    new_file_path = new_parent_dir / file.name
            
            new_parent_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(new_file_path))
            print(f"📂 Moved '{relative_path}' to '{new_file_path.relative_to(dest_path)}'")
            
    print("\n--------------------------------------------------")
    print("✅ Organization complete!")


if __name__ == "__main__":
    print("📁 Welcome to the File Organizer Script! 📁")

    # Get User Input
    source_directory = input("Enter the path to the main source directory: ")
    
    # Ask to scan all or a specific subdirectory
    scan_path = Path(source_directory) # Default to the main source
    
    scan_choice = input("Scan the 'entire' directory or a 'specific' subdirectory? (entire/specific): ").lower()
    
    if scan_choice == 'specific':
        subdir_name = input(f"Enter the name of the subdirectory inside '{source_directory}': ")
        custom_path = Path(source_directory) / subdir_name
        
        if custom_path.is_dir():
            scan_path = custom_path
            print(f"✅ Scanning custom directory: {scan_path}")
        else:
            print(f"❌ Error: Subdirectory '{custom_path}' not found. Exiting.")
            exit()
    
    destination_directory = input("Enter the path to the destination directory: ")

    print("\nHow should the folder structure be handled?")
    print("  'f' - Flatten all files into category folders (e.g., all images go into 'Images/').")
    print("  'r' - Retain the full original folder structure inside category folders.")
    print("  Enter a number (e.g., '1') to retain that many levels of the original folder structure.")
    
    structure_choice = input("Enter your choice (f, r, or a number): ").lower()

    # Run the Organizer
    organize_files(str(scan_path), destination_directory, structure_choice)