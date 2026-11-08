"""Store only this application's sign-in state in desktop Secret Service."""

import gi

from .config import URL
from .errors import AuthenticationError

gi.require_version("Secret", "1")
from gi.repository import Secret  # noqa: E402 - Select the namespace version first.


def _saved_login(kind, value=None, *, forget=False, on_progress=None):
    """Keep only this helper's session state in the desktop Secret Service."""
    schema = Secret.Schema.new(
        "in.res.tifr.vpn",
        Secret.SchemaFlags.NONE,
        {
            "server": Secret.SchemaAttributeType.STRING,
            "kind": Secret.SchemaAttributeType.STRING,
        },
    )
    attributes = {"server": URL, "kind": kind}
    try:
        if forget:
            return Secret.password_clear_sync(schema, attributes, None)
        if value is not None:
            return Secret.password_store_sync(
                schema,
                attributes,
                Secret.COLLECTION_DEFAULT,
                "TIFR VPN " + kind,
                value,
                None,
            )
        return Secret.password_lookup_sync(schema, attributes, None)
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        if on_progress is not None:
            on_progress(
                "tifr VPN: desktop keyring unavailable; saved login could not be accessed."
            )
        return None


def load_session(*, on_progress=None):
    return _saved_login("session", on_progress=on_progress)


def save_session(cookie, *, on_progress=None):
    return _saved_login("session", cookie, on_progress=on_progress)


def load_browser_state(*, on_progress=None):
    return _saved_login("browser", on_progress=on_progress)


def save_browser_state(state, *, on_progress=None):
    return _saved_login("browser", state, on_progress=on_progress)


def clear_saved_login():
    cleared = [
        _saved_login("session", forget=True),
        _saved_login("browser", forget=True),
    ]
    if any(result is None for result in cleared):
        raise AuthenticationError("could not clear all saved sign-in state.")


def clear_session(*, on_progress=None):
    return _saved_login("session", forget=True, on_progress=on_progress)
