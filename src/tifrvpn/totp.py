"""Decode a single-account Google Authenticator export and calculate TOTP."""

import base64
import hashlib
import hmac
import struct
import time
from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit


def _fields(data: bytes) -> Iterator[tuple[int, int | bytes]]:
    offset = 0

    def varint() -> int:
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

    value: int | bytes
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


def decode_export(text: str):
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
        number == 3 and (not isinstance(value, int) or value > 1)
        for number, value in payload
    ):
        raise ValueError("Export only the TIFR entry, then scan the new QR.")
    account_data = accounts[0]
    if not isinstance(account_data, bytes):
        raise ValueError("Invalid export QR.")  # noqa: TRY004 - Malformed QR data.
    account = dict(_fields(account_data))
    secret = account.get(1)
    if not isinstance(secret, bytes) or not secret:
        raise ValueError("The export contains no setup key.")
    name = account.get(2, b"")
    issuer = account.get(3, b"")
    if not isinstance(name, bytes) or not isinstance(issuer, bytes):
        raise ValueError("Invalid export QR.")  # noqa: TRY004 - Malformed QR data.
    algorithms = {1: "SHA1", 2: "SHA256", 3: "SHA512"}
    digits = {1: 6, 2: 8}
    algorithm = account.get(4)
    digit_format = account.get(5)
    if (
        account.get(6) != 2
        or not isinstance(algorithm, int)
        or algorithm not in algorithms
        or not isinstance(digit_format, int)
        or digit_format not in digits
    ):
        raise ValueError(
            "This export is not a supported time-based authenticator entry."
        )
    return {
        "secret": base64.b32encode(secret).decode().rstrip("="),
        "name": name.decode("utf-8"),
        "issuer": issuer.decode("utf-8"),
        "algorithm": algorithms[algorithm],
        "digits": digits[digit_format],
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
