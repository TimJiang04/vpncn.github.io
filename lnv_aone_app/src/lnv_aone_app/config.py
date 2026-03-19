"""
Configuration constants for lnv_aone_app storage paths and index files.

Storage layout:
  <base_dir>/
    recordings/          # regular recording_ files
      recording_index.json
      recording_<timestamp>.wav
      ...
    aistreams/           # aistream_ files (key_ai button)
      aistream_index.json
      aistream_<timestamp>.wav
      ...
"""

import os

# Base directory under which all recording data lives.
# Can be overridden at runtime via the LNV_BASE_DIR environment variable.
BASE_DIR: str = os.environ.get(
    "LNV_BASE_DIR",
    os.path.join(os.path.expanduser("~"), "lnv_aone_data"),
)

# ── Regular recordings (recording_ prefix) ───────────────────────────────────
RECORDING_DIR: str = os.path.join(BASE_DIR, "recordings")
RECORDING_PREFIX: str = "recording_"
RECORDING_INDEX_FILE: str = os.path.join(RECORDING_DIR, "recording_index.json")

# ── AI-stream recordings (aistream_ prefix, triggered by key_ai) ─────────────
AISTREAM_DIR: str = os.path.join(BASE_DIR, "aistreams")
AISTREAM_PREFIX: str = "aistream_"
AISTREAM_INDEX_FILE: str = os.path.join(AISTREAM_DIR, "aistream_index.json")
