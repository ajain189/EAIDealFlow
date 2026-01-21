"""
PDF Generator module for EAI DealFlow Terminal.
Creates professional one-pager valuation reports using fpdf2.
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
import pandas as pd
import tempfile
import os
from typing import List, Tuple


class DealFlowPDF(FPDF):
    """Custom PDF class with EAI Capital branding."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        """Add branded header to each page."""
        # Logo placeholder (text-based branding)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(99, 102, 241)  # Blurple
        self.cell(0, 12, 'EAI Capital', new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')

        # Tagline
        self.set_font('Helvetica', '', 10)
        self.set_text_color(128, 128, 128)
        self.set_xy(10, 22)
        self.cell(0, 5, 'Valuation Snapshot', new_x=XPos.LMARGIN, new_y=YPos.NEXT,
                  align='L')

        # Divider line
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.5)
        self.line(10, 30, 200, 30)
        self.ln(15)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Confidential - For Discussion Purposes Only', align='C')


def generate_one_pager(
    company_name: str,
    industry: str,
    revenue: float,
    valuation_range: Tuple[float, float, float],
    top_comps: pd.DataFrame,
    chart_fig,
    upside_bullets: List[str]
) -> bytes:
    """
    Generate PDF report, return as bytes.

    Args:
        company_name: Target company name
        industry: Industry category
        revenue: Target revenue
        valuation_range: (low, high, median) valuation tuple
        top_comps: DataFrame of top comparable transactions
        chart_fig: Plotly figure object for the market chart
        upside_bullets: List of 3 upside bullet strings

    Returns:
        PDF as bytes
    """
    pdf = DealFlowPDF()
    pdf.add_page()

    # ===== EXECUTIVE SUMMARY SECTION =====
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(31, 41, 55)  # Dark gray
    pdf.cell(0, 10, f'Target: {company_name}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(75, 85, 99)  # Medium gray
    pdf.cell(0, 6, f'Industry: {industry}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f'Revenue: ${revenue:,.0f}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)

    # ===== VALUATION RANGE BOX =====
    low, high, median = valuation_range

    # Draw background box
    box_y = pdf.get_y()
    pdf.set_fill_color(249, 250, 251)  # Light gray background
    pdf.set_draw_color(99, 102, 241)  # Blurple border
    pdf.set_line_width(0.3)
    pdf.rect(10, box_y, 190, 28, style='DF')

    # Valuation content
    pdf.set_xy(15, box_y + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 6, 'Estimated Valuation Range', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(31, 41, 55)

    if low > 0 and high > 0:
        pdf.cell(0, 12, f'${low:,.0f} - ${high:,.0f}',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 12, 'Insufficient data for valuation',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(box_y + 32)

    # ===== MARKET POSITION CHART =====
    if chart_fig:
        try:
            import plotly.io as pio

            # Create temp file for chart image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name

            # Export chart to PNG
            pio.write_image(chart_fig, tmp_path, width=800, height=450, scale=2)

            pdf.ln(5)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(31, 41, 55)
            pdf.cell(0, 8, 'Market Position', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)

            # Add image
            pdf.image(tmp_path, x=10, w=190)

            # Clean up temp file
            os.unlink(tmp_path)

        except Exception as e:
            print(f"Chart export failed: {e}")
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 8, '[Market position chart - see attached analysis]',
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(8)

    # ===== COMPARABLE TRANSACTIONS TABLE =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, 'Comparable Transactions', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    if not top_comps.empty:
        # Table header
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(99, 102, 241)  # Blurple header
        pdf.set_text_color(255, 255, 255)

        col_widths = [75, 38, 38, 38]
        headers = ['Description', 'Revenue', 'Margin', 'Multiple']

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        pdf.ln()

        # Table rows
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(55, 65, 81)

        row_count = 0
        for _, row in top_comps.iterrows():
            if row_count >= 3:  # Limit to 3 rows
                break

            # Truncate description if too long
            desc = str(row.get('description', 'N/A'))
            if len(desc) > 40:
                desc = desc[:37] + '...'

            # Format values
            rev_val = row.get('revenue')
            rev = f"${rev_val:,.0f}" if pd.notna(rev_val) else 'N/A'
            margin_val = row.get('ebitda_margin')
            margin = f"{margin_val:.1f}%" if pd.notna(margin_val) else 'N/A'
            mult_val = row.get('multiple')
            mult = f"{mult_val:.2f}x" if pd.notna(mult_val) else 'N/A'

            # Alternate row colors
            if row_count % 2 == 1:
                pdf.set_fill_color(249, 250, 251)
                fill = True
            else:
                fill = False

            pdf.cell(col_widths[0], 7, desc, border=1, fill=fill)
            pdf.cell(col_widths[1], 7, rev, border=1, align='R', fill=fill)
            pdf.cell(col_widths[2], 7, margin, border=1, align='R', fill=fill)
            pdf.cell(col_widths[3], 7, mult, border=1, align='R', fill=fill)
            pdf.ln()
            row_count += 1
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, 'No comparable transactions available for this criteria',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(8)

    # ===== OPERATIONAL UPSIDE SECTION =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, 'Operational Upside Potential', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(55, 65, 81)

    for bullet in upside_bullets:
        # Bullet point - use hyphen as bullet since Helvetica doesn't have Unicode
        pdf.set_x(15)
        pdf.cell(5, 6, '-', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.multi_cell(180, 6, f' {bullet}')
        pdf.ln(1)

    # ===== RETURN PDF BYTES =====
    return bytes(pdf.output())


def generate_simple_one_pager(
    company_name: str,
    industry: str,
    revenue: float,
    valuation_range: Tuple[float, float, float],
    peer_count: int,
    upside_bullets: List[str]
) -> bytes:
    """
    Generate a simpler PDF without the chart (faster, no dependencies).

    Args:
        company_name: Target company name
        industry: Industry category
        revenue: Target revenue
        valuation_range: (low, high, median) valuation tuple
        peer_count: Number of comparable peers
        upside_bullets: List of upside bullet strings

    Returns:
        PDF as bytes
    """
    pdf = DealFlowPDF()
    pdf.add_page()

    # Executive Summary
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 10, f'Target: {company_name}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(75, 85, 99)
    pdf.cell(0, 6, f'Industry: {industry}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f'Revenue: ${revenue:,.0f}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f'Based on {peer_count} comparable transactions',
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)

    # Valuation Box
    low, high, median = valuation_range

    box_y = pdf.get_y()
    pdf.set_fill_color(249, 250, 251)
    pdf.set_draw_color(99, 102, 241)
    pdf.rect(10, box_y, 190, 30, style='DF')

    pdf.set_xy(15, box_y + 6)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 6, 'Estimated Valuation Range', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(31, 41, 55)

    if low > 0:
        pdf.cell(0, 12, f'${low:,.0f} - ${high:,.0f}',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 12, 'Valuation data unavailable',
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(box_y + 40)

    # Operational Upside
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 8, 'Operational Upside Potential',
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(55, 65, 81)

    for bullet in upside_bullets:
        pdf.set_x(15)
        pdf.cell(5, 6, '-', new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.multi_cell(180, 6, f' {bullet}')
        pdf.ln(2)

    return bytes(pdf.output())
