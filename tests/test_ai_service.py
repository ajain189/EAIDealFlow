"""
Tests for ai_service module.
Tests email generation with 3 tones (formal, friendly, direct) and supporting functions.
"""

from unittest.mock import patch, MagicMock
from modules.ai_service import (
    TONE_TEMPLATES,
    _parse_email,
    _generate_hook_email,
    _generate_asset_email,
    _generate_close_email,
    generate_emails,
    generate_upside_bullets,
    scrape_website_summary,
    check_api_status
)


class TestToneTemplates:
    """Tests for TONE_TEMPLATES configuration."""

    def test_all_tones_exist(self):
        """Test that all 3 tones are defined."""
        assert 'formal' in TONE_TEMPLATES
        assert 'friendly' in TONE_TEMPLATES
        assert 'direct' in TONE_TEMPLATES

    def test_formal_tone_structure(self):
        """Test formal tone has required fields."""
        tone = TONE_TEMPLATES['formal']
        assert 'style' in tone
        assert 'greeting' in tone
        assert 'sign_off' in tone
        assert 'characteristics' in tone

    def test_friendly_tone_structure(self):
        """Test friendly tone has required fields."""
        tone = TONE_TEMPLATES['friendly']
        assert 'style' in tone
        assert 'greeting' in tone
        assert 'sign_off' in tone
        assert 'characteristics' in tone

    def test_direct_tone_structure(self):
        """Test direct tone has required fields."""
        tone = TONE_TEMPLATES['direct']
        assert 'style' in tone
        assert 'greeting' in tone
        assert 'sign_off' in tone
        assert 'characteristics' in tone

    def test_formal_greeting(self):
        """Test formal tone uses 'Dear' greeting."""
        assert TONE_TEMPLATES['formal']['greeting'] == 'Dear'

    def test_friendly_greeting(self):
        """Test friendly tone uses 'Hi' greeting."""
        assert TONE_TEMPLATES['friendly']['greeting'] == 'Hi'

    def test_direct_greeting(self):
        """Test direct tone uses 'Hello' greeting."""
        assert TONE_TEMPLATES['direct']['greeting'] == 'Hello'

    def test_formal_sign_off(self):
        """Test formal tone uses 'Best regards' sign-off."""
        assert TONE_TEMPLATES['formal']['sign_off'] == 'Best regards'

    def test_friendly_sign_off(self):
        """Test friendly tone uses 'Best' sign-off."""
        assert TONE_TEMPLATES['friendly']['sign_off'] == 'Best'

    def test_direct_sign_off(self):
        """Test direct tone uses 'Regards' sign-off."""
        assert TONE_TEMPLATES['direct']['sign_off'] == 'Regards'

    def test_formal_style_is_professional(self):
        """Test formal style describes professional characteristics."""
        style = TONE_TEMPLATES['formal']['style']
        assert 'formal' in style.lower()
        assert 'professional' in style.lower()

    def test_friendly_style_is_warm(self):
        """Test friendly style describes warm characteristics."""
        style = TONE_TEMPLATES['friendly']['style']
        assert 'warm' in style.lower() or 'personable' in style.lower()

    def test_direct_style_is_concise(self):
        """Test direct style describes concise characteristics."""
        style = TONE_TEMPLATES['direct']['style']
        assert 'concise' in style.lower() or 'straightforward' in style.lower()


