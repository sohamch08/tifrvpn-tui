"""Export decoding checks using a public test key and malformed field types."""

import base64
import unittest
from urllib.parse import urlencode

from tifrvpn.totp import current_code, decode_export


# Public RFC 6238 test key, followed by SHA1, six digits and TOTP fields.
ACCOUNT = b"\x0a\x1412345678901234567890\x20\x01\x28\x01\x30\x02"


def export_url(payload):
    query = urlencode({"data": base64.b64encode(payload).decode("ascii")})
    return f"otpauth-migration://offline?{query}"


def account_payload(account):
    return b"\x0a" + bytes([len(account)]) + account


class ExportTests(unittest.TestCase):
    def test_decode_without_optional_metadata_and_generate_code(self):
        account = decode_export(export_url(account_payload(ACCOUNT)))
        self.assertEqual(
            account,
            {
                "secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
                "name": "",
                "issuer": "",
                "algorithm": "SHA1",
                "digits": 6,
                "period": 30,
            },
        )
        self.assertEqual(current_code(account, timestamp=59), "287082")

    def test_decode_with_metadata_and_single_export_batch(self):
        account = ACCOUNT + b"\x12\x04TIFR\x1a\x03VPN"
        decoded = decode_export(export_url(account_payload(account) + b"\x18\x01"))
        self.assertEqual(decoded["name"], "TIFR")
        self.assertEqual(decoded["issuer"], "VPN")

    def test_wrong_field_types_and_multiple_batches_raise_value_error(self):
        payloads = {
            "integer account": b"\x08\x01",
            "integer secret": account_payload(ACCOUNT + b"\x08\x01"),
            "integer name": account_payload(ACCOUNT + b"\x10\x01"),
            "integer issuer": account_payload(ACCOUNT + b"\x18\x01"),
            "byte algorithm": account_payload(ACCOUNT + b"\x22\x01x"),
            "byte digits": account_payload(ACCOUNT + b"\x2a\x01x"),
            "byte OTP type": account_payload(ACCOUNT + b"\x32\x01x"),
            "byte batch size": account_payload(ACCOUNT) + b"\x1a\x01x",
            "multiple batches": account_payload(ACCOUNT) + b"\x18\x02",
        }
        for name, payload in payloads.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                decode_export(export_url(payload))


if __name__ == "__main__":
    unittest.main()
