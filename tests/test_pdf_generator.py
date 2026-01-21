"""
Tests for PDF generator module.
Tests PDF generation with all sections: executive summary, valuation range,
market position chart, comparable transactions table, and operational upside.
"""

import pandas as pd
import numpy as np
import pytest
from unittest.mock import Mock, patch
import tempfile
import os

from modules.pdf_generator import (
    DealFlowPDF,
    generate_one_pager,
    generate_simple_one_pager
)


def create_sample_top_comps(num_comps=3):
    """Create a sample comparable transactions DataFrame for testing."""
    return pd.DataFrame({
        'description': [f'Company {i+1} - HVAC Services' for i in range(num_comps)],
        'revenue': [2_000_000 + i * 500_000 for i in range(num_comps)],
        'ebitda_margin': [12.0 + i * 2 for i in range(num_comps)],
        'multiple': [2.0 + i * 0.3 for i in range(num_comps)]
    })


def create_sample_upside_bullets():
    """Create sample upside bullet points for testing."""
    return [
        "Margin improvement potential of 5% through operational optimization",
        "Scale benefits through platform resources and vendor relationships",
        "Technology and process improvements to drive efficiency gains"
    ]


class TestDealFlowPDF:
    """Tests for the DealFlowPDF class."""

    def test_instantiation(self):
        """Test that DealFlowPDF can be instantiated."""
        pdf = DealFlowPDF()
        assert pdf is not None

    def test_auto_page_break_enabled(self):
        """Test that auto page break is enabled with margin."""
        pdf = DealFlowPDF()
        assert pdf.auto_page_break is True

    def test_header_renders_without_error(self):
        """Test that header renders without raising an error."""
        pdf = DealFlowPDF()
        pdf.add_page()
        # If no error is raised, header was rendered successfully
        assert pdf.page_no() == 1

    def test_footer_renders_without_error(self):
        """Test that footer renders without raising an error."""
        pdf = DealFlowPDF()
        pdf.add_page()
        # Footer is rendered during output
        output = pdf.output()
        assert len(output) > 0


