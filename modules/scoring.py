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
