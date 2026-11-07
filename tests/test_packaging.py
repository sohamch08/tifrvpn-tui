"""Installed package entry points must work outside the source checkout."""

import os
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifrvpn package ")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.directory))
        self.environment.pop("PYTHONPATH", None)
        self.scripts = Path(sysconfig.get_path("scripts"))

    def run_command(self, arguments):
        return subprocess.run(
            arguments,
            check=False,
            cwd=self.directory,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def test_installed_commands_from_another_directory(self):
        for command in ("tifrvpn", "tifr-otp", "tifr-import-totp"):
            with self.subTest(command=command):
                executable = self.scripts / command
                self.assertTrue(
                    executable.is_file(), f"Install the package first: {executable}"
                )
                result = self.run_command([str(executable), "--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout.lower())
                self.assertEqual(result.stderr, "")

    def test_module_and_worker_from_another_directory(self):
        for module in ("tifrvpn", "tifrvpn._sso_worker"):
            with self.subTest(module=module):
                result = self.run_command(
                    [sys.executable, "-I", "-m", module, "--help"]
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--quiet", result.stdout)
                self.assertEqual(result.stderr, "")

    def test_generated_command_preserves_argument_errors(self):
        result = self.run_command([str(self.scripts / "tifrvpn"), "--quiet", "-d"])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--quiet is only supported when connecting", result.stderr)

    def test_library_import_from_another_directory(self):
        result = self.run_command(
            [
                sys.executable,
                "-I",
                "-c",
                (
                    "from tifrvpn import connect, disconnect, status; "
                    "assert all(callable(function) for function in (connect, disconnect, status))"
                ),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
