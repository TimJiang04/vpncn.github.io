"""
Tests for lnv_aone_app — recording path + index separation.

Run with:
    cd lnv_aone_app
    python -m pytest tests/ -v
"""

import json
import os
import tempfile

import pytest

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_dirs(tmp_path):
    """Provide isolated temporary directories for each manager."""
    rec_dir = tmp_path / "recordings"
    ai_dir = tmp_path / "aistreams"
    rec_dir.mkdir()
    ai_dir.mkdir()
    return {
        "rec_dir": str(rec_dir),
        "rec_idx": str(rec_dir / "recording_index.json"),
        "ai_dir": str(ai_dir),
        "ai_idx": str(ai_dir / "aistream_index.json"),
    }


# ── RecordingManager tests ────────────────────────────────────────────────────


class TestRecordingManager:
    def _make(self, dirs):
        from lnv_aone_app.recording_manager import RecordingManager

        return RecordingManager(
            recording_dir=dirs["rec_dir"],
            index_file=dirs["rec_idx"],
        )

    def test_start_recording_creates_index_entry(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_recording()

        assert os.path.basename(path).startswith("recording_")
        entries = mgr.list_recordings()
        assert len(entries) == 1
        assert entries[0]["filename"] == os.path.basename(path)

    def test_finish_recording_updates_duration(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_recording()
        mgr.finish_recording(path, duration=3.5)

        entries = mgr.list_recordings()
        assert entries[0]["duration"] == 3.5

    def test_delete_recording_removes_entry(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_recording()
        filename = os.path.basename(path)

        removed = mgr.delete_recording(filename)
        assert removed is True
        assert mgr.list_recordings() == []

    def test_index_file_stored_in_recording_dir(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        assert mgr.index_file.startswith(tmp_dirs["rec_dir"])

    def test_files_stored_in_recording_dir(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_recording()
        assert path.startswith(tmp_dirs["rec_dir"])


# ── AIStreamManager tests ─────────────────────────────────────────────────────


class TestAIStreamManager:
    def _make(self, dirs):
        from lnv_aone_app.aistream_manager import AIStreamManager

        return AIStreamManager(
            aistream_dir=dirs["ai_dir"],
            index_file=dirs["ai_idx"],
        )

    def test_start_stream_creates_index_entry(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_stream()

        assert os.path.basename(path).startswith("aistream_")
        entries = mgr.list_streams()
        assert len(entries) == 1
        assert entries[0]["filename"] == os.path.basename(path)

    def test_finish_stream_updates_duration(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_stream()
        mgr.finish_stream(path, duration=7.1)

        entries = mgr.list_streams()
        assert entries[0]["duration"] == 7.1

    def test_delete_stream_removes_entry(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_stream()
        filename = os.path.basename(path)

        removed = mgr.delete_stream(filename)
        assert removed is True
        assert mgr.list_streams() == []

    def test_index_file_stored_in_aistream_dir(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        assert mgr.index_file.startswith(tmp_dirs["ai_dir"])

    def test_files_stored_in_aistream_dir(self, tmp_dirs):
        mgr = self._make(tmp_dirs)
        path = mgr.start_stream()
        assert path.startswith(tmp_dirs["ai_dir"])


# ── Separation tests (core requirement) ──────────────────────────────────────


class TestIndexSeparation:
    """Confirm that the two managers use completely independent paths + indexes."""

    def _managers(self, dirs):
        from lnv_aone_app.aistream_manager import AIStreamManager
        from lnv_aone_app.recording_manager import RecordingManager

        rec = RecordingManager(
            recording_dir=dirs["rec_dir"],
            index_file=dirs["rec_idx"],
        )
        ai = AIStreamManager(
            aistream_dir=dirs["ai_dir"],
            index_file=dirs["ai_idx"],
        )
        return rec, ai

    def test_directories_are_different(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        assert rec.directory != ai.directory

    def test_index_files_are_different(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        assert rec.index_file != ai.index_file

    def test_aistream_prefix_differs_from_recording_prefix(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        rec_path = rec.start_recording()
        ai_path = ai.start_stream()

        assert os.path.basename(rec_path).startswith("recording_")
        assert os.path.basename(ai_path).startswith("aistream_")

    def test_recording_entries_not_in_aistream_index(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        rec.start_recording()
        rec.start_recording()

        # Nothing should appear in the aistream index
        assert ai.list_streams() == []

    def test_aistream_entries_not_in_recording_index(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        ai.start_stream()
        ai.start_stream()

        # Nothing should appear in the recording index
        assert rec.list_recordings() == []

    def test_independent_index_files_on_disk(self, tmp_dirs):
        rec, ai = self._managers(tmp_dirs)
        rec.start_recording()
        ai.start_stream()

        # Both index files exist
        assert os.path.exists(tmp_dirs["rec_idx"])
        assert os.path.exists(tmp_dirs["ai_idx"])

        # They contain separate data
        with open(tmp_dirs["rec_idx"], encoding="utf-8") as f:
            rec_data = json.load(f)
        with open(tmp_dirs["ai_idx"], encoding="utf-8") as f:
            ai_data = json.load(f)

        rec_names = [e["filename"] for e in rec_data["entries"]]
        ai_names = [e["filename"] for e in ai_data["entries"]]

        assert all(n.startswith("recording_") for n in rec_names)
        assert all(n.startswith("aistream_") for n in ai_names)
        # No cross-contamination
        assert not set(rec_names) & set(ai_names)


# ── KeyHandler tests ──────────────────────────────────────────────────────────


class TestKeyHandler:
    def _setup(self, dirs):
        from lnv_aone_app.aistream_manager import AIStreamManager
        from lnv_aone_app.key_handler import KeyHandler
        from lnv_aone_app.recording_manager import RecordingManager

        rec = RecordingManager(
            recording_dir=dirs["rec_dir"],
            index_file=dirs["rec_idx"],
        )
        ai = AIStreamManager(
            aistream_dir=dirs["ai_dir"],
            index_file=dirs["ai_idx"],
        )
        handler = KeyHandler(rec, ai)
        return handler, rec, ai

    def test_key_record_routes_to_recording_manager(self, tmp_dirs):
        handler, rec, ai = self._setup(tmp_dirs)
        path = handler.on_key_down("key_record")
        handler.on_key_up("key_record", 2.0)

        assert os.path.basename(path).startswith("recording_")
        assert len(rec.list_recordings()) == 1
        assert len(ai.list_streams()) == 0

    def test_key_ai_routes_to_aistream_manager(self, tmp_dirs):
        handler, rec, ai = self._setup(tmp_dirs)
        path = handler.on_key_down("key_ai")
        handler.on_key_up("key_ai", 4.5)

        assert os.path.basename(path).startswith("aistream_")
        assert len(ai.list_streams()) == 1
        assert len(rec.list_recordings()) == 0

    def test_key_ai_duration_persisted_in_aistream_index(self, tmp_dirs):
        handler, rec, ai = self._setup(tmp_dirs)
        handler.on_key_down("key_ai")
        handler.on_key_up("key_ai", 8.8)

        entry = ai.list_streams()[0]
        assert entry["duration"] == 8.8
