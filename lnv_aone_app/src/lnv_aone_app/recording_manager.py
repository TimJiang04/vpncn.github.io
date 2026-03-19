"""
Manages regular recordings (recording_ prefix).

Files are stored under RECORDING_DIR and registered in RECORDING_INDEX_FILE.
This manager is completely independent of AIStreamManager: it never reads or
writes to AISTREAM_DIR or AISTREAM_INDEX_FILE.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from . import config
from .index_store import add_entry, load_index, remove_entry, save_index


class RecordingManager:
    """Handles the lifecycle of ``recording_*`` audio files."""

    def __init__(
        self,
        recording_dir: str = config.RECORDING_DIR,
        index_file: str = config.RECORDING_INDEX_FILE,
        prefix: str = config.RECORDING_PREFIX,
    ) -> None:
        self._dir = recording_dir
        self._index_file = index_file
        self._prefix = prefix
        os.makedirs(self._dir, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def start_recording(self, timestamp: Optional[datetime] = None) -> str:
        """Return the full path for a new recording file and register it."""
        ts = (timestamp or datetime.now()).strftime("%Y%m%d_%H%M%S")
        filename = f"{self._prefix}{ts}.wav"
        filepath = os.path.join(self._dir, filename)

        entry: Dict = {
            "filename": filename,
            "path": filepath,
            "created": (timestamp or datetime.now()).isoformat(),
            "duration": None,
        }
        add_entry(self._index_file, entry)
        return filepath

    def finish_recording(self, filepath: str, duration: float) -> None:
        """Update the duration field for a finished recording."""
        entries = load_index(self._index_file)
        filename = os.path.basename(filepath)
        for entry in entries:
            if entry.get("filename") == filename:
                entry["duration"] = duration
                break
        save_index(self._index_file, entries)

    def delete_recording(self, filename: str) -> bool:
        """Delete a recording file and remove it from the index."""
        filepath = os.path.join(self._dir, filename)
        removed = remove_entry(self._index_file, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        return removed

    def list_recordings(self) -> List[Dict]:
        """Return all entries in the recording index."""
        return load_index(self._index_file)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def directory(self) -> str:
        return self._dir

    @property
    def index_file(self) -> str:
        return self._index_file
