"""
Tests for first_visit module.
Tests first-visit tooltip display, tour progression, and state persistence.
"""

import os
import json
import tempfile

import pytest

from modules.first_visit import (
    _load_state,
    _save_state,
    _get_default_state,
    is_first_visit,
    get_current_tooltip,
    get_tooltip_by_id,
    advance_tooltip,
    skip_tour,
    complete_tour,
    reset_tour,
    get_tour_progress,
    get_all_tooltips,
    dismiss_tooltip,
    is_tooltip_dismissed,
    get_tour_state,
    TOOLTIPS,
)


@pytest.fixture
def temp_first_visit_file():
    """Create a temporary first visit state file for testing."""
    fd, temp_file = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield temp_file
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def mock_first_visit_env(temp_first_visit_file):
    """Override first visit file with temp file."""
    import modules.first_visit as first_visit_module
    original_file = first_visit_module.FIRST_VISIT_FILE

    first_visit_module.FIRST_VISIT_FILE = temp_first_visit_file

    yield

    first_visit_module.FIRST_VISIT_FILE = original_file


class TestDefaultState:
    """Tests for default state structure."""

    def test_get_default_state_returns_dict(self):
        """Test _get_default_state returns a dictionary."""
        state = _get_default_state()
        assert isinstance(state, dict)

    def test_get_default_state_has_tour_completed(self):
        """Test default state has tour_completed field."""
        state = _get_default_state()
        assert "tour_completed" in state
        assert state["tour_completed"] is False

    def test_get_default_state_has_tour_skipped(self):
        """Test default state has tour_skipped field."""
        state = _get_default_state()
        assert "tour_skipped" in state
        assert state["tour_skipped"] is False

    def test_get_default_state_has_current_step(self):
        """Test default state has current_step field."""
        state = _get_default_state()
        assert "current_step" in state
        assert state["current_step"] == 0

    def test_get_default_state_has_tooltips_dismissed(self):
        """Test default state has tooltips_dismissed field."""
        state = _get_default_state()
        assert "tooltips_dismissed" in state
        assert state["tooltips_dismissed"] == []


class TestLoadSaveState:
    """Tests for state load/save operations."""

    def test_load_state_returns_defaults_for_missing_file(
        self, mock_first_visit_env
    ):
        """Test loading from non-existent file returns defaults."""
        import modules.first_visit as first_visit_module
        if os.path.exists(first_visit_module.FIRST_VISIT_FILE):
            os.remove(first_visit_module.FIRST_VISIT_FILE)

        state = _load_state()
        assert state == _get_default_state()

    def test_load_state_returns_saved_data(self, mock_first_visit_env):
        """Test loading returns previously saved data."""
        import modules.first_visit as first_visit_module

        test_state = {
            "tour_completed": True,
            "tour_skipped": False,
            "current_step": 3,
            "tooltips_dismissed": ["welcome"]
        }
        with open(first_visit_module.FIRST_VISIT_FILE, 'w') as f:
            json.dump(test_state, f)

        state = _load_state()
        assert state == test_state

    def test_load_state_handles_corrupt_json(self, mock_first_visit_env):
        """Test loading handles corrupt JSON gracefully."""
        import modules.first_visit as first_visit_module

        with open(first_visit_module.FIRST_VISIT_FILE, 'w') as f:
            f.write("not valid json {{{")

        state = _load_state()
        assert state == _get_default_state()

    def test_save_state_creates_file(self, mock_first_visit_env):
        """Test saving creates the state file."""
        import modules.first_visit as first_visit_module

        if os.path.exists(first_visit_module.FIRST_VISIT_FILE):
            os.remove(first_visit_module.FIRST_VISIT_FILE)

        _save_state(_get_default_state())
        assert os.path.exists(first_visit_module.FIRST_VISIT_FILE)

    def test_save_state_writes_valid_json(self, mock_first_visit_env):
        """Test saving writes valid JSON."""
        import modules.first_visit as first_visit_module

        test_state = {
            "tour_completed": True,
            "tour_skipped": False,
            "current_step": 2,
            "tooltips_dismissed": []
        }
        _save_state(test_state)

        with open(first_visit_module.FIRST_VISIT_FILE, 'r') as f:
            loaded = json.load(f)
        assert loaded == test_state