class TestParseEmail:
    """Tests for _parse_email function."""

    def test_parse_valid_email(self):
        """Test parsing well-formatted email response."""
        raw = """SUBJECT: Test Subject Line
BODY:
Hello,

This is the email body.

Best regards,
Sender"""
        result = _parse_email(raw)
        assert result['subject'] == 'Test Subject Line'
        assert 'Hello' in result['body']
        assert 'email body' in result['body']

    def test_parse_subject_only(self):
        """Test parsing with subject but no body marker."""
        raw = """SUBJECT: Just a Subject
Some content without body marker"""
        result = _parse_email(raw)
        assert result['subject'] == 'Just a Subject'
        # Body should be empty since no BODY: marker
        assert result['body'] == '' or 'Some content' in result['body']

    def test_parse_body_only(self):
        """Test parsing with body but no subject."""
        raw = """BODY:
Just the body content here."""
        result = _parse_email(raw)
        assert result['subject'] == 'Follow-up from EAI Capital'
        assert 'body content' in result['body']

    def test_parse_empty_string(self):
        """Test parsing empty string returns fallback."""
        raw = ""
        result = _parse_email(raw)
        assert result['subject'] == 'Follow-up from EAI Capital'
        assert result['body'] == ''

    def test_parse_no_markers(self):
        """Test parsing raw text without markers returns it as body."""
        raw = "This is raw text with no SUBJECT or BODY markers at all."
        result = _parse_email(raw)
        assert result['subject'] == 'Follow-up from EAI Capital'
        assert raw.strip() in result['body']

    def test_parse_multiline_body(self):
        """Test parsing multiline body content."""
        raw = """SUBJECT: Multi-line Test
BODY:
Line 1
Line 2
Line 3

Best,
Name"""
        result = _parse_email(raw)
        assert result['subject'] == 'Multi-line Test'
        assert 'Line 1' in result['body']
        assert 'Line 2' in result['body']
        assert 'Line 3' in result['body']

    def test_parse_case_insensitive_markers(self):
        """Test parsing handles case variations in markers."""
        raw = """subject: Lower Case Subject
body:
Lower case body content."""
        result = _parse_email(raw)
        assert result['subject'] == 'Lower Case Subject'
        assert 'Lower case body' in result['body']

    def test_parse_with_whitespace(self):
        """Test parsing handles extra whitespace."""
        raw = """   SUBJECT:   Spaced Subject
   BODY:
   Spaced body content   """
        result = _parse_email(raw)
        assert 'Spaced Subject' in result['subject']
        assert 'Spaced body' in result['body']

    def test_parse_colon_in_subject(self):
        """Test parsing handles colon in subject line."""
        raw = """SUBJECT: Re: Your inquiry about Company: Details
BODY:
Body here."""
        result = _parse_email(raw)
        assert 'Re: Your inquiry' in result['subject']

    def test_parse_returns_dict(self):
        """Test that parse always returns dict with subject and body keys."""
        raw = "Any content"
        result = _parse_email(raw)
        assert isinstance(result, dict)
        assert 'subject' in result
        assert 'body' in result


class TestGenerateHookEmail:
    """Tests for _generate_hook_email function."""

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_with_api_success(self, mock_retry):
        """Test hook email generation with successful API call."""
        mock_retry.return_value = """SUBJECT: Introduction regarding Test Company
BODY:
Dear Owner,

We have analyzed your business. Looking forward to connecting.

Best regards,
Advisor"""
        result = _generate_hook_email(
            company='Test Company',
            industry='HVAC',
            revenue=5000000,
            multiple=4.5,
            tone='formal',
            summary='HVAC services provider'
        )
        assert 'subject' in result
        assert 'body' in result
        assert result['subject'] != ''

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_fallback_on_api_failure(self, mock_retry):
        """Test hook email returns fallback when API fails."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='Test Company',
            industry='HVAC',
            revenue=5000000,
            multiple=4.5,
            tone='formal',
            summary=''
        )
        assert 'subject' in result
        assert 'body' in result
        assert 'EAI Capital' in result['subject']
        assert 'Test Company' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_formal_tone_fallback(self, mock_retry):
        """Test hook email fallback uses formal greeting."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='ACME Corp',
            industry='Transportation',
            revenue=3000000,
            multiple=3.5,
            tone='formal',
            summary=''
        )
        assert 'Dear' in result['body']
        assert 'Best regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_friendly_tone_fallback(self, mock_retry):
        """Test hook email fallback uses friendly greeting."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='ACME Corp',
            industry='Transportation',
            revenue=3000000,
            multiple=3.5,
            tone='friendly',
            summary=''
        )
        assert 'Hi' in result['body']
        assert 'Best' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_direct_tone_fallback(self, mock_retry):
        """Test hook email fallback uses direct greeting."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='ACME Corp',
            industry='Transportation',
            revenue=3000000,
            multiple=3.5,
            tone='direct',
            summary=''
        )
        assert 'Hello' in result['body']
        assert 'Regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_includes_company_in_fallback(self, mock_retry):
        """Test hook email fallback includes company name."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='Specific Company Name',
            industry='Utility',
            revenue=7000000,
            multiple=5.0,
            tone='formal',
            summary=''
        )
        assert 'Specific Company Name' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_includes_industry_in_fallback(self, mock_retry):
        """Test hook email fallback includes industry."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='Test Co',
            industry='HVAC',
            revenue=4000000,
            multiple=4.0,
            tone='formal',
            summary=''
        )
        assert 'HVAC' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_invalid_tone_defaults_to_formal(self, mock_retry):
        """Test hook email defaults to formal for invalid tone."""
        mock_retry.return_value = None
        result = _generate_hook_email(
            company='Test Co',
            industry='HVAC',
            revenue=4000000,
            multiple=4.0,
            tone='invalid_tone',
            summary=''
        )
        assert 'Dear' in result['body']


