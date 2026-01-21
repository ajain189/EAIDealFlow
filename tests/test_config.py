"""
Tests for config module.
Tests configuration loading, saving, and peer filtering settings.
"""

import os
import tempfile

from modules.config import (
    load_config,
    save_config,
    get_deal_heat_config,
    get_peer_filtering_config,
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
