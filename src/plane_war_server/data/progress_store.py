"""Simple JSON-backed per-user progress store.

Avoids DB migrations by persisting a mapping of user_id -> max_unlocked_level
in a local JSON file. Intended for small-scale/dev use.
"""

from __future__ import annotations

import json
import os
from typing import Dict


PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "user_progress.json")
DEFAULT_MAX_LEVEL = 1


def _load_all() -> Dict[str, int]:
    try:
        if not os.path.exists(PROGRESS_FILE):
            return {}
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {str(k): int(v) for k, v in data.items()}
            return {}
    except Exception:
        return {}


def _save_all(data: Dict[str, int]) -> None:
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # Best-effort; ignore write failures in dev
        pass


def get_max_unlocked_level_for_user(user_id: int) -> int:
    data = _load_all()
    return int(data.get(str(user_id), DEFAULT_MAX_LEVEL))


def set_max_unlocked_level_for_user(user_id: int, max_unlocked_level: int) -> int:
    if max_unlocked_level < DEFAULT_MAX_LEVEL:
        max_unlocked_level = DEFAULT_MAX_LEVEL
    data = _load_all()
    current = int(data.get(str(user_id), DEFAULT_MAX_LEVEL))
    if max_unlocked_level != current:
        data[str(user_id)] = int(max_unlocked_level)
        _save_all(data)
    return int(data[str(user_id)])

