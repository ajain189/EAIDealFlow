"""
Tests for clipboard module.
Tests text formatting and JavaScript escaping functionality.
"""

from modules.clipboard import (
    _escape_for_js,
    format_email_for_copy,
    format_valuation_for_copy,
    format_deal_summary_for_copy,
)


class TestEscapeForJs:
    """Tests for JavaScript escaping function."""

    def test_escape_plain_text(self):
        """Test that plain text passes through unchanged."""
        text = "Hello World"
        result = _escape_for_js(text)
        assert result == "Hello World"

    def test_escape_backslashes(self):
        """Test that backslashes are escaped."""
        text = "path\\to\\file"
        result = _escape_for_js(text)
        assert result == "path\\\\to\\\\file"

    def test_escape_backticks(self):
        """Test that backticks are escaped for template literals."""
        text = "Use `code` here"
        result = _escape_for_js(text)
        assert result == "Use \\`code\\` here"

    def test_escape_template_interpolation(self):
        """Test that ${} syntax is escaped."""
        text = "Value is ${value}"
        result = _escape_for_js(text)
        assert result == "Value is \\${value}"

    def test_escape_complex_text(self):
        """Test escaping text with multiple special characters."""
        text = "Path `C:\\Users\\${name}` is invalid"
        result = _escape_for_js(text)
        assert result == "Path \\`C:\\\\Users\\\\\\${name}\\` is invalid"

    def test_escape_empty_string(self):
        """Test that empty string returns empty string."""
        result = _escape_for_js("")
        assert result == ""

    def test_escape_multiline_text(self):
        """Test that newlines are preserved."""
        text = "Line 1\nLine 2\nLine 3"
        result = _escape_for_js(text)
        assert result == "Line 1\nLine 2\nLine 3"

    def test_escape_unicode(self):
        """Test that unicode characters are preserved."""
        text = "Hello 世界 🌍"
        result = _escape_for_js(text)
        assert result == "Hello 世界 🌍"


class TestFormatEmailForCopy:
    """Tests for email formatting function."""

    def test_format_basic_email(self):
        """Test formatting a basic email."""
        result = format_email_for_copy("Test Subject", "Test body content")
        assert result == "Subject: Test Subject\n\nTest body content"

    def test_format_empty_subject(self):
        """Test formatting email with empty subject."""
        result = format_email_for_copy("", "Body only")
        assert result == "Subject: \n\nBody only"

    def test_format_empty_body(self):
        """Test formatting email with empty body."""
        result = format_email_for_copy("Subject only", "")
        assert result == "Subject: Subject only\n\n"

    def test_format_multiline_body(self):
        """Test formatting email with multiline body."""
        body = "Line 1\nLine 2\nLine 3"
        result = format_email_for_copy("Multi-line", body)
        expected = "Subject: Multi-line\n\nLine 1\nLine 2\nLine 3"
        assert result == expected

    def test_format_email_with_special_chars(self):
        """Test formatting email with special characters."""
        result = format_email_for_copy(
            "Re: Deal for Bob's HVAC",
            "Dear Sir/Madam,\n\nThe valuation is $5M - $10M."
        )
        assert "Subject: Re: Deal for Bob's HVAC" in result
        assert "$5M - $10M" in result


class TestFormatValuationForCopy:
    """Tests for valuation formatting function."""

    def test_format_basic_valuation(self):
        """Test formatting a basic valuation range."""
        result = format_valuation_for_copy("Test Corp", 1000000, 1500000, 2000000)
        assert "Test Corp - Estimated Valuation Range" in result
        assert "Low (25th %ile): $1,000,000" in result
        assert "Median: $1,500,000" in result
        assert "High (75th %ile): $2,000,000" in result

    def test_format_large_valuation(self):
        """Test formatting large valuations."""
        result = format_valuation_for_copy(
            "Big Company",
            50000000,
            75000000,
            100000000
        )
        assert "$50,000,000" in result
        assert "$75,000,000" in result
        assert "$100,000,000" in result

    def test_format_small_valuation(self):
        """Test formatting small valuations."""
        result = format_valuation_for_copy("Small Biz", 100000, 150000, 200000)
        assert "$100,000" in result
        assert "$150,000" in result
        assert "$200,000" in result

    def test_format_valuation_with_decimals(self):
        """Test that decimal valuations are rounded."""
        result = format_valuation_for_copy(
            "Decimal Corp",
            1234567.89,
            2345678.12,
            3456789.56
        )
        # Should be formatted without decimal places
        assert "$1,234,568" in result
        assert "$2,345,678" in result
        assert "$3,456,790" in result

    def test_format_valuation_company_name_preserved(self):
        """Test that company name with special chars is preserved."""
        result = format_valuation_for_copy(
            "Bob's HVAC & Plumbing, Inc.",
            1000000,
            1500000,
            2000000
        )
        assert "Bob's HVAC & Plumbing, Inc." in result


