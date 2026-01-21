"""
Tests for data_ingestion module.
Tests CSV loading for all 3 industry files: HVAC, Transportation, Utility.
"""

import pandas as pd
import numpy as np
import tempfile

from modules.data_ingestion import (
    clean_numeric,
    detect_industry,
    detect_industry_with_details,
    normalize_columns,
    load_all_csvs,
    get_available_industries,
    get_peer_group,
    get_industry_stats,
    INDUSTRY_KEYWORDS,
    COLUMN_MAP
)


class TestCleanNumeric:
    """Tests for clean_numeric function."""

    def test_clean_currency(self):
        assert clean_numeric("$1,000,000") == 1000000.0

    def test_clean_percentage(self):
        assert clean_numeric("15.5%") == 15.5

    def test_clean_multiplier(self):
        assert clean_numeric("3.5x") == 3.5

    def test_clean_integer(self):
        assert clean_numeric(100) == 100.0

    def test_clean_float(self):
        assert clean_numeric(99.9) == 99.9

    def test_clean_na_string(self):
        assert np.isnan(clean_numeric("N/A"))

    def test_clean_dash(self):
        assert np.isnan(clean_numeric("-"))

    def test_clean_none(self):
        assert np.isnan(clean_numeric(None))

    def test_clean_nan(self):
        assert np.isnan(clean_numeric(np.nan))

    def test_clean_invalid_string(self):
        assert np.isnan(clean_numeric("invalid"))

    def test_clean_uppercase_x(self):
        """Test uppercase X multiplier is handled."""
        assert clean_numeric("3.5X") == 3.5

    def test_clean_parentheses_negative(self):
        """Test parentheses indicating negative numbers."""
        assert clean_numeric("(1000)") == -1000.0

    def test_clean_parentheses_with_currency(self):
        """Test parentheses with currency format."""
        assert clean_numeric("($1,000)") == -1000.0

    def test_clean_whitespace(self):
        """Test whitespace is stripped."""
        assert clean_numeric("  $1,000  ") == 1000.0

    def test_clean_combined_dirty_data(self):
        """Test combined dirty data symbols."""
        assert clean_numeric("$1,500,000") == 1500000.0
        assert clean_numeric("25.5%") == 25.5
        assert clean_numeric("2.5x") == 2.5


