"""Terminal adapters for the public library and the optional GUI tools."""

import argparse
import subprocess
import sys

from . import credentials, vpn
from . import networkmanager as nm
from .config import load_config
from .errors import ConnectionBusy, ProfileNotFound, VPNError
from .gui.credential_setup import setup
from .gui.qr_import import run

USAGE = "Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login|--help]"
HELP = """Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login] (no option: toggle)
Server: https://sslvpn.tifr.res.in/tifruser (Ivanti SSL VPN)
Reuses a valid saved session; otherwise fills TIFR SSO from KeePassXC/GPG.
TIFR may ask you to confirm replacing another active session.
--quiet hides the SSO browser using Xvfb (120-second limit); terminal messages remain visible.
--quiet alone connects. GPG can prompt before background sign-in; retry without --quiet if TIFR needs input.
--forget-login clears remembered sign-in state from the desktop keyring.
TOTP from KeePassXC/GPG: tifr-otp (first run: tifr-otp --setup)"""


def _progress(message):
    # Color status symbols consistently, including redirected output.
    for symbol, color in (("✔", 32), ("●", 32), ("⋯", 33), ("○", 33)):
        if message.startswith(symbol):
            message = f"\033[{color}m{symbol}\033[39m" + message[1:]
            break
    if any(
        text in message
        for text in (
            "desktop keyring unavailable",
            "signing in in the background",
            "submitting saved",
            "SSO reported an error",
            "automatic sign-in",
            "browser session could not be remembered",
        )
    ):
        print(message, file=sys.stderr, flush=True)
    else:
        print(message, flush=True)


def _notify(message):
    try:
        subprocess.run(
            ["notify-send", "-a", "tifrvpn", "tifr VPN", message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def _show_status(result):
    if result.state == "not-configured":
        print("tifr VPN: not configured; run tifrvpn --setup")
        return 1
    if not result.connected:
        print(f"tifr VPN: {result.state}")
        return 1
    _progress("● tifr VPN: Connected (Ivanti/OpenConnect)")
    if result.details:
        print(result.details)
    return 0


def _connect(quiet):
    result = vpn.connect(quiet=quiet, on_progress=_progress)
    code = _show_status(result)
    if not code and result.changed:
        _notify("Connected")
    return code


def _disconnect():
    result = vpn.disconnect(on_progress=_progress)
    if result.state == "not-configured":
        print("tifr VPN: no tifr-ivanti profile; nothing to disconnect.")
    elif result.changed:
        _progress("○ tifr VPN: Disconnected")
        _notify("Disconnected")
    else:
        print("tifr VPN: already disconnected")
    return 0


def _vpn_main(argv):
    action = None
    quiet = False
    for argument in argv:
        if argument == "--quiet":
            quiet = True
        elif argument in (
            "-c",
            "-d",
            "-s",
            "--setup",
            "--forget-login",
            "-h",
            "--help",
        ):
            if action is not None:
                print(
                    "Choose one action: -c, -d, -s, --setup, --forget-login or --help.",
                    file=sys.stderr,
                )
                return 2
            action = argument
        else:
            print(USAGE, file=sys.stderr)
            return 2
    if quiet:
        if action is not None and action != "-c":
            print("--quiet is only supported when connecting (-c).", file=sys.stderr)
            return 2
        action = "-c"
    if action in ("-h", "--help"):
        print(HELP)
        return 0
    if action == "--setup":
        vpn.setup(on_progress=_progress)
        return 0
    if action == "--forget-login":
        vpn.forget_login()
        print("tifr VPN: saved sign-in state cleared; an active tunnel is unaffected.")
        return 0
    if action == "-s":
        return _show_status(vpn.status())
    if action == "-d":
        return _disconnect()
    if action == "-c":
        return _connect(quiet)
    # No arguments: retain the original toggle, including transitional states.
    nm.require_available()
    try:
        state = nm.state(nm.profile_uuid())
    except ProfileNotFound:
        state = ""
    if state and state != "deactivated":
        return _disconnect()
    return _connect(False)


def main(argv=None):
    try:
        return _vpn_main(sys.argv[1:] if argv is None else argv)
    except KeyboardInterrupt:
        print("\ntifr VPN: cancelled", file=sys.stderr)
        return 130
    except ConnectionBusy as error:
        print(f"tifr VPN: {error}")
        return error.returncode
    except VPNError as error:
        message = str(error)
        print(
            message
            if message.startswith("Install dependencies")
            else f"tifr VPN: {message}",
            file=sys.stderr,
        )
        return error.returncode
    except ImportError:
        print(
            "tifr VPN: install dependencies: sudo dnf install python3-gobject webkit2gtk4.1 python3-cryptography",
            file=sys.stderr,
        )
        return 1
    except (ValueError, OSError, subprocess.SubprocessError):
        print(
            "tifr VPN: could not prepare the VPN session; check the preceding errors.",
            file=sys.stderr,
        )
        return 1


def otp_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read a TIFR TOTP from KeePassXC using a GPG-encrypted database password."
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="prompt locally and encrypt the database password",
    )
    parser.add_argument("--recipient", help="GPG recipient fingerprint for setup")
    args = parser.parse_args(argv)
    if args.recipient and not args.setup:
        parser.error("--recipient requires --setup")
    try:
        config = load_config()
        if args.setup:
            credentials.validate_config(config)
            return setup(
                config.password_file,
                config.database,
                config.entry,
                args.recipient,
                on_progress=_progress,
            )
        print(credentials.get_code(config=config))
        return 0
    except KeyboardInterrupt:
        print("\nTIFR OTP: cancelled.", file=sys.stderr)
        return 130
    except RuntimeError as error:
        print(f"TIFR OTP: {error}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError, subprocess.SubprocessError, ImportError):
        print(
            "TIFR OTP: operation failed. No password or code was logged.",
            file=sys.stderr,
        )
        return 1


def import_totp_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read one Google Authenticator migration QR locally; never log its contents."
    )
    parser.add_argument(
        "--image",
        action="store_true",
        help="use a local QR image without starting the webcam",
    )
    args = parser.parse_args(argv)
    try:
        return run(image=args.image)
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        print(
            "The local QR scanner could not start. No QR contents were logged.",
            file=sys.stderr,
        )
        return 1
