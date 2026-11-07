"""Configuration, credential parsing and TOTP checks without personal data."""

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tifrvpn import credentials as OTP
from tifrvpn import totp as QR
from tifrvpn.config import load_config


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifr setup ")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.home))
        for name in (
            "XDG_CONFIG_HOME",
            "TIFR_KEEPASS_DATABASE",
            "TIFR_KEEPASS_ENTRY",
            "TIFR_KEEPASS_PASSWORD_FILE",
        ):
            self.environment.pop(name, None)

    def configure(self, settings):
        config = self.home / ".config/tifr-vpn/config.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(settings))

    def test_default_and_configured_paths_and_environment_override(self):
        database = self.home / "Documents/KeePass/Passwords.kdbx"
        database.parent.mkdir(parents=True)
        database.touch()
        with patch.dict(os.environ, self.environment, clear=True):
            self.assertEqual(load_config().database, database)
            self.configure(
                {
                    "database": str(database),
                    "entry": "VPN/TIFR",
                    "password_file": "~/private/master.gpg",
                }
            )
            self.assertEqual(
                load_config().password_file, self.home / "private/master.gpg"
            )
            self.assertEqual(load_config().entry, "VPN/TIFR")
            with patch.dict(os.environ, {"TIFR_KEEPASS_ENTRY": "Other/TIFR"}):
                self.assertEqual(load_config().entry, "Other/TIFR")

    def test_bad_config_is_rejected(self):
        for settings in (
            [],
            {"database": 42},
            {"entry": ""},
            {"unknown": "value"},
            {"database": "relative.kdbx"},
        ):
            with (
                self.subTest(settings=settings),
                patch.dict(os.environ, self.environment, clear=True),
            ):
                self.configure(settings)
                with self.assertRaises(RuntimeError):
                    load_config()

    def test_login_parser_keeps_fields_out_of_output(self):
        result = subprocess.CompletedProcess(
            [], 0, "example-user\nexample-password\n123456\n", ""
        )
        output = io.StringIO()
        with (
            patch("shutil.which", return_value="/usr/bin/keepassxc-cli"),
            patch("subprocess.run", return_value=result) as run,
            contextlib.redirect_stdout(output),
        ):
            login = OTP.read_login("example-master", Path("example.kdbx"), "TIFR")
        self.assertEqual(
            login, {"username": "example-user", "password": "example-password"}
        )
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn("example-master", run.call_args.args[0])
        self.assertIn("--show-protected", run.call_args.args[0])

    def test_missing_login_fields_are_rejected(self):
        result = subprocess.CompletedProcess([], 0, "example-user\n\n123456\n", "")
        with (
            patch("shutil.which", return_value="/usr/bin/keepassxc-cli"),
            patch("subprocess.run", return_value=result),
            self.assertRaisesRegex(RuntimeError, "Username and Password"),
        ):
            OTP.read_login("example-master", Path("example.kdbx"), "TIFR")

    def test_totp_against_public_rfc6238_vector(self):
        # Public RFC test key; never use it for a real account.
        account = {
            "secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "period": 30,
            "algorithm": "SHA1",
            "digits": 8,
        }
        self.assertEqual(QR.current_code(account, timestamp=59), "94287082")


if __name__ == "__main__":
    unittest.main()
