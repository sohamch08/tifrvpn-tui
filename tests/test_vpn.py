"""Public API state transitions with fake NetworkManager and sign-in services."""

import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from tifrvpn import vpn
from tifrvpn.errors import AuthenticationError, NetworkManagerError, ProfileNotFound


class VPNTests(unittest.TestCase):
    def setUp(self):
        self.nm = Mock()
        self.nm.profile_uuid.return_value = "profile-uuid"
        self.nm.state.return_value = "deactivated"
        self.nm.details.return_value = (
            "GENERAL.DEVICES: tun0\nIP4.ADDRESS[1]: 10.0.0.2/24"
        )
        self.keyring = Mock()
        self.keyring.load_session.return_value = None
        self.auth = Mock()
        self.auth.authenticate.return_value = "DSID=example-session"
        for name, value in [
            ("nm", self.nm),
            ("keyring", self.keyring),
            ("auth", self.auth),
        ]:
            patcher = patch.object(vpn, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_valid_saved_session_bypasses_credentials_and_browser(self):
        self.keyring.load_session.return_value = "DSID=example-saved"
        self.auth.valid_session.return_value = True
        self.nm.state.side_effect = ["deactivated", "activated"]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = vpn.connect(quiet=True)
        self.assertTrue(result.connected)
        self.assertTrue(result.changed)
        self.assertEqual(result.devices, ("tun0",))
        self.auth.authenticate.assert_not_called()
        self.nm.activate.assert_called_once_with(
            "profile-uuid", "DSID=example-saved", on_progress=None
        )
        self.assertEqual(out.getvalue() + err.getvalue(), "")

    def test_expired_session_is_cleared_before_signin_and_new_session_saved(self):
        self.keyring.load_session.return_value = "DSID=example-expired"
        self.auth.valid_session.return_value = False
        self.nm.state.side_effect = ["deactivated", "activated"]
        sequence = Mock()
        sequence.attach_mock(self.keyring.clear_session, "clear")
        sequence.attach_mock(self.auth.authenticate, "authenticate")
        sequence.attach_mock(self.keyring.save_session, "save")
        sequence.attach_mock(self.nm.activate, "activate")
        events = []
        config = object()
        result = vpn.connect(config=config, quiet=True, on_progress=events.append)
        self.assertTrue(result.connected)
        self.assertEqual(
            [call[0] for call in sequence.mock_calls],
            ["clear", "authenticate", "save", "activate"],
        )
        self.auth.authenticate.assert_called_once_with(
            quiet=True, config=config, on_progress=events.append
        )
        self.assertTrue(any("expired" in event for event in events))
        self.assertNotIn("example-session", "\n".join(events))

    def test_already_connected_never_signs_in_or_activates_again(self):
        self.nm.state.return_value = "activated"
        result = vpn.connect()
        self.assertTrue(result.connected)
        self.assertFalse(result.changed)
        self.keyring.load_session.assert_not_called()
        self.nm.activate.assert_not_called()

    def test_busy_connection_fails_before_credentials(self):
        self.nm.state.return_value = "activating"
        with self.assertRaisesRegex(NetworkManagerError, "wait or run tifrvpn -d"):
            vpn.connect()
        self.keyring.load_session.assert_not_called()

    def test_missing_profile_is_created(self):
        self.nm.profile_uuid.side_effect = [ProfileNotFound("missing"), "new-uuid"]
        self.nm.setup_profile.return_value = "new-uuid"
        self.nm.state.side_effect = ["deactivated", "activated"]
        result = vpn.connect()
        self.assertEqual(result.profile_uuid, "new-uuid")
        self.nm.setup_profile.assert_called_once_with(on_progress=None)
        self.nm.activate.assert_called_once_with(
            "new-uuid", "DSID=example-session", on_progress=None
        )

    def test_ambiguous_profile_never_creates_another(self):
        self.nm.profile_uuid.side_effect = NetworkManagerError("expected one")
        with self.assertRaises(NetworkManagerError):
            vpn.connect()
        self.nm.setup_profile.assert_not_called()

    def test_authentication_failure_never_activates(self):
        self.auth.authenticate.side_effect = AuthenticationError("cancelled")
        with self.assertRaises(AuthenticationError):
            vpn.connect()
        self.nm.activate.assert_not_called()
        self.keyring.save_session.assert_not_called()

    def test_failed_activation_is_not_reported_as_connected(self):
        self.nm.activate.side_effect = NetworkManagerError("failed", returncode=10)
        with self.assertRaises(NetworkManagerError) as result:
            vpn.connect()
        self.assertEqual(result.exception.returncode, 10)

    def test_disconnect_handles_missing_inactive_and_active_profiles(self):
        self.nm.profile_uuid.side_effect = ProfileNotFound("missing")
        self.assertEqual(vpn.disconnect().state, "not-configured")
        self.nm.profile_uuid.side_effect = None
        for state, changed in [
            ("", False),
            ("deactivated", False),
            ("activated", True),
            ("activating", True),
        ]:
            with self.subTest(state=state):
                self.nm.state.return_value = state
                self.nm.deactivate.reset_mock()
                result = vpn.disconnect()
                self.assertFalse(result.connected)
                self.assertEqual(result.changed, changed)
                self.assertEqual(self.nm.deactivate.called, changed)
