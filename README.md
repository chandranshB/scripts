# repo-clone.bat

This batch script automates the process of syncing changes from one Git repository (source) to another (destination).

## What it does:

1. Clones both the source and destination repositories into temporary folders.
2. Copies all files and folders from the source repository to the destination repository's temporary folder, excluding the `.git` directory.
3. Stages and commits all changes in the destination repository's temporary folder with a commit message provided by the user.
4. Pushes the committed changes from the destination repository's temporary folder to its remote.
5. Removes the temporary folders created during the process.

## Usage:

```bash
repo-clone.bat
```

The script will prompt you for the source repository URL, the destination repository URL, and the commit message for the changes.
