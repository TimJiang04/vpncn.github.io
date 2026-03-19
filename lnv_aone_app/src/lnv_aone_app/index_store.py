"""
Index helper shared by both RecordingManager and AIStreamManager.

Each manager owns its own index file (RECORDING_INDEX_FILE or
AISTREAM_INDEX_FILE).  This module provides the load/save/add/remove
primitives so the two managers stay independent and never touch each
other's index.

Index file format (JSON):
  {
    "entries": [
      {
        "filename": "recording_20240101_120000.wav",
        "path":     "/abs/path/to/recordings/recording_20240101_120000.wav",
        "created":  "2024-01-01T12:00:00",
        "duration": 5.3
      },
      ...
    ]
  }
"""

import json
import os
from typing import Dict, List


def load_index(index_file: str) -> List[Dict]:
    """Return the list of index entries from *index_file*.

    Creates an empty index when the file does not yet exist.
    """
    if not os.path.exists(index_file):
        return []
    with open(index_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("entries", [])


def save_index(index_file: str, entries: List[Dict]) -> None:
    """Persist *entries* to *index_file*, creating parent directories as needed."""
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    with open(index_file, "w", encoding="utf-8") as fh:
        json.dump({"entries": entries}, fh, indent=2, ensure_ascii=False)


def add_entry(index_file: str, entry: Dict) -> None:
    """Append *entry* to the index stored in *index_file*."""
    entries = load_index(index_file)
    entries.append(entry)
    save_index(index_file, entries)


def remove_entry(index_file: str, filename: str) -> bool:
    """Remove the entry whose ``filename`` matches *filename*.

    Returns ``True`` if an entry was removed, ``False`` otherwise.
    """
    entries = load_index(index_file)
    new_entries = [e for e in entries if e.get("filename") != filename]
    if len(new_entries) == len(entries):
        return False
    save_index(index_file, new_entries)
    return True
