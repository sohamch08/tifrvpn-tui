"""Decode a single-account Google Authenticator export and calculate TOTP."""

import base64
import hashlib
import hmac
import struct
import time
from urllib.parse import parse_qs, urlsplit


def _fields(data):
    offset = 0

    def varint():
        nonlocal offset
        value = 0
        for shift in range(0, 70, 7):
            if offset >= len(data):
                raise ValueError("Incomplete export QR.")
            byte = data[offset]
            offset += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                return value
        raise ValueError("Invalid export QR.")

    while offset < len(data):
        tag = varint()
        number, wire = tag >> 3, tag & 7
        if not number:
            raise ValueError("Invalid export QR.")
        if wire == 0:
            value = varint()
        elif wire in (1, 2, 5):
            size = varint() if wire == 2 else (8 if wire == 1 else 4)
            if size > len(data) - offset:
                raise ValueError("Incomplete export QR.")
            value = data[offset : offset + size]
            offset += size
        else:
            raise ValueError("Unsupported export QR format.")
        yield number, value


def decode_export(text):
    uri = urlsplit(text)
    if uri.scheme != "otpauth-migration" or uri.netloc != "offline":
        raise ValueError(
            "Show the Google Authenticator export QR, selecting only TIFR."
        )
    encoded = parse_qs(uri.query).get("data", [""])[0].replace(" ", "+")
    if not encoded or len(encoded) > 32000:
        raise ValueError("Invalid export QR.")
    try:
        payload = list(
            _fields(
                base64.b64decode(encoded + "=" * (-len(encoded) % 4), validate=True)
            )
        )
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        raise ValueError("Could not decode this export QR.") from None
    accounts = [value for number, value in payload if number == 1]
    if len(accounts) != 1 or any(
        number == 3 and value > 1 for number, value in payload
    ):
        raise ValueError("Export only the TIFR entry, then scan the new QR.")
    account = dict(_fields(accounts[0]))
    if not isinstance(account.get(1), bytes) or not account[1]:
        raise ValueError("The export contains no setup key.")
    algorithms = {1: "SHA1", 2: "SHA256", 3: "SHA512"}
    digits = {1: 6, 2: 8}
    if (
        account.get(6) != 2
        or account.get(4) not in algorithms
        or account.get(5) not in digits
    ):
        raise ValueError(
            "This export is not a supported time-based authenticator entry."
        )
    return {
        "secret": base64.b32encode(account[1]).decode().rstrip("="),
        "name": account.get(2, b"").decode("utf-8"),
        "issuer": account.get(3, b"").decode("utf-8"),
        "algorithm": algorithms[account[4]],
        "digits": digits[account[5]],
        "period": 30,
    }


def current_code(account, timestamp=None):
    secret = account["secret"]
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    step = int(time.time() if timestamp is None else timestamp) // account["period"]
    digest = hmac.new(
        key, struct.pack(">Q", step), getattr(hashlib, account["algorithm"].lower())
    ).digest()
    offset = digest[-1] & 15
    value = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
    return str(value % 10 ** account["digits"]).zfill(account["digits"])
