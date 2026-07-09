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

def find_overlaps(old_photos_dir, proofs_dir, dry_run=True):
    # Scan Proofs first — these are the ones to keep
    proofs_hashes = scan_folder(proofs_dir, "Proofs")

    # Scan Old Photos
    old_hashes = scan_folder(old_photos_dir, "Old Photos")

    # Find overlap — photos that exist in both
    overlap = {h: old_hashes[h] for h in old_hashes if h in proofs_hashes}

    print(f"\n{'=' * 60}")
    print(f"  Photos in Proofs:          {len(proofs_hashes)}")
    print(f"  Photos in Old Photos:      {len(old_hashes)}")
    print(f"  Overlapping (duplicates):  {len(overlap)}")
    print(f"{'=' * 60}\n")

    if not overlap:
        print("🎉 No overlapping photos found! Both folders are unique.")
        return

    dupes_dir = os.path.join(old_photos_dir, 'Duplicates-Proofs')
    total_size = 0

    for h, fpath in overlap.items():
        size_mb = round(os.path.getsize(fpath) / 1024 / 1024, 2)
        total_size += os.path.getsize(fpath)
        proofs_path = proofs_hashes[h]

        if dry_run:
            print(f"  ✅ KEEP in Proofs:      {proofs_path}")
            print(f"  🗑️  REMOVE from Old Photos: {fpath} ({size_mb} MB)")
            print()
        else:
            rel = os.path.relpath(fpath, old_photos_dir)
            dest = os.path.join(dupes_dir, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(fpath, dest)

    print(f"{'=' * 60}")
    print(f"  Files to remove from Old Photos: {len(overlap)}")
    print(f"  Space to free up:                {round(total_size / 1024 / 1024 / 1024, 2)} GB")
    print(f"{'=' * 60}")

    if dry_run:
        print("\n👆 PREVIEW MODE - nothing was moved")
        print("   Run with --execute to move overlaps to Old Photos/Duplicates-Proofs/")
    else:
        print(f"\n✅ Done! Overlapping photos moved to Old Photos/Duplicates-Proofs/")
        print("   Review them, then delete that folder when you're happy.")

def main():
    import sys

    dry_run = '--execute' not in sys.argv
    args = [a for a in sys.argv[1:] if a != '--execute']

    if len(args) < 2:
        print("Usage: python3 remove_overlaps.py /path/to/Old\\ Photos /path/to/Proofs [--execute]")
        print("Example: python3 remove_overlaps.py ~/Desktop/Old\\ Photos ~/Desktop/Proofs --execute")
        sys.exit(1)

    old_photos_dir = os.path.expanduser(args[0])
    proofs_dir = os.path.expanduser(args[1])

    if not os.path.exists(old_photos_dir):
        print(f"❌ Old Photos folder not found: {old_photos_dir}")
        sys.exit(1)

    if not os.path.exists(proofs_dir):
        print(f"❌ Proofs folder not found: {proofs_dir}")
        sys.exit(1)

    if dry_run:
        print("👀 PREVIEW MODE - nothing will be moved")
    else:
        print("🚀 EXECUTE MODE - overlapping photos will be moved out of Old Photos")

    find_overlaps(old_photos_dir, proofs_dir, dry_run=dry_run)

if __name__ == '__main__':
    main()