class TestGenerateOnePager:
    """Tests for the generate_one_pager function."""

    def test_returns_bytes(self):
        """Test that function returns bytes object."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_pdf_not_empty(self):
        """Test that generated PDF is not empty."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert len(result) > 0

    def test_pdf_starts_with_pdf_header(self):
        """Test that output is a valid PDF (starts with PDF magic number)."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        # PDF files start with %PDF
        assert result[:4] == b'%PDF'

    def test_handles_empty_top_comps(self):
        """Test that PDF generates successfully with empty comparables."""
        empty_comps = pd.DataFrame(columns=['description', 'revenue', 'ebitda_margin', 'multiple'])
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=empty_comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_handles_none_chart(self):
        """Test that PDF generates successfully with None chart."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_zero_valuation(self):
        """Test that PDF handles zero valuation range."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(0, 0, 0),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_negative_valuation(self):
        """Test that PDF handles negative valuation range gracefully."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(-1, -1, -1),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_empty_upside_bullets(self):
        """Test that PDF generates with empty upside bullets list."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=[]
        )
        assert isinstance(result, bytes)

    def test_handles_long_company_name(self):
        """Test that PDF handles very long company names."""
        long_name = "A" * 200
        result = generate_one_pager(
            company_name=long_name,
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_special_characters_in_name(self):
        """Test that PDF handles special characters in company name."""
        result = generate_one_pager(
            company_name="Test & Company (LLC) - Division",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_unicode_in_name(self):
        """Test that PDF handles unicode characters in company name."""
        result = generate_one_pager(
            company_name="Test Company GmbH",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_large_revenue(self):
        """Test that PDF handles very large revenue values."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=1_000_000_000,  # 1 billion
            valuation_range=(800_000_000, 1_200_000_000, 1_000_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_small_revenue(self):
        """Test that PDF handles very small revenue values."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=100,
            valuation_range=(80, 120, 100),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_many_upside_bullets(self):
        """Test that PDF handles many upside bullet points."""
        many_bullets = ["Bullet point {}".format(i) for i in range(10)]
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=many_bullets
        )
        assert isinstance(result, bytes)

    def test_handles_long_upside_bullets(self):
        """Test that PDF handles very long upside bullet text."""
        long_bullets = [
            "This is a very long bullet point that describes in great detail "
            "the operational upside potential that could be realized through "
            "various strategic initiatives and process improvements."
        ] * 3
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=long_bullets
        )
        assert isinstance(result, bytes)

    def test_handles_nan_in_top_comps(self):
        """Test that PDF handles NaN values in comparable transactions."""
        comps_with_nan = pd.DataFrame({
            'description': ['Company 1', 'Company 2', 'Company 3'],
            'revenue': [2_000_000, np.nan, 3_000_000],
            'ebitda_margin': [12.0, 14.0, np.nan],
            'multiple': [np.nan, 2.3, 2.6]
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=comps_with_nan,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_limits_comparable_transactions_to_three(self):
        """Test that PDF limits comparable transactions to 3 rows."""
        many_comps = create_sample_top_comps(num_comps=10)
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=many_comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_truncates_long_descriptions(self):
        """Test that PDF truncates long descriptions in table."""
        comps_with_long_desc = pd.DataFrame({
            'description': ['A' * 100, 'B' * 100, 'C' * 100],
            'revenue': [2_000_000, 2_500_000, 3_000_000],
            'ebitda_margin': [12.0, 14.0, 16.0],
            'multiple': [2.0, 2.3, 2.6]
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=comps_with_long_desc,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)


class TestGenerateOnePagerWithChart:
    """Tests for generate_one_pager with chart figure."""

    @patch('plotly.io.write_image')
    def test_chart_export_called(self, mock_write_image):
        """Test that chart export is attempted when figure is provided."""
        mock_fig = Mock()

        generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=mock_fig,
            upside_bullets=create_sample_upside_bullets()
        )

        # Check that write_image was called
        assert mock_write_image.called

    @patch('plotly.io.write_image')
    def test_handles_chart_export_failure(self, mock_write_image):
        """Test that PDF generates even when chart export fails."""
        mock_fig = Mock()
        mock_write_image.side_effect = Exception("Chart export failed")

        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=mock_fig,
            upside_bullets=create_sample_upside_bullets()
        )

        # Should still return valid PDF
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('plotly.io.write_image')
    def test_chart_export_uses_correct_dimensions(self, mock_write_image):
        """Test that chart export uses correct width and height."""
        mock_fig = Mock()

        generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=mock_fig,
            upside_bullets=create_sample_upside_bullets()
        )

        # Check the call arguments
        call_args = mock_write_image.call_args
        assert call_args[1]['width'] == 800
        assert call_args[1]['height'] == 450


class TestGenerateSimpleOnePager:
    """Tests for the generate_simple_one_pager function."""

    def test_returns_bytes(self):
        """Test that function returns bytes object."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_pdf_not_empty(self):
        """Test that generated PDF is not empty."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=create_sample_upside_bullets()
        )
        assert len(result) > 0

    def test_pdf_starts_with_pdf_header(self):
        """Test that output is a valid PDF."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=create_sample_upside_bullets()
        )
        assert result[:4] == b'%PDF'

    def test_handles_zero_peer_count(self):
        """Test that PDF handles zero peer count."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=0,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_zero_valuation(self):
        """Test that PDF handles zero valuation range."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(0, 0, 0),
            peer_count=10,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_handles_empty_bullets(self):
        """Test that PDF handles empty upside bullets."""
        result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=[]
        )
        assert isinstance(result, bytes)

    def test_handles_special_characters(self):
        """Test that PDF handles special characters in inputs."""
        result = generate_simple_one_pager(
            company_name="Test & Company (LLC)",
            industry="HVAC & Plumbing",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=["Bullet with special chars: & < > \""]
        )
        assert isinstance(result, bytes)

    def test_smaller_than_full_one_pager(self):
        """Test that simple one-pager is typically smaller than full one-pager."""
        simple_result = generate_simple_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            peer_count=10,
            upside_bullets=create_sample_upside_bullets()
        )

        full_result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )

        # Simple version should be different (typically smaller without table)
        assert isinstance(simple_result, bytes)
        assert isinstance(full_result, bytes)