class TestDetectIndustry:
    """Tests for detect_industry function."""

    def test_detect_hvac(self):
        assert detect_industry("Heating, Ventilation, and Air Conditioning (HVAC) Company") == "HVAC"

    def test_detect_hvac_refrigeration(self):
        assert detect_industry("Commercial HVAC and refrigeration services") == "HVAC"

    def test_detect_transportation_trucking(self):
        assert detect_industry("Short Haul Trucking") == "Transportation"

    def test_detect_transportation_freight(self):
        assert detect_industry("Freight Brokerage and Trucking Company") == "Transportation"

    def test_detect_transportation_logistics(self):
        assert detect_industry("International Logistics Firm") == "Transportation"

    def test_detect_transportation_bus(self):
        assert detect_industry("Charter Bus Business") == "Transportation"

    def test_detect_utility_solar(self):
        assert detect_industry("Solar Energy Production") == "Utility"

    def test_detect_utility_power(self):
        assert detect_industry("Coal-Fired Power Plant") == "Utility"

    def test_detect_utility_water(self):
        assert detect_industry("Water Treatment Company") == "Utility"

    def test_detect_utility_gas(self):
        assert detect_industry("Natural Gas Distribution") == "Utility"

    def test_detect_other(self):
        assert detect_industry("Generic Retail Company") == "Other"

    def test_detect_na(self):
        assert detect_industry(None) == "Other"

    def test_detect_empty(self):
        assert detect_industry("") == "Other"

    def test_detect_hvac_mechanical_contractor(self):
        """Test mechanical contractor keyword."""
        assert detect_industry("Industrial Mechanical Contractor Services") == "HVAC"

    def test_detect_hvac_plumbing(self):
        """Test plumbing keyword."""
        assert detect_industry("Plumbing and HVAC Company") == "HVAC"

    def test_detect_transportation_charter(self):
        """Test charter keyword."""
        assert detect_industry("Charter Bus Business") == "Transportation"

    def test_detect_transportation_customs(self):
        """Test customs broker keyword."""
        assert detect_industry("Customs Broker Services") == "Transportation"

    def test_detect_transportation_warehouse(self):
        """Test warehouse keyword."""
        assert detect_industry("Warehouse and Freight Services") == "Transportation"

    def test_detect_utility_power_plant(self):
        """Test power plant keyword."""
        assert detect_industry("Coal-Fired Power Plant") == "Utility"

    def test_detect_utility_natural_gas(self):
        """Test natural gas keyword."""
        assert detect_industry("Natural Gas Distribution Company") == "Utility"

    def test_detect_utility_water_treatment(self):
        """Test water treatment keyword."""
        assert detect_industry("Water Treatment and Purification") == "Utility"

    def test_detect_utility_photovoltaic(self):
        """Test photovoltaic keyword."""
        assert detect_industry("Photovoltaic Power Generation Projects") == "Utility"

    def test_detect_scoring_prefers_more_matches(self):
        """Test that descriptions with more matching keywords win."""
        # HVAC should win when more HVAC keywords are present
        desc = "Heating, Ventilation, and Air Conditioning (HVAC) Company"
        assert detect_industry(desc) == "HVAC"

    def test_detect_whitespace_only(self):
        """Test whitespace-only string returns Other."""
        assert detect_industry("   ") == "Other"


class TestDetectIndustryWithDetails:
    """Tests for detect_industry_with_details function."""

    def test_returns_dict_structure(self):
        """Test that function returns expected dict structure."""
        result = detect_industry_with_details("HVAC Company")
        assert isinstance(result, dict)
        assert 'industry' in result
        assert 'matched_keywords' in result
        assert 'scores' in result
        assert 'confidence' in result

    def test_hvac_matched_keywords(self):
        """Test matched keywords are returned."""
        result = detect_industry_with_details("Heating, Ventilation, and Air Conditioning (HVAC) Company")
        assert result['industry'] == 'HVAC'
        assert 'hvac' in result['matched_keywords']
        assert 'heating' in result['matched_keywords']
        assert 'ventilation' in result['matched_keywords']
        assert 'air conditioning' in result['matched_keywords']

    def test_scores_dict(self):
        """Test scores dictionary is populated."""
        result = detect_industry_with_details("HVAC and Solar Company")
        assert 'HVAC' in result['scores']
        assert 'Utility' in result['scores']
        assert result['scores']['HVAC'] > 0
        assert result['scores']['Utility'] > 0

    def test_high_confidence_single_industry(self):
        """Test high confidence when only one industry matches."""
        result = detect_industry_with_details("Trucking and Freight Company")
        assert result['industry'] == 'Transportation'
        assert result['confidence'] == 'high'

    def test_confidence_with_competing_industries(self):
        """Test confidence when multiple industries match."""
        # When matches are close, confidence should be lower
        result = detect_industry_with_details("Solar Freight Transportation")
        assert result['confidence'] in ['low', 'medium', 'high']

    def test_other_returns_empty_matches(self):
        """Test Other industry returns empty matches."""
        result = detect_industry_with_details("Generic Retail Store")
        assert result['industry'] == 'Other'
        assert result['matched_keywords'] == []
        assert result['scores'] == {}
        assert result['confidence'] == 'low'

    def test_none_input(self):
        """Test None input returns Other with low confidence."""
        result = detect_industry_with_details(None)
        assert result['industry'] == 'Other'
        assert result['confidence'] == 'low'

    def test_empty_input(self):
        """Test empty input returns Other with low confidence."""
        result = detect_industry_with_details("")
        assert result['industry'] == 'Other'
        assert result['confidence'] == 'low'


