from __future__ import annotations

from pathlib import Path
from typing import Optional

from libtools.registry import Entry


library_root: Optional[Path] = None
entries: list[Entry] = []
selected_entry_id: Optional[str] = None
schema_override: dict | None = None


def selected_entry() -> Entry | None:
    if selected_entry_id is None:
        return None
    for entry in entries:
        if entry.id == selected_entry_id:
            return entry
    return None
