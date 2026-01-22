# EAI DealFlow Terminal (DFT) v2.0
**Ralph-Optimized Development Specification**

---

## Quick Start

```bash
# Setup
cd EAIDealFlow
python -m venv venv && source venv/bin/activate
pip install streamlit pandas numpy plotly fpdf2 google-genai python-dotenv

# Run
streamlit run app.py
```

**API Key:** Set `GEMINI_API_KEY` in `.env` file or environment variable.

---

## Project Structure

```
EAIDealFlow/
├── app.py                 # Main Streamlit entry point
├── data/                  # CSV benchmark files
│   ├── HVAC.csv
│   ├── Transportation.csv
│   └── Utility.csv
├── modules/
│   ├── data_ingestion.py  # CSV loading & normalization
│   ├── scoring.py         # Deal Heat algorithm
│   ├── visualization.py   # Plotly scatter chart
│   ├── ai_service.py      # Gemini integration
│   ├── pdf_generator.py   # One-pager PDF
│   ├── storage.py         # Local storage & history
│   └── config.py          # Admin settings & constants
├── .env                   # GEMINI_API_KEY=your_key
└── requirements.txt
```

---

## Core Concept

**What it does:** Analyst enters a target company → System benchmarks against CSV data → Generates valuation insights + personalized emails + PDF report.

**Goal:** Reduce analyst time-to-pitch from 45 min to <60 seconds.

---

## Requirements Summary

### Confirmed Decisions

| Area | Decision |
|------|----------|
| Framework | Streamlit (Python) |
| Users | Single user, no auth |
| Offline | Not supported (requires internet for AI) |
| Target Margin | Peer median with draggable override |
| Deal Heat Thresholds | $2M-$10M default + admin editable |
| Industry Detection | Keyword matching + CSV auto-detect + manual add |
| Data Weighting | Equal weight (no recency bias) |
| Chart Outliers | Show all data |
| Chart Interactivity | Full (zoom, pan, hover, drag) |
| Confidence Band | IQR (25th-75th percentile) |
| Peer Count Display | Sidebar + chart subtitle |
| AI Calls | Parallel execution |
| Scrape Failures | Silent fallback → retry with backoff → graceful degradation |
| Email Format | Subject + Body |
| Email Tone | Selector (Formal/Friendly/Direct) |
| Upside Bullets | Template + AI content |
| PDF Quality | Functional with text logo |
| PDF Storage | Store bytes with history |
| Valuation Calc | Multiple range × Revenue |
| History View | Cards with quick preview + detailed modal |
| Delete Options | Single + bulk + auto-archive (90 days) |
| Generate Trigger | Manual click only |
| Copy Emails | Button + selectable text |
| Error Messages | User-friendly hints |
| Tooltips | First visit only, dismissable |
| PDF Prerequisites | Prompt to generate strategy first |
| Keyboard Shortcuts | Optional (off by default) |
| Analytics | Local-only usage stats |
| Admin Settings | Auto-save + reset to defaults |

---

## TASK 1: Project Setup

Create folder structure and config files.

**File: `requirements.txt`**
```
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
fpdf2>=2.7.0
google-genai>=0.3.0
python-dotenv>=1.0.0
requests>=2.31.0
```

**File: `.env`**
```
GEMINI_API_KEY=your_api_key_here
```

**File: `modules/__init__.py`** (empty)

**File: `modules/config.py`**
```python
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "deal_heat": {
        "revenue_min": 2_000_000,
        "revenue_max": 10_000_000,
        "peer_threshold": 5,
        "margin_threshold": 15
    },
    "auto_archive_days": 90,
    "keyboard_shortcuts_enabled": False,
    "first_visit_complete": False
}

def load_config() -> dict:
    """Load config from file or return defaults."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    """Auto-save config to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def reset_to_defaults() -> dict:
    """Reset config to defaults and save."""
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()
```

---

## TASK 2: Data Ingestion Module

**File: `modules/data_ingestion.py`**

**Purpose:** Load CSVs, normalize columns, detect industries, filter peers.

