"""
Data ingestion module for EAI DealFlow Terminal.
Handles CSV loading, column normalization, industry detection, and peer filtering.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List

from modules.error_handler import get_user_friendly_message

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

# Industry keyword detection - expanded keywords based on actual transaction data
# Keywords are matched case-insensitively against descriptions
INDUSTRY_KEYWORDS = {
    'HVAC': [
        'hvac', 'hvacr', 'heating', 'ventilation', 'air conditioning',
        'refrigeration', 'cooling', 'mechanical contractor', 'plumbing',
        'pipe insulation', 'mechanical engineering'
    ],
    'Transportation': [
        'trucking', 'freight', 'logistics', 'transportation', 'shipping',
        'hauling', 'moving', 'bus', 'towing', 'charter', 'customs broker',
        'packing', 'warehouse', 'storage services', 'forwarding',
        'wood chips', 'sawdust', 'bark'
    ],
    'Utility': [
        'solar', 'energy', 'water', 'gas', 'power', 'electric', 'utility',
        'wastewater', 'propane', 'electricity', 'wind', 'coal', 'photovoltaic',
        'power plant', 'power generation', 'natural gas', 'water treatment',
        'water filtration', 'water purification', 'irrigation', 'distillates',
        'net-metered', 'rooftop solar'
    ]
}


def clean_numeric(value) -> float:
    """
    Strip dirty data symbols ($, %, x, commas) and convert to float.

    Handles:
    - Currency: "$1,000,000" -> 1000000.0
    - Percentages: "15.5%" -> 15.5
    - Multiples: "3.5x" or "3.5X" -> 3.5
    - Parentheses for negatives: "($1,000)" or "(1,000)" -> -1000.0
    - Whitespace and mixed formats
    """
    if pd.isna(value) or value == 'N/A' or value == '-':
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)

    cleaned = str(value).strip()

    # Handle parentheses indicating negative numbers
    is_negative = cleaned.startswith('(') and cleaned.endswith(')')
    if is_negative:
        cleaned = cleaned[1:-1]

    # Remove dirty data symbols (case-insensitive for 'x')
    cleaned = cleaned.replace('$', '').replace(',', '').replace('%', '')
    cleaned = cleaned.replace('x', '').replace('X', '').strip()

    try:
        result = float(cleaned)
        return -result if is_negative else result
    except ValueError:
        return np.nan


def detect_industry(description: str) -> str:
    """
    Detect industry from description using keyword matching.

    Uses a scoring system to find the best matching industry:
    - Each keyword match adds to the industry's score
    - Longer keyword matches score higher (more specific)
    - Returns the industry with the highest score, or 'Other' if no matches

    Args:
        description: Company description text to analyze

    Returns:
        Industry name ('HVAC', 'Transportation', 'Utility', or 'Other')
    """
    if pd.isna(description) or not str(description).strip():
        return 'Other'

    desc_lower = str(description).lower()
    industry_scores = {}

    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in desc_lower:
                # Longer keywords are more specific, give them higher weight
                score += len(keyword)
        if score > 0:
            industry_scores[industry] = score

    if not industry_scores:
        return 'Other'

    # Return the industry with the highest score
    return max(industry_scores, key=industry_scores.get)


def detect_industry_with_details(description: str) -> dict:
    """
    Detect industry from description and return detailed match information.

    Useful for debugging, UI feedback, or understanding why an industry was chosen.

    Args:
        description: Company description text to analyze

    Returns:
        dict with keys:
            - industry: detected industry name
            - matched_keywords: list of keywords that matched
            - scores: dict of industry -> score for all matching industries
            - confidence: 'high', 'medium', or 'low' based on score differential
    """
    if pd.isna(description) or not str(description).strip():
        return {
            'industry': 'Other',
            'matched_keywords': [],
            'scores': {},
            'confidence': 'low'
        }

    desc_lower = str(description).lower()
    industry_scores = {}
    matched_keywords = {}

    for industry, keywords in INDUSTRY_KEYWORDS.items():
        matches = []
        score = 0
        for keyword in keywords:
            if keyword in desc_lower:
                matches.append(keyword)
                score += len(keyword)
        if score > 0:
            industry_scores[industry] = score
            matched_keywords[industry] = matches

    if not industry_scores:
        return {
            'industry': 'Other',
            'matched_keywords': [],
            'scores': {},
            'confidence': 'low'
        }

    best_industry = max(industry_scores, key=industry_scores.get)
    best_score = industry_scores[best_industry]

    # Calculate confidence based on score differential
    other_scores = [s for ind, s in industry_scores.items() if ind != best_industry]
    if not other_scores:
        confidence = 'high'
    elif best_score > max(other_scores) * 2:
        confidence = 'high'
    elif best_score > max(other_scores) * 1.5:
        confidence = 'medium'
    else:
        confidence = 'low'

    return {
        'industry': best_industry,
        'matched_keywords': matched_keywords.get(best_industry, []),
        'scores': industry_scores,
        'confidence': confidence
    }


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
        print(get_user_friendly_message("data", "no_data_directory"))
        return pd.DataFrame()

    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        print(get_user_friendly_message("data", "no_csv_files"))
        return pd.DataFrame()

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.stem  # Track source for industry fallback
            all_dfs.append(df)
            print(f"Loaded {len(df)} rows from {csv_file.name}")
        except Exception:
            print(get_user_friendly_message(
                "data", "csv_load_failed", filename=csv_file.name
            ))

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


def get_peer_group(
    df: pd.DataFrame,
    industry: str,
    revenue: float,
    revenue_min: float = None,
    revenue_max: float = None
) -> pd.DataFrame:
    """
    Filter peers by industry and revenue range.

    Args:
        df: DataFrame with peer transactions
        industry: Industry to filter by (e.g., 'HVAC', 'Transportation', 'Utility')
        revenue: Target company revenue (used for default ±50% range)
        revenue_min: Optional minimum revenue threshold (absolute value).
                     If None, defaults to revenue * 0.5
        revenue_max: Optional maximum revenue threshold (absolute value).
                     If None, defaults to revenue * 1.5

    Returns:
        DataFrame filtered by industry and revenue range
    """
    if df.empty:
        return df

    # Use provided bounds or default to ±50% of target revenue
    min_bound = revenue_min if revenue_min is not None else revenue * 0.5
    max_bound = revenue_max if revenue_max is not None else revenue * 1.5

    # Filter by industry and revenue range
    mask = (df['industry'] == industry)
    if 'revenue' in df.columns:
        mask = mask & (df['revenue'] >= min_bound) & (df['revenue'] <= max_bound)

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