class TestGenerateAssetEmail:
    """Tests for _generate_asset_email function."""

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_with_api_success(self, mock_retry):
        """Test asset email generation with successful API call."""
        mock_retry.return_value = """SUBJECT: Valuation Snapshot for Test Company
BODY:
Dear Owner,

I have prepared a valuation snapshot for your review.

Best regards,
Advisor"""
        result = _generate_asset_email(company='Test Company', tone='formal')
        assert 'subject' in result
        assert 'body' in result
        assert 'Valuation' in result['subject']

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_fallback_on_api_failure(self, mock_retry):
        """Test asset email returns fallback when API fails."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='Test Company', tone='formal')
        assert 'Valuation Snapshot' in result['subject']
        assert 'Test Company' in result['subject']
        assert 'attached' in result['body'].lower()

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_formal_tone_fallback(self, mock_retry):
        """Test asset email fallback uses formal greeting."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='ACME Corp', tone='formal')
        assert 'Dear' in result['body']
        assert 'Best regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_friendly_tone_fallback(self, mock_retry):
        """Test asset email fallback uses friendly greeting."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='ACME Corp', tone='friendly')
        assert 'Hi' in result['body']
        assert 'Best' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_direct_tone_fallback(self, mock_retry):
        """Test asset email fallback uses direct greeting."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='ACME Corp', tone='direct')
        assert 'Hello' in result['body']
        assert 'Regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_mentions_valuation(self, mock_retry):
        """Test asset email fallback mentions valuation."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='Test Co', tone='formal')
        assert 'valuation' in result['body'].lower()

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_mentions_comparable(self, mock_retry):
        """Test asset email fallback mentions comparables."""
        mock_retry.return_value = None
        result = _generate_asset_email(company='Test Co', tone='formal')
        assert 'comparable' in result['body'].lower()


class TestGenerateCloseEmail:
    """Tests for _generate_close_email function."""

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_with_api_success(self, mock_retry):
        """Test close email generation with successful API call."""
        mock_retry.return_value = """SUBJECT: Quick follow-up - Test Company
BODY:
Dear Owner,

Just checking in about the valuation report.

Best regards,
Advisor"""
        result = _generate_close_email(company='Test Company', tone='formal')
        assert 'subject' in result
        assert 'body' in result
        assert 'follow-up' in result['subject'].lower()

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_fallback_on_api_failure(self, mock_retry):
        """Test close email returns fallback when API fails."""
        mock_retry.return_value = None
        result = _generate_close_email(company='Test Company', tone='formal')
        assert 'follow-up' in result['subject'].lower()
        assert 'Test Company' in result['subject']
        assert '5-minute' in result['body'] or '5 minute' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_formal_tone_fallback(self, mock_retry):
        """Test close email fallback uses formal greeting."""
        mock_retry.return_value = None
        result = _generate_close_email(company='ACME Corp', tone='formal')
        assert 'Dear' in result['body']
        assert 'Best regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_friendly_tone_fallback(self, mock_retry):
        """Test close email fallback uses friendly greeting."""
        mock_retry.return_value = None
        result = _generate_close_email(company='ACME Corp', tone='friendly')
        assert 'Hi' in result['body']
        assert 'Best' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_direct_tone_fallback(self, mock_retry):
        """Test close email fallback uses direct greeting."""
        mock_retry.return_value = None
        result = _generate_close_email(company='ACME Corp', tone='direct')
        assert 'Hello' in result['body']
        assert 'Regards' in result['body']

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_mentions_valuation_report(self, mock_retry):
        """Test close email fallback mentions valuation snapshot."""
        mock_retry.return_value = None
        result = _generate_close_email(company='Test Co', tone='formal')
        assert 'valuation' in result['body'].lower()


class TestGenerateEmails:
    """Tests for generate_emails main function."""

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_returns_all_three(self, mock_retry):
        """Test generate_emails returns hook, asset, and close emails."""
        mock_retry.return_value = """SUBJECT: Test Subject