class TestIsFirstVisit:
    """Tests for is_first_visit function."""

    def test_is_first_visit_true_for_new_user(self, mock_first_visit_env):
        """Test is_first_visit returns True for new user."""
        reset_tour()
        assert is_first_visit() is True

    def test_is_first_visit_false_after_tour_completed(
        self, mock_first_visit_env
    ):
        """Test is_first_visit returns False after tour completed."""
        reset_tour()
        complete_tour()
        assert is_first_visit() is False

    def test_is_first_visit_false_after_tour_skipped(
        self, mock_first_visit_env
    ):
        """Test is_first_visit returns False after tour skipped."""
        reset_tour()
        skip_tour()
        assert is_first_visit() is False


class TestGetCurrentTooltip:
    """Tests for get_current_tooltip function."""

    def test_get_current_tooltip_returns_first_for_new_user(
        self, mock_first_visit_env
    ):
        """Test get_current_tooltip returns first tooltip for new user."""
        reset_tour()
        tooltip = get_current_tooltip()

        assert tooltip is not None
        assert tooltip["id"] == TOOLTIPS[0]["id"]

    def test_get_current_tooltip_returns_none_after_completion(
        self, mock_first_visit_env
    ):
        """Test get_current_tooltip returns None after tour completed."""
        reset_tour()
        complete_tour()
        tooltip = get_current_tooltip()

        assert tooltip is None

    def test_get_current_tooltip_returns_none_after_skip(
        self, mock_first_visit_env
    ):
        """Test get_current_tooltip returns None after tour skipped."""
        reset_tour()
        skip_tour()
        tooltip = get_current_tooltip()

        assert tooltip is None

    def test_get_current_tooltip_advances_through_tour(
        self, mock_first_visit_env
    ):
        """Test get_current_tooltip returns correct tooltip at each step."""
        reset_tour()

        for i in range(len(TOOLTIPS)):
            tooltip = get_current_tooltip()
            assert tooltip["id"] == TOOLTIPS[i]["id"]
            advance_tooltip()


class TestGetTooltipById:
    """Tests for get_tooltip_by_id function."""

    def test_get_tooltip_by_id_returns_correct_tooltip(self):
        """Test get_tooltip_by_id returns the correct tooltip."""
        tooltip = get_tooltip_by_id("welcome")
        assert tooltip is not None
        assert tooltip["id"] == "welcome"

    def test_get_tooltip_by_id_returns_none_for_missing(self):
        """Test get_tooltip_by_id returns None for non-existent ID."""
        tooltip = get_tooltip_by_id("nonexistent_tooltip")
        assert tooltip is None

    def test_get_tooltip_by_id_returns_all_tooltips(self):
        """Test get_tooltip_by_id can find all defined tooltips."""
        for expected_tooltip in TOOLTIPS:
            tooltip = get_tooltip_by_id(expected_tooltip["id"])
            assert tooltip is not None
            assert tooltip["id"] == expected_tooltip["id"]


class TestAdvanceTooltip:
    """Tests for advance_tooltip function."""

    def test_advance_tooltip_increments_step(self, mock_first_visit_env):
        """Test advance_tooltip increments current_step."""
        reset_tour()
        state_before = get_tour_state()
        assert state_before["current_step"] == 0

        advance_tooltip()

        state_after = get_tour_state()
        assert state_after["current_step"] == 1

    def test_advance_tooltip_returns_next_tooltip(self, mock_first_visit_env):
        """Test advance_tooltip returns the next tooltip."""
        reset_tour()
        next_tooltip = advance_tooltip()

        assert next_tooltip is not None
        assert next_tooltip["id"] == TOOLTIPS[1]["id"]

    def test_advance_tooltip_completes_tour_at_end(self, mock_first_visit_env):
        """Test advance_tooltip completes tour when reaching the end."""
        reset_tour()

        # Advance through all tooltips
        for _ in range(len(TOOLTIPS)):
            advance_tooltip()

        state = get_tour_state()
        assert state["tour_completed"] is True

    def test_advance_tooltip_returns_none_at_end(self, mock_first_visit_env):
        """Test advance_tooltip returns None when reaching the end."""
        reset_tour()

        # Advance to last tooltip
        for _ in range(len(TOOLTIPS) - 1):
            advance_tooltip()

        # One more advance should complete and return None
        result = advance_tooltip()
        assert result is None


