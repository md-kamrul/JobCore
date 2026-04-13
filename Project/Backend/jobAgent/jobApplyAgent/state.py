from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class ApplicationSession:
    application_id: str
    apply_url: str
    profile: Dict[str, Any]
    answers: Dict[str, Any] = field(default_factory=dict)

    # Interactive Selenium session state (in-memory only)
    driver: Any = None
    wait: Any = None
    questions: Any = None
    index: int = 0
    # Remote-debug port used by the real Chrome process (for reconnection)
    debug_port: int = 0


_LOCK = Lock()
_SESSIONS: Dict[str, ApplicationSession] = {}


def create_session(*, apply_url: str, profile: Dict[str, Any]) -> ApplicationSession:
    with _LOCK:
        application_id = str(uuid4())
        session = ApplicationSession(
            application_id=application_id,
            apply_url=apply_url,
            profile=profile or {},
            answers={},
            driver=None,
            wait=None,
            questions=None,
            index=0,
        )
        _SESSIONS[application_id] = session
        return session


def get_session(application_id: str) -> Optional[ApplicationSession]:
    with _LOCK:
        return _SESSIONS.get(application_id)


def update_session_answers(application_id: str, new_answers: Dict[str, Any]) -> Optional[ApplicationSession]:
    with _LOCK:
        session = _SESSIONS.get(application_id)
        if not session:
            return None
        if new_answers:
            session.answers.update({k: v for k, v in new_answers.items() if v is not None})
        return session


def delete_session(application_id: str) -> None:
    with _LOCK:
        session = _SESSIONS.pop(application_id, None)

    # Close Selenium connection and terminate the real Chrome subprocess
    if session:
        try:
            if session.driver:
                # Grab the subprocess handle before quitting the driver
                proc = getattr(session.driver, "_chrome_proc", None)
                try:
                    session.driver.quit()
                except Exception:
                    pass
                # Terminate the real Chrome process we launched
                if proc is not None:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
        except Exception:
            pass
