"""
Tests for the full application flow with sample data.
Tests the complete user journey from data loading through PDF generation and storage.
"""

import os
import tempfile
from unittest.mock import patch

import pytest
import pandas as pd

from modules.data_ingestion import (
    load_all_csvs,
    get_peer_group,
    get_available_industries,
    get_industry_stats,
    detect_industry
)
from modules.scoring import (
    calculate_deal_heat,
    get_heat_color,
    get_heat_label,
    get_score_breakdown
)
from modules.visualization import (
    create_market_chart,
    calculate_valuation_range
)
from modules.ai_service import generate_emails, generate_upside_bullets
from modules.pdf_generator import generate_one_pager
from modules.storage import (
    save_entry,
    get_all_entries,
    get_entry_by_id,
    get_pdf_bytes,
    delete_entry,
    get_stats,
    reset_stats
)
from modules.config import load_config
from modules.clipboard import (
    format_email_for_copy,
    format_valuation_for_copy,
    format_deal_summary_for_copy
)


# ===== SAMPLE DATA =====

SAMPLE_COMPANIES = [
    {
        "name": "Midwest HVAC Services",
        "industry": "HVAC",
        "revenue": 3500000,
        "website": "https://midwesthvac.example.com",
        "target_margin": 15.0,
        "tone": "formal"
    },
    {
        "name": "Coastal Freight Solutions",
        "industry": "Transportation",
        "revenue": 8000000,
        "website": "https://coastalfreight.example.com",
        "target_margin": 12.0,
        "tone": "friendly"
    },
    {
        "name": "SunPower Utilities",
        "industry": "Utility",
        "revenue": 25000000,
        "website": "https://sunpower.example.com",
        "target_margin": 20.0,
        "tone": "direct"
    }
]


@pytest.fixture
def sample_hvac_company():
    """Return sample HVAC company data."""
    return SAMPLE_COMPANIES[0]


@pytest.fixture
def sample_transportation_company():
    """Return sample Transportation company data."""
    return SAMPLE_COMPANIES[1]


@pytest.fixture
def sample_utility_company():
    """Return sample Utility company data."""
    return SAMPLE_COMPANIES[2]


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
def loaded_data():
    """Load actual CSV data from data folder."""
    return load_all_csvs("data")


class TestFullFlowDataLoading:
    """Tests for the data loading phase of the full flow."""

    def test_load_all_industry_data(self, loaded_data):
        """Test that all industry CSV files are loaded successfully."""
        assert not loaded_data.empty
        assert 'revenue' in loaded_data.columns
        assert 'industry' in loaded_data.columns
        assert 'source_file' in loaded_data.columns

        # Verify all three industries are present
        source_files = loaded_data['source_file'].unique()
        assert 'HVAC' in source_files
        assert 'Transportation' in source_files
        assert 'Utility' in source_files

    def test_data_has_required_columns_for_analysis(self, loaded_data):
        """Test that loaded data has all columns required for analysis."""
        required_columns = ['revenue', 'industry', 'ebitda_margin', 'multiple']
        for col in required_columns:
            assert col in loaded_data.columns, f"Missing column: {col}"

    def test_numeric_data_is_valid(self, loaded_data):
        """Test that numeric columns contain valid data."""
        # Revenue should be positive
        valid_revenue = loaded_data['revenue'].dropna()
        assert len(valid_revenue) > 0
        assert (valid_revenue > 0).all()

        # Multiples should be positive
        valid_multiples = loaded_data['multiple'].dropna()
        if len(valid_multiples) > 0:
            assert (valid_multiples > 0).all()

    def test_get_available_industries_includes_all(self, loaded_data):
        """Test that get_available_industries returns all detected industries."""
        industries = get_available_industries(loaded_data)
        assert 'HVAC' in industries
        assert 'Transportation' in industries
        assert 'Utility' in industries


