#!/usr/bin/env python3

import os
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict

PHOTO_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.tif',
    '.gif', '.bmp', '.raw', '.cr2', '.nef', '.arw', '.dng',
    '.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv', '.3gp'
}

def get_hash(filepath):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"  ⚠️  Could not read {filepath}: {e}")
        return None

def get_folder_depth(filepath, base_path):
    rel = Path(filepath).relative_to(base_path)
    return len(rel.parts)

def find_duplicates(source_dir):
    print(f"\n🔍 Scanning {source_dir} for photos and videos...")
    print("   This may take a while for large collections...\n")

    hash_map = defaultdict(list)
    total = 0
    skipped = 0

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d != 'Duplicates']
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext not in PHOTO_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            total += 1
            if total % 100 == 0:
                print(f"   Scanned {total} files...")
            h = get_hash(fpath)
            if h:
                hash_map[h].append(fpath)
            else:
                skipped += 1

    print(f"\n✅ Scan complete: {total} photos/videos found, {skipped} skipped")
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    print(f"🔁 Found {len(duplicates)} groups of duplicates\n")
    return duplicates

def choose_keeper(paths, base_path):
    return max(paths, key=lambda p: get_folder_depth(p, base_path))

def process_duplicates(duplicates, source_dir, dry_run=True):
    dupes_dir = os.path.join(source_dir, 'Duplicates')
    total_size = 0
    total_files = 0

    for h, paths in duplicates.items():
        keeper = choose_keeper(paths, source_dir)
        to_move = [p for p in paths if p != keeper]

        if dry_run:
            print(f"✅ KEEP:   {keeper}")
            for r in to_move:
                size_mb = round(os.path.getsize(r) / 1024 / 1024, 2)
                print(f"🗑️  REMOVE: {r} ({size_mb} MB)")
            print()
        
        for fpath in to_move:
            size = os.path.getsize(fpath)
            total_size += size
            total_files += 1

            if not dry_run:
                rel = os.path.relpath(fpath, source_dir)
                dest = os.path.join(dupes_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(fpath, dest)

    return total_files, total_size

def main():
    import sys

    dry_run = '--execute' not in sys.argv

    if len(sys.argv) < 2 or (len(sys.argv) == 2 and sys.argv[1] == '--execute'):
        print("Usage: python3 find_duplicates.py /path/to/photos [--execute]")
        print("Example: python3 find_duplicates.py ~/Library/CloudStorage/OneDrive-Personal --execute")
        sys.exit(1)

    source_dir = os.path.expanduser(sys.argv[1])

    if not os.path.exists(source_dir):
        print(f"❌ Folder not found: {source_dir}")
        sys.exit(1)

    if dry_run:
        print("👀 PREVIEW MODE - nothing will be moved")
    else:
        print("🚀 EXECUTE MODE - duplicates will be moved to Duplicates/ folder")

    duplicates = find_duplicates(source_dir)

    if not duplicates:
        print("🎉 No duplicates found!")
        return

    total_files, total_size = process_duplicates(duplicates, source_dir, dry_run=dry_run)

    print("=" * 60)
    print(f"  Duplicate groups:  {len(duplicates)}")
    print(f"  Files to remove:   {total_files}")
    print(f"  Space to free up:  {round(total_size / 1024 / 1024 / 1024, 2)} GB")
    print("=" * 60)

    if dry_run:
        print("\n👆 PREVIEW MODE - nothing was moved")
        print("   Run with --execute to move duplicates to Duplicates/ folder")
    else:
        print("\n✅ Done! Duplicates moved to Duplicates/ folder")
        print("   Review them, then delete the folder when you're happy")

if __name__ == '__main__':
    main()