```python
import pandas as pd
import numpy as np
import os
from pathlib import Path

# Column mapping: raw variations -> normalized name
COLUMN_MAP = {
    'sde_margin': ['SDE %', 'SDE_Margin', 'SDE Margin'],
    'ebitda_margin': ['EBITDA %', 'EBITDA_Margin', 'EBITDA Margin'],
    'multiple': ['Multiple', 'EV/EBITDA', 'Valuation Multiple'],
    'revenue': ['Revenue'],
    'date': ['Transaction Date'],
    'description': ['Description'],
    'ebitda': ['EBITDA'],
    'sde': ['SDE'],
    'mvic': ['MVIC Price', 'MVIC']
}

# Industry keyword detection
INDUSTRY_KEYWORDS = {
    'HVAC': ['hvac', 'heating', 'ventilation', 'air conditioning', 'refrigeration'],
    'Transportation': ['trucking', 'freight', 'logistics', 'transportation', 'shipping', 'hauling'],
    'Utility': ['solar', 'energy', 'water', 'gas', 'power', 'electric', 'utility']
}

def clean_numeric(value):
    """Strip $, %, x, commas and convert to float."""
    if pd.isna(value) or value == 'N/A':
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace('$', '').replace(',', '').replace('%', '').replace('x', '').strip()
    try:
        return float(cleaned)
    except ValueError:
        return np.nan

def detect_industry(description: str) -> str:
    """Detect industry from description using keywords."""
    if pd.isna(description):
        return 'Other'
    desc_lower = str(description).lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return industry
    return 'Other'

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and clean data."""
    # Rename columns to normalized names
    rename_map = {}
    for norm_name, variations in COLUMN_MAP.items():
        for var in variations:
            if var in df.columns:
                rename_map[var] = norm_name
                break

    df = df.rename(columns=rename_map)

    # Clean numeric columns
    numeric_cols = ['revenue', 'ebitda', 'sde', 'mvic', 'ebitda_margin', 'sde_margin', 'multiple']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric)

    # Detect industry from description
    if 'description' in df.columns:
        df['industry'] = df['description'].apply(detect_industry)

    return df

def load_all_csvs(data_dir: str = "data") -> pd.DataFrame:
    """Scan data/ folder, load all CSVs, return merged normalized dataframe."""
    all_dfs = []
    data_path = Path(data_dir)

    if not data_path.exists():
        return pd.DataFrame()

    for csv_file in data_path.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.stem  # Track source for industry fallback
            all_dfs.append(df)
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    merged = pd.concat(all_dfs, ignore_index=True)
    return normalize_columns(merged)

def get_available_industries(df: pd.DataFrame) -> list:
    """Get list of available industries from data + allow custom."""
    if 'industry' not in df.columns:
        return ['HVAC', 'Transportation', 'Utility', 'Other']
    industries = df['industry'].dropna().unique().tolist()
    # Ensure base industries are always present
    for base in ['HVAC', 'Transportation', 'Utility']:
        if base not in industries:
            industries.append(base)
    return sorted(industries)

def get_peer_group(df: pd.DataFrame, industry: str, revenue: float) -> pd.DataFrame:
    """Filter to same industry, revenue within ±50%."""
    if df.empty:
        return df

    revenue_min = revenue * 0.5
    revenue_max = revenue * 1.5

    mask = (
        (df['industry'] == industry) &
        (df['revenue'] >= revenue_min) &
        (df['revenue'] <= revenue_max)
    )

    return df[mask].copy()
```

---

## TASK 3: Deal Heat Scoring Module

**File: `modules/scoring.py`**

**Scoring Logic:** Configurable thresholds from admin settings.

```python
from modules.config import load_config

def calculate_deal_heat(revenue: float, peer_count: int, median_ebitda_margin: float, config: dict = None) -> int:
    """
    Calculate Deal Heat score (0-100).

    Scoring:
    - Base: 50 points
    - +25 if revenue in sweet spot (configurable, default $2M-$10M)
    - +15 if peer count >= threshold (configurable, default 5)
    - +10 if median EBITDA margin >= threshold (configurable, default 15%)
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    rev_min = dh.get('revenue_min', 2_000_000)
    rev_max = dh.get('revenue_max', 10_000_000)
    peer_thresh = dh.get('peer_threshold', 5)
    margin_thresh = dh.get('margin_threshold', 15)

    score = 50  # Base

    # Revenue sweet spot bonus
    if rev_min <= revenue <= rev_max:
        score += 25

    # Peer group density bonus
    if peer_count >= peer_thresh:
        score += 15

    # Margin health bonus
    if median_ebitda_margin and median_ebitda_margin >= margin_thresh:
        score += 10

    return min(score, 100)

def get_heat_color(score: int) -> str:
    """Return color hex based on score."""
    if score < 50:
        return "#ef4444"  # Red
    elif score < 75:
        return "#f59e0b"  # Yellow/Amber
    else:
        return "#10b981"  # Green/Emerald

def get_heat_label(score: int) -> str:
    """Return text label for score range."""
    if score < 50:
        return "Low"
    elif score < 75:
        return "Medium"
    else:
        return "High"
```

---

## TASK 4: Visualization Module

**File: `modules/visualization.py`**

**Features:** Scatter plot with draggable target, IQR confidence band, full interactivity.