class TestFullFlowPeerFiltering:
    """Tests for the peer filtering phase of the full flow."""

    def test_peer_group_for_hvac_company(
        self, loaded_data, sample_hvac_company
    ):
        """Test peer group filtering for HVAC company."""
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        assert isinstance(peers, pd.DataFrame)
        if not peers.empty:
            assert all(peers['industry'] == 'HVAC')
            # Revenue should be within ±50% of target
            min_rev = sample_hvac_company['revenue'] * 0.5
            max_rev = sample_hvac_company['revenue'] * 1.5
            valid_rev = peers['revenue'].dropna()
            assert (valid_rev >= min_rev).all()
            assert (valid_rev <= max_rev).all()

    def test_peer_group_for_transportation_company(
        self, loaded_data, sample_transportation_company
    ):
        """Test peer group filtering for Transportation company."""
        peers = get_peer_group(
            loaded_data,
            sample_transportation_company['industry'],
            sample_transportation_company['revenue']
        )

        assert isinstance(peers, pd.DataFrame)
        if not peers.empty:
            assert all(peers['industry'] == 'Transportation')

    def test_peer_group_for_utility_company(
        self, loaded_data, sample_utility_company
    ):
        """Test peer group filtering for Utility company."""
        peers = get_peer_group(
            loaded_data,
            sample_utility_company['industry'],
            sample_utility_company['revenue']
        )

        assert isinstance(peers, pd.DataFrame)
        if not peers.empty:
            assert all(peers['industry'] == 'Utility')

    def test_industry_stats_calculation(self, loaded_data):
        """Test industry statistics are calculated correctly."""
        for industry in ['HVAC', 'Transportation', 'Utility']:
            stats = get_industry_stats(loaded_data, industry)

            assert 'count' in stats
            assert 'median_revenue' in stats
            assert 'median_margin' in stats
            assert 'median_multiple' in stats

            assert stats['count'] > 0


class TestFullFlowDealHeatScoring:
    """Tests for the Deal Heat scoring phase of the full flow."""

    def test_deal_heat_calculation_with_sample_data(
        self, loaded_data, sample_hvac_company
    ):
        """Test Deal Heat calculation using actual peer data."""
        config = load_config()
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        peer_count = len(peers)
        median_margin = None
        if peer_count > 0 and 'ebitda_margin' in peers.columns:
            mm = peers['ebitda_margin'].median()
            if pd.notna(mm):
                median_margin = mm

        heat = calculate_deal_heat(
            sample_hvac_company['revenue'],
            peer_count,
            median_margin,
            config
        )

        assert isinstance(heat, int)
        assert 0 <= heat <= 100

    def test_deal_heat_color_and_label(self, loaded_data, sample_hvac_company):
        """Test Deal Heat color and label generation."""
        config = load_config()
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        heat = calculate_deal_heat(
            sample_hvac_company['revenue'],
            len(peers),
            15.0,
            config
        )

        color = get_heat_color(heat)
        label = get_heat_label(heat)

        assert color.startswith('#')
        assert len(color) == 7
        assert label in ['Low', 'Medium', 'High']

    def test_score_breakdown_details(self, loaded_data, sample_hvac_company):
        """Test Deal Heat score breakdown provides details."""
        config = load_config()
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        breakdown = get_score_breakdown(
            sample_hvac_company['revenue'],
            len(peers),
            15.0,
            config
        )

        assert 'base' in breakdown
        assert 'revenue_bonus' in breakdown
        assert 'peer_bonus' in breakdown
        assert 'margin_bonus' in breakdown
        assert 'total' in breakdown
        assert 'details' in breakdown
        assert 'weights' in breakdown

    def test_deal_heat_for_all_sample_companies(self, loaded_data):
        """Test Deal Heat calculation for all sample companies."""
        config = load_config()

        for company in SAMPLE_COMPANIES:
            peers = get_peer_group(
                loaded_data,
                company['industry'],
                company['revenue']
            )

            median_margin = None
            if len(peers) > 0 and 'ebitda_margin' in peers.columns:
                mm = peers['ebitda_margin'].median()
                if pd.notna(mm):
                    median_margin = mm

            heat = calculate_deal_heat(
                company['revenue'],
                len(peers),
                median_margin,
                config
            )

            assert 0 <= heat <= 100, f"Invalid heat for {company['name']}"


