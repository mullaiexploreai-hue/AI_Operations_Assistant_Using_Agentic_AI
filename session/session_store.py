"""Thread-safe in-memory conversation storage for the local POC."""
import threading
from typing import Any, Dict, Optional

from pipeline.state import new_session_state

_lock = threading.Lock()
_sessions: Dict[str, Dict[str, Any]] = {}


# --------------------------------------------------------------------------
# Sessions
# --------------------------------------------------------------------------

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        return _sessions.get(session_id)


def get_or_create_session(session_id: str) -> Dict[str, Any]:
    with _lock:
        if session_id not in _sessions:
            _sessions[session_id] = new_session_state(session_id)
        return _sessions[session_id]


def save_session(session_id: str, state: Dict[str, Any]) -> None:
    with _lock:
        _sessions[session_id] = state