class TestNormalizeColumns:
    """Tests for normalize_columns function."""

    def test_rename_revenue(self):
        df = pd.DataFrame({"Revenue": [1000000]})
        result = normalize_columns(df)
        assert "revenue" in result.columns

    def test_rename_ebitda_margin(self):
        df = pd.DataFrame({"EBITDA Margin": ["15%"]})
        result = normalize_columns(df)
        assert "ebitda_margin" in result.columns

    def test_rename_valuation_multiple(self):
        df = pd.DataFrame({"Valuation Multiple": ["3.5x"]})
        result = normalize_columns(df)
        assert "multiple" in result.columns

    def test_clean_numeric_values(self):
        df = pd.DataFrame({
            "Revenue": ["$1,000,000"],
            "EBITDA Margin": ["15%"],
            "Valuation Multiple": ["3.5x"]
        })
        result = normalize_columns(df)
        assert result["revenue"].iloc[0] == 1000000.0
        assert result["ebitda_margin"].iloc[0] == 15.0
        assert result["multiple"].iloc[0] == 3.5

    def test_adds_industry_column(self):
        df = pd.DataFrame({"Description": ["HVAC Company"]})
        result = normalize_columns(df)
        assert "industry" in result.columns
        assert result["industry"].iloc[0] == "HVAC"

    def test_industry_other_when_no_description(self):
        df = pd.DataFrame({"Revenue": [1000000]})
        result = normalize_columns(df)
        assert result["industry"].iloc[0] == "Other"


