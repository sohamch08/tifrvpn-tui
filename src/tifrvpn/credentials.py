"""KeePassXC/GPG access; passwords and codes are returned only in memory."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import Config, load_config
from .errors import CredentialError


def validate_config(config: Config) -> None:
    if not config.database.is_file():
        raise CredentialError(
            f"Database not found: {config.database}. Set TIFR_KEEPASS_DATABASE to its path."
        )
    if not shutil.which("gpg"):
        raise CredentialError("GPG is required.")


def keepass_command(database, entry):
    if shutil.which("keepassxc-cli"):
        command = ["keepassxc-cli"]
    elif shutil.which("flatpak"):
        command = [
            "flatpak",
            "run",
            "--command=keepassxc-cli",
            "org.keepassxc.KeePassXC",
        ]
    else:
        raise CredentialError("Install KeePassXC or its Flatpak first.")
    return command + ["show", "--quiet", "--totp", str(database), entry]


def read_code(password, database, entry):
    if any(char in password for char in "\r\n\0"):
        raise CredentialError("The database password must be a single line.")
    result = subprocess.run(
        keepass_command(database, entry),
        check=False,
        input=password + "\n",
        capture_output=True,
        text=True,
    )
    code = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9]{6,8}", code):
        raise CredentialError(
            "Could not unlock KeePassXC or read the entry's TOTP. Check the password, database and entry name."
        )
    return code


def read_login(password, database, entry):
    """Return login fields in memory; never expose them as CLI output."""
    if any(char in password for char in "\r\n\0"):
        raise CredentialError("The database password must be a single line.")
    command = keepass_command(database, entry)
    # Explicitly request the protected value, captured only in this process.
    command = (
        command[:-2]
        + ["--show-protected", "-a", "UserName", "-a", "Password"]
        + command[-2:]
    )
    result = subprocess.run(
        command, check=False, input=password + "\n", capture_output=True, text=True
    )
    fields = result.stdout.splitlines()
    if (
        result.returncode
        or len(fields) != 3
        or not re.fullmatch(r"[0-9]{6,8}", fields[2])
    ):
        raise CredentialError("Could not read the KeePassXC login entry and TOTP.")
    if not fields[0].strip() or not fields[1]:
        raise CredentialError(
            "Fill the Username and Password fields of the TIFR entry in KeePassXC, then save the database."
        )
    return {"username": fields[0].strip(), "password": fields[1]}


def decrypt_password(password_file, *, allow_prompt=True):
    if not password_file.is_file():
        raise CredentialError(
            "Encrypted password file not found. Run tifr-otp --setup first."
        )
    if sys.stdin.isatty():
        os.environ["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    command = ["gpg", "--quiet"]
    if not allow_prompt:
        # A pinentry window on Xvfb would be invisible. Fail instead of waiting.
        command += ["--batch", "--no-tty", "--pinentry-mode", "error"]
    decrypted = subprocess.run(
        command + ["--decrypt", "--", str(password_file)],
        check=False,
        capture_output=True,
    )
    if decrypted.returncode:
        raise CredentialError(
            "Could not decrypt the password file. Unlock your GPG key and retry."
        )
    return decrypted.stdout.decode("utf-8").removesuffix("\n").removesuffix("\r")


def recipient_key(explicit):
    if explicit:
        return explicit
    result = subprocess.run(
        ["gpg", "--batch", "--with-colons", "--list-secret-keys", "--fingerprint"],
        capture_output=True,
        text=True,
        check=True,
    )
    keys = []
    eligible = False
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if parts[0] == "sec":
            eligible = parts[1] not in ("r", "e", "d") and "e" in parts[11].lower()
        elif parts[0] == "ssb":
            eligible = False
        elif parts[0] == "fpr" and eligible:
            keys.append(parts[9])
            eligible = False
    if len(keys) != 1:
        raise CredentialError(
            "Specify your GPG encryption key: tifr-otp --setup --recipient FINGERPRINT"
        )
    return keys[0]


def save_password(password, password_file, recipient):
    """Encrypt and atomically save a verified database password."""
    result = subprocess.run(
        ["gpg", "--batch", "--encrypt", "--recipient", recipient, "--output", "-"],
        check=False,
        input=password.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode or not result.stdout:
        raise CredentialError(
            "GPG encryption failed; no password file was written. Check the recipient key."
        )
    password_file.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if password_file.parent == Path.home() / ".local/share/tifr-vpn":
        password_file.parent.chmod(0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=password_file.parent, prefix=".keepass-password-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(result.stdout)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, password_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def get_code(*, config: Config | None = None) -> str:
    """Return the current KeePassXC TOTP; GPG can prompt to unlock its key."""
    config = config if config is not None else load_config()
    validate_config(config)
    password = decrypt_password(config.password_file)
    return read_code(password, config.database, config.entry)
