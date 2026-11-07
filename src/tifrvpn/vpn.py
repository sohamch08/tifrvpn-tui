"""Public VPN operations. No terminal output or process exits occur here."""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

from . import auth, keyring
from . import networkmanager as nm
from .config import Config
from .errors import ConnectionBusy, NetworkManagerError, ProfileNotFound, VPNError


def _operation(function):
    @wraps(function)
    def run(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except VPNError:
            raise
        except ImportError:
            raise VPNError(
                "Required Python or system bindings are missing; see README.md."
            ) from None
        except (OSError, ValueError, subprocess.SubprocessError):
            raise VPNError(
                "Could not prepare the VPN session; check dependencies and configuration."
            ) from None

    return run


@dataclass(frozen=True)
class VPNStatus:
    state: str
    profile_uuid: str | None = None
    details: str = ""
    changed: bool = False

    @property
    def connected(self) -> bool:
        return self.state == "activated"

    @property
    def devices(self) -> tuple[str, ...]:
        for line in self.details.splitlines():
            name, separator, value = line.partition(":")
            if separator and name.strip() == "GENERAL.DEVICES":
                return tuple(
                    item.strip()
                    for item in value.split(",")
                    if item.strip() and item.strip() != "--"
                )
        return ()


def _emit(callback, message):
    if callback is not None:
        callback(message)


@_operation
def status() -> VPNStatus:
    """Read connection state; an absent profile has state not-configured."""
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        return VPNStatus("not-configured")
    state = nm.state(uuid) or "disconnected"
    return VPNStatus(state, uuid, nm.details(uuid) if state == "activated" else "")


@_operation
def setup(*, on_progress: Callable[[str], None] | None = None) -> str:
    """Create/update the user-specific OpenConnect profile and return its UUID."""
    uuid = nm.setup_profile(on_progress=on_progress)
    _emit(on_progress, "✔ tifr VPN: Ivanti profile ready (NetworkManager/OpenConnect)")
    return uuid


@_operation
def connect(
    *,
    quiet: bool = False,
    config: Config | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> VPNStatus:
    """Connect synchronously, reusing a valid saved session when possible.

    Quiet mode hides the browser in Xvfb; GPG may still prompt on the desktop.
    Progress is delivered to on_progress, and expected failures raise VPNError.
    """
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        uuid = setup(on_progress=on_progress)
    state = nm.state(uuid)
    if state == "activated":
        return status()
    if state and state != "deactivated":
        raise ConnectionBusy(f"{state}; wait or run tifrvpn -d before retrying.")
    _emit(on_progress, "⋯ tifr VPN: checking saved sign-in for sslvpn.tifr.res.in")
    nm.validate_profile(uuid)
    cookie = keyring.load_session(on_progress=on_progress)
    if cookie and auth.valid_session(cookie):
        _emit(on_progress, "tifr VPN: reusing saved session")
    else:
        if cookie:
            keyring.clear_session(on_progress=on_progress)
            _emit(
                on_progress,
                "tifr VPN: saved session expired; TIFR requires sign-in again.",
            )
        cookie = auth.authenticate(quiet=quiet, config=config, on_progress=on_progress)
        keyring.save_session(cookie, on_progress=on_progress)
    nm.activate(uuid, cookie, on_progress=on_progress)
    result = status()
    if not result.connected:
        raise NetworkManagerError(f"{result.state}")
    return VPNStatus(result.state, result.profile_uuid, result.details, changed=True)


@_operation
def disconnect(*, on_progress: Callable[[str], None] | None = None) -> VPNStatus:
    """Disconnect an active/transitional profile; safe to repeat."""
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        return VPNStatus("not-configured")
    state = nm.state(uuid)
    if not state or state == "deactivated":
        return VPNStatus("deactivated", uuid)
    nm.deactivate(uuid, on_progress=on_progress)
    return VPNStatus("deactivated", uuid, changed=True)


@_operation
def forget_login() -> None:
    """Clear saved browser and VPN sessions without changing an active tunnel."""
    keyring.clear_saved_login()