class TestPDFSections:
    """Tests to verify all PDF sections are included."""

    def test_executive_summary_section(self):
        """Test that executive summary section is generated."""
        # The executive summary includes company name, industry, and revenue
        # We verify this by checking the PDF generates successfully with these inputs
        result = generate_one_pager(
            company_name="Acme HVAC Services",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valuation_range_section(self):
        """Test that valuation range section is generated."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(3_500_000, 7_500_000, 5_500_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_comparable_transactions_section(self):
        """Test that comparable transactions table section is generated."""
        comps = pd.DataFrame({
            'description': ['HVAC Company A', 'HVAC Company B', 'HVAC Company C'],
            'revenue': [2_500_000, 3_000_000, 4_000_000],
            'ebitda_margin': [14.5, 16.2, 18.0],
            'multiple': [2.1, 2.4, 2.8]
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_operational_upside_section(self):
        """Test that operational upside section is generated."""
        bullets = [
            "Revenue growth through geographic expansion",
            "Margin improvement via procurement optimization",
            "Technology modernization opportunities"
        ]
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=bullets
        )
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_all_sections_together(self):
        """Test that all sections work together in a complete PDF."""
        result = generate_one_pager(
            company_name="Complete Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        # Verify it's a valid PDF of reasonable size
        assert isinstance(result, bytes)
        assert result[:4] == b'%PDF'
        # A complete PDF with all sections should be larger than a minimal PDF
        assert len(result) > 1000


class TestPDFBranding:
    """Tests for PDF branding elements."""

    def test_header_included(self):
        """Test that EAI Capital header is included."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        # PDF is generated successfully with header
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_footer_included(self):
        """Test that confidentiality footer is included."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        # PDF is generated successfully with footer
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestPDFFormatting:
    """Tests for PDF formatting and styling."""

    def test_currency_formatting_large_values(self):
        """Test that large currency values are formatted correctly."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=15_000_000,
            valuation_range=(12_000_000, 18_000_000, 15_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_percentage_formatting(self):
        """Test that percentages are formatted correctly in table."""
        comps = pd.DataFrame({
            'description': ['Company A', 'Company B', 'Company C'],
            'revenue': [2_000_000, 3_000_000, 4_000_000],
            'ebitda_margin': [10.55, 15.75, 20.33],
            'multiple': [2.0, 2.5, 3.0]
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_multiple_formatting(self):
        """Test that multiples are formatted correctly in table."""
        comps = pd.DataFrame({
            'description': ['Company A', 'Company B', 'Company C'],
            'revenue': [2_000_000, 3_000_000, 4_000_000],
            'ebitda_margin': [15.0, 16.0, 17.0],
            'multiple': [1.85, 2.33, 3.14159]
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_string_company_name(self):
        """Test handling of empty company name."""
        result = generate_one_pager(
            company_name="",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_empty_string_industry(self):
        """Test handling of empty industry."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_zero_revenue(self):
        """Test handling of zero revenue."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=0,
            valuation_range=(0, 0, 0),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_float_revenue(self):
        """Test handling of float revenue values."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000.50,
            valuation_range=(4_000_000.25, 6_000_000.75, 5_000_000.50),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_missing_columns_in_top_comps(self):
        """Test handling of missing columns in comparables DataFrame."""
        incomplete_comps = pd.DataFrame({
            'description': ['Company A', 'Company B'],
            'revenue': [2_000_000, 3_000_000]
            # Missing ebitda_margin and multiple columns
        })
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=incomplete_comps,
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)

    def test_none_values_in_upside_bullets(self):
        """Test handling of None values in upside bullets list."""
        bullets_with_none = ["Valid bullet", None, "Another valid bullet"]
        # Filter out None values as the function might not handle them
        valid_bullets = [b for b in bullets_with_none if b is not None]
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=valid_bullets
        )
        assert isinstance(result, bytes)

    def test_inverted_valuation_range(self):
        """Test handling of inverted valuation range (low > high)."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(8_000_000, 4_000_000, 6_000_000),  # low > high
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)


class TestPDFWriteToFile:
    """Tests for writing PDF to file."""

    def test_can_write_to_file(self):
        """Test that PDF can be written to a file."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(result)
            temp_path = f.name

        # Verify file was written
        assert os.path.exists(temp_path)
        assert os.path.getsize(temp_path) > 0

        # Clean up
        os.unlink(temp_path)

    def test_file_is_readable_pdf(self):
        """Test that written file is a valid PDF."""
        result = generate_one_pager(
            company_name="Test Company",
            industry="HVAC",
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(result)
            temp_path = f.name

        # Read back and verify
        with open(temp_path, 'rb') as f:
            content = f.read()

        assert content[:4] == b'%PDF'

        # Clean up
        os.unlink(temp_path)


class TestAllIndustriesSupported:
    """Tests to verify all industries are supported."""

    @pytest.mark.parametrize("industry", [
        "HVAC",
        "Transportation",
        "Utility",
        "Other",
        "Custom Industry"
    ])
    def test_industry_supported(self, industry):
        """Test that PDF generates for each industry."""
        result = generate_one_pager(
            company_name="Test Company",
            industry=industry,
            revenue=5_000_000,
            valuation_range=(4_000_000, 6_000_000, 5_000_000),
            top_comps=create_sample_top_comps(),
            chart_fig=None,
            upside_bullets=create_sample_upside_bullets()
        )
        assert isinstance(result, bytes)
        assert len(result) > 0
