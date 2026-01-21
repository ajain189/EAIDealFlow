"""
Tests for storage module.
Tests history save, load, delete, archive, and usage stats functionality.
"""

import os
import json
import tempfile
import base64
from datetime import datetime, timedelta

import pytest

from modules.storage import (
    _load_storage,
    _save_storage,
    _generate_id,
    save_entry,
    get_all_entries,
    get_entry_by_id,
    get_pdf_bytes,
    delete_entry,
    delete_entries,
    archive_entry,
    auto_archive_old_entries,
    restore_entry,
    get_archived_entries,
    search_entries,
    _load_stats,
    increment_stat,
    get_stats,
    reset_stats,
    get_entry_count,
)


@pytest.fixture
def temp_storage_file():
    """Create a temporary storage file for testing."""
    fd, temp_file = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def temp_stats_file():
    """Create a temporary stats file for testing."""
    fd, temp_file = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def mock_storage_env(temp_storage_file, temp_stats_file):
    """Override storage files with temp files."""
    import modules.storage as storage_module
    original_storage = storage_module.STORAGE_FILE
    original_stats = storage_module.STATS_FILE

    storage_module.STORAGE_FILE = temp_storage_file
    storage_module.STATS_FILE = temp_stats_file

    yield

    storage_module.STORAGE_FILE = original_storage
    storage_module.STATS_FILE = original_stats


@pytest.fixture
def sample_entry_data():
    """Sample entry data for testing."""
    return {
        "company_name": "Test Company",
        "industry": "HVAC",
        "revenue": 5000000.0,
        "website": "https://test.com",
        "deal_heat": 75,
        "valuation_range": (10000000, 20000000, 15000000),
        "emails": {
            "hook": {"subject": "Test Hook", "body": "Hook body"},
            "asset": {"subject": "Test Asset", "body": "Asset body"},
            "close": {"subject": "Test Close", "body": "Close body"}
        },
        "pdf_bytes": b"fake pdf content"
    }


class TestGenerateId:
    """Tests for ID generation."""

    def test_generate_id_returns_string(self):
        """Test that _generate_id returns a string."""
        result = _generate_id("Test Company", "2024-01-01T00:00:00")
        assert isinstance(result, str)

    def test_generate_id_returns_12_chars(self):
        """Test that generated ID is 12 characters."""
        result = _generate_id("Test Company", "2024-01-01T00:00:00")
        assert len(result) == 12

    def test_generate_id_is_deterministic(self):
        """Test that same inputs produce same ID."""
        id1 = _generate_id("Test Company", "2024-01-01T00:00:00")
        id2 = _generate_id("Test Company", "2024-01-01T00:00:00")
        assert id1 == id2

    def test_generate_id_different_for_different_inputs(self):
        """Test that different inputs produce different IDs."""
        id1 = _generate_id("Company A", "2024-01-01T00:00:00")
        id2 = _generate_id("Company B", "2024-01-01T00:00:00")
        assert id1 != id2

    def test_generate_id_different_for_different_timestamps(self):
        """Test that different timestamps produce different IDs."""
        id1 = _generate_id("Test Company", "2024-01-01T00:00:00")
        id2 = _generate_id("Test Company", "2024-01-02T00:00:00")
        assert id1 != id2


