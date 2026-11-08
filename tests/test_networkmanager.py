"""Backend checks with mocked commands and TLS, using no live services."""

import os
import subprocess
import unittest
from unittest.mock import Mock, patch

from cryptography import x509

from tifrvpn import networkmanager as nm
from tifrvpn.errors import NetworkManagerError, ProfileNotFound


class NetworkManagerTests(unittest.TestCase):
    def test_duplicate_profile_is_rejected(self):
        with (
            patch.object(
                nm.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, "one\ntwo\n", ""),
            ),
            self.assertRaisesRegex(NetworkManagerError, "expected one"),
        ):
            nm.profile_uuid()

    def test_existing_incompatible_profile_is_not_modified(self):
        with (
            patch.object(nm, "require_available"),
            patch.object(nm, "profile_uuid", return_value="profile"),
            patch.object(nm, "_run", return_value="different-plugin") as run,
            self.assertRaisesRegex(NetworkManagerError, "different VPN plugin"),
        ):
            nm.setup_profile()
        self.assertEqual(run.call_count, 1)

    def test_missing_profile_is_created_with_original_flags(self):
        with (
            patch.object(nm, "require_available"),
            patch.object(
                nm,
                "profile_uuid",
                side_effect=[ProfileNotFound("missing"), "new-profile"],
            ),
            patch.object(nm, "_run", side_effect=["other-profile", "created"]) as run,
        ):
            self.assertEqual(nm.setup_profile(), "new-profile")
        args = run.call_args.args[0]
        self.assertIn("connection.permissions", args)
        self.assertEqual(args[-2:], ["vpn.data", nm.VPN_DATA])
        self.assertIn("prevent_invalid_cert=yes", args[-1])
        self.assertIn("cookie-flags=2", args[-1])
        self.assertIn("connection.autoconnect", args)

    def test_ambiguous_missing_lookup_cannot_create_duplicate(self):
        with (
            patch.object(nm, "require_available"),
            patch.object(nm, "profile_uuid", side_effect=ProfileNotFound("missing")),
            patch.object(nm, "_run", return_value="tifr-ivanti\nother") as run,
            self.assertRaisesRegex(NetworkManagerError, "ambiguous"),
        ):
            nm.setup_profile()
        self.assertEqual(run.call_count, 1)

    def test_profile_gateway_and_protocol_are_validated(self):
        for gateway, protocol, valid in [
            (nm.URL, "nc", True),
            ("https://example.com", "nc", False),
            (nm.URL, "anyconnect", False),
        ]:
            with (
                self.subTest(gateway=gateway, protocol=protocol),
                patch.object(
                    nm,
                    "_run",
                    side_effect=[
                        "org.freedesktop.NetworkManager.openconnect",
                        f"gateway = {gateway}, protocol = {protocol}",
                    ],
                ),
            ):
                if valid:
                    nm.validate_profile("profile")
                else:
                    with self.assertRaisesRegex(
                        NetworkManagerError, "Profile settings differ"
                    ):
                        nm.validate_profile("profile")

    def test_command_failure_preserves_exit_status(self):
        result = subprocess.CompletedProcess([], 10, "", "NetworkManager failure\n")
        with (
            patch.object(nm.subprocess, "run", return_value=result),
            self.assertRaises(NetworkManagerError) as raised,
        ):
            nm.deactivate("profile")
        self.assertEqual(raised.exception.returncode, 10)

    def test_session_secrets_use_only_an_inherited_memory_file(self):
        connection = Mock()
        connection.__enter__ = Mock(return_value=connection)
        connection.__exit__ = Mock(return_value=False)
        tls = Mock()
        tls.__enter__ = Mock(return_value=tls)
        tls.__exit__ = Mock(return_value=False)
        tls.getpeercert.return_value = b"mock-certificate"
        tls.getpeername.return_value = ("192.0.2.1", 443)
        context = Mock()
        context.wrap_socket.return_value = tls
        cert = Mock()
        cert.public_key.return_value.public_bytes.return_value = b"example-public-key"
        captured = {}

        def activate(arguments, **kwargs):
            (fd,) = kwargs["pass_fds"]
            captured["fd"] = fd
            self.assertEqual(arguments[-1], f"/proc/self/fd/{fd}")
            self.assertNotIn("DSID=example-session", repr(arguments))
            payload = os.read(fd, 8192).decode()
            self.assertIn("vpn.secrets.cookie:DSID=example-session\n", payload)
            self.assertIn("vpn.secrets.resolve:sslvpn.tifr.res.in:192.0.2.1\n", payload)
            self.assertIn("vpn.secrets.gwcert:pin-sha256:", payload)
            raise NetworkManagerError("fake activation failure")

        with (
            patch.object(nm.socket, "create_connection", return_value=connection),
            patch.object(nm.ssl, "create_default_context", return_value=context),
            patch.object(x509, "load_der_x509_certificate", return_value=cert),
            patch.object(nm, "_run", side_effect=activate),
            self.assertRaisesRegex(NetworkManagerError, "fake activation failure"),
        ):
            nm.activate("profile", "DSID=example-session")
        with self.assertRaises(OSError):
            os.fstat(captured["fd"])
        context.wrap_socket.assert_called_once_with(connection, server_hostname=nm.HOST)
