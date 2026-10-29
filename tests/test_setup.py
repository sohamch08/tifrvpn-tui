"""Offline packaging/configuration checks; no real vault, keyring or VPN access."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OTP = runpy.run_path(str(ROOT / "tifr-otp.py"))
QR = runpy.run_path(str(ROOT / "tifr-import-totp.py"))


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifr setup ")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.home))
        for name in ("TIFR_INSTALL_DIR", "TIFR_COMMAND_DIR", "XDG_CONFIG_HOME",
                     "TIFR_KEEPASS_DATABASE", "TIFR_KEEPASS_ENTRY", "TIFR_KEEPASS_PASSWORD_FILE"):
            self.environment.pop(name, None)

    def install(self):
        return subprocess.run([str(ROOT / "install.sh")], cwd="/", env=self.environment,
                              capture_output=True, text=True)

    def test_install_from_another_directory_and_command_symlinks(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("tifrvpn", "tifr-otp", "tifr-import-totp"):
            executable = self.home / ".local/bin" / command
            self.assertTrue(executable.is_symlink())
            result = subprocess.run([str(executable), "--help"], cwd="/", env=self.environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".zshrc").exists())
        self.assertEqual(self.install().returncode, 0)

    def test_unrelated_command_is_preserved_before_any_copy(self):
        command = self.home / ".local/bin/tifrvpn"
        command.parent.mkdir(parents=True)
        command.write_text("existing command")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(command.read_text(), "existing command")
        self.assertFalse((self.home / "bin/tifr").exists())

    def test_custom_install_locations(self):
        self.environment.update(TIFR_INSTALL_DIR=str(self.home / "custom helpers"),
                                TIFR_COMMAND_DIR=str(self.home / "custom commands"))
        self.assertEqual(self.install().returncode, 0)
        command = self.home / "custom commands/tifrvpn"
        self.assertEqual(command.resolve(), self.home / "custom helpers/tifrvpn")

    def configure(self, settings):
        config = self.home / ".config/tifr-vpn/config.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(settings))

    def test_default_and_configured_paths_and_environment_override(self):
        database = self.home / "Documents/KeePass/Passwords.kdbx"
        database.parent.mkdir(parents=True)
        database.touch()
        with patch.dict(os.environ, self.environment, clear=True):
            self.assertEqual(OTP["configuration"]()[0], database)
            self.configure({"database": str(database), "entry": "VPN/TIFR",
                            "password_file": "~/private/master.gpg"})
            self.assertEqual(OTP["configuration"]()[1:],
                             (self.home / "private/master.gpg", "VPN/TIFR"))
            with patch.dict(os.environ, {"TIFR_KEEPASS_ENTRY": "Other/TIFR"}):
                self.assertEqual(OTP["configuration"]()[2], "Other/TIFR")

    def test_bad_config_is_rejected(self):
        for settings in ([], {"database": 42}, {"entry": ""}, {"unknown": "value"},
                         {"database": "relative.kdbx"}):
            with self.subTest(settings=settings), patch.dict(os.environ, self.environment, clear=True):
                self.configure(settings)
                with self.assertRaises(RuntimeError):
                    OTP["configuration"]()

    def test_login_parser_keeps_fields_out_of_output(self):
        result = subprocess.CompletedProcess([], 0, "example-user\nexample-password\n123456\n", "")
        output = io.StringIO()
        with patch("shutil.which", return_value="/usr/bin/keepassxc-cli"), \
                patch("subprocess.run", return_value=result) as run, \
                contextlib.redirect_stdout(output):
            login = OTP["read_login"]("example-master", Path("example.kdbx"), "TIFR")
        self.assertEqual(login, {"username": "example-user", "password": "example-password"})
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn("example-master", run.call_args.args[0])
        self.assertIn("--show-protected", run.call_args.args[0])

    def test_missing_login_fields_are_rejected(self):
        result = subprocess.CompletedProcess([], 0, "example-user\n\n123456\n", "")
        with patch("shutil.which", return_value="/usr/bin/keepassxc-cli"), \
                patch("subprocess.run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "Username and Password"):
                OTP["read_login"]("example-master", Path("example.kdbx"), "TIFR")

    def test_totp_against_public_rfc6238_vector(self):
        # Public RFC test key; never use it for a real account.
        account = {"secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", "period": 30,
                   "algorithm": "SHA1", "digits": 8}
        self.assertEqual(QR["current_code"](account, timestamp=59), "94287082")


if __name__ == "__main__":
    unittest.main()