class TestLoadSaveStorage:
    """Tests for storage load/save operations."""

    def test_load_storage_empty_for_missing(self, mock_storage_env):
        """Test loading from non-existent file returns empty structure."""
        import modules.storage as storage_module
        if os.path.exists(storage_module.STORAGE_FILE):
            os.remove(storage_module.STORAGE_FILE)

        result = _load_storage()
        assert result == {"entries": [], "archived": []}

    def test_load_storage_returns_data_from_file(self, mock_storage_env):
        """Test loading from existing file returns data."""
        import modules.storage as storage_module

        test_data = {"entries": [{"id": "test123"}], "archived": []}
        with open(storage_module.STORAGE_FILE, 'w') as f:
            json.dump(test_data, f)

        result = _load_storage()
        assert result == test_data

    def test_load_storage_handles_corrupt_json(self, mock_storage_env):
        """Test loading handles corrupt JSON gracefully."""
        import modules.storage as storage_module

        with open(storage_module.STORAGE_FILE, 'w') as f:
            f.write("not valid json {{{")

        result = _load_storage()
        assert result == {"entries": [], "archived": []}

    def test_save_storage_creates_file(self, mock_storage_env):
        """Test saving creates storage file."""
        import modules.storage as storage_module

        if os.path.exists(storage_module.STORAGE_FILE):
            os.remove(storage_module.STORAGE_FILE)

        _save_storage({"entries": [], "archived": []})
        assert os.path.exists(storage_module.STORAGE_FILE)

    def test_save_storage_writes_valid_json(self, mock_storage_env):
        """Test saving writes valid JSON."""
        import modules.storage as storage_module

        test_data = {"entries": [{"id": "abc123"}], "archived": []}
        _save_storage(test_data)

        with open(storage_module.STORAGE_FILE, 'r') as f:
            loaded = json.load(f)
        assert loaded == test_data


class TestSaveEntry:
    """Tests for save_entry function."""

    def test_save_entry_returns_id(self, mock_storage_env, sample_entry_data):
        """Test save_entry returns an entry ID."""
        entry_id = save_entry(**sample_entry_data)
        assert isinstance(entry_id, str)
        assert len(entry_id) == 12

    def test_save_entry_persists(self, mock_storage_env, sample_entry_data):
        """Test save_entry persists entry to storage."""
        entry_id = save_entry(**sample_entry_data)

        entries = get_all_entries()
        assert len(entries) == 1
        assert entries[0]["id"] == entry_id

    def test_save_entry_stores_correct_fields(
        self, mock_storage_env, sample_entry_data
    ):
        """Test save_entry stores all correct fields."""
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert entry["company_name"] == "Test Company"
        assert entry["industry"] == "HVAC"
        assert entry["revenue"] == 5000000.0
        assert entry["website"] == "https://test.com"
        assert entry["deal_heat"] == 75
        assert entry["valuation_low"] == 10000000
        assert entry["valuation_high"] == 20000000
        assert entry["valuation_median"] == 15000000
        assert entry["archived"] is False

    def test_save_entry_stores_emails(
        self, mock_storage_env, sample_entry_data
    ):
        """Test save_entry stores emails."""
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert "hook" in entry["emails"]
        assert entry["emails"]["hook"]["subject"] == "Test Hook"

    def test_save_entry_encodes_pdf(self, mock_storage_env, sample_entry_data):
        """Test save_entry encodes PDF as base64."""
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert entry["pdf_base64"] is not None
        decoded = base64.b64decode(entry["pdf_base64"])
        assert decoded == b"fake pdf content"

    def test_save_entry_handles_empty_valuation(
        self, mock_storage_env, sample_entry_data
    ):
        """Test save_entry handles empty valuation range."""
        sample_entry_data["valuation_range"] = ()
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert entry["valuation_low"] == 0
        assert entry["valuation_high"] == 0
        assert entry["valuation_median"] == 0

    def test_save_entry_none_pdf(self, mock_storage_env, sample_entry_data):
        """Test save_entry handles None pdf_bytes."""
        sample_entry_data["pdf_bytes"] = None
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert entry["pdf_base64"] is None

    def test_save_entry_increments_stats(
        self, mock_storage_env, sample_entry_data
    ):
        """Test save_entry increments reports_generated."""
        reset_stats()
        save_entry(**sample_entry_data)

        stats = get_stats()
        assert stats["reports_generated"] == 1

    def test_save_entry_multiple_ordered(
        self, mock_storage_env, sample_entry_data
    ):
        """Test entries are ordered most recent first."""
        sample_entry_data["company_name"] = "First Company"
        save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Second Company"
        save_entry(**sample_entry_data)

        entries = get_all_entries()
        assert len(entries) == 2
        assert entries[0]["company_name"] == "Second Company"
        assert entries[1]["company_name"] == "First Company"