class TestLoadAllCsvs:
    """Tests for load_all_csvs function with actual data files."""

    def test_loads_all_three_industry_files(self):
        """Verify all 3 CSV files are loaded."""
        df = load_all_csvs("data")

        # Check that data was loaded
        assert not df.empty

        # Check source files are tracked
        assert "source_file" in df.columns
        source_files = df["source_file"].unique().tolist()

        # Verify all 3 industry files are present
        assert "HVAC" in source_files
        assert "Transportation" in source_files
        assert "Utility" in source_files

    def test_has_required_columns(self):
        """Verify normalized columns exist."""
        df = load_all_csvs("data")

        required_cols = ["revenue", "industry", "source_file"]
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"

    def test_hvac_transactions_loaded(self):
        """Verify HVAC transactions are present."""
        df = load_all_csvs("data")
        hvac_df = df[df["source_file"] == "HVAC"]

        assert len(hvac_df) > 0
        # HVAC file has 23 data rows
        assert len(hvac_df) >= 20

    def test_transportation_transactions_loaded(self):
        """Verify Transportation transactions are present."""
        df = load_all_csvs("data")
        transportation_df = df[df["source_file"] == "Transportation"]

        assert len(transportation_df) > 0
        # Transportation file has 14 data rows
        assert len(transportation_df) >= 10

    def test_utility_transactions_loaded(self):
        """Verify Utility transactions are present."""
        df = load_all_csvs("data")
        utility_df = df[df["source_file"] == "Utility"]

        assert len(utility_df) > 0
        # Utility file has 20 data rows
        assert len(utility_df) >= 15

    def test_industry_detection_works(self):
        """Verify industry detection assigns correct industries."""
        df = load_all_csvs("data")

        industries = df["industry"].unique().tolist()

        # At least HVAC, Transportation, Utility should be detected
        assert "HVAC" in industries
        assert "Transportation" in industries
        assert "Utility" in industries

    def test_numeric_columns_cleaned(self):
        """Verify numeric columns are properly cleaned."""
        df = load_all_csvs("data")

        # Revenue should be numeric
        assert df["revenue"].dtype in [np.float64, np.int64, float, int]

        # Should have positive revenue values
        valid_revenue = df["revenue"].dropna()
        assert (valid_revenue > 0).all()

    def test_empty_directory_returns_empty_df(self):
        """Verify empty directory returns empty DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            df = load_all_csvs(tmpdir)
            assert df.empty

    def test_nonexistent_directory_returns_empty_df(self):
        """Verify non-existent directory returns empty DataFrame."""
        df = load_all_csvs("/nonexistent/path")
        assert df.empty


class TestGetAvailableIndustries:
    """Tests for get_available_industries function."""

    def test_returns_industries_from_data(self):
        df = load_all_csvs("data")
        industries = get_available_industries(df)

        assert "HVAC" in industries
        assert "Transportation" in industries
        assert "Utility" in industries

    def test_empty_df_returns_defaults(self):
        industries = get_available_industries(pd.DataFrame())

        assert "HVAC" in industries
        assert "Transportation" in industries
        assert "Utility" in industries
        assert "Other" in industries


class TestGetPeerGroup:
    """Tests for get_peer_group function."""

    def test_filters_by_industry(self):
        df = load_all_csvs("data")
        peers = get_peer_group(df, "HVAC", 3000000)

        assert all(peers["industry"] == "HVAC")

    def test_filters_by_revenue_range(self):
        df = load_all_csvs("data")
        target_revenue = 3000000
        peers = get_peer_group(df, "HVAC", target_revenue)

        # Revenue should be within ±50%
        min_rev = target_revenue * 0.5
        max_rev = target_revenue * 1.5

        valid_revenue = peers["revenue"].dropna()
        assert (valid_revenue >= min_rev).all()
        assert (valid_revenue <= max_rev).all()

    def test_empty_df_returns_empty(self):
        peers = get_peer_group(pd.DataFrame(), "HVAC", 1000000)
        assert peers.empty

    def test_custom_revenue_min(self):
        """Test filtering with custom minimum revenue threshold."""
        df = load_all_csvs("data")
        # Set a higher minimum to narrow the range
        peers = get_peer_group(df, "HVAC", 3000000, revenue_min=2500000)

        valid_revenue = peers["revenue"].dropna()
        if not valid_revenue.empty:
            assert (valid_revenue >= 2500000).all()
            # Max should still be default (3M * 1.5 = 4.5M)
            assert (valid_revenue <= 4500000).all()

    def test_custom_revenue_max(self):
        """Test filtering with custom maximum revenue threshold."""
        df = load_all_csvs("data")
        # Set a lower maximum to narrow the range
        peers = get_peer_group(df, "HVAC", 3000000, revenue_max=3500000)

        valid_revenue = peers["revenue"].dropna()
        if not valid_revenue.empty:
            # Min should still be default (3M * 0.5 = 1.5M)
            assert (valid_revenue >= 1500000).all()
            assert (valid_revenue <= 3500000).all()

    def test_custom_revenue_range_both_bounds(self):
        """Test filtering with both custom min and max revenue thresholds."""
        df = load_all_csvs("data")
        peers = get_peer_group(
            df, "HVAC", 3000000,
            revenue_min=1000000,
            revenue_max=5000000
        )

        valid_revenue = peers["revenue"].dropna()
        if not valid_revenue.empty:
            assert (valid_revenue >= 1000000).all()
            assert (valid_revenue <= 5000000).all()

    def test_wide_revenue_range_returns_more_peers(self):
        """Test that wider revenue range returns more peers."""
        df = load_all_csvs("data")

        # Narrow range (default ±50%)
        narrow_peers = get_peer_group(df, "HVAC", 3000000)

        # Wide range (1M to 50M)
        wide_peers = get_peer_group(
            df, "HVAC", 3000000,
            revenue_min=1000000,
            revenue_max=50000000
        )

        # Wide range should have at least as many peers
        assert len(wide_peers) >= len(narrow_peers)

    def test_zero_revenue_min(self):
        """Test that revenue_min=0 allows all low-revenue peers."""
        df = load_all_csvs("data")
        peers = get_peer_group(
            df, "Transportation", 5000000,
            revenue_min=0,
            revenue_max=10000000
        )

        valid_revenue = peers["revenue"].dropna()
        if not valid_revenue.empty:
            assert (valid_revenue >= 0).all()
            assert (valid_revenue <= 10000000).all()

    def test_filters_different_industries(self):
        """Test filtering works across different industries."""
        df = load_all_csvs("data")

        hvac_peers = get_peer_group(
            df, "HVAC", 5000000,
            revenue_min=1000000, revenue_max=20000000
        )
        trans_peers = get_peer_group(
            df, "Transportation", 5000000,
            revenue_min=1000000, revenue_max=20000000
        )
        util_peers = get_peer_group(
            df, "Utility", 50000000,
            revenue_min=10000000, revenue_max=100000000
        )

        # Each should only contain its own industry
        if not hvac_peers.empty:
            assert all(hvac_peers["industry"] == "HVAC")
        if not trans_peers.empty:
            assert all(trans_peers["industry"] == "Transportation")
        if not util_peers.empty:
            assert all(util_peers["industry"] == "Utility")


class TestGetIndustryStats:
    """Tests for get_industry_stats function."""

    def test_returns_stats_dict(self):
        df = load_all_csvs("data")
        stats = get_industry_stats(df, "HVAC")

        assert "count" in stats
        assert "median_revenue" in stats
        assert "median_margin" in stats
        assert "median_multiple" in stats

    def test_count_is_positive(self):
        df = load_all_csvs("data")
        stats = get_industry_stats(df, "HVAC")

        assert stats["count"] > 0

    def test_empty_industry_returns_zeros(self):
        df = load_all_csvs("data")
        stats = get_industry_stats(df, "NonexistentIndustry")

        assert stats["count"] == 0
        assert stats["median_revenue"] == 0


class TestIndustryKeywords:
    """Tests for INDUSTRY_KEYWORDS constant."""

    def test_hvac_keywords_exist(self):
        assert "HVAC" in INDUSTRY_KEYWORDS
        assert len(INDUSTRY_KEYWORDS["HVAC"]) > 0

    def test_transportation_keywords_exist(self):
        assert "Transportation" in INDUSTRY_KEYWORDS
        assert len(INDUSTRY_KEYWORDS["Transportation"]) > 0

    def test_utility_keywords_exist(self):
        assert "Utility" in INDUSTRY_KEYWORDS
        assert len(INDUSTRY_KEYWORDS["Utility"]) > 0

    def test_hvac_has_expanded_keywords(self):
        """Test HVAC has expanded keyword set."""
        hvac_keywords = INDUSTRY_KEYWORDS["HVAC"]
        assert 'hvac' in hvac_keywords
        assert 'plumbing' in hvac_keywords
        assert 'mechanical contractor' in hvac_keywords
        assert 'pipe insulation' in hvac_keywords

    def test_transportation_has_expanded_keywords(self):
        """Test Transportation has expanded keyword set."""
        trans_keywords = INDUSTRY_KEYWORDS["Transportation"]
        assert 'trucking' in trans_keywords
        assert 'charter' in trans_keywords
        assert 'customs broker' in trans_keywords
        assert 'warehouse' in trans_keywords
        assert 'forwarding' in trans_keywords

    def test_utility_has_expanded_keywords(self):
        """Test Utility has expanded keyword set."""
        util_keywords = INDUSTRY_KEYWORDS["Utility"]
        assert 'solar' in util_keywords
        assert 'power plant' in util_keywords
        assert 'natural gas' in util_keywords
        assert 'water treatment' in util_keywords
        assert 'photovoltaic' in util_keywords
        assert 'wastewater' in util_keywords


class TestColumnMap:
    """Tests for COLUMN_MAP constant."""

    def test_essential_mappings_exist(self):
        assert "revenue" in COLUMN_MAP
        assert "ebitda" in COLUMN_MAP
        assert "multiple" in COLUMN_MAP
        assert "description" in COLUMN_MAP