class TestFullFlowVisualization:
    """Tests for the visualization phase of the full flow."""

    def test_create_market_chart_with_sample_data(
        self, loaded_data, sample_hvac_company
    ):
        """Test market chart creation with actual data."""
        import plotly.graph_objects as go

        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        fig = create_market_chart(
            peers,
            sample_hvac_company['name'],
            sample_hvac_company['revenue'],
            sample_hvac_company['target_margin']
        )

        assert isinstance(fig, go.Figure)

    def test_valuation_range_calculation(
        self, loaded_data, sample_hvac_company
    ):
        """Test valuation range calculation with actual data."""
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        if not peers.empty and 'multiple' in peers.columns:
            val_range = calculate_valuation_range(
                peers,
                sample_hvac_company['revenue']
            )

            assert isinstance(val_range, tuple)
            assert len(val_range) == 3
            low, high, median = val_range

            # Median should be between low and high
            if low > 0 and high > 0:
                assert low <= median <= high

    def test_valuation_range_for_all_industries(self, loaded_data):
        """Test valuation calculation works for all industries."""
        for company in SAMPLE_COMPANIES:
            peers = get_peer_group(
                loaded_data,
                company['industry'],
                company['revenue']
            )

            if not peers.empty and 'multiple' in peers.columns:
                val_range = calculate_valuation_range(peers, company['revenue'])
                assert len(val_range) == 3


class TestFullFlowEmailGeneration:
    """Tests for the email generation phase of the full flow."""

    def test_generate_emails_structure(self, sample_hvac_company):
        """Test email generation returns correct structure."""
        with patch('modules.ai_service._get_client') as mock_client:
            mock_client.return_value = None  # Trigger fallback templates

            emails = generate_emails(
                sample_hvac_company['name'],
                sample_hvac_company['industry'],
                sample_hvac_company['revenue'],
                3.5,  # median multiple
                "Company provides HVAC services",
                sample_hvac_company['tone']
            )

            assert isinstance(emails, dict)
            assert 'hook' in emails
            assert 'asset' in emails
            assert 'close' in emails

            for email_type in ['hook', 'asset', 'close']:
                assert 'subject' in emails[email_type]
                assert 'body' in emails[email_type]
                assert len(emails[email_type]['subject']) > 0
                assert len(emails[email_type]['body']) > 0

    def test_generate_emails_for_different_tones(self, sample_hvac_company):
        """Test email generation with different tones."""
        with patch('modules.ai_service._get_client') as mock_client:
            mock_client.return_value = None

            for tone in ['formal', 'friendly', 'direct']:
                emails = generate_emails(
                    sample_hvac_company['name'],
                    sample_hvac_company['industry'],
                    sample_hvac_company['revenue'],
                    3.5,
                    "HVAC services provider",
                    tone
                )

                assert emails is not None
                assert 'hook' in emails

    def test_generate_upside_bullets_structure(self, loaded_data):
        """Test upside bullets generation returns correct structure."""
        with patch('modules.ai_service._get_client') as mock_client:
            mock_client.return_value = None  # Trigger fallback

            peers = get_peer_group(loaded_data, 'HVAC', 3500000)
            peer_median_margin = 18.0
            if not peers.empty and 'ebitda_margin' in peers.columns:
                pm = peers['ebitda_margin'].median()
                if pd.notna(pm):
                    peer_median_margin = pm

            bullets = generate_upside_bullets(
                "Test Company",
                "HVAC",
                15.0,  # target margin
                peer_median_margin,
                "HVAC services provider"  # website summary
            )

            assert isinstance(bullets, list)
            assert len(bullets) >= 1


