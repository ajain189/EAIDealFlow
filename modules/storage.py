"""
Storage module for EAI DealFlow Terminal.
Handles local JSON storage for history, PDF caching, auto-archive, and usage stats.
"""

import json
import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from modules.error_handler import get_user_friendly_message

STORAGE_FILE = "dealflow_history.json"
STATS_FILE = "dealflow_stats.json"


def _load_storage() -> Dict[str, Any]:
    """Load storage from file."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(get_user_friendly_message("storage", "file_corrupted"))
            return {"entries": [], "archived": []}
        except IOError:
            print(get_user_friendly_message("storage", "load_failed"))
            return {"entries": [], "archived": []}
    return {"entries": [], "archived": []}


def _save_storage(data: Dict[str, Any]) -> bool:
    """Save storage to file. Returns True on success, False on failure."""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError:
        print(get_user_friendly_message("storage", "save_failed"))
        return False


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
    emails: Dict[str, Dict[str, str]],
    pdf_bytes: bytes
) -> str:
    """
    Save a new entry to history.

    Args:
        company_name: Target company name
        industry: Industry category
        revenue: Target revenue
        website: Company website URL
        deal_heat: Deal Heat score
        valuation_range: (low, high, median) tuple
        emails: Dict of generated emails
        pdf_bytes: PDF report as bytes

    Returns:
        The entry ID
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
        "valuation_low": valuation_range[0] if valuation_range else 0,
        "valuation_high": valuation_range[1] if valuation_range else 0,
        "valuation_median": valuation_range[2] if len(valuation_range) > 2 else 0,
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


def get_all_entries(include_archived: bool = False) -> List[Dict[str, Any]]:
    """
    Get all entries, optionally including archived.

    Args:
        include_archived: Whether to include archived entries

    Returns:
        List of entry dicts
    """
    storage = _load_storage()
    entries = storage.get("entries", [])

    if not include_archived:
        entries = [e for e in entries if not e.get("archived", False)]

    return entries


def get_entry_by_id(entry_id: str) -> Optional[Dict[str, Any]]:
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
        try:
            return base64.b64decode(entry["pdf_base64"])
        except Exception:
            return None
    return None


def delete_entry(entry_id: str) -> bool:
    """Delete a single entry."""
    storage = _load_storage()
    original_len = len(storage["entries"])
    storage["entries"] = [e for e in storage["entries"] if e.get("id") != entry_id]

    if len(storage["entries"]) < original_len:
        _save_storage(storage)
        return True
    return False


def delete_entries(entry_ids: List[str]) -> int:
    """
    Bulk delete entries.

    Args:
        entry_ids: List of entry IDs to delete

    Returns:
        Count of entries deleted
    """
    storage = _load_storage()
    original_count = len(storage["entries"])
    storage["entries"] = [e for e in storage["entries"] if e.get("id") not in entry_ids]
    deleted_count = original_count - len(storage["entries"])

    if deleted_count > 0:
        _save_storage(storage)

    return deleted_count


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
    """
    Auto-archive entries older than specified days.

    Args:
        days: Number of days after which to archive

    Returns:
        Count of entries archived
    """
    storage = _load_storage()
    cutoff = datetime.now() - timedelta(days=days)
    count = 0

    for entry in storage["entries"]:
        if not entry.get("archived"):
            try:
                created = datetime.fromisoformat(entry.get("created_at", ""))
                if created < cutoff:
                    entry["archived"] = True
                    count += 1
            except (ValueError, TypeError):
                continue

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


def get_archived_entries() -> List[Dict[str, Any]]:
    """Get only archived entries."""
    storage = _load_storage()
    return [e for e in storage.get("entries", []) if e.get("archived", False)]


def search_entries(query: str) -> List[Dict[str, Any]]:
    """
    Search entries by company name or industry.

    Args:
        query: Search query string

    Returns:
        List of matching entries
    """
    query_lower = query.lower()
    entries = get_all_entries(include_archived=False)

    return [
        e for e in entries
        if query_lower in e.get("company_name", "").lower()
        or query_lower in e.get("industry", "").lower()
    ]


# ===== USAGE STATS =====

def _load_stats() -> Dict[str, Any]:
    """Load stats from file."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "reports_generated": 0,
        "emails_copied": 0,
        "pdfs_downloaded": 0,
        "first_use": None,
        "last_use": None
    }


def _save_stats(stats: Dict[str, Any]) -> None:
    """Save stats to file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def increment_stat(stat_name: str, amount: int = 1) -> None:
    """
    Increment a stat counter.

    Args:
        stat_name: Name of the stat to increment
        amount: Amount to increment by
    """
    stats = _load_stats()
    stats[stat_name] = stats.get(stat_name, 0) + amount
    stats["last_use"] = datetime.now().isoformat()

    if not stats.get("first_use"):
        stats["first_use"] = stats["last_use"]

    _save_stats(stats)


def get_stats() -> Dict[str, Any]:
    """Get all usage stats."""
    return _load_stats()


def reset_stats() -> None:
    """Reset all stats to zero."""
    stats = {
        "reports_generated": 0,
        "emails_copied": 0,
        "pdfs_downloaded": 0,
        "first_use": None,
        "last_use": None
    }
    _save_stats(stats)


def get_entry_count() -> Dict[str, int]:
    """Get count of entries by status."""
    storage = _load_storage()
    entries = storage.get("entries", [])

    active = len([e for e in entries if not e.get("archived", False)])
    archived = len([e for e in entries if e.get("archived", False)])

    return {
        "active": active,
        "archived": archived,
        "total": len(entries)
    }