```python
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_market_chart(
    peers_df: pd.DataFrame,
    target_name: str,
    target_revenue: float,
    target_margin: float,
    show_confidence_band: bool = True
) -> go.Figure:
    """
    Create interactive scatter plot with:
    - Grey dots: peer companies (semi-transparent)
    - Cyan dot: target company (larger, draggable)
    - Shaded IQR confidence band (25th-75th percentile)
    """
    fig = go.Figure()

    # Calculate IQR confidence band if enough data
    if show_confidence_band and len(peers_df) >= 4:
        margin_25 = peers_df['ebitda_margin'].quantile(0.25)
        margin_75 = peers_df['ebitda_margin'].quantile(0.75)
        rev_min = peers_df['revenue'].min()
        rev_max = peers_df['revenue'].max()

        # Add shaded confidence band
        fig.add_trace(go.Scatter(
            x=[rev_min, rev_max, rev_max, rev_min],
            y=[margin_25, margin_25, margin_75, margin_75],
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.1)',
            line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
            name='IQR Range (25th-75th)',
            hoverinfo='skip'
        ))

    # Peers (ghost dots)
    if not peers_df.empty:
        fig.add_trace(go.Scatter(
            x=peers_df['revenue'],
            y=peers_df['ebitda_margin'],
            mode='markers',
            marker=dict(
                size=10,
                color='rgba(156, 163, 175, 0.4)',
                line=dict(width=1, color='rgba(255, 255, 255, 0.2)')
            ),
            name='Market Peers',
            hovertemplate=(
                '<b>Comparable Deal</b><br>'
                'Revenue: $%{x:,.0f}<br>'
                'EBITDA Margin: %{y:.1f}%<br>'
                '<extra></extra>'
            )
        ))

    # Target (cyan orb) - larger and highlighted
    fig.add_trace(go.Scatter(
        x=[target_revenue],
        y=[target_margin],
        mode='markers+text',
        marker=dict(
            size=20,
            color='#06b6d4',
            line=dict(width=3, color='white'),
            symbol='circle'
        ),
        text=[target_name],
        textposition='top center',
        textfont=dict(color='#06b6d4', size=12),
        name=target_name,
        hovertemplate=(
            f'<b>{target_name}</b><br>'
            'Revenue: $%{x:,.0f}<br>'
            'Est. Margin: %{y:.1f}%<br>'
            '<extra></extra>'
        )
    ))

    # Layout with dark theme
    peer_count = len(peers_df)
    fig.update_layout(
        title=dict(
            text=f'Market Position Analysis<br><sub>Based on {peer_count} comparable transactions</sub>',
            font=dict(size=16, color='white')
        ),
        template='plotly_dark',
        paper_bgcolor='#0E1117',
        plot_bgcolor='rgba(30, 35, 50, 0.5)',
        font=dict(family='Inter, sans-serif', color='white'),
        xaxis=dict(
            title='Revenue ($)',
            tickformat='$,.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title='EBITDA Margin (%)',
            ticksuffix='%',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='closest',
        dragmode='pan'  # Enable panning by default
    )

    # Enable zoom and pan
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig

def calculate_valuation_range(peers_df: pd.DataFrame, target_revenue: float) -> tuple:
    """
    Calculate valuation range using Multiple × Revenue.
    Returns (low_val, high_val, median_val).
    """
    if peers_df.empty or 'multiple' not in peers_df.columns:
        return (0, 0, 0)

    multiples = peers_df['multiple'].dropna()
    if len(multiples) == 0:
        return (0, 0, 0)

    low_multiple = multiples.quantile(0.25)
    high_multiple = multiples.quantile(0.75)
    median_multiple = multiples.median()

    return (
        target_revenue * low_multiple,
        target_revenue * high_multiple,
        target_revenue * median_multiple
    )
```

---

## TASK 5: AI Service Module

**File: `modules/ai_service.py`**

**Features:** Parallel email generation, tone selector, retry with backoff, graceful degradation.

