"""
Tests for config module.
Tests configuration loading, saving, and peer filtering settings.
"""

import os
import tempfile

from modules.config import (
    load_config,
    save_config,
    reset_to_defaults,
    get_deal_heat_config,
    get_peer_filtering_config,
    get_valuation_config,
    DEFAULT_CONFIG,
    CONFIG_FILE
)


class TestPeerFilteringConfig:
    """Tests for peer filtering configuration."""

    def test_default_config_has_peer_filtering(self):
        """Verify DEFAULT_CONFIG includes peer_filtering section."""
        assert "peer_filtering" in DEFAULT_CONFIG
        pf = DEFAULT_CONFIG["peer_filtering"]
        assert "use_custom_range" in pf
        assert "revenue_min" in pf
        assert "revenue_max" in pf

    def test_default_peer_filtering_values(self):
        """Verify default peer filtering values."""
        pf = DEFAULT_CONFIG["peer_filtering"]
        assert pf["use_custom_range"] is False
        assert pf["revenue_min"] is None
        assert pf["revenue_max"] is None

    def test_get_peer_filtering_config_returns_dict(self):
        """Test get_peer_filtering_config returns a dict."""
        result = get_peer_filtering_config()
        assert isinstance(result, dict)

    def test_get_peer_filtering_config_has_required_keys(self):
        """Test get_peer_filtering_config returns required keys."""
        result = get_peer_filtering_config()
        assert "use_custom_range" in result
        assert "revenue_min" in result
        assert "revenue_max" in result

    def test_get_peer_filtering_config_with_custom_config(self):
        """Test get_peer_filtering_config with custom config dict."""
        custom_config = {
            "peer_filtering": {
                "use_custom_range": True,
                "revenue_min": 1000000,
                "revenue_max": 5000000
            }
        }
        result = get_peer_filtering_config(custom_config)
        assert result["use_custom_range"] is True
        assert result["revenue_min"] == 1000000
        assert result["revenue_max"] == 5000000

    def test_get_peer_filtering_config_falls_back_to_defaults(self):
        """Test fallback to defaults when peer_filtering missing."""
        config_without_pf = {"deal_heat": {}}
        result = get_peer_filtering_config(config_without_pf)
        # Should return default values
        assert result == DEFAULT_CONFIG["peer_filtering"]


class TestDealHeatConfig:
    """Tests for deal heat configuration."""

    def test_get_deal_heat_config_returns_dict(self):
        """Test get_deal_heat_config returns a dict."""
        result = get_deal_heat_config()
        assert isinstance(result, dict)

    def test_get_deal_heat_config_has_required_keys(self):
        """Test get_deal_heat_config returns required keys."""
        result = get_deal_heat_config()
        assert "revenue_min" in result
        assert "revenue_max" in result
        assert "peer_threshold" in result
        assert "margin_threshold" in result


class TestConfigPersistence:
    """Tests for config save/load functionality."""

    def test_save_and_load_peer_filtering(self):
        """Test that peer filtering config persists correctly."""
        # Create a temp config file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            # Temporarily override CONFIG_FILE
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            # Save custom config
            custom_config = {
                **DEFAULT_CONFIG,
                "peer_filtering": {
                    "use_custom_range": True,
                    "revenue_min": 2000000,
                    "revenue_max": 8000000
                }
            }
            save_config(custom_config)

            # Load and verify
            loaded = load_config()
            assert loaded["peer_filtering"]["use_custom_range"] is True
            assert loaded["peer_filtering"]["revenue_min"] == 2000000
            assert loaded["peer_filtering"]["revenue_max"] == 8000000

        finally:
            # Restore original and clean up
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)


class TestValuationConfig:
    """Tests for valuation configuration."""

    def test_default_config_has_valuation(self):
        """Verify DEFAULT_CONFIG includes valuation section."""
        assert "valuation" in DEFAULT_CONFIG
        val = DEFAULT_CONFIG["valuation"]
        assert "confidence_thresholds" in val

    def test_default_valuation_confidence_thresholds(self):
        """Verify default valuation confidence thresholds."""
        val = DEFAULT_CONFIG["valuation"]
        thresholds = val["confidence_thresholds"]
        assert thresholds["high_min_peers"] == 10
        assert thresholds["medium_min_peers"] == 5

    def test_get_valuation_config_returns_dict(self):
        """Test get_valuation_config returns a dict."""
        result = get_valuation_config()
        assert isinstance(result, dict)

    def test_get_valuation_config_has_required_keys(self):
        """Test get_valuation_config returns required keys."""
        result = get_valuation_config()
        assert "confidence_thresholds" in result

    def test_get_valuation_config_with_custom_config(self):
        """Test get_valuation_config with custom config dict."""
        custom_config = {
            "valuation": {
                "confidence_thresholds": {
                    "high_min_peers": 15,
                    "medium_min_peers": 8
                }
            }
        }
        result = get_valuation_config(custom_config)
        assert result["confidence_thresholds"]["high_min_peers"] == 15
        assert result["confidence_thresholds"]["medium_min_peers"] == 8

    def test_get_valuation_config_falls_back_to_defaults(self):
        """Test fallback to defaults when valuation missing."""
        config_without_val = {"deal_heat": {}}
        result = get_valuation_config(config_without_val)
        # Should return default values
        assert result == DEFAULT_CONFIG["valuation"]


