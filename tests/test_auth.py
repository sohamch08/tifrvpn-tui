"""Authentication protocol checks without a real gateway or browser."""

import io
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from tifrvpn import auth
from tifrvpn.config import Config
from tifrvpn.errors import AuthenticationError


class AuthTests(unittest.TestCase):
    def test_custom_configuration_reaches_worker_without_changing_parent(self):
        config = Config(
            Path("/example/custom.kdbx"), Path("/example/master.gpg"), "VPN/custom"
        )
        with (
            patch.object(
                auth.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, "DSID=example"),
            ) as run,
            patch.dict(
                os.environ,
                {"TIFR_KEEPASS_ENTRY": "original", "PYTHONPATH": "/example/path"},
            ),
        ):
            self.assertEqual(auth.authenticate(config=config), "DSID=example")
            self.assertEqual(os.environ["TIFR_KEEPASS_ENTRY"], "original")
        command = run.call_args.args[0]
        self.assertEqual(command[1:], ["-m", "tifrvpn._sso_worker"])
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["TIFR_KEEPASS_ENTRY"], "VPN/custom")
        self.assertEqual(env["TIFR_KEEPASS_DATABASE"], "/example/custom.kdbx")
        self.assertEqual(env["PYTHONPATH"], "/example/path")

    def test_malformed_worker_output_never_becomes_a_session(self):
        for value in ("", "example", "DSID=example\nother", "DSID=example\0"):
            with (
                self.subTest(value=value),
                patch.object(
                    auth.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, value),
                ),
                self.assertRaisesRegex(AuthenticationError, "Invalid SSO session"),
            ):
                auth.authenticate()

    def test_failure_does_not_expose_worker_stdout(self):
        with (
            patch.object(
                auth.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 1, "DSID=example-sensitive"
                ),
            ),
            self.assertRaises(AuthenticationError) as result,
        ):
            auth.authenticate()
        self.assertNotIn("example-sensitive", str(result.exception))

    def test_session_validation_statuses(self):
        for code, location, expected in [
            (302, "/dana/home/welcome.cgi", True),
            (302, "https://sso.tifr.res.in/login", False),
            (302, "/login", False),
            (401, "", False),
            (403, "", False),
        ]:
            with self.subTest(code=code, location=location):
                opener = Mock()
                error = HTTPError(
                    "https://example",
                    code,
                    "test",
                    {"Location": location},
                    io.BytesIO(),
                )
                self.addCleanup(error.close)
                opener.open.side_effect = error
                with patch.object(auth, "build_opener", return_value=opener):
                    self.assertEqual(auth.valid_session("DSID=example"), expected)
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=Mock(status=200))
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(auth, "build_opener", return_value=opener):
            self.assertTrue(auth.valid_session("DSID=example"))