```python
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = None
MODEL = "gemini-2.0-flash"

def init_client():
    """Initialize Gemini client."""
    global client
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
    return client is not None

def _call_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with exponential backoff retry."""
    if not client:
        if not init_client():
            return None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1  # 1s, 3s, 5s
                time.sleep(wait_time)
            else:
                print(f"Gemini API failed after {max_retries} attempts: {e}")
                return None
    return None

def scrape_website_summary(url: str) -> str:
    """
    Use Gemini to summarize company from website URL.
    Returns empty string on failure (silent fallback).
    """
    if not url or not url.strip():
        return ""

    prompt = f"""Analyze the website at {url} and extract:
1. Company description (2 sentences max)
2. Key services or products offered
3. Any hints about ownership, size, or employees

Return as brief bullet points. If you cannot access the site, return empty string."""

    result = _call_with_retry(prompt)
    return result if result else ""

# Tone-specific prompt templates
TONE_TEMPLATES = {
    'formal': {
        'style': 'formal, professional, respectful',
        'greeting': 'Dear',
        'sign_off': 'Best regards'
    },
    'friendly': {
        'style': 'warm, personable, conversational but professional',
        'greeting': 'Hi',
        'sign_off': 'Best'
    },
    'direct': {
        'style': 'concise, straightforward, no fluff, action-oriented',
        'greeting': 'Hello',
        'sign_off': 'Regards'
    }
}

def _generate_hook_email(company: str, industry: str, revenue: float, multiple: float, tone: str, summary: str) -> dict:
    """Generate Email 1: The Hook."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""Write a cold outreach email for {company}, a {industry} company.
Context: Revenue is ${revenue:,.0f}. Similar companies trade at {multiple:.1f}x multiple.
Website info: {summary if summary else 'Not available'}

Requirements:
- Tone: {t['style']}
- Start with "{t['greeting']}"
- 3-4 sentences in body
- Mention we see operational upside potential
- Reference the valuation multiple naturally
- No emojis, no hype
- End with "{t['sign_off']}"

Return format:
SUBJECT: [subject line]
BODY:
[email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    return {'subject': 'Introduction - EAI Capital', 'body': f'[Email generation failed. Please write manually for {company}]'}

def _generate_asset_email(company: str, tone: str) -> dict:
    """Generate Email 2: The Asset."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""Write a follow-up email offering a free one-page valuation snapshot for {company}.

Requirements:
- Tone: {t['style']}
- Start with "{t['greeting']}"
- 2-3 sentences
- Reference benchmarking against recent comparable sales
- Mention the PDF is attached
- No emojis
- End with "{t['sign_off']}"

Return format:
SUBJECT: [subject line]
BODY:
[email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    return {'subject': f'Valuation Snapshot for {company}', 'body': '[Email generation failed. Please write manually]'}

def _generate_close_email(company: str, tone: str) -> dict:
    """Generate Email 3: The Close."""
    t = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['formal'])

    prompt = f"""Write a brief final follow-up email for {company} asking for 5 minutes to discuss the valuation report.

Requirements:
- Tone: {t['style']}
- Start with "{t['greeting']}"
- 2 sentences maximum
- Low pressure, respectful of their time
- No emojis
- End with "{t['sign_off']}"

Return format:
SUBJECT: [subject line]
BODY:
[email body]"""

    result = _call_with_retry(prompt)
    if result:
        return _parse_email(result)
    return {'subject': f'Quick follow-up - {company}', 'body': '[Email generation failed. Please write manually]'}

def _parse_email(raw: str) -> dict:
    """Parse raw AI response into subject and body."""
    lines = raw.strip().split('\n')
    subject = ""
    body_lines = []
    in_body = False

    for line in lines:
        if line.upper().startswith('SUBJECT:'):
            subject = line.split(':', 1)[1].strip()
        elif line.upper().startswith('BODY:'):
            in_body = True
        elif in_body:
            body_lines.append(line)

    return {
        'subject': subject or "Follow-up from EAI Capital",
        'body': '\n'.join(body_lines).strip() or raw
    }

def generate_emails(
    company_name: str,
    industry: str,
    revenue: float,
    median_multiple: float,
    website_summary: str,
    tone: str = 'formal'
) -> dict:
    """
    Generate 3-email drip campaign in parallel.
    Returns dict with 'hook', 'asset', 'close' keys, each containing 'subject' and 'body'.
    """
    # Run all 3 email generations in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        hook_future = executor.submit(_generate_hook_email, company_name, industry, revenue, median_multiple, tone, website_summary)
        asset_future = executor.submit(_generate_asset_email, company_name, tone)
        close_future = executor.submit(_generate_close_email, company_name, tone)

        return {
            'hook': hook_future.result(),
            'asset': asset_future.result(),
            'close': close_future.result()
        }

def generate_upside_bullets(
    company_name: str,
    industry: str,
    target_margin: float,
    peer_median_margin: float,
    website_summary: str
) -> list:
    """Generate 3 operational upside bullet points using template + AI."""
    margin_gap = peer_median_margin - target_margin if peer_median_margin and target_margin else 0

    prompt = f"""Generate exactly 3 bullet points about operational upside for {company_name} ({industry}).

Context:
- Margin gap vs peers: {margin_gap:.1f}% potential improvement
- Website info: {website_summary if website_summary else 'Not available'}

Requirements:
- Each bullet should be 1 sentence
- Focus on realistic operational improvements
- Reference specific areas: pricing, efficiency, scale, technology
- Professional tone, no hype
- Format: Return only the 3 bullets, one per line, starting with "•" """

    result = _call_with_retry(prompt)
    if result:
        bullets = [line.strip().lstrip('•').strip() for line in result.strip().split('\n') if line.strip()]
        return bullets[:3] if len(bullets) >= 3 else bullets + ['Operational efficiency improvements identified'] * (3 - len(bullets))

    # Fallback template bullets
    return [
        f"Margin improvement potential of {abs(margin_gap):.1f}% through operational optimization",
        "Scale benefits through EAI's platform resources and vendor relationships",
        "Technology and process improvements to drive efficiency gains"
    ]
```

---

## TASK 6: PDF Generator Module

**File: `modules/pdf_generator.py`**

**Features:** Functional PDF with branding, chart embed, comps table, upside bullets.

```python
from fpdf import FPDF
import plotly.io as pio
import pandas as pd
import tempfile
import os

class DealFlowPDF(FPDF):
    """Custom PDF class with EAI branding."""

    def header(self):
        # Logo placeholder (text-based)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(99, 102, 241)  # Blurple
        self.cell(0, 15, 'EAI Capital', ln=True, align='L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Valuation Snapshot', ln=True, align='L')
        self.ln(5)
        # Divider line
        self.set_draw_color(99, 102, 241)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Confidential - For Discussion Purposes Only', align='C')

def generate_one_pager(
    company_name: str,
    industry: str,
    revenue: float,
    valuation_range: tuple,
    top_comps: pd.DataFrame,
    chart_fig,
    upside_bullets: list
) -> bytes:
    """
    Generate PDF report, return as bytes.

    Args:
        company_name: Target company name
        industry: Industry category
        revenue: Target revenue
        valuation_range: (low, high, median) valuation tuple
        top_comps: DataFrame of top 3 comparable transactions
        chart_fig: Plotly figure object
        upside_bullets: List of 3 upside bullet strings
    """
    pdf = DealFlowPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Executive Summary Section
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
        except Exception as e:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 8, '[Chart generation failed]', ln=True)

    pdf.ln(10)

    # Comparable Transactions Table
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Comparable Transactions', ln=True)

    if not top_comps.empty:
        # Table header
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(99, 102, 241)
        pdf.set_text_color(255, 255, 255)
        col_widths = [70, 40, 40, 40]
        headers = ['Description', 'Revenue', 'Margin', 'Multiple']
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 7, header, border=1, fill=True, align='C')
        pdf.ln()

        # Table rows
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        for _, row in top_comps.head(3).iterrows():
            desc = str(row.get('description', 'N/A'))[:35] + '...' if len(str(row.get('description', ''))) > 35 else str(row.get('description', 'N/A'))
            rev = f"${row.get('revenue', 0):,.0f}" if pd.notna(row.get('revenue')) else 'N/A'
            margin = f"{row.get('ebitda_margin', 0):.1f}%" if pd.notna(row.get('ebitda_margin')) else 'N/A'
            mult = f"{row.get('multiple', 0):.2f}x" if pd.notna(row.get('multiple')) else 'N/A'

            pdf.cell(col_widths[0], 6, desc, border=1)
            pdf.cell(col_widths[1], 6, rev, border=1, align='R')
            pdf.cell(col_widths[2], 6, margin, border=1, align='R')
            pdf.cell(col_widths[3], 6, mult, border=1, align='R')
            pdf.ln()
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 8, 'No comparable transactions available', ln=True)

    pdf.ln(10)

    # Operational Upside Section
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Operational Upside Potential', ln=True)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(64, 64, 64)
    for bullet in upside_bullets:
        pdf.cell(5, 6, chr(149))  # Bullet character
        pdf.multi_cell(0, 6, f' {bullet}')

    return bytes(pdf.output())
```