BODY:
Test body content."""
        result = generate_emails(
            company_name='Test Company',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='Test summary',
            tone='formal'
        )
        assert 'hook' in result
        assert 'asset' in result
        assert 'close' in result

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_each_has_subject_and_body(self, mock_retry):
        """Test each email has subject and body."""
        mock_retry.return_value = """SUBJECT: Test Subject
BODY:
Test body."""
        result = generate_emails(
            company_name='Test Company',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='formal'
        )
        for key in ['hook', 'asset', 'close']:
            assert 'subject' in result[key]
            assert 'body' in result[key]

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_formal_tone(self, mock_retry):
        """Test generate_emails with formal tone."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='formal'
        )
        assert 'Dear' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_friendly_tone(self, mock_retry):
        """Test generate_emails with friendly tone."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='friendly'
        )
        assert 'Hi' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_direct_tone(self, mock_retry):
        """Test generate_emails with direct tone."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='direct'
        )
        assert 'Hello' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_invalid_tone_defaults_to_formal(self, mock_retry):
        """Test invalid tone defaults to formal."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='INVALID'
        )
        assert 'Dear' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_uppercase_tone_normalized(self, mock_retry):
        """Test uppercase tone is normalized to lowercase."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='FRIENDLY'
        )
        assert 'Hi' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_default_tone_is_formal(self, mock_retry):
        """Test default tone is formal when not specified."""
        mock_retry.return_value = None  # Force fallback
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary=''
            # tone not specified, should default to 'formal'
        )
        assert 'Dear' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_generate_emails_handles_exception_gracefully(self, mock_retry):
        """Test generate_emails handles exceptions in email generation."""
        # First call raises exception, subsequent calls return None
        mock_retry.side_effect = [Exception("API Error"), None, None]
        result = generate_emails(
            company_name='Test Co',
            industry='HVAC',
            revenue=5000000,
            median_multiple=4.5,
            website_summary='',
            tone='formal'
        )
        # Should still return dict with all three keys
        assert 'hook' in result
        assert 'asset' in result
        assert 'close' in result


class TestGenerateUpsideBullets:
    """Tests for generate_upside_bullets function."""

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_returns_three(self, mock_retry):
        """Test upside bullets returns exactly 3 items."""
        mock_retry.return_value = """• First bullet point
• Second bullet point
• Third bullet point"""
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=15,
            website_summary=''
        )
        assert len(result) == 3

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_fallback_on_api_failure(self, mock_retry):
        """Test upside bullets returns fallback when API fails."""
        mock_retry.return_value = None
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=15,
            website_summary=''
        )
        assert len(result) == 3
        assert any('margin' in bullet.lower() for bullet in result)

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_removes_bullet_characters(self, mock_retry):
        """Test upside bullets removes bullet character prefixes."""
        mock_retry.return_value = """• Bullet with dot
- Bullet with dash
* Bullet with asterisk"""
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=15,
            website_summary=''
        )
        for bullet in result:
            assert not bullet.startswith('•')
            assert not bullet.startswith('-')
            assert not bullet.startswith('*')

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_pads_if_fewer_than_three(self, mock_retry):
        """Test upside bullets pads to 3 if fewer returned."""
        mock_retry.return_value = """• Only one bullet"""
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=15,
            website_summary=''
        )
        assert len(result) == 3

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_truncates_if_more_than_three(self, mock_retry):
        """Test upside bullets truncates to 3 if more returned."""
        mock_retry.return_value = """• First
• Second
• Third
• Fourth
• Fifth"""
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=15,
            website_summary=''
        )
        assert len(result) == 3

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_handles_zero_margins(self, mock_retry):
        """Test upside bullets handles zero margins."""
        mock_retry.return_value = None
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=0,
            peer_median_margin=0,
            website_summary=''
        )
        assert len(result) == 3

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_handles_none_margins(self, mock_retry):
        """Test upside bullets handles None margins gracefully."""
        mock_retry.return_value = None
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=None,
            peer_median_margin=None,
            website_summary=''
        )
        assert len(result) == 3

    @patch('modules.ai_service._call_with_retry')
    def test_upside_bullets_margin_gap_in_fallback(self, mock_retry):
        """Test upside bullets fallback includes margin gap."""
        mock_retry.return_value = None
        result = generate_upside_bullets(
            company_name='Test Co',
            industry='HVAC',
            target_margin=10,
            peer_median_margin=20,
            website_summary=''
        )
        # First bullet should mention the margin gap (10%)
        assert '10' in result[0] or 'margin' in result[0].lower()


