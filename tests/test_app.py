"""
Tests for the main Streamlit app (app.py).
Tests module imports, helper functions, and component integration.
"""

from unittest.mock import patch
import pandas as pd


class TestAppImports:
    """Tests that all required modules can be imported correctly."""

    def test_import_data_ingestion(self):
        """Test data_ingestion module imports."""
        from modules.data_ingestion import (
            load_all_csvs, get_peer_group, get_available_industries
        )
        assert callable(load_all_csvs)
        assert callable(get_peer_group)
        assert callable(get_available_industries)

    def test_import_scoring(self):
        """Test scoring module imports."""
        from modules.scoring import (
            calculate_deal_heat, get_heat_color, get_heat_label
        )
        assert callable(calculate_deal_heat)
        assert callable(get_heat_color)
        assert callable(get_heat_label)

    def test_import_visualization(self):
        """Test visualization module imports."""
        from modules.visualization import (
            create_market_chart, calculate_valuation_range, get_chart_config
        )
        assert callable(create_market_chart)
        assert callable(calculate_valuation_range)
        assert callable(get_chart_config)

    def test_import_ai_service(self):
        """Test ai_service module imports."""
        from modules.ai_service import (
            scrape_website_summary, generate_emails, generate_upside_bullets
        )
        assert callable(scrape_website_summary)
        assert callable(generate_emails)
        assert callable(generate_upside_bullets)

    def test_import_pdf_generator(self):
        """Test pdf_generator module imports."""
        from modules.pdf_generator import generate_one_pager
        assert callable(generate_one_pager)

    def test_import_storage(self):
        """Test storage module imports."""
        from modules.storage import (
            save_entry, get_all_entries, get_pdf_bytes,
            delete_entry, delete_entries, auto_archive_old_entries,
            increment_stat, get_stats
        )
        assert callable(save_entry)
        assert callable(get_all_entries)
        assert callable(get_pdf_bytes)
        assert callable(delete_entry)
        assert callable(delete_entries)
        assert callable(auto_archive_old_entries)
        assert callable(increment_stat)
        assert callable(get_stats)

    def test_import_clipboard(self):
        """Test clipboard module imports."""
        from modules.clipboard import (
            copy_to_clipboard, format_email_for_copy,
            format_valuation_for_copy, format_deal_summary_for_copy
        )
        assert callable(copy_to_clipboard)
        assert callable(format_email_for_copy)
        assert callable(format_valuation_for_copy)
        assert callable(format_deal_summary_for_copy)

    def test_import_config(self):
        """Test config module imports."""
        from modules.config import load_config, save_config, reset_to_defaults
        assert callable(load_config)
        assert callable(save_config)
        assert callable(reset_to_defaults)

    def test_import_first_visit(self):
        """Test first_visit module imports."""
        from modules.first_visit import (
            is_first_visit, get_current_tooltip, advance_tooltip,
            skip_tour, get_tour_progress, reset_tour
        )
        assert callable(is_first_visit)
        assert callable(get_current_tooltip)
        assert callable(advance_tooltip)
        assert callable(skip_tour)
        assert callable(get_tour_progress)
        assert callable(reset_tour)


class TestDataLoading:
    """Tests for data loading functionality."""

    def test_load_all_csvs_returns_dataframe(self):
        """Test that load_all_csvs returns a DataFrame."""
        from modules.data_ingestion import load_all_csvs
        df = load_all_csvs("data")
        assert isinstance(df, pd.DataFrame)

    def test_load_all_csvs_not_empty(self):
        """Test that loaded data is not empty."""
        from modules.data_ingestion import load_all_csvs
        df = load_all_csvs("data")
        assert not df.empty

    def test_load_all_csvs_has_required_columns(self):
        """Test that loaded data has required columns."""
        from modules.data_ingestion import load_all_csvs
        df = load_all_csvs("data")
        # Check for essential columns
        assert 'revenue' in df.columns
        assert 'industry' in df.columns

    def test_get_available_industries_returns_list(self):
        """Test that get_available_industries returns a list."""
        from modules.data_ingestion import load_all_csvs, get_available_industries
        df = load_all_csvs("data")
        industries = get_available_industries(df)
        assert isinstance(industries, list)

    def test_get_available_industries_not_empty(self):
        """Test that available industries list is not empty."""
        from modules.data_ingestion import load_all_csvs, get_available_industries
        df = load_all_csvs("data")
        industries = get_available_industries(df)
        assert len(industries) > 0