---

## TASK 7: Storage Module

**File: `modules/storage.py`**

**Features:** Local JSON storage, history with PDF bytes, auto-archive, usage stats.

```python
import json
import os
import base64
from datetime import datetime, timedelta
from typing import Optional
import hashlib

STORAGE_FILE = "dealflow_history.json"
STATS_FILE = "dealflow_stats.json"

def _load_storage() -> dict:
    """Load storage from file."""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {"entries": [], "archived": []}

def _save_storage(data: dict) -> None:
    """Save storage to file."""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def _generate_id(company_name: str, timestamp: str) -> str:
    """Generate unique ID for entry."""
    return hashlib.md5(f"{company_name}{timestamp}".encode()).hexdigest()[:12]

def save_entry(
    company_name: str,
    industry: str,
    revenue: float,
    website: str,
    deal_heat: int,
    valuation_range: tuple,
    emails: dict,
    pdf_bytes: bytes
) -> str:
    """
    Save a new entry to history.
    Returns the entry ID.
    """
    storage = _load_storage()
    timestamp = datetime.now().isoformat()
    entry_id = _generate_id(company_name, timestamp)

    entry = {
        "id": entry_id,
        "company_name": company_name,
        "industry": industry,
        "revenue": revenue,
        "website": website,
        "deal_heat": deal_heat,
        "valuation_low": valuation_range[0],
        "valuation_high": valuation_range[1],
        "valuation_median": valuation_range[2],
        "emails": emails,
        "pdf_base64": base64.b64encode(pdf_bytes).decode() if pdf_bytes else None,
        "created_at": timestamp,
        "archived": False
    }

    storage["entries"].insert(0, entry)  # Most recent first
    _save_storage(storage)

    # Update stats
    increment_stat("reports_generated")

    return entry_id

def get_all_entries(include_archived: bool = False) -> list:
    """Get all entries, optionally including archived."""
    storage = _load_storage()
    entries = storage.get("entries", [])

    if not include_archived:
        entries = [e for e in entries if not e.get("archived", False)]

    return entries

def get_entry_by_id(entry_id: str) -> Optional[dict]:
    """Get a specific entry by ID."""
    storage = _load_storage()
    for entry in storage.get("entries", []):
        if entry.get("id") == entry_id:
            return entry
    return None

def get_pdf_bytes(entry_id: str) -> Optional[bytes]:
    """Get PDF bytes for an entry."""
    entry = get_entry_by_id(entry_id)
    if entry and entry.get("pdf_base64"):
        return base64.b64decode(entry["pdf_base64"])
    return None

def delete_entry(entry_id: str) -> bool:
    """Delete a single entry."""
    storage = _load_storage()
    storage["entries"] = [e for e in storage["entries"] if e.get("id") != entry_id]
    _save_storage(storage)
    return True

def delete_entries(entry_ids: list) -> int:
    """Bulk delete entries. Returns count deleted."""
    storage = _load_storage()
    original_count = len(storage["entries"])
    storage["entries"] = [e for e in storage["entries"] if e.get("id") not in entry_ids]
    _save_storage(storage)
    return original_count - len(storage["entries"])

def archive_entry(entry_id: str) -> bool:
    """Archive a single entry."""
    storage = _load_storage()
    for entry in storage["entries"]:
        if entry.get("id") == entry_id:
            entry["archived"] = True
            _save_storage(storage)
            return True
    return False

def auto_archive_old_entries(days: int = 90) -> int:
    """Auto-archive entries older than specified days. Returns count archived."""
    storage = _load_storage()
    cutoff = datetime.now() - timedelta(days=days)
    count = 0

    for entry in storage["entries"]:
        if not entry.get("archived"):
            created = datetime.fromisoformat(entry.get("created_at", datetime.now().isoformat()))
            if created < cutoff:
                entry["archived"] = True
                count += 1

    if count > 0:
        _save_storage(storage)
    return count

def restore_entry(entry_id: str) -> bool:
    """Restore an archived entry."""
    storage = _load_storage()
    for entry in storage["entries"]:
        if entry.get("id") == entry_id:
            entry["archived"] = False
            _save_storage(storage)
            return True
    return False

# Usage Stats Functions

def _load_stats() -> dict:
    """Load stats from file."""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        "reports_generated": 0,
        "emails_copied": 0,
        "pdfs_downloaded": 0,
        "first_use": None,
        "last_use": None
    }

def _save_stats(stats: dict) -> None:
    """Save stats to file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def increment_stat(stat_name: str, amount: int = 1) -> None:
    """Increment a stat counter."""
    stats = _load_stats()
    stats[stat_name] = stats.get(stat_name, 0) + amount
    stats["last_use"] = datetime.now().isoformat()
    if not stats.get("first_use"):
        stats["first_use"] = stats["last_use"]
    _save_stats(stats)

def get_stats() -> dict:
    """Get all usage stats."""
    return _load_stats()
```

