#!/usr/bin/env python3

import os
import shutil
import subprocess
from pathlib import Path

PHOTO_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.tif',
    '.gif', '.bmp', '.raw', '.cr2', '.nef', '.arw', '.dng',
    '.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv', '.3gp'
}

MONTH_NAMES = {
    '01': '01 - January', '02': '02 - February', '03': '03 - March',
    '04': '04 - April', '05': '05 - May', '06': '06 - June',
    '07': '07 - July', '08': '08 - August', '09': '09 - September',
    '10': '10 - October', '11': '11 - November', '12': '12 - December'
}

def get_date_from_exif(filepath):
    """Use ExifTool to get the original date taken"""
    try:
        result = subprocess.run(
            ['exiftool', '-DateTimeOriginal', '-CreateDate', '-s3', filepath],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and len(line) >= 10:
                # Format: 2021:05:21 20:26:02
                year = line[0:4]
                month = line[5:7]
                if year.isdigit() and month.isdigit() and 1900 <= int(year) <= 2100 and 1 <= int(month) <= 12:
                    return year, month
    except Exception:
        pass
    return None, None

def get_date_from_modified(filepath):
    """Fall back to file modification date"""
    try:
        import datetime
        mtime = os.path.getmtime(filepath)
        dt = datetime.datetime.fromtimestamp(mtime)
        year = str(dt.year)
        month = str(dt.month).zfill(2)
        if 1990 <= int(year) <= 2100:
            return year, month
    except Exception:
        pass
    return None, None

def get_photo_date(filepath):
    """Try EXIF first, then file modification date"""
    year, month = get_date_from_exif(filepath)
    if year and month:
        return year, month, 'exif'
    
    year, month = get_date_from_modified(filepath)
    if year and month:
        return year, month, 'modified'
    
    return None, None, 'unknown'

def sort_photos(source_dir, output_dir, dry_run=True):
    print(f"\n🔍 Scanning {source_dir} for photos and videos...")
    print(f"📁 Output folder: {output_dir}\n")

    total = 0
    copied = 0
    unknown = 0
    skipped_dupes = 0

    # Track filenames in output to avoid overwriting
    seen_files = {}

    for root, dirs, files in os.walk(source_dir):
        # Skip the Duplicates folder
        dirs[:] = [d for d in dirs if d not in ('Duplicates', os.path.basename(output_dir))]
        
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in PHOTO_EXTENSIONS:
                continue
            
            fpath = os.path.join(root, fname)
            total += 1

            if total % 100 == 0:
                print(f"   Processed {total} files...")

            year, month, source = get_photo_date(fpath)

            if year and month:
                month_name = MONTH_NAMES.get(month, month)
                dest_folder = os.path.join(output_dir, year, month_name)
            else:
                dest_folder = os.path.join(output_dir, 'Unknown')
                unknown += 1

            # Handle duplicate filenames in destination
            dest_path = os.path.join(dest_folder, fname)
            base = Path(fname).stem
            ext_str = Path(fname).suffix
            counter = 1
            while dest_path in seen_files or (not dry_run and os.path.exists(dest_path)):
                dest_path = os.path.join(dest_folder, f"{base}_{counter}{ext_str}")
                counter += 1
            
            seen_files[dest_path] = True

            if dry_run:
                if year and month:
                    print(f"  {year}/{month_name}/{fname}  [{source}]")
                else:
                    print(f"  Unknown/{fname}  [no date found]")
            else:
                os.makedirs(dest_folder, exist_ok=True)
                shutil.move(fpath, dest_path)
            
            copied += 1

    print(f"\n{'=' * 60}")
    print(f"  Total photos/videos found: {total}")
    print(f"  Would be sorted:           {copied}")
    print(f"  No date found (Unknown/):  {unknown}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\n👆 PREVIEW MODE - nothing was copied")
        print(f"   Run with --execute to copy photos to {output_dir}")
    else:
        print(f"\n✅ Done! Photos sorted into {output_dir}")
        print("   Your original files are untouched.")

def main():
    import sys

    dry_run = '--execute' not in sys.argv

    args = [a for a in sys.argv[1:] if a != '--execute']

    if len(args) < 1:
        print("Usage: python3 sort_photos.py /path/to/photos [/path/to/output] [--execute]")
        print("Example: python3 sort_photos.py ~/Desktop/OneDrive\\ Mom ~/Desktop/Photos-Sorted --execute")
        sys.exit(1)

    source_dir = os.path.expanduser(args[0])
    
    if len(args) >= 2:
        output_dir = os.path.expanduser(args[1])
    else:
        output_dir = os.path.join(os.path.dirname(source_dir), 'Photos-Sorted')

    if not os.path.exists(source_dir):
        print(f"❌ Source folder not found: {source_dir}")
        sys.exit(1)

    if dry_run:
        print("👀 PREVIEW MODE - showing what would happen")
    else:
        print("🚀 EXECUTE MODE - copying photos to sorted folder")

    sort_photos(source_dir, output_dir, dry_run=dry_run)

if __name__ == '__main__':
    main()
