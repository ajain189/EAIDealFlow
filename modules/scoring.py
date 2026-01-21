"""
Deal Heat scoring module for EAI DealFlow Terminal.
Calculates deal attractiveness score with configurable thresholds.
"""

from modules.config import load_config


def calculate_deal_heat(
    revenue: float,
    peer_count: int,
    median_ebitda_margin: float,
    config: dict = None
) -> int:
    """
    Calculate Deal Heat score (0-100).

    Scoring:
    - Base: 50 points
    - +25 if revenue in sweet spot (configurable, default $2M-$10M)
    - +15 if peer count >= threshold (configurable, default 5)
    - +10 if median EBITDA margin >= threshold (configurable, default 15%)

    Args:
        revenue: Target company revenue in dollars
        peer_count: Number of comparable peers found
        median_ebitda_margin: Median EBITDA margin of peer group (as percentage, e.g., 15 for 15%)
        config: Optional config dict, will load from file if not provided

    Returns:
        Integer score from 0-100
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    rev_min = dh.get('revenue_min', 2_000_000)
    rev_max = dh.get('revenue_max', 10_000_000)
    peer_thresh = dh.get('peer_threshold', 5)
    margin_thresh = dh.get('margin_threshold', 15)

    score = 50  # Base score

    # Revenue sweet spot bonus (+25)
    if rev_min <= revenue <= rev_max:
        score += 25

    # Peer group density bonus (+15)
    if peer_count >= peer_thresh:
        score += 15

    # Margin health bonus (+10)
    if median_ebitda_margin and median_ebitda_margin >= margin_thresh:
        score += 10

    return min(score, 100)


def get_heat_color(score: int) -> str:
    """
    Return color hex based on score.

    - Red (#ef4444): score < 50 (Low)
    - Yellow/Amber (#f59e0b): 50 <= score < 75 (Medium)
    - Green/Emerald (#10b981): score >= 75 (High)
    """
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


def get_score_breakdown(
    revenue: float,
    peer_count: int,
    median_ebitda_margin: float,
    config: dict = None
) -> dict:
    """
    Get detailed breakdown of score components.

    Returns dict with:
    - base: Base score (always 50)
    - revenue_bonus: 0 or 25
    - peer_bonus: 0 or 15
    - margin_bonus: 0 or 10
    - total: Final score
    - details: Human-readable explanations
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    rev_min = dh.get('revenue_min', 2_000_000)
    rev_max = dh.get('revenue_max', 10_000_000)
    peer_thresh = dh.get('peer_threshold', 5)
    margin_thresh = dh.get('margin_threshold', 15)

    breakdown = {
        'base': 50,
        'revenue_bonus': 0,
        'peer_bonus': 0,
        'margin_bonus': 0,
        'details': []
    }

    # Revenue check
    if rev_min <= revenue <= rev_max:
        breakdown['revenue_bonus'] = 25
        breakdown['details'].append(f"Revenue ${revenue:,.0f} is in sweet spot (${rev_min/1e6:.1f}M-${rev_max/1e6:.1f}M)")
    else:
        breakdown['details'].append(f"Revenue ${revenue:,.0f} is outside sweet spot")

    # Peer count check
    if peer_count >= peer_thresh:
        breakdown['peer_bonus'] = 15
        breakdown['details'].append(f"{peer_count} peers found (threshold: {peer_thresh})")
    else:
        breakdown['details'].append(f"Only {peer_count} peers found (need {peer_thresh}+)")

    # Margin check
    if median_ebitda_margin and median_ebitda_margin >= margin_thresh:
        breakdown['margin_bonus'] = 10
        breakdown['details'].append(f"Median margin {median_ebitda_margin:.1f}% meets threshold ({margin_thresh}%)")
    else:
        margin_str = f"{median_ebitda_margin:.1f}%" if median_ebitda_margin else "N/A"
        breakdown['details'].append(f"Median margin {margin_str} below threshold ({margin_thresh}%)")

    breakdown['total'] = min(
        breakdown['base'] + breakdown['revenue_bonus'] + breakdown['peer_bonus'] + breakdown['margin_bonus'],
        100
    )

    return breakdown
