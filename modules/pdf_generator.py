from fpdf import FPDF
import plotly.io as pio
import pandas as pd
import tempfile
import os

class DealFlowPDF(FPDF):
    """Custom PDF class with EAI branding."""
    
    def header(self):
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(99, 102, 241)
        self.cell(0, 15, 'EAI Capital', ln=True, align='L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Valuation Snapshot', ln=True, align='L')
        self.ln(5)
        self.set_draw_color(99, 102, 241)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Confidential - For Discussion Purposes Only', align='C')

def generate_one_pager(company_name: str, industry: str, revenue: float, valuation_range: tuple,
                       top_comps: pd.DataFrame, chart_fig, upside_bullets: list) -> bytes:
    """Generate PDF report, return as bytes."""
    pdf = DealFlowPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Executive Summary
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f'Target: {company_name}', ln=True)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(64, 64, 64)
    pdf.cell(0, 6, f'Industry: {industry}', ln=True)
    pdf.cell(0, 6, f'Revenue: ${revenue:,.0f}', ln=True)
    pdf.ln(5)
    
    # Valuation Range Box
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(99, 102, 241)
    pdf.rect(10, pdf.get_y(), 190, 25, style='DF')
    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 6, 'Estimated Valuation Range', ln=True)
    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(0, 0, 0)
    low, high, median = valuation_range
    pdf.cell(0, 10, f'${low:,.0f} - ${high:,.0f}', ln=True)
    pdf.ln(15)
    
    # Market Position Chart
    if chart_fig:
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                pio.write_image(chart_fig, tmp.name, width=700, height=400, scale=2)
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 8, 'Market Position', ln=True)
                pdf.image(tmp.name, x=10, w=190)
                os.unlink(tmp.name)
        except:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 8, '[Chart generation failed]', ln=True)
    
    pdf.ln(10)
    
    # Comparable Transactions Table
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Comparable Transactions', ln=True)
    
    if not top_comps.empty:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(99, 102, 241)
        pdf.set_text_color(255, 255, 255)
        col_widths = [70, 40, 40, 40]
        headers = ['Description', 'Revenue', 'Margin', 'Multiple']
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 7, header, border=1, fill=True, align='C')
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        for _, row in top_comps.head(3).iterrows():
            desc = str(row.get('description', 'N/A'))[:35]
            rev = f"${row.get('revenue', 0):,.0f}" if pd.notna(row.get('revenue')) else 'N/A'
            margin = f"{row.get('ebitda_margin', 0):.1f}%" if pd.notna(row.get('ebitda_margin')) else 'N/A'
            mult = f"{row.get('multiple', 0):.2f}x" if pd.notna(row.get('multiple')) else 'N/A'
            
            pdf.cell(col_widths[0], 6, desc, border=1)
            pdf.cell(col_widths[1], 6, rev, border=1, align='R')
            pdf.cell(col_widths[2], 6, margin, border=1, align='R')
            pdf.cell(col_widths[3], 6, mult, border=1, align='R')
            pdf.ln()
    
    pdf.ln(10)
    
    # Operational Upside
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Operational Upside Potential', ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(64, 64, 64)
    for bullet in upside_bullets:
        pdf.cell(5, 6, chr(149))
        pdf.multi_cell(0, 6, f' {bullet}')
    
    return bytes(pdf.output())
