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

    Scoring (all configurable):
    - Base: configurable points (default 50)
    - Revenue bonus if in sweet spot (default +25, range $2M-$10M)
    - Peer bonus if count >= threshold (default +15, threshold 5)
    - Margin bonus if margin >= threshold (default +10, threshold 15%)

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

    # Get configurable weights
    weights = dh.get('weights', {})
    base_weight = weights.get('base', 50)
    revenue_weight = weights.get('revenue_bonus', 25)
    peer_weight = weights.get('peer_bonus', 15)
    margin_weight = weights.get('margin_bonus', 10)

    score = base_weight

    # Revenue sweet spot bonus
    if rev_min <= revenue <= rev_max:
        score += revenue_weight

    # Peer group density bonus
    if peer_count >= peer_thresh:
        score += peer_weight

    # Margin health bonus
    if median_ebitda_margin and median_ebitda_margin >= margin_thresh:
        score += margin_weight

    return min(score, 100)


def get_heat_color(score: int, config: dict = None) -> str:
    """
    Return color hex based on score with configurable thresholds.

    Default thresholds:
    - Red (#ef4444): score < 50 (Low)
    - Yellow/Amber (#f59e0b): 50 <= score < 75 (Medium)
    - Green/Emerald (#10b981): score >= 75 (High)

    Args:
        score: The deal heat score
        config: Optional config dict, will load from file if not provided

    Returns:
        Hex color string
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    thresholds = dh.get('label_thresholds', {})
    low_max = thresholds.get('low_max', 50)
    medium_max = thresholds.get('medium_max', 75)

    if score < low_max:
        return "#ef4444"  # Red
    elif score < medium_max:
        return "#f59e0b"  # Yellow/Amber
    else:
        return "#10b981"  # Green/Emerald


def get_heat_label(score: int, config: dict = None) -> str:
    """
    Return text label for score range with configurable thresholds.

    Args:
        score: The deal heat score
        config: Optional config dict, will load from file if not provided

    Returns:
        Label string ("Low", "Medium", or "High")
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    thresholds = dh.get('label_thresholds', {})
    low_max = thresholds.get('low_max', 50)
    medium_max = thresholds.get('medium_max', 75)

    if score < low_max:
        return "Low"
    elif score < medium_max:
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
    - base: Base score (configurable, default 50)
    - revenue_bonus: 0 or configured weight (default 25)
    - peer_bonus: 0 or configured weight (default 15)
    - margin_bonus: 0 or configured weight (default 10)
    - total: Final score
    - details: Human-readable explanations
    - weights: The configured weights used
    """
    if config is None:
        config = load_config()

    dh = config.get('deal_heat', {})
    rev_min = dh.get('revenue_min', 2_000_000)
    rev_max = dh.get('revenue_max', 10_000_000)
    peer_thresh = dh.get('peer_threshold', 5)
    margin_thresh = dh.get('margin_threshold', 15)

    # Get configurable weights
    weights = dh.get('weights', {})
    base_weight = weights.get('base', 50)
    revenue_weight = weights.get('revenue_bonus', 25)
    peer_weight = weights.get('peer_bonus', 15)
    margin_weight = weights.get('margin_bonus', 10)

    breakdown = {
        'base': base_weight,
        'revenue_bonus': 0,
        'peer_bonus': 0,
        'margin_bonus': 0,
        'details': [],
        'weights': {
            'base': base_weight,
            'revenue_bonus': revenue_weight,
            'peer_bonus': peer_weight,
            'margin_bonus': margin_weight
        }
    }

    # Revenue check
    if rev_min <= revenue <= rev_max:
        breakdown['revenue_bonus'] = revenue_weight
        rev_min_m = rev_min / 1e6
        rev_max_m = rev_max / 1e6
        breakdown['details'].append(
            f"Revenue ${revenue:,.0f} is in sweet spot (${rev_min_m:.1f}M-${rev_max_m:.1f}M)"
        )
    else:
        breakdown['details'].append(f"Revenue ${revenue:,.0f} is outside sweet spot")

    # Peer count check
    if peer_count >= peer_thresh:
        breakdown['peer_bonus'] = peer_weight
        breakdown['details'].append(f"{peer_count} peers found (threshold: {peer_thresh})")
    else:
        breakdown['details'].append(f"Only {peer_count} peers found (need {peer_thresh}+)")

    # Margin check
    if median_ebitda_margin and median_ebitda_margin >= margin_thresh:
        breakdown['margin_bonus'] = margin_weight
        breakdown['details'].append(f"Median margin {median_ebitda_margin:.1f}% meets threshold ({margin_thresh}%)")
    else:
        margin_str = f"{median_ebitda_margin:.1f}%" if median_ebitda_margin else "N/A"
        breakdown['details'].append(f"Median margin {margin_str} below threshold ({margin_thresh}%)")

    breakdown['total'] = min(
        breakdown['base'] + breakdown['revenue_bonus'] + breakdown['peer_bonus'] + breakdown['margin_bonus'],
        100
    )

    return breakdown
