"""
lnv_aone_app — main entry point.

Run with:
    python -m lnv_aone_app

This module wires together RecordingManager, AIStreamManager, and KeyHandler,
then starts a simple interactive REPL that simulates key presses for
demonstration / manual testing purposes.
"""

import sys
import time

from lnv_aone_app import AIStreamManager, KeyHandler, RecordingManager
from lnv_aone_app import config


def _show_status(recording_mgr: RecordingManager, aistream_mgr: AIStreamManager) -> None:
    print("\n── Storage layout ────────────────────────────────────────")
    print(f"  recordings dir : {recording_mgr.directory}")
    print(f"  recordings idx : {recording_mgr.index_file}")
    print(f"  aistreams  dir : {aistream_mgr.directory}")
    print(f"  aistreams  idx : {aistream_mgr.index_file}")

    recordings = recording_mgr.list_recordings()
    streams = aistream_mgr.list_streams()
    print(f"\n  recording_ files  : {len(recordings)}")
    for e in recordings:
        print(f"    {e['filename']}  duration={e['duration']}s")
    print(f"\n  aistream_  files  : {len(streams)}")
    for e in streams:
        print(f"    {e['filename']}  duration={e['duration']}s")
    print()


def main() -> None:
    recording_mgr = RecordingManager()
    aistream_mgr = AIStreamManager()
    handler = KeyHandler(recording_mgr, aistream_mgr)

    print("lnv_aone_app  —  key simulation REPL")
    print("Commands:  r=key_record  a=key_ai  s=status  q=quit")

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd == "q":
            break
        elif cmd == "s":
            _show_status(recording_mgr, aistream_mgr)
        elif cmd in ("r", "a"):
            key = KeyHandler.KEY_RECORD if cmd == "r" else KeyHandler.KEY_AI
            path = handler.on_key_down(key)
            print(f"  started → {path}")
            time.sleep(0.05)
            duration = round(time.time() % 10, 2)
            handler.on_key_up(key, duration)
            print(f"  stopped  (duration={duration}s)")
        else:
            print("  unknown command")


if __name__ == "__main__":
    main()