class TestPeerFiltering:
    """Tests for peer filtering functionality."""

    def test_get_peer_group_returns_dataframe(self):
        """Test that get_peer_group returns a DataFrame."""
        from modules.data_ingestion import load_all_csvs, get_peer_group
        df = load_all_csvs("data")
        if not df.empty and 'industry' in df.columns:
            industry = df['industry'].iloc[0]
            revenue = df['revenue'].iloc[0] if 'revenue' in df.columns else 1000000
            peers = get_peer_group(df, industry, revenue)
            assert isinstance(peers, pd.DataFrame)

    def test_get_peer_group_empty_df(self):
        """Test get_peer_group with empty DataFrame."""
        from modules.data_ingestion import get_peer_group
        df = pd.DataFrame()
        peers = get_peer_group(df, "HVAC", 3000000)
        assert isinstance(peers, pd.DataFrame)
        assert peers.empty


class TestDealHeatIntegration:
    """Tests for Deal Heat score integration."""

    def test_deal_heat_calculation(self):
        """Test Deal Heat calculation with sample data."""
        from modules.scoring import calculate_deal_heat
        from modules.config import load_config

        config = load_config()
        heat = calculate_deal_heat(5000000, 10, 20, config)
        assert isinstance(heat, int)
        assert 0 <= heat <= 100

    def test_heat_color_returns_valid_hex(self):
        """Test that heat color returns valid hex code."""
        from modules.scoring import get_heat_color
        color = get_heat_color(75)
        assert color.startswith("#")
        assert len(color) == 7

    def test_heat_label_returns_string(self):
        """Test that heat label returns a string."""
        from modules.scoring import get_heat_label
        label = get_heat_label(75)
        assert isinstance(label, str)
        assert label in ["Low", "Medium", "High"]


class TestVisualizationIntegration:
    """Tests for visualization integration."""

    def test_create_market_chart_returns_figure(self):
        """Test that create_market_chart returns a Plotly figure."""
        import plotly.graph_objects as go
        from modules.visualization import create_market_chart
        from modules.data_ingestion import load_all_csvs, get_peer_group

        df = load_all_csvs("data")
        if not df.empty and 'industry' in df.columns:
            industry = df['industry'].iloc[0]
            revenue = 3000000
            peers = get_peer_group(df, industry, revenue)
            fig = create_market_chart(peers, "Test Company", revenue, 15.0)
            assert isinstance(fig, go.Figure)

    def test_calculate_valuation_range_returns_tuple(self):
        """Test that calculate_valuation_range returns a tuple."""
        from modules.visualization import calculate_valuation_range
        from modules.data_ingestion import load_all_csvs, get_peer_group

        df = load_all_csvs("data")
        if not df.empty and 'industry' in df.columns:
            industry = df['industry'].iloc[0]
            revenue = 3000000
            peers = get_peer_group(df, industry, revenue)
            val_range = calculate_valuation_range(peers, revenue)
            assert isinstance(val_range, tuple)
            assert len(val_range) == 3


class TestStorageIntegration:
    """Tests for storage integration."""

    def test_get_all_entries_returns_list(self):
        """Test that get_all_entries returns a list."""
        from modules.storage import get_all_entries
        entries = get_all_entries()
        assert isinstance(entries, list)

    def test_get_stats_returns_dict(self):
        """Test that get_stats returns a dictionary."""
        from modules.storage import get_stats
        stats = get_stats()
        assert isinstance(stats, dict)


class TestConfigIntegration:
    """Tests for configuration integration."""

    def test_load_config_returns_dict(self):
        """Test that load_config returns a dictionary."""
        from modules.config import load_config
        config = load_config()
        assert isinstance(config, dict)

    def test_config_has_deal_heat(self):
        """Test that config has deal_heat section."""
        from modules.config import load_config
        config = load_config()
        assert 'deal_heat' in config

    def test_config_has_auto_archive_days(self):
        """Test that config has auto_archive_days setting."""
        from modules.config import load_config
        config = load_config()
        assert 'auto_archive_days' in config


class TestFirstVisitIntegration:
    """Tests for first visit tour integration."""

    def test_is_first_visit_returns_bool(self):
        """Test that is_first_visit returns a boolean."""
        from modules.first_visit import is_first_visit
        result = is_first_visit()
        assert isinstance(result, bool)

    def test_get_tour_progress_returns_dict(self):
        """Test that get_tour_progress returns a dictionary."""
        from modules.first_visit import get_tour_progress
        progress = get_tour_progress()
        assert isinstance(progress, dict)

    def test_tour_progress_has_required_keys(self):
        """Test that tour progress has required keys."""
        from modules.first_visit import get_tour_progress
        progress = get_tour_progress()
        assert 'current_step' in progress
        assert 'total_steps' in progress


