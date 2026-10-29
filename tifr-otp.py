#!/usr/bin/env python3
"""Read a TIFR TOTP from KeePassXC using a GPG-encrypted database password."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def keepass_command(database, entry):
    if shutil.which("keepassxc-cli"):
        command = ["keepassxc-cli"]
    elif shutil.which("flatpak"):
        command = ["flatpak", "run", "--command=keepassxc-cli", "org.keepassxc.KeePassXC"]
    else:
        raise RuntimeError("Install KeePassXC or its Flatpak first.")
    return command + ["show", "--quiet", "--totp", str(database), entry]


def read_code(password, database, entry):
    if any(char in password for char in "\r\n\0"):
        raise RuntimeError("The database password must be a single line.")
    result = subprocess.run(
        keepass_command(database, entry), input=password + "\n",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    code = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9]{6,8}", code):
        raise RuntimeError("Could not unlock KeePassXC or read the entry's TOTP. Check the password, database and entry name.")
    return code


def read_login(password, database, entry):
    """Return login fields in memory; never expose them as CLI output."""
    if any(char in password for char in "\r\n\0"):
        raise RuntimeError("The database password must be a single line.")
    command = keepass_command(database, entry)
    # Explicitly request the protected value, captured only in this process.
    command = command[:-2] + ["--show-protected", "-a", "UserName", "-a", "Password"] + command[-2:]
    result = subprocess.run(command, input=password + "\n", stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    fields = result.stdout.splitlines()
    if result.returncode or len(fields) != 3 or not re.fullmatch(r"[0-9]{6,8}", fields[2]):
        raise RuntimeError("Could not read the KeePassXC login entry and TOTP.")
    if not fields[0].strip() or not fields[1]:
        raise RuntimeError("Fill the Username and Password fields of the TIFR entry in KeePassXC, then save the database.")
    return {"username": fields[0].strip(), "password": fields[1]}


def configuration():
    config_path = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))).expanduser() / "tifr-vpn/config.json"
    try:
        settings = json.loads(config_path.read_text()) if config_path.exists() else {}
    except (OSError, ValueError):
        raise RuntimeError(f"Could not read valid JSON configuration: {config_path}") from None
    if (not isinstance(settings, dict) or set(settings) - {"database", "password_file", "entry"}
            or any(not isinstance(value, str) or not value.strip() for value in settings.values())):
        raise RuntimeError("Configuration accepts only nonempty database, entry and password_file strings.")
    database = Path(os.environ.get("TIFR_KEEPASS_DATABASE", settings.get("database", "~/Documents/KeePass/Passwords.kdbx"))).expanduser()
    password_file = Path(os.environ.get("TIFR_KEEPASS_PASSWORD_FILE", settings.get("password_file", "~/.local/share/tifr-vpn/keepass-password.gpg"))).expanduser()
    entry = os.environ.get("TIFR_KEEPASS_ENTRY", settings.get("entry", "TIFR"))
    if not database.is_absolute() or not password_file.is_absolute() or not entry.strip():
        raise RuntimeError("Use absolute paths (or ~/ paths) and a nonempty KeePassXC entry name.")
    if not database.is_file():
        raise RuntimeError(f"Database not found: {database}. Set TIFR_KEEPASS_DATABASE to its path.")
    if not shutil.which("gpg"):
        raise RuntimeError("GPG is required.")
    return database, password_file, entry


def decrypt_password(password_file):
    if not password_file.is_file():
        raise RuntimeError("Encrypted password file not found. Run tifr-otp --setup first.")
    if sys.stdin.isatty():
        os.environ["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    decrypted = subprocess.run(
        ["gpg", "--quiet", "--decrypt", "--", str(password_file)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if decrypted.returncode:
        raise RuntimeError("Could not decrypt the password file. Unlock your GPG key and retry.")
    return decrypted.stdout.decode("utf-8").removesuffix("\n").removesuffix("\r")


def recipient_key(explicit):
    if explicit:
        return explicit
    result = subprocess.run(
        ["gpg", "--batch", "--with-colons", "--list-secret-keys", "--fingerprint"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
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
        raise RuntimeError("Specify your GPG encryption key: tifr-otp --setup --recipient FINGERPRINT")
    return keys[0]


def setup(password_file, database, entry, recipient):
    from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

    app = QApplication.instance() or QApplication([])
    if password_file.exists() or password_file.is_symlink():
        answer = QMessageBox.question(
            None, "TIFR OTP setup", f"Replace the encrypted password file?\n{password_file}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return 130
    recipient = recipient_key(recipient)
    while True:
        password, accepted = QInputDialog.getText(
            None, "TIFR OTP — encrypt KeePassXC password",
            f"Enter the MASTER PASSWORD for this KeePassXC database:\n{database}\n\n"
            "It will be verified locally, then encrypted with your GPG key.\n"
            "This is the database password, not your TIFR VPN password.",
            QLineEdit.EchoMode.Password,
        )
        if not accepted:
            return 130
        try:
            read_login(password, database, entry)
        except RuntimeError as error:
            QMessageBox.warning(None, "Could not verify database password", str(error))
            continue
        break
    result = subprocess.run(
        ["gpg", "--batch", "--encrypt", "--recipient", recipient, "--output", "-"],
        input=password.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    password = None
    if result.returncode or not result.stdout:
        raise RuntimeError("GPG encryption failed; no password file was written. Check the recipient key.")
    password_file.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if password_file.parent == Path.home() / ".local/share/tifr-vpn":
        password_file.parent.chmod(0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=password_file.parent, prefix=".keepass-password-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(result.stdout)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, password_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Verified the TOTP entry and saved the GPG-encrypted database password: {password_file}", flush=True)
    QMessageBox.information(None, "TIFR OTP ready", "The encrypted password file is ready.\n\nRun tifr-otp to get the current code.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true", help="prompt locally and encrypt the database password")
    parser.add_argument("--recipient", help="GPG recipient fingerprint for setup")
    args = parser.parse_args()
    if args.recipient and not args.setup:
        parser.error("--recipient requires --setup")
    database, password_file, entry = configuration()
    if args.setup:
        return setup(password_file, database, entry, args.recipient)
    password = decrypt_password(password_file)
    print(read_code(password, database, entry))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTIFR OTP: cancelled.", file=sys.stderr)
        sys.exit(130)
    except RuntimeError as error:
        print(f"TIFR OTP: {error}", file=sys.stderr)
        sys.exit(1)
    except (OSError, UnicodeError, subprocess.SubprocessError, ImportError):
        print("TIFR OTP: operation failed. No password or code was logged.", file=sys.stderr)
        sys.exit(1)
