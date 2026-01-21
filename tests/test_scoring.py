"""
Tests for scoring module.
Tests Deal Heat scoring with configurable thresholds and weights.
"""

from modules.scoring import (
    calculate_deal_heat,
    get_heat_color,
    get_heat_label,
    get_score_breakdown
)
from modules.config import DEFAULT_CONFIG


class TestCalculateDealHeat:
    """Tests for calculate_deal_heat function."""

    def test_base_score_only(self):
        """Test score when no bonuses apply."""
        # Revenue outside sweet spot, 0 peers, 0 margin
        score = calculate_deal_heat(
            revenue=500_000,  # Below 2M
            peer_count=0,
            median_ebitda_margin=0,
            config=DEFAULT_CONFIG
        )
        assert score == 50  # Base only

    def test_all_bonuses_apply(self):
        """Test maximum score when all criteria met."""
        score = calculate_deal_heat(
            revenue=5_000_000,  # In sweet spot (2M-10M)
            peer_count=10,  # Above threshold (5)
            median_ebitda_margin=20,  # Above threshold (15%)
            config=DEFAULT_CONFIG
        )
        assert score == 100  # 50 + 25 + 15 + 10

    def test_revenue_bonus_only(self):
        """Test score with only revenue bonus."""
        score = calculate_deal_heat(
            revenue=5_000_000,  # In sweet spot
            peer_count=2,  # Below threshold
            median_ebitda_margin=10,  # Below threshold
            config=DEFAULT_CONFIG
        )
        assert score == 75  # 50 + 25

    def test_peer_bonus_only(self):
        """Test score with only peer bonus."""
        score = calculate_deal_heat(
            revenue=500_000,  # Outside sweet spot
            peer_count=10,  # Above threshold
            median_ebitda_margin=10,  # Below threshold
            config=DEFAULT_CONFIG
        )
        assert score == 65  # 50 + 15

    def test_margin_bonus_only(self):
        """Test score with only margin bonus."""
        score = calculate_deal_heat(
            revenue=500_000,  # Outside sweet spot
            peer_count=2,  # Below threshold
            median_ebitda_margin=20,  # Above threshold
            config=DEFAULT_CONFIG
        )
        assert score == 60  # 50 + 10

    def test_revenue_at_lower_boundary(self):
        """Test revenue exactly at lower boundary gets bonus."""
        score = calculate_deal_heat(
            revenue=2_000_000,  # Exactly at minimum
            peer_count=0,
            median_ebitda_margin=0,
            config=DEFAULT_CONFIG
        )
        assert score == 75  # 50 + 25

    def test_revenue_at_upper_boundary(self):
        """Test revenue exactly at upper boundary gets bonus."""
        score = calculate_deal_heat(
            revenue=10_000_000,  # Exactly at maximum
            peer_count=0,
            median_ebitda_margin=0,
            config=DEFAULT_CONFIG
        )
        assert score == 75  # 50 + 25

    def test_peer_at_threshold(self):
        """Test peer count exactly at threshold gets bonus."""
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=5,  # Exactly at threshold
            median_ebitda_margin=0,
            config=DEFAULT_CONFIG
        )
        assert score == 65  # 50 + 15

    def test_margin_at_threshold(self):
        """Test margin exactly at threshold gets bonus."""
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=0,
            median_ebitda_margin=15,  # Exactly at threshold
            config=DEFAULT_CONFIG
        )
        assert score == 60  # 50 + 10

    def test_none_margin_no_bonus(self):
        """Test None median margin doesn't give bonus."""
        score = calculate_deal_heat(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=None,
            config=DEFAULT_CONFIG
        )
        assert score == 90  # 50 + 25 + 15, no margin bonus

    def test_score_capped_at_100(self):
        """Test score cannot exceed 100."""
        # Custom config with very high weights
        custom_config = {
            'deal_heat': {
                'revenue_min': 1_000_000,
                'revenue_max': 20_000_000,
                'peer_threshold': 1,
                'margin_threshold': 5,
                'weights': {
                    'base': 80,
                    'revenue_bonus': 50,
                    'peer_bonus': 50,
                    'margin_bonus': 50
                }
            }
        }
        score = calculate_deal_heat(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=custom_config
        )
        assert score == 100  # Capped at 100


