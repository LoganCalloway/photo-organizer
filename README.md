# Photo Organizer Tools

Three Python scripts to help clean up a messy photo collection.

## Tools

### `find_duplicates.py`
Finds exact duplicate photos and moves the extra copies to a `Duplicates/` folder for review.

### `sort_photos.py`
Reads the date each photo was taken and sorts everything into year/month folders.

### `remove_overlaps.py`
Removes photos from one folder that already exist in another folder.

## Requirements

- Python 3
- ExifTool (for `sort_photos.py` only) — install with `brew install exiftool`

## Usage

Always run without `--execute` first to preview what will happen.

```bash
# Find duplicates
python3 find_duplicates.py /path/to/photos
python3 find_duplicates.py /path/to/photos --execute

# Sort by year/month
python3 sort_photos.py /path/to/photos /path/to/output
python3 sort_photos.py /path/to/photos /path/to/output --execute

# Remove overlapping photos between two folders
python3 remove_overlaps.py /path/to/folder1 /path/to/folder2
python3 remove_overlaps.py /path/to/folder1 /path/to/folder2 --execute
```

## Notes

- Nothing is permanently deleted — duplicates are moved to a review folder
- Always make a backup before running any script
- Full guide available on Overleaf
