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

def save_entry(company_name: str, industry: str, revenue: float, website: str,
               deal_heat: int, valuation_range: tuple, emails: dict, pdf_bytes: bytes) -> str:
    """Save a new entry to history. Returns the entry ID."""
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
    
    storage["entries"].insert(0, entry)
    _save_storage(storage)
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

def auto_archive_old_entries(days: int = 90) -> int:
    """Auto-archive entries older than specified days."""
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

def _load_stats() -> dict:
    """Load stats from file."""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"reports_generated": 0, "emails_copied": 0, "pdfs_downloaded": 0}

def _save_stats(stats: dict) -> None:
    """Save stats to file."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def increment_stat(stat_name: str, amount: int = 1) -> None:
    """Increment a stat counter."""
    stats = _load_stats()
    stats[stat_name] = stats.get(stat_name, 0) + amount
    _save_stats(stats)

def get_stats() -> dict:
    """Get all usage stats."""
    return _load_stats()