class TestGetAllEntries:
    """Tests for get_all_entries function."""

    def test_get_all_entries_empty_storage(self, mock_storage_env):
        """Test get_all_entries with no entries."""
        entries = get_all_entries()
        assert entries == []

    def test_get_all_entries_excludes_archived(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_all_entries excludes archived entries by default."""
        entry_id = save_entry(**sample_entry_data)
        archive_entry(entry_id)

        entries = get_all_entries()
        assert len(entries) == 0

    def test_get_all_entries_includes_archived(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_all_entries includes archived when requested."""
        entry_id = save_entry(**sample_entry_data)
        archive_entry(entry_id)

        entries = get_all_entries(include_archived=True)
        assert len(entries) == 1


class TestGetEntryById:
    """Tests for get_entry_by_id function."""

    def test_get_entry_by_id_returns_entry(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_entry_by_id returns correct entry."""
        entry_id = save_entry(**sample_entry_data)
        entry = get_entry_by_id(entry_id)

        assert entry is not None
        assert entry["id"] == entry_id

    def test_get_entry_by_id_returns_none_for_missing(self, mock_storage_env):
        """Test get_entry_by_id returns None for missing entry."""
        entry = get_entry_by_id("nonexistent123")
        assert entry is None


class TestGetPdfBytes:
    """Tests for get_pdf_bytes function."""

    def test_get_pdf_bytes_returns_bytes(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_pdf_bytes returns decoded bytes."""
        entry_id = save_entry(**sample_entry_data)
        pdf = get_pdf_bytes(entry_id)

        assert pdf == b"fake pdf content"

    def test_get_pdf_bytes_returns_none_missing(self, mock_storage_env):
        """Test get_pdf_bytes returns None for missing entry."""
        pdf = get_pdf_bytes("nonexistent123")
        assert pdf is None

    def test_get_pdf_bytes_returns_none_no_pdf(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_pdf_bytes returns None when entry has no PDF."""
        sample_entry_data["pdf_bytes"] = None
        entry_id = save_entry(**sample_entry_data)

        pdf = get_pdf_bytes(entry_id)
        assert pdf is None


class TestDeleteEntry:
    """Tests for delete_entry function."""

    def test_delete_entry_removes(self, mock_storage_env, sample_entry_data):
        """Test delete_entry removes the entry."""
        entry_id = save_entry(**sample_entry_data)
        assert get_entry_by_id(entry_id) is not None

        result = delete_entry(entry_id)

        assert result is True
        assert get_entry_by_id(entry_id) is None

    def test_delete_entry_returns_false_for_missing(self, mock_storage_env):
        """Test delete_entry returns False for missing entry."""
        result = delete_entry("nonexistent123")
        assert result is False

    def test_delete_entry_preserves_others(
        self, mock_storage_env, sample_entry_data
    ):
        """Test delete_entry preserves other entries."""
        entry_id1 = save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Other Company"
        entry_id2 = save_entry(**sample_entry_data)

        delete_entry(entry_id1)

        assert get_entry_by_id(entry_id1) is None
        assert get_entry_by_id(entry_id2) is not None


class TestDeleteEntries:
    """Tests for delete_entries (bulk delete) function."""

    def test_delete_entries_removes_multiple(
        self, mock_storage_env, sample_entry_data
    ):
        """Test delete_entries removes multiple entries."""
        ids = []
        for i in range(3):
            sample_entry_data["company_name"] = f"Company {i}"
            ids.append(save_entry(**sample_entry_data))

        deleted_count = delete_entries(ids[:2])

        assert deleted_count == 2
        assert get_entry_by_id(ids[0]) is None
        assert get_entry_by_id(ids[1]) is None
        assert get_entry_by_id(ids[2]) is not None

    def test_delete_entries_returns_count(
        self, mock_storage_env, sample_entry_data
    ):
        """Test delete_entries returns count."""
        entry_id = save_entry(**sample_entry_data)

        count = delete_entries([entry_id, "nonexistent123"])
        assert count == 1

    def test_delete_entries_empty_list(
        self, mock_storage_env, sample_entry_data
    ):
        """Test delete_entries with empty list does nothing."""
        save_entry(**sample_entry_data)

        count = delete_entries([])
        assert count == 0


class TestArchiveEntry:
    """Tests for archive_entry function."""

    def test_archive_entry_sets_flag(
        self, mock_storage_env, sample_entry_data
    ):
        """Test archive_entry sets archived to True."""
        entry_id = save_entry(**sample_entry_data)

        result = archive_entry(entry_id)

        assert result is True
        entry = get_entry_by_id(entry_id)
        assert entry["archived"] is True

    def test_archive_entry_returns_false_missing(self, mock_storage_env):
        """Test archive_entry returns False for missing entry."""
        result = archive_entry("nonexistent123")
        assert result is False


class TestAutoArchiveOldEntries:
    """Tests for auto_archive_old_entries function."""

    def test_auto_archive_archives_old(self, mock_storage_env):
        """Test auto_archive archives entries older than threshold."""
        old_timestamp = (datetime.now() - timedelta(days=100)).isoformat()
        recent_timestamp = datetime.now().isoformat()

        storage_data = {
            "entries": [
                {
                    "id": "old123",
                    "company_name": "Old Co",
                    "created_at": old_timestamp,
                    "archived": False
                },
                {
                    "id": "new123",
                    "company_name": "New Co",
                    "created_at": recent_timestamp,
                    "archived": False
                }
            ],
            "archived": []
        }
        _save_storage(storage_data)

        count = auto_archive_old_entries(days=90)

        assert count == 1
        old_entry = get_entry_by_id("old123")
        new_entry = get_entry_by_id("new123")
        assert old_entry["archived"] is True
        assert new_entry["archived"] is False

    def test_auto_archive_skips_already_archived(self, mock_storage_env):
        """Test auto_archive skips already archived entries."""
        old_timestamp = (datetime.now() - timedelta(days=100)).isoformat()

        storage_data = {
            "entries": [
                {
                    "id": "old123",
                    "company_name": "Old Co",
                    "created_at": old_timestamp,
                    "archived": True
                }
            ],
            "archived": []
        }
        _save_storage(storage_data)

        count = auto_archive_old_entries(days=90)
        assert count == 0

    def test_auto_archive_handles_invalid_timestamps(self, mock_storage_env):
        """Test auto_archive handles invalid timestamps."""
        storage_data = {
            "entries": [
                {
                    "id": "bad123",
                    "company_name": "Bad Co",
                    "created_at": "not a timestamp",
                    "archived": False
                }
            ],
            "archived": []
        }
        _save_storage(storage_data)

        count = auto_archive_old_entries(days=90)
        assert count == 0


class TestRestoreEntry:
    """Tests for restore_entry function."""

    def test_restore_entry_clears_flag(
        self, mock_storage_env, sample_entry_data
    ):
        """Test restore_entry sets archived to False."""
        entry_id = save_entry(**sample_entry_data)
        archive_entry(entry_id)

        result = restore_entry(entry_id)

        assert result is True
        entry = get_entry_by_id(entry_id)
        assert entry["archived"] is False

    def test_restore_entry_returns_false_missing(self, mock_storage_env):
        """Test restore_entry returns False for missing entry."""
        result = restore_entry("nonexistent123")
        assert result is False


class TestGetArchivedEntries:
    """Tests for get_archived_entries function."""

    def test_get_archived_returns_only_archived(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_archived_entries returns only archived entries."""
        entry_id1 = save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Other Company"
        save_entry(**sample_entry_data)

        archive_entry(entry_id1)

        archived = get_archived_entries()
        assert len(archived) == 1
        assert archived[0]["id"] == entry_id1

    def test_get_archived_empty_when_none(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_archived_entries returns empty list when none archived."""
        save_entry(**sample_entry_data)

        archived = get_archived_entries()
        assert archived == []


class TestSearchEntries:
    """Tests for search_entries function."""

    def test_search_by_company_name(self, mock_storage_env, sample_entry_data):
        """Test search_entries finds by company name."""
        sample_entry_data["company_name"] = "Acme Corp"
        save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Beta Inc"
        save_entry(**sample_entry_data)

        results = search_entries("Acme")
        assert len(results) == 1
        assert results[0]["company_name"] == "Acme Corp"

    def test_search_by_industry(self, mock_storage_env, sample_entry_data):
        """Test search_entries finds by industry."""
        sample_entry_data["industry"] = "HVAC"
        save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Other Co"
        sample_entry_data["industry"] = "Transportation"
        save_entry(**sample_entry_data)

        results = search_entries("HVAC")
        assert len(results) == 1

    def test_search_case_insensitive(
        self, mock_storage_env, sample_entry_data
    ):
        """Test search_entries ignores case."""
        sample_entry_data["company_name"] = "ACME Corp"
        save_entry(**sample_entry_data)

        results = search_entries("acme")
        assert len(results) == 1

    def test_search_excludes_archived(
        self, mock_storage_env, sample_entry_data
    ):
        """Test search_entries excludes archived."""
        sample_entry_data["company_name"] = "Acme Corp"
        entry_id = save_entry(**sample_entry_data)
        archive_entry(entry_id)

        results = search_entries("Acme")
        assert len(results) == 0

    def test_search_no_results(self, mock_storage_env, sample_entry_data):
        """Test search_entries returns empty for no matches."""
        save_entry(**sample_entry_data)

        results = search_entries("xyz123nonexistent")
        assert results == []


class TestUsageStats:
    """Tests for usage statistics functions."""

    def test_load_stats_returns_defaults_missing(self, mock_storage_env):
        """Test _load_stats returns defaults when file missing."""
        import modules.storage as storage_module
        if os.path.exists(storage_module.STATS_FILE):
            os.remove(storage_module.STATS_FILE)

        stats = _load_stats()
        assert stats["reports_generated"] == 0
        assert stats["emails_copied"] == 0
        assert stats["pdfs_downloaded"] == 0
        assert stats["first_use"] is None
        assert stats["last_use"] is None

    def test_increment_stat_increases_value(self, mock_storage_env):
        """Test increment_stat increases the stat value."""
        reset_stats()
        increment_stat("emails_copied")
        increment_stat("emails_copied")

        stats = get_stats()
        assert stats["emails_copied"] == 2

    def test_increment_stat_with_amount(self, mock_storage_env):
        """Test increment_stat with custom amount."""
        reset_stats()
        increment_stat("pdfs_downloaded", 5)

        stats = get_stats()
        assert stats["pdfs_downloaded"] == 5

    def test_increment_stat_updates_last_use(self, mock_storage_env):
        """Test increment_stat updates last_use timestamp."""
        reset_stats()
        increment_stat("emails_copied")

        stats = get_stats()
        assert stats["last_use"] is not None

    def test_increment_stat_sets_first_use(self, mock_storage_env):
        """Test increment_stat sets first_use on first call."""
        reset_stats()
        increment_stat("emails_copied")

        stats = get_stats()
        assert stats["first_use"] is not None
        assert stats["first_use"] == stats["last_use"]

    def test_reset_stats_clears_all(self, mock_storage_env):
        """Test reset_stats clears all stats."""
        increment_stat("reports_generated", 10)
        increment_stat("emails_copied", 5)

        reset_stats()

        stats = get_stats()
        assert stats["reports_generated"] == 0
        assert stats["emails_copied"] == 0
        assert stats["first_use"] is None


class TestGetEntryCount:
    """Tests for get_entry_count function."""

    def test_get_entry_count_empty(self, mock_storage_env):
        """Test get_entry_count with empty storage."""
        counts = get_entry_count()
        assert counts["active"] == 0
        assert counts["archived"] == 0
        assert counts["total"] == 0

    def test_get_entry_count_with_entries(
        self, mock_storage_env, sample_entry_data
    ):
        """Test get_entry_count with active and archived."""
        entry_id1 = save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Company 2"
        save_entry(**sample_entry_data)

        sample_entry_data["company_name"] = "Company 3"
        save_entry(**sample_entry_data)

        archive_entry(entry_id1)

        counts = get_entry_count()
        assert counts["active"] == 2
        assert counts["archived"] == 1
        assert counts["total"] == 3
