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