class TestConfigurableWeights:
    """Tests for configurable scoring weights."""

    def test_custom_base_weight(self):
        """Test custom base weight."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 30,
                    'revenue_bonus': 25,
                    'peer_bonus': 15,
                    'margin_bonus': 10
                }
            }
        }
        score = calculate_deal_heat(
            revenue=500_000,  # No bonus
            peer_count=0,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 30

    def test_custom_revenue_weight(self):
        """Test custom revenue bonus weight."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 40,
                    'peer_bonus': 15,
                    'margin_bonus': 10
                }
            }
        }
        score = calculate_deal_heat(
            revenue=5_000_000,  # Gets revenue bonus
            peer_count=0,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 90  # 50 + 40

    def test_custom_peer_weight(self):
        """Test custom peer bonus weight."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 25,
                    'peer_bonus': 30,
                    'margin_bonus': 10
                }
            }
        }
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=10,  # Gets peer bonus
            median_ebitda_margin=0,
            config=config
        )
        assert score == 80  # 50 + 30

    def test_custom_margin_weight(self):
        """Test custom margin bonus weight."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 25,
                    'peer_bonus': 15,
                    'margin_bonus': 20
                }
            }
        }
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=0,
            median_ebitda_margin=20,  # Gets margin bonus
            config=config
        )
        assert score == 70  # 50 + 20

    def test_all_custom_weights(self):
        """Test all custom weights together."""
        config = {
            'deal_heat': {
                'revenue_min': 1_000_000,
                'revenue_max': 5_000_000,
                'peer_threshold': 3,
                'margin_threshold': 10,
                'weights': {
                    'base': 40,
                    'revenue_bonus': 20,
                    'peer_bonus': 20,
                    'margin_bonus': 20
                }
            }
        }
        score = calculate_deal_heat(
            revenue=3_000_000,
            peer_count=5,
            median_ebitda_margin=15,
            config=config
        )
        assert score == 100  # 40 + 20 + 20 + 20

    def test_zero_weights(self):
        """Test with zero weights for some bonuses."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 0,
                    'peer_bonus': 0,
                    'margin_bonus': 50
                }
            }
        }
        score = calculate_deal_heat(
            revenue=5_000_000,  # Would get revenue bonus if weight > 0
            peer_count=10,  # Would get peer bonus if weight > 0
            median_ebitda_margin=20,  # Gets margin bonus
            config=config
        )
        assert score == 100  # 50 + 0 + 0 + 50


class TestConfigurableThresholds:
    """Tests for configurable scoring thresholds."""

    def test_custom_revenue_range(self):
        """Test custom revenue sweet spot range."""
        config = {
            'deal_heat': {
                'revenue_min': 500_000,  # Lower minimum
                'revenue_max': 3_000_000,  # Lower maximum
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 25,
                    'peer_bonus': 15,
                    'margin_bonus': 10
                }
            }
        }
        # Revenue in custom range
        score = calculate_deal_heat(
            revenue=1_000_000,
            peer_count=0,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 75  # 50 + 25

        # Revenue outside custom range
        score = calculate_deal_heat(
            revenue=5_000_000,
            peer_count=0,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 50  # Base only

    def test_custom_peer_threshold(self):
        """Test custom peer threshold."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 10,  # Higher threshold
                'margin_threshold': 15,
                'weights': {
                    'base': 50,
                    'revenue_bonus': 25,
                    'peer_bonus': 15,
                    'margin_bonus': 10
                }
            }
        }
        # Below custom threshold
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=5,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 50  # No peer bonus

        # At custom threshold
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=10,
            median_ebitda_margin=0,
            config=config
        )
        assert score == 65  # 50 + 15

    def test_custom_margin_threshold(self):
        """Test custom margin threshold."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 20,  # Higher threshold
                'weights': {
                    'base': 50,
                    'revenue_bonus': 25,
                    'peer_bonus': 15,
                    'margin_bonus': 10
                }
            }
        }
        # Below custom threshold
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=0,
            median_ebitda_margin=15,
            config=config
        )
        assert score == 50  # No margin bonus

        # At custom threshold
        score = calculate_deal_heat(
            revenue=500_000,
            peer_count=0,
            median_ebitda_margin=20,
            config=config
        )
        assert score == 60  # 50 + 10


class TestGetHeatColor:
    """Tests for get_heat_color function."""

    def test_low_score_red(self):
        """Test low score returns red."""
        assert get_heat_color(0) == "#ef4444"
        assert get_heat_color(25) == "#ef4444"
        assert get_heat_color(49) == "#ef4444"

    def test_medium_score_amber(self):
        """Test medium score returns amber."""
        assert get_heat_color(50) == "#f59e0b"
        assert get_heat_color(60) == "#f59e0b"
        assert get_heat_color(74) == "#f59e0b"

    def test_high_score_green(self):
        """Test high score returns green."""
        assert get_heat_color(75) == "#10b981"
        assert get_heat_color(90) == "#10b981"
        assert get_heat_color(100) == "#10b981"

    def test_custom_thresholds(self):
        """Test custom label thresholds for colors."""
        config = {
            'deal_heat': {
                'label_thresholds': {
                    'low_max': 40,  # Low if < 40
                    'medium_max': 80  # Medium if < 80, High if >= 80
                }
            }
        }
        # With custom thresholds
        assert get_heat_color(39, config) == "#ef4444"  # Low
        assert get_heat_color(40, config) == "#f59e0b"  # Medium
        assert get_heat_color(79, config) == "#f59e0b"  # Medium
        assert get_heat_color(80, config) == "#10b981"  # High


class TestGetHeatLabel:
    """Tests for get_heat_label function."""

    def test_low_score_label(self):
        """Test low score returns 'Low' label."""
        assert get_heat_label(0) == "Low"
        assert get_heat_label(25) == "Low"
        assert get_heat_label(49) == "Low"

    def test_medium_score_label(self):
        """Test medium score returns 'Medium' label."""
        assert get_heat_label(50) == "Medium"
        assert get_heat_label(60) == "Medium"
        assert get_heat_label(74) == "Medium"

    def test_high_score_label(self):
        """Test high score returns 'High' label."""
        assert get_heat_label(75) == "High"
        assert get_heat_label(90) == "High"
        assert get_heat_label(100) == "High"

    def test_custom_thresholds(self):
        """Test custom label thresholds."""
        config = {
            'deal_heat': {
                'label_thresholds': {
                    'low_max': 30,
                    'medium_max': 70
                }
            }
        }
        assert get_heat_label(29, config) == "Low"
        assert get_heat_label(30, config) == "Medium"
        assert get_heat_label(69, config) == "Medium"
        assert get_heat_label(70, config) == "High"


class TestGetScoreBreakdown:
    """Tests for get_score_breakdown function."""

    def test_breakdown_structure(self):
        """Test breakdown returns correct structure."""
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=DEFAULT_CONFIG
        )
        assert 'base' in breakdown
        assert 'revenue_bonus' in breakdown
        assert 'peer_bonus' in breakdown
        assert 'margin_bonus' in breakdown
        assert 'total' in breakdown
        assert 'details' in breakdown
        assert 'weights' in breakdown

    def test_breakdown_all_bonuses(self):
        """Test breakdown with all bonuses applied."""
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=DEFAULT_CONFIG
        )
        assert breakdown['base'] == 50
        assert breakdown['revenue_bonus'] == 25
        assert breakdown['peer_bonus'] == 15
        assert breakdown['margin_bonus'] == 10
        assert breakdown['total'] == 100

    def test_breakdown_no_bonuses(self):
        """Test breakdown with no bonuses."""
        breakdown = get_score_breakdown(
            revenue=500_000,
            peer_count=2,
            median_ebitda_margin=5,
            config=DEFAULT_CONFIG
        )
        assert breakdown['base'] == 50
        assert breakdown['revenue_bonus'] == 0
        assert breakdown['peer_bonus'] == 0
        assert breakdown['margin_bonus'] == 0
        assert breakdown['total'] == 50

    def test_breakdown_details_populated(self):
        """Test breakdown details has explanations."""
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=DEFAULT_CONFIG
        )
        assert len(breakdown['details']) == 3
        assert any('sweet spot' in detail for detail in breakdown['details'])
        assert any('peers found' in detail for detail in breakdown['details'])
        assert any('margin' in detail.lower() for detail in breakdown['details'])

    def test_breakdown_with_custom_weights(self):
        """Test breakdown reflects custom weights."""
        config = {
            'deal_heat': {
                'revenue_min': 2_000_000,
                'revenue_max': 10_000_000,
                'peer_threshold': 5,
                'margin_threshold': 15,
                'weights': {
                    'base': 40,
                    'revenue_bonus': 30,
                    'peer_bonus': 20,
                    'margin_bonus': 10
                }
            }
        }
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=config
        )
        assert breakdown['base'] == 40
        assert breakdown['revenue_bonus'] == 30
        assert breakdown['peer_bonus'] == 20
        assert breakdown['margin_bonus'] == 10
        assert breakdown['total'] == 100
        assert breakdown['weights']['base'] == 40
        assert breakdown['weights']['revenue_bonus'] == 30

    def test_breakdown_weights_included(self):
        """Test breakdown includes weights dict."""
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=20,
            config=DEFAULT_CONFIG
        )
        assert 'weights' in breakdown
        assert breakdown['weights']['base'] == 50
        assert breakdown['weights']['revenue_bonus'] == 25
        assert breakdown['weights']['peer_bonus'] == 15
        assert breakdown['weights']['margin_bonus'] == 10

    def test_breakdown_none_margin(self):
        """Test breakdown handles None margin."""
        breakdown = get_score_breakdown(
            revenue=5_000_000,
            peer_count=10,
            median_ebitda_margin=None,
            config=DEFAULT_CONFIG
        )
        assert breakdown['margin_bonus'] == 0
        assert any('N/A' in detail for detail in breakdown['details'])


class TestDefaultConfigIntegration:
    """Tests verifying DEFAULT_CONFIG has correct structure."""

    def test_default_config_has_weights(self):
        """Test DEFAULT_CONFIG includes weights."""
        assert 'deal_heat' in DEFAULT_CONFIG
        assert 'weights' in DEFAULT_CONFIG['deal_heat']

    def test_default_config_weights_values(self):
        """Test DEFAULT_CONFIG has expected weight values."""
        weights = DEFAULT_CONFIG['deal_heat']['weights']
        assert weights['base'] == 50
        assert weights['revenue_bonus'] == 25
        assert weights['peer_bonus'] == 15
        assert weights['margin_bonus'] == 10

    def test_default_config_has_label_thresholds(self):
        """Test DEFAULT_CONFIG includes label thresholds."""
        assert 'label_thresholds' in DEFAULT_CONFIG['deal_heat']

    def test_default_config_label_threshold_values(self):
        """Test DEFAULT_CONFIG has expected threshold values."""
        thresholds = DEFAULT_CONFIG['deal_heat']['label_thresholds']
        assert thresholds['low_max'] == 50
        assert thresholds['medium_max'] == 75

    def test_weights_sum_to_100(self):
        """Test default weights sum to exactly 100."""
        weights = DEFAULT_CONFIG['deal_heat']['weights']
        total = (
            weights['base'] +
            weights['revenue_bonus'] +
            weights['peer_bonus'] +
            weights['margin_bonus']
        )
        assert total == 100
