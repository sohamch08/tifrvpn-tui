# TIFR VPN from the terminal

Connect to **https://sslvpn.tifr.res.in/tifruser** with NetworkManager/OpenConnect.
Reuse an existing session, or automatically fill TIFR SSO using a KeePassXC entry
containing your username, password and TOTP setup key.

```sh
tifrvpn -c   # connect
tifrvpn -c --quiet  # connect without showing the SSO browser
tifrvpn -s   # status
tifrvpn -d   # disconnect
```

Unofficial. Tested on Fedora 44 with KeePassXC 2.8 and OpenConnect 9.12. These are terminal controls with a **graphical sign-in window**, not a headless VPN client. You need your own TIFR account and working authenticator enrollment. The official Ivanti client is not required.

## 1. Install dependencies and commands

Install these dependencies using your preferred package manager:

- **Runtime:** Python 3.13 or newer.
- **VPN:** NetworkManager, its OpenConnect VPN plugin, and OpenConnect.
- **Credentials:** KeePassXC (including `keepassxc-cli`), GnuPG, and a pinentry
  program for unlocking your GPG key.
- **Desktop integration:** GTK 3, WebKitGTK 4.1, libsoup 3, libsecret, and their
  GObject introspection bindings, accessible through Python's PyGObject (`gi`).
- **Python packages:** `cryptography` and `PySide6`; also `numpy` and `zxing-cpp`
  if you use the optional Google Authenticator QR importer.
- **Background sign-in (optional):** Xvfb, the `xvfb-run` wrapper, and `xauth`.

Package names vary between distributions. The project's Python dependencies are
declared in `pyproject.toml`. When using a virtual environment with system-installed
PyGObject, create it from system Python with access to system site packages.

NetworkManager must be running. Your desktop must provide a working, unlocked
Secret Service keyring, such as GNOME Keyring. Minimal window-manager sessions
may need desktop keyring and PolicyKit authentication-agent setup first.

From this checkout, run **as your normal user**:

```sh
./install.sh
export PATH="$HOME/.local/bin:$PATH"
```

The installer copies the Python package into `~/bin/tifr/lib/` and thin
compatibility launchers into `~/bin/tifr/`. It links `tifrvpn`, `tifr-otp` and
`tifr-import-totp` into `~/.local/bin/`. Keep that directory on your shell's
`PATH`. No helper needs sourcing; nothing runs at shell startup. Commands use
Python and work independently of your login shell. The installer does not
download Python packages; install the dependencies listed above first.

Re-run `./install.sh` after updating this checkout. Installation directories can
be overridden with `TIFR_INSTALL_DIR` and `TIFR_COMMAND_DIR` (absolute paths).

## 2. Save your own login in KeePassXC

1. Create/open a **password-protected** database. The default location expected
   by these scripts is `~/Documents/KeePass/Passwords.kdbx`.
2. Create an entry named **TIFR**. Fill in your TIFR SSO **Username** and
   **Password**, click **OK** to create the entry, then select it in the list.
3. Right-click the saved entry → **TOTP → Set up TOTP…**. Enter the setup key
   from your TIFR authenticator enrollment. Match the enrollment settings;
   the automatic login helper expects a **30-second** TOTP period.
4. Check that its code matches your phone, then **save the database** (`Ctrl+S`).

Already enrolled only in Google Authenticator? Use the optional local importer:

```sh
tifr-import-totp          # scan using your webcam
# Or, if the webcam is unsuitable:
tifr-import-totp --image  # choose a QR image already on this computer
```

On your phone: **Google Authenticator → Transfer accounts/codes → Export →
select only TIFR**. Scan the export QR with this helper. Copy the resulting setup
key into KeePassXC's TOTP setup dialog and use the displayed settings. It stays
on your computer; the helper does not upload or save decoded keys or camera
frames. If you transferred a QR image, delete that image after importing.
Your phone entry continues to work. Do not post the QR or setup key in issues.

If your database or entry has a different location/name, copy the optional config
and edit it **before continuing**:

