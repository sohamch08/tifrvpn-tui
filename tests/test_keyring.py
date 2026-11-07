"""Exercise Secret Service adapters without accessing a real desktop keyring."""

import contextlib
import io
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

from tifrvpn import keyring
from tifrvpn.config import URL
from tifrvpn.errors import AuthenticationError


class KeyringTests(unittest.TestCase):
    def setUp(self):
        self.secret = Mock()
        gi = ModuleType("gi")
        gi.require_version = Mock()
        repository = ModuleType("gi.repository")
        repository.Secret = self.secret
        patcher = patch.dict(sys.modules, {"gi": gi, "gi.repository": repository})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_load_and_store_use_the_existing_schema_and_server(self):
        self.secret.password_lookup_sync.return_value = "DSID=example"
        self.assertEqual(keyring.load_session(), "DSID=example")
        schema = self.secret.Schema.new.return_value
        self.secret.Schema.new.assert_called_with(
            "in.res.tifr.vpn",
            self.secret.SchemaFlags.NONE,
            {
                "server": self.secret.SchemaAttributeType.STRING,
                "kind": self.secret.SchemaAttributeType.STRING,
            },
        )
        self.secret.password_lookup_sync.assert_called_once_with(
            schema, {"server": URL, "kind": "session"}, None
        )
        keyring.save_session("DSID=example")
        self.secret.password_store_sync.assert_called_once_with(
            schema,
            {"server": URL, "kind": "session"},
            self.secret.COLLECTION_DEFAULT,
            "TIFR VPN session",
            "DSID=example",
            None,
        )

    def test_browser_state_uses_a_separate_key(self):
        keyring.load_browser_state()
        self.assertEqual(
            self.secret.password_lookup_sync.call_args.args[1],
            {"server": URL, "kind": "browser"},
        )
        keyring.save_browser_state("[]")
        self.assertEqual(
            self.secret.password_store_sync.call_args.args[1],
            {"server": URL, "kind": "browser"},
        )

    def test_forgetting_clears_both_kinds(self):
        keyring.clear_saved_login()
        self.assertEqual(
            [
                call.args[1]["kind"]
                for call in self.secret.password_clear_sync.call_args_list
            ],
            ["session", "browser"],
        )

    def test_backend_errors_do_not_expose_secret_values(self):
        self.secret.password_lookup_sync.side_effect = RuntimeError(
            "DSID=example-sensitive"
        )
        events = []
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            self.assertIsNone(keyring.load_session(on_progress=events.append))
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(len(events), 1)
        self.assertNotIn("example-sensitive", events[0])

    def test_clear_failure_is_reported_after_trying_both_kinds(self):
        self.secret.password_clear_sync.side_effect = [
            RuntimeError("unavailable"),
            True,
        ]
        with self.assertRaises(AuthenticationError):
            keyring.clear_saved_login()
        self.assertEqual(self.secret.password_clear_sync.call_count, 2)