class TestFullFlowPdfGeneration:
    """Tests for the PDF generation phase of the full flow."""

    def test_generate_pdf_with_sample_data(
        self, loaded_data, sample_hvac_company
    ):
        """Test PDF generation with actual sample data."""
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        fig = create_market_chart(
            peers,
            sample_hvac_company['name'],
            sample_hvac_company['revenue'],
            sample_hvac_company['target_margin']
        )

        val_range = (8000000, 15000000, 11000000)
        upside_bullets = [
            "Margin improvement opportunity vs. peer median",
            "Scale benefits through platform integration",
            "Technology upgrades to improve efficiency"
        ]

        pdf_bytes = generate_one_pager(
            sample_hvac_company['name'],
            sample_hvac_company['industry'],
            sample_hvac_company['revenue'],
            val_range,
            peers,
            fig,
            upside_bullets
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Check PDF magic bytes
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_pdf_for_all_industries(self, loaded_data):
        """Test PDF generation works for all industries."""
        for company in SAMPLE_COMPANIES:
            peers = get_peer_group(
                loaded_data,
                company['industry'],
                company['revenue']
            )

            fig = create_market_chart(
                peers,
                company['name'],
                company['revenue'],
                company['target_margin']
            )

            val_range = (5000000, 20000000, 12000000)
            upside_bullets = ["Improvement opportunity 1", "Opportunity 2"]

            pdf_bytes = generate_one_pager(
                company['name'],
                company['industry'],
                company['revenue'],
                val_range,
                peers,
                fig,
                upside_bullets
            )

            assert pdf_bytes[:4] == b'%PDF', f"Invalid PDF for {company['name']}"


class TestFullFlowStorage:
    """Tests for the storage phase of the full flow."""

    def test_save_and_retrieve_entry(
        self, mock_storage_env, loaded_data, sample_hvac_company
    ):
        """Test saving and retrieving a complete entry."""
        reset_stats()

        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        fig = create_market_chart(
            peers,
            sample_hvac_company['name'],
            sample_hvac_company['revenue'],
            sample_hvac_company['target_margin']
        )

        val_range = (8000000, 15000000, 11000000)
        upside_bullets = ["Opportunity 1", "Opportunity 2"]

        pdf_bytes = generate_one_pager(
            sample_hvac_company['name'],
            sample_hvac_company['industry'],
            sample_hvac_company['revenue'],
            val_range,
            peers,
            fig,
            upside_bullets
        )

        emails = {
            'hook': {'subject': 'Hook Subject', 'body': 'Hook body'},
            'asset': {'subject': 'Asset Subject', 'body': 'Asset body'},
            'close': {'subject': 'Close Subject', 'body': 'Close body'}
        }

        entry_id = save_entry(
            company_name=sample_hvac_company['name'],
            industry=sample_hvac_company['industry'],
            revenue=sample_hvac_company['revenue'],
            website=sample_hvac_company['website'],
            deal_heat=85,
            valuation_range=val_range,
            emails=emails,
            pdf_bytes=pdf_bytes
        )

        assert isinstance(entry_id, str)
        assert len(entry_id) == 12

        # Retrieve and verify
        entry = get_entry_by_id(entry_id)
        assert entry is not None
        assert entry['company_name'] == sample_hvac_company['name']
        assert entry['industry'] == sample_hvac_company['industry']
        assert entry['revenue'] == sample_hvac_company['revenue']
        assert entry['deal_heat'] == 85
        assert entry['valuation_low'] == 8000000
        assert entry['valuation_high'] == 15000000
        assert entry['valuation_median'] == 11000000

        # Verify PDF retrieval
        retrieved_pdf = get_pdf_bytes(entry_id)
        assert retrieved_pdf == pdf_bytes

        # Verify stats incremented
        stats = get_stats()
        assert stats['reports_generated'] == 1

    def test_save_multiple_entries_ordered(
        self, mock_storage_env, loaded_data
    ):
        """Test that multiple entries are saved in correct order."""
        reset_stats()

        for company in SAMPLE_COMPANIES:
            peers = get_peer_group(
                loaded_data,
                company['industry'],
                company['revenue']
            )

            fig = create_market_chart(
                peers,
                company['name'],
                company['revenue'],
                company['target_margin']
            )

            pdf_bytes = generate_one_pager(
                company['name'],
                company['industry'],
                company['revenue'],
                (5000000, 15000000, 10000000),
                peers,
                fig,
                ["Bullet 1"]
            )

            save_entry(
                company_name=company['name'],
                industry=company['industry'],
                revenue=company['revenue'],
                website=company['website'],
                deal_heat=75,
                valuation_range=(5000000, 15000000, 10000000),
                emails={'hook': {'subject': 'S', 'body': 'B'},
                        'asset': {'subject': 'S', 'body': 'B'},
                        'close': {'subject': 'S', 'body': 'B'}},
                pdf_bytes=pdf_bytes
            )

        entries = get_all_entries()
        assert len(entries) == 3

        # Most recent should be first
        assert entries[0]['company_name'] == SAMPLE_COMPANIES[2]['name']

        # Verify stats
        stats = get_stats()
        assert stats['reports_generated'] == 3

    def test_delete_entry_from_history(
        self, mock_storage_env, loaded_data, sample_hvac_company
    ):
        """Test deleting an entry from history."""
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )

        fig = create_market_chart(
            peers,
            sample_hvac_company['name'],
            sample_hvac_company['revenue'],
            sample_hvac_company['target_margin']
        )

        pdf_bytes = generate_one_pager(
            sample_hvac_company['name'],
            sample_hvac_company['industry'],
            sample_hvac_company['revenue'],
            (5000000, 15000000, 10000000),
            peers,
            fig,
            ["Bullet 1"]
        )

        entry_id = save_entry(
            company_name=sample_hvac_company['name'],
            industry=sample_hvac_company['industry'],
            revenue=sample_hvac_company['revenue'],
            website=sample_hvac_company['website'],
            deal_heat=75,
            valuation_range=(5000000, 15000000, 10000000),
            emails={'hook': {'subject': 'S', 'body': 'B'},
                    'asset': {'subject': 'S', 'body': 'B'},
                    'close': {'subject': 'S', 'body': 'B'}},
            pdf_bytes=pdf_bytes
        )

        assert get_entry_by_id(entry_id) is not None

        result = delete_entry(entry_id)
        assert result is True
        assert get_entry_by_id(entry_id) is None