class TestFormatDealSummaryForCopy:
    """Tests for deal summary formatting function."""

    def test_format_basic_summary(self):
        """Test formatting a basic deal summary."""
        result = format_deal_summary_for_copy(
            company_name="Test Company",
            industry="HVAC",
            revenue=5000000,
            heat_score=75,
            heat_label="Warm",
            peer_count=10
        )
        assert "Deal Summary: Test Company" in result
        assert "Industry: HVAC" in result
        assert "Revenue: $5,000,000" in result
        assert "Deal Heat: 75/100 (Warm)" in result
        assert "Comparable Deals: 10" in result

    def test_format_hot_deal(self):
        """Test formatting a hot deal."""
        result = format_deal_summary_for_copy(
            "Hot Corp", "Manufacturing", 10000000, 95, "Hot", 25
        )
        assert "Deal Heat: 95/100 (Hot)" in result
        assert "Comparable Deals: 25" in result

    def test_format_cold_deal(self):
        """Test formatting a cold deal."""
        result = format_deal_summary_for_copy(
            "Cold Inc", "Retail", 500000, 25, "Cold", 2
        )
        assert "Deal Heat: 25/100 (Cold)" in result
        assert "Comparable Deals: 2" in result

    def test_format_summary_zero_peers(self):
        """Test formatting summary with zero peers."""
        result = format_deal_summary_for_copy(
            "No Peers LLC", "Niche", 1000000, 50, "Medium", 0
        )
        assert "Comparable Deals: 0" in result

    def test_format_summary_large_revenue(self):
        """Test formatting summary with large revenue."""
        result = format_deal_summary_for_copy(
            "Big Corp", "Tech", 500000000, 90, "Hot", 50
        )
        assert "Revenue: $500,000,000" in result

    def test_format_summary_special_chars_in_name(self):
        """Test formatting with special characters in company name."""
        result = format_deal_summary_for_copy(
            "O'Brien's & Sons, LLC",
            "Services",
            2000000,
            60,
            "Warm",
            5
        )
        assert "Deal Summary: O'Brien's & Sons, LLC" in result


class TestIntegration:
    """Integration tests for clipboard formatting."""

    def test_email_can_be_escaped_for_js(self):
        """Test that formatted email can be safely escaped."""
        email = format_email_for_copy(
            "Re: Acquisition of Bob's HVAC",
            "Dear Team,\n\nThe valuation is ${value}.\n\nBest,\nAnalyst"
        )
        escaped = _escape_for_js(email)
        # Should not raise any errors
        assert len(escaped) > len(email)  # Should have escape chars
        assert "\\${value}" in escaped

    def test_valuation_can_be_escaped_for_js(self):
        """Test that formatted valuation can be safely escaped."""
        valuation = format_valuation_for_copy(
            "Test `Company`",
            1000000,
            1500000,
            2000000
        )
        escaped = _escape_for_js(valuation)
        assert "\\`Company\\`" in escaped

    def test_deal_summary_can_be_escaped_for_js(self):
        """Test that formatted deal summary can be safely escaped."""
        summary = format_deal_summary_for_copy(
            "Path\\Corp",
            "Industry",
            1000000,
            75,
            "Warm",
            5
        )
        escaped = _escape_for_js(summary)
        assert "Path\\\\Corp" in escaped