class TestClipboardFormatting:
    """Tests for clipboard formatting functions."""

    def test_format_email_for_copy(self):
        """Test email formatting for clipboard."""
        from modules.clipboard import format_email_for_copy
        result = format_email_for_copy("Test Subject", "Test body content")
        assert "Subject: Test Subject" in result
        assert "Test body content" in result

    def test_format_valuation_for_copy(self):
        """Test valuation formatting for clipboard."""
        from modules.clipboard import format_valuation_for_copy
        result = format_valuation_for_copy("Test Co", 1000000, 2000000, 1500000)
        assert "Test Co" in result
        assert "$" in result

    def test_format_deal_summary_for_copy(self):
        """Test deal summary formatting for clipboard."""
        from modules.clipboard import format_deal_summary_for_copy
        result = format_deal_summary_for_copy(
            "Test Co", "HVAC", 3000000, 75, "High", 10
        )
        assert "Test Co" in result
        assert "HVAC" in result
        assert "75" in result


class TestAppWorkflow:
    """Tests for end-to-end app workflow."""

    def test_full_analysis_workflow(self):
        """Test the complete analysis workflow."""
        from modules.data_ingestion import load_all_csvs, get_peer_group
        from modules.scoring import calculate_deal_heat, get_heat_color, get_heat_label
        from modules.visualization import create_market_chart, calculate_valuation_range
        from modules.config import load_config

        # Load data
        df = load_all_csvs("data")
        assert not df.empty

        # Get config
        config = load_config()
        assert config is not None

        # Get industry and create peer group
        if 'industry' in df.columns:
            industry = df['industry'].iloc[0]
            revenue = 3000000
            peers = get_peer_group(df, industry, revenue)

            # Calculate deal heat
            peer_count = len(peers)
            median_margin = 15.0
            if peer_count > 0 and 'ebitda_margin' in peers.columns:
                mm = peers['ebitda_margin'].median()
                if pd.notna(mm):
                    median_margin = mm

            heat = calculate_deal_heat(revenue, peer_count, median_margin, config)
            color = get_heat_color(heat)
            label = get_heat_label(heat)

            assert 0 <= heat <= 100
            assert color.startswith("#")
            assert label in ["Low", "Medium", "High"]

            # Create chart
            fig = create_market_chart(peers, "Test Company", revenue, median_margin)
            assert fig is not None

            # Calculate valuation
            val_range = calculate_valuation_range(peers, revenue)
            assert len(val_range) == 3


class TestEmailGeneration:
    """Tests for email generation workflow (mocked API)."""

    def test_generate_emails_structure(self):
        """Test that generate_emails returns correct structure."""
        from modules.ai_service import generate_emails

        with patch('modules.ai_service._get_client') as mock_client:
            mock_client.return_value = None  # Trigger fallback
            emails = generate_emails(
                "Test Company",
                "HVAC",
                3000000,
                3.5,
                "Sample summary",
                "formal"
            )

            assert isinstance(emails, dict)
            assert 'hook' in emails
            assert 'asset' in emails
            assert 'close' in emails

            for key in ['hook', 'asset', 'close']:
                assert 'subject' in emails[key]
                assert 'body' in emails[key]


class TestPdfGeneration:
    """Tests for PDF generation workflow."""

    def test_generate_one_pager_returns_bytes(self):
        """Test that generate_one_pager returns bytes."""
        from modules.pdf_generator import generate_one_pager
        from modules.visualization import create_market_chart
        import pandas as pd

        # Create sample data
        peers_df = pd.DataFrame({
            'description': ['Test Comp 1', 'Test Comp 2', 'Test Comp 3'],
            'revenue': [2000000, 3000000, 4000000],
            'ebitda_margin': [15.0, 18.0, 20.0],
            'multiple': [3.0, 3.5, 4.0]
        })

        fig = create_market_chart(peers_df, "Test Company", 3000000, 17.0)
        upside_bullets = [
            "Potential margin improvement",
            "Scale benefits through platform",
            "Technology improvements"
        ]

        pdf_bytes = generate_one_pager(
            "Test Company",
            "HVAC",
            3000000,
            (6000000, 12000000, 9000000),
            peers_df,
            fig,
            upside_bullets
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Check PDF magic bytes
        assert pdf_bytes[:4] == b'%PDF'


class TestAutoArchive:
    """Tests for auto-archive functionality on startup."""

    def test_auto_archive_function_exists(self):
        """Test that auto_archive_old_entries function exists."""
        from modules.storage import auto_archive_old_entries
        assert callable(auto_archive_old_entries)

    def test_auto_archive_returns_int(self):
        """Test that auto_archive returns count of archived entries."""
        from modules.storage import auto_archive_old_entries
        result = auto_archive_old_entries(90)
        assert isinstance(result, int)
        assert result >= 0