class TestFullFlowClipboard:
    """Tests for clipboard formatting in the full flow."""

    def test_format_email_for_clipboard(self, sample_hvac_company):
        """Test email formatting for clipboard."""
        result = format_email_for_copy(
            "Partnership Opportunity",
            f"Dear {sample_hvac_company['name']} team,\n\nWe are interested..."
        )

        assert "Subject: Partnership Opportunity" in result
        assert sample_hvac_company['name'] in result

    def test_format_valuation_for_clipboard(self, sample_hvac_company):
        """Test valuation formatting for clipboard."""
        result = format_valuation_for_copy(
            sample_hvac_company['name'],
            8000000,
            15000000,
            11000000
        )

        assert sample_hvac_company['name'] in result
        assert "$" in result

    def test_format_deal_summary_for_clipboard(self, sample_hvac_company):
        """Test deal summary formatting for clipboard."""
        result = format_deal_summary_for_copy(
            sample_hvac_company['name'],
            sample_hvac_company['industry'],
            sample_hvac_company['revenue'],
            85,
            "High",
            10
        )

        assert sample_hvac_company['name'] in result
        assert sample_hvac_company['industry'] in result
        assert "85" in result


class TestFullFlowEndToEnd:
    """End-to-end tests for the complete application flow."""

    def test_complete_flow_hvac_company(
        self, mock_storage_env, loaded_data, sample_hvac_company
    ):
        """Test complete flow for HVAC company from start to finish."""
        reset_stats()
        config = load_config()

        # Step 1: Data loading (already done via fixture)
        assert not loaded_data.empty

        # Step 2: Peer group filtering
        peers = get_peer_group(
            loaded_data,
            sample_hvac_company['industry'],
            sample_hvac_company['revenue']
        )
        peer_count = len(peers)

        # Step 3: Deal Heat calculation
        median_margin = None
        if peer_count > 0 and 'ebitda_margin' in peers.columns:
            mm = peers['ebitda_margin'].median()
            if pd.notna(mm):
                median_margin = mm

        deal_heat = calculate_deal_heat(
            sample_hvac_company['revenue'],
            peer_count,
            median_margin,
            config
        )
        heat_color = get_heat_color(deal_heat)
        heat_label = get_heat_label(deal_heat)

        assert 0 <= deal_heat <= 100
        assert heat_color.startswith('#')
        assert heat_label in ['Low', 'Medium', 'High']

        # Step 4: Visualization
        fig = create_market_chart(
            peers,
            sample_hvac_company['name'],
            sample_hvac_company['revenue'],
            sample_hvac_company['target_margin']
        )
        assert fig is not None

        val_range = calculate_valuation_range(
            peers,
            sample_hvac_company['revenue']
        )
        assert len(val_range) == 3

        # Step 5: Email generation (mocked)
        with patch('modules.ai_service._get_client') as mock_client:
            mock_client.return_value = None
            emails = generate_emails(
                sample_hvac_company['name'],
                sample_hvac_company['industry'],
                sample_hvac_company['revenue'],
                3.5,
                "HVAC services provider",
                sample_hvac_company['tone']
            )

        assert 'hook' in emails
        assert 'asset' in emails
        assert 'close' in emails

        # Step 6: PDF generation
        upside_bullets = [
            "Margin improvement vs peer median",
            "Scale benefits through platform"
        ]
        pdf_bytes = generate_one_pager(
            sample_hvac_company['name'],
            sample_hvac_company['industry'],
            sample_hvac_company['revenue'],
            val_range,
            peers,
            fig,
            upside_bullets
        )
        assert pdf_bytes[:4] == b'%PDF'

        # Step 7: Save to storage
        entry_id = save_entry(
            company_name=sample_hvac_company['name'],
            industry=sample_hvac_company['industry'],
            revenue=sample_hvac_company['revenue'],
            website=sample_hvac_company['website'],
            deal_heat=deal_heat,
            valuation_range=val_range,
            emails=emails,
            pdf_bytes=pdf_bytes
        )

        # Step 8: Verify saved entry
        entry = get_entry_by_id(entry_id)
        assert entry is not None
        assert entry['company_name'] == sample_hvac_company['name']
        assert entry['deal_heat'] == deal_heat

        # Step 9: Verify PDF retrieval
        retrieved_pdf = get_pdf_bytes(entry_id)
        assert retrieved_pdf == pdf_bytes

        # Step 10: Verify stats updated
        stats = get_stats()
        assert stats['reports_generated'] == 1

    def test_complete_flow_all_industries(self, mock_storage_env, loaded_data):
        """Test complete flow for all sample companies."""
        reset_stats()
        config = load_config()

        for company in SAMPLE_COMPANIES:
            # Peer filtering
            peers = get_peer_group(
                loaded_data,
                company['industry'],
                company['revenue']
            )

            # Deal Heat
            median_margin = None
            if len(peers) > 0 and 'ebitda_margin' in peers.columns:
                mm = peers['ebitda_margin'].median()
                if pd.notna(mm):
                    median_margin = mm

            deal_heat = calculate_deal_heat(
                company['revenue'],
                len(peers),
                median_margin,
                config
            )

            # Visualization
            fig = create_market_chart(
                peers,
                company['name'],
                company['revenue'],
                company['target_margin']
            )
            val_range = calculate_valuation_range(peers, company['revenue'])

            # PDF
            pdf_bytes = generate_one_pager(
                company['name'],
                company['industry'],
                company['revenue'],
                val_range,
                peers,
                fig,
                ["Improvement opportunity"]
            )

            # Save
            with patch('modules.ai_service._get_client') as mock_client:
                mock_client.return_value = None
                emails = generate_emails(
                    company['name'],
                    company['industry'],
                    company['revenue'],
                    3.5,
                    "Company summary",
                    company['tone']
                )

            entry_id = save_entry(
                company_name=company['name'],
                industry=company['industry'],
                revenue=company['revenue'],
                website=company['website'],
                deal_heat=deal_heat,
                valuation_range=val_range,
                emails=emails,
                pdf_bytes=pdf_bytes
            )

            assert entry_id is not None

        # Verify all entries saved
        entries = get_all_entries()
        assert len(entries) == 3

        # Verify stats
        stats = get_stats()
        assert stats['reports_generated'] == 3

    def test_flow_with_edge_case_revenue(self, mock_storage_env, loaded_data):
        """Test flow with edge case revenue values."""
        config = load_config()

        edge_revenues = [
            500000,     # Very small
            2000000,    # At lower sweet spot
            10000000,   # At upper sweet spot
            50000000    # Very large
        ]

        for revenue in edge_revenues:
            peers = get_peer_group(loaded_data, 'HVAC', revenue)

            deal_heat = calculate_deal_heat(
                revenue,
                len(peers),
                15.0,
                config
            )

            assert 0 <= deal_heat <= 100

    def test_flow_with_empty_peer_group(self, mock_storage_env):
        """Test flow handles empty peer group gracefully."""
        config = load_config()

        # Use revenue that won't match any peers
        peers = pd.DataFrame()

        deal_heat = calculate_deal_heat(
            1000000,
            0,
            None,
            config
        )

        assert deal_heat == 50  # Base score only

        # Visualization should still work
        fig = create_market_chart(
            peers,
            "Test Company",
            1000000,
            15.0
        )
        assert fig is not None

        # Valuation range should return zeros
        val_range = calculate_valuation_range(peers, 1000000)
        assert len(val_range) == 3


