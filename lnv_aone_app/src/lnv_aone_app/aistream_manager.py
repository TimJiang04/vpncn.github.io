"""
Manages AI-stream recordings (aistream_ prefix, triggered by the key_ai button).

Files are stored under AISTREAM_DIR — a directory **separate** from the
regular recordings directory — and are registered in AISTREAM_INDEX_FILE,
which is an **independent** index file that has no overlap with
RECORDING_INDEX_FILE.

This separation ensures:
  * aistream_ files are never mixed with recording_ files on disk.
  * Each file type is searchable / manageable through its own dedicated index.
  * Adding, removing, or rebuilding one index never affects the other.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from . import config
from .index_store import add_entry, load_index, remove_entry, save_index


class AIStreamManager:
    """Handles the lifecycle of ``aistream_*`` audio files (key_ai button)."""

    def __init__(
        self,
        aistream_dir: str = config.AISTREAM_DIR,
        index_file: str = config.AISTREAM_INDEX_FILE,
        prefix: str = config.AISTREAM_PREFIX,
    ) -> None:
        self._dir = aistream_dir
        self._index_file = index_file
        self._prefix = prefix
        os.makedirs(self._dir, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def start_stream(self, timestamp: Optional[datetime] = None) -> str:
        """Return the full path for a new aistream file and register it in the
        aistream index.

        This is the entry point called when the *key_ai* button is pressed to
        begin an AI-assisted recording session.
        """
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

    def finish_stream(self, filepath: str, duration: float) -> None:
        """Update the duration field for a finished AI-stream recording."""
        entries = load_index(self._index_file)
        filename = os.path.basename(filepath)
        for entry in entries:
            if entry.get("filename") == filename:
                entry["duration"] = duration
                break
        save_index(self._index_file, entries)

    def delete_stream(self, filename: str) -> bool:
        """Delete an aistream file and remove it from the aistream index."""
        filepath = os.path.join(self._dir, filename)
        removed = remove_entry(self._index_file, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        return removed

    def list_streams(self) -> List[Dict]:
        """Return all entries in the aistream index."""
        return load_index(self._index_file)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def directory(self) -> str:
        return self._dir

    @property
    def index_file(self) -> str:
        return self._index_file