class TestSkipTour:
    """Tests for skip_tour function."""

    def test_skip_tour_sets_flag(self, mock_first_visit_env):
        """Test skip_tour sets tour_skipped flag."""
        reset_tour()
        skip_tour()

        state = get_tour_state()
        assert state["tour_skipped"] is True

    def test_skip_tour_makes_first_visit_false(self, mock_first_visit_env):
        """Test skip_tour makes is_first_visit return False."""
        reset_tour()
        assert is_first_visit() is True

        skip_tour()
        assert is_first_visit() is False


class TestCompleteTour:
    """Tests for complete_tour function."""

    def test_complete_tour_sets_flag(self, mock_first_visit_env):
        """Test complete_tour sets tour_completed flag."""
        reset_tour()
        complete_tour()

        state = get_tour_state()
        assert state["tour_completed"] is True

    def test_complete_tour_makes_first_visit_false(self, mock_first_visit_env):
        """Test complete_tour makes is_first_visit return False."""
        reset_tour()
        assert is_first_visit() is True

        complete_tour()
        assert is_first_visit() is False


class TestResetTour:
    """Tests for reset_tour function."""

    def test_reset_tour_clears_completion(self, mock_first_visit_env):
        """Test reset_tour clears tour_completed flag."""
        complete_tour()
        reset_tour()

        state = get_tour_state()
        assert state["tour_completed"] is False

    def test_reset_tour_clears_skipped(self, mock_first_visit_env):
        """Test reset_tour clears tour_skipped flag."""
        skip_tour()
        reset_tour()

        state = get_tour_state()
        assert state["tour_skipped"] is False

    def test_reset_tour_resets_step(self, mock_first_visit_env):
        """Test reset_tour resets current_step to 0."""
        reset_tour()
        advance_tooltip()
        advance_tooltip()

        reset_tour()

        state = get_tour_state()
        assert state["current_step"] == 0

    def test_reset_tour_clears_dismissed(self, mock_first_visit_env):
        """Test reset_tour clears dismissed tooltips."""
        reset_tour()
        dismiss_tooltip("welcome")

        reset_tour()

        state = get_tour_state()
        assert state["tooltips_dismissed"] == []


class TestGetTourProgress:
    """Tests for get_tour_progress function."""

    def test_get_tour_progress_returns_dict(self, mock_first_visit_env):
        """Test get_tour_progress returns a dictionary."""
        reset_tour()
        progress = get_tour_progress()
        assert isinstance(progress, dict)

    def test_get_tour_progress_has_current_step(self, mock_first_visit_env):
        """Test progress has current_step field."""
        reset_tour()
        progress = get_tour_progress()
        assert "current_step" in progress
        assert progress["current_step"] == 0

    def test_get_tour_progress_has_total_steps(self, mock_first_visit_env):
        """Test progress has total_steps field."""
        reset_tour()
        progress = get_tour_progress()
        assert "total_steps" in progress
        assert progress["total_steps"] == len(TOOLTIPS)

    def test_get_tour_progress_has_percentage(self, mock_first_visit_env):
        """Test progress has percentage field."""
        reset_tour()
        progress = get_tour_progress()
        assert "percentage" in progress
        assert progress["percentage"] == 0

    def test_get_tour_progress_percentage_updates(self, mock_first_visit_env):
        """Test percentage updates as tour progresses."""
        reset_tour()

        # Advance halfway through
        halfway = len(TOOLTIPS) // 2
        for _ in range(halfway):
            advance_tooltip()

        progress = get_tour_progress()
        expected_pct = int((halfway / len(TOOLTIPS)) * 100)
        assert progress["percentage"] == expected_pct

    def test_get_tour_progress_is_complete(self, mock_first_visit_env):
        """Test is_complete field reflects completion status."""
        reset_tour()
        progress = get_tour_progress()
        assert progress["is_complete"] is False

        complete_tour()
        progress = get_tour_progress()
        assert progress["is_complete"] is True