class TestAutoSaveConfig:
    """Tests for auto-save configuration functionality."""

    def test_default_config_has_auto_archive_days(self):
        """Verify DEFAULT_CONFIG includes auto_archive_days setting."""
        assert "auto_archive_days" in DEFAULT_CONFIG
        assert DEFAULT_CONFIG["auto_archive_days"] == 90

    def test_save_auto_archive_days(self):
        """Test that auto_archive_days persists correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            custom_config = {
                **DEFAULT_CONFIG,
                "auto_archive_days": 30
            }
            save_config(custom_config)

            loaded = load_config()
            assert loaded["auto_archive_days"] == 30

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)

    def test_save_preserves_nested_deal_heat_settings(self):
        """Test that saving deal_heat preserves nested weights and thresholds."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            # Start with default config
            save_config(DEFAULT_CONFIG.copy())

            # Simulate updating deal_heat while preserving nested values
            loaded = load_config()
            dh = loaded.get('deal_heat', {})
            updated_deal_heat = {
                **dh,
                'revenue_min': 3_000_000,
                'revenue_max': 15_000_000,
                'peer_threshold': 8,
                'margin_threshold': 20
            }
            loaded['deal_heat'] = updated_deal_heat
            save_config(loaded)

            # Verify nested values are preserved
            final = load_config()
            assert final['deal_heat']['revenue_min'] == 3_000_000
            assert final['deal_heat']['revenue_max'] == 15_000_000
            assert final['deal_heat']['peer_threshold'] == 8
            assert final['deal_heat']['margin_threshold'] == 20
            # Check nested values are preserved
            assert 'weights' in final['deal_heat']
            assert 'label_thresholds' in final['deal_heat']

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)

    def test_save_multiple_settings_simultaneously(self):
        """Test that multiple settings can be saved at once."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            custom_config = {
                **DEFAULT_CONFIG,
                "auto_archive_days": 60,
                "deal_heat": {
                    **DEFAULT_CONFIG["deal_heat"],
                    "revenue_min": 5_000_000,
                    "margin_threshold": 25
                }
            }
            save_config(custom_config)

            loaded = load_config()
            assert loaded["auto_archive_days"] == 60
            assert loaded["deal_heat"]["revenue_min"] == 5_000_000
            assert loaded["deal_heat"]["margin_threshold"] == 25

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)

    def test_save_config_creates_file_if_not_exists(self):
        """Test that save_config creates the config file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = os.path.join(temp_dir, 'new_config.json')

            original_config_file = CONFIG_FILE

            try:
                import modules.config as config_module
                config_module.CONFIG_FILE = temp_config_file

                assert not os.path.exists(temp_config_file)
                save_config(DEFAULT_CONFIG)
                assert os.path.exists(temp_config_file)

            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_load_config_returns_defaults_on_missing_file(self):
        """Test that load_config returns defaults when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = os.path.join(temp_dir, 'nonexistent.json')

            original_config_file = CONFIG_FILE

            try:
                import modules.config as config_module
                config_module.CONFIG_FILE = temp_config_file

                loaded = load_config()
                assert loaded == DEFAULT_CONFIG

            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_load_config_returns_defaults_on_invalid_json(self):
        """Test that load_config returns defaults when file has invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {{{")
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            loaded = load_config()
            assert loaded == DEFAULT_CONFIG

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)

    def test_auto_archive_days_boundary_values(self):
        """Test auto_archive_days with boundary values (min: 7, max: 365)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            # Test minimum value
            config = {**DEFAULT_CONFIG, "auto_archive_days": 7}
            save_config(config)
            loaded = load_config()
            assert loaded["auto_archive_days"] == 7

            # Test maximum value
            config = {**DEFAULT_CONFIG, "auto_archive_days": 365}
            save_config(config)
            loaded = load_config()
            assert loaded["auto_archive_days"] == 365

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)

    def test_reset_to_defaults_restores_all_settings(self):
        """Test that reset_to_defaults restores all settings to defaults."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_config_file = f.name

        original_config_file = CONFIG_FILE

        try:
            import modules.config as config_module
            config_module.CONFIG_FILE = temp_config_file

            # Save custom config with modified values
            custom_config = {
                **DEFAULT_CONFIG,
                "auto_archive_days": 30,
                "deal_heat": {
                    **DEFAULT_CONFIG["deal_heat"],
                    "revenue_min": 5_000_000,
                    "margin_threshold": 30
                }
            }
            save_config(custom_config)

            # Verify custom values were saved
            loaded = load_config()
            assert loaded["auto_archive_days"] == 30
            assert loaded["deal_heat"]["revenue_min"] == 5_000_000

            # Reset to defaults
            reset_config = reset_to_defaults()

            # Verify reset returns default values
            assert reset_config["auto_archive_days"] == DEFAULT_CONFIG["auto_archive_days"]
            assert reset_config["deal_heat"]["revenue_min"] == DEFAULT_CONFIG["deal_heat"]["revenue_min"]

            # Verify file was updated
            loaded_after_reset = load_config()
            assert loaded_after_reset["auto_archive_days"] == DEFAULT_CONFIG["auto_archive_days"]
            assert loaded_after_reset["deal_heat"]["revenue_min"] == DEFAULT_CONFIG["deal_heat"]["revenue_min"]

        finally:
            config_module.CONFIG_FILE = original_config_file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)