```sh
mkdir -p ~/.config/tifr-vpn
cp config.example.json ~/.config/tifr-vpn/config.json
```

`database` and `password_file` accept absolute paths or `~/…`; `entry` is the
KeePassXC entry path, for example `VPN/TIFR`. The config contains paths and names,
not passwords. `$XDG_CONFIG_HOME/tifr-vpn/config.json` is used when set.
Environment variables `TIFR_KEEPASS_DATABASE`, `TIFR_KEEPASS_ENTRY` and
`TIFR_KEEPASS_PASSWORD_FILE` override the corresponding config values.
Key-file and hardware-token database unlocking are not implemented.

## 3. Encrypt the database password with GPG

Use your own encryption-capable GPG key. If you do not have one, create one:

```sh
gpg --full-generate-key
gpg --list-secret-keys --keyid-format long --with-fingerprint
```

Choose a key with encryption support and protect it with a passphrase. Then run:

```sh
tifr-otp --setup
```

If you have multiple keys, choose explicitly with
`tifr-otp --setup --recipient YOUR_KEY_FINGERPRINT`.
The local dialog asks for your **KeePassXC database master password**, verifies
the login entry and TOTP, then encrypts the master password with your GPG key.
The default output is `~/.local/share/tifr-vpn/keepass-password.gpg` (mode `600`).
Your VPN password stays inside the KeePassXC database.

Run `tifr-otp` once to check the generated code against your phone. It prints
the current code to your terminal; don't share that output.

## 4. Connect

```sh
tifrvpn --setup  # create/update the user-specific tifr-ivanti NM profile
tifrvpn -c
```

Run these as your normal desktop user, without `sudo`. NetworkManager may ask
for administrative authorization through your desktop's PolicyKit agent.

A valid saved session connects directly. Otherwise, a browser window opens and
fills the username, password and current authenticator code automatically.
Unlock GPG if prompted. If TIFR reports another active session, choose
**Continue the session** only if you want to disconnect that other session.
The window closes once the authenticated session is handed to NetworkManager.
KeePassXC and your phone do not need to be open for daily connections.

For background sign-in, use `tifrvpn -c --quiet` (or just `tifrvpn --quiet`).
GPG unlocks on your normal desktop first if needed, then the SSO browser runs
on a private Xvfb display. Terminal progress and errors remain visible. If TIFR
requires confirmation or rejects the login, quiet mode stops; retry `tifrvpn -c`
to see the page. Background sign-in times out after two minutes and cleans up
the browser and virtual display. It never automatically replaces another session.

Optional shell shortcut: `alias tifr-quiet='tifrvpn -c --quiet'`.

| Command                  | Action                                                       |
| ------------------------ | ------------------------------------------------------------ |
| `tifrvpn -c`             | Connect, or report status if already connected               |
| `tifrvpn -d`             | Disconnect                                                   |
| `tifrvpn -s`             | Show status, assigned addresses and DNS                      |
| `tifrvpn`                | Toggle connection                                            |
| `tifrvpn --forget-login` | Clear this helper's cached sessions; leave any tunnel active |
| `tifr-otp --setup`       | Replace the encrypted master password after changing it      |

The applet can display/disconnect this connection. **Connect using `tifrvpn -c`**:
clicking `tifr-ivanti` in nm-applet does not invoke this helper and may fail with
`Unknown form … kc-form-login` on TIFR's SSO page.

## Troubleshooting and storage

- **Autofill stops:** check the saved entry, save the database, and confirm your
  system clock and phone codes agree. Avoid repeatedly submitting rejected
  credentials. If TIFR changes its login form, the helper may need updating.
- **GPG cannot decrypt:** unlock your own GPG key using its pinentry prompt.
  GPG/keyring unlocks and TIFR session confirmations can still require input.
- **Connection errors:** check `tifrvpn -s` and
  `journalctl -b -u NetworkManager --since '5 minutes ago'`. Remove personal
  information and authentication data before sharing diagnostics.
- **VPN service path:** the launcher currently checks
  `/usr/libexec/nm-openconnect-service`; other layouts require adapting it.

