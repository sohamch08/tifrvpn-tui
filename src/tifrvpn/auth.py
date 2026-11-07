"""Validate sessions and coordinate an isolated SSO browser process."""

import json
import os
import shutil
import signal
import ssl
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from . import credentials
from .config import HOST, load_config
from .errors import AuthenticationError

BACKGROUND_TIMEOUT = 120


def valid_session(cookie):
    """Ask the gateway whether the saved session still grants portal access."""

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    request = Request(
        "https://" + HOST + "/dana/home/index.cgi", headers={"Cookie": cookie}
    )
    opener = build_opener(
        NoRedirect(), HTTPSHandler(context=ssl.create_default_context())
    )
    try:
        with opener.open(request, timeout=15) as response:
            return response.status == 200
    except HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            location = urlsplit(error.headers.get("Location", ""))
            return location.hostname in (None, HOST) and location.path.startswith(
                "/dana/home/"
            )
        if error.code in (401, 403):
            return False
        raise


def background_browser(command, *, env=None):
    """Run a disposable virtual display and clean up its entire process group."""
    environment = dict(os.environ if env is None else env, GDK_BACKEND="x11")
    environment.pop("WAYLAND_DISPLAY", None)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        start_new_session=True,
    )
    try:
        output, errors = process.communicate(timeout=BACKGROUND_TIMEOUT)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
        if isinstance(error, KeyboardInterrupt):
            raise
        raise AuthenticationError(
            "Background sign-in timed out. Retry tifrvpn -c to see whether TIFR needs input."
        ) from None
    return subprocess.CompletedProcess(command, process.returncode, output, errors)


def authenticate(*, quiet=False, config=None, on_progress=None):
    # Isolate WebKit from the tunnel controller, including its native shutdown.
    command = [sys.executable, "-m", "tifrvpn._sso_worker"]
    environment = dict(os.environ)
    environment.pop("_TIFR_WORKER_CONFIG", None)
    if config is not None:
        environment.update(
            TIFR_KEEPASS_DATABASE=str(config.database),
            TIFR_KEEPASS_PASSWORD_FILE=str(config.password_file),
            TIFR_KEEPASS_ENTRY=config.entry,
            _TIFR_WORKER_CONFIG=json.dumps(
                {
                    "database": str(config.database),
                    "password_file": str(config.password_file),
                    "entry": config.entry,
                }
            ),
        )
    options = {"env": environment}
    if quiet:
        missing = [
            name for name in ("xvfb-run", "Xvfb", "xauth") if not shutil.which(name)
        ]
        if missing:
            raise AuthenticationError(
                "Background sign-in requires: "
                + ", ".join(missing)
                + ". Install Xvfb and xauth, or retry without --quiet."
            )
        # Unlock on the real desktop before changing DISPLAY. The child only
        # uses cached GPG access, so it can never hide a pinentry prompt.
        selected = config if config is not None else load_config()
        credentials.validate_config(selected)
        credentials.decrypt_password(selected.password_file)
        if on_progress is not None:
            on_progress("tifr VPN: signing in in the background (120-second limit)")
        result = background_browser(
            ["xvfb-run", "-a"] + command + ["--quiet"], **options
        )
    else:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, **options
        )
    if on_progress is not None and result.stderr:
        for message in result.stderr.splitlines():
            on_progress(message)
    if result.returncode:
        if quiet:
            raise AuthenticationError(
                "Background sign-in did not complete. Retry tifrvpn -c to see the sign-in window."
            )
        raise AuthenticationError(
            "SSO sign-in did not complete; no tunnel was started."
        )
    cookie = result.stdout.strip()
    if not cookie.startswith("DSID=") or any(char in cookie for char in "\r\n\0"):
        raise AuthenticationError("Invalid SSO session; no tunnel was started.")
    return cookie
