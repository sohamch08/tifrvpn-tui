"""Command dispatch and output checks, without accessing desktop services."""

import contextlib
import io
import unittest
from unittest.mock import patch

from tifrvpn import cli
from tifrvpn import networkmanager as nm
from tifrvpn.errors import NetworkManagerError
from tifrvpn.vpn import VPNStatus


class CLITests(unittest.TestCase):
    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_option_order_and_forwarding(self):
        for args, quiet in [
            (["-c", "--quiet"], True),
            (["--quiet", "-c"], True),
            (["--quiet"], True),
            (["-c"], False),
        ]:
            with (
                self.subTest(args=args),
                patch.object(
                    cli.vpn, "connect", return_value=VPNStatus("activated")
                ) as connect,
            ):
                self.assertEqual(self.run_cli(args)[0], 0)
                connect.assert_called_once_with(quiet=quiet, on_progress=cli._progress)
        with patch.object(
            cli.vpn, "disconnect", return_value=VPNStatus("deactivated")
        ) as disconnect:
            self.assertEqual(self.run_cli(["-d"])[0], 0)
            disconnect.assert_called_once()
        with patch.object(
            cli.vpn, "status", return_value=VPNStatus("activated")
        ) as status:
            self.assertEqual(self.run_cli(["-s"])[0], 0)
            status.assert_called_once()

    def test_invalid_options_fail_before_any_operations(self):
        for args in (
            ["--quiet", "-d"],
            ["-s", "--quiet"],
            ["--quiet", "--setup"],
            ["-c", "-s"],
            ["--unknown"],
            ["-h", "--quiet"],
            ["-c", "-c"],
        ):
            with self.subTest(args=args), patch.object(cli.vpn, "connect") as connect:
                code, out, err = self.run_cli(args)
                self.assertEqual(code, 2)
                self.assertEqual(out, "")
                self.assertTrue(err)
                connect.assert_not_called()

    def test_help_needs_no_networkmanager(self):
        with patch.object(cli.vpn, "status", side_effect=AssertionError("called")):
            for args in (["--help"], ["-h"]):
                code, out, err = self.run_cli(args)
                self.assertEqual((code, out, err), (0, cli.HELP + "\n", ""))

    def test_toggle_preserves_transitional_state_behavior(self):
        for state, connects in [
            ("activated", False),
            ("activating", False),
            ("deactivated", True),
            ("", True),
        ]:
            with (
                self.subTest(state=state),
                patch.object(nm, "require_available"),
                patch.object(nm, "profile_uuid", return_value="profile"),
                patch.object(nm, "state", return_value=state),
                patch.object(cli, "_connect", return_value=0) as connect,
                patch.object(cli, "_disconnect", return_value=0) as disconnect,
            ):
                self.assertEqual(self.run_cli([])[0], 0)
                self.assertEqual(connect.called, connects)
                self.assertEqual(disconnect.called, not connects)

    def test_status_exit_codes_and_details(self):
        for result, expected in [
            (VPNStatus("not-configured"), 1),
            (VPNStatus("deactivated"), 1),
            (VPNStatus("activating"), 1),
            (VPNStatus("activated", details="GENERAL.DEVICES: tun0"), 0),
        ]:
            with (
                self.subTest(state=result.state),
                patch.object(cli.vpn, "status", return_value=result),
            ):
                code, out, err = self.run_cli(["-s"])
                self.assertEqual(code, expected)
                self.assertEqual(err, "")
                if result.connected:
                    self.assertIn(result.details, out)

    def test_failure_exit_code_is_preserved(self):
        with patch.object(
            cli.vpn, "connect", side_effect=NetworkManagerError("failed", returncode=10)
        ):
            self.assertEqual(self.run_cli(["-c"]), (10, "", "tifr VPN: failed\n"))

    def test_connect_notification_only_when_tunnel_was_started(self):
        for changed in (False, True):
            with (
                patch.object(
                    cli.vpn,
                    "connect",
                    return_value=VPNStatus("activated", changed=changed),
                ),
                patch.object(cli, "_notify") as notify,
            ):
                self.assertEqual(self.run_cli(["-c"])[0], 0)
                self.assertEqual(notify.called, changed)

    def test_otp_does_not_dump_unexpected_error_details(self):
        with (
            patch.object(
                cli, "load_config", side_effect=OSError("example-master-password")
            ),
            contextlib.redirect_stderr(io.StringIO()) as output,
        ):
            self.assertEqual(cli.otp_main([]), 1)
        self.assertNotIn("example-master-password", output.getvalue())
