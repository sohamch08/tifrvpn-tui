"""Quiet-mode checks without accessing a real vault, keyring or VPN."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tifr_auth_test", ROOT / "tifr-vpn-auth.py")
AUTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTH)
OTP_SPEC = importlib.util.spec_from_file_location("tifr_otp_test", ROOT / "tifr-otp.py")
OTP = importlib.util.module_from_spec(OTP_SPEC)
OTP_SPEC.loader.exec_module(OTP)


class QuietAuthenticationTests(unittest.TestCase):
    def test_quiet_unlocks_before_starting_virtual_display(self):
        events = []
        helper = {
            "configuration": lambda: (Path("example.kdbx"), Path("example.gpg"), "TIFR"),
            "decrypt_password": lambda path: events.append("unlock") or "example-master",
        }
        def browser(command):
            events.append("browser")
            self.assertEqual(command[:2], ["xvfb-run", "-a"])
            self.assertEqual(command[-2:], ["--sso-window", "--quiet"])
            self.assertNotIn("example-master", command)
            return subprocess.CompletedProcess(command, 0, "DSID=example-session")
        output = io.StringIO()
        with patch.object(AUTH.shutil, "which", return_value="/example/executable"), \
                patch.object(AUTH.runpy, "run_path", return_value=helper), \
                patch.object(AUTH, "background_browser", side_effect=browser), \
                contextlib.redirect_stderr(output):
            self.assertEqual(AUTH.authenticate(quiet=True), "DSID=example-session")
        self.assertEqual(events, ["unlock", "browser"])
        self.assertNotIn("example-master", output.getvalue())
        self.assertNotIn("example-session", output.getvalue())

    def test_missing_xvfb_fails_before_reading_credentials(self):
        with patch.object(AUTH.shutil, "which", return_value=None), \
                patch.object(AUTH.runpy, "run_path") as helper:
            with self.assertRaisesRegex(RuntimeError, "requires: xvfb-run, Xvfb, xauth"):
                AUTH.authenticate(quiet=True)
            helper.assert_not_called()

    def test_foreground_keeps_existing_browser_path(self):
        result = subprocess.CompletedProcess([], 0, "DSID=example-session")
        with patch.object(AUTH.subprocess, "run", return_value=result) as run, \
                patch.object(AUTH, "background_browser") as background:
            self.assertEqual(AUTH.authenticate(), "DSID=example-session")
            self.assertNotIn("--quiet", run.call_args.args[0])
            background.assert_not_called()

    def test_virtual_display_uses_x11_and_owns_its_process_group(self):
        process = Mock(returncode=0)
        process.communicate.return_value = ("DSID=example-session", None)
        with patch.object(AUTH.subprocess, "Popen", return_value=process) as popen, \
                patch.dict(os.environ, {"WAYLAND_DISPLAY": "wayland-example", "GDK_BACKEND": "wayland"}):
            AUTH.background_browser(["example-browser"])
        options = popen.call_args.kwargs
        self.assertEqual(options["env"]["GDK_BACKEND"], "x11")
        self.assertNotIn("WAYLAND_DISPLAY", options["env"])
        self.assertTrue(options["start_new_session"])
        process.communicate.assert_called_once_with(timeout=120)

    def test_timeout_escalates_cleanup_of_browser_and_display(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [
            subprocess.TimeoutExpired("example-browser", 120),
            subprocess.TimeoutExpired("example-browser", 5),
            ("", None),
        ]
        with patch.object(AUTH.subprocess, "Popen", return_value=process), \
                patch.object(AUTH.os, "killpg") as kill:
            with self.assertRaisesRegex(RuntimeError, "timed out.*Retry tifrvpn -c"):
                AUTH.background_browser(["example-browser"])
        self.assertEqual([call.args for call in kill.call_args_list],
                         [(123456789, signal.SIGTERM), (123456789, signal.SIGKILL)])

    def test_cancel_cleans_up_and_propagates(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [KeyboardInterrupt(), ("", None)]
        with patch.object(AUTH.subprocess, "Popen", return_value=process), \
                patch.object(AUTH.os, "killpg") as kill:
            with self.assertRaises(KeyboardInterrupt):
                AUTH.background_browser(["example-browser"])
        kill.assert_called_once_with(123456789, signal.SIGTERM)

    def test_hidden_gpg_never_opens_a_pinentry_prompt(self):
        with tempfile.NamedTemporaryFile() as password_file:
            result = subprocess.CompletedProcess([], 1, b"", b"example error")
            with patch.object(OTP.subprocess, "run", return_value=result) as run:
                with self.assertRaisesRegex(RuntimeError, "Could not decrypt"):
                    OTP.decrypt_password(Path(password_file.name), allow_prompt=False)
        command = run.call_args.args[0]
        self.assertIn("--batch", command)
        self.assertIn("--no-tty", command)
        self.assertEqual(command[command.index("--pinentry-mode") + 1], "error")


@unittest.skipUnless(shutil.which("zsh"), "Zsh is required for the launcher")
class QuietLauncherTests(unittest.TestCase):
    def test_option_order_and_forwarding_without_real_network_access(self):
        with tempfile.TemporaryDirectory(prefix="tifr quiet ") as temporary:
            directory = Path(temporary)
            # Source just the functions, then override network-dependent helpers.
            source = (ROOT / "tifrvpn").read_text().removesuffix('tifrvpn "$@"\n')
            harness = directory / "launcher.zsh"
            harness.write_text(source + '''
function tifr-on() { print -r -- "connect:$*"; }
function tifr-off() { print -- disconnect; }
function tifr-status() { print -- status; }
tifrvpn "$@"
''')
            for arguments, expected in [
                (["-c", "--quiet"], "connect:--quiet"),
                (["--quiet", "-c"], "connect:--quiet"),
                (["--quiet"], "connect:--quiet"),
                (["-c"], "connect:"),
                (["-d"], "disconnect"),
                (["-s"], "status"),
            ]:
                with self.subTest(arguments=arguments):
                    result = subprocess.run(["zsh", "-f", str(harness), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), expected)
            for arguments in (["--quiet", "-d"], ["-s", "--quiet"],
                              ["--quiet", "--setup"], ["-c", "-s"], ["--unknown"]):
                with self.subTest(arguments=arguments):
                    result = subprocess.run(["zsh", "-f", str(harness), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
