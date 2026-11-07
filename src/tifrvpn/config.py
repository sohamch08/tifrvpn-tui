"""Load settings without opening a vault or requiring runtime programs."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .errors import ConfigurationError

URL = "https://sslvpn.tifr.res.in/tifruser"
HOST = "sslvpn.tifr.res.in"


@dataclass(frozen=True)
class Config:
    database: Path
    password_file: Path
    entry: str = "TIFR"

    def __post_init__(self):
        object.__setattr__(self, "database", Path(self.database).expanduser())
        object.__setattr__(self, "password_file", Path(self.password_file).expanduser())
        if (
            not self.database.is_absolute()
            or not self.password_file.is_absolute()
            or not self.entry.strip()
        ):
            raise ConfigurationError(
                "Use absolute paths (or ~/ paths) and a nonempty KeePassXC entry name."
            )


def load_config() -> Config:
    """Load defaults, optional JSON settings, and TIFR_KEEPASS_* overrides."""
    config_path = (
        Path(
            os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        ).expanduser()
        / "tifr-vpn/config.json"
    )
    try:
        settings = json.loads(config_path.read_text()) if config_path.exists() else {}
    except (OSError, ValueError):
        raise ConfigurationError(
            f"Could not read valid JSON configuration: {config_path}"
        ) from None
    if (
        not isinstance(settings, dict)
        or set(settings) - {"database", "password_file", "entry"}
        or any(
            not isinstance(value, str) or not value.strip()
            for value in settings.values()
        )
    ):
        raise ConfigurationError(
            "Configuration accepts only nonempty database, entry and password_file strings."
        )
    settings = cast(dict[str, str], settings)
    database = Path(
        os.environ.get(
            "TIFR_KEEPASS_DATABASE",
            settings.get("database", "~/Documents/KeePass/Passwords.kdbx"),
        )
    ).expanduser()
    password_file = Path(
        os.environ.get(
            "TIFR_KEEPASS_PASSWORD_FILE",
            settings.get(
                "password_file", "~/.local/share/tifr-vpn/keepass-password.gpg"
            ),
        )
    ).expanduser()
    entry = os.environ.get("TIFR_KEEPASS_ENTRY", settings.get("entry", "TIFR"))
    if (
        not database.is_absolute()
        or not password_file.is_absolute()
        or not entry.strip()
    ):
        raise ConfigurationError(
            "Use absolute paths (or ~/ paths) and a nonempty KeePassXC entry name."
        )
    return Config(database, password_file, entry)