---

## TASK 8: Main Streamlit App

**File: `app.py`**

**Features:** Full layout with sidebar inputs, admin settings, chart, emails, history.

```python
import streamlit as st
from modules.data_ingestion import load_all_csvs, get_peer_group, get_available_industries
from modules.scoring import calculate_deal_heat, get_heat_color, get_heat_label
from modules.visualization import create_market_chart, calculate_valuation_range
from modules.ai_service import scrape_website_summary, generate_emails, generate_upside_bullets, init_client
from modules.pdf_generator import generate_one_pager
from modules.storage import (
    save_entry, get_all_entries, get_entry_by_id, get_pdf_bytes,
    delete_entry, delete_entries, auto_archive_old_entries, increment_stat, get_stats
)
from modules.config import load_config, save_config, reset_to_defaults

# Page config
st.set_page_config(
    page_title="EAI DealFlow Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load config and data
config = load_config()

@st.cache_data
def load_data():
    return load_all_csvs("data")

df = load_data()

# Auto-archive old entries on startup
auto_archive_old_entries(config.get('auto_archive_days', 90))

# Initialize session state
if 'target_margin' not in st.session_state:
    st.session_state.target_margin = None
if 'emails_generated' not in st.session_state:
    st.session_state.emails_generated = None
if 'show_history' not in st.session_state:
    st.session_state.show_history = False

# Apply dark theme CSS
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');

    /* Background */
    .stApp {
        background: radial-gradient(ellipse at top center, #1a1f2e 0%, #0E1117 50%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Glass panels */
    .stTabs [data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }

    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #10b981, #06b6d4);
    }

    /* Typography */
    h1, h2, h3, p, span, label, .stMarkdown {
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }

    /* Monospace for numbers */
    .stMetric [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }

    /* Tooltip styling */
    .tooltip {
        background: rgba(0, 0, 0, 0.8);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Show first-visit tooltips
if not config.get('first_visit_complete', False):
    st.info("👋 Welcome to DealFlow Terminal! Hover over fields for tips. This message won't appear again.")
    config['first_visit_complete'] = True
    save_config(config)

# ============== SIDEBAR ==============
with st.sidebar:
    st.title("📊 DealFlow Terminal")

    # Target Input Section
    st.header("Target Input")

    company_name = st.text_input(
        "Company Name",
        help="Enter the target company's name"
    )

    website = st.text_input(
        "Website URL",
        help="Optional: Used for AI-powered context extraction"
    )

    industries = get_available_industries(df)
    industry = st.selectbox(
        "Industry",
        options=industries + ["+ Add Custom"],
        help="Select industry or add a custom one"
    )

    if industry == "+ Add Custom":
        industry = st.text_input("Enter custom industry")

    revenue = st.number_input(
        "Revenue ($)",
        min_value=0,
        value=1_000_000,
        step=100_000,
        format="%d",
        help="Annual revenue in dollars"
    )

    tone = st.selectbox(
        "Email Tone",
        options=["Formal", "Friendly", "Direct"],
        help="Sets the communication style for generated emails"
    )

    st.divider()

    # Deal Heat Score
    if company_name and revenue > 0 and industry:
        peers = get_peer_group(df, industry, revenue)
        peer_count = len(peers)
        median_margin = peers['ebitda_margin'].median() if peer_count > 0 else 0
        heat = calculate_deal_heat(revenue, peer_count, median_margin, config)
        color = get_heat_color(heat)
        label = get_heat_label(heat)

        st.subheader("Deal Heat Score")
        st.markdown(f"### <span style='color:{color}'>{heat}/100 ({label})</span>", unsafe_allow_html=True)
        st.progress(heat / 100)
        st.caption(f"Based on {peer_count} comparable deals")

    st.divider()

    # Admin Settings (Collapsible)
    with st.expander("⚙️ Admin Settings"):
        st.subheader("Deal Heat Thresholds")

        dh = config.get('deal_heat', {})

        new_rev_min = st.number_input(
            "Revenue Min ($)",
            value=dh.get('revenue_min', 2_000_000),
            step=500_000
        )
        new_rev_max = st.number_input(
            "Revenue Max ($)",
            value=dh.get('revenue_max', 10_000_000),
            step=500_000
        )
        new_peer_thresh = st.number_input(
            "Peer Count Threshold",
            value=dh.get('peer_threshold', 5),
            min_value=1,
            max_value=20
        )
        new_margin_thresh = st.number_input(
            "Margin Threshold (%)",
            value=dh.get('margin_threshold', 15),
            min_value=0,
            max_value=50
        )

        # Auto-save on change
        if (new_rev_min != dh.get('revenue_min') or
            new_rev_max != dh.get('revenue_max') or
            new_peer_thresh != dh.get('peer_threshold') or
            new_margin_thresh != dh.get('margin_threshold')):

            config['deal_heat'] = {
                'revenue_min': new_rev_min,
                'revenue_max': new_rev_max,
                'peer_threshold': new_peer_thresh,
                'margin_threshold': new_margin_thresh
            }
            save_config(config)
            st.success("Settings auto-saved!")
            st.rerun()

        if st.button("Reset to Defaults"):
            config = reset_to_defaults()
            st.rerun()

        st.divider()

        # Usage Stats
        st.subheader("Usage Stats")
        stats = get_stats()
        st.metric("Reports Generated", stats.get('reports_generated', 0))
        st.metric("PDFs Downloaded", stats.get('pdfs_downloaded', 0))

# ============== MAIN CONTENT ==============
col1, col2 = st.columns([2, 1])

with col1:
    # Toggle between Chart and History
    tab1, tab2 = st.tabs(["📈 Analysis", "📋 History"])

    with tab1:
        if company_name and revenue > 0 and industry and industry != "+ Add Custom":
            peers = get_peer_group(df, industry, revenue)

            # Calculate target margin (use session state if dragged, else peer median)
            if st.session_state.target_margin is None:
                target_margin = peers['ebitda_margin'].median() if len(peers) > 0 else 15.0
            else:
                target_margin = st.session_state.target_margin

            # Margin adjustment slider (simulates draggable)
            target_margin = st.slider(
                "Adjust Target Margin (%)",
                min_value=0.0,
                max_value=50.0,
                value=float(target_margin),
                step=0.5,
                help="Drag to adjust the target's estimated margin position"
            )
            st.session_state.target_margin = target_margin

            # Create and display chart
            fig = create_market_chart(peers, company_name, revenue, target_margin)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

            # Valuation range
            val_range = calculate_valuation_range(peers, revenue)
            if val_range[0] > 0:
                st.markdown("### Estimated Valuation Range")
                vcol1, vcol2, vcol3 = st.columns(3)
                with vcol1:
                    st.metric("Low (25th %ile)", f"${val_range[0]:,.0f}")
                with vcol2:
                    st.metric("Median", f"${val_range[2]:,.0f}")
                with vcol3:
                    st.metric("High (75th %ile)", f"${val_range[1]:,.0f}")
        else:
            st.info("Enter company details in the sidebar to begin analysis.")

    with tab2:
        # History View
        st.subheader("Report History")

        entries = get_all_entries(include_archived=False)

        if entries:
            # Bulk delete option
            selected_ids = []
            for entry in entries:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    if st.checkbox(
                        f"**{entry['company_name']}** ({entry['industry']}) - ${entry['revenue']:,.0f}",
                        key=f"select_{entry['id']}"
                    ):
                        selected_ids.append(entry['id'])
                    st.caption(f"Deal Heat: {entry['deal_heat']} | Created: {entry['created_at'][:10]}")
                with col_b:
                    if st.button("View", key=f"view_{entry['id']}"):
                        st.session_state.viewing_entry = entry['id']
                with col_c:
                    pdf = get_pdf_bytes(entry['id'])
                    if pdf:
                        st.download_button(
                            "PDF",
                            pdf,
                            f"{entry['company_name']}_Valuation.pdf",
                            key=f"pdf_{entry['id']}"
                        )
                st.divider()

            if selected_ids:
                if st.button(f"🗑️ Delete Selected ({len(selected_ids)})"):
                    delete_entries(selected_ids)
                    st.success(f"Deleted {len(selected_ids)} entries")
                    st.rerun()
        else:
            st.info("No saved reports yet. Generate your first report!")

with col2:
    st.header("📧 Outreach Strategy")

    # Generate Strategy Button
    if company_name and revenue > 0 and industry:
        if st.button("🚀 Generate Strategy", type="primary", use_container_width=True):
            with st.spinner("AI generating personalized emails..."):
                # Get website summary (silent fallback on failure)
                summary = scrape_website_summary(website) if website else ""

                # Get peer data for context
                peers = get_peer_group(df, industry, revenue)
                median_multiple = peers['multiple'].median() if len(peers) > 0 else 3.0

                # Generate emails in parallel
                emails = generate_emails(
                    company_name,
                    industry,
                    revenue,
                    median_multiple,
                    summary,
                    tone.lower()
                )

                st.session_state.emails_generated = emails
                st.session_state.website_summary = summary

        # Display generated emails
        if st.session_state.emails_generated:
            emails = st.session_state.emails_generated

            email_tabs = st.tabs(["🎣 Hook", "📎 Asset", "🤝 Close"])

            for i, (tab, key) in enumerate(zip(email_tabs, ['hook', 'asset', 'close'])):
                with tab:
                    email = emails[key]
                    st.text_input("Subject", email['subject'], key=f"subject_{key}")
                    body = st.text_area("Body", email['body'], height=200, key=f"body_{key}")

                    # Copy button
                    full_email = f"Subject: {email['subject']}\n\n{email['body']}"
                    if st.button(f"📋 Copy Email", key=f"copy_{key}"):
                        st.code(full_email)
                        increment_stat("emails_copied")
                        st.success("Email copied! Use Cmd+C to copy from the box above.")

            st.divider()

            # PDF Generation
            if st.button("📄 Generate PDF Report", type="secondary", use_container_width=True):
                if not st.session_state.emails_generated:
                    st.warning("Please generate strategy first before creating PDF.")
                else:
                    with st.spinner("Generating PDF..."):
                        peers = get_peer_group(df, industry, revenue)
                        target_margin = st.session_state.target_margin or peers['ebitda_margin'].median()
                        val_range = calculate_valuation_range(peers, revenue)

                        # Get top 3 comps
                        top_comps = peers.nlargest(3, 'revenue') if len(peers) > 0 else peers

                        # Generate upside bullets
                        upside = generate_upside_bullets(
                            company_name,
                            industry,
                            target_margin,
                            peers['ebitda_margin'].median() if len(peers) > 0 else 15,
                            st.session_state.get('website_summary', '')
                        )

                        # Create chart for PDF
                        fig = create_market_chart(peers, company_name, revenue, target_margin)

                        # Generate PDF
                        pdf_bytes = generate_one_pager(
                            company_name,
                            industry,
                            revenue,
                            val_range,
                            top_comps,
                            fig,
                            upside
                        )

                        # Save to history
                        entry_id = save_entry(
                            company_name,
                            industry,
                            revenue,
                            website,
                            calculate_deal_heat(revenue, len(peers), peers['ebitda_margin'].median() if len(peers) > 0 else 0, config),
                            val_range,
                            st.session_state.emails_generated,
                            pdf_bytes
                        )

                        # Download button
                        st.download_button(
                            "⬇️ Download PDF",
                            pdf_bytes,
                            f"{company_name.replace(' ', '_')}_Valuation.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        increment_stat("pdfs_downloaded")
                        st.success(f"Report saved! ID: {entry_id}")
    else:
        st.info("Enter company details in the sidebar to generate outreach strategy.")
```

