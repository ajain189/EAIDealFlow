"""
First-visit tooltip display module for EAI DealFlow Terminal.
Provides guided tooltips for first-time users with step-by-step progression.
"""

import json
import os
from typing import Dict, Any, Optional, List

FIRST_VISIT_FILE = "first_visit_state.json"

# Tooltip configurations for each step of the guided tour
TOOLTIPS = [
    {
        "id": "welcome",
        "title": "Welcome to DealFlow Terminal",
        "message": (
            "Let's take a quick tour of the key features. "
            "Click 'Next' to continue or 'Skip Tour' to dismiss."
        ),
        "target": "main",
        "icon": "wave"
    },
    {
        "id": "company_input",
        "title": "Enter Target Company",
        "message": (
            "Start by entering the target company's name, website, and industry. "
            "This powers the AI analysis."
        ),
        "target": "sidebar_input",
        "icon": "building"
    },
    {
        "id": "deal_heat",
        "title": "Deal Heat Score",
        "message": (
            "The Deal Heat score (0-100) shows how attractive a deal is "
            "based on revenue, peer data, and margins."
        ),
        "target": "deal_heat",
        "icon": "fire"
    },
    {
        "id": "analysis_chart",
        "title": "Market Analysis Chart",
        "message": (
            "The interactive chart plots your target against comparable deals. "
            "Drag the slider to adjust margin assumptions."
        ),
        "target": "analysis",
        "icon": "chart"
    },
    {
        "id": "outreach_strategy",
        "title": "AI Outreach Strategy",
        "message": (
            "Click 'Generate Strategy' to create personalized outreach emails "
            "and a PDF valuation report."
        ),
        "target": "outreach",
        "icon": "email"
    },
    {
        "id": "history",
        "title": "Report History",
        "message": (
            "All generated reports are saved here. "
            "You can download PDFs and manage your analysis history."
        ),
        "target": "history",
        "icon": "history"
    }
]


def _load_state() -> Dict[str, Any]:
    """Load first-visit state from file."""
    if os.path.exists(FIRST_VISIT_FILE):
        try:
            with open(FIRST_VISIT_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return _get_default_state()
    return _get_default_state()


def _save_state(state: Dict[str, Any]) -> None:
    """Save first-visit state to file."""
    with open(FIRST_VISIT_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def _get_default_state() -> Dict[str, Any]:
    """Get default first-visit state."""
    return {
        "tour_completed": False,
        "tour_skipped": False,
        "current_step": 0,
        "tooltips_dismissed": []
    }


def is_first_visit() -> bool:
    """
    Check if this is the user's first visit (tour not completed or skipped).

    Returns:
        True if the user hasn't completed or skipped the tour
    """
    state = _load_state()
    return not state.get("tour_completed", False) and not state.get("tour_skipped", False)


def get_current_tooltip() -> Optional[Dict[str, Any]]:
    """
    Get the current tooltip to display.

    Returns:
        Tooltip configuration dict or None if tour is complete
    """
    state = _load_state()

    if state.get("tour_completed") or state.get("tour_skipped"):
        return None

    current_step = state.get("current_step", 0)

    if current_step >= len(TOOLTIPS):
        return None

    return TOOLTIPS[current_step]


def get_tooltip_by_id(tooltip_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific tooltip by its ID.

    Args:
        tooltip_id: The tooltip identifier

    Returns:
        Tooltip configuration dict or None if not found
    """
    for tooltip in TOOLTIPS:
        if tooltip["id"] == tooltip_id:
            return tooltip
    return None


def advance_tooltip() -> Optional[Dict[str, Any]]:
    """
    Advance to the next tooltip in the tour.

    Returns:
        The next tooltip configuration or None if tour is complete
    """
    state = _load_state()
    current_step = state.get("current_step", 0)
    next_step = current_step + 1

    if next_step >= len(TOOLTIPS):
        state["tour_completed"] = True
        state["current_step"] = next_step
        _save_state(state)
        return None

    state["current_step"] = next_step
    _save_state(state)

    return TOOLTIPS[next_step]


def skip_tour() -> None:
    """Mark the tour as skipped."""
    state = _load_state()
    state["tour_skipped"] = True
    _save_state(state)


def complete_tour() -> None:
    """Mark the tour as completed."""
    state = _load_state()
    state["tour_completed"] = True
    _save_state(state)


def reset_tour() -> None:
    """Reset the tour to start from the beginning."""
    _save_state(_get_default_state())


def get_tour_progress() -> Dict[str, Any]:
    """
    Get the current tour progress.

    Returns:
        Dict with current_step, total_steps, and percentage
    """
    state = _load_state()
    current_step = state.get("current_step", 0)
    total_steps = len(TOOLTIPS)

    return {
        "current_step": current_step,
        "total_steps": total_steps,
        "percentage": int((current_step / total_steps) * 100) if total_steps > 0 else 0,
        "is_complete": state.get("tour_completed", False) or state.get("tour_skipped", False)
    }


def get_all_tooltips() -> List[Dict[str, Any]]:
    """
    Get all tooltip configurations.

    Returns:
        List of all tooltip dicts
    """
    return TOOLTIPS.copy()


def dismiss_tooltip(tooltip_id: str) -> None:
    """
    Mark a specific tooltip as dismissed.

    Args:
        tooltip_id: The tooltip identifier to dismiss
    """
    state = _load_state()
    dismissed = state.get("tooltips_dismissed", [])

    if tooltip_id not in dismissed:
        dismissed.append(tooltip_id)
        state["tooltips_dismissed"] = dismissed
        _save_state(state)


def is_tooltip_dismissed(tooltip_id: str) -> bool:
    """
    Check if a specific tooltip has been dismissed.

    Args:
        tooltip_id: The tooltip identifier

    Returns:
        True if the tooltip has been dismissed
    """
    state = _load_state()
    return tooltip_id in state.get("tooltips_dismissed", [])


def get_tour_state() -> Dict[str, Any]:
    """
    Get the full tour state.

    Returns:
        The complete tour state dict
    """
    return _load_state()
