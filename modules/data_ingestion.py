"""
Data ingestion module for EAI DealFlow Terminal.
Handles CSV loading, column normalization, industry detection, and peer filtering.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List

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
    'HVAC': ['hvac', 'heating', 'ventilation', 'air conditioning', 'refrigeration', 'cooling'],
    'Transportation': ['trucking', 'freight', 'logistics', 'transportation', 'shipping', 'hauling', 'moving', 'bus', 'towing'],
    'Utility': ['solar', 'energy', 'water', 'gas', 'power', 'electric', 'utility', 'wastewater', 'propane']
}


def clean_numeric(value) -> float:
    """Strip $, %, x, commas and convert to float."""
    if pd.isna(value) or value == 'N/A' or value == '-':
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
    df = df.copy()

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
    else:
        df['industry'] = 'Other'

    return df


def load_all_csvs(data_dir: str = "data") -> pd.DataFrame:
    """Scan data/ folder, load all CSVs, return merged normalized dataframe."""
    all_dfs = []
    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"Warning: Data directory '{data_dir}' does not exist")
        return pd.DataFrame()

    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        print(f"Warning: No CSV files found in '{data_dir}'")
        return pd.DataFrame()

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.stem  # Track source for industry fallback
            all_dfs.append(df)
            print(f"Loaded {len(df)} rows from {csv_file.name}")
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    merged = pd.concat(all_dfs, ignore_index=True)
    normalized = normalize_columns(merged)
    print(f"Total: {len(normalized)} transactions loaded")
    return normalized


def get_available_industries(df: pd.DataFrame) -> List[str]:
    """Get list of available industries from data."""
    if df.empty or 'industry' not in df.columns:
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

    # Filter by industry and revenue range
    mask = (df['industry'] == industry)
    if 'revenue' in df.columns:
        mask = mask & (df['revenue'] >= revenue_min) & (df['revenue'] <= revenue_max)

    filtered = df[mask].copy()
    return filtered


def get_industry_stats(df: pd.DataFrame, industry: str) -> dict:
    """Get summary statistics for an industry."""
    industry_df = df[df['industry'] == industry] if not df.empty else pd.DataFrame()

    if industry_df.empty:
        return {
            'count': 0,
            'median_revenue': 0,
            'median_margin': 0,
            'median_multiple': 0
        }

    return {
        'count': len(industry_df),
        'median_revenue': industry_df['revenue'].median() if 'revenue' in industry_df else 0,
        'median_margin': industry_df['ebitda_margin'].median() if 'ebitda_margin' in industry_df else 0,
        'median_multiple': industry_df['multiple'].median() if 'multiple' in industry_df else 0
    }