---

## TASK 9: Error Handling & User Feedback

Add user-friendly error messages throughout the app.

**Error Message Templates:**
```python
ERROR_MESSAGES = {
    'no_peers': "No comparable deals found for this industry and revenue range. Try adjusting the revenue or selecting a different industry.",
    'api_failed': "AI generation temporarily unavailable. You can still use the chart and valuation features.",
    'invalid_revenue': "Please enter a valid revenue amount greater than $0.",
    'no_company': "Please enter a company name to continue.",
    'pdf_failed': "PDF generation failed. Please try again.",
    'scrape_failed': ""  # Silent - no message shown
}
```

---

## TASK 10: Testing Checklist

- [x] CSV loading with all 3 industry files
- [x] Column normalization with dirty data ($, %, x symbols)
- [x] Industry detection from descriptions
- [x] Peer filtering by industry + revenue range
- [x] Deal Heat scoring with configurable thresholds
- [x] Chart rendering with confidence band
- [x] Margin slider updates chart in real-time
- [x] Valuation range calculation
- [x] Email generation (all 3 tones)
- [x] PDF generation with all sections
- [x] History save/load/delete
- [x] Admin settings auto-save
- [x] First-visit tooltip display
- [x] Copy-to-clipboard functionality

---

## Color Reference

| Use | Color | Hex |
|-----|-------|-----|
| Background | Deep Charcoal | `#0E1117` |
| Gradient Top | Slate | `#1a1f2e` |
| Glass Border | White 10% | `rgba(255,255,255,0.1)` |
| Primary Button | Blurple | `#6366f1` to `#8b5cf6` |
| Target Dot | Cyan | `#06b6d4` |
| Peer Dots | Grey | `#9ca3af` at 40% |
| Success/Green | Emerald | `#10b981` |
| Warning/Yellow | Amber | `#f59e0b` |
| Error/Red | Red | `#ef4444` |
| Confidence Band | Blurple 10% | `rgba(99, 102, 241, 0.1)` |

