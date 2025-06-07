import subprocess
import os
from datetime import datetime

def get_commit_time(file_path):
    """Get the latest commit time of a file."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ci', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def sync_files(source_file, target_file, exclude_lines):
    """Sync source file to target file, excluding specified lines."""
    source_lines = []
    target_lines = []
    
    # Read source and target files
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
        with open(target_file, 'r', encoding='utf-8') as f:
            target_lines = f.readlines()
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    # Initialize output with source lines
    source_output = source_lines.copy()  # Ensure enough space for all source lines
    
    # Preserve excluded lines from target (if they exist)
    for i in range(len(source_lines)):
        if i + 1 in exclude_lines:  # Line numbers start from 1
            if i < len(target_lines):
                source_output[i] = target_lines[i]  # Use target line
            else:
                source_output[i] = "\n"  # Fallback to empty line if target is shorter
    
    # Write to target file
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(source_output)
        print(f"Successfully synced {source_file} to {target_file}, preserving lines {exclude_lines}")
    except Exception as e:
        print(f"Error writing to {target_file}: {e}")

def main():
    file1 = "2024.json"
    file2 = "2024Pro.json"
    
    # Get commit times
    time1 = get_commit_time(file1)
    time2 = get_commit_time(file2)
    
    print(f"Commit time for {file1}: {time1}")
    print(f"Commit time for {file2}: {time2}")
    
    # Determine source and target based on commit time
    if time1 and time2:
        if time1 > time2:
            print(f"Source: {file1}, Target: {file2}")
            sync_files(file1, file2, exclude_lines=[16, 17])
        else:
            print(f"Source: {file2}, Target: {file1}")
            sync_files(file2, file1, exclude_lines=[16, 17])
    else:
        print("Error retrieving commit times.")

if __name__ == "__main__":
    main()