Passwords and the TOTP seed remain in your encrypted KeePassXC database. Its
master password is stored separately as GPG ciphertext. Reusable VPN/browser
sessions are stored in your desktop keyring; live tunnel secrets pass through
memory rather than a plaintext password file. HTTPS certificates are verified.
Only the trusted TIFR SSO origin receives automatic credential entry.
Keep the database, GPG keys, encrypted password file and authenticator QR images
out of this repository. The `.gitignore` covers common secret-file formats.

Setup reference: [KeePassXC TOTP guide](https://keepassxc.org/docs/KeePassXC_UserGuide#_adding_totp_to_an_entry).

## Python library and development

The import name is **`tifrvpn`**; the distribution name remains `tifrvpn-tui`.
To install the library and generated commands into a development environment,
run from this checkout:

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -e .
source .venv/bin/activate
```

Use system Python so the virtual environment can access its PyGObject bindings.
The package installer installs declared Python dependencies; system programs
and GTK/WebKit/Secret Service bindings still need the packages listed above.
This is an alternative to `install.sh`; the offline copy installer makes the
commands available but does not register the library in Python site-packages.

```python
import tifrvpn

connection = tifrvpn.status()
print(connection.state, connection.devices)

# These perform the same operations as tifrvpn -c and tifrvpn -d.
connection = tifrvpn.connect(quiet=True, on_progress=print)
tifrvpn.disconnect()
```

`setup()` creates or updates the NetworkManager profile and returns its UUID.
`forget_login()` clears saved sign-in state without disconnecting a tunnel.
`status()`, `connect()` and `disconnect()` return a frozen `VPNStatus` with
`state`, `profile_uuid`, `details`, `devices`, `connected`, and `changed`.
Intermediate NetworkManager states are preserved. A missing profile is reported
as `not-configured`. Expected public VPN-operation failures raise `VPNError`
(or a subclass), which exposes the command's `returncode` where applicable.

Settings use the same config file and environment variables as the commands.
You can also supply a `Config` directly, without changing process environment:

```python
from pathlib import Path
from tifrvpn import Config, VPNError, connect

settings = Config(
    database=Path("~/Documents/KeePass/Passwords.kdbx"),
    password_file=Path("~/.local/share/tifr-vpn/keepass-password.gpg"),
    entry="VPN/TIFR",
)
try:
    connection = connect(config=settings)
except VPNError as error:
    print(str(error))
```

Importing the package does not read credentials, start subprocesses, create
windows, or contact the server. VPN operations are synchronous and may open
sign-in or GPG dialogs; `quiet=True` hides the SSO browser using Xvfb. Progress
is sent to the optional callback. With no callback, the controller does not
print progress. The CLI uses the callback for its terminal messages.

Specialized helpers are available through their modules:

```python
from tifrvpn.credentials import get_code
from tifrvpn.totp import decode_export, current_code

code = get_code()  # returns the KeePassXC TOTP rather than printing it
```

| Module | Responsibility |
| --- | --- |
| `vpn` | Public connection operations and `VPNStatus` |
| `networkmanager` | Profile management, tunnel activation and state queries |
| `config` | Validated settings and environment overrides |
| `credentials` | KeePassXC access, GPG decryption and atomic password-file writes |
| `keyring` | Remembered VPN and browser sessions in Secret Service |
| `auth` | Session validation, worker launch and Xvfb lifecycle |
| `totp` | Authenticator export decoding and TOTP calculation |
| `gui` | SSO window, credential setup dialogs and QR importer |
| `cli` | Arguments, terminal output, notifications and exit codes |
| `_sso_worker` | Private isolated WebKit subprocess entry point |

`python -m tifrvpn` runs the same CLI as `tifrvpn`. The original root script
names remain as compatibility launchers; their implementations live under
`src/tifrvpn/`.

Offline checks from a checkout:

```sh
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
uv build --offline
```

Tests use fake commands and services; they do not access personal credentials,
change NetworkManager profiles or connect to the VPN. A live desktop sign-in
and tunnel connection still need verification with your own TIFR account.