class TestFullFlowIndustryDetection:
    """Tests for industry detection in full flow."""

    def test_detect_industry_from_descriptions(self, loaded_data):
        """Test that industries are correctly detected from descriptions."""
        # HVAC descriptions
        assert detect_industry("HVAC Company") == "HVAC"
        assert detect_industry("Air Conditioning Services") == "HVAC"
        assert detect_industry("Heating and Cooling") == "HVAC"

        # Transportation descriptions
        assert detect_industry("Trucking Company") == "Transportation"
        assert detect_industry("Freight Services") == "Transportation"
        assert detect_industry("Logistics Provider") == "Transportation"

        # Utility descriptions
        assert detect_industry("Solar Power") == "Utility"
        assert detect_industry("Water Treatment") == "Utility"
        assert detect_industry("Natural Gas Distribution") == "Utility"

    def test_industry_detection_in_loaded_data(self, loaded_data):
        """Test that loaded data has correct industry assignments."""
        hvac_data = loaded_data[loaded_data['source_file'] == 'HVAC']
        assert (hvac_data['industry'] == 'HVAC').sum() > 0

        trans_data = loaded_data[loaded_data['source_file'] == 'Transportation']
        assert (trans_data['industry'] == 'Transportation').sum() > 0

        utility_data = loaded_data[loaded_data['source_file'] == 'Utility']
        assert (utility_data['industry'] == 'Utility').sum() > 0