---

## CSV Data Format Reference

All CSVs in `data/` should have these columns (names may vary):

| Column | Example Values |
|--------|----------------|
| Transaction Date | `06/30/2025` |
| Description | `HVAC Company` |
| Revenue | `3436991` or `$3,436,991` |
| EBITDA | `449404` |
| EBITDA Margin | `13.08%` or `13.08` |
| SDE | `534404` |
| SDE Margin | `15.55%` |
| Valuation Multiple | `1.34x` or `1.34` |
| MVIC Price | `600000` |

---

## Security Notes

1. **API Key:** Never hardcode. Use `.env` file or environment variable.
2. **Data Privacy:** CSVs stay local. Only aggregated metrics sent to Gemini.
3. **No raw deal data** in AI prompts - only medians, counts, industry names.
4. **Local storage:** All history stored locally in JSON files.

---

## Task Checklist for Ralph

- [x] **Task 1:** Create folder structure + config.py
- [x] **Task 2:** Build `data_ingestion.py` (CSV load, normalize, peer filter, industry detect)
- [x] **Task 3:** Build `scoring.py` (Deal Heat with configurable thresholds)
- [x] **Task 4:** Build `visualization.py` (Plotly chart with IQR band)
- [x] **Task 5:** Build `ai_service.py` (Gemini with retry, parallel emails, tone selector)
- [x] **Task 6:** Build `pdf_generator.py` (fpdf2 one-pager)
- [x] **Task 7:** Build `storage.py` (local JSON history, stats, auto-archive)
- [x] **Task 8:** Build `app.py` (full Streamlit app with all features)
- [x] **Task 9:** Add error handling with user-friendly messages
- [x] **Task 10:** Test full flow with sample data
