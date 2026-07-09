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

def scan_folder(folder, label):
    print(f"\n🔍 Scanning {label}: {folder}...")
    hash_map = {}
    total = 0
    for root, dirs, files in os.walk(folder):
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
                hash_map[h] = fpath
    print(f"   ✅ Found {total} photos/videos")
    return hash_map

def find_overlaps(folder1, folder2, dry_run=True):
    folder1_name = os.path.basename(folder1.rstrip('/'))
    folder2_name = os.path.basename(folder2.rstrip('/'))

    # Scan folder2 first — these are the ones to keep
    folder2_hashes = scan_folder(folder2, folder2_name)

    # Scan folder1
    folder1_hashes = scan_folder(folder1, folder1_name)

    # Find overlap — photos that exist in both
    overlap = {h: folder1_hashes[h] for h in folder1_hashes if h in folder2_hashes}

    print(f"\n{'=' * 60}")
    print(f"  Photos in {folder2_name}:  {len(folder2_hashes)}")
    print(f"  Photos in {folder1_name}:  {len(folder1_hashes)}")
    print(f"  Overlapping (duplicates):  {len(overlap)}")
    print(f"{'=' * 60}\n")

    if not overlap:
        print(f"🎉 No overlapping photos found! Both folders are unique.")
        return

    dupes_dir = os.path.join(folder1, f'Duplicates-{folder2_name}')
    total_size = 0

    for h, fpath in overlap.items():
        size_mb = round(os.path.getsize(fpath) / 1024 / 1024, 2)
        total_size += os.path.getsize(fpath)
        folder2_path = folder2_hashes[h]

        if dry_run:
            print(f"  ✅ KEEP in {folder2_name}:         {folder2_path}")
            print(f"  🗑️  REMOVE from {folder1_name}: {fpath} ({size_mb} MB)")
            print()
        else:
            rel = os.path.relpath(fpath, folder1)
            dest = os.path.join(dupes_dir, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(fpath, dest)

    print(f"{'=' * 60}")
    print(f"  Files to remove from {folder1_name}: {len(overlap)}")
    print(f"  Space to free up:                    {round(total_size / 1024 / 1024 / 1024, 2)} GB")
    print(f"{'=' * 60}")

    if dry_run:
        print("\n👆 PREVIEW MODE - nothing was moved")
        print(f"   Run with --execute to move overlaps to {folder1_name}/Duplicates-{folder2_name}/")
    else:
        print(f"\n✅ Done! Overlapping photos moved to {folder1_name}/Duplicates-{folder2_name}/")
        print("   Review them, then delete that folder when you're happy.")

def main():
    import sys

    dry_run = '--execute' not in sys.argv
    args = [a for a in sys.argv[1:] if a != '--execute']

    if len(args) < 2:
        print("Usage: python3 remove_overlaps.py /path/to/folder1 /path/to/folder2 [--execute]")
        print("Example: python3 remove_overlaps.py ~/Desktop/Photos ~/Desktop/Proofs --execute")
        sys.exit(1)

    folder1 = os.path.expanduser(args[0])
    folder2 = os.path.expanduser(args[1])

    if not os.path.exists(folder1):
        print(f"❌ Folder not found: {folder1}")
        sys.exit(1)

    if not os.path.exists(folder2):
        print(f"❌ Folder not found: {folder2}")
        sys.exit(1)

    if dry_run:
        print("👀 PREVIEW MODE - nothing will be moved")
    else:
        print("🚀 EXECUTE MODE - overlapping photos will be moved out of folder1")

    find_overlaps(folder1, folder2, dry_run=dry_run)

if __name__ == '__main__':
    main()