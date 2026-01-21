"""
Clipboard Helper Module - Browser-based copy-to-clipboard functionality.

Provides copy-to-clipboard functionality for Streamlit apps using
browser JavaScript (navigator.clipboard API).
"""

import streamlit as st
import streamlit.components.v1 as components


def copy_to_clipboard(text: str, success_message: str = "Copied to clipboard!") -> None:
    """
    Copy text to clipboard using browser JavaScript.

    Uses the navigator.clipboard API which works in modern browsers.
    Shows a success toast notification after copying.

    Args:
        text: The text to copy to clipboard.
        success_message: Message to show in the toast notification.
    """
    # Escape special characters for JavaScript
    escaped_text = _escape_for_js(text)

    # Inject JavaScript to copy to clipboard
    components.html(
        f"""
        <script>
        (function() {{
            const text = `{escaped_text}`;
            navigator.clipboard.writeText(text).then(function() {{
                console.log('Text copied to clipboard');
            }}).catch(function(err) {{
                console.error('Failed to copy text: ', err);
            }});
        }})();
        </script>
        """,
        height=0,
        width=0
    )

    # Show success notification
    st.toast(success_message, icon="✅")


def _escape_for_js(text: str) -> str:
    """
    Escape text for safe inclusion in JavaScript template literals.

    Handles backticks, backslashes, and dollar signs that could
    interfere with template literal syntax.

    Args:
        text: The text to escape.

    Returns:
        Escaped text safe for JavaScript template literals.
    """
    # Escape backslashes first (must be done before other escapes)
    escaped = text.replace('\\', '\\\\')
    # Escape backticks (template literal delimiter)
    escaped = escaped.replace('`', '\\`')
    # Escape ${} interpolation syntax
    escaped = escaped.replace('${', '\\${')
    return escaped


def format_email_for_copy(subject: str, body: str) -> str:
    """
    Format email subject and body into a single copyable string.

    Args:
        subject: The email subject line.
        body: The email body text.

    Returns:
        Formatted email string with subject prefix.
    """
    return f"Subject: {subject}\n\n{body}"


def format_valuation_for_copy(company_name: str, low: float, median: float, high: float) -> str:
    """
    Format valuation range into a copyable string.

    Args:
        company_name: Name of the company.
        low: Low end of valuation range.
        median: Median valuation.
        high: High end of valuation range.

    Returns:
        Formatted valuation string.
    """
    return (
        f"{company_name} - Estimated Valuation Range\n"
        f"Low (25th %ile): ${low:,.0f}\n"
        f"Median: ${median:,.0f}\n"
        f"High (75th %ile): ${high:,.0f}"
    )


def format_deal_summary_for_copy(
    company_name: str,
    industry: str,
    revenue: float,
    heat_score: int,
    heat_label: str,
    peer_count: int
) -> str:
    """
    Format deal summary into a copyable string.

    Args:
        company_name: Name of the company.
        industry: Industry category.
        revenue: Annual revenue.
        heat_score: Deal heat score (0-100).
        heat_label: Heat label (e.g., "Hot", "Warm", "Cold").
        peer_count: Number of comparable deals.

    Returns:
        Formatted deal summary string.
    """
    return (
        f"Deal Summary: {company_name}\n"
        f"Industry: {industry}\n"
        f"Revenue: ${revenue:,.0f}\n"
        f"Deal Heat: {heat_score}/100 ({heat_label})\n"
        f"Comparable Deals: {peer_count}"
    )
