"""
Key event handler for lnv_aone_app.

Dispatches the *key_ai* hardware button press to AIStreamManager so that
AI-stream recordings are correctly routed to the dedicated aistream directory
with their own index file.
"""

from .aistream_manager import AIStreamManager
from .recording_manager import RecordingManager


class KeyHandler:
    """Routes hardware key events to the appropriate recording manager."""

    KEY_RECORD = "key_record"
    KEY_AI = "key_ai"

    def __init__(
        self,
        recording_manager: RecordingManager,
        aistream_manager: AIStreamManager,
    ) -> None:
        self._recording = recording_manager
        self._aistream = aistream_manager

        # Tracks the active file path per key so finish() knows which file to
        # update.
        self._active: dict = {}

    def on_key_down(self, key: str) -> str:
        """Handle a key-down event.

        Returns the file path that was opened for recording.

        * ``key_record`` → RecordingManager (recording_* files, recording index)
        * ``key_ai``     → AIStreamManager  (aistream_* files, aistream index)
        """
        if key == self.KEY_RECORD:
            path = self._recording.start_recording()
        elif key == self.KEY_AI:
            path = self._aistream.start_stream()
        else:
            raise ValueError(f"Unknown key: {key!r}")

        self._active[key] = path
        return path

    def on_key_up(self, key: str, duration: float) -> None:
        """Handle a key-up event, finalising the recording with its duration."""
        path = self._active.pop(key, None)
        if path is None:
            return

        if key == self.KEY_RECORD:
            self._recording.finish_recording(path, duration)
        elif key == self.KEY_AI:
            self._aistream.finish_stream(path, duration)