class TestScrapeWebsiteSummary:
    """Tests for scrape_website_summary function."""

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_returns_summary(self, mock_retry):
        """Test scrape returns summary on success."""
        mock_retry.return_value = "Company provides HVAC services."
        result = scrape_website_summary('https://example.com')
        assert result == "Company provides HVAC services."

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_returns_empty_on_failure(self, mock_retry):
        """Test scrape returns empty string on API failure."""
        mock_retry.return_value = None
        result = scrape_website_summary('https://example.com')
        assert result == ""

    def test_scrape_empty_url_returns_empty(self):
        """Test scrape with empty URL returns empty string."""
        result = scrape_website_summary('')
        assert result == ""

    def test_scrape_whitespace_url_returns_empty(self):
        """Test scrape with whitespace URL returns empty string."""
        result = scrape_website_summary('   ')
        assert result == ""

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_adds_https_to_url(self, mock_retry):
        """Test scrape adds https:// to URL without protocol."""
        mock_retry.return_value = "Summary"
        scrape_website_summary('example.com')
        # Check that the call was made with https://
        call_args = mock_retry.call_args[0][0]
        assert 'https://example.com' in call_args

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_preserves_existing_https(self, mock_retry):
        """Test scrape preserves existing https:// protocol."""
        mock_retry.return_value = "Summary"
        scrape_website_summary('https://example.com')
        call_args = mock_retry.call_args[0][0]
        # Should not have double https://
        assert 'https://https://' not in call_args

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_preserves_existing_http(self, mock_retry):
        """Test scrape preserves existing http:// protocol."""
        mock_retry.return_value = "Summary"
        scrape_website_summary('http://example.com')
        call_args = mock_retry.call_args[0][0]
        assert 'http://example.com' in call_args

    @patch('modules.ai_service._call_with_retry')
    def test_scrape_strips_whitespace_from_result(self, mock_retry):
        """Test scrape strips whitespace from result."""
        mock_retry.return_value = "  Summary with whitespace  \n\n"
        result = scrape_website_summary('https://example.com')
        assert result == "Summary with whitespace"


