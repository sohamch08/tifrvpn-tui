"""NetworkManager/OpenConnect backend, using nmcli without shell evaluation."""

import base64
import hashlib
import os
import shutil
import socket
import ssl
import subprocess

from .config import HOST, URL
from .errors import NetworkManagerError, ProfileNotFound

PROFILE_NAME = "tifr-ivanti"
VPN_DATA = (
    f"gateway={URL},protocol=nc,prevent_invalid_cert=yes,"
    "cookie-flags=2,gateway-flags=2,gwcert-flags=2,resolve-flags=2"
)


def _run(arguments, *, on_progress=None, **options):
    result = subprocess.run(
        ["nmcli", *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ, LC_ALL="C"),
        **options,
    )
    if result.returncode:
        raise NetworkManagerError(
            result.stderr.strip() or "NetworkManager operation failed.",
            returncode=result.returncode,
        )
    if on_progress is not None and result.stdout.strip():
        on_progress(result.stdout.rstrip())
    return result.stdout.strip()


def require_available():
    if not all(
        shutil.which(name) for name in ("nmcli", "openconnect", "python3")
    ) or not os.access("/usr/libexec/nm-openconnect-service", os.X_OK):
        raise NetworkManagerError(
            "Install dependencies listed in README.md (NetworkManager-openconnect, OpenConnect and system Python bindings)."
        )
    _run(["general", "status"])


def profile_uuid():
    result = subprocess.run(
        [
            "nmcli",
            "--get-values",
            "connection.uuid",
            "connection",
            "show",
            "id",
            PROFILE_NAME,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ, LC_ALL="C"),
    )
    if result.returncode or not result.stdout.strip():
        raise ProfileNotFound("no tifr-ivanti profile")
    uuid = result.stdout.strip()
    if "\n" in uuid:
        raise NetworkManagerError(
            "expected one NetworkManager profile named tifr-ivanti."
        )
    return uuid


def setup_profile(*, on_progress=None):
    require_available()
    try:
        uuid = profile_uuid()
    except ProfileNotFound:
        names = _run(["--get-values", "NAME", "connection", "show"]).splitlines()
        if PROFILE_NAME in names:
            raise NetworkManagerError(
                "ambiguous tifr-ivanti profile; resolve duplicate names before setup."
            ) from None
        import getpass

        _run(
            [
                "connection",
                "add",
                "type",
                "vpn",
                "vpn-type",
                "openconnect",
                "con-name",
                PROFILE_NAME,
                "connection.permissions",
                "user:" + getpass.getuser(),
                "connection.autoconnect",
                "no",
                "vpn.data",
                VPN_DATA,
            ],
            on_progress=on_progress,
        )
        return profile_uuid()
    service = _run(
        ["--get-values", "vpn.service-type", "connection", "show", "uuid", uuid]
    )
    if service != "org.freedesktop.NetworkManager.openconnect":
        raise NetworkManagerError(
            "tifr-ivanti exists but uses a different VPN plugin; rename it before setup."
        )
    _run(
        [
            "connection",
            "modify",
            "uuid",
            uuid,
            "connection.autoconnect",
            "no",
            "+vpn.data",
            VPN_DATA,
        ],
        on_progress=on_progress,
    )
    return uuid


def state(uuid):
    return _run(["--get-values", "GENERAL.STATE", "connection", "show", "uuid", uuid])


def details(uuid):
    return _run(
        [
            "--fields",
            "GENERAL.STATE,GENERAL.DEVICES,IP4.ADDRESS,IP4.DNS,IP6.ADDRESS,IP6.DNS",
            "connection",
            "show",
            "uuid",
            uuid,
        ]
    )


def validate_profile(uuid):
    service = _run(["-g", "vpn.service-type", "connection", "show", "uuid", uuid])
    data = _run(
        ["--escape", "no", "-g", "vpn.data", "connection", "show", "uuid", uuid]
    )
    settings = dict(
        item.strip().split(" = ", 1) for item in data.split(",") if " = " in item
    )
    if (
        service != "org.freedesktop.NetworkManager.openconnect"
        or settings.get("gateway") != URL
        or settings.get("protocol") != "nc"
    ):
        raise NetworkManagerError("Profile settings differ; run tifrvpn --setup.")


def activate(uuid, cookie, *, on_progress=None):
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    # Verify the gateway with the system trust store before pinning this session.
    context = ssl.create_default_context()
    with (
        socket.create_connection((HOST, 443), timeout=15) as connection,
        context.wrap_socket(connection, server_hostname=HOST) as tls,
    ):
        public_key = x509.load_der_x509_certificate(
            tls.getpeercert(binary_form=True)
        ).public_key()
        spki = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        fingerprint = (
            "pin-sha256:" + base64.b64encode(hashlib.sha256(spki).digest()).decode()
        )
        gateway_ip = tls.getpeername()[0]
    secrets = {
        "cookie": cookie,
        "gateway": "https://" + HOST,
        "gwcert": fingerprint,
        "resolve": f"{HOST}:{gateway_ip}",
    }
    fd = os.memfd_create("tifr-vpn-session", os.MFD_CLOEXEC)
    try:
        with os.fdopen(os.dup(fd), "w") as stream:
            stream.write(
                "".join(
                    f"vpn.secrets.{key}:{value}\n" for key, value in secrets.items()
                )
            )
        os.lseek(fd, 0, os.SEEK_SET)
        if on_progress is not None:
            on_progress("tifr VPN: starting NetworkManager tunnel")
        _run(
            [
                "--wait",
                "90",
                "connection",
                "up",
                "uuid",
                uuid,
                "passwd-file",
                f"/proc/self/fd/{fd}",
            ],
            pass_fds=(fd,),
            on_progress=on_progress,
        )
    finally:
        os.close(fd)


def deactivate(uuid, *, on_progress=None):
    _run(["--wait", "20", "connection", "down", "uuid", uuid], on_progress=on_progress)