class TestGetAllTooltips:
    """Tests for get_all_tooltips function."""

    def test_get_all_tooltips_returns_list(self):
        """Test get_all_tooltips returns a list."""
        tooltips = get_all_tooltips()
        assert isinstance(tooltips, list)

    def test_get_all_tooltips_returns_all(self):
        """Test get_all_tooltips returns all defined tooltips."""
        tooltips = get_all_tooltips()
        assert len(tooltips) == len(TOOLTIPS)

    def test_get_all_tooltips_returns_copy(self):
        """Test get_all_tooltips returns a copy, not the original."""
        tooltips = get_all_tooltips()
        tooltips.append({"id": "test"})

        assert len(get_all_tooltips()) == len(TOOLTIPS)


class TestDismissTooltip:
    """Tests for dismiss_tooltip function."""

    def test_dismiss_tooltip_adds_to_dismissed(self, mock_first_visit_env):
        """Test dismiss_tooltip adds ID to dismissed list."""
        reset_tour()
        dismiss_tooltip("welcome")

        state = get_tour_state()
        assert "welcome" in state["tooltips_dismissed"]

    def test_dismiss_tooltip_no_duplicates(self, mock_first_visit_env):
        """Test dismiss_tooltip doesn't add duplicates."""
        reset_tour()
        dismiss_tooltip("welcome")
        dismiss_tooltip("welcome")

        state = get_tour_state()
        assert state["tooltips_dismissed"].count("welcome") == 1


class TestIsTooltipDismissed:
    """Tests for is_tooltip_dismissed function."""

    def test_is_tooltip_dismissed_false_initially(self, mock_first_visit_env):
        """Test is_tooltip_dismissed returns False initially."""
        reset_tour()
        assert is_tooltip_dismissed("welcome") is False

    def test_is_tooltip_dismissed_true_after_dismiss(
        self, mock_first_visit_env
    ):
        """Test is_tooltip_dismissed returns True after dismissing."""
        reset_tour()
        dismiss_tooltip("welcome")
        assert is_tooltip_dismissed("welcome") is True

    def test_is_tooltip_dismissed_only_affects_dismissed(
        self, mock_first_visit_env
    ):
        """Test dismissing one tooltip doesn't affect others."""
        reset_tour()
        dismiss_tooltip("welcome")

        assert is_tooltip_dismissed("welcome") is True
        assert is_tooltip_dismissed("company_input") is False


class TestTooltipStructure:
    """Tests for tooltip configuration structure."""

    def test_all_tooltips_have_required_fields(self):
        """Test all tooltips have required fields."""
        required_fields = ["id", "title", "message", "target", "icon"]

        for tooltip in TOOLTIPS:
            for field in required_fields:
                assert field in tooltip, f"Tooltip {tooltip.get('id', 'unknown')} missing {field}"

    def test_all_tooltips_have_unique_ids(self):
        """Test all tooltip IDs are unique."""
        ids = [t["id"] for t in TOOLTIPS]
        assert len(ids) == len(set(ids)), "Duplicate tooltip IDs found"

    def test_tooltips_have_non_empty_strings(self):
        """Test tooltip strings are not empty."""
        for tooltip in TOOLTIPS:
            assert len(tooltip["id"]) > 0
            assert len(tooltip["title"]) > 0
            assert len(tooltip["message"]) > 0


class TestGetTourState:
    """Tests for get_tour_state function."""

    def test_get_tour_state_returns_dict(self, mock_first_visit_env):
        """Test get_tour_state returns a dictionary."""
        reset_tour()
        state = get_tour_state()
        assert isinstance(state, dict)

    def test_get_tour_state_has_all_fields(self, mock_first_visit_env):
        """Test get_tour_state returns all expected fields."""
        reset_tour()
        state = get_tour_state()

        expected_fields = [
            "tour_completed",
            "tour_skipped",
            "current_step",
            "tooltips_dismissed"
        ]
        for field in expected_fields:
            assert field in state

    def test_get_tour_state_reflects_changes(self, mock_first_visit_env):
        """Test get_tour_state reflects state changes."""
        reset_tour()

        state1 = get_tour_state()
        assert state1["current_step"] == 0

        advance_tooltip()

        state2 = get_tour_state()
        assert state2["current_step"] == 1