class TestCheckApiStatus:
    """Tests for check_api_status function."""

    @patch('modules.ai_service._get_client')
    def test_api_status_returns_false_when_no_client(self, mock_get_client):
        """Test API status returns False when client not available."""
        mock_get_client.return_value = None
        result = check_api_status()
        assert result is False

    @patch('modules.ai_service._get_client')
    def test_api_status_returns_true_on_success(self, mock_get_client):
        """Test API status returns True on successful API call."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "OK"
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client
        result = check_api_status()
        assert result is True

    @patch('modules.ai_service._get_client')
    def test_api_status_returns_false_on_exception(self, mock_get_client):
        """Test API status returns False on API exception."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        result = check_api_status()
        assert result is False

    @patch('modules.ai_service._get_client')
    def test_api_status_returns_false_on_empty_response(self, mock_get_client):
        """Test API status returns False on empty response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client
        result = check_api_status()
        assert result is False


class TestCallWithRetry:
    """Tests for _call_with_retry function."""

    @patch('modules.ai_service._get_client')
    def test_retry_returns_none_when_no_client(self, mock_get_client):
        """Test retry returns None when client not available."""
        mock_get_client.return_value = None
        from modules.ai_service import _call_with_retry
        result = _call_with_retry("test prompt")
        assert result is None

    @patch('modules.ai_service._get_client')
    def test_retry_returns_response_on_success(self, mock_get_client):
        """Test retry returns response text on success."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Response text"
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client
        from modules.ai_service import _call_with_retry
        result = _call_with_retry("test prompt")
        assert result == "Response text"

    @patch('modules.ai_service.time.sleep')
    @patch('modules.ai_service._get_client')
    def test_retry_retries_on_failure(self, mock_get_client, mock_sleep):
        """Test retry attempts multiple times on failure."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            MagicMock(text="Success")
        ]
        mock_get_client.return_value = mock_client
        from modules.ai_service import _call_with_retry
        result = _call_with_retry("test prompt", max_retries=3)
        assert result == "Success"
        assert mock_client.models.generate_content.call_count == 3

    @patch('modules.ai_service.time.sleep')
    @patch('modules.ai_service._get_client')
    def test_retry_returns_none_after_max_retries(self, mock_get_client, mock_sleep):
        """Test retry returns None after exhausting retries."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("Always fails")
        mock_get_client.return_value = mock_client
        from modules.ai_service import _call_with_retry
        result = _call_with_retry("test prompt", max_retries=3)
        assert result is None
        assert mock_client.models.generate_content.call_count == 3


class TestEmailContentQuality:
    """Tests for email content quality and structure."""

    @patch('modules.ai_service._call_with_retry')
    def test_all_tones_produce_different_greetings(self, mock_retry):
        """Test that different tones produce different greetings in fallbacks."""
        mock_retry.return_value = None  # Force fallback

        formal_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'formal')
        friendly_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'friendly')
        direct_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'direct')

        # Check hook emails have different greetings
        assert 'Dear' in formal_result['hook']['body']
        assert 'Hi' in friendly_result['hook']['body']
        assert 'Hello' in direct_result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_all_tones_produce_different_sign_offs(self, mock_retry):
        """Test that different tones produce different sign-offs in fallbacks."""
        mock_retry.return_value = None  # Force fallback

        formal_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'formal')
        friendly_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'friendly')
        direct_result = generate_emails('Test', 'HVAC', 1000000, 4.0, '', 'direct')

        # Check hook emails have different sign-offs
        assert 'Best regards' in formal_result['hook']['body']
        assert 'Best,' in friendly_result['hook']['body'] or 'Best\n' in friendly_result['hook']['body']
        assert 'Regards' in direct_result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_emails_contain_company_name(self, mock_retry):
        """Test that fallback emails contain the company name."""
        mock_retry.return_value = None
        result = generate_emails('Acme Corporation', 'HVAC', 1000000, 4.0, '', 'formal')

        assert 'Acme Corporation' in result['hook']['body']
        assert 'Acme Corporation' in result['asset']['subject']
        assert 'Acme Corporation' in result['close']['subject']

    @patch('modules.ai_service._call_with_retry')
    def test_hook_email_mentions_industry(self, mock_retry):
        """Test that hook email mentions the industry."""
        mock_retry.return_value = None
        result = generate_emails('Test Co', 'Transportation', 1000000, 4.0, '', 'formal')

        assert 'Transportation' in result['hook']['body']

    @patch('modules.ai_service._call_with_retry')
    def test_asset_email_mentions_attachment(self, mock_retry):
        """Test that asset email mentions the attachment."""
        mock_retry.return_value = None
        result = generate_emails('Test Co', 'HVAC', 1000000, 4.0, '', 'formal')

        body = result['asset']['body'].lower()
        assert 'attached' in body or 'attachment' in body

    @patch('modules.ai_service._call_with_retry')
    def test_close_email_mentions_call(self, mock_retry):
        """Test that close email mentions a call or conversation."""
        mock_retry.return_value = None
        result = generate_emails('Test Co', 'HVAC', 1000000, 4.0, '', 'formal')

        body = result['close']['body'].lower()
        assert 'call' in body or '5-minute' in body or 'conversation' in body
