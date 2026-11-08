---
number headings: auto, first-level 1, max 5, _.1.1
---

# TIFR VPN Package Guide

Current implementation guide for `tifrvpn/package` at committed revision `589be0d`, inspected on 8 November 2026. For the original scripts and shared foundations, see [[TIFR Vpn TUI|TIFR Vpn TUI]]. Start with [[#15 Understanding the November fixes — a beginner's walkthrough|the beginner walkthrough]] for the recent changes, then use the full source appendix as a reference.

- Source snapshot: 8 November 2026.
- Repository: `/home/soham/projects/tifrvpn-tui`.
- Package revision: `589be0d86a538b1a28f08d384474a156628668c4` (`589be0d`).
- Checkout state at inspection: clean; the dependency, export validation, import/QR fixes and README changes are committed.
- Main baseline: `41b2346c8af8da7e1f224bdf9de10f50a946a261`.
- Documented snapshot: 34 files, 3,692 lines across those files; 53 offline test methods pass.
- Verified local runtime: uv-managed Python 3.13.18, PyGObject 3.58.1 inside an isolated `.venv` with system-site-packages disabled.
- This Research note was refreshed on 8 November 2026; it is separate from the repository's tracked `docs/TIFR Vpn TUI Package.md` copy.

## 1 Package branch — start here


### 1.1 Current implementation: `tifrvpn/package`

**Recorded revision:** `589be0d86a53` · **main baseline:** `41b2346c8af8` · **34 documented files / 3,692 lines** · **53 offline tests pass**.

This branch reorganizes the working VPN scripts into an importable Python library and three package-generated commands. The original main tutorial is retained in [[TIFR Vpn TUI|TIFR Vpn TUI]] for comparison. Its `install.sh`, Zsh launcher and root-script locations describe the older architecture. Use this package guide for the recorded current branch.

The early package cleanup was committed as `3275bad`, followed by its installation documentation in `075f9cd`. The configuration cast is now committed as `507b4b3`. The additional PyGObject, export validation, module-import/QR and README changes are committed as `bf6fa28`, `41d6410`, `6d5aa1a` and `589be0d`. The embedded source reflects that final clean checkout; it is not a collection of uncommitted suggestions.

**Package navigation:** [[#15 Understanding the November fixes — a beginner's walkthrough|New fixes explained]] · [[#2 Package branch — history and terminology|History]] · [[#3 Package branch — migration map|What moved and why]] · [[#4 Package branch — file map|Where code lives]] · [[#5 Package branch — setup and installation|Install]] · [[#6 Package branch — daily use|Daily use]] · [[#7 Package branch — workflows|Workflows]] · [[#8 Package branch — Python API|Python API]] · [[#9 Package branch — new concepts|New concepts]] · [[#10 Package branch — tests and verification|Tests]] · [[#13 Package branch — every current file|Every code line]] · [[#14 Package branch — transitional launchers explained|Removed wrappers]] · [[#11 Package branch — troubleshooting and maintenance|Troubleshooting]] · [[#12 Package branch — references|References]]


### 1.2 Your old installed commands are still a separate version

At the original 7 November inspection, all five files under `~/bin/tifr` matched `main`'s old scripts byte for byte. That is a recorded historical comparison, not a claim that this documentation refresh recopied or rechecked those files. `~/bin` resolves to `~/projects/dotfiles/bin`. Switching the repository to `tifrvpn/package` did not overwrite those files, move your vault, change your GPG key or replace your installed commands.

The package code lives in this checkout's `src/tifrvpn/`. An installation into a chosen Python environment generates commands in that environment's `bin/`. Which implementation runs depends on shell command resolution and that executable's Python environment—not merely on the branch shown in Git.

The original documentation check used a separate temporary environment. The final setup subsequently installed PyGObject directly into the project's existing uv-managed Python 3.13 `.venv`; the current 53-test run used that environment. Neither that package installation nor this guide copies over the separate `~/bin/tifr` scripts. Shell aliases/functions and PATH can still select a different executable; section 5 shows how to identify the one in use.

## 2 Package branch — history and terminology


### 2.1 What a branch, commit and working tree mean here

A **repository** stores source files and Git history. A **commit** records one snapshot. A **branch** is a movable named reference to a commit. Your **working tree** is the files currently checked out, plus any uncommitted edits. A **remote** is another repository location; `origin/main` is your local record of that remote branch's last fetched state.

The slash in `tifrvpn/package` is part of a branch name. It does not mean Git automatically creates a `tifrvpn/package` folder or installs a Python package. The package folder happens to be `src/tifrvpn`; that is a separate source-layout decision.

`main` still points at `41b2346`, the older script implementation. The package branch adds these commits:

| Commit | What its snapshot means |
| --- | --- |
| `41b2346` | Main baseline: independent root scripts and copy installer; [[TIFR Vpn TUI|The original guide]] covers this version. |
| `ade9780` | First refactor: create `src/tifrvpn`, public API, component modules and tests; temporarily retain Python compatibility wrappers and a copy installer. |
| `3275bad` | Use package entry points exclusively: delete the root wrappers/installer and the compatibility-only `auth_main`; remove manual worker PYTHONPATH injection; add installed-package tests. |
| `075f9cd` | Earlier package installation/editable-development documentation. |
| `b61531d` | Add the earlier ChatGPT-derived guides under the repository's `docs/` directory. |
| `507b4b3` | Record the validated configuration dictionary type so Path/entry lookups type-check correctly. |
| `bf6fa28` | Declare and lock PyGObject so ordinary uv installs provide `import gi`. |
| `41d6410` | Validate decoded export field types and add three decoder test methods. |
| `6d5aa1a` | Move imports to module scope, update dependency mocks and repair the QR/Qt typing paths. |
| `589be0d` | Document the ordinary uv installation and native GI prerequisites; current recorded head. |

Reasons stated in this guide describe effects visible in code, tests and commit changes. They do not assume undocumented personal motives of the author. The intermediate `ade9780` source is included later to explain how migration happened; it is not the current installation route.


### 2.2 Read history and compare branches without changing them

From the repository:

```sh
git branch --show-current
git status --short
git log --oneline main..tifrvpn/package
git diff --stat main...tifrvpn/package
git show main:tifr-vpn-auth.py
git show tifrvpn/package:src/tifrvpn/auth.py
```

The first command identifies the checked-out branch. The second shows pending source edits. `main..tifrvpn/package` selects commits reachable from the package branch but not main. The three-dot diff compares from their common ancestor. `git show branch:path` reads a historical file without switching branches or replacing files.

Committing records source; installing changes what a Python environment can import/run. Pushing sends commits to a remote; it does not automatically update local `~/bin/tifr` copies or publish a package to PyPI.

## 3 Package branch — migration map


### 3.1 The architectural change in one view

**Main:** root executables contain most of the logic; Zsh calls a neighboring Python script; Python loads another hyphenated script with `runpy`; a shell installer copies the files.

**Current package branch:** generated executable → `cli.py` adapter → `vpn.py` public operations → focused Python modules. WebKit still runs in an isolated worker, and NetworkManager/OpenConnect still own the tunnel.

```text
Installed tifrvpn executable
  → tifrvpn.cli.main
    → tifrvpn.vpn.connect / disconnect / status / setup / forget_login
      ├─ networkmanager: profile, state, verified secret handoff, tunnel
      ├─ keyring: cached session and browser-state adapters
      └─ auth: cached-token probe and browser-process supervisor
          → python -m tifrvpn._sso_worker
            → gui.sso.login_cookie
              ├─ config: selected paths / entry
              ├─ credentials: GPG + KeePassXC login and TOTP
              └─ keyring: selected remembered browser cookies

Installed tifr-otp executable
  → cli.otp_main
    ├─ credentials.get_code → return code → CLI prints it
    └─ gui.credential_setup.setup → verify input → credentials.save_password

Installed tifr-import-totp executable
  → cli.import_totp_main
    → gui.qr_import.run
      → totp.decode_export / current_code
```


### 3.2 Old location → new location → reason


| Main responsibility | Current home | Purpose of separating it |
| --- | --- | --- |
| `tifrvpn`: option parser, status text and notifications | `cli.py` | Keep terminal presentation out of the reusable operations. |
| `tifrvpn`: connect/disconnect/status sequencing | `vpn.py` | Offer the same operations as callable Python functions returning results. |
| `tifrvpn`: nmcli checks, profile creation/update/state/down | `networkmanager.py` | Put OS networking details behind one backend. |
| `tifr-vpn-auth.py`: activation TLS/key pin/memfd | `networkmanager.activate` | Keep tunnel activation with the rest of the NetworkManager backend. |
| `tifr-vpn-auth.py`: saved-login read/write/delete | `keyring.py` | Give session and browser state clearly named wrappers and preserve the existing cache namespace. |
| `tifr-vpn-auth.py`: portal validation and worker/Xvfb supervision | `auth.py` | Separate non-GUI authentication control from the web window. |
| `tifr-vpn-auth.py`: JavaScript, GTK/WebKit window and cookie callbacks | `gui/sso.py` | Keep browser GUI logic in the isolated worker; its toolkit imports now load with that module, while the window opens only during actual sign-in. |
| `tifr-vpn-auth.py`: internal `--sso-window` mode | `_sso_worker.py` | Make isolated process execution a dedicated importable module. |
| `tifr-vpn-auth.py`: cached/fresh session followed by activation | `vpn.connect` | Make the complete operation available to both CLI and other Python callers. |
| `tifr-otp.py`: configuration tuple | `config.Config` + `load_config` | Return named settings fields and permit explicit settings objects. |
| Configuration's vault/executable checks | `credentials.validate_config` | Defer real runtime prerequisites until credentials are needed. |
| `tifr-otp.py`: KeePass reads, GPG decryption/key choice | `credentials.py` | Reuse headless credential access independently of command printing or Qt dialogs. |
| `tifr-otp.py`: setup password prompt | `gui/credential_setup.py` | Separate collecting/confirming input from encrypting/storing it. |
| `tifr-otp.py`: ciphertext write portion of setup | `credentials.save_password` | Reuse and test encrypted atomic-file handling without a dialog. |
| OTP script's `main()` | `cli.otp_main` | Keep intentional terminal code output and CLI errors at the command boundary. |
| QR script's `fields`, `decode_export`, `current_code` | `totp._fields`, `decode_export`, `current_code` | Pure algorithms can be tested/used without camera, Qt or NumPy. |
| QR script's `Scanner` and Qt event loop | `gui/qr_import.run` | Keep interactive camera/image work optional. |
| QR command parser and startup errors | `cli.import_totp_main` | Generate a command from package metadata while retaining safe --help/error behavior. |
| Extensionless QR wrapper | No current source equivalent needed | Package installation generates its executable wrapper. |
| Copying `install.sh` | Standard/editable package installation | Register imports and command entry points through one supported installation model. |
| `src/tifrvpn_tui` greeting scaffold | Replaced by `src/tifrvpn` | The declared package now exposes real VPN behavior. |
| General `RuntimeError` and numeric script exits | `errors.py` + CLI error conversion | Applications catch failures; command adapters decide output/exit codes. |
| Missing example config reference | Actual `config.example.json` | The documented customization example now exists. |
| `tests/test_setup.py` copy/config checks | `test_config.py` + `test_packaging.py` | Preserve config/parser checks and verify the new installed-package model instead of the removed copier. |

Moving a responsibility is not always a literal Git rename. One old file can split into several new modules; two old responsibilities can join in one layer. The table explains semantic lineage, while Git may display additions/deletions rather than detect a single renamed file.


### 3.3 What deliberately stays compatible

The fixed portal/hostname, `tifr-ivanti` profile name, OpenConnect `nc` protocol, certificate checks, secret flags and desktop-keyring schema/kinds remain. Default vault/ciphertext/entry locations and TIFR environment override names stay familiar. The user-facing `-c`, `-d`, `-s`, toggle, quiet, setup and forget-login actions are preserved.

Old scripts and the package can therefore operate on the **same** NetworkManager profile and keyring records when used under the same account/desktop. They are not automatically separate VPN identities. Clearing the shared cache through one affects what the other can reuse. A saved token is still validated by the gateway before reuse.

No vault, master password, GPG key or authenticator enrollment was migrated by merely moving Python source. Your files stay at their configured paths; the new modules call the same external tools and read those settings when invoked.


### 3.4 What changes beyond filenames

- **Reusable API:** `import tifrvpn` exposes operations, not a greeting or an auto-executed CLI.
- **Structured data:** state/device/change results travel as `VPNStatus`, while settings travel as `Config`.
- **Catchable errors:** expected failures are `VPNError` subclasses carrying `returncode`, rather than library code choosing to terminate the application.
- **Presentation boundary:** terminal colors, stdout/stderr choices and notifications live in `cli.py`. Callers can omit progress or supply their own callback.
- **Import placement and behavior:** imports now appear at module scope. The relevant dependencies must be installed before importing those modules. Application imports still do not read credentials/configuration, launch subprocesses, open windows or create VPN sockets; the revised import test checks that boundary using fake dependency interfaces.
- **Worker startup:** `python -m tifrvpn._sso_worker` replaces invoking the old root script with `--sso-window`. It must be importable in that interpreter's environment.
- **Worker diagnostics:** both child streams are captured. The cookie stays on stdout; stderr lines are forwarded after the child returns. This differs from main's live inherited stderr.
- **Installation checks:** tests now require genuine installed entry points and isolated imports from another directory, preventing hidden dependence on the source cwd/PYTHONPATH.
- **Dependencies:** separately distributed `argparse` is removed because Python supplies it. PyGObject is now declared alongside cryptography, NumPy, PySide6 and ZXing. Their imports are grouped at module scope; no optional dependency extras are defined.

## 4 Package branch — file map

The package's main public entry is `src/tifrvpn/__init__.py`. Begin with `vpn.py` to understand the operation, then inspect the backend/helper it calls. The full snapshots below also include tests, metadata, lock data and unchanged support files.

| Current file | Lines | Purpose |
| --- | ---: | --- |
| [[#13.1 Package source — src/tifrvpn/__init__.py\|src/tifrvpn/__init__.py]] | 20 | The public front door of the importable library |
| [[#13.2 Package source — src/tifrvpn/__main__.py\|src/tifrvpn/__main__.py]] | 6 | The module-execution adapter |
| [[#13.3 Package source — src/tifrvpn/vpn.py\|src/tifrvpn/vpn.py]] | 143 | The public orchestration layer: it chooses the sequence of backend operations and returns structured results |
| [[#13.4 Package source — src/tifrvpn/cli.py\|src/tifrvpn/cli.py]] | 238 | Terminal presentation and command dispatch now live in Python |
| [[#13.5 Package source — src/tifrvpn/config.py\|src/tifrvpn/config.py]] | 83 | Settings are now an immutable Config object plus a loader, extracted from main’s tifr-otp.py configuration() |
| [[#13.6 Package source — src/tifrvpn/errors.py\|src/tifrvpn/errors.py]] | 31 | A small error vocabulary shared by the library and command adapters |
| [[#13.7 Package source — src/tifrvpn/credentials.py\|src/tifrvpn/credentials.py]] | 171 | The headless credential-access layer extracted from main’s tifr-otp.py |
| [[#13.8 Package source — src/tifrvpn/auth.py\|src/tifrvpn/auth.py]] | 140 | The non-GUI authentication supervisor, split out of main’s large authentication script |
| [[#13.9 Package source — src/tifrvpn/_sso_worker.py\|src/tifrvpn/_sso_worker.py]] | 52 | The private worker entry point replaces main’s --sso-window self-invocation mode |
| [[#13.10 Package source — src/tifrvpn/keyring.py\|src/tifrvpn/keyring.py]] | 70 | A named adapter around desktop Secret Service replaces the multifunction saved_login() inside main’s authentication script |
| [[#13.11 Package source — src/tifrvpn/networkmanager.py\|src/tifrvpn/networkmanager.py]] | 217 | The NetworkManager/OpenConnect backend replaces main’s Zsh nmcli helpers and receives the old Python activate() TLS/descriptor handoff |
| [[#13.12 Package source — src/tifrvpn/totp.py\|src/tifrvpn/totp.py]] | 114 | Pure-data QR migration parsing and TOTP calculation moved out of main’s combined QR/Qt script |
| [[#13.13 Package source — src/tifrvpn/gui/__init__.py\|src/tifrvpn/gui/__init__.py]] | 1 | Marks the optional GUI subpackage |
| [[#13.14 Package source — src/tifrvpn/gui/credential_setup.py\|src/tifrvpn/gui/credential_setup.py]] | 51 | Qt password-collection dialogs were split from the non-GUI GPG/ciphertext writing operations |
| [[#13.15 Package source — src/tifrvpn/gui/sso.py\|src/tifrvpn/gui/sso.py]] | 336 | The GTK/WebKit window and restricted autofill logic moved out of the old all-in-one authentication script |
| [[#13.16 Package source — src/tifrvpn/gui/qr_import.py\|src/tifrvpn/gui/qr_import.py]] | 233 | The Qt camera/image UI moved out of the old combined QR script |
| [[#13.17 Package source — tests/test_imports.py\|tests/test_imports.py]] | 54 | Import tests supply fake dependency interfaces and reject application external work during module loading |
| [[#13.18 Package source — tests/test_vpn.py\|tests/test_vpn.py]] | 132 | Offline regression checks for vpn |
| [[#13.19 Package source — tests/test_cli.py\|tests/test_cli.py]] | 133 | Offline regression checks for cli |
| [[#13.20 Package source — tests/test_config.py\|tests/test_config.py]] | 112 | Offline regression checks for config |
| [[#13.21 Package source — tests/test_auth.py\|tests/test_auth.py]] | 93 | Offline regression checks for auth |
| [[#13.22 Package source — tests/test_keyring.py\|tests/test_keyring.py]] | 86 | Offline regression checks for keyring |
| [[#13.23 Package source — tests/test_networkmanager.py\|tests/test_networkmanager.py]] | 134 | Offline regression checks for networkmanager |
| [[#13.24 Package source — tests/test_quiet.py\|tests/test_quiet.py]] | 130 | Offline regression checks for quiet |
| [[#13.25 Package source — tests/test_packaging.py\|tests/test_packaging.py]] | 74 | Installation tests replace the old copy-installer checks |
| [[#13.26 Package source — pyproject.toml\|pyproject.toml]] | 28 | The package distribution is still named tifrvpn-tui, but the Python import name is tifrvpn and the three installed commands are tifrvpn, tifr-otp and tifr-import-totp |
| [[#13.27 Package source — config.example.json\|config.example.json]] | 5 | The previously missing example config is now present on the package branch |
| [[#13.28 Package source — README.md\|README.md]] | 305 | The branch’s human-facing instructions now describe installing an actual Python distribution and using its library |
| [[#13.29 Package source — uv.lock\|uv.lock]] | 376 | Generated locked dependency selection, now including PyGObject and Pycairo |
| [[#13.30 Package source — .envrc\|.envrc]] | 1 | The developer-environment instruction remains unchanged; it is independent of the old script installer |
| [[#13.31 Package source — .python-version\|.python-version]] | 1 | The preferred development Python series remains unchanged |
| [[#13.32 Package source — .gitignore\|.gitignore]] | 38 | The existing ignore patterns remain unchanged in this branch snapshot |
| [[#13.33 Package source — LICENSE\|LICENSE]] | 21 | The license text remains unchanged, including its unfilled copyright placeholders |
| [[#13.34 Package source — tests/test_totp.py\|tests/test_totp.py]] | 63 | Three decoder tests covering valid public-key fixtures and nine malformed/unsupported payload cases |


### 4.1 Where source, installed code, command wrappers and personal data live


| Kind of thing | Location / identity | What it means |
| --- | --- | --- |
| This Git checkout | `~/projects/tifrvpn-tui` | Branch-controlled source. |
| Import package source | `src/tifrvpn/` | Python modules currently being developed. |
| Distribution name | `tifrvpn-tui` | Name used in installation metadata/artifact names. |
| Python import name | `tifrvpn` | Name used by `import tifrvpn`; selected by uv_build's module-name setting. |
| Generated commands | `<chosen environment>/bin/` | Wrappers for the three functions in `[project.scripts]`. |
| Normal installed code | Environment's Python site-packages | Installed package contents; source edits require reinstallation to update that copy. |
| Editable installation | Environment metadata points at this source layout | New interpreter processes use checkout code; don't remove/switch away its package tree and expect the editable install to remain unchanged. |
| Old runtime copies | `~/bin/tifr` → `~/projects/dotfiles/bin/tifr` | Still main's five scripts at this inspection. |
| Optional config | `~/.config/tifr-vpn/config.json` or `$XDG_CONFIG_HOME/tifr-vpn/config.json` | Paths/entry names, not passwords. |
| Default encrypted vault | `~/Documents/KeePass/Passwords.kdbx` | Stores account fields and TOTP enrollment seed. |
| Default GPG ciphertext | `~/.local/share/tifr-vpn/keepass-password.gpg` | Stores the encrypted database master password. |
| Session/browser cache | Desktop Secret Service, schema `in.res.tifr.vpn` | Scoped by unchanged server URL and `session`/`browser` kind. |
| VPN recipe | NetworkManager profile `tifr-ivanti` | Saved networking settings, distinct from an active tunnel. |
| Live activation handoff | Anonymous `memfd` descriptor | Transient secret data passed to nmcli, avoiding a named plaintext password file. |

A source file is not automatically an installed command; an installed distribution is not the same as a Git branch; and a generated command's name is not a guarantee it uses the interpreter you expected. Diagnose these identities separately.

## 5 Package branch — setup and installation


### 5.1 The final environment: ordinary uv-managed Python 3.13

The final verified checkout uses Python 3.13.18 in `.venv`. `include-system-site-packages = false` is intentional. PyGObject 3.58.1 is installed inside that environment and provides `import gi`; Pycairo 1.29.2 was built/installed as its dependency. Python 3.14 is not a package requirement and is not needed by this route.

Earlier instructions suggested reusing Fedora's preinstalled Python 3.14 GI bindings through a compatible system interpreter and `--system-site-packages`. That is an alternative, not the final recommendation here. The successful final fix was `uv add PyGObject`, building the bindings for the project's own Python 3.13. This dependency is now already recorded in the repository, so a fresh clone uses `uv sync --locked`.

There are two layers to install: Python distributions inside `.venv`, and native Linux libraries/programs outside it. uv manages the first layer. Your OS package manager provides the second. Section 15 explains the name and version differences with examples.

### 5.2 Install on a fresh machine and explain each step

Install NetworkManager/OpenConnect support, KeePassXC CLI, GnuPG/pinentry and desktop keyring support as described in README. For GI runtime/build prerequisites on Fedora, the current README specifies:

```sh
sudo dnf install gcc pkgconf-pkg-config gobject-introspection-devel cairo-gobject-devel gtk3 webkit2gtk4.1 libsoup3 libsecret
```

This covers GI support, not all the VPN/credential programs. Building Python bindings needs a compiler, native development files and matching interpreter headers. uv-managed CPython supplies its own Python headers; system Python may require `python3-devel`. Other distributions use different package names and must meet the locked release's native-library requirements.

From your actual clone location:

```sh
cd /home/soham/projects/tifrvpn-tui
uv sync --locked
source .venv/bin/activate
```

`cd` selects the project directory. `uv sync` creates or updates the local environment and installs the package plus its Python dependencies. `--locked` requires the checked-in lockfile to remain valid rather than silently updating it. Activation changes command lookup in this shell so commands resolve to `.venv/bin`. On another machine, replace the absolute clone path with its real location.

Do not rerun `uv add PyGObject` merely to launch a fresh clone: the dependency is already declared. Use `uv add` when intentionally changing dependencies, and `uv sync --locked` to install the declared selection. The UV project install is editable; new Python processes read the checkout's source. Without shell activation, prefix commands with `uv run`, for example `uv run tifrvpn --help`. No explicit system interpreter override is needed in this final setup.

The Python package installation does not create a TIFR account, migrate your vault, install OS services or enroll an authenticator. Complete those separate preparation steps below.

### 5.3 Verify which package and commands you will actually use


```sh
type -a tifrvpn
command -v tifrvpn
python -c 'import sys, tifrvpn; print(sys.executable); print(tifrvpn.__file__)'
python -m tifrvpn --help
tifrvpn --help
tifr-otp --help
tifr-import-totp --help
```

`type -a` can reveal aliases/functions and multiple executable candidates. `command -v` shows the selected command in that shell. Python prints its actual interpreter and imported package source. In an editable environment, the package location should correspond to this checkout's `src/tifrvpn`; in a normal installation it should correspond to that environment's installed files. Help paths do not read a real vault, query NetworkManager or open a GUI, but the module-level Python/native imports must be available even for help.

If an old shell alias/function wins over the generated executable, activation alone may not override that alias/function. You can use the explicit environment command or `.../bin/python -m tifrvpn` to make the chosen implementation unambiguous. No alias, PATH setting or startup file was modified by this guide.


### 5.4 One-time account and credential preparation

**1. Save the TIFR entry.** Open your KeePass database, fill account Username/Password, configure the existing TOTP enrollment seed/settings and save the database. The CLI reads the saved file; leaving unsaved GUI edits is insufficient. The auto-login time-boundary logic assumes 30-second codes.

**2. Optionally import an existing enrollment.** Run `tifr-import-totp` or `tifr-import-totp --image`, export only TIFR from Google Authenticator, copy the decoded seed/settings into KeePassXC and save there. This duplicates the enrolled seed; it does not create a new TIFR enrollment or automatically edit the vault. The camera stops after success. Clipboard cleanup affects the live clipboard only, not independent clipboard-manager history.

**3. Customize paths only if needed.** The branch now includes a real `config.example.json`:

```json
{
  "database": "~/Documents/KeePass/Passwords.kdbx",
  "password_file": "~/.local/share/tifr-vpn/keepass-password.gpg",
  "entry": "TIFR"
}
```

Defaults work without that file. If creating a custom config, put these fields under the selected config directory and adapt them. The README's `cp config.example.json ...` can overwrite an existing config; it is a setup example rather than something to repeat each day. Environment variables override the corresponding JSON fields; direct `Config` injection is another programmatic option. No passwords/seeds belong in this JSON.

**4. Encrypt database access.** Ensure you have an appropriate GPG encryption key, then run `tifr-otp --setup`, optionally `--recipient YOUR_FINGERPRINT`. Its Qt dialog asks for the **vault master password**, verifies local vault entry access, and calls `credentials.save_password` to GPG-encrypt and atomically save it. Local verification does not submit a server login.

**5. Check a code.** `tifr-otp` intentionally prints the current short-lived code; compare it with the phone. The lower-level `credentials.get_code()` returns it without printing.

**6. Prepare the connection recipe.** `tifrvpn --setup` creates/updates the user-specific NetworkManager OpenConnect profile. This is a separate setup task from encrypting the database password. Connect then uses that recipe.

Use your ordinary desktop account, allowing NetworkManager's configured authorization agent to ask if required. The package does not bypass system policy. Moving from main does not require regenerating an already working seed or re-encrypting an unchanged working master-password file purely because the source layout changed.

## 6 Package branch — daily use


### 6.1 A normal day's terminal workflow


```sh
# Once per new shell when using this chosen environment:
source /home/soham/projects/tifrvpn-tui/.venv/bin/activate

# Connect, then inspect the result:
tifrvpn -c
tifrvpn -s

# Or choose quiet browser sign-in when connecting:
tifrvpn -c --quiet

# At the end of your work:
tifrvpn -d
```

Choose normal or quiet connect; there is no need to run both after the first already succeeded. If already active, connect reports status and does not create another tunnel. If a remembered session is still valid, either mode bypasses fresh browser/vault authentication. If expired, the controller clears that direct cookie, obtains a new session, saves it and activates the tunnel.

The phone and KeePassXC GUI do not need to stay open for ordinary saved-file access. GPG/keyring unlocking or a portal confirmation can still require your attention. An already active or transitional profile uses the same `tifr-ivanti` identity created by main, so avoid treating old/new commands as independent networks.


### 6.2 Daily command meanings and exit behavior


| Action | What happens | Result convention |
| --- | --- | --- |
| `-c` | Connect, or show existing active status. | CLI 0 for successful active result. |
| `-c --quiet`, `--quiet -c`, `--quiet` | Same connect action with a hidden fresh-sign-in browser. | Same success/error conventions; quiet is a modifier, not log suppression. |
| `-s` | Read saved-profile state and active details. | CLI 0 only if activated; 1 for inactive/not-configured states. |
| `-d` | Bring down active/transitional profile; tolerate missing/inactive profile. | CLI success for nothing-to-disconnect too. |
| No arguments | Disconnect a nonempty nondeactivated state, otherwise connect. | Explicit `-c`/`-d` can be easier when learning than a state-dependent toggle. |
| `--setup` | Prepare profile settings only. | Does not establish an authenticated tunnel itself. |
| `--forget-login` | Delete this helper's cached session/browser records. | Leaves vault/ciphertext and a running tunnel alone. |
| Invalid combinations | Reject before calling the operation. | Status 2; e.g. `--quiet -d`, two actions or unknown options. |
| Ctrl+C | Cancel current work; supervisor cleans up the hidden process group where applicable. | Cancellation status 130 at the CLI boundary. |

No-argument toggle is deliberately compatible with main, including an `activating` state choosing disconnect. Ordinary library `status()` returns a status object even when inactive; CLI `-s` separately converts nonconnected states to exit status 1. Library `disconnect()` returns an object; the CLI prints its explanation and usually returns 0 on successful/no-op disconnection.


### 6.3 Quiet mode, prompts and progress timing

A real GTK/WebKit browser still runs, on a private Xvfb display. `auth.authenticate` checks Xvfb tools, validates selected credential prerequisites, attempts GPG unlock on the real desktop, then starts the worker with `--quiet`. The worker's decryption call uses `allow_prompt=False`, asking GPG to fail rather than open an invisible pinentry.

A valid cached session skips this new-browser path entirely. The 120-second limit starts around the background child communication; earlier GPG/keyring prompting and later TLS/nmcli activation are outside that timer. SIGTERM cleanup gets a five-second grace period before SIGKILL escalation; the final cleanup wait has no new explicit timeout. Group cleanup targets descendants that remain in that process group, not a universal guarantee about arbitrary detached processes.

Known rejected-login/session-replacement cases stop hidden automation and tell you to retry `tifrvpn -c` visibly. Unknown required interaction can eventually cause timeout. The code does not automatically click confirmation to terminate another session.

**Current progress detail:** this branch captures worker stdout/stderr and forwards worker stderr lines only after the subprocess returns. Initial parent messages can appear immediately through the callback, but intermediate “submitting saved…” messages can arrive together afterward. `flush=True` in the child does not make a parent that waits in `communicate()` deliver live callbacks. This is a real distinction from main's inherited stderr, and the source notes identify the exact lines.

## 7 Package branch — workflows


### 7.1 Fresh connection, step by step through actual functions

1. The installer-generated executable imports `cli.main`; its wrapper converts the returned number to process exit status.
2. `cli.main` calls `_vpn_main` with arguments. Parsing chooses `_connect(quiet)` after validating combinations.
3. `_connect` calls `vpn.connect(quiet=..., on_progress=_progress)`.
4. `@_operation` wraps public failure handling. `nm.require_available()` checks tools and NetworkManager.
5. `nm.profile_uuid()` finds the exact saved profile. `ProfileNotFound` triggers `vpn.setup`; ambiguity is a different error and does not create a duplicate.
6. Current state is checked. Activated returns status immediately; a busy transition raises `ConnectionBusy` before credentials.
7. `nm.validate_profile(uuid)` verifies OpenConnect service, fixed gateway and `nc` protocol.
8. `keyring.load_session()` looks under the unchanged schema/server/session key.
9. If a saved token passes `auth.valid_session`, go straight to activation. Otherwise clear the expired direct token and enter new authentication.
10. `auth.authenticate` prepares a child-only environment. Explicit `Config` paths/entry are serialized as `_TIFR_WORKER_CONFIG` as well as corresponding TIFR overrides; passwords/cookies are not that payload.
11. Start the same interpreter with `-m tifrvpn._sso_worker`, either directly or under Xvfb for quiet mode. Package installation makes this module reachable without the deleted manual source-path injection.
12. `_sso_worker.sso_window_process` reconstructs Config if explicitly supplied and loads `gui.sso.login_cookie`; `_run` owns output/errors/immediate child shutdown.
13. The worker module has already loaded its GI namespaces at module import. Calling `login_cookie` now creates the ephemeral WebKit context and GTK window, and restores valid allowed TIFR cookie records from the keyring before loading the portal.
14. Event handlers and timers inspect only the intended SSO origin/realm. Known page errors stop repeated autofill; submitted-step tracking prevents blind repeats.
15. Once an allowed form needs credentials, choose direct/loaded settings, run `credentials.validate_config`, GPG-decrypt the database master password, and read saved login fields from the KeePass CLI.
16. At the OTP form, wait if fewer than five seconds remain in the assumed 30-second period, then obtain a fresh code from KeePassXC. JSON-encoded values are inserted into the restricted page's inputs and submitted using normal form events.
17. A DSID cookie is a candidate, not immediate proof of completion. `valid_session` probes portal access; known session-conflict warnings in quiet mode request a visible retry.
18. Save allowed browser cookies under kind=browser, clean up GTK timers/window, and return the accepted cookie from `login_cookie`.
19. Worker `_run` writes only cookie data to captured stdout, flushes and terminates that isolated process. Parent `authenticate` replays captured diagnostics if requested and rejects malformed/failed output.
20. `vpn.connect` attempts to save the new direct token under kind=session, then calls `nm.activate`.
21. `nm.activate` verifies the server with normal TLS trust, derives a SHA-256 SubjectPublicKeyInfo pin, retains the verified connection's gateway IP, and creates the transient secret payload.
22. Write that payload to an anonymous Linux descriptor, rewind it, and inherit it into `nmcli --wait 90 connection up ... passwd-file /proc/self/fd/N`. The cookie does not become an argv value or a named plaintext password file.
23. NetworkManager/OpenConnect establish the tunnel. The descriptor is closed even on failure. `vpn.connect` queries actual resulting status and refuses to return a connected result if activation did not leave it active.
24. Return `VPNStatus(..., changed=True)`. The CLI formats it and sends a desktop notification only for a successful state change. An embedding program instead receives the object and chooses its own response.


### 7.2 Other important paths through the workflow

**Cached reconnect:** profile/state validation → load accepted cached DSID → verified activation → resulting status. No fresh browser/vault path is required, even if the call specified quiet mode or a different Config whose credentials never need loading in this cached path.

**Already connected:** runtime/profile/state checks → `status()` → connected result with `changed=False`; no new token read, sign-in or activation.

**Profile missing during status:** `status()` returns `VPNStatus('not-configured')` without creating anything. Profile missing during connect is a recoverable setup path. An ambiguous profile is an error requiring resolution.

**Disconnect:** check tools → find profile → return a no-op status for missing/inactive state, or call `nm.deactivate` for active/transitional state → deactivated result with the appropriate changed flag.

**Forget cached sign-in:** attempt both keyring kinds; a missing record is acceptable, a caught backend failure can produce an AuthenticationError after both attempts. No `nm.deactivate` call belongs to this workflow.

**OTP command:** parse flags → `load_config` → either validate and open credential setup, or call `credentials.get_code` → validate, decrypt, read_code → intentionally print the returned code at the CLI boundary.

**QR import:** import the CLI/GUI modules and their dependencies → parse --image → call the scanner with a verified QApplication → camera frames or local image → grayscale/stride-correct array → ZXing QR text with an explicit BarcodeFormats selection → `totp.decode_export` validates field types → display masked seed/settings/current code → manual paste into KeePassXC → stop devices and conditionally clear the live clipboard.


### 7.3 How data crosses each boundary


| Boundary | Passed data | Why this form |
| --- | --- | --- |
| Shell → generated command | Argument list such as `-c`, `--quiet` | CLI chooses intent before any credential operation. |
| CLI → library | Booleans, optional Config, callback | Reuse the operation without parsing terminal text again. |
| Library → caller | `VPNStatus`, UUID, None, or typed exception | Structured results and caller-controlled reporting. |
| Config → child | Database/ciphertext paths and entry in copied env/JSON | Select one call's settings without rewriting the parent's environment. |
| GPG → credential code | Captured decrypted bytes | Obtain master password without putting it in process argv. |
| Credential code → KeePass CLI | Master password via stdin | Match the CLI's single-line password protocol. |
| KeePass CLI → credential code | Captured username/password/code lines | Validate known output shape before using it; avoid automatic terminal output. |
| Browser form → Python callback | JSON step/error status | Inspect state without returning field values as status text. |
| Browser child → parent | Accepted DSID on captured stdout; diagnostics on stderr | Keep token data separate from human messages. |
| Controller → Secret Service | Direct token or serialized allowed cookies under separate kinds | Permit later authenticated reuse using unchanged cache identity. |
| Controller → nmcli | Anonymous inherited descriptor | Support nmcli's file-reading interface without a named plaintext secret file or token argv. |

Sensitive values necessarily exist in process/browser memory while used. Dropping a Python variable is not a secure wipe of every copy. File permissions, .gitignore, virtual displays, TLS trust, keyring storage and anonymous descriptors each address a different concern; none is a universal guarantee that a privileged observer, core dump or swap can never see memory.

## 8 Package branch — Python API


### 8.1 The public functions and their contracts


| API | Inputs | Successful result | Actual effects when called |
| --- | --- | --- | --- |
| `load_config()` | Defaults + optional JSON + environment | `Config` | Reads settings only; does not require the vault/GPG yet. |
| `Config(database, password_file, entry='TIFR')` | Path-like fields and string entry | Immutable normalized settings object | Expands ~ and checks basic path/entry form; does not read/open the vault. |
| `status()` | None | `VPNStatus` | Checks/query NetworkManager; no automatic profile creation or login. |
| `setup(on_progress=None)` | Optional callback | Profile UUID string | Creates/updates user profile; not necessarily an active tunnel. |
| `connect(quiet=False, config=None, on_progress=None)` | Keyword-only mode/settings/callback | `VPNStatus` | Synchronous check/authenticate/activate workflow. May prompt or open GUI. |
| `disconnect(on_progress=None)` | Optional callback | `VPNStatus` | Down operation only if needed; tolerates missing/inactive profile. |
| `forget_login()` | None | `None` | Clears cached session/browser state, leaving live tunnel alone. |
| `credentials.get_code(config=None)` | Optional Config | Current TOTP string | May prompt GPG and read the vault; does not print the code. |
| `totp.decode_export(text)` | Supplied migration-QR text | Normalized account dictionary | Pure decoding; does not start a camera or contact a service. |
| `totp.current_code(account, timestamp=None)` | Account seed/settings + optional fixed time | Zero-padded code string | Pure calculation using current/provided time. |

Expected public VPN-operation failures raise `VPNError` or a subclass. Type hints describe expected inputs; they do not make arbitrary wrong objects safe. For example entry is expected to be a string and the code explicitly calls `.strip()` on it. Treat underscore-prefixed helpers/workers as internal implementation details even though Python does not enforce module privacy.


### 8.2 Read status without running a connect/disconnect example accidentally


```python
import tifrvpn

connection = tifrvpn.status()
print(connection.state)
print(connection.connected)
print(connection.devices)
print(connection.profile_uuid)
```

`import` loads safe definitions; `status()` is the point at which backend tools are queried. `connection` is an ordinary variable name holding a `VPNStatus`, not a live connection object you must close. Its fields describe that query's result; they do not automatically update if the tunnel later changes.


### 8.3 Connect with explicit settings and catch failures


```python
from pathlib import Path
from tifrvpn import Config, VPNError, connect, disconnect

settings = Config(
    database=Path('~/Documents/KeePass/Passwords.kdbx'),
    password_file=Path('~/.local/share/tifr-vpn/keepass-password.gpg'),
    entry='TIFR',
)

messages = []
try:
    connection = connect(
        quiet=True,
        config=settings,
        on_progress=messages.append,
    )
    print(connection.connected, connection.changed, connection.devices)
except VPNError as error:
    print(f'Could not connect: {error}; backend status {error.returncode}')

# Call disconnect() separately when you actually want to end the tunnel.
```

This example **does perform a real connection** when executed in a configured environment. `messages.append` is passed without parentheses so the operation can call it later with each safe progress string. You can use `print` for visible messages or `None` for no controller progress. The API returns after its synchronous work finishes; it is not an async future or background job handle.

An explicit Config applies to credential access during fresh authentication; a valid accepted cached session can be reused before new credentials are needed. The parent copies settings into its child environment rather than rewriting your parent's TIFR variables. Long-running/GUI applications must plan around blocking operations and the worker/display lifecycle; simply being importable does not make a connect call nonblocking.


### 8.4 Every VPNStatus field and property


| Member | Meaning |
| --- | --- |
| `state` | Preserved state string, such as activated, deactivated, activating, disconnected or not-configured. |
| `profile_uuid` | Exact saved connection identifier, or None when absent. |
| `details` | Selected raw nmcli field text, usually populated for an activated result. |
| `changed` | Whether this successful connect/disconnect operation changed state; status/already-active/no-op paths default False. It is not a lifetime connection history. |
| `connected` | Computed property true only when state equals activated. |
| `devices` | Computed tuple of usable names parsed from GENERAL.DEVICES in details; empty when none is available. |

`@dataclass(frozen=True)` prevents normal field reassignment, making results/settings predictable values. A property looks like an attribute but runs its calculation when read. It does not issue another backend query here. To obtain newer state, call `status()` again.


### 8.5 Errors and their inheritance


```text
RuntimeError
  └─ VPNError (message + returncode)
      ├─ ConfigurationError
      ├─ CredentialError
      ├─ AuthenticationError
      └─ NetworkManagerError
          ├─ ProfileNotFound
          └─ ConnectionBusy
```

Catch `VPNError` for expected public operation failures or a subclass for a particular response. ProfileNotFound can mean setup is needed; a generic NetworkManagerError for duplicates must not be treated as permission to create another profile. `@_operation` preserves existing VPNError subclasses and translates selected import/OS/value/subprocess failures to safe common messages. It does not catch every possible exception, and direct lower-level APIs have their own contracts. The CLI converts these failures to printed text and numeric return codes, retaining backend code 10, for example, when supplied.

## 9 Package branch — new concepts


### 9.1 Package, module, distribution and entry point

A **module** is an importable unit, usually one `.py` file. A **package** groups modules under a namespace, usually a directory with `__init__.py`. `tifrvpn.gui.sso` names the file `src/tifrvpn/gui/sso.py` under nested packages.

A **distribution** is what installation metadata/build tools manage. Its name can differ from the import package: here `tifrvpn-tui` installs `tifrvpn`. The source-layout setting `[tool.uv.build-backend] module-name = 'tifrvpn'` makes that difference explicit.

A **console entry point** declares a generated executable-to-function connection. For example `tifrvpn = 'tifrvpn.cli:main'` means: import the module to the left of the colon and call the function to the right. It is not a filesystem path and the colon does not mean a network port. Installation creates a wrapper using that environment's interpreter; the wrapper is generated output, not a source file this branch needs to maintain at the repository root.

`python -m tifrvpn` asks Python to execute the package's `__main__.py`, which calls the same CLI main. `python -m tifrvpn._sso_worker` selects the private worker module. Running an internal source file directly by pathname can break its relative imports; package/module invocation is the intended model.

The distribution name ending in “tui” is not evidence of a full-screen text UI implementation. This snapshot provides a CLI plus optional GTK/Qt graphical dialogs, and a library that another application could use.


### 9.2 Module-level imports and operation safety

The current source groups imports at the tops of modules. Importing executes module-level imports, definitions and decorators; it is not literally instruction-free. Importing a function loads its definition, while calling it executes its body. The earlier function-local/deferred imports are historical behavior and have been removed from the current source.

Dependencies therefore load sooner: importing the core package needs GI/Secret and cryptography, and importing the CLI also loads Qt/QR libraries. Missing dependencies can fail before a function's later error handling starts. The code still defers actual credential/config reads, process launches, network requests, window creation and camera capture until operations are called. The revised import test supplies dependency interfaces and rejects those application operations during import.

The worker remains an independent process. Its main guard keeps deliberate worker startup and its os._exit path out of ordinary imports. Grouping imports at module scope does not mean launching a GUI or opening a VPN at module scope. Section 15.5 walks through the distinction and the special GI namespace-selection ordering.

### 9.3 Relative imports, re-exports and internal names

`from .config import Config` means the sibling module within the tifrvpn package. `from ..credentials import read_login` inside tifrvpn.gui moves one package level upward. It does not mean “go up from my terminal's current directory.”

`__init__.py` re-exports selected names so users have stable convenient imports such as `from tifrvpn import connect`. `__all__` lists the intended star-import surface; it is not access control. An underscore in `_operation`, `_fields`, `_saved_login` or `_sso_worker` signals implementation detail by convention, not enforced privacy.


### 9.4 Dataclasses, annotations, properties and decorators

**Dataclass:** describes a record through fields; Python generates routine initialization/representation/equality methods. Config normalizes its paths in `__post_init__`, after the generated initializer. It deliberately uses `object.__setattr__` during construction despite being frozen.

**Annotation:** `str | None`, `Path`, `Callable[[str], None]` or `-> VPNStatus` describes expected types for readers/tools. These do not independently validate arbitrary runtime values. Explicit validation remains code you can inspect.

**Property:** `@property` lets `result.connected` or `result.devices` compute a value from stored fields while reading like an attribute. These particular properties do not connect/query again.

**Decorator:** `@_operation` replaces a function with a wrapper that calls the real function and translates expected errors. `@wraps` keeps the original function metadata understandable. Building this wrapper at import does not run the underlying connect operation.

**Keyword-only arguments:** a `*` in the signature requires readable calls such as `connect(quiet=True)`. `*args` and `**kwargs` instead gather/forward positional and named arguments. The same `**` can unpack a dictionary into Config's named fields in the worker.


### 9.5 Normal install, editable install, build and lockfile

A **normal install** installs built package contents into the environment. Editing the checkout does not automatically replace those contents; reinstall to update. An **editable install** registers the source tree so new interpreter processes load its code. Already-imported modules in a running Python process can retain their previous definitions; restarting that process is the straightforward way to use edits.

Editing project metadata, generated entry-point declarations or package layout can still require reinstalling even in editable mode. Switching this editable checkout to main removes the `src/tifrvpn` tree and can make that environment's package/worker fail. Keeping the package checkout stable—or using a separate suitable checkout/worktree when needed—avoids confusing source disappearance with a VPN failure. No worktree or branch was switched during this documentation task.

`pyproject.toml` declares project identity and allowed dependency ranges, including PyGObject. `uv.lock` records selected dependency versions/artifacts, including PyGObject 3.58.1 and Pycairo 1.29.2. The earlier redundant argparse dependency remains removed. `uv build` creates a source distribution and wheel. These are build artifacts, not an upload to a package registry. `py3-none-any` describes this wheel's Python-code packaging compatibility; the actual application still requires Linux/NetworkManager/GI and Linux memfd support.

## 10 Package branch — tests and verification


### 10.1 What was actually checked for this snapshot

After PyGObject was installed through uv, the project's ordinary isolated Python 3.13.18 environment loaded all four GI namespaces: Secret 1, Gtk 3.0, WebKit2 4.1 and Soup 3.0. `uv run python -B -m unittest discover -s tests -q` was repeated during this documentation refresh and passed all 53 test methods.

Targeted Pyright checks for `config.py`, `totp.py` and `gui/qr_import.py` report zero errors/warnings. Ruff's selected TRY004 check for `totp.py` passes. These are targeted checks, not claims that every file passes every possible lint rule or that the whole project is fully typed. A separate offscreen check decoded an in-memory QR containing the public RFC test key, guarded copy before decoding, and verified conditional clipboard cleanup with a mocked clipboard.

The earlier 50-test/build check used a separate system-Python environment; it is historical evidence for the earlier snapshot. It is not the installation route now required. This refresh does not claim a new build artifact or a live TIFR sign-in/tunnel test. Tests and inspection did not read personal vault contents or change a live VPN connection.

### 10.2 Test files, counts and what they establish


| File | Tests | Behaviors checked |
| --- | ---: | --- |
| `test_auth.py` | 4 | Explicit Config reaches child; parent/PYTHONPATH preservation; malformed/failed worker output; portal response rules. |
| `test_cli.py` | 8 | Option order, invalid arguments, help, toggling, status output, backend code preservation, notification gating, safe OTP errors. |
| `test_config.py` | 5 | Defaults/JSON/environment, invalid config, nonprinting login parsing, missing fields, public RFC TOTP vector. |
| `test_imports.py` | 1 | Fake dependency modules permit top-level imports while application subprocess/socket/configuration-read operations are blocked. |
| `test_keyring.py` | 5 | Existing schema/server compatibility, separate browser key, clearing both kinds, safe warnings, clear-failure ordering. |
| `test_networkmanager.py` | 7 | Duplicate/incompatible profiles, original settings, validation, backend status, verified anonymous secret handoff/cleanup. |
| `test_packaging.py` | 4 | Generated commands, module/worker help, argument errors and safe library imports from unrelated directories without PYTHONPATH. |
| `test_quiet.py` | 7 | Unlock/display ordering, missing dependencies, foreground path, X11/group setup, timeout escalation, cancellation, no hidden pinentry. |
| `test_vpn.py` | 9 | Cached/fresh/active/busy/missing/ambiguous cases, failed sign-in/activation and idempotent disconnect. |
| `test_totp.py` | 3 | Decode public-key export fixtures with/without metadata; reject nine malformed-type/multi-part-batch cases using subTest. |
| **Total** | **53** | Offline test methods; individual assertions/input cases are more numerous. Mocks are not live desktop/server verification. |

Each full test function and its lines appear in the source appendix. **Mocks** return invented results and remember calls; **side_effect** can produce exceptions or successive fake states; **subTest** identifies a specific loop scenario; **TemporaryDirectory** isolates files; **patch** restores substitutions after a block or registered cleanup. Fake password/token strings in tests are examples, not personal credentials.

The installation tests intentionally differ from unit tests run only with `PYTHONPATH=src`: they ask this interpreter's real generated executables to work from another directory, and use Python `-I` to ignore environment/user-path contamination. The import test adds `-S` to skip site initialization, supplies the intended source root and fake dependency module interfaces, then blocks application external actions. It now permits imported dependency names instead of treating their import itself as a failure. These flags test import/install contracts, not a sandbox for actual VPN operations.


### 10.3 Repeat the documented checks in the project environment

```sh
cd /home/soham/projects/tifrvpn-tui
uv sync --locked
uv run python -B -m unittest discover -s tests -v
uvx pyright --pythonpath .venv/bin/python src/tifrvpn/config.py src/tifrvpn/totp.py src/tifrvpn/gui/qr_import.py
uvx ruff check --select TRY004 src/tifrvpn/totp.py
git diff --check
```

The explicit Pyright interpreter selects this environment for dependency lookup. The -B option avoids writing bytecode cache files. The unittest command runs existing checks without a real sign-in. `git diff --check` checks patch whitespace; it does not run Python. A passing suite does not prove server form compatibility, a working desktop authorization agent or a successful live tunnel.

To create distributable archives as a separate task, use `uv build`; successful creation is not the same as publishing them.

### 10.4 Earlier configuration-only verification — 8 November 2026

From `/home/soham/projects/tifrvpn-tui`, the following checks were run against the updated working tree:

```sh
uvx pyright src/tifrvpn/config.py
uv run python -B -m unittest discover -s tests -v
git diff --check
```

Pyright reproduced the screenshot's **six errors** before the fix and reported **0 errors, 0 warnings, 0 informations** afterward. At that earlier point the offline suite passed all 50 tests, and `git diff --check` passed. The current snapshot adds three methods for a total of 53, as recorded above. This Pyright result covers `config.py`; it is not a package-wide type-check result. These checks did not include a live VPN sign-in or tunnel test.

## 11 Package branch — troubleshooting and maintenance


### 11.1 I am on the package branch, but the old command still runs

Git branch state selects source; the shell selects executables independently. Inspect `type -a tifrvpn`, the active interpreter and `tifrvpn.__file__`. Activate the intended environment or invoke its full `bin/tifrvpn`/`bin/python -m tifrvpn` path. Your observed `~/bin/tifr` copies remain main's implementation and are not automatically upgraded by checkout/commit.


### 11.2 Why does `import tifrvpn` or the worker module fail?

Check that the project is installed into the **same interpreter** running the command. A src layout is not automatically on every Python search path just because your terminal is inside the repository. The current worker deliberately relies on installation rather than the removed manual PYTHONPATH injection. An editable source checkout switched to main or moved/deleted can break its registered path; reinstall or restore a suitable package checkout as appropriate.


### 11.3 Why do GI/GTK/WebKit/Secret imports fail in my environment?

`import gi` is supplied by the Python distribution PyGObject. In the current checkout, `uv sync --locked` installs it inside the isolated Python 3.13 environment. Confirm the actual interpreter and import location with `uv run python -c 'import sys, gi; print(sys.executable); print(gi.__file__)'`.

If installation fails while compiling PyGObject/Pycairo, check native development libraries, compiler and Python headers. If gi imports but a namespace is unavailable, check that namespace's native runtime/introspection package and requested version. Python 3.14 and system-site-packages are not needed for the final uv route. Optional editor stubs do not fix missing runtime bindings. Since imports are now at module scope, missing dependencies can fail as soon as a module is imported; see sections 15.1–15.5 for the full explanation.

### 11.4 Why does a fresh quiet sign-in stop or show messages late?

Known form errors or a session-replacement decision require visible review; retry `tifrvpn -c`. Other required interaction can hit the browser deadline. GPG unlocking happens before the quiet timer. Current child stderr is captured and forwarded after completion, so late grouped progress is explained by code rather than necessarily a frozen VPN. Desktop keyring prompts are another independent service interaction.


### 11.5 Which setup action do I repeat after changing something?

**Only source changed:** editable code is used by new interpreter processes; normal installs need reinstall. **Metadata/entry points changed:** reinstall to refresh generated commands and registration. **Vault master password changed:** run `tifr-otp --setup` to replace its GPG ciphertext after local verification. **TIFR account password changed:** update/save the KeePass entry; a later fresh sign-in reads the saved value. **Vault path/entry changed:** update selected config/environment/direct Config. **TOTP enrollment changed:** import/store the newly enrolled seed/settings and compare codes. **Profile settings wrong:** run `tifrvpn --setup` and resolve duplicate/incompatible names if reported. These are different changes with different repair points.


### 11.6 Why is an inactive status an error code, and can I repeatedly disconnect?

The library returns a status object for ordinary inactive/not-configured cases. CLI status uses code 1 to let shell automation test whether the connection is active. Disconnect treats missing/inactive state as a successful no-op, returning changed=False. This distinction is intentional and covered by tests; it is not a requirement to recreate the profile every day.


### 11.7 Concrete remaining assumptions and limits

- The backend still checks `/usr/libexec/nm-openconnect-service`; other Linux layouts may require adapting that assumption. Several error hints use Fedora's dnf package names.
- The fixed portal, hostname and Keycloak realm/form selectors are TIFR-specific. Server page changes can require code maintenance.
- Automatic OTP timing and migration decoding assume a 30-second period. CLI output validation accepts 6–8 ASCII digits.
- A frozen Config/result is a programming model, not a guarantee against deliberately bypassing it; type annotations do not replace explicit input checks.
- `get_code()` and GUI operations are synchronous and may prompt. Import safety does not make later credential/network calls side-effect-free or nonblocking.
- Ephemeral WebKit profile storage is separate from deliberately remembered selected cookies in the desktop keyring. A silent callback-less controller can still involve external service dialogs.
- NetworkManager `_run` may use its backend stderr in a typed error. The code keeps its own secret payload out of argv/ordinary progress, but callers should still inspect diagnostics before sharing personal networking information.
- GUI/QR library imports are at module scope. Those Python/native dependencies must be available when the corresponding modules load, even if a later GUI operation is not requested.
- The example config is now present; the unfilled license year/name placeholders remain unchanged. Old main observations should be read in their historical section.


### 11.8 Review and understand the refactor

- [ ] Explain the difference between Git branch, distribution name, import name and executable name.
- [ ] Find which executable and interpreter your shell actually selects.
- [ ] Trace the generated command through cli.main → vpn.connect → auth/networkmanager.
- [ ] Explain which old function moved into each new module and what boundary that creates.
- [ ] Describe a fresh login and a cached reconnect separately.
- [ ] Explain why `Config` loading is separate from runtime vault/GPG validation.
- [ ] Read VPNStatus.changed versus connected, and identify which ones are stored fields/properties.
- [ ] Explain why the library raises errors and the CLI returns exit statuses.
- [ ] Distinguish worker config paths from actual passwords/tokens.
- [ ] Explain why the private worker remains a subprocess despite the package becoming importable.
- [ ] Recognize buffered worker progress as a current difference from main.
- [ ] Explain why `PYTHONPATH=src` is weaker evidence than installed commands passing from another directory.
- [ ] Read the current source sections relevant to the feature you want to change before editing it.

### 11.9 Why does the editor report `str | None` in `config.py`?

The JSON validation loop checks every supplied value, but Pyright does not infer a `dict[str, str]` from that loop. Its inferred optional values trigger errors at `Path(...)`, `entry.strip()` and `Config(...)`. The fix imports `cast` and adds `settings = cast(dict[str, str], settings)` immediately after successful JSON validation. The cast records the already-checked type; it does not convert values or replace validation. See [[#13.5 Package source — src/tifrvpn/config.py|the updated source and line-by-line explanation]] and [[#10.4 Earlier configuration-only verification — 8 November 2026|verification results]].

## 12 Package branch — references

The recorded commit history, exact current source and targeted/offline checks are evidence for project-specific statements. These primary references explain the language/packaging mechanisms used:

- [Python packaging installation tutorial](https://packaging.python.org/en/latest/tutorials/installing-packages/) — environments and installing distributions.
- [pip local project installs](https://pip.pypa.io/en/stable/topics/local-project-installs/) — normal versus editable installs and reinstall considerations.
- [Entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/) — generated console-script-to-function behavior.
- [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/) — source layout and module-name configuration.
- [Python venv](https://docs.python.org/3.13/library/venv.html) — interpreter selection, activation and system-site-packages.
- [Python dataclasses](https://docs.python.org/3.13/library/dataclasses.html) — generated record methods, frozen objects and post-initialization.
- [Python packages](https://docs.python.org/3.13/tutorial/modules.html#packages) — package namespaces and relative imports.
- [Python unittest](https://docs.python.org/3.13/library/unittest.html) and [unittest.mock](https://docs.python.org/3.13/library/unittest.mock.html) — regression checks, patches and fake call histories.
- [PyGObject installation](https://pygobject.gnome.org/getting_started.html#fedora) — Python bindings and native build/runtime prerequisites.
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) — synchronize the isolated environment from the lockfile.
- [Ruff TRY004](https://docs.astral.sh/ruff/rules/type-check-without-type-error/) — the general type-check exception recommendation.
- [Qt QApplication](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QApplication.html) — widget application behavior.
- [Git: recording changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) — working tree, staging area and commits.
- [Obsidian heading folding](https://obsidian.md/help/folding) — collapse file or function headings to keep the source reference compact.

The complete current source follows. The original main source remains embedded in [[TIFR Vpn TUI|the original guide]]; both guides can be read without the live source checkout at its original filesystem path.

## 13 Package branch — every current file

This section embeds the exact 34-file snapshot at **589be0d**, separately from the historical main snapshots. It includes the new decoder test file. Refreshed sections divide source into short numbered pieces; the pieces are consecutive parts of one file, not independent scripts to execute separately. Every nonblank code line has an explanation; wrapped lines in one statement can share a labeled range. Blank source lines are retained. File overviews explain responsibility; function/test summaries explain purpose; the function and step subsections contain the exact source and its line-by-line notes.

### 13.1 Package source — src/tifrvpn/__init__.py


The public front door of the importable library. It re-exports the settings type, common error, status type and connection operations. Importing this file loads Python definitions; it does not itself call status/connect, read configuration, start programs, open windows or contact a server. The current import test supplies fake dependency interfaces and checks that importing submodules does not start application external operations.


#### 13.1.1 L1–L20 · Module documentation, imports and shared definitions


```python
"""TIFR VPN library and command-line tools.

Importing the package performs no credential, network, or GUI operations.
"""

from .config import Config, load_config
from .errors import VPNError
from .vpn import VPNStatus, connect, disconnect, forget_login, setup, status

__all__ = [
    "Config",
    "VPNError",
    "VPNStatus",
    "connect",
    "disconnect",
    "forget_login",
    "load_config",
    "setup",
    "status",
]
```

**Line-by-line explanation**

- **L1** — Module docstring documents the intended import contract: loading names must be safe independently of doing a VPN operation. Import is an action Python performs to load definitions; it is different from calling connect().
- **L3–L4** — Module docstring documents the intended import contract: loading names must be safe independently of doing a VPN operation. Import is an action Python performs to load definitions; it is different from calling connect().
- **L6** — Re-export Config and load\_config from the sibling config module. The leading dot means a relative import within the same tifrvpn package; it does not mean the current terminal directory.
- **L7** — Expose the common VPNError so application code can catch expected VPN failures without importing private details.
- **L8** — Re-export the status data type and all five public operations from vpn.py. Users can write tifrvpn.connect() rather than knowing the internal module layout.
- **L10** — Begin the explicit public-name list. \_\_all\_\_ controls star-import exposure and documents the supported public surface; it does not stop explicit imports of other module names.
- **L11** — Publish the Config settings object type.
- **L12** — Publish the common VPNError exception type.
- **L13** — Publish VPNStatus, the structured result type.
- **L14** — Publish connect, which synchronously connects and returns VPNStatus.
- **L15** — Publish disconnect, which synchronously disconnects and returns VPNStatus.
- **L16** — Publish forget\_login, which clears saved sessions without disconnecting.
- **L17** — Publish load\_config, which explicitly reads settings when called.
- **L18** — Publish setup, which prepares a NetworkManager profile and returns its UUID.
- **L19** — Publish status, which queries connection state and returns VPNStatus.
- **L20** — Close the public-name list. No operation is invoked by listing its name here.


[[#4 Package branch — file map|↑ Package file map]]

### 13.2 Package source — src/tifrvpn/__main__.py


The module-execution adapter. Python uses this file for python -m tifrvpn. Both that command and the installed tifrvpn console script call the same cli.main function, so argument behavior has one implementation.


#### 13.2.1 L1–L6 · Module documentation, imports and shared definitions


```python
"""Run the same CLI as the tifrvpn command."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

**Line-by-line explanation**

- **L1** — Docstring records that module invocation and the installed command share behavior.
- **L3** — Import the sibling CLI main function without calling it.
- **L5** — Only execute the following entry point when Python runs this module as a program. Importing tifrvpn.\_\_main\_\_ during tests does not exit the caller.
- **L6** — Call main, then raise SystemExit with the returned integer status. This process exit belongs at the CLI boundary, while ordinary library operations raise errors or return objects.


[[#4 Package branch — file map|↑ Package file map]]

### 13.3 Package source — src/tifrvpn/vpn.py


The public orchestration layer: it chooses the sequence of backend operations and returns structured results. Main’s tifr-on/off/status and authentication main flow are reorganized here. It does not format terminal output, send desktop notifications or call sys.exit. Progress goes to an optional callback; expected problems become VPNError subclasses. Operations are synchronous and may still perform network work or display necessary sign-in/GPG dialogs when actually called.

**Relation to main:** [[TIFR Vpn TUI#7.1 tifrvpn|tifrvpn]] — Shell connect/disconnect/status decisions plus authentication-controller sequencing become reusable Python operations.

**Functions and their purpose**

- **\_operation**, L14–L30: Define an internal decorator that wraps a public operation with a consistent failure boundary. A leading underscore marks internal intent; it does not make the function inaccessible.
- **\_operation.run**, L16–L28: Accept arbitrary positional and keyword arguments and forward them to the real operation.
- **VPNStatus.connected**, L41–L42: Declare the computed boolean property.
- **VPNStatus.devices**, L45–L54: Annotate a tuple of zero or more strings; ... means variable tuple length in this type expression.
- **\_emit**, L57–L59: Define the shared progress-emission helper.
- **status**, L63–L71: Read connection state; an absent profile has state not-configured.
- **setup**, L75–L79: Create/update the user-specific OpenConnect profile and return its UUID.
- **connect**, L83–L122: Connect synchronously, reusing a valid saved session when possible.

Quiet mode hides the browser in Xvfb; GPG may still prompt on the desktop.
Progress is delivered to on\_progress, and expected failures raise VPNError.
- **disconnect**, L126–L137: Disconnect an active/transitional profile; safe to repeat.
- **forget\_login**, L141–L143: Clear saved browser and VPN sessions without changing an active tunnel.


#### 13.3.1 L1–L13 · Module documentation, imports and shared definitions


```python
"""Public VPN operations. No terminal output or process exits occur here."""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

from . import auth, keyring
from . import networkmanager as nm
from .config import Config
from .errors import ConnectionBusy, NetworkManagerError, ProfileNotFound, VPNError
```

**Line-by-line explanation**

- **L1** — State the separation between reusable VPN operations and terminal presentation/process exit.
- **L3** — Import subprocess exception types so unexpected child-program failures can be normalized.
- **L4** — Import Callable for progress-callback type annotations.
- **L5** — Import dataclass for the immutable status record.
- **L6** — Import wraps so a decorator preserves the wrapped operation's name, documentation and introspection metadata.
- **L8** — Import authentication/session-storage modules without calling their operations.
- **L9** — Give networkmanager the short local alias nm, making orchestration calls readable.
- **L10** — Import the Config type used in connect's optional settings parameter.
- **L11** — Import the typed failure categories needed for recoverable missing profiles, busy transitions and general error conversion.


#### 13.3.2 L14–L14 · _operation


```python
def _operation(function):
```

**Line-by-line explanation**

- **L14** — Define an internal decorator that wraps a public operation with a consistent failure boundary. A leading underscore marks internal intent; it does not make the function inaccessible.


#### 13.3.3 L15–L32 · _operation.run


```python
    @wraps(function)
    def run(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except VPNError:
            raise
        except ImportError:
            raise VPNError(
                "Required Python or system bindings are missing; see README.md."
            ) from None
        except (OSError, ValueError, subprocess.SubprocessError):
            raise VPNError(
                "Could not prepare the VPN session; check dependencies and configuration."
            ) from None

    return run
```

**Line-by-line explanation**

- **L15** — Copy the wrapped function's metadata to the inner function using functools.wraps.
- **L16** — Accept arbitrary positional and keyword arguments and forward them to the real operation.
- **L17** — Begin handling failures raised during that operation.
- **L18** — Run the actual function and return its result unchanged on success.
- **L19–L20** — Reraise an existing VPNError unchanged so its more precise type, message and backend returncode survive.
- **L21–L24** — Convert a missing imported dependency into a generic readable VPNError rather than leaking import details through the public interface.
- **L25–L28** — Convert expected OS, parsing/value and subprocess failures into a safe common error without raw backend exception details. Other exception categories are not universally swallowed by this decorator.
- **L30** — Return the wrapper function. Using @\_operation replaces each decorated operation name with this wrapper.


#### 13.3.4 L33–L39 · VPNStatus — type/state/test structure


```python
@dataclass(frozen=True)
class VPNStatus:
    state: str
    profile_uuid: str | None = None
    details: str = ""
    changed: bool = False
```

**Line-by-line explanation**

- **L33** — Generate a frozen dataclass: result fields can be read and compared without ordinary reassignment.
- **L34** — Define VPNStatus, the return type of status/connect/disconnect.
- **L35** — Store the original NetworkManager state string, preserving transitions such as activating rather than flattening everything into a boolean.
- **L36** — Store the profile UUID or None when no profile exists. str | None is a union type annotation.
- **L37** — Store raw selected nmcli detail text, defaulting to empty when details were not requested/available.
- **L38** — Record whether this operation actually changed connection state. This is not a live watcher of future changes.


#### 13.3.5 L40–L43 · VPNStatus.connected


```python
    @property
    def connected(self) -> bool:
        return self.state == "activated"
```

**Line-by-line explanation**

- **L40** — Expose the next method as a computed attribute, allowing result.connected instead of result.connected().
- **L41** — Declare the computed boolean property.
- **L42** — Only the exact activated state counts as connected.


#### 13.3.6 L44–L56 · VPNStatus.devices


```python
    @property
    def devices(self) -> tuple[str, ...]:
        for line in self.details.splitlines():
            name, separator, value = line.partition(":")
            if separator and name.strip() == "GENERAL.DEVICES":
                return tuple(
                    item.strip()
                    for item in value.split(",")
                    if item.strip() and item.strip() != "--"
                )
        return ()
```

**Line-by-line explanation**

- **L44** — Expose device parsing as another computed property.
- **L45** — Annotate a tuple of zero or more strings; ... means variable tuple length in this type expression.
- **L46** — Inspect the stored nmcli detail output one line at a time.
- **L47** — Split at the first colon into field name, separator marker and field value. partition always returns three strings, even if no colon exists.
- **L48** — Only parse the GENERAL.DEVICES field when its separator exists.
- **L49–L53** — Split comma-separated devices, strip whitespace, discard empty placeholders and '--', and return an immutable tuple. This parses saved details rather than issuing another command.
- **L54** — Return an empty tuple when no usable device field is present.


#### 13.3.7 L57–L61 · _emit


```python
def _emit(callback, message):
    if callback is not None:
        callback(message)
```

**Line-by-line explanation**

- **L57** — Define the shared progress-emission helper.
- **L58** — Check whether the caller supplied a callback.
- **L59** — Call it with one readable message. This is an ordinary synchronous function call and can execute the caller's own code.


#### 13.3.8 L62–L73 · status


```python
@_operation
def status() -> VPNStatus:
    """Read connection state; an absent profile has state not-configured."""
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        return VPNStatus("not-configured")
    state = nm.state(uuid) or "disconnected"
    return VPNStatus(state, uuid, nm.details(uuid) if state == "activated" else "")
```

**Line-by-line explanation**

- **L62** — Wrap status with the common error conversion decorator.
- **L63** — Define a parameterless public state query returning VPNStatus.
- **L64** — Document the explicit not-configured result for an absent profile.
- **L65** — Check required tools and that NetworkManager responds.
- **L66–L67** — Attempt to identify the saved profile.
- **L68–L69** — Represent recoverable profile absence as VPNStatus('not-configured'), rather than automatically creating anything during a read-only status query.
- **L70** — Read the backend state, using disconnected if it returns an empty value.
- **L71** — Return state and UUID; query details only for activated connections. This avoids printing or returning a process exit status from the library.


#### 13.3.9 L74–L81 · setup


```python
@_operation
def setup(*, on_progress: Callable[[str], None] | None = None) -> str:
    """Create/update the user-specific OpenConnect profile and return its UUID."""
    uuid = nm.setup_profile(on_progress=on_progress)
    _emit(on_progress, "✔ tifr VPN: Ivanti profile ready (NetworkManager/OpenConnect)")
    return uuid
```

**Line-by-line explanation**

- **L74** — Apply the public-operation error boundary to setup.
- **L75** — Accept an optional keyword-only progress callback and declare that setup returns the profile UUID as text.
- **L76** — Document that setup prepares a recipe, not necessarily an active tunnel.
- **L77** — Ask the NetworkManager backend to create/update the profile, forwarding progress handling.
- **L78** — Emit the successful-profile message only through the supplied callback.
- **L79** — Return the selected UUID for programmatic callers.


#### 13.3.10 L82–L113 · connect · section 1


```python
@_operation
def connect(
    *,
    quiet: bool = False,
    config: Config | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> VPNStatus:
    """Connect synchronously, reusing a valid saved session when possible.

    Quiet mode hides the browser in Xvfb; GPG may still prompt on the desktop.
    Progress is delivered to on_progress, and expected failures raise VPNError.
    """
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        uuid = setup(on_progress=on_progress)
    state = nm.state(uuid)
    if state == "activated":
        return status()
    if state and state != "deactivated":
        raise ConnectionBusy(f"{state}; wait or run tifrvpn -d before retrying.")
    _emit(on_progress, "⋯ tifr VPN: checking saved sign-in for sslvpn.tifr.res.in")
    nm.validate_profile(uuid)
    cookie = keyring.load_session(on_progress=on_progress)
    if cookie and auth.valid_session(cookie):
        _emit(on_progress, "tifr VPN: reusing saved session")
    else:
        if cookie:
            keyring.clear_session(on_progress=on_progress)
            _emit(
                on_progress,
```

**Line-by-line explanation**

- **L82** — Apply the public-operation error boundary to connect.
- **L83–L88** — Define connect with keyword-only quiet=False, optional Config and optional one-string progress callback; return VPNStatus. Defaults let CLI/library callers choose the normal settings workflow.
- **L89** — Document synchronous behavior, cache reuse, possible GPG prompting, callback progress and catchable failures. A library call can still open a GUI when a fresh sign-in needs one.
- **L91–L93** — Document synchronous behavior, cache reuse, possible GPG prompting, callback progress and catchable failures. A library call can still open a GUI when a fresh sign-in needs one.
- **L94** — Check the runtime tools and service before any vault/session work.
- **L95–L96** — Find the saved connection profile by its name and require a unique UUID.
- **L97–L98** — Only an actual ProfileNotFound exception triggers profile setup. Ambiguous names raise a different error and must not create another duplicate.
- **L99** — Read the current state before signing in.
- **L100–L101** — If already activated, return a fresh status result without reading credentials, signing in or activating again; changed remains False.
- **L102–L103** — Reject a nonempty transitional/other nondeactivated state with ConnectionBusy before touching credentials.
- **L104** — Emit a safe session-checking message through the callback.
- **L105** — Validate the profile's service, gateway and protocol before feeding session data to it.
- **L106** — Try retrieving the helper's cached VPN cookie from the desktop keyring.
- **L107–L108** — If a cookie exists and the gateway accepts it, emit cache-reuse progress and bypass new browser/vault access.
- **L109** — Otherwise use the fresh-authentication branch.
- **L110–L113** — If an old cookie existed but failed validation, remove it and explain expiry through the optional callback.


#### 13.3.11 L114–L124 · connect · section 2


```python
                "tifr VPN: saved session expired; TIFR requires sign-in again.",
            )
        cookie = auth.authenticate(quiet=quiet, config=config, on_progress=on_progress)
        keyring.save_session(cookie, on_progress=on_progress)
    nm.activate(uuid, cookie, on_progress=on_progress)
    result = status()
    if not result.connected:
        raise NetworkManagerError(f"{result.state}")
    return VPNStatus(result.state, result.profile_uuid, result.details, changed=True)
```

**Line-by-line explanation**

- **L114–L115** — If an old cookie existed but failed validation, remove it and explain expiry through the optional callback.
- **L116** — Obtain a fresh session, forwarding quiet mode, explicit Config if supplied, and the callback.
- **L117** — Attempt to cache the new cookie for later use. A keyring backend warning can be reported without making current activation impossible.
- **L118** — Pass the cookie and UUID to the actual tunnel backend; this is where activation begins.
- **L119** — Query the resulting state after activation returns.
- **L120–L121** — Do not report success if the queried state is not activated; raise a NetworkManagerError instead.
- **L122** — Return a new status record with changed=True because this call started the connection. The device property is computed from the returned detail text.


#### 13.3.12 L125–L139 · disconnect


```python
@_operation
def disconnect(*, on_progress: Callable[[str], None] | None = None) -> VPNStatus:
    """Disconnect an active/transitional profile; safe to repeat."""
    nm.require_available()
    try:
        uuid = nm.profile_uuid()
    except ProfileNotFound:
        return VPNStatus("not-configured")
    state = nm.state(uuid)
    if not state or state == "deactivated":
        return VPNStatus("deactivated", uuid)
    nm.deactivate(uuid, on_progress=on_progress)
    return VPNStatus("deactivated", uuid, changed=True)
```

**Line-by-line explanation**

- **L125** — Apply common public-error handling to disconnect.
- **L126** — Define synchronous disconnect with optional progress and a structured result.
- **L127** — Document that it can be safely repeated: missing/inactive states do not need another down operation.
- **L128** — Require available networking tools/service.
- **L129–L130** — Find the existing profile.
- **L131–L132** — Return not-configured if it is absent; do not create a profile merely to disconnect.
- **L133** — Read its current state.
- **L134–L135** — An empty/deactivated state returns a deactivated result with changed=False and no backend down command.
- **L136** — For active/transitional states, ask the backend to deactivate the exact profile UUID.
- **L137** — Return deactivated with changed=True after successful deactivation.


#### 13.3.13 L140–L143 · forget_login


```python
@_operation
def forget_login() -> None:
    """Clear saved browser and VPN sessions without changing an active tunnel."""
    keyring.clear_saved_login()
```

**Line-by-line explanation**

- **L140** — Apply common error handling to cached-session clearing.
- **L141** — Define forget\_login; -> None means it has no meaningful returned value on success.
- **L142** — Clarify that cache clearing leaves a running tunnel alone.
- **L143** — Clear both saved browser and VPN session kinds through the dedicated keyring adapter.


[[#4 Package branch — file map|↑ Package file map]]

### 13.4 Package source — src/tifrvpn/cli.py

Terminal adapters format messages and dispatch commands to the reusable library. Imports are now grouped at module scope, including the two Qt helper entry points. Consequently the command module requires those dependencies even for help; loading functions is separate from invoking VPN, vault or GUI operations.

**Relation to main:** [[TIFR Vpn TUI#7.1 tifrvpn|tifrvpn]] — Zsh dispatch/output/notifications are rewritten as Python adapters, together with old OTP/importer CLI entry points.

**Functions and their purpose**

- **_progress**, L25–L44: Define the progress callback the CLI passes to library operations. A caller embedding the library can supply a different callback or omit it.
- **_notify**, L47–L56: Define optional desktop notification delivery; this is presentation behavior, not a library-side state change.
- **_show_status**, L59–L69: Format a structured VPNStatus as terminal output and return a CLI status number.
- **_connect**, L72–L77: Define the command adapter for connect. It receives the parsed quiet boolean, not raw command text.
- **_disconnect**, L80–L89: Define the command adapter for disconnect.
- **_vpn_main**, L92–L146: Define VPN argument parsing/dispatch separately from its outer exception handler. Passing argv explicitly makes offline tests easy.
- **main**, L149–L178: Define the installed tifrvpn command entry point; an optional explicit argv is useful to tests/embedding adapters.
- **otp_main**, L181–L218: Define the installed tifr-otp entry point. It shares credential functions with the library, adding explicit terminal code output and setup dialogs.
- **import_totp_main**, L221–L238: Define the installed tifr-import-totp entry point.

#### 13.4.1 L1–L24 · Module setup and definitions

```python
"""Terminal adapters for the public library and the optional GUI tools."""

import argparse
import subprocess
import sys

from . import credentials, vpn
from . import networkmanager as nm
from .config import load_config
from .errors import ConnectionBusy, ProfileNotFound, VPNError
from .gui.credential_setup import setup
from .gui.qr_import import run

USAGE = "Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login|--help]"
HELP = """Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login] (no option: toggle)
Server: https://sslvpn.tifr.res.in/tifruser (Ivanti SSL VPN)
Reuses a valid saved session; otherwise fills TIFR SSO from KeePassXC/GPG.
TIFR may ask you to confirm replacing another active session.
--quiet hides the SSO browser using Xvfb (120-second limit); terminal messages remain visible.
--quiet alone connects. GPG can prompt before background sign-in; retry without --quiet if TIFR needs input.
--forget-login clears remembered sign-in state from the desktop keyring.
TOTP from KeePassXC/GPG: tifr-otp (first run: tifr-otp --setup)"""


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import argparse at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import subprocess at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import sys at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L7** — Bind credentials, vpn from . at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Bind networkmanager as nm from . at module scope. These names are then available to the functions below without a function-local import.
- **L9** — Bind load_config from .config at module scope. These names are then available to the functions below without a function-local import.
- **L10** — Bind ConnectionBusy, ProfileNotFound, VPNError from .errors at module scope. These names are then available to the functions below without a function-local import.
- **L11** — Bind setup from .gui.credential_setup at module scope. These names are then available to the functions below without a function-local import.
- **L12** — Bind run from .gui.qr_import at module scope. These names are then available to the functions below without a function-local import.
- **L14** — Store short usage text once so invalid-option paths share the same syntax description.
- **L15–L22** — Store the multiline --help text. These are literal display lines, not operations executed when the module is imported. They retain user-facing main-branch commands while their implementation is reorganized.

#### 13.4.2 L25–L46 · _progress

```python
def _progress(message):
    # Color status symbols consistently, including redirected output.
    for symbol, color in (("✔", 32), ("●", 32), ("⋯", 33), ("○", 33)):
        if message.startswith(symbol):
            message = f"\033[{color}m{symbol}\033[39m" + message[1:]
            break
    if any(
        text in message
        for text in (
            "desktop keyring unavailable",
            "signing in in the background",
            "submitting saved",
            "SSO reported an error",
            "automatic sign-in",
            "browser session could not be remembered",
        )
    ):
        print(message, file=sys.stderr, flush=True)
    else:
        print(message, flush=True)


```

**Line-by-line explanation**

- **L25** — Define the progress callback the CLI passes to library operations. A caller embedding the library can supply a different callback or omit it.
- **L26** — Explain the choice to color state markers even when output is redirected; this code does not first test isatty.
- **L27** — Map the four display symbols to ANSI color codes: 32 for green and 33 for yellow.
- **L28** — Only recolor messages starting with one of those markers.
- **L29** — Wrap the first symbol in ANSI foreground escape sequences and append the rest of the message. message\[1:\] excludes the original first Unicode character.
- **L30** — Stop searching once that starting symbol was handled.
- **L31–L41** — Classify selected diagnostics/browser progress by substring membership. any(...) returns true for the first matching category; this determines stdout versus stderr, not whether authentication succeeded.
- **L42** — Print those diagnostic/progress categories to stderr and flush immediately once the callback receives them.
- **L43–L44** — Print other progress to stdout, also flushing. Worker messages may already have been buffered until the child finished before this callback receives them.

#### 13.4.3 L47–L58 · _notify

```python
def _notify(message):
    try:
        subprocess.run(
            ["notify-send", "-a", "tifrvpn", "tifr VPN", message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


```

**Line-by-line explanation**

- **L47** — Define optional desktop notification delivery; this is presentation behavior, not a library-side state change.
- **L48–L54** — Invoke notify-send with application/title/message arguments, ignore its nonzero exit status and discard both output streams.
- **L55–L56** — Ignore an OS error such as notify-send being absent, so notification availability does not turn a successful VPN operation into a failed one.

#### 13.4.4 L59–L71 · _show_status

```python
def _show_status(result):
    if result.state == "not-configured":
        print("tifr VPN: not configured; run tifrvpn --setup")
        return 1
    if not result.connected:
        print(f"tifr VPN: {result.state}")
        return 1
    _progress("● tifr VPN: Connected (Ivanti/OpenConnect)")
    if result.details:
        print(result.details)
    return 0


```

**Line-by-line explanation**

- **L59** — Format a structured VPNStatus as terminal output and return a CLI status number.
- **L60–L62** — An absent profile prints a setup instruction and returns nonactive status 1.
- **L63–L65** — Any other nonconnected state prints its exact value and returns 1.
- **L66** — Print the green connected message through the common CLI progress formatter.
- **L67–L68** — Show NetworkManager details when the result includes them.
- **L69** — Return CLI success for an activated connection.

#### 13.4.5 L72–L79 · _connect

```python
def _connect(quiet):
    result = vpn.connect(quiet=quiet, on_progress=_progress)
    code = _show_status(result)
    if not code and result.changed:
        _notify("Connected")
    return code


```

**Line-by-line explanation**

- **L72** — Define the command adapter for connect. It receives the parsed quiet boolean, not raw command text.
- **L73** — Call the public library operation and select \_progress as its readable-message callback.
- **L74** — Format its structured result and retain the resulting exit status.
- **L75** — Only announce a connection when the connection succeeded and this request actually changed tunnel state.
- **L76** — Send the optional desktop notification after a newly successful connection.
- **L77** — Return the display/connection status to the entry point.

#### 13.4.6 L80–L91 · _disconnect

```python
def _disconnect():
    result = vpn.disconnect(on_progress=_progress)
    if result.state == "not-configured":
        print("tifr VPN: no tifr-ivanti profile; nothing to disconnect.")
    elif result.changed:
        _progress("○ tifr VPN: Disconnected")
        _notify("Disconnected")
    else:
        print("tifr VPN: already disconnected")
    return 0


```

**Line-by-line explanation**

- **L80** — Define the command adapter for disconnect.
- **L81** — Run library disconnect with CLI progress reporting.
- **L82–L83** — Explain a missing profile as nothing to disconnect.
- **L84–L86** — If this operation actually changed state, print Disconnected and attempt a desktop notification.
- **L87–L88** — Otherwise print already disconnected rather than announcing another state change.
- **L89** — Disconnecting an absent/inactive connection is successful, so return 0.

#### 13.4.7 L92–L123 · _vpn_main

```python
def _vpn_main(argv):
    action = None
    quiet = False
    for argument in argv:
        if argument == "--quiet":
            quiet = True
        elif argument in (
            "-c",
            "-d",
            "-s",
            "--setup",
            "--forget-login",
            "-h",
            "--help",
        ):
            if action is not None:
                print(
                    "Choose one action: -c, -d, -s, --setup, --forget-login or --help.",
                    file=sys.stderr,
                )
                return 2
            action = argument
        else:
            print(USAGE, file=sys.stderr)
            return 2
    if quiet:
        if action is not None and action != "-c":
            print("--quiet is only supported when connecting (-c).", file=sys.stderr)
            return 2
        action = "-c"
    if action in ("-h", "--help"):
        print(HELP)
```

**Line-by-line explanation**

- **L92** — Define VPN argument parsing/dispatch separately from its outer exception handler. Passing argv explicitly makes offline tests easy.
- **L93** — Initialize no selected action.
- **L94** — Initialize the quiet flag as off.
- **L95** — Inspect each supplied argument in its original order.
- **L96–L97** — Recognize --quiet as a modifier; defer acting until the entire list has been validated.
- **L98–L106** — Recognize the supported main actions: connect, disconnect, status, profile setup, cache clearing and either help spelling.
- **L107–L112** — Reject a second selected action, including repetitions; print the readable error to stderr and return argument-error status 2.
- **L113** — Remember the recognized action for later dispatch.
- **L114–L116** — Reject any unknown argument before running a VPN operation.
- **L117** — After parsing, apply quiet-mode action rules.
- **L118–L120** — Reject quiet with any explicit nonconnect action and explain the allowed use on stderr.
- **L121** — Make --quiet alone choose connect.
- **L122–L123** — Print help and succeed without requiring NetworkManager or opening credentials.

#### 13.4.8 L124–L148 · _vpn_main

```python
        return 0
    if action == "--setup":
        vpn.setup(on_progress=_progress)
        return 0
    if action == "--forget-login":
        vpn.forget_login()
        print("tifr VPN: saved sign-in state cleared; an active tunnel is unaffected.")
        return 0
    if action == "-s":
        return _show_status(vpn.status())
    if action == "-d":
        return _disconnect()
    if action == "-c":
        return _connect(quiet)
    # No arguments: retain the original toggle, including transitional states.
    nm.require_available()
    try:
        state = nm.state(nm.profile_uuid())
    except ProfileNotFound:
        state = ""
    if state and state != "deactivated":
        return _disconnect()
    return _connect(False)


```

**Line-by-line explanation**

- **L124** — Print help and succeed without requiring NetworkManager or opening credentials.
- **L125–L127** — For --setup, call library setup with CLI progress and return success.
- **L128–L131** — For --forget-login, clear cached state, explain that a running tunnel is unaffected, and return success.
- **L132–L133** — For -s, query structured status and convert it to terminal output/exit status.
- **L134–L135** — For -d, run the disconnect adapter.
- **L136–L137** — For -c, run the connect adapter with the validated quiet flag.
- **L138** — Comment identifies the no-argument fallback as preservation of main's original toggle behavior, including transitional states.
- **L139** — Check networking tools/service before querying toggle state.
- **L140–L141** — Find the profile and obtain its current state.
- **L142–L143** — An absent profile is treated as no existing connection state for toggle, allowing connect to create it later.
- **L144–L145** — Any nonempty state other than deactivated chooses disconnect; this includes activating transitions.
- **L146** — Otherwise choose ordinary visible-mode connect. Quiet alone was already explicitly dispatched above.

#### 13.4.9 L149–L180 · main

```python
def main(argv=None):
    try:
        return _vpn_main(sys.argv[1:] if argv is None else argv)
    except KeyboardInterrupt:
        print("\ntifr VPN: cancelled", file=sys.stderr)
        return 130
    except ConnectionBusy as error:
        print(f"tifr VPN: {error}")
        return error.returncode
    except VPNError as error:
        message = str(error)
        print(
            message
            if message.startswith("Install dependencies")
            else f"tifr VPN: {message}",
            file=sys.stderr,
        )
        return error.returncode
    except ImportError:
        print(
            "tifr VPN: install dependencies: sudo dnf install python3-gobject webkit2gtk4.1 python3-cryptography",
            file=sys.stderr,
        )
        return 1
    except (ValueError, OSError, subprocess.SubprocessError):
        print(
            "tifr VPN: could not prepare the VPN session; check the preceding errors.",
            file=sys.stderr,
        )
        return 1


```

**Line-by-line explanation**

- **L149** — Define the installed tifrvpn command entry point; an optional explicit argv is useful to tests/embedding adapters.
- **L150–L151** — Use real sys.argv without the executable name when argv was omitted, then return the internal dispatcher's integer status.
- **L152–L154** — Catch Ctrl+C, print a fresh-line cancellation message to stderr, and return 130.
- **L155–L157** — Catch ConnectionBusy separately, show its message on stdout and preserve its returncode. This matches a deliberate terminal-behavior distinction.
- **L158–L166** — For other VPNError subclasses, print the safe readable message to stderr, avoid double-prefixing the dependency instruction, and preserve backend returncode.
- **L167–L172** — Handle missing imported runtime libraries with a Fedora/dnf-oriented suggestion and failure status. Actual package names depend on the Linux distribution.
- **L173–L178** — For expected OS/value/subprocess problems, print a generic preparation error without the raw exception's possibly sensitive contents and return 1.

#### 13.4.10 L181–L212 · otp_main

```python
def otp_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read a TIFR TOTP from KeePassXC using a GPG-encrypted database password."
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="prompt locally and encrypt the database password",
    )
    parser.add_argument("--recipient", help="GPG recipient fingerprint for setup")
    args = parser.parse_args(argv)
    if args.recipient and not args.setup:
        parser.error("--recipient requires --setup")
    try:
        config = load_config()
        if args.setup:
            credentials.validate_config(config)
            return setup(
                config.password_file,
                config.database,
                config.entry,
                args.recipient,
                on_progress=_progress,
            )
        print(credentials.get_code(config=config))
        return 0
    except KeyboardInterrupt:
        print("\nTIFR OTP: cancelled.", file=sys.stderr)
        return 130
    except RuntimeError as error:
        print(f"TIFR OTP: {error}", file=sys.stderr)
        return 1
```

**Line-by-line explanation**

- **L181** — Define the installed tifr-otp entry point. It shares credential functions with the library, adding explicit terminal code output and setup dialogs.
- **L182–L184** — Build the OTP argument parser with its descriptive purpose.
- **L185–L189** — Register --setup as a boolean flag that requests local master-password encryption setup.
- **L190** — Register an optional recipient fingerprint value for GPG encryption.
- **L191** — Parse the supplied or process arguments; argparse handles --help before runtime work.
- **L192–L193** — Reject --recipient without --setup because ordinary code retrieval performs decryption, not new encryption.
- **L194–L195** — Begin protected OTP work by loading the package's Config object.
- **L196–L197** — For setup, check the vault exists and GPG is available before displaying setup dialogs.
- **L198–L204** — Run credential setup with the selected paths, entry, recipient and CLI progress callback; return its success/cancellation status.
- **L205** — Otherwise call the nonprinting credentials.get\_code and explicitly print its returned short-lived code at this terminal boundary.
- **L206** — Return success after output.
- **L207–L209** — Handle user cancellation with a readable diagnostic and status 130.
- **L210–L212** — Show deliberate RuntimeError/CredentialError messages and return 1. CredentialError inherits RuntimeError through VPNError.

#### 13.4.11 L213–L220 · otp_main

```python
    except (OSError, UnicodeError, subprocess.SubprocessError, ImportError):
        print(
            "TIFR OTP: operation failed. No password or code was logged.",
            file=sys.stderr,
        )
        return 1


```

**Line-by-line explanation**

- **L213–L218** — Hide raw filesystem, encoding, subprocess and import exception contents behind a generic OTP failure message and status 1.

#### 13.4.12 L221–L238 · import_totp_main

```python
def import_totp_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read one Google Authenticator migration QR locally; never log its contents."
    )
    parser.add_argument(
        "--image",
        action="store_true",
        help="use a local QR image without starting the webcam",
    )
    args = parser.parse_args(argv)
    try:
        return run(image=args.image)
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        print(
            "The local QR scanner could not start. No QR contents were logged.",
            file=sys.stderr,
        )
        return 1
```

**Line-by-line explanation**

- **L221** — Define the installed tifr-import-totp entry point.
- **L222–L224** — Create its parser before importing heavy GUI/camera dependencies, keeping --help available independently.
- **L225–L229** — Register --image as a boolean requesting local-image mode without webcam startup.
- **L230** — Parse command-line arguments.
- **L231** — Only import the scanner runner after argument parsing succeeds and actual scanning is requested.
- **L232** — Run the optional Qt scanner with the parsed image flag and return its GUI event-loop result.
- **L233–L238** — Catch ordinary scanner startup exceptions, avoid raw QR-bearing details, print a generic stderr message and return failure. This does not catch BaseException categories such as KeyboardInterrupt/SystemExit.

[[#4 Package branch — file map|↑ Package file map]]

### 13.5 Package source — src/tifrvpn/config.py


Settings are now an immutable Config object plus a loader, extracted from main’s tifr-otp.py configuration(). Reading configuration is separated from checking a real database and executable availability, which moved to credentials.validate_config(). This makes import and direct Config construction useful to other Python programs before they touch credentials.

**8 November 2026 typing fix:** Pyright could not carry the string-value guarantee from the `any(...)` validation loop into later dictionary lookups. It therefore inferred `str | None` for values passed to `Path`, `entry.strip()` and `Config`. Adding `from typing import cast` and, after successful validation, `settings = cast(dict[str, str], settings)` makes the validated type explicit. Defaults, environment precedence and runtime validation remain unchanged.

**Relation to main:** [[TIFR Vpn TUI#7.2 tifr-otp.py|tifr-otp.py]] — configuration() is split into Config/load_config and runtime credentials.validate_config.

**Functions and their purpose**

- **Config.\_\_post\_init\_\_**, L21–L31: Define post-initialization normalization called by the dataclass-generated initializer after assigning its fields.
- **load\_config**, L34–L83: Load defaults, optional JSON settings, and TIFR\_KEEPASS\_\* overrides.


#### 13.5.1 L1–L14 · Module documentation, imports and shared definitions


```python
"""Load settings without opening a vault or requiring runtime programs."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .errors import ConfigurationError

URL = "https://sslvpn.tifr.res.in/tifruser"
HOST = "sslvpn.tifr.res.in"
```

**Line-by-line explanation**

- **L1** — Document that loading settings does not itself open a vault or require runtime executables.
- **L3** — Import JSON decoding for optional settings text.
- **L4** — Import environment-variable access for XDG and TIFR\_KEEPASS overrides.
- **L5** — Import the dataclass decorator to generate an initializer, representation and equality behavior from declared fields.
- **L6** — Import Path for filesystem path objects and home expansion.
- **L7** — Import `cast` to tell the type checker the type of settings after runtime validation.
- **L9** — Use the package's typed configuration exception rather than a bare RuntimeError.
- **L11** — Centralize the fixed TIFR VPN portal URL for profile checks and keyring attributes.
- **L12** — Centralize its hostname for TLS, cookies and portal requests.


#### 13.5.2 L15–L20 · Config — type/state/test structure


```python
@dataclass(frozen=True)
class Config:
    database: Path
    password_file: Path
    entry: str = "TIFR"
```

**Line-by-line explanation**

- **L15** — Turn the following class into a frozen dataclass. Its fields cannot be reassigned through ordinary attribute assignment after initialization; frozen is a programming contract, not a security sandbox.
- **L16** — Define Config, the structured settings object passed between library components.
- **L17** — Declare the KeePass database path field. The annotation describes the expected type; it is not automatic runtime type enforcement by itself.
- **L18** — Declare the GPG-encrypted database-master-password path.
- **L19** — Declare the KeePass entry path, defaulting to TIFR when omitted.


#### 13.5.3 L21–L33 · Config.__post_init__


```python
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
```

**Line-by-line explanation**

- **L21** — Define post-initialization normalization called by the dataclass-generated initializer after assigning its fields.
- **L22** — Convert database to Path and expand a leading ~. object.\_\_setattr\_\_ deliberately performs this construction-time normalization despite the class being frozen.
- **L23** — Apply the same normalization to the ciphertext pathname.
- **L24–L28** — Reject nonabsolute paths after home expansion or a blank entry name. These are shape checks; they do not yet require either file to exist.
- **L29–L31** — Raise ConfigurationError with a readable instruction when those settings are invalid.


#### 13.5.4 L34–L66 · load_config · section 1


```python
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
```

**Line-by-line explanation**

- **L34** — Define explicit settings loading and annotate the returned Config type. Merely importing this function does not read the user's config file.
- **L35** — State precedence: defaults, then optional JSON fields, then the corresponding environment overrides.
- **L36–L41** — Build XDG\_CONFIG\_HOME/tifr-vpn/config.json, defaulting the base directory to ~/.config and expanding a leading ~.
- **L42** — Start guarded reading/JSON parsing.
- **L43** — Read and parse the optional file when present; otherwise begin with an empty dictionary so defaults will apply.
- **L44** — Catch filesystem access errors and JSON/value parsing errors.
- **L45–L47** — Replace the lower-level failure with a readable ConfigurationError naming the config path, suppressing chained internal details.
- **L48–L55** — Require a dictionary, only the three known keys, and nonempty string values. The generator checks each supplied value; unsupported keys are found by set subtraction.
- **L56–L58** — Report unsupported JSON shape/keys/values with the package-specific exception.
- **L59** — Mark the validated settings as `dict[str, str]`. `cast` returns the same dictionary without conversion or additional runtime checks; the preceding validation establishes that its allowed keys and values are strings. With string defaults, the following `.get()` calls now resolve to strings for type checking.
- **L60–L65** — Select database from TIFR\_KEEPASS\_DATABASE, otherwise the JSON field, otherwise the default KeePass path; convert it to Path and expand ~.
- **L66** — Select the encrypted master-password file with the same environment → JSON → default precedence, then normalize its path.


#### 13.5.5 L67–L83 · load_config · section 2


```python
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
```

**Line-by-line explanation**

- **L67–L73** — Select the encrypted master-password file with the same environment → JSON → default precedence, then normalize its path.
- **L74** — Choose the entry name from TIFR\_KEEPASS\_ENTRY, then JSON entry, then TIFR.
- **L75–L79** — Check absolute paths and nonblank entry before constructing the settings object. This duplicates the class's basic validation so both the loader and direct construction enforce the required form.
- **L80–L82** — Raise a readable configuration error when that check fails.
- **L83** — Return one Config object instead of main's three-element tuple. Callers now use config.database, config.password\_file and config.entry.


[[#4 Package branch — file map|↑ Package file map]]

### 13.6 Package source — src/tifrvpn/errors.py


A small error vocabulary shared by the library and command adapters. Expected failures inherit VPNError and carry returncode. Library callers can catch an exception; CLI callers receive printed diagnostics and exit statuses. This separates failure reporting from deciding to end a process.

**Functions and their purpose**

- **VPNError.\_\_init\_\_**, L5–L7: Initialize the readable message plus a keyword-only returncode, defaulting to ordinary failure status 1.


#### 13.6.1 L1–L3 · Module documentation, imports and shared definitions


```python
"""Expected failures that applications can handle without exiting."""
```

**Line-by-line explanation**

- **L1** — Docstring states the purpose: represent expected failures as catchable Python objects instead of terminating an embedding application.


#### 13.6.2 L4–L4 · VPNError — type/state/test structure


```python
class VPNError(RuntimeError):
```

**Line-by-line explanation**

- **L4** — Define VPNError as a specialized RuntimeError. Existing callers catching RuntimeError can still catch it; callers needing more precision can catch VPNError.


#### 13.6.3 L5–L9 · VPNError.__init__


```python
    def __init__(self, message, *, returncode=1):
        super().__init__(message)
        self.returncode = returncode
```

**Line-by-line explanation**

- **L5** — Initialize the readable message plus a keyword-only returncode, defaulting to ordinary failure status 1.
- **L6** — Call the parent exception initializer so str(error) returns the supplied readable message.
- **L7** — Store the numeric exit status as an attribute; the CLI can preserve a backend's specific nmcli failure code.


#### 13.6.4 L10–L13 · ConfigurationError — type/state/test structure


```python
class ConfigurationError(VPNError):
    pass
```

**Line-by-line explanation**

- **L10** — ConfigurationError identifies invalid JSON, paths or settings; it still belongs to the VPNError family.
- **L11** — pass adds no methods; the distinct exception type itself is useful for selective catching.


#### 13.6.5 L14–L17 · CredentialError — type/state/test structure


```python
class CredentialError(VPNError):
    pass
```

**Line-by-line explanation**

- **L14** — CredentialError identifies GPG, vault access, entry parsing and password-storage failures.
- **L15** — Inherit the parent message and returncode behavior unchanged.


#### 13.6.6 L18–L21 · AuthenticationError — type/state/test structure


```python
class AuthenticationError(VPNError):
    pass
```

**Line-by-line explanation**

- **L18** — AuthenticationError identifies unusable session data, failed web sign-in and related keyring/worker failures.
- **L19** — No additional implementation is required to make this a distinct catchable failure category.


#### 13.6.7 L22–L25 · NetworkManagerError — type/state/test structure


```python
class NetworkManagerError(VPNError):
    pass
```

**Line-by-line explanation**

- **L22** — NetworkManagerError identifies profile, state-query or tunnel-command failures.
- **L23** — Reuse the parent initializer and returncode attribute.


#### 13.6.8 L26–L29 · ProfileNotFound — type/state/test structure


```python
class ProfileNotFound(NetworkManagerError):
    pass
```

**Line-by-line explanation**

- **L26** — ProfileNotFound is a particular NetworkManagerError used for the recoverable absence of a configured profile. Setup/connect can respond by creating it.
- **L27** — Inherit behavior; only the type distinction is new.


#### 13.6.9 L30–L31 · ConnectionBusy — type/state/test structure


```python
class ConnectionBusy(NetworkManagerError):
    """A tunnel is already changing state and cannot be connected again."""
```

**Line-by-line explanation**

- **L30** — ConnectionBusy is another NetworkManagerError. It prevents a connect attempt while a connection is already changing state.
- **L31** — Class docstring explains the transitional-state case; the class otherwise inherits the common message/status behavior.


[[#4 Package branch — file map|↑ Package file map]]

### 13.7 Package source — src/tifrvpn/credentials.py


The headless credential-access layer extracted from main’s tifr-otp.py. It now uses Config fields and CredentialError, returns codes/data instead of printing them, and separates password encryption/storage from the Qt prompt that collects a password. Keeping GPG/KeePass functions out of GUI modules makes them reusable and testable. Most cryptographic/file-handling mechanics match the earlier main tutorial; the line notes below are reused where the exact operation is unchanged.

**Relation to main:** [[TIFR Vpn TUI#7.2 tifr-otp.py|tifr-otp.py]] — The CLI/vault/GPG functions remain, while config and Qt dialog code now have separate modules.

**Functions and their purpose**

- **validate\_config**, L15–L21: Define runtime credential prerequisites separately from Config shape validation and import. -> None indicates success returns no meaningful data.
- **keepass\_command**, L24–L36: Build argv for native keepassxc-cli or its Flatpak equivalent; the command is executed by later functions.
- **read\_code**, L39–L54: Define current-code retrieval with an already decrypted database master password.
- **read\_login**, L57–L82: Return login fields in memory; never expose them as CLI output.
- **decrypt\_password**, L85–L105: Define decryption with keyword-only allow\_prompt=True, allowing the hidden browser to explicitly prohibit pinentry.
- **recipient\_key**, L108–L132: Choose a supplied recipient or infer one eligible primary GPG key. This remains the same selection heuristic explained in the main guide.
- **save\_password**, L135–L163: Encrypt and atomically save a verified database password.
- **get\_code**, L166–L171: Return the current KeePassXC TOTP; GPG can prompt to unlock its key.


#### 13.7.1 L1–L14 · Module documentation, imports and shared definitions


```python
"""KeePassXC/GPG access; passwords and codes are returned only in memory."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import Config, load_config
from .errors import CredentialError
```

**Line-by-line explanation**

- **L1** — Document that this module returns sensitive values in process memory; terminal output decisions belong to cli.py.
- **L3** — Import operating-system features: environment variables, file synchronization and atomic replacement.
- **L4** — Import regular expressions for checking that generated codes contain the expected digits.
- **L5** — Import shutil, used here to locate external programs on PATH.
- **L6** — Import subprocess to start gpg, keepassxc-cli or flatpak and communicate through pipes.
- **L7** — Import Python process information and input/output streams, including stdin, stderr and exit status handling.
- **L8** — Import temporary-file support for writing ciphertext safely before replacing the final file.
- **L9** — Import Path, a class for filesystem paths. The / operator on Paths joins path components rather than dividing numbers.
- **L11** — Import the immutable settings type and explicit settings loader; there is no runpy lookup or three-value configuration tuple here.
- **L12** — Import the credential-specific VPNError subclass for typed failures.


#### 13.7.2 L15–L23 · validate_config


```python
def validate_config(config: Config) -> None:
    if not config.database.is_file():
        raise CredentialError(
            f"Database not found: {config.database}. Set TIFR_KEEPASS_DATABASE to its path."
        )
    if not shutil.which("gpg"):
        raise CredentialError("GPG is required.")
```

**Line-by-line explanation**

- **L15** — Define runtime credential prerequisites separately from Config shape validation and import. -> None indicates success returns no meaningful data.
- **L16–L19** — Require the configured database to be a real file at the moment credentials are needed; otherwise raise a readable path/configuration instruction.
- **L20–L21** — Require gpg at the credential-use boundary rather than while simply loading settings or importing the package.


#### 13.7.3 L24–L38 · keepass_command


```python
def keepass_command(database, entry):
    if shutil.which("keepassxc-cli"):
        command = ["keepassxc-cli"]
    elif shutil.which("flatpak"):
        command = [
            "flatpak",
            "run",
            "--command=keepassxc-cli",
            "org.keepassxc.KeePassXC",
        ]
    else:
        raise CredentialError("Install KeePassXC or its Flatpak first.")
    return command + ["show", "--quiet", "--totp", str(database), entry]
```

**Line-by-line explanation**

- **L24** — Build argv for native keepassxc-cli or its Flatpak equivalent; the command is executed by later functions.
- **L25** — shutil.which returns the path of an available executable, or None. Prefer a natively installed KeePassXC CLI.
- **L26** — Start the command argument list with keepassxc-cli.
- **L27** — If the native CLI was not found, check whether Flatpak is available as an alternative launcher.
- **L28–L33** — Build the Flatpak alternative argv: flatpak run --command=keepassxc-cli org.keepassxc.KeePassXC. The list is an argument vector rather than a shell-evaluated string; executing it remains the caller's later step.
- **L34** — Otherwise, neither native CLI nor Flatpak launcher was found; the following typed credential failure explains the dependency.
- **L35** — Raise the credential-specific error if neither CLI launcher is available. Availability of Flatpak itself does not prove KeePassXC is installed inside it.
- **L36** — Append show, quiet output, --totp, database filename and entry name. str(database) converts the Path object into text. List + concatenates argument lists; each element becomes one argument, so spaces in paths stay intact.


#### 13.7.4 L39–L56 · read_code


```python
def read_code(password, database, entry):
    if any(char in password for char in "\r\n\0"):
        raise CredentialError("The database password must be a single line.")
    result = subprocess.run(
        keepass_command(database, entry),
        check=False,
        input=password + "\n",
        capture_output=True,
        text=True,
    )
    code = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9]{6,8}", code):
        raise CredentialError(
            "Could not unlock KeePassXC or read the entry's TOTP. Check the password, database and entry name."
        )
    return code
```

**Line-by-line explanation**

- **L39** — Define current-code retrieval with an already decrypted database master password.
- **L40** — Reject carriage return, newline or NUL in the password. any(...) tests whether any character in this group appears. The CLI input protocol uses a single password line.
- **L41** — Reject passwords incompatible with the single-line stdin protocol using CredentialError.
- **L42** — Start the subprocess.run call, which waits for the child command to finish.
- **L43** — Use keepass\_command to choose the native/Flatpak KeePass argv for this vault and entry before providing master-password stdin.
- **L44** — Do not let subprocess.run raise automatically for nonzero status; the following code performs validation and emits a safe credential-specific message.
- **L45** — Send the master password through stdin followed by a newline, excluding it from process arguments.
- **L46** — Capture both stdout and stderr instead of printing child output automatically.
- **L47** — Decode the captured data as strings for code validation.
- **L48** — Close the current-code subprocess call and retain its result for exit-status/output validation below.
- **L49** — Remove surrounding whitespace from output to obtain the candidate numeric code.
- **L50** — Reject a failed child command or output that does not fully match 6 through 8 ASCII digits. r"..." is a raw string, useful for regular expressions. The regex also technically accepts 7 digits.
- **L51–L53** — Report a failed unlock/invalid TOTP with a generic CredentialError without exposing raw vault output.
- **L54** — Return the validated code to the caller. Only main() explicitly prints it for the standalone OTP command.


#### 13.7.5 L57–L84 · read_login


```python
def read_login(password, database, entry):
    """Return login fields in memory; never expose them as CLI output."""
    if any(char in password for char in "\r\n\0"):
        raise CredentialError("The database password must be a single line.")
    command = keepass_command(database, entry)
    # Explicitly request the protected value, captured only in this process.
    command = (
        command[:-2]
        + ["--show-protected", "-a", "UserName", "-a", "Password"]
        + command[-2:]
    )
    result = subprocess.run(
        command, check=False, input=password + "\n", capture_output=True, text=True
    )
    fields = result.stdout.splitlines()
    if (
        result.returncode
        or len(fields) != 3
        or not re.fullmatch(r"[0-9]{6,8}", fields[2])
    ):
        raise CredentialError("Could not read the KeePassXC login entry and TOTP.")
    if not fields[0].strip() or not fields[1]:
        raise CredentialError(
            "Fill the Username and Password fields of the TIFR entry in KeePassXC, then save the database."
        )
    return {"username": fields[0].strip(), "password": fields[1]}
```

**Line-by-line explanation**

- **L57–L58** — Define login-field retrieval and document that the return value stays in memory rather than being printed.
- **L59** — Repeat the one-line master-password validation before using the CLI.
- **L60** — Use CredentialError for a malformed multiline master password.
- **L61** — Get the ordinary show/--totp command arguments.
- **L62** — Comment explains that protected password data must be requested explicitly and captured.
- **L63–L67** — Insert --show-protected and UserName/Password attribute requests before the final database/entry arguments, preserving the existing --totp request. List slices rebuild argv without shell parsing.
- **L68–L70** — Execute the CLI with master-password stdin, captured text output and explicit return-code handling.
- **L71** — Split the returned text into lines: expected username, password and a current TOTP.
- **L72–L76** — Require successful exit, exactly username/password/code lines and a 6-to-8-digit ASCII TOTP; short-circuit checks protect fields\[2\] when the list is too short.
- **L77** — Raise a safe CredentialError for malformed/failed entry retrieval.
- **L78** — Require a nonblank username and a nonempty password. Username whitespace is stripped; password whitespace is preserved because it can be meaningful.
- **L79–L81** — Explain missing saved login fields without printing their contents.
- **L82** — Return a dictionary containing username and password. The code from this CLI call validated the entry but is deliberately not returned here; fresh codes are requested later at the OTP form step.


#### 13.7.6 L85–L107 · decrypt_password


```python
def decrypt_password(password_file, *, allow_prompt=True):
    if not password_file.is_file():
        raise CredentialError(
            "Encrypted password file not found. Run tifr-otp --setup first."
        )
    if sys.stdin.isatty():
        os.environ["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    command = ["gpg", "--quiet"]
    if not allow_prompt:
        # A pinentry window on Xvfb would be invisible. Fail instead of waiting.
        command += ["--batch", "--no-tty", "--pinentry-mode", "error"]
    decrypted = subprocess.run(
        command + ["--decrypt", "--", str(password_file)],
        check=False,
        capture_output=True,
    )
    if decrypted.returncode:
        raise CredentialError(
            "Could not decrypt the password file. Unlock your GPG key and retry."
        )
    return decrypted.stdout.decode("utf-8").removesuffix("\n").removesuffix("\r")
```

**Line-by-line explanation**

- **L85** — Define decryption with keyword-only allow\_prompt=True, allowing the hidden browser to explicitly prohibit pinentry.
- **L86** — Require the ciphertext file to exist before invoking GPG.
- **L87–L89** — Report a missing ciphertext file and direct the user to the OTP setup command.
- **L90** — Check whether standard input is attached to a terminal, rather than a pipe or file.
- **L91** — When attached, tell GPG the terminal device name through GPG\_TTY so a terminal pinentry can use it.
- **L92** — Begin a gpg command with reduced routine output.
- **L93** — When prompting is forbidden, add flags for noninteractive failure instead of waiting for an invisible unlock window.
- **L94** — The comment explains the quiet-mode hazard: pinentry must not appear on the hidden display.
- **L95** — --batch and --no-tty avoid interactive command-line input; --pinentry-mode error asks GPG to fail if a new pinentry prompt would be necessary. A cached unlock may still work.
- **L96** — Run decryption and capture its result.
- **L97** — --decrypt selects decryption; -- ends option parsing before the filename. The ciphertext pathname can appear in arguments, but the decrypted master password does not.
- **L98** — Inspect GPG's returncode explicitly rather than generating an automatic raw child exception.
- **L99** — Capture both byte streams; omission of text=True keeps decryption output as bytes until explicit UTF-8 decoding.
- **L100** — Close the GPG decryption call; ciphertext is a pathname argument, while decrypted plaintext is captured stdout bytes.
- **L101** — A nonzero return code means decryption failed.
- **L102–L104** — Report failed decryption generically through CredentialError, without emitting captured secret-bearing streams.
- **L105** — Decode the decrypted UTF-8 bytes and remove at most one final newline then one final carriage return. This tolerates a conventional line ending while preserving other password characters; strip() would remove meaningful spaces.


#### 13.7.7 L108–L134 · recipient_key


```python
def recipient_key(explicit):
    if explicit:
        return explicit
    result = subprocess.run(
        ["gpg", "--batch", "--with-colons", "--list-secret-keys", "--fingerprint"],
        capture_output=True,
        text=True,
        check=True,
    )
    keys = []
    eligible = False
    for line in result.stdout.splitlines():
        parts = line.split(":")
        if parts[0] == "sec":
            eligible = parts[1] not in ("r", "e", "d") and "e" in parts[11].lower()
        elif parts[0] == "ssb":
            eligible = False
        elif parts[0] == "fpr" and eligible:
            keys.append(parts[9])
            eligible = False
    if len(keys) != 1:
        raise CredentialError(
            "Specify your GPG encryption key: tifr-otp --setup --recipient FINGERPRINT"
        )
    return keys[0]
```

**Line-by-line explanation**

- **L108** — Choose a supplied recipient or infer one eligible primary GPG key. This remains the same selection heuristic explained in the main guide.
- **L109** — If the user explicitly supplied a recipient, use that value.
- **L110** — Return the explicit identifier without trying automatic selection.
- **L111** — Otherwise ask GPG for available secret-key records.
- **L112** — --with-colons requests machine-parseable records; --fingerprint includes stable key identifiers; --list-secret-keys lists locally available private-key records. --batch avoids interactive selection.
- **L113–L115** — Capture GPG's machine-readable text and use check=True here for key-listing command failure, rather than handling a plaintext-returning operation.
- **L116** — Close the checked GPG key-listing command and retain its machine-readable text result.
- **L117** — Begin an empty list of eligible primary-key fingerprints for automatic recipient selection.
- **L118** — Track whether the most recent primary-key record qualifies for encryption.
- **L119** — Process the machine-readable output one line at a time.
- **L120** — Split a record into colon-separated fields. Python indexes start at 0: parts\[1\] is the second field.
- **L121** — sec identifies a primary secret-key record.
- **L122** — Accept a primary record unless its validity flag is revoked, expired or disabled, and require encryption capability in field 12. .lower() accepts both e and E capability markers. This is this program's selection heuristic, not a full replacement for GPG's own key validation.
- **L123** — ssb identifies a secret subkey record.
- **L124** — Do not collect the following subkey fingerprint as a separate primary-key candidate.
- **L125** — When a fingerprint record follows an eligible primary record, collect it.
- **L126** — The fingerprint is in the tenth colon-separated field.
- **L127** — Reset eligibility so the same primary key is not collected repeatedly.
- **L128** — Require exactly one automatically selected key. Zero or multiple candidates require an explicit user choice.
- **L129–L131** — Require explicit recipient selection when exactly one eligible primary key cannot be inferred.
- **L132** — Return the sole candidate's fingerprint; index 0 selects the first list element.


#### 13.7.8 L135–L165 · save_password


```python
def save_password(password, password_file, recipient):
    """Encrypt and atomically save a verified database password."""
    result = subprocess.run(
        ["gpg", "--batch", "--encrypt", "--recipient", recipient, "--output", "-"],
        check=False,
        input=password.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode or not result.stdout:
        raise CredentialError(
            "GPG encryption failed; no password file was written. Check the recipient key."
        )
    password_file.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if password_file.parent == Path.home() / ".local/share/tifr-vpn":
        password_file.parent.chmod(0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=password_file.parent, prefix=".keepass-password-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(result.stdout)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, password_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
```

**Line-by-line explanation**

- **L135** — Define non-GUI password encryption/storage. This helper expects a previously verified master password; its name is not a claim that it independently opens/verifies the vault here.
- **L136** — Document that ciphertext saving is atomic at the destination replacement step.
- **L137** — Start a GPG encryption subprocess.
- **L138** — Encrypt for the selected recipient; --output - sends ciphertext to stdout so Python can capture it rather than having GPG write the final destination directly.
- **L139** — Handle GPG encryption failure explicitly below rather than exposing a raw failed subprocess object.
- **L140** — Send UTF-8 master-password bytes to GPG on stdin, not in argv.
- **L141** — Capture ciphertext and diagnostics in memory.
- **L142** — Finish encryption subprocess execution; the following check requires successful nonempty ciphertext before writing anything.
- **L143** — Require successful encryption and a nonempty ciphertext result before any destination replacement.
- **L144–L146** — Refuse to replace the destination when GPG failed or returned no ciphertext.
- **L147** — Create the parent directory with requested mode 700: owner-only read/write/traverse. exist\_ok=True tolerates an existing directory; creation mode alone does not change permissions of an existing one.
- **L148** — Check whether this is the standard private application directory.
- **L149** — For that standard directory, explicitly enforce owner-only 700 permissions even when it already exists. Custom directory permissions are not forcibly rewritten here.
- **L150** — Initialize temporary to None so cleanup knows whether a temporary pathname was created.
- **L151** — Begin the protected temporary-file write/rename path; its finally block removes any leftover temporary ciphertext file.
- **L152–L154** — Create a temporary ciphertext file inside the destination directory, so completed replacement does not cross filesystems and partial writes do not replace the target.
- **L155** — Remember the temporary file's pathname for permissions and cleanup.
- **L156** — Write encrypted bytes, never the plaintext password, to that temporary file.
- **L157** — Flush Python's buffered bytes to the underlying operating-system file handle.
- **L158** — Ask the operating system to synchronize the file contents using fsync. This improves durability; the code does not additionally fsync the parent directory.
- **L159** — Set file permissions to 600: owner can read/write; group and others have no permission bits.
- **L160** — Atomically replace the destination pathname with the completed temporary ciphertext file. This avoids leaving a half-written target during an ordinary interrupted write.
- **L161** — The finally body executes whether writing/replacement succeeds or raises an exception.
- **L162** — Only attempt temporary-path cleanup if a pathname was actually created.
- **L163** — Delete a leftover temporary file; missing\_ok=True tolerates it already having been renamed into place.


#### 13.7.9 L166–L171 · get_code


```python
def get_code(*, config: Config | None = None) -> str:
    """Return the current KeePassXC TOTP; GPG can prompt to unlock its key."""
    config = config if config is not None else load_config()
    validate_config(config)
    password = decrypt_password(config.password_file)
    return read_code(password, config.database, config.entry)
```

**Line-by-line explanation**

- **L166** — Define the convenient programmatic OTP API: return a string and accept optional explicit Config without printing it.
- **L167** — Document that GPG may still ask to unlock its own key when this function is actually called.
- **L168** — Use explicitly supplied Config when present, otherwise read normal configuration now.
- **L169** — Check actual vault existence and GPG availability before attempting decryption.
- **L170** — Decrypt the encrypted vault master password, allowing a normal unlock prompt if required.
- **L171** — Ask KeePassXC for a fresh current code and return it directly. cli.otp\_main is the separate layer that intentionally prints it for a terminal user.


[[#4 Package branch — file map|↑ Package file map]]

### 13.8 Package source — src/tifrvpn/auth.py


The non-GUI authentication supervisor, split out of main’s large authentication script. It probes cached sessions and starts an isolated importable worker using the same Python interpreter. Explicit Config values are passed to that child without replacing the parent’s settings. Unlike main, worker stderr is captured and only forwarded through on_progress after communicate/run returns, so child sign-in progress is not streamed live. Standard package installation now makes the worker importable; the previous manual PYTHONPATH injection was removed.

**Relation to main:** [[TIFR Vpn TUI#7.3 tifr-vpn-auth.py|tifr-vpn-auth.py]] — valid_session, background_browser and authenticate move into a non-GUI supervisor.

**Functions and their purpose**

- **valid\_session**, L21–L45: Ask the gateway whether the saved session still grants portal access.
- **valid\_session.NoRedirect.redirect\_request**, L25–L26: Override redirect handling so a login redirect does not get followed into a misleading successful login-page response.
- **background\_browser**, L48–L80: Run a disposable virtual display and clean up its entire process group.
- **authenticate**, L83–L140: Define fresh authentication with keyword-only quiet, optional explicit Config and optional progress callback.


#### 13.8.1 L1–L20 · Module documentation, imports and shared definitions


```python
"""Validate sessions and coordinate an isolated SSO browser process."""

import json
import os
import shutil
import signal
import ssl
import subprocess
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from . import credentials
from .config import HOST, load_config
from .errors import AuthenticationError

BACKGROUND_TIMEOUT = 120
```

**Line-by-line explanation**

- **L1** — State responsibility: validate sessions and supervise a separate SSO browser process.
- **L3** — JSON serializes explicit nonsecret config fields for the child worker.
- **L4** — os provides environment variables, process groups and Linux file-descriptor operations.
- **L5** — shutil locates quiet-mode executables on PATH.
- **L6** — signal supplies named Unix signals such as SIGTERM and SIGKILL.
- **L7** — ssl verifies HTTPS/TLS certificates using the system's trusted certificate authorities.
- **L8** — subprocess launches browser child processes and nmcli.
- **L9** — sys provides the current interpreter path, argument list, streams and exit functions.
- **L10** — HTTPError represents HTTP error responses, including redirects deliberately not followed by this code.
- **L11** — urlsplit separates a URL into scheme, hostname, port, path and related pieces.
- **L12** — Import HTTPRedirectHandler, HTTPSHandler, Request, build\_opener from urllib.request for verified portal HTTP requests and explicit redirect behavior. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L14** — Import the normal credentials module, replacing runpy-based loading of a neighboring script.
- **L15** — Use centralized host constants and explicit settings loading.
- **L16** — Use AuthenticationError, a catchable VPNError subclass, for expected sign-in failures.
- **L18** — Keep the quiet browser communication deadline at 120 seconds; it is not a timer around every step of a whole connection.


#### 13.8.2 L21–L23 · valid_session


```python
def valid_session(cookie):
    """Ask the gateway whether the saved session still grants portal access."""
```

**Line-by-line explanation**

- **L21** — Define the reusable session probe. It does network work only when called, not at import.
- **L22** — Document that gateway portal access, not token shape alone, is checked.


#### 13.8.3 L24–L24 · valid_session.NoRedirect — type/state/test structure


```python
    class NoRedirect(HTTPRedirectHandler):
```

**Line-by-line explanation**

- **L24** — Override redirect handling so a login redirect does not get followed into a misleading successful login-page response.


#### 13.8.4 L25–L47 · valid_session.NoRedirect.redirect_request


```python
        def redirect_request(self, *_args, **_kwargs):
            return None

    request = Request(
        "https://" + HOST + "/dana/home/index.cgi", headers={"Cookie": cookie}
    )
    opener = build_opener(
        NoRedirect(), HTTPSHandler(context=ssl.create_default_context())
    )
    try:
        with opener.open(request, timeout=15) as response:
            return response.status == 200
    except HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            location = urlsplit(error.headers.get("Location", ""))
            return location.hostname in (None, HOST) and location.path.startswith(
                "/dana/home/"
            )
        if error.code in (401, 403):
            return False
        raise
```

**Line-by-line explanation**

- **L25–L26** — Override redirect handling so a login redirect does not get followed into a misleading successful login-page response.
- **L28–L30** — Build the portal request with the provided cookie as an HTTP header; the cookie is not printed.
- **L31–L33** — Use the no-redirect handler and normal default TLS certificate verification.
- **L34–L36** — Open the request with a 15-second timeout and accept HTTP 200 according to this implementation's portal heuristic.
- **L37–L42** — Inspect redirect errors without following them; accept relative/same-host redirects only into /dana/home/.
- **L43–L44** — Treat unauthorized/forbidden HTTP responses as an invalid session.
- **L45** — Reraise other HTTP errors; server/network failures are not all silently treated as expired credentials.


#### 13.8.5 L48–L79 · background_browser · section 1


```python
def background_browser(command, *, env=None):
    """Run a disposable virtual display and clean up its entire process group."""
    environment = dict(os.environ if env is None else env, GDK_BACKEND="x11")
    environment.pop("WAYLAND_DISPLAY", None)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        start_new_session=True,
    )
    try:
        output, errors = process.communicate(timeout=BACKGROUND_TIMEOUT)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
        if isinstance(error, KeyboardInterrupt):
            raise
        raise AuthenticationError(
            "Background sign-in timed out. Retry tifrvpn -c to see whether TIFR needs input."
        ) from None
```

**Line-by-line explanation**

- **L48** — Define quiet-browser lifecycle supervision and accept an optional child environment dictionary.
- **L49** — Document the disposable display and intended same-process-group cleanup.
- **L50** — Copy the supplied environment, or parent environment by default, while selecting GTK's X11 backend for Xvfb.
- **L51** — Remove a Wayland display selection from that child's environment only.
- **L52–L59** — Start the child/wrapper with captured stdout AND stderr, text conversion, the prepared environment and a new session/process group. Capturing stderr is a change from main's inherited terminal stderr.
- **L60–L61** — Drain both captured streams while waiting up to 120 seconds, retaining stdout data and stderr diagnostics separately.
- **L62–L66** — On deadline expiry or Ctrl+C, signal the process group with SIGTERM; tolerate the group already having exited.
- **L67–L74** — Wait five seconds for graceful cleanup, then escalate to SIGKILL if necessary, tolerate an already-gone group and drain/reap the process. The final wait has no explicit additional timeout.
- **L75–L76** — After cleanup, propagate a user's KeyboardInterrupt so its cancellation semantics survive.
- **L77–L79** — Convert deadline expiry to a readable AuthenticationError recommending visible sign-in; suppress noisy exception chaining.


#### 13.8.6 L80–L82 · background_browser · section 2


```python
    return subprocess.CompletedProcess(command, process.returncode, output, errors)
```

**Line-by-line explanation**

- **L80** — Return command, exit code, stdout and stderr in a CompletedProcess record. The extra stderr field supports callback-based reporting after completion.


#### 13.8.7 L83–L114 · authenticate · section 1


```python
def authenticate(*, quiet=False, config=None, on_progress=None):
    # Isolate WebKit from the tunnel controller, including its native shutdown.
    command = [sys.executable, "-m", "tifrvpn._sso_worker"]
    environment = dict(os.environ)
    environment.pop("_TIFR_WORKER_CONFIG", None)
    if config is not None:
        environment.update(
            TIFR_KEEPASS_DATABASE=str(config.database),
            TIFR_KEEPASS_PASSWORD_FILE=str(config.password_file),
            TIFR_KEEPASS_ENTRY=config.entry,
            _TIFR_WORKER_CONFIG=json.dumps(
                {
                    "database": str(config.database),
                    "password_file": str(config.password_file),
                    "entry": config.entry,
                }
            ),
        )
    options = {"env": environment}
    if quiet:
        missing = [
            name for name in ("xvfb-run", "Xvfb", "xauth") if not shutil.which(name)
        ]
        if missing:
            raise AuthenticationError(
                "Background sign-in requires: "
                + ", ".join(missing)
                + ". Install Xvfb and xauth, or retry without --quiet."
            )
        # Unlock on the real desktop before changing DISPLAY. The child only
        # uses cached GPG access, so it can never hide a pinentry prompt.
        selected = config if config is not None else load_config()
```

**Line-by-line explanation**

- **L83** — Define fresh authentication with keyword-only quiet, optional explicit Config and optional progress callback.
- **L84** — Comment explains why WebKit's native lifecycle stays isolated from the controller responsible for activating the tunnel.
- **L85** — Launch the same interpreter using -m tifrvpn.\_sso\_worker, not a neighboring root script pathname. This interpreter must have the package installed/importable.
- **L86** — Copy the parent environment so this attempt can customize the child's settings without rewriting the parent's variables.
- **L87** — Remove an inherited private worker-config payload to prevent stale values from overriding this call's intended settings.
- **L88–L100** — When a Config object is explicitly supplied, pass its nonsecret paths and entry via child-only TIFR variables and a private JSON payload. The worker reconstructs Config directly, so it need not first parse unrelated/bad optional JSON configuration. Do not put vault passwords or cookies into this payload.
- **L101** — Prepare a common env keyword argument dictionary for either visible or quiet process launching.
- **L102** — Use the background path only if fresh authentication was requested with quiet=True.
- **L103–L105** — Find missing xvfb-run, Xvfb and xauth executables before accessing the vault or creating a display.
- **L106–L111** — Report missing tools through AuthenticationError with an ordinary-mode fallback instruction.
- **L112–L113** — Comments explain unlocking GPG on the actual desktop first; the later hidden child is forbidden to open a new pinentry prompt.
- **L114** — Select the directly supplied Config or explicitly load normal settings.


#### 13.8.8 L115–L140 · authenticate · section 2


```python
        credentials.validate_config(selected)
        credentials.decrypt_password(selected.password_file)
        if on_progress is not None:
            on_progress("tifr VPN: signing in in the background (120-second limit)")
        result = background_browser(
            ["xvfb-run", "-a"] + command + ["--quiet"], **options
        )
    else:
        result = subprocess.run(
            command, check=False, capture_output=True, text=True, **options
        )
    if on_progress is not None and result.stderr:
        for message in result.stderr.splitlines():
            on_progress(message)
    if result.returncode:
        if quiet:
            raise AuthenticationError(
                "Background sign-in did not complete. Retry tifrvpn -c to see the sign-in window."
            )
        raise AuthenticationError(
            "SSO sign-in did not complete; no tunnel was started."
        )
    cookie = result.stdout.strip()
    if not cookie.startswith("DSID=") or any(char in cookie for char in "\r\n\0"):
        raise AuthenticationError("Invalid SSO session; no tunnel was started.")
    return cookie
```

**Line-by-line explanation**

- **L115** — Validate the actual vault pathname and GPG availability at the credential-use boundary.
- **L116** — Attempt decryption/unlock on the real desktop before starting the background browser deadline. The returned plaintext exists temporarily in memory but is not passed as a command argument.
- **L117–L118** — Emit background-start progress only if a callback was supplied. With no callback the controller stays silent here.
- **L119–L121** — Run xvfb-run -a with the importable worker module and --quiet, forwarding the prepared child environment.
- **L122–L125** — For visible mode, run the same module without Xvfb and capture both output streams. No explicit browser deadline is applied on this foreground path.
- **L126–L128** — After the child returns, forward each captured stderr line to on\_progress when provided. This is buffered replay after completion, not live streaming while sign-in is underway.
- **L129–L136** — Turn a failed worker exit into a quiet-specific or ordinary readable AuthenticationError; never use a failed child's stdout as a usable session.
- **L137** — Strip surrounding whitespace from the captured worker result.
- **L138–L139** — Require DSID= and reject embedded carriage return/newline/NUL before returning session data. Detailed portal validity was checked within the browser workflow.
- **L140** — Return the cookie as data in memory to the orchestration layer.


[[#4 Package branch — file map|↑ Package file map]]

### 13.9 Package source — src/tifrvpn/_sso_worker.py

The private browser-worker entry point imports Config and the SSO function at module scope. Import loads the GTK/WebKit dependencies, but only deliberate worker execution calls login_cookie or os._exit. The parent still starts this module in a separate process.

**Relation to main:** [[TIFR Vpn TUI#7.3 tifr-vpn-auth.py|tifr-vpn-auth.py]] — sso_window_process becomes a dedicated -m worker entry point with explicit config reconstruction.

**Functions and their purpose**

- **sso_window_process**, L12–L15: Define the worker's actual sign-in invocation, with quiet defaulting to False.
- **_run**, L18–L41: Separate execution/error/shutdown handling from loading the browser function, making it possible to reason about or test without opening a real GUI.
- **main**, L44–L48: Define the worker CLI adapter, optionally accepting explicit arguments for help/tests.

#### 13.9.1 L1–L11 · Module setup and definitions

```python
"""Private subprocess entry point; never exits a process merely on import."""

import argparse
import json
import os
import sys

from .config import Config
from .gui.sso import login_cookie


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import argparse at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import json at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import os at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Import sys at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L8** — Bind Config from .config at module scope. These names are then available to the functions below without a function-local import.
- **L9** — Bind login_cookie from .gui.sso at module scope. These names are then available to the functions below without a function-local import.

#### 13.9.2 L12–L17 · sso_window_process

```python
def sso_window_process(*, quiet=False):
    raw = os.environ.get("_TIFR_WORKER_CONFIG")
    config = Config(**json.loads(raw)) if raw is not None else None
    _run(login_cookie, quiet=quiet, config=config)


```

**Line-by-line explanation**

- **L12** — Define the worker's actual sign-in invocation, with quiet defaulting to False.
- **L13** — Read the private config payload supplied by auth.authenticate, if any.
- **L14** — If provided, JSON-decode the payload and unpack its named fields into Config; otherwise leave config=None so the GUI loads normal settings when needed. \*\*dictionary expands keyword arguments.
- **L15** — Call the protected execution helper with the browser function and settings. Config decoding/imports occur before that helper's own try block; not every malformed private payload is handled inside \_run.

#### 13.9.3 L18–L43 · _run

```python
def _run(login_cookie, *, quiet=False, config=None):
    code = 1
    try:
        cookie = login_cookie(quiet=quiet, config=config)
        sys.stdout.write(cookie)
        sys.stdout.flush()
        code = 0
    except KeyboardInterrupt:
        print("tifr VPN: sign-in cancelled", file=sys.stderr)
        code = 130
    except RuntimeError as error:
        print(f"tifr VPN: {error}", file=sys.stderr)
    except ImportError:
        print(
            "tifr VPN: install SSO support: sudo dnf install python3-gobject webkit2gtk4.1",
            file=sys.stderr,
        )
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        print("tifr VPN: the SSO window could not complete sign-in.", file=sys.stderr)
    finally:
        # WebKit uses native worker processes. Avoid interpreter finalization
        # of its GI wrappers after the window closes.
        sys.stderr.flush()
        os._exit(code)


```

**Line-by-line explanation**

- **L18** — Separate execution/error/shutdown handling from loading the browser function, making it possible to reason about or test without opening a real GUI.
- **L19** — Start with a failure exit code until sign-in and output writing complete.
- **L20–L24** — Run sign-in, write the returned cookie alone to stdout, flush it, then mark success. Flushing is essential before immediate os.\_exit.
- **L25–L27** — Report a user cancellation on stderr and choose status 130.
- **L28–L29** — Print readable RuntimeError-family sign-in failures without dumping raw secret-bearing tracebacks.
- **L30–L34** — Give a Fedora-oriented missing-GUI-dependency suggestion when an ImportError reaches this block.
- **L35–L36** — For other ordinary exceptions, print a generic incomplete-sign-in diagnostic.
- **L37–L41** — Always flush diagnostics and immediately terminate this dedicated child using os.\_exit(code). It bypasses normal Python finalization of native WebKit wrappers, so it is confined to this deliberate subprocess role.

#### 13.9.4 L44–L52 · main

```python
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    sso_window_process(quiet=args.quiet)


if __name__ == "__main__":
    main()
```

**Line-by-line explanation**

- **L44** — Define the worker CLI adapter, optionally accepting explicit arguments for help/tests.
- **L45** — Create its parser using the module docstring.
- **L46** — Register the private boolean --quiet flag.
- **L47** — Parse arguments; --help exits before sign-in/GI operations are invoked.
- **L48** — Run the isolated sign-in path using the chosen flag.
- **L51** — Run the worker entry point only when this module is executed as a program; ordinary import does not call main.
- **L52** — Parse the worker arguments and begin deliberate worker execution.

[[#4 Package branch — file map|↑ Package file map]]

### 13.10 Package source — src/tifrvpn/keyring.py

This module binds the Secret Service API when imported. Namespace version selection precedes the GI from-import. Lookup/store/delete operations still occur only when a helper function is called. Tests now replace the Secret name already bound in this module.

**Relation to main:** [[TIFR Vpn TUI#7.3 tifr-vpn-auth.py|tifr-vpn-auth.py]] — saved_login becomes a private primitive plus named session/browser read/write/clear helpers.

**Functions and their purpose**

- **_saved_login**, L12–L41: Keep only this helper's session state in the desktop Secret Service.
- **load_session**, L44–L45: Publicly named helper to load the reusable VPN session cookie under kind=session.
- **save_session**, L48–L49: Publicly named helper to store that cookie under kind=session.
- **load_browser_state**, L52–L53: Load serialized browser-cookie records under the separate kind=browser identity.
- **save_browser_state**, L56–L57: Store serialized browser state separately from the direct VPN-session cookie.
- **clear_saved_login**, L60–L66: Define full remembered-state clearing, a different action from disconnecting a tunnel.
- **clear_session**, L69–L70: Clear only the stale direct session cookie during a connect retry, preserving browser cookies that might help the next SSO attempt.

#### 13.10.1 L1–L11 · Module setup and definitions

```python
"""Store only this application's sign-in state in desktop Secret Service."""

import gi

from .config import URL
from .errors import AuthenticationError

gi.require_version("Secret", "1")
from gi.repository import Secret  # noqa: E402 - Select the namespace version first.


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import gi at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Bind URL from .config at module scope. These names are then available to the functions below without a function-local import.
- **L6** — Bind AuthenticationError from .errors at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Select the Secret API namespace version before importing it. This chooses an API version, not a Python interpreter version.
- **L9** — Import Secret from the selected GI namespaces at module scope. Version selection above must happen first; the E402 comment documents that intentional import ordering.

#### 13.10.2 L12–L43 · _saved_login

```python
def _saved_login(kind, value=None, *, forget=False, on_progress=None):
    """Keep only this helper's session state in the desktop Secret Service."""
    schema = Secret.Schema.new(
        "in.res.tifr.vpn",
        Secret.SchemaFlags.NONE,
        {
            "server": Secret.SchemaAttributeType.STRING,
            "kind": Secret.SchemaAttributeType.STRING,
        },
    )
    attributes = {"server": URL, "kind": kind}
    try:
        if forget:
            return Secret.password_clear_sync(schema, attributes, None)
        if value is not None:
            return Secret.password_store_sync(
                schema,
                attributes,
                Secret.COLLECTION_DEFAULT,
                "TIFR VPN " + kind,
                value,
                None,
            )
        return Secret.password_lookup_sync(schema, attributes, None)
    except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
        if on_progress is not None:
            on_progress(
                "tifr VPN: desktop keyring unavailable; saved login could not be accessed."
            )
        return None


```

**Line-by-line explanation**

- **L12** — Define the internal read/write/delete primitive with kind, optional value, keyword-only deletion flag and progress callback.
- **L13** — Document the intended Secret Service storage boundary.
- **L14–L21** — Create the existing in.res.tifr.vpn schema with string server/kind attributes. A schema is lookup metadata, not an encryption algorithm or a replacement for a working unlocked desktop keyring.
- **L22** — Build the exact cache lookup identity: fixed server URL plus session or browser kind.
- **L23** — Handle errors from keyring operations without exposing their raw secret-bearing exception text. Imports/schema creation above are outside this try block.
- **L24–L25** — Deletion takes priority when forget=True; return the backend result. False can mean no matching secret, while this helper uses None for a caught backend failure.
- **L26–L34** — If value is explicitly provided, store it in the default secret collection with the TIFR VPN kind label, then return the backend result. None means no cancellation object.
- **L35** — Otherwise perform lookup and return the stored string or None when absent.
- **L36–L41** — On a caught backend exception, optionally emit a generic callback message and return None. Without a callback, this low-level warning is not printed.

#### 13.10.3 L44–L47 · load_session

```python
def load_session(*, on_progress=None):
    return _saved_login("session", on_progress=on_progress)


```

**Line-by-line explanation**

- **L44–L45** — Publicly named helper to load the reusable VPN session cookie under kind=session.

#### 13.10.4 L48–L51 · save_session

```python
def save_session(cookie, *, on_progress=None):
    return _saved_login("session", cookie, on_progress=on_progress)


```

**Line-by-line explanation**

- **L48–L49** — Publicly named helper to store that cookie under kind=session.

#### 13.10.5 L52–L55 · load_browser_state

```python
def load_browser_state(*, on_progress=None):
    return _saved_login("browser", on_progress=on_progress)


```

**Line-by-line explanation**

- **L52–L53** — Load serialized browser-cookie records under the separate kind=browser identity.

#### 13.10.6 L56–L59 · save_browser_state

```python
def save_browser_state(state, *, on_progress=None):
    return _saved_login("browser", state, on_progress=on_progress)


```

**Line-by-line explanation**

- **L56–L57** — Store serialized browser state separately from the direct VPN-session cookie.

#### 13.10.7 L60–L68 · clear_saved_login

```python
def clear_saved_login():
    cleared = [
        _saved_login("session", forget=True),
        _saved_login("browser", forget=True),
    ]
    if any(result is None for result in cleared):
        raise AuthenticationError("could not clear all saved sign-in state.")


```

**Line-by-line explanation**

- **L60** — Define full remembered-state clearing, a different action from disconnecting a tunnel.
- **L61–L64** — Attempt deletion of both session and browser kinds sequentially, collecting both results even if the first helper returns a failure indication.
- **L65–L66** — If either result is None, raise a readable failure after both attempts. Ordinary False no-match results are tolerated.

#### 13.10.8 L69–L70 · clear_session

```python
def clear_session(*, on_progress=None):
    return _saved_login("session", forget=True, on_progress=on_progress)
```

**Line-by-line explanation**

- **L69–L70** — Clear only the stale direct session cookie during a connect retry, preserving browser cookies that might help the next SSO attempt.

[[#4 Package branch — file map|↑ Package file map]]

### 13.11 Package source — src/tifrvpn/networkmanager.py

The NetworkManager/OpenConnect backend keeps command execution, state queries and verified TLS/secret handoff together. getpass and cryptography imports now live at the top; importing them does not itself start a tunnel or fetch a certificate.

**Relation to main:** [[TIFR Vpn TUI#7.3 tifr-vpn-auth.py|tifr-vpn-auth.py]] — activate retains verified TLS and memfd handoff; profile/state/down helpers are translated from main’s Zsh launcher.

**Functions and their purpose**

- **_run**, L25–L41: Define a common nmcli runner, with optional progress and forwarded subprocess options such as pass\_fds.
- **require_available**, L44–L51: Define explicit runtime/service checks; importing the module alone performs none of them.
- **profile_uuid**, L54–L77: Define lookup of the configured profile UUID by its friendly name.
- **setup_profile**, L80–L130: Define idempotent profile preparation with optional progress.
- **state**, L133–L134: Return the current GENERAL.STATE string for one exact UUID. This preserves transitional states for orchestration decisions.
- **details**, L137–L147: Return selected state/device/IPv4/IPv6 address and DNS detail text for that profile; the library result can retain it while the CLI chooses to display it.
- **validate_profile**, L150–L163: Define a defensive configuration check before using the profile for authentication/tunnel setup.
- **activate**, L166–L213: Intercept the fake activation call, inspect the anonymous descriptor payload and raise the intended fake failure to exercise cleanup.
- **deactivate**, L216–L217: Deactivate the exact profile through nmcli with a 20-second wait, forwarding optional progress and preserving failure semantics through \_run.

#### 13.11.1 L1–L24 · Module setup and definitions

```python
"""NetworkManager/OpenConnect backend, using nmcli without shell evaluation."""

import base64
import getpass
import hashlib
import os
import shutil
import socket
import ssl
import subprocess

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .config import HOST, URL
from .errors import NetworkManagerError, ProfileNotFound

PROFILE_NAME = "tifr-ivanti"
VPN_DATA = (
    f"gateway={URL},protocol=nc,prevent_invalid_cert=yes,"
    "cookie-flags=2,gateway-flags=2,gwcert-flags=2,resolve-flags=2"
)


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import base64 at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import getpass at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import hashlib at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Import os at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L7** — Import shutil at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L8** — Import socket at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L9** — Import ssl at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L10** — Import subprocess at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L12** — Bind x509 from cryptography at module scope. These names are then available to the functions below without a function-local import.
- **L13** — Bind Encoding, PublicFormat from cryptography.hazmat.primitives.serialization at module scope. These names are then available to the functions below without a function-local import.
- **L15** — Bind HOST, URL from .config at module scope. These names are then available to the functions below without a function-local import.
- **L16** — Bind NetworkManagerError, ProfileNotFound from .errors at module scope. These names are then available to the functions below without a function-local import.
- **L18** — Keep the saved connection name tifr-ivanti, allowing the new package to find a profile created by main.
- **L19–L22** — Build the shared plugin-data string: fixed portal, nc protocol, invalid-certificate prevention and flag value 2 for transient cookie/gateway/certificate/resolve secrets. +vpn.data later merges rather than replacing unrelated plugin data.

#### 13.11.2 L25–L43 · _run

```python
def _run(arguments, *, on_progress=None, **options):
    result = subprocess.run(
        ["nmcli", *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ, LC_ALL="C"),
        **options,
    )
    if result.returncode:
        raise NetworkManagerError(
            result.stderr.strip() or "NetworkManager operation failed.",
            returncode=result.returncode,
        )
    if on_progress is not None and result.stdout.strip():
        on_progress(result.stdout.rstrip())
    return result.stdout.strip()


```

**Line-by-line explanation**

- **L25** — Define a common nmcli runner, with optional progress and forwarded subprocess options such as pass\_fds.
- **L26–L33** — Run nmcli plus separately supplied arguments, capture both streams as text, avoid automatic check=True raising and force LC\_ALL=C for stable machine-readable output. \*\*options forwards supported keyword arguments without using a shell.
- **L34–L38** — On nonzero status, raise NetworkManagerError with stderr or a generic fallback and preserve the exact backend returncode for CLI/library callers.
- **L39–L40** — Forward nonempty normal output to a supplied callback after the command completes. Raw detail-returning calls normally omit that callback.
- **L41** — Return trimmed stdout as data to the caller.

#### 13.11.3 L44–L53 · require_available

```python
def require_available():
    if not all(
        shutil.which(name) for name in ("nmcli", "openconnect", "python3")
    ) or not os.access("/usr/libexec/nm-openconnect-service", os.X_OK):
        raise NetworkManagerError(
            "Install dependencies listed in README.md (NetworkManager-openconnect, OpenConnect and system Python bindings)."
        )
    _run(["general", "status"])


```

**Line-by-line explanation**

- **L44** — Define explicit runtime/service checks; importing the module alone performs none of them.
- **L45–L50** — Require nmcli, openconnect and python3 plus executable access to the hardcoded nm-openconnect-service path. Missing tools trigger the readable dependency error; this remains distribution-layout-specific despite the package refactor.
- **L51** — Check that NetworkManager responds using the common runner, discarding its returned normal status text at this call site.

#### 13.11.4 L54–L79 · profile_uuid

```python
def profile_uuid():
    result = subprocess.run(
        [
            "nmcli",
            "--get-values",
            "connection.uuid",
            "connection",
            "show",
            "id",
            PROFILE_NAME,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ, LC_ALL="C"),
    )
    if result.returncode or not result.stdout.strip():
        raise ProfileNotFound("no tifr-ivanti profile")
    uuid = result.stdout.strip()
    if "\n" in uuid:
        raise NetworkManagerError(
            "expected one NetworkManager profile named tifr-ivanti."
        )
    return uuid


```

**Line-by-line explanation**

- **L54** — Define lookup of the configured profile UUID by its friendly name.
- **L55–L69** — Call nmcli for only connection.uuid on tifr-ivanti, capturing text under a fixed locale. This uses a direct subprocess call because its nonzero/empty result has a special recoverable meaning here.
- **L70–L71** — Treat failed/empty lookup as ProfileNotFound. A later setup lookup additionally checks existing names before creating a profile, rather than trusting every failure as absence.
- **L72** — Trim trailing whitespace from the returned UUID text.
- **L73–L76** — Reject multiline UUID output as ambiguous profile names with a general NetworkManagerError, preventing accidental duplicate creation.
- **L77** — Return the unique identifier.

#### 13.11.5 L80–L111 · setup_profile

```python
def setup_profile(*, on_progress=None):
    require_available()
    try:
        uuid = profile_uuid()
    except ProfileNotFound:
        names = _run(["--get-values", "NAME", "connection", "show"]).splitlines()
        if PROFILE_NAME in names:
            raise NetworkManagerError(
                "ambiguous tifr-ivanti profile; resolve duplicate names before setup."
            ) from None
        _run(
            [
                "connection",
                "add",
                "type",
                "vpn",
                "vpn-type",
                "openconnect",
                "con-name",
                PROFILE_NAME,
                "connection.permissions",
                "user:" + getpass.getuser(),
                "connection.autoconnect",
                "no",
                "vpn.data",
                VPN_DATA,
            ],
            on_progress=on_progress,
        )
        return profile_uuid()
    service = _run(
        ["--get-values", "vpn.service-type", "connection", "show", "uuid", uuid]
```

**Line-by-line explanation**

- **L80** — Define idempotent profile preparation with optional progress.
- **L81** — Check prerequisites/service availability before profile modifications.
- **L82–L83** — Attempt existing-profile lookup.
- **L84–L89** — When that lookup reports missing, list all names and reject a name already present; this prevents blindly creating another tifr-ivanti after an ambiguous lookup/failure.
- **L90–L108** — Create a user-restricted OpenConnect VPN profile named tifr-ivanti, with autoconnect disabled and the shared VPN\_DATA settings. Each list element is one nmcli argument; values containing spaces stay intact.
- **L109** — After successful creation, query and return the actual generated UUID.
- **L110–L111** — For an existing profile, query its vpn.service-type.

#### 13.11.6 L112–L132 · setup_profile

```python
    )
    if service != "org.freedesktop.NetworkManager.openconnect":
        raise NetworkManagerError(
            "tifr-ivanti exists but uses a different VPN plugin; rename it before setup."
        )
    _run(
        [
            "connection",
            "modify",
            "uuid",
            uuid,
            "connection.autoconnect",
            "no",
            "+vpn.data",
            VPN_DATA,
        ],
        on_progress=on_progress,
    )
    return uuid


```

**Line-by-line explanation**

- **L112** — For an existing profile, query its vpn.service-type.
- **L113–L116** — Refuse to rewrite a same-name profile using another VPN plugin; ask the user to resolve the naming conflict.
- **L117–L129** — Update the existing exact UUID, disable autoconnect and merge the intended plugin settings, forwarding safe command progress to the optional callback.
- **L130** — Return the existing profile UUID after successful update.

#### 13.11.7 L133–L136 · state

```python
def state(uuid):
    return _run(["--get-values", "GENERAL.STATE", "connection", "show", "uuid", uuid])


```

**Line-by-line explanation**

- **L133–L134** — Return the current GENERAL.STATE string for one exact UUID. This preserves transitional states for orchestration decisions.

#### 13.11.8 L137–L149 · details

```python
def details(uuid):
    return _run(
        [
            "--fields",
            "GENERAL.STATE,GENERAL.DEVICES,IP4.ADDRESS,IP4.DNS,IP6.ADDRESS,IP6.DNS",
            "connection",
            "show",
            "uuid",
            uuid,
        ]
    )


```

**Line-by-line explanation**

- **L137–L147** — Return selected state/device/IPv4/IPv6 address and DNS detail text for that profile; the library result can retain it while the CLI chooses to display it.

#### 13.11.9 L150–L165 · validate_profile

```python
def validate_profile(uuid):
    service = _run(["-g", "vpn.service-type", "connection", "show", "uuid", uuid])
    data = _run(
        ["--escape", "no", "-g", "vpn.data", "connection", "show", "uuid", uuid]
    )
    settings = dict(
        item.strip().split(" = ", 1) for item in data.split(",") if " = " in item
    )
    if (
        service != "org.freedesktop.NetworkManager.openconnect"
        or settings.get("gateway") != URL
        or settings.get("protocol") != "nc"
    ):
        raise NetworkManagerError("Profile settings differ; run tifrvpn --setup.")


```

**Line-by-line explanation**

- **L150** — Define a defensive configuration check before using the profile for authentication/tunnel setup.
- **L151** — Read its backend service identifier.
- **L152–L154** — Read unescaped vpn.data text for expected key/value parsing.
- **L155–L157** — Build a dictionary by splitting comma-delimited items and each first ' = ' separator. This parser expects nmcli's current representation for these particular fields.
- **L158–L163** — Require the OpenConnect service, exact fixed gateway URL and nc protocol. Otherwise raise a setup instruction instead of handing session data to an unexpected profile.

#### 13.11.10 L166–L197 · activate

```python
def activate(uuid, cookie, *, on_progress=None):
    # Verify the gateway with the system trust store before pinning this session.
    context = ssl.create_default_context()
    with (
        socket.create_connection((HOST, 443), timeout=15) as connection,
        context.wrap_socket(connection, server_hostname=HOST) as tls,
    ):
        public_key = x509.load_der_x509_certificate(
            tls.getpeercert(binary_form=True)
        ).public_key()
        spki = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        fingerprint = (
            "pin-sha256:" + base64.b64encode(hashlib.sha256(spki).digest()).decode()
        )
        gateway_ip = tls.getpeername()[0]
    secrets = {
        "cookie": cookie,
        "gateway": "https://" + HOST,
        "gwcert": fingerprint,
        "resolve": f"{HOST}:{gateway_ip}",
    }
    fd = os.memfd_create("tifr-vpn-session", os.MFD_CLOEXEC)
    try:
        with os.fdopen(os.dup(fd), "w") as stream:
            stream.write(
                "".join(
                    f"vpn.secrets.{key}:{value}\n" for key, value in secrets.items()
                )
            )
        os.lseek(fd, 0, os.SEEK_SET)
        if on_progress is not None:
            on_progress("tifr VPN: starting NetworkManager tunnel")
```

**Line-by-line explanation**

- **L166** — Define tunnel activation with the profile UUID, accepted cookie and optional progress callback.
- **L167–L168** — Create a default certificate-verifying TLS context before deriving any public-key pin.
- **L169–L172** — Open a gateway TCP connection with a 15-second socket timeout and wrap it in hostname-verified TLS; the combined with statement closes both resources on exit.
- **L173–L175** — Read the binary DER peer certificate, parse it and extract the public key.
- **L176** — Serialize the key as DER SubjectPublicKeyInfo, the bytes to fingerprint for the OpenConnect pin.
- **L177–L179** — SHA-256 hash the key, Base64-encode the digest and prefix pin-sha256:. Normal trust verification happened first, so this is not an untrusted first-contact acceptance scheme.
- **L180** — Retain the actual gateway IP used by that verified connection.
- **L181–L186** — Assemble transient secrets: cookie, gateway origin, verified key pin and hostname-to-verified-IP resolve override. These values remain data and do not become command-line arguments.
- **L187** — Create the Linux anonymous memory-backed file descriptor with close-on-exec protection; pass\_fds below deliberately allows only this handle into nmcli. This avoids a named plaintext password file but does not guarantee immunity from swap/dumps/privileged inspection.
- **L188** — Ensure the original descriptor is always closed after activation or failure.
- **L189** — Duplicate the descriptor and open the duplicate as a text stream so writing/closing the stream leaves the original handle available for the child.
- **L190–L194** — Write one vpn.secrets.key:value newline-delimited record per secret. ''.join builds the payload in memory; none is printed to the terminal here.
- **L195** — Rewind to byte zero before the nmcli child reads the shared file resource.
- **L196–L197** — Report tunnel startup only through the supplied progress callback.

#### 13.11.11 L198–L215 · activate

```python
        _run(
            [
                "--wait",
                "90",
                "connection",
                "up",
                "uuid",
                uuid,
                "passwd-file",
                f"/proc/self/fd/{fd}",
            ],
            pass_fds=(fd,),
            on_progress=on_progress,
        )
    finally:
        os.close(fd)


```

**Line-by-line explanation**

- **L198–L211** — Activate the exact profile with nmcli --wait 90 connection up, point passwd-file to /proc/self/fd/N and explicitly inherit fd via pass\_fds. In the child, self means nmcli's own process. The common runner preserves command failures.
- **L212–L213** — Close the original anonymous descriptor in a finally block even when certificate handoff or activation raises an error.

#### 13.11.12 L216–L217 · deactivate

```python
def deactivate(uuid, *, on_progress=None):
    _run(["--wait", "20", "connection", "down", "uuid", uuid], on_progress=on_progress)
```

**Line-by-line explanation**

- **L216–L217** — Deactivate the exact profile through nmcli with a 20-second wait, forwarding optional progress and preserving failure semantics through \_run.

[[#4 Package branch — file map|↑ Package file map]]

### 13.12 Package source — src/tifrvpn/totp.py

Decode serialized Google Authenticator exports and calculate TOTP from validated account data. The parser explicitly describes integer-or-bytes fields; the decoder checks each field before comparisons, decoding or dictionary indexing. Two narrow TRY004 comments preserve ValueError for malformed serialized contents. Section 15 explains the representations and checks in order.

**Relation to main:** [[TIFR Vpn TUI#7.5 tifr-import-totp.py|tifr-import-totp.py]] — fields is renamed _fields; decode_export/current_code move into a pure-data algorithm module.

**Functions and their purpose**

- **_fields**, L12–L44: Yield integer field numbers paired with integer-or-bytes values, rejecting unsupported or truncated wire data.
- **_fields.varint**, L15–L26: Read one bounded variable-length integer and advance the enclosing byte offset.
- **decode_export**, L47–L102: Validate migration URL data and supported single-account fields, then return decoded setup data.
- **current_code**, L105–L114: Define current-code calculation; timestamp=None uses the real clock while tests can provide a fixed Unix timestamp.

#### 13.12.1 L1–L11 · Module setup and definitions

```python
"""Decode a single-account Google Authenticator export and calculate TOTP."""

import base64
import hashlib
import hmac
import struct
import time
from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import base64 at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import hashlib at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import hmac at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Import struct at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L7** — Import time at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L8** — Bind Iterator from collections.abc at module scope. These names are then available to the functions below without a function-local import.
- **L9** — Bind parse_qs, urlsplit from urllib.parse at module scope. These names are then available to the functions below without a function-local import.

#### 13.12.2 L12–L14 · _fields

```python
def _fields(data: bytes) -> Iterator[tuple[int, int | bytes]]:
    offset = 0

```

**Line-by-line explanation**

- **L12** — Define a byte-input parser yielding pairs: an integer field number and a value that can be either an integer or bytes. The vertical bar means either type is possible.
- **L13** — Start the byte-reading position at 0.

#### 13.12.3 L15–L46 · _fields.varint

```python
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


```

**Line-by-line explanation**

- **L15** — Define the nested variable-length-integer reader and state that successful calls return an int.
- **L16** — nonlocal offset means assignments update the containing fields function's position instead of creating a new local position inside varint.
- **L17** — Initialize the varint accumulator to integer zero before combining seven-bit payload groups.
- **L18** — Read up to ten 7-bit groups, shifting by 0, 7, 14, ... 63 bits. This bounds parsing effort for a malformed endless integer.
- **L19** — Before accessing a byte, check that input remains.
- **L20** — Fail clearly if the integer extends beyond the supplied bytes.
- **L21** — Read one byte as an integer from 0 to 255.
- **L22** — Advance to the next byte.
- **L23** — Keep the byte's lower seven bits with &127, shift them into position with <<shift, and combine them with the current value using |=. These are bit operations on binary digits.
- **L24** — The upper bit, value 128, indicates that another varint byte follows. If it is absent, this integer is complete. 'not byte & 128' is evaluated as not (byte & 128).
- **L25** — Return the decoded integer, preserving the updated enclosing offset.
- **L26** — If ten groups never completed the integer, reject the encoding rather than looping forever.
- **L28** — Allow the local value variable to hold an integer in one wire-format branch or bytes in another. The annotation describes the existing two possible representations.
- **L29** — Continue reading fields while unconsumed bytes remain.
- **L30** — Read the field tag as a varint.
- **L31** — The tag's upper bits encode the field number (>>3); its low three bits encode the wire type (&7). Python can assign both extracted values at once.
- **L32** — Protobuf field number 0 is invalid.
- **L33** — Reject that malformed tag.
- **L34** — Wire type 0 means the field value is another varint.
- **L35** — Decode that numeric value with the nested helper.
- **L36** — Handle fixed-width 64-bit fields (wire 1), length-delimited fields (wire 2), and fixed-width 32-bit fields (wire 5).
- **L37** — For wire 2, read the byte length; for fixed widths use 8 or 4 bytes. This line contains nested conditional expressions.
- **L38** — Check that the requested byte count fits the remaining input.
- **L39** — Reject truncated field data before slicing it.
- **L40** — Slice exactly the declared field byte count. Added formatting spaces around ':' do not change slice behavior; the stop index remains excluded.
- **L41** — Advance the current reading position by that many bytes.
- **L42** — An unsupported protobuf wire type takes the rejection branch rather than attempting an unsafe guessed parse.
- **L43** — Report the unsupported format.
- **L44** — yield returns one field pair to the caller and suspends this generator; iteration later resumes at the next field.

#### 13.12.4 L47–L78 · decode_export

```python
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
```

**Line-by-line explanation**

- **L47** — Accept QR URL text; subsequent validation turns its encoded contents into one supported account dictionary.
- **L48** — Split the URI into its parts without making any network request.
- **L49** — Require the migration URI scheme and the offline authority name. Despite looking like a URL, this payload is treated as local data here.
- **L50–L52** — Reject a URI whose scheme/authority is not the supported offline Google Authenticator migration export.
- **L53** — Get the first data query value, defaulting to empty text. parse\_qs normally treats + as spaces, so replace spaces with + before decoding this Base64 payload.
- **L54** — Reject an empty payload or one longer than 32,000 encoded characters to bound input size.
- **L55** — Raise a format error for that invalid size/content condition.
- **L56** — Guard Base64 decoding and binary-field parsing so malformed export bytes receive a safe ValueError.
- **L57–L61** — Base64-decode the validated payload with restored padding, feed it to the internal field generator and collect its decoded field pairs.
- **L62–L63** — Convert any ordinary parsing/backend exception into a generic ValueError without revealing raw export data or chained internals. The noqa comment suppresses a linter warning for this deliberate broad catch; it does not execute.
- **L64** — Collect field-1 values, which this migration format uses for account messages.
- **L65** — Require exactly one account and no batch-size greater than one, avoiding incomplete/multi-account imports.
- **L66** — For an outer batch-size field, reject a noninteger value or an integer greater than one. Short-circuit or prevents comparing bytes to a number.
- **L67** — Perform that batch-size check for each parsed outer field; this line completes the any(...) generator.
- **L68** — Require exactly one account and no batch-size greater than one, avoiding incomplete/multi-account imports.
- **L69** — Ask the user to export only the TIFR entry.
- **L70** — Take the sole account payload after the preceding exactly-one-account check.
- **L71** — Require serialized account contents to be bytes before passing them into the byte parser.
- **L72** — Report malformed QR contents as ValueError. Suppress only Ruff TRY004 on this line because the invalid type is inside serialized data, not the public text argument.
- **L73** — Parse the nested account bytes into a dictionary keyed by numeric field identifiers.
- **L74** — Read field 1 into one stable local variable so both the runtime check and type checker reason about the same value.
- **L75** — Require a nonempty byte sequence for the authenticator seed. Either a wrong type or empty bytes is invalid.
- **L76** — Reject an account without a usable seed.
- **L77** — Read the optional account-name bytes; use empty bytes if the field is absent.
- **L78** — Read optional issuer bytes; use empty bytes if that field is absent.

#### 13.12.5 L79–L104 · decode_export

```python
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


```

**Line-by-line explanation**

- **L79** — Require both text fields to be encoded bytes before calling their decode methods later.
- **L80** — Use the same malformed-data ValueError convention; the narrow TRY004 comment preserves validation and explains the linter exception.
- **L81** — Map the migration format's algorithm enumeration numbers to hash names.
- **L82** — Map its digit enumeration numbers to six or eight displayed digits.
- **L83** — Read the algorithm identifier once before validating it.
- **L84** — Read the digit-format identifier once. This numeric enum will be translated to a digit count rather than used directly as the count.
- **L85–L86** — Require TOTP type enum 2 and supported hash/digit enum values before normalizing the account.
- **L87** — Require an integer algorithm identifier before using it to look up a supported algorithm name.
- **L88** — Require that integer to exist in the supported algorithm map.
- **L89** — Require an integer digit-format identifier before using it as a digit-map key.
- **L90** — Require that digit-format identifier to be supported: 1 maps to six digits and 2 maps to eight.
- **L91** — Require TOTP type enum 2 and supported hash/digit enum values before normalizing the account.
- **L92–L94** — Explain unsupported authenticator settings using a safe ValueError.
- **L95** — Begin the normalized account dictionary returned as pure data to a caller, containing seed, labels and compatible algorithm settings.
- **L96** — Encode the validated seed bytes as Base32 text and remove padding for the displayed setup key. Encoding does not encrypt the seed.
- **L97** — Decode the validated account-name bytes as UTF-8 text.
- **L98** — Decode the validated issuer bytes as UTF-8 text.
- **L99** — Translate the checked algorithm identifier to SHA1, SHA256 or SHA512.
- **L100** — Translate the checked digit-format identifier into the actual displayed digit count.
- **L101** — Assume the migration account's time period is 30 seconds in this implementation.
- **L102** — Close that account dictionary and return it; it contains a long-term secret and is not printed by decode\_export.

#### 13.12.6 L105–L114 · current_code

```python
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
```

**Line-by-line explanation**

- **L105** — Define current-code calculation; timestamp=None uses the real clock while tests can provide a fixed Unix timestamp.
- **L106** — Get the Base32 seed text from the normalized account.
- **L107** — Restore padding to a multiple of 8 characters and decode the text back to raw key bytes.
- **L108** — Choose current/specified Unix time, convert to whole seconds and integer-divide by the period. // is floor division. Every instant in the same time window produces the same counter.
- **L109–L111** — HMAC the big-endian 8-byte time counter using the account's decoded seed and selected hashlib hash function, then obtain raw digest bytes.
- **L112** — Use the low four bits of the final digest byte to select an offset from 0 to 15, the HOTP dynamic-truncation step.
- **L113** — Read four digest bytes at the dynamic offset in big-endian order and clear the sign bit with 0x7FFFFFFF, yielding the same nonnegative 31-bit value as before.
- **L114** — Reduce the number modulo 10 raised to the number of digits, convert to text and pad leading zeros. For example, a 6-digit numeric value 123 must display as 000123. These steps implement the time-based algorithm tested against RFC 6238.

[[#4 Package branch — file map|↑ Package file map]]

### 13.13 Package source — src/tifrvpn/gui/__init__.py


Marks the optional GUI subpackage. Its actual implementations import heavy toolkits inside operations, so discovering/importing modules is safe without opening a window.


#### 13.13.1 L1–L1 · Module documentation, imports and shared definitions


```python
"""Optional windows. Importing this package does not start a GUI."""
```

**Line-by-line explanation**

- **L1** — Package docstring: this directory groups optional windows, and importing the package itself starts none of them.


[[#4 Package branch — file map|↑ Package file map]]

### 13.14 Package source — src/tifrvpn/gui/credential_setup.py

Qt dialog classes are imported at module scope. Calling setup creates/reuses a Qt application, verifies the saved vault entry and delegates encryption/storage to the headless credential helpers. Merely loading the module does not open the password prompt.

**Relation to main:** [[TIFR Vpn TUI#7.2 tifr-otp.py|tifr-otp.py]] — The interactive portion of setup keeps the dialogs and delegates ciphertext saving to credentials.save_password.

**Functions and their purpose**

- **setup**, L8–L51: Define GUI setup with selected paths/entry/recipient and optional progress; its integer result represents success or cancellation for the OTP command adapter.

#### 13.14.1 L1–L7 · Module setup and definitions

```python
"""Interactive credential setup; dialogs open only when setup is called."""

from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

from ..credentials import read_login, recipient_key, save_password


```

**Line-by-line explanation**

- **L1** — Document that importing Qt classes is separate from opening the setup dialogs.
- **L3** — Bind QApplication, QInputDialog, QLineEdit, QMessageBox from PySide6.QtWidgets at module scope. These names are then available to the functions below without a function-local import.
- **L5** — Bind read_login, recipient_key, save_password from ..credentials at module scope. These names are then available to the functions below without a function-local import.

#### 13.14.2 L8–L39 · setup

```python
def setup(password_file, database, entry, recipient, *, on_progress=None):
    _app = QApplication.instance() or QApplication(
        []
    )  # Keep Qt alive through all dialogs.
    if password_file.exists() or password_file.is_symlink():
        answer = QMessageBox.question(
            None,
            "TIFR OTP setup",
            f"Replace the encrypted password file?\n{password_file}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return 130
    recipient = recipient_key(recipient)
    while True:
        password, accepted = QInputDialog.getText(
            None,
            "TIFR OTP — encrypt KeePassXC password",
            f"Enter the MASTER PASSWORD for this KeePassXC database:\n{database}\n\n"
            "It will be verified locally, then encrypted with your GPG key.\n"
            "This is the database password, not your TIFR VPN password.",
            QLineEdit.EchoMode.Password,
        )
        if not accepted:
            return 130
        try:
            read_login(password, database, entry)
        except RuntimeError as error:
            QMessageBox.warning(None, "Could not verify database password", str(error))
            continue
        break
```

**Line-by-line explanation**

- **L8** — Define GUI setup with selected paths/entry/recipient and optional progress; its integer result represents success or cancellation for the OTP command adapter.
- **L9–L11** — Reuse or create QApplication and retain a local reference for the entire dialog sequence so Qt stays alive.
- **L12–L21** — If a ciphertext destination or symlink already exists, ask whether to replace it, default to No, and return 130 for cancellation.
- **L22** — Resolve the explicit/automatic GPG recipient before collecting the master password.
- **L23–L31** — Repeatedly prompt for the KeePass database master password in a masked field, clearly distinguishing it from the TIFR account password.
- **L32–L33** — Return cancellation without encryption if the input dialog was dismissed.
- **L34–L39** — Verify that the password opens the configured entry and yields login fields/TOTP. On readable failure show a warning and retry; break the loop only after local success. This does not test an actual server login.

#### 13.14.3 L40–L51 · setup

```python
    save_password(password, password_file, recipient)
    password = None
    if on_progress is not None:
        on_progress(
            f"Verified the TOTP entry and saved the GPG-encrypted database password: {password_file}"
        )
    QMessageBox.information(
        None,
        "TIFR OTP ready",
        "The encrypted password file is ready.\n\nRun tifr-otp to get the current code.",
    )
    return 0
```

**Line-by-line explanation**

- **L40** — Delegate GPG encryption and atomic ciphertext replacement to the headless credentials.save\_password function.
- **L41** — Drop this variable's plaintext reference; Python/Qt do not promise secure wiping of every prior memory copy.
- **L42–L45** — If requested, report only the ciphertext destination and successful local verification through the caller's callback.
- **L46–L50** — Show the completion dialog explaining the OTP command; no account password or seed is shown in that message.
- **L51** — Return success to cli.otp\_main after dialogs complete.

[[#4 Package branch — file map|↑ Package file map]]

### 13.15 Package source — src/tifrvpn/gui/sso.py

The isolated worker imports GTK/WebKit/Soup at module scope after selecting the intended namespace versions. login_cookie still performs all actual window, credential and cookie operations. Import placement does not remove the subprocess boundary between this browser and the tunnel controller.

**Relation to main:** [[TIFR Vpn TUI#7.3 tifr-vpn-auth.py|tifr-vpn-auth.py]] — signin_script, confirmation JavaScript and login_cookie move into the optional GUI module.

**Functions and their purpose**

- **signin_script**, L27–L60: Autofill only TIFR's Keycloak forms, returning status without field values.
- **login_cookie**, L63–L336: Define actual graphical login with optional quiet behavior and optional explicit Config. The controller launches it in a separate interpreter, so ordinary library import remains safe.
- **login_cookie.fill_ready**, L81–L87: Define the callback invoked after the JavaScript filling operation finishes. 'source' is the WebView and result is its asynchronous result handle.
- **login_cookie.form_ready**, L89–L149: Define the callback that receives inspected form status and decides whether to load credentials and fill it.
- **login_cookie.autofill_tick**, L151–L164: Define the repeating timer callback that looks for a ready SSO form.
- **login_cookie.remember_browser**, L166–L193: Define the callback that stores allowed browser cookies after a valid VPN session has been identified.
- **login_cookie.cookies_ready**, L195–L220: Define the callback for a cookie lookup associated with the gateway portal.
- **login_cookie.confirmation_ready**, L222–L231: Define the completion callback for quiet-mode concurrent-session warning detection.
- **login_cookie.check_cookies**, L233–L250: Define an event callback accepting any extra signal arguments, which it does not need. Different GTK signals supply different argument lists.
- **login_cookie.tls_error**, L252–L255: Define handling for TLS certificate errors from the embedded browser. Leading underscores indicate arguments intentionally unused.
- **login_cookie.close**, L257–L259: Define the callback for closing the sign-in window.
- **login_cookie.load_page**, L267–L268: Define a small function that begins portal navigation after any cookie restoration finishes.
- **login_cookie.restored**, L272–L279: Define the callback called after each restored cookie has been added to WebKit.
- **login_cookie.portal_tick**, L321–L323: Define a periodic portal-cookie check callback.

#### 13.15.1 L1–L26 · Module setup and definitions

```python
"""GTK/WebKit SSO window, executed in the isolated worker process."""

import json
import sys
import time
from urllib.parse import urlsplit

import gi

from .. import credentials
from ..auth import valid_session
from ..config import HOST, URL, load_config
from ..errors import AuthenticationError
from ..keyring import load_browser_state, save_browser_state

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
gi.require_version("Soup", "3.0")
from gi.repository import GLib, Gtk, Soup, WebKit2  # noqa: E402 - Select namespace versions first.

CONFIRMATION_SCRIPT = """(() => {
  if (location.origin !== 'https://sslvpn.tifr.res.in') return false;
  return /There are already other user sessions in progress|Continue will result in termination of the other session/i.test(document.body?.innerText || '');
})()"""


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import json at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import sys at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import time at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Bind urlsplit from urllib.parse at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Import gi at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L10** — Bind credentials from .. at module scope. These names are then available to the functions below without a function-local import.
- **L11** — Bind valid_session from ..auth at module scope. These names are then available to the functions below without a function-local import.
- **L12** — Bind HOST, URL, load_config from ..config at module scope. These names are then available to the functions below without a function-local import.
- **L13** — Bind AuthenticationError from ..errors at module scope. These names are then available to the functions below without a function-local import.
- **L14** — Bind load_browser_state, save_browser_state from ..keyring at module scope. These names are then available to the functions below without a function-local import.
- **L16** — Require GTK API 3.0 before importing the GTK namespace.
- **L17** — Require the WebKit2 4.1 namespace, matching the native WebKitGTK library used by this project.
- **L18** — Require Soup API 3.0 before importing it; these selections happen at module load.
- **L19** — Import GLib, Gtk, Soup, WebKit2 from the selected GI namespaces at module scope. Version selection above must happen first; the E402 comment documents that intentional import ordering.
- **L21** — Begin JavaScript that recognizes known concurrent-session warning wording on the VPN origin.
- **L22** — Only inspect confirmation text on the exact HTTPS VPN origin. An origin combines scheme, host and effective port.
- **L23** — Test visible page text for either of two known concurrent-session warnings, ignoring letter case with /i. ?. safely handles a missing body; || '' uses empty text if needed. This detects known wording; it does not automatically click a confirmation button.
- **L24** — Close the immediately invoked JavaScript warning detector and its Python multiline string; no browser evaluation occurs merely by constructing this constant.

#### 13.15.2 L27–L58 · signin_script

```python
def signin_script(values=None):
    """Autofill only TIFR's Keycloak forms, returning status without field values."""
    return (
        """((values) => {
      if (location.origin !== 'https://sso.tifr.res.in' ||
          !location.pathname.startsWith('/realms/TIFRSSO2/')) return JSON.stringify({step: null});
      const visible = el => el && !el.disabled && el.getClientRects().length > 0;
      if ([...document.querySelectorAll('[aria-invalid=true], .alert-error, #input-error, #input-error-password, #input-error-otp-code')].some(visible))
        return JSON.stringify({error: true});
      const form = document.querySelector('#kc-form-login, #kc-otp-login-form, #kc-totp-login-form');
      if (!form || new URL(form.action, location.href).origin !== location.origin)
        return JSON.stringify({step: null});
      const username = form.querySelector('input[name=username]');
      const password = form.querySelector('input[name=password]');
      const otp = form.querySelector('input[name=otp], input[name=totp]');
      const step = visible(otp) ? 'otp' : visible(password) ? 'password' : visible(username) ? 'username' : null;
      if (!step || form.dataset.tifrSubmitted) return JSON.stringify({step: null});
      if (values === null) return JSON.stringify({step});
      const set = (input, value) => {
        if (!visible(input) || value === undefined) return;
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(input, value);
        input.dispatchEvent(new Event('input', {bubbles: true}));
        input.dispatchEvent(new Event('change', {bubbles: true}));
      };
      set(username, values.username); set(password, values.password); set(otp, values.otp);
      if (step === 'otp' && !values.otp) return JSON.stringify({step: null});
      form.dataset.tifrSubmitted = 'true';
      const submit = form.querySelector('input[type=submit], button[type=submit]');
      if (submit) form.requestSubmit(submit); else form.requestSubmit();
      return JSON.stringify({submitted: step});
    })("""
        + json.dumps(values)
```

**Line-by-line explanation**

- **L27–L28** — Build the same restricted Keycloak form-inspection/autofill JavaScript described in the main guide; values=None means inspect without supplied credentials.
- **L29–L30** — Return a parenthesized concatenation of a multiline JavaScript string and JSON-encoded data; reformatting here does not execute the script until WebKit evaluates it later.
- **L31** — Require the exact TIFR SSO HTTPS origin. || means JavaScript logical OR, so either invalid origin or invalid path stops processing.
- **L32** — Also require the intended Keycloak realm path. Return JSON text with step:null if this is not an allowed page. This helps prevent filling credentials into an unexpected page.
- **L33** — Define a small JavaScript predicate: an input must exist, be enabled, and have layout rectangles to count as visible. This is a practical visibility check rather than a complete browser-perception model.
- **L34** — Select known validation/error elements. \[...nodeList\] turns results into an array; .some(visible) checks if any selected error is visible.
- **L35** — Return an error status when the page reports a known visible validation error, avoiding repeated blind submissions.
- **L36** — Locate one of the expected Keycloak login/OTP form IDs. CSS # selects an element ID; commas mean alternatives.
- **L37** — Require a form whose submission destination has the same origin as the current page. new URL resolves a relative form.action against the page address.
- **L38** — Return no actionable step if that destination check fails.
- **L39** — Locate the username input inside the chosen form using its name attribute.
- **L40** — Locate the password input similarly.
- **L41** — Locate either supported OTP input name: otp or totp.
- **L42** — Choose the current form step by visibility, preferring OTP, then password, then username. The ? : syntax is JavaScript's conditional expression.
- **L43** — Ignore unknown steps and a form already marked by this helper as submitted. dataset accesses HTML data-\* properties.
- **L44** — If no values were supplied, return only which form step is ready. This separates inspection from loading the password vault.
- **L45** — Define a helper that sets one input and dispatches browser events so the login page can notice the change.
- **L46** — Do nothing when the input is not visible or no value was provided for it.
- **L47** — Use the native HTMLInputElement value setter to update the field, including pages that wrap input handling. The secret is inserted into a DOM input, so it is present in the browser process during login.
- **L48** — Dispatch a bubbling input event. Bubbling lets handlers on parent elements see the event.
- **L49** — Dispatch a change event for login-page code listening for completed edits.
- **L50** — Close the JavaScript field-setting helper inside the generated script. Its statements run later within the browser's allowed page context.
- **L51** — Attempt to fill all three possible fields. Missing or hidden fields are skipped by the setter, so the same script supports multi-page and combined forms.
- **L52** — Do not submit an OTP form if a fresh OTP value was not supplied.
- **L53** — Mark this particular form as submitted to reduce duplicate submissions.
- **L54** — Find an explicit submit input or button when available.
- **L55** — Use requestSubmit with the submit button if found, otherwise requestSubmit without an argument. This respects normal browser form-submission behavior better than bypassing it with a raw submit call.
- **L56** — Return status naming the submitted step, without returning credentials.
- **L57–L58** — Complete the JavaScript function string, append json.dumps(values), close its invocation and finish the Python concatenation. JSON serialization treats credential values as data within the script.

#### 13.15.3 L59–L62 · signin_script

```python
        + ")"
    )


```

**Line-by-line explanation**

- **L59–L60** — Complete the JavaScript function string, append json.dumps(values), close its invocation and finish the Python concatenation. JSON serialization treats credential values as data within the script.

#### 13.15.4 L63–L80 · login_cookie

```python
def login_cookie(*, quiet=False, config=None):
    if not Gtk.init_check()[0]:
        raise AuthenticationError("A graphical session is required for TIFR SSO login.")
    context = WebKit2.WebContext.new_ephemeral()
    manager = context.get_cookie_manager()
    view = WebKit2.WebView.new_with_context(context)
    window = Gtk.Window(title="TIFR VPN — SSO sign in")
    window.set_default_size(900, 720)
    layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    address = Gtk.Label(label=URL)
    address.set_selectable(True)
    address.set_line_wrap(True)
    layout.pack_start(address, False, False, 8)
    layout.pack_start(view, True, True, 0)
    window.add(layout)
    session = {"cookie": None, "busy": False, "error": None}
    autofill = {"busy": False, "stopped": False, "submitted": set(), "provider": None}

```

**Line-by-line explanation**

- **L63** — Define actual graphical login with optional quiet behavior and optional explicit Config. The controller launches it in a separate interpreter, so ordinary library import remains safe.
- **L64** — Attempt GTK initialization and inspect its success flag. A usable display is required, either the real desktop or an Xvfb virtual display.
- **L65** — Raise the typed authentication failure when GTK cannot initialize a real or virtual display.
- **L66** — Create an ephemeral WebKit context: it avoids an ordinary persistent browser profile on disk. This program still deliberately saves selected cookies separately in the keyring.
- **L67** — Get this context's cookie manager, which can read and restore HTTP cookies.
- **L68** — Create a WebView, an embeddable browser widget, using that context.
- **L69** — Create a GTK top-level window and title it for TIFR sign-in.
- **L70** — Set its initial window size to 900 by 720 pixels.
- **L71** — Create a vertical layout box with 8 pixels between children.
- **L72** — Create a label displaying the initial portal address.
- **L73** — Allow selecting/copying the address label's text.
- **L74** — Allow the label to wrap instead of forcing an excessively wide window.
- **L75** — Add the address label to the layout without giving it expandable vertical space, with padding 8.
- **L76** — Add the browser, letting it expand to fill the remaining space.
- **L77** — Put the layout inside the window.
- **L78** — Initialize shared sign-in state: no accepted cookie, no pending cookie lookup and no error. Nested callbacks mutate this dictionary.
- **L79** — Initialize autofill state: busy/stopped flags, a set of submitted step names, and no loaded credential provider. A set keeps unique values and supports quick membership checks.

#### 13.15.5 L81–L88 · login_cookie.fill_ready

```python
    def fill_ready(source, result):
        autofill["busy"] = False
        try:
            source.evaluate_javascript_finish(result)
        except Exception:  # noqa: BLE001, S110 - Navigation can invalidate the JavaScript context.
            # Navigation can destroy the previous page's JS context.
            pass

```

**Line-by-line explanation**

- **L81** — Define the callback invoked after the JavaScript filling operation finishes. 'source' is the WebView and result is its asynchronous result handle.
- **L82** — Allow later autofill work by clearing the busy marker.
- **L83** — Guard completion of asynchronous field-filling JavaScript; navigation can invalidate the previous context.
- **L84** — Finish the WebKit asynchronous JavaScript operation. The return value is not needed here.
- **L85–L87** — Ignore a JavaScript-completion error caused by navigation destroying its old context. noqa suppresses chosen linter warnings; the comment itself changes no runtime behavior.

#### 13.15.6 L89–L120 · login_cookie.form_ready

```python
    def form_ready(source, result):
        try:
            state = json.loads(source.evaluate_javascript_finish(result).to_string())
            if state.get("error"):
                autofill["stopped"] = True
                if quiet:
                    session["error"] = (
                        "SSO rejected the saved login. Retry tifrvpn -c to see the error."
                    )
                    Gtk.main_quit()
                    return
                print(
                    "tifr VPN: SSO reported an error; autofill stopped. Check the sign-in window and saved credentials.",
                    file=sys.stderr,
                )
                return
            step = state.get("step")
            if not step or step in autofill["submitted"]:
                return
            if autofill["provider"] is None:
                selected = config if config is not None else load_config()
                credentials.validate_config(selected)
                database, password_file, entry = (
                    selected.database,
                    selected.password_file,
                    selected.entry,
                )
                helper = credentials
                master = helper.decrypt_password(password_file, allow_prompt=not quiet)
                login = helper.read_login(master, database, entry)
                autofill["provider"] = (helper, database, entry, master, login)
            helper, database, entry, master, login = autofill["provider"]
```

**Line-by-line explanation**

- **L89** — Define the callback that receives inspected form status and decides whether to load credentials and fill it.
- **L90** — Guard the form-inspection result and subsequent credential selection/submission logic.
- **L91** — Finish JavaScript evaluation, convert its result to a string, then parse that JSON string into a Python dictionary.
- **L92** — Check whether the page reported a visible validation error.
- **L93** — Stop further automatic filling to avoid repeated rejected submissions.
- **L94** — In quiet mode there is no visible window for the user to inspect, so stop with a readable diagnostic.
- **L95–L97** — Record a readable failure when quiet mode sees the page reject saved credentials; the hidden browser cannot be manually inspected there.
- **L98** — Ask GTK's event loop to stop.
- **L99** — Return immediately after quiet-mode rejected-credentials handling requested GTK shutdown.
- **L100–L103** — For visible mode, print a generic stopped-autofill message on the worker's stderr, preserving a human-operable window. Parent forwarding may be delayed by capture.
- **L104** — Return after visible-mode autofill was stopped; the human-readable browser window remains available.
- **L105** — Get the current recognized form step, or None if absent.
- **L106** — If no actionable step exists or that named step was already submitted during this attempt, do nothing. This set-level guard spans navigations as well as the DOM marker.
- **L107** — Ignore an unrecognized step or a named form step already submitted during this attempt.
- **L108** — Delay creation of the credential provider until autofill first needs it. This is an operation/data initialization check, not a deferred Python import.
- **L109** — Use an explicitly supplied Config when available, otherwise load the selected defaults/JSON/environment settings at that point.
- **L110** — Validate real vault existence and GPG availability at this credential-use point.
- **L111–L115** — Extract the selected Config's database, encrypted-password path and entry attributes for the existing autofill provider structure.
- **L116** — Use the imported credentials module itself as helper; no dictionary of runpy-loaded definitions is needed.
- **L117** — Decrypt through the normal helper function, forbidding a new GPG prompt when this worker is on the hidden display.
- **L118** — Read the saved account fields through the normal module function and keep them only as process data for filling the allowed form.
- **L119** — Cache the helper definitions, paths, entry, master password and login dictionary in this browser process for later form steps. The master password is therefore in process memory during the attempt.
- **L120** — Unpack the cached provider tuple for convenient use.

#### 13.15.7 L121–L150 · login_cookie.form_ready

```python
            values = dict(login)
            if step == "otp":
                # Leave enough time to unlock the vault and submit this code.
                if 30 - time.time() % 30 < 5:
                    return
                values["otp"] = helper.read_code(master, database, entry)
            autofill["submitted"].add(step)
            label = "authenticator code" if step == "otp" else step
            print(f"tifr VPN: submitting saved {label}", file=sys.stderr, flush=True)
            view.evaluate_javascript(
                signin_script(values), -1, None, None, None, fill_ready
            )
        except RuntimeError as error:
            session["error"] = str(error)
            Gtk.main_quit()
        except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
            autofill["stopped"] = True
            if quiet:
                session["error"] = (
                    "Automatic sign-in could not continue. Retry tifrvpn -c to see the sign-in window."
                )
                Gtk.main_quit()
                return
            print(
                "tifr VPN: automatic sign-in could not continue; check the sign-in window.",
                file=sys.stderr,
            )
        finally:
            autofill["busy"] = False

```

**Line-by-line explanation**

- **L121** — Make a new dictionary containing login values so an OTP can be added without altering the original login dictionary.
- **L122** — Only request a fresh authenticator code when the page is at the OTP step.
- **L123** — Comment describes avoiding a code that would expire during vault access and form submission.
- **L124** — time.time()%30 gives elapsed seconds within the current 30-second window; 30 minus that is remaining time. If fewer than 5 seconds remain, wait for a later timer tick. This hardcodes a 30-second period for automatic login.
- **L125** — Leave the OTP step unsubmitted when fewer than five seconds remain in its 30-second window, allowing a later timer tick to obtain a fresh code.
- **L126** — Read a fresh current TOTP through helper.read\_code only at the OTP step; the timing guard above still assumes 30-second periods.
- **L127** — Record the step as submitted before asynchronously filling/submitting the form, preventing duplicate timer-triggered work.
- **L128** — Choose a readable progress label, using authenticator code rather than the internal otp name.
- **L129** — Print the step label to standard error immediately. The actual username/password/code is not included.
- **L130–L132** — Start asynchronous form-filling JavaScript with fill\_ready as completion handler, keeping browser operations inside its event loop.
- **L133** — Catch deliberate configuration/vault RuntimeErrors.
- **L134** — Store the readable error text in shared session state.
- **L135** — Stop the GUI loop so the outer function can raise that error.
- **L136** — Deliberately catch unexpected autofill exceptions without dumping secret-bearing exception details; the linter suppression documents that choice.
- **L137** — Disable further automatic attempts.
- **L138** — For quiet mode, stop because the user cannot inspect the hidden page.
- **L139–L141** — For hidden mode, record a safe visible-retry instruction before stopping the GUI loop.
- **L142** — Stop the event loop.
- **L143** — Return after recording an unexpected hidden-autofill failure and requesting shutdown.
- **L144–L147** — For a visible browser, print the generic automation warning to worker stderr while leaving manual login possible.
- **L148** — The finally block always runs, including after return or an exception.
- **L149** — Release the autofill busy flag, allowing later ticks where autofill has not been stopped.

#### 13.15.8 L151–L165 · login_cookie.autofill_tick

```python
    def autofill_tick():
        page = urlsplit(view.get_uri() or "")
        if (
            not autofill["busy"]
            and not autofill["stopped"]
            and not view.is_loading()
            and page.scheme == "https"
            and page.hostname == "sso.tifr.res.in"
            and page.port in (None, 443)
            and page.path.startswith("/realms/TIFRSSO2/")
        ):
            autofill["busy"] = True
            view.evaluate_javascript(signin_script(), -1, None, None, None, form_ready)
        return True

```

**Line-by-line explanation**

- **L151** — Define the repeating timer callback that looks for a ready SSO form.
- **L152** — Parse the current page address, using empty text if WebKit has no URI yet.
- **L153–L161** — Only poll a fully loaded, enabled autofill state on HTTPS sso.tifr.res.in, default/443 port and the expected realm path. These checks precede credential entry.
- **L162** — Mark an inspection as pending before starting the asynchronous operation.
- **L163** — Run the inspection version of signin\_script, with no supplied credentials, and use form\_ready to process its response.
- **L164** — Return True to keep GLib's half-second autofill timer repeating. It is a timer-lifetime instruction, not a connected-VPN result.

#### 13.15.9 L166–L194 · login_cookie.remember_browser

```python
    def remember_browser(source, result):
        try:
            records = []
            for cookie in source.get_all_cookies_finish(result):
                domain = cookie.get_domain()
                if domain.lstrip(".") != "tifr.res.in" and not domain.endswith(
                    ".tifr.res.in"
                ):
                    continue
                expires = cookie.get_expires()
                records.append(
                    {
                        "name": cookie.get_name(),
                        "value": cookie.get_value(),
                        "domain": domain,
                        "path": cookie.get_path(),
                        "secure": cookie.get_secure(),
                        "http_only": cookie.get_http_only(),
                        "expires": expires.to_unix() if expires else None,
                    }
                )
            save_browser_state(
                json.dumps(records),
                on_progress=lambda message: print(message, file=sys.stderr),
            )
        except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
            print("tifr VPN: browser session could not be remembered.", file=sys.stderr)
        Gtk.main_quit()

```

**Line-by-line explanation**

- **L166** — Define the callback that stores allowed browser cookies after a valid VPN session has been identified.
- **L167** — Guard cookie serialization and remembered browser-state storage.
- **L168** — Create a list of cookie records to save.
- **L169** — Complete asynchronous retrieval of all cookies and iterate through them.
- **L170** — Read each cookie's domain.
- **L171–L174** — Only serialize cookies for tifr.res.in itself or dot-boundary subdomains, skipping unrelated hosts.
- **L175** — Read a possible expiry timestamp; session-only cookies may have no explicit expiry.
- **L176–L186** — Construct a plain record of cookie name/value/domain/path, Secure/HttpOnly flags and optional expiry; values can be authentication secrets and are not printed.
- **L187–L190** — Serialize selected cookie records to JSON and call the named browser-state saver; its warning callback writes safe diagnostics to this worker's stderr.
- **L191** — Catch cookie serialization/storage exceptions without logging raw cookie values.
- **L192** — Explain that browser state could not be remembered; failure to cache is separate from whether this login succeeded.
- **L193** — Stop the GTK loop now that the current successful session has been collected.

#### 13.15.10 L195–L221 · login_cookie.cookies_ready

```python
    def cookies_ready(source, result):
        session["busy"] = False
        try:
            cookies = source.get_cookies_finish(result)
        except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
            return
        for cookie in cookies:
            if cookie.get_name() == "DSID" and cookie.get_value():
                value = cookie.get_value()
                if any(char in value for char in "\r\n\0"):
                    session["error"] = "Invalid VPN session cookie."
                else:
                    candidate = "DSID=" + value
                    # Portal landing paths vary. Validate access rather than
                    # assuming a specific welcome-page URL means completion.
                    try:
                        if not valid_session(candidate):
                            return
                    except OSError:
                        return
                    session["cookie"] = candidate
                if session["error"]:
                    Gtk.main_quit()
                else:
                    manager.get_all_cookies(None, remember_browser)
                return

```

**Line-by-line explanation**

- **L195** — Define the callback for a cookie lookup associated with the gateway portal.
- **L196** — Release the pending-cookie-lookup flag.
- **L197** — Guard completion of the asynchronous portal-cookie request.
- **L198** — Get the cookies returned for the portal URL.
- **L199–L200** — If asynchronous cookie retrieval fails, return so later events/timers may retry rather than accepting an unverified result.
- **L201** — Inspect each returned cookie.
- **L202** — Look specifically for a nonempty DSID cookie, the session token expected by this VPN portal.
- **L203** — Get its raw value.
- **L204** — Reject carriage returns, newlines or NUL, which could corrupt headers or the line-based nmcli secret format later.
- **L205** — Store an invalid-cookie error for the outer sign-in function.
- **L206** — For a DSID with no forbidden control characters, construct/probe a candidate rather than recording an invalid-token error.
- **L207** — Prefix the value with DSID= to form the Cookie-header text expected by the gateway.
- **L208–L209** — Comments explain why a portal-access probe is more reliable here than assuming that a particular final page URL always means login completion.
- **L210** — Guard the network probe of a candidate portal session.
- **L211** — Probe whether the candidate actually grants portal access. A DSID can exist before concurrent-session confirmation is complete.
- **L212** — If portal access is not yet valid, return without accepting the token so later navigation/timer events can try again.
- **L213** — Handle network/system errors while probing.
- **L214** — On a probe OS/network error, leave the browser available for later checks rather than accepting the cookie without validation.
- **L215** — Save a validated session string in shared state. Its presence is how login\_cookie ultimately knows it succeeded.
- **L216** — If earlier validation recorded an invalid-cookie error, stop rather than export state.
- **L217** — Stop the event loop on that error.
- **L218** — After accepting a cookie without an error, collect allowed browser-state records before shutting down the sign-in loop.
- **L219** — Asynchronously retrieve all browser cookies, with remember\_browser as the completion callback.
- **L220** — Finish processing the first relevant DSID cookie; do not continue accepting additional candidates in this callback.

#### 13.15.11 L222–L232 · login_cookie.confirmation_ready

```python
    def confirmation_ready(source, result):
        try:
            required = source.evaluate_javascript_finish(result).to_boolean()
        except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
            return
        if required:
            session["error"] = (
                "TIFR requires confirmation to replace another session. Retry tifrvpn -c and review the warning."
            )
            Gtk.main_quit()

```

**Line-by-line explanation**

- **L222** — Define the completion callback for quiet-mode concurrent-session warning detection.
- **L223** — Guard completion of the quiet-mode session-conflict JavaScript inspection.
- **L224** — Convert the warning-inspection JavaScript result to a boolean.
- **L225–L226** — If warning-inspection JavaScript fails, skip this particular check while other cookie checks and the supervisor deadline remain active.
- **L227** — If a known replacement-session warning is present, require an ordinary visible attempt.
- **L228–L230** — Record that explicit session-replacement review is required. This helper does not click the confirmation automatically.
- **L231** — Stop the GTK loop.

#### 13.15.12 L233–L251 · login_cookie.check_cookies

```python
    def check_cookies(*_args):
        page = urlsplit(view.get_uri() or "")
        # A DSID may exist before the concurrent-session confirmation finishes;
        # cookies_ready checks portal access before accepting it.
        if (
            not view.is_loading()
            and page.hostname == HOST
            and not session["busy"]
            and not session["cookie"]
        ):
            session["busy"] = True
            if quiet:
                view.evaluate_javascript(
                    CONFIRMATION_SCRIPT, -1, None, None, None, confirmation_ready
                )
            manager.get_cookies(
                "https://" + HOST + "/dana/home/index.cgi", None, cookies_ready
            )

```

**Line-by-line explanation**

- **L233** — Define an event callback accepting any extra signal arguments, which it does not need. Different GTK signals supply different argument lists.
- **L234** — Read and parse the current browser location.
- **L235–L236** — Comments explain that a DSID alone is insufficient; cookies\_ready probes portal access before accepting it.
- **L237–L242** — Only start another gateway-cookie check after loading settles, while none is already pending and no session has yet been accepted.
- **L243** — Mark a cookie check as pending.
- **L244** — If quiet, also inspect the page for a known session-replacement warning.
- **L245–L247** — Asynchronously inspect known session-conflict warnings in quiet mode and route the result to confirmation\_ready.
- **L248–L250** — Asynchronously retrieve cookies scoped to the portal URL, using cookies\_ready to validate the resulting DSID.

#### 13.15.13 L252–L256 · login_cookie.tls_error

```python
    def tls_error(_view, _uri, _certificate, _errors):
        session["error"] = "SSO certificate verification failed. Contact TIFR IT."
        Gtk.main_quit()
        return False

```

**Line-by-line explanation**

- **L252** — Define handling for TLS certificate errors from the embedded browser. Leading underscores indicate arguments intentionally unused.
- **L253** — Record a certificate failure and tell the user to contact TIFR IT; this does not offer an insecure certificate bypass.
- **L254** — Stop the event loop.
- **L255** — Return False from the TLS error handler so the browser does not treat this callback as accepting an invalid certificate.

#### 13.15.14 L257–L266 · login_cookie.close

```python
    def close(*_args):
        Gtk.main_quit()
        return False

    manager.connect("changed", check_cookies)
    view.connect("load-changed", check_cookies)
    view.connect("notify::uri", lambda *_: address.set_text(view.get_uri() or URL))
    view.connect("load-failed-with-tls-errors", tls_error)
    window.connect("delete-event", close)

```

**Line-by-line explanation**

- **L257** — Define the callback for closing the sign-in window.
- **L258** — Stop GTK's event loop when the user closes the window.
- **L259** — Return False from the close-event handler to allow default window-close behavior after stopping the loop.
- **L261** — Register check\_cookies to run when the cookie manager reports a change. Here connect means attach an event handler, not open a VPN.
- **L262** — Also check cookies when the browser's load state changes.
- **L263** — When the URI changes, update the address label. lambda \*\_: ... is an anonymous function ignoring all supplied signal arguments.
- **L264** — Connect certificate-failure events to the strict TLS error handler.
- **L265** — Connect a user window-close request to the close callback.

#### 13.15.15 L267–L271 · login_cookie.load_page

```python
    def load_page():
        view.load_uri(URL)

    pending = {"count": 0}

```

**Line-by-line explanation**

- **L267** — Define a small function that begins portal navigation after any cookie restoration finishes.
- **L268** — Tell the WebView to load the fixed portal URL.
- **L270** — Initialize a mutable counter for outstanding asynchronous cookie-restoration operations.

#### 13.15.16 L272–L303 · login_cookie.restored

```python
    def restored(source, result):
        try:
            source.add_cookie_finish(result)
        except Exception:  # noqa: BLE001, S110 - Ignore an unusable saved cookie without logging its value.
            pass
        pending["count"] -= 1
        if not pending["count"]:
            load_page()

    try:
        records = json.loads(
            load_browser_state(
                on_progress=lambda message: print(message, file=sys.stderr)
            )
            or "[]"
        )
    except (ValueError, TypeError):
        records = []
    cookies = []
    for record in records:
        try:
            domain = record["domain"]
            if domain.lstrip(".") != "tifr.res.in" and not domain.endswith(
                ".tifr.res.in"
            ):
                continue
            expires = record.get("expires")
            if expires is not None and expires <= time.time():
                continue
            cookie = Soup.Cookie.new(
                record["name"], record["value"], domain, record["path"], -1
            )
```

**Line-by-line explanation**

- **L272** — Define the callback called after each restored cookie has been added to WebKit.
- **L273** — Guard completion of one restored cookie addition; failure of one saved cookie should not prevent fresh sign-in.
- **L274** — Finish that asynchronous add operation; any error is handled below.
- **L275–L276** — Ignore a single unusable restored cookie without printing its value; remaining restoration callbacks still complete the pending counter.
- **L277** — Decrease the number of outstanding restores whether this one succeeded or failed.
- **L278** — When all restore operations have completed, it is safe to start loading the portal.
- **L279** — Begin navigation using whatever cookies were successfully restored.
- **L281** — Attempt retrieval and JSON parsing of the saved browser-cookie records.
- **L282–L287** — Load saved browser state through the dedicated keyring helper, routing generic warnings to worker stderr, default to \[\] when absent and JSON-decode it.
- **L288** — Catch malformed JSON or an invalid input type.
- **L289** — Discard malformed cached records and continue with an empty list.
- **L290** — Build a fresh list of actual libsoup cookie objects to restore.
- **L291** — Loop through saved records. Cached data is still checked rather than blindly used.
- **L292** — Validate one cached cookie record independently, skipping malformed records while retaining usable ones.
- **L293** — Read the saved domain field.
- **L294–L297** — Reapply the TIFR-only domain restriction when reading cached records; saved data is not trusted blindly.
- **L298** — Read an optional expiry timestamp.
- **L299** — Reject cookies whose explicit expiry is already in the past. time.time() gives current Unix seconds.
- **L300** — Skip the expired cookie without attempting to restore it.
- **L301–L303** — Construct a libsoup cookie from validated saved fields before restoring its security flags and explicit expiry.

#### 13.15.17 L304–L320 · login_cookie

```python
            cookie.set_secure(record["secure"])
            cookie.set_http_only(record["http_only"])
            if expires is not None:
                cookie.set_expires(GLib.DateTime.new_from_unix_utc(expires))
            cookies.append(cookie)
        except (KeyError, TypeError, ValueError):
            continue
    pending["count"] = len(cookies)
    for cookie in cookies:
        manager.add_cookie(cookie, None, restored)
    if not cookies:
        load_page()
    window.show_all()
    autofill_timer = GLib.timeout_add(500, autofill_tick)

    # WebKit's load-changed signal can arrive before is_loading becomes false.
    # Check again after navigation has settled, including delayed portal redirects.
```

**Line-by-line explanation**

- **L304** — Restore the Secure flag.
- **L305** — Restore the HttpOnly flag.
- **L306** — If the saved cookie had a persistent expiry, restore it.
- **L307** — Convert saved Unix seconds to a GLib UTC date/time and attach it to the cookie.
- **L308** — Append the constructed cookie to the restoration list.
- **L309** — Catch common malformed-record errors.
- **L310** — Skip that record and continue with others.
- **L311** — Set the pending counter before starting callbacks; this avoids incorrectly navigating after only the first addition finishes.
- **L312** — Loop over all validated reconstructed cookies.
- **L313** — Begin each asynchronous addition with restored as its completion callback.
- **L314** — If there are no cookies, no callbacks will arrive to start navigation.
- **L315** — Load the portal immediately in that empty-cache case.
- **L316** — Show the GTK widgets. In quiet mode the same graphical window appears on the private Xvfb display rather than the real desktop.
- **L317** — Schedule autofill\_tick every 500 milliseconds, twice per second; store the timer ID for later removal.
- **L319–L320** — Comments explain the second timer: load-change events may fire before the page truly settles, especially with delayed redirects.

#### 13.15.18 L321–L336 · login_cookie.portal_tick

```python
    def portal_tick():
        check_cookies()
        return True

    portal_timer = GLib.timeout_add_seconds(2, portal_tick)
    try:
        Gtk.main()
    finally:
        GLib.source_remove(autofill_timer)
        GLib.source_remove(portal_timer)
        window.destroy()
    if session["error"]:
        raise AuthenticationError(session["error"])
    if not session["cookie"]:
        raise AuthenticationError("Sign-in cancelled; no VPN tunnel was started.")
    return session["cookie"]
```

**Line-by-line explanation**

- **L321** — Define a periodic portal-cookie check callback.
- **L322** — Run the same guarded cookie-check logic used by browser events.
- **L323** — Return True so the two-second portal-check timer remains scheduled until explicit cleanup.
- **L325** — Schedule portal\_tick roughly every 2 seconds and remember its ID.
- **L326** — Enter GTK with a finally cleanup block that removes timers and destroys the window on exit.
- **L327** — Enter GTK's event loop. It waits for browser/network/user/timer events and invokes callbacks until Gtk.main\_quit is called. Code after this line waits for the loop to finish.
- **L328** — Always perform GUI/timer cleanup when the event loop exits or an exception escapes.
- **L329** — Remove the autofill timer by its ID.
- **L330** — Remove the portal-cookie timer.
- **L331** — Destroy the sign-in window and its widgets.
- **L332** — After the loop, check whether a callback recorded an error.
- **L333** — Raise the typed AuthenticationError for a callback-recorded failure after GTK cleanup.
- **L334** — If no accepted cookie exists, the loop ended without successful authentication.
- **L335** — Report an incomplete/cancelled sign-in rather than returning a missing token.
- **L336** — Return the validated DSID string to this process's caller.

[[#4 Package branch — file map|↑ Package file map]]

### 13.16 Package source — src/tifrvpn/gui/qr_import.py

The local image/camera importer loads Qt, NumPy and ZXing at module scope. run verifies a QApplication, captures its clipboard interface, and defines the scanner window. The scan passes a BarcodeFormats selection object. Copying is guarded until an account exists; cleanup preserves clipboard text copied afterward. No real secret is needed to test those paths.

**Relation to main:** [[TIFR Vpn TUI#7.5 tifr-import-totp.py|tifr-import-totp.py]] — The Scanner/Qt workflow moves into run(image=...), importing algorithms from the parent package.

**Functions and their purpose**

- **run**, L29–L233: Define the scanner runner with keyword-only image=False; cli.import\_totp\_main parses --image and passes the boolean here.
- **run.Scanner.__init__**, L36–L124: Define the object initializer. self refers to the particular Scanner instance being initialized.
- **run.Scanner.open_image**, L126–L149: Define the image-file selection handler.
- **run.Scanner.frame**, L151–L165: Define the per-camera-frame callback. The argument named frame is a Qt video frame, separate from this method's own name.
- **run.Scanner.scan_image**, L167–L200: Define the common scanner used by both camera frames and selected image files.
- **run.Scanner.refresh_code**, L202–L209: Define code-display refresh.
- **run.Scanner.copy_key**, L211–L216: Copy only after a valid account exists, record the copied seed and schedule conditional cleanup.
- **run.Scanner.clear_clipboard**, L218–L221: Clear the live clipboard only when it still matches the seed this window copied.
- **run.Scanner.closeEvent**, L223–L229: Override QWidget's close-event handler so closing the window cleans up devices and displayed state.

#### 13.16.1 L1–L28 · Module setup and definitions

```python
"""Local webcam/image importer; scanning starts only when run is called."""

import time

import numpy as np
import zxingcpp
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtMultimedia import (
    QCamera,
    QMediaCaptureSession,
    QMediaDevices,
    QVideoSink,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..totp import current_code, decode_export


```

**Line-by-line explanation**

- **L1** — Document that imports load dependencies, while camera/image scanning begins only when run() is called.
- **L3** — Import time at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import numpy as np at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Import zxingcpp at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L7** — Bind Qt, QTimer from PySide6.QtCore at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Bind QImage, QPixmap from PySide6.QtGui at module scope. These names are then available to the functions below without a function-local import.
- **L9–L14** — Bind QCamera, QMediaCaptureSession, QMediaDevices, QVideoSink from PySide6.QtMultimedia at module scope. These names are then available to the functions below without a function-local import.
- **L15–L24** — Bind QApplication, QCheckBox, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget from PySide6.QtWidgets at module scope. These names are then available to the functions below without a function-local import.
- **L26** — Bind current_code, decode_export from ..totp at module scope. These names are then available to the functions below without a function-local import.

#### 13.16.2 L29–L34 · run

```python
def run(*, image=False):
    app = QApplication.instance() or QApplication([])
    if not isinstance(app, QApplication):
        raise RuntimeError("The QR importer requires a QApplication instance.")
    clipboard = app.clipboard()

```

**Line-by-line explanation**

- **L29** — Define the scanner runner with keyword-only image=False; cli.import\_totp\_main parses --image and passes the boolean here.
- **L30** — Reuse an existing Qt application if one exists or create a new one. The following app.exec is still a synchronous event-loop operation, so embedded use needs a suitable GUI lifecycle.
- **L31** — Check that the reused or newly created Qt application is specifically a QApplication, which supports widgets and the clipboard interface.
- **L32** — Stop with a clear error if another program already created only an unsuitable base application object.
- **L33** — Obtain the application clipboard interface once; the nested handlers use this same object.

#### 13.16.3 L35–L35 · run

```python
    class Scanner(QWidget):
```

**Line-by-line explanation**

- **L35** — Define the scanner QWidget subclass inside run, with methods capturing the run-local image choice and app object.

#### 13.16.4 L36–L67 · run.Scanner.__init__

```python
        def __init__(self):
            super().__init__()
            self.account = None
            self.last_scan = 0
            self.copied = None
            self.setWindowTitle("TIFR — import Google Authenticator locally")
            self.resize(860, 700)
            layout = QVBoxLayout(self)
            intro = QLabel(
                "On your phone: Google Authenticator → Transfer codes → Export → select only TIFR.\n"
                "Use a local QR image or hold the QR toward the camera. Everything stays on this laptop."
            )
            intro.setWordWrap(True)
            layout.addWidget(intro)
            self.preview = QLabel("Starting webcam…")
            self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.preview.setMinimumSize(640, 360)
            layout.addWidget(self.preview, 1)
            self.open_button = QPushButton("Open QR image from this laptop…")
            self.open_button.clicked.connect(self.open_image)
            layout.addWidget(self.open_button)
            self.status = QLabel("No camera frames or setup keys are saved to files.")
            self.status.setWordWrap(True)
            layout.addWidget(self.status)
            self.key = QLineEdit()
            self.key.setReadOnly(True)
            self.key.setEchoMode(QLineEdit.EchoMode.Password)
            self.key.setPlaceholderText(
                "The setup key will appear here after a successful scan"
            )
            layout.addWidget(self.key)
            show = QCheckBox("Reveal setup key in this window")
```

**Line-by-line explanation**

- **L36** — Define the object initializer. self refers to the particular Scanner instance being initialized.
- **L37** — Initialize the inherited QWidget part before configuring this custom window.
- **L38** — No decoded account exists yet.
- **L39** — Initialize the last-scan time for throttling camera processing.
- **L40** — Track which setup key this tool placed on the clipboard so it can avoid erasing unrelated later clipboard text.
- **L41** — Set the window title.
- **L42** — Choose its initial size: 860 by 700 pixels.
- **L43** — Create a vertical layout owned by this window.
- **L44–L47** — Create the phone-side export/local-processing instruction label. Adjacent quoted strings concatenate into one message.
- **L48** — Wrap long instructions to the available width.
- **L49** — Add that label to the layout.
- **L50** — Create a label that will show camera preview frames or status text.
- **L51** — Center its content using a Qt alignment flag.
- **L52** — Give the preview a minimum area of 640 by 360 pixels.
- **L53** — Add it to the layout with stretch factor 1, letting it take available space.
- **L54** — Create a button for choosing an existing local QR image.
- **L55** — Connect its clicked signal to this instance's open\_image method. The method is passed without () so it runs on future clicks rather than immediately.
- **L56** — Add the file-selection button to the window layout.
- **L57** — Create a status label stating that this program does not save captured frames/setup keys as files. Selecting an image does not remove the original image file.
- **L58** — Allow status messages to wrap.
- **L59** — Add the status label.
- **L60** — Create a single-line field for the decoded setup seed.
- **L61** — Make it read-only so accidental typing cannot alter the displayed seed.
- **L62** — Mask its text by default, like a password field.
- **L63–L65** — Provide placeholder text for the masked seed field before a successful import.
- **L66** — Add the masked field to the layout.
- **L67** — Create a checkbox controlling whether the seed is visibly revealed.

#### 13.16.5 L68–L99 · run.Scanner.__init__

```python
            show.toggled.connect(
                lambda checked: self.key.setEchoMode(
                    QLineEdit.EchoMode.Normal
                    if checked
                    else QLineEdit.EchoMode.Password
                )
            )
            layout.addWidget(show)
            self.copy = QPushButton(
                "Copy setup key for KeePassXC (clears after 60 seconds)"
            )
            self.copy.setEnabled(False)
            self.copy.clicked.connect(self.copy_key)
            layout.addWidget(self.copy)
            self.code = QLabel()
            self.code.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            layout.addWidget(self.code)
            instructions = QLabel(
                "After scanning: KeePassXC → right-click TIFR → TOTP → Set up TOTP.\n"
                "Paste the setup key and match the displayed digits, period and algorithm.\n"
                "Compare the codes with your phone, then save the KeePassXC database."
            )
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
            self.session = QMediaCaptureSession(self)
            self.sink = QVideoSink(self)
            self.session.setVideoSink(self.sink)
            self.sink.videoFrameChanged.connect(self.frame)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_code)
```

**Line-by-line explanation**

- **L68–L74** — When the reveal checkbox changes, switch the seed field between normal and masked display. This changes visual presentation, not whether the seed is held in process memory.
- **L75** — Add the reveal checkbox.
- **L76–L78** — Create the copy-key button and describe the intended 60-second live clipboard cleanup.
- **L79** — Disable the button until a valid account has been decoded.
- **L80** — Connect future clicks to copy\_key.
- **L81** — Add the copy button.
- **L82** — Create a label for the currently calculated TOTP and countdown.
- **L83–L85** — Allow the displayed short-lived code to be selected with the mouse.
- **L86** — Add the code label.
- **L87–L91** — Explain the manual KeePassXC import, matching settings, phone comparison and database save; the scanner does not perform that final database write itself.
- **L92** — Wrap these instructions.
- **L93** — Add them to the layout.
- **L94** — Create a media capture session associated with this window.
- **L95** — Create a video sink that receives camera frames for Python processing.
- **L96** — Route session video output to that sink.
- **L97** — Connect each new-frame event to this instance's frame method. This 'connect' is Qt event registration, unrelated to establishing a VPN.
- **L98** — Create a timer owned by this window.
- **L99** — Connect each timer event to refresh\_code.

#### 13.16.6 L100–L125 · run.Scanner.__init__

```python
            self.timer.start(1000)
            cameras = QMediaDevices.videoInputs() if not image else []
            if not cameras:
                self.preview.setText("Open the QR image using the button below")
                self.status.setText(
                    "Image mode: the webcam is off. No decoded setup keys are saved to files."
                )
                return
            self.camera = QCamera(cameras[0], self)
            formats = [
                fmt
                for fmt in cameras[0].videoFormats()
                if 640 <= fmt.resolution().width() <= 1920
            ]
            if formats:
                self.camera.setCameraFormat(
                    max(formats, key=lambda fmt: fmt.resolution().width())
                )
            self.session.setCamera(self.camera)
            self.camera.errorOccurred.connect(
                lambda *_: self.status.setText(
                    "Camera error: " + self.camera.errorString()
                )
            )
            self.camera.start()

```

**Line-by-line explanation**

- **L100** — Run the timer every 1000 milliseconds, updating the current code/countdown once per second.
- **L101** — Use the run parameter image rather than args.image. In image-only mode choose no cameras and avoid webcam startup; this function no longer parses command-line arguments itself.
- **L102** — If there are no cameras, fall back to image selection.
- **L103** — Replace preview text with a prompt to use the image button.
- **L104–L106** — Explain the image-mode fallback without exposing a decoded setup seed in that status text.
- **L107** — Return from the window initializer after configuring image-only fallback. The window still exists and can open an image; this does not exit the program.
- **L108** — Create a camera object for the first detected device, owned by this window.
- **L109–L113** — Filter advertised camera formats by a practical width range, using a list comprehension.
- **L114** — Only set a preferred format when the filtered list is nonempty.
- **L115–L117** — Choose the widest format from that filtered list; no special frame-rate choice is made here.
- **L118** — Attach the camera to the capture session.
- **L119–L123** — Update status on camera errors using a callback that ignores extra signal arguments. These are device diagnostics, not seed output.
- **L124** — Start the camera asynchronously.

#### 13.16.7 L126–L150 · run.Scanner.open_image

```python
        def open_image(self):
            if self.account:
                return
            if hasattr(self, "camera"):
                self.camera.stop()
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Google Authenticator export QR",
                "",
                "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)",
            )
            if not path:
                return
            image = QImage(path)
            if image.isNull():
                self.status.setText(
                    "Could not open this image. Select a PNG or JPEG containing the export QR."
                )
                return
            self.scan_image(image)
            if not self.account:
                self.status.setText(
                    "No supported single-entry export QR was found. Use the original full-resolution image and select only TIFR when exporting."
                )

```

**Line-by-line explanation**

- **L126** — Define the image-file selection handler.
- **L127** — If an account has already been accepted, ignore further import requests.
- **L128** — Ignore another image request after a successful account has already been accepted.
- **L129** — Check whether this Scanner ever initialized a camera attribute; image-only instances may not have one.
- **L130** — Stop the camera before opening the file chooser.
- **L131–L136** — Open the image chooser and keep its selected path, ignoring the selected filter label. An earlier initialized camera is stopped before this chooser.
- **L137** — An empty path means the user cancelled.
- **L138** — Return when the file chooser was cancelled. A camera stopped before the chooser is not automatically restarted by this code.
- **L139** — Load the selected file into a Qt image in memory.
- **L140** — Check whether image loading failed.
- **L141–L143** — Show a readable image-load failure rather than attempting QR decoding on an invalid QImage.
- **L144** — Stop this image attempt after reporting a null/unloadable image.
- **L145** — Try scanning the loaded image.
- **L146** — If no account was accepted, provide a more specific single-entry/full-resolution suggestion.
- **L147–L149** — If no supported account was imported, suggest the full-resolution single-TIFR export image.

#### 13.16.8 L151–L166 · run.Scanner.frame

```python
        def frame(self, frame):
            if self.account or time.monotonic() - self.last_scan < 0.2:
                return
            self.last_scan = time.monotonic()
            image = frame.toImage()
            if image.isNull():
                return
            self.preview.setPixmap(
                QPixmap.fromImage(image).scaled(
                    self.preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.scan_image(image)

```

**Line-by-line explanation**

- **L151** — Define the per-camera-frame callback. The argument named frame is a Qt video frame, separate from this method's own name.
- **L152** — Skip work if an account is already accepted, or if fewer than 0.2 seconds elapsed since the last scan. This caps scanning near five attempts per second without blocking the camera's own frame delivery.
- **L153** — Skip a camera frame when already complete or when fewer than 0.2 seconds have elapsed since the last scan.
- **L154** — Record the current monotonic time, a clock suitable for elapsed durations because normal wall-clock adjustments do not make it jump backwards.
- **L155** — Convert the received video frame to a QImage for preview and scanning.
- **L156** — If conversion produced no usable image, skip it.
- **L157** — Ignore a video frame that could not be converted into a usable QImage.
- **L158–L164** — Scale a pixmap smoothly into the preview with aspect ratio preserved; the decoder receives the original image rather than that smaller preview.
- **L165** — Attempt QR detection on that frame's full image.

#### 13.16.9 L167–L198 · run.Scanner.scan_image

```python
        def scan_image(self, image):
            gray = image.convertToFormat(QImage.Format.Format_Grayscale8)
            pixels = np.frombuffer(gray.constBits(), dtype=np.uint8).reshape(
                gray.height(), gray.bytesPerLine()
            )[:, : gray.width()]
            try:
                results = zxingcpp.read_barcodes(
                    pixels, formats=zxingcpp.BarcodeFormats(zxingcpp.BarcodeFormat.QRCode)
                )
                for result in results:
                    self.account = decode_export(result.text)
                    break
            except Exception:  # noqa: BLE001 - Never expose authentication data from backend errors.
                self.status.setText(
                    "Could not import this QR. Export only the TIFR entry from Google Authenticator and try again."
                )
                return
            if self.account:
                if hasattr(self, "camera"):
                    self.camera.stop()
                self.open_button.setEnabled(False)
                print(
                    "QR decoded locally; camera stopped. Complete the import in KeePassXC.",
                    flush=True,
                )
                self.preview.clear()
                self.preview.setText("QR scanned — camera is off")
                self.key.setText(self.account["secret"])
                self.copy.setEnabled(True)
                self.status.setText(
                    f"Account: {self.account['name']} | Issuer: {self.account['issuer']}\n"
                    f"Settings: {self.account['algorithm']}, {self.account['digits']} digits, {self.account['period']} seconds"
```

**Line-by-line explanation**

- **L167** — Define the common scanner used by both camera frames and selected image files.
- **L168** — Convert to an 8-bit grayscale image, giving one intensity byte per pixel rather than separate red/green/blue channels.
- **L169–L171** — View grayscale memory as an unsigned-byte array using real row stride, then slice away per-row padding before QR decoding.
- **L172** — Guard barcode decoding/export parsing so a malformed image/QR does not expose its raw data through an exception report.
- **L173** — Ask ZXing only for QRCode results; no network operation is involved.
- **L174** — Wrap the QRCode format identifier in BarcodeFormats, the selection-object type expected by the installed ZXing API. The pixels are the grayscale NumPy view built above.
- **L175** — Ask ZXing only for QRCode results; no network operation is involved.
- **L176** — Loop over detected QR results.
- **L177** — Parse one QR's text as a supported single-account migration export and save the normalized account.
- **L178** — Stop scanning further decoded QR results after the first supported account is accepted. A prior unsupported result raising an exception takes the error path instead.
- **L179–L183** — Catch QR decoder/export parser exceptions and show a safe generic retry instruction instead of raw QR contents.
- **L184** — If an account was decoded, update the UI into the completed/import-ready state.
- **L185** — Check whether camera hardware was initialized.
- **L186** — Stop it immediately after successful decoding.
- **L187** — Disable choosing another image during this instance's completed state.
- **L188–L191** — Print a generic local-success message; this specialized interactive tool intentionally prints that message even though the public VPN controller uses optional callbacks for progress.
- **L192** — Remove the camera image from the preview label.
- **L193** — Replace it with a camera-off success message.
- **L194** — Put the sensitive Base32 seed in the read-only masked field. Masking reduces casual viewing, but the value is still stored in GUI/process memory.
- **L195** — Enable copying the setup seed.
- **L196** — Begin a status message showing account metadata and TOTP settings.
- **L197–L198** — Display account/issuer metadata and algorithm/digits/period; the long-term seed stays in the separate masked/read-only field until deliberately revealed/copied.

#### 13.16.10 L199–L201 · run.Scanner.scan_image

```python
                )
                self.refresh_code()

```

**Line-by-line explanation**

- **L199** — Close the account/settings status-label update; the separate seed field remains masked until the user chooses to reveal it.
- **L200** — Update the code/countdown immediately instead of waiting for the next one-second timer event.

#### 13.16.11 L202–L210 · run.Scanner.refresh_code

```python
        def refresh_code(self):
            if self.account:
                remaining = (
                    self.account["period"] - int(time.time()) % self.account["period"]
                )
                self.code.setText(
                    f"Current code: {current_code(self.account)}   ({remaining} seconds remaining)"
                )

```

**Line-by-line explanation**

- **L202** — Define code-display refresh.
- **L203** — Only calculate/display a code if an account is available.
- **L204–L206** — Compute remaining whole seconds in the configured TOTP period using modulo arithmetic.
- **L207–L209** — Display the locally computed current code and countdown, without fetching codes from a remote server.

#### 13.16.12 L211–L217 · run.Scanner.copy_key

```python
        def copy_key(self):
            if self.account is None:
                return
            self.copied = self.account["secret"]
            clipboard.setText(self.copied)
            QTimer.singleShot(60000, self.clear_clipboard)

```

**Line-by-line explanation**

- **L211** — Define the copy-button handler.
- **L212** — If no valid account has been decoded, there is no seed to copy; do not index None.
- **L213** — Return immediately from this handler without changing the clipboard when no account exists.
- **L214** — Remember the seed this window is copying, so cleanup can check ownership of the current clipboard text.
- **L215** — Copy this account seed through the verified QApplication clipboard interface. No seed is printed to the terminal.
- **L216** — Schedule a one-time clear\_clipboard callback 60,000 milliseconds later. It requires the GUI event loop to keep running normally.

#### 13.16.13 L218–L222 · run.Scanner.clear_clipboard

```python
        def clear_clipboard(self):
            if self.copied and clipboard.text() == self.copied:
                clipboard.clear()
            self.copied = None

```

**Line-by-line explanation**

- **L218** — Define guarded clipboard cleanup.
- **L219** — Only clear when this window copied a seed and the current clipboard still contains exactly that seed; preserve text copied later by the user.
- **L220** — Clear the live clipboard after the ownership/content check. Independent clipboard-manager history is outside this operation.
- **L221** — Drop the stored copied-value reference after attempting cleanup.

#### 13.16.14 L223–L233 · run.Scanner.closeEvent

```python
        def closeEvent(self, event):
            if hasattr(self, "camera"):
                self.camera.stop()
            self.clear_clipboard()
            self.key.clear()
            self.account = None
            event.accept()

    window = Scanner()
    window.show()
    return app.exec()
```

**Line-by-line explanation**

- **L223** — Override QWidget's close-event handler so closing the window cleans up devices and displayed state.
- **L224** — If a camera object exists, stop it.
- **L225** — Request camera stop.
- **L226** — Attempt clipboard cleanup immediately rather than waiting for the timer.
- **L227** — Clear the seed field.
- **L228** — Drop the normalized account reference. This is not guaranteed secure wiping of every copy of the seed in memory.
- **L229** — Accept the close event so the window may close.
- **L231–L233** — Create/show Scanner and synchronously enter Qt's event loop, returning its result after the application exits. Exceptions are handled by the separate CLI adapter.

[[#4 Package branch — file map|↑ Package file map]]

### 13.17 Package source — tests/test_imports.py

A child interpreter is supplied fake dependency interfaces, then imports every application module while subprocess, socket and configuration-read operations are forbidden. This revised test permits the requested module-level imports. It does not claim the real package works without installed native/Python dependencies.

**Functions and their purpose**

- **ImportTests.test_all_modules_import_without_external_actions**, L12–L54: Import all application modules in an isolated child with fake dependency interfaces while blocking application external work.

#### 13.17.1 L1–L10 · Module setup and definitions

```python
"""Module imports load dependencies without starting application operations."""

import subprocess
import sys
import unittest
from pathlib import Path

import tifrvpn


```

**Line-by-line explanation**

- **L1** — State the current import contract: dependencies may be imported, but importing application modules must not start credential, network, GUI or subprocess operations.
- **L3** — Import subprocess at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import sys at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import unittest at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Bind Path from pathlib at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Import tifrvpn at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.

#### 13.17.2 L11–L11 · Module setup and definitions

```python
class ImportTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L11** — Define ImportTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.

#### 13.17.3 L12–L43 · ImportTests.test_all_modules_import_without_external_actions

```python
    def test_all_modules_import_without_external_actions(self):
        package_root = str(Path(tifrvpn.__file__).resolve().parent.parent)
        script = """
import sys
sys.path.insert(0, sys.argv[1])
import pathlib
import pkgutil
import socket
import subprocess
from types import ModuleType
from unittest.mock import patch
def forbidden(*args, **kwargs):
    raise AssertionError("External operation during import")
# Supply dependency interfaces without running third-party initialization.
# Importing a name is allowed; calling it to start an operation is not.
for name in (
    "gi", "gi.repository", "cryptography", "cryptography.hazmat",
    "cryptography.hazmat.primitives", "cryptography.hazmat.primitives.serialization",
    "PySide6", "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets",
    "PySide6.QtMultimedia", "numpy", "zxingcpp",
):
    module = ModuleType(name)
    module.__path__ = []
    module.__getattr__ = lambda name: forbidden
    sys.modules[name] = module
sys.modules["gi"].require_version = lambda *args: None
with patch.object(subprocess, "run", forbidden), patch.object(subprocess, "Popen", forbidden), \\
        patch.object(socket, "create_connection", forbidden), patch.object(pathlib.Path, "read_text", forbidden):
    import tifrvpn
    for module in pkgutil.walk_packages(tifrvpn.__path__, "tifrvpn."):
        __import__(module.name)
    assert callable(tifrvpn.connect)
```

**Line-by-line explanation**

- **L12** — Test application import behavior in a separate isolated interpreter with supplied fake dependency interfaces.
- **L13** — Locate the imported package's parent directory explicitly for the isolated subprocess, rather than relying on cwd or installed third-party dependencies.
- **L14** — Begin an embedded Python script string. Lines inside the string will execute in a separate interpreter when subprocess.run invokes -c below, not as part of this outer test's immediate flow.
- **L15** — Inside the child script, import interpreter/search-path access.
- **L16** — Insert only the explicitly supplied package root into the child search path. The test intentionally uses -I -S so neither normal PYTHONPATH nor site-package startup explains a passing import.
- **L17** — Load filesystem path helpers so file-reading can be replaced with a forbidden function.
- **L18** — Load package discovery to enumerate every tifrvpn submodule, including GUI and worker entry modules.
- **L19** — Load socket APIs so attempted live connections during import can be blocked.
- **L20** — Load subprocess APIs so attempted child startup during import can be blocked.
- **L21** — Inside the child-script string, import ModuleType so the test can create fake dependency module objects.
- **L22** — Load patch for temporary runtime substitutions within the child test script.
- **L23** — Define a replacement callable accepting arbitrary arguments for prohibited external operations.
- **L24** — Raise immediately if module import attempts to run a child, open a socket or read configuration text.
- **L25** — Explain why the child script supplies dependency interfaces: avoid native library initialization while inspecting application import behavior.
- **L26** — Allow importing dependency names, but arrange for calls that start operations to fail the test.
- **L27** — Iterate through the dependency module names to supply in the child interpreter.
- **L28** — Supply GI and cryptography package interfaces; these are fake module identities only.
- **L29** — Supply the nested cryptography namespaces imported by the network backend.
- **L30** — Supply the Qt modules imported by the command adapters and GUI helpers.
- **L31** — Also supply multimedia, NumPy and ZXing interfaces required by the QR importer.
- **L32** — Finish the dependency-name list and begin creating each fake module.
- **L33** — Create an empty module object carrying that dependency name.
- **L34** — Mark it as package-like so nested imports can be resolved from the supplied fake modules.
- **L35** — Make missing imported attributes resolve to the forbidden callable. Looking up a name succeeds; invoking it to perform work fails.
- **L36** — Register this fake under its import name in the child interpreter module cache.
- **L37** — Permit GI namespace-version selection during import; this fake returns None and does not load native bindings.
- **L38–L39** — Temporarily replace subprocess.run/Popen, socket.create\_connection and Path.read\_text with that forbidden callable while importing the package tree.
- **L40** — Import the public package under all these restrictions.
- **L41** — Discover its nested modules with fully qualified tifrvpn. names.
- **L42** — Import each discovered module, including private worker and optional GUI modules, without calling their operations.
- **L43** — Require the public connect name to exist as a callable without actually connecting.

#### 13.17.4 L44–L54 · ImportTests.test_all_modules_import_without_external_actions

```python
    assert callable(tifrvpn.disconnect)
"""
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", script, package_root],
            check=False,
            cwd="/",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
```

**Line-by-line explanation**

- **L44** — Require the public disconnect name similarly.
- **L45** — Close the embedded script string; the outer test resumes here.
- **L46–L52** — Launch the same Python interpreter with -I (isolate environment/user path), -S (skip site initialization), -c (execute embedded text), explicit package-root argument and cwd=/; capture results instead of displaying them.
- **L53** — Require successful child exit and show stderr only if the assertion fails.
- **L54** — Require import discovery to print no normal output.

[[#4 Package branch — file map|↑ Package file map]]

### 13.18 Package source — tests/test_vpn.py


Offline regression checks for vpn. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Functions and their purpose**

- **VPNTests.setUp**, L13–L31: Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **VPNTests.test\_valid\_saved\_session\_bypasses\_credentials\_and\_browser**, L33–L47: Fake an accepted cached session and state transition to active; require no fresh browser, correct activation cookie, connected/changed/devices results and no controller output without a callback.
- **VPNTests.test\_expired\_session\_is\_cleared\_before\_signin\_and\_new\_session\_saved**, L49–L70: Record mock call order for expiry: clear old session → authenticate → save new session → activate; require explicit Config/quiet/progress forwarding and token-free messages.
- **VPNTests.test\_already\_connected\_never\_signs\_in\_or\_activates\_again**, L72–L78: Return already activated state and require connected=True/changed=False without cache retrieval or another activation.
- **VPNTests.test\_busy\_connection\_fails\_before\_credentials**, L80–L84: Return activating state and require a busy error before loading session/credentials.
- **VPNTests.test\_missing\_profile\_is\_created**, L86–L95: Fake a missing profile, successful setup and activation; require the new UUID and the corresponding setup/activate calls.
- **VPNTests.test\_ambiguous\_profile\_never\_creates\_another**, L97–L101: Raise a nonmissing ambiguous-profile error and require connect to propagate it without calling setup\_profile.
- **VPNTests.test\_authentication\_failure\_never\_activates**, L103–L108: Make fresh authentication fail and require no activation and no saving of a nonexistent new session.
- **VPNTests.test\_failed\_activation\_is\_not\_reported\_as\_connected**, L110–L114: Make activation raise code-10 NetworkManagerError and require that failure/code to propagate instead of returning false success.
- **VPNTests.test\_disconnect\_handles\_missing\_inactive\_and\_active\_profiles**, L116–L132: Exercise missing, empty, deactivated, activated and activating states; require sensible nonconnected results, changed flags and backend down calls only when needed.


#### 13.18.1 L1–L11 · Module documentation, imports and shared definitions


```python
"""Public API state transitions with fake NetworkManager and sign-in services."""

import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from tifrvpn import vpn
from tifrvpn.errors import AuthenticationError, NetworkManagerError, ProfileNotFound
```

**Line-by-line explanation**

- **L1** — Documentation string describing this module/function or embedded program. Text inside a string is data here; embedded scripts execute only when explicitly passed to another interpreter.
- **L3** — Import contextlib: temporary output redirection and context-manager cleanup. Importing a definition is distinct from calling an operation.
- **L4** — Import io: in-memory text/byte streams for harmless example output. Importing a definition is distinct from calling an operation.
- **L5** — Import unittest: test discovery, isolated test cases and assertions. Importing a definition is distinct from calling an operation.
- **L6** — Import Mock, patch from unittest.mock for temporary function/environment replacements and recording fake calls. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L8** — Import vpn from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L9** — Import AuthenticationError, NetworkManagerError, ProfileNotFound from tifrvpn.errors for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.


#### 13.18.2 L12–L12 · VPNTests — type/state/test structure


```python
class VPNTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L12** — Define VPNTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.


#### 13.18.3 L13–L32 · VPNTests.setUp


```python
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
```

**Line-by-line explanation**

- **L13** — Define setUp(self). Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **L14** — Store the result as self.nm. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L15** — Assign 'profile-uuid' to self.nm.profile\_uuid.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L16** — Assign 'deactivated' to self.nm.state.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L17–L19** — Assign 'GENERAL.DEVICES: tun0\\nIP4.ADDRESS\[1\]: 10.0.0.2/24' to self.nm.details.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L20** — Store the result as self.keyring. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L21** — Assign None to self.keyring.load\_session.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L22** — Store the result as self.auth. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L23** — Assign 'DSID=example-session' to self.auth.authenticate.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L24–L28** — For each (name, value) in \[('nm', self.nm), ('keyring', self.keyring), ('auth', self.auth)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L29** — Store the result as patcher. Temporarily replace vpn, name for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L30** — Call patcher.start with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L31** — Register cleanup with unittest so the temporary resource or patch is restored even if a later assertion fails.


#### 13.18.4 L33–L48 · VPNTests.test_valid_saved_session_bypasses_credentials_and_browser


```python
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
```

**Line-by-line explanation**

- **L33** — Define test\_valid\_saved\_session\_bypasses\_credentials\_and\_browser(self). Fake an accepted cached session and state transition to active; require no fresh browser, correct activation cookie, connected/changed/devices results and no controller output without a callback.
- **L34** — Assign 'DSID=example-saved' to self.keyring.load\_session.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L35** — Assign True to self.auth.valid\_session.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L36** — Prepare self.nm.state.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L37** — Prepare (out, err) as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L38** — Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L39** — Store the result as result. Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L40** — Require result.connected to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L41** — Require result.changed to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L42** — Require result.devices to equal ('tun0',). If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L43** — Check that self.auth.authenticate was never invoked, proving rejection/bypass happened before that side effect.
- **L44–L46** — Check the recorded call to self.nm.activate used the specified positional/keyword arguments exactly once.
- **L47** — Require out.getvalue() + err.getvalue() to equal ''. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


#### 13.18.5 L49–L71 · VPNTests.test_expired_session_is_cleared_before_signin_and_new_session_saved


```python
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
```

**Line-by-line explanation**

- **L49** — Define test\_expired\_session\_is\_cleared\_before\_signin\_and\_new\_session\_saved(self). Record mock call order for expiry: clear old session → authenticate → save new session → activate; require explicit Config/quiet/progress forwarding and token-free messages.
- **L50** — Assign 'DSID=example-expired' to self.keyring.load\_session.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L51** — Assign False to self.auth.valid\_session.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L52** — Prepare self.nm.state.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L53** — Store the result as sequence. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L54–L57** — Attach this fake operation under a readable name so one combined mock-call history can verify cross-service ordering.
- **L58** — Prepare events as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L59** — Store the result as config. Call object with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L60** — Store the result as result. Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L61** — Require result.connected to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L62–L65** — Require \[call\[0\] for call in sequence.mock\_calls\] to equal \['clear', 'authenticate', 'save', 'activate'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L66–L68** — Check the recorded call to self.auth.authenticate used the specified positional/keyword arguments exactly once.
- **L69** — Require any(('expired' in event for event in events)) to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L70** — Require 'example-session' to be absent from '\\n'.join(events). The test inspects data/captured calls rather than trusting printed progress alone.


#### 13.18.6 L72–L79 · VPNTests.test_already_connected_never_signs_in_or_activates_again


```python
    def test_already_connected_never_signs_in_or_activates_again(self):
        self.nm.state.return_value = "activated"
        result = vpn.connect()
        self.assertTrue(result.connected)
        self.assertFalse(result.changed)
        self.keyring.load_session.assert_not_called()
        self.nm.activate.assert_not_called()
```

**Line-by-line explanation**

- **L72** — Define test\_already\_connected\_never\_signs\_in\_or\_activates\_again(self). Return already activated state and require connected=True/changed=False without cache retrieval or another activation.
- **L73** — Assign 'activated' to self.nm.state.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L74** — Store the result as result. Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L75** — Require result.connected to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L76** — Require result.changed to evaluate as false; this is an assertion about the tested behavior, not a real connection request.
- **L77** — Check that self.keyring.load\_session was never invoked, proving rejection/bypass happened before that side effect.
- **L78** — Check that self.nm.activate was never invoked, proving rejection/bypass happened before that side effect.


#### 13.18.7 L80–L85 · VPNTests.test_busy_connection_fails_before_credentials


```python
    def test_busy_connection_fails_before_credentials(self):
        self.nm.state.return_value = "activating"
        with self.assertRaisesRegex(NetworkManagerError, "wait or run tifrvpn -d"):
            vpn.connect()
        self.keyring.load_session.assert_not_called()
```

**Line-by-line explanation**

- **L80** — Define test\_busy\_connection\_fails\_before\_credentials(self). Return activating state and require a busy error before loading session/credentials.
- **L81** — Assign 'activating' to self.nm.state.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L82** — Expect the enclosed call to raise NetworkManagerError with a message matching 'wait or run tifrvpn -d'. A missing/wrong exception makes the test fail.
- **L83** — Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L84** — Check that self.keyring.load\_session was never invoked, proving rejection/bypass happened before that side effect.


#### 13.18.8 L86–L96 · VPNTests.test_missing_profile_is_created


```python
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
```

**Line-by-line explanation**

- **L86** — Define test\_missing\_profile\_is\_created(self). Fake a missing profile, successful setup and activation; require the new UUID and the corresponding setup/activate calls.
- **L87** — Prepare self.nm.profile\_uuid.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L88** — Assign 'new-uuid' to self.nm.setup\_profile.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L89** — Prepare self.nm.state.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L90** — Store the result as result. Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L91** — Require result.profile\_uuid to equal 'new-uuid'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L92** — Check the recorded call to self.nm.setup\_profile used the specified positional/keyword arguments exactly once.
- **L93–L95** — Check the recorded call to self.nm.activate used the specified positional/keyword arguments exactly once.


#### 13.18.9 L97–L102 · VPNTests.test_ambiguous_profile_never_creates_another


```python
    def test_ambiguous_profile_never_creates_another(self):
        self.nm.profile_uuid.side_effect = NetworkManagerError("expected one")
        with self.assertRaises(NetworkManagerError):
            vpn.connect()
        self.nm.setup_profile.assert_not_called()
```

**Line-by-line explanation**

- **L97** — Define test\_ambiguous\_profile\_never\_creates\_another(self). Raise a nonmissing ambiguous-profile error and require connect to propagate it without calling setup\_profile.
- **L98** — Store the result as self.nm.profile\_uuid.side\_effect. Call NetworkManagerError with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L99** — Expect the enclosed call to raise NetworkManagerError. A missing/wrong exception makes the test fail.
- **L100** — Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L101** — Check that self.nm.setup\_profile was never invoked, proving rejection/bypass happened before that side effect.


#### 13.18.10 L103–L109 · VPNTests.test_authentication_failure_never_activates


```python
    def test_authentication_failure_never_activates(self):
        self.auth.authenticate.side_effect = AuthenticationError("cancelled")
        with self.assertRaises(AuthenticationError):
            vpn.connect()
        self.nm.activate.assert_not_called()
        self.keyring.save_session.assert_not_called()
```

**Line-by-line explanation**

- **L103** — Define test\_authentication\_failure\_never\_activates(self). Make fresh authentication fail and require no activation and no saving of a nonexistent new session.
- **L104** — Store the result as self.auth.authenticate.side\_effect. Call AuthenticationError with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L105** — Expect the enclosed call to raise AuthenticationError. A missing/wrong exception makes the test fail.
- **L106** — Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L107** — Check that self.nm.activate was never invoked, proving rejection/bypass happened before that side effect.
- **L108** — Check that self.keyring.save\_session was never invoked, proving rejection/bypass happened before that side effect.


#### 13.18.11 L110–L115 · VPNTests.test_failed_activation_is_not_reported_as_connected


```python
    def test_failed_activation_is_not_reported_as_connected(self):
        self.nm.activate.side_effect = NetworkManagerError("failed", returncode=10)
        with self.assertRaises(NetworkManagerError) as result:
            vpn.connect()
        self.assertEqual(result.exception.returncode, 10)
```

**Line-by-line explanation**

- **L110** — Define test\_failed\_activation\_is\_not\_reported\_as\_connected(self). Make activation raise code-10 NetworkManagerError and require that failure/code to propagate instead of returning false success.
- **L111** — Store the result as self.nm.activate.side\_effect. Call NetworkManagerError with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L112** — Expect the enclosed call to raise NetworkManagerError. A missing/wrong exception makes the test fail.
- **L113** — Call vpn.connect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L114** — Require result.exception.returncode to equal 10. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


#### 13.18.12 L116–L132 · VPNTests.test_disconnect_handles_missing_inactive_and_active_profiles


```python
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
```

**Line-by-line explanation**

- **L116** — Define test\_disconnect\_handles\_missing\_inactive\_and\_active\_profiles(self). Exercise missing, empty, deactivated, activated and activating states; require sensible nonconnected results, changed flags and backend down calls only when needed.
- **L117** — Store the result as self.nm.profile\_uuid.side\_effect. Call ProfileNotFound with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L118** — Require vpn.disconnect().state to equal 'not-configured'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L119** — Assign None to self.nm.profile\_uuid.side\_effect. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L120–L125** — For each (state, changed) in \[('', False), ('deactivated', False), ('activated', True), ('activating', True)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L126** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run.
- **L127** — Assign state to self.nm.state.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L128** — Clear previous call history before the next scenario so assertions describe only this iteration.
- **L129** — Store the result as result. Call vpn.disconnect with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L130** — Require result.connected to evaluate as false; this is an assertion about the tested behavior, not a real connection request.
- **L131** — Require result.changed to equal changed. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L132** — Require self.nm.deactivate.called to equal changed. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


[[#4 Package branch — file map|↑ Package file map]]

### 13.19 Package source — tests/test_cli.py

Offline regression checks for cli. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Functions and their purpose**

- **CLITests.run_cli**, L15–L19: Capture both CLI output streams while calling cli.main with explicit arguments, then return status/stdout/stderr for assertions.
- **CLITests.test_option_order_and_forwarding**, L21–L45: Exercise accepted connect/quiet orders and status/disconnect dispatch; verify the correct library function receives the boolean flag and CLI callback.
- **CLITests.test_invalid_options_fail_before_any_operations**, L47–L62: Try incompatible flags, duplicate actions and unknown options; require status 2, stderr explanation, no stdout and no connect operation.
- **CLITests.test_help_needs_no_networkmanager**, L64–L68: Check both help spellings using a backend that would fail if called; require exact help output and success without querying connection state.
- **CLITests.test_toggle_preserves_transitional_state_behavior**, L70–L87: Fake active/activating/deactivated/empty states and require no-argument toggle to preserve main's disconnect-versus-connect decisions.
- **CLITests.test_status_exit_codes_and_details**, L89–L104: Convert structured not-configured, inactive, transitional and active statuses to the appropriate CLI code; active output must include returned details.
- **CLITests.test_failure_exit_code_is_preserved**, L106–L110: Raise a backend NetworkManagerError with returncode=10 and require CLI code 10 with the safe expected stderr message.
- **CLITests.test_connect_notification_only_when_tunnel_was_started**, L112–L123: Vary VPNStatus.changed and require a successful connect notification only when this operation actually started the tunnel.
- **CLITests.test_otp_does_not_dump_unexpected_error_details**, L125–L133: Raise an OS error containing an invented password string during config loading; require a generic OTP failure that omits that string.

#### 13.19.1 L1–L13 · Module setup and definitions

```python
"""Command dispatch and output checks, without accessing desktop services."""

import contextlib
import io
import unittest
from unittest.mock import patch

from tifrvpn import cli
from tifrvpn import networkmanager as nm
from tifrvpn.errors import NetworkManagerError
from tifrvpn.vpn import VPNStatus


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import contextlib at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import io at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import unittest at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Bind patch from unittest.mock at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Bind cli from tifrvpn at module scope. These names are then available to the functions below without a function-local import.
- **L9** — Bind networkmanager as nm from tifrvpn at module scope. These names are then available to the functions below without a function-local import.
- **L10** — Bind NetworkManagerError from tifrvpn.errors at module scope. These names are then available to the functions below without a function-local import.
- **L11** — Bind VPNStatus from tifrvpn.vpn at module scope. These names are then available to the functions below without a function-local import.

#### 13.19.2 L14–L14 · Module setup and definitions

```python
class CLITests(unittest.TestCase):
```

**Line-by-line explanation**

- **L14** — Define CLITests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.

#### 13.19.3 L15–L20 · CLITests.run_cli

```python
    def run_cli(self, arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(arguments)
        return code, stdout.getvalue(), stderr.getvalue()

```

**Line-by-line explanation**

- **L15** — Define run\_cli(self, arguments). Capture both CLI output streams while calling cli.main with explicit arguments, then return status/stdout/stderr for assertions.
- **L16** — Prepare (stdout, stderr) as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L17** — Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L18** — Store the result as code. Call cli.main with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L19** — Return (code, stdout.getvalue(), stderr.getvalue()) from this function. A library return is ordinary data; CLI adapters separately interpret integer exit results.

#### 13.19.4 L21–L46 · CLITests.test_option_order_and_forwarding

```python
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

```

**Line-by-line explanation**

- **L21** — Define test\_option\_order\_and\_forwarding(self). Exercise accepted connect/quiet orders and status/disconnect dispatch; verify the correct library function receives the boolean flag and CLI callback.
- **L22–L27** — For each (args, quiet) in \[(\['-c', '--quiet'\], True), (\['--quiet', '-c'\], True), (\['--quiet'\], True), (\['-c'\], False)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L28–L33** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace cli.vpn, 'connect' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L34** — Require self.run\_cli(args)\[0\] to equal 0. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L35** — Check the recorded call to connect used the specified positional/keyword arguments exactly once.
- **L36–L38** — Temporarily replace cli.vpn, 'disconnect' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L39** — Require self.run\_cli(\['-d'\])\[0\] to equal 0. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L40** — Require exactly one call to disconnect, detecting accidental repeated operations.
- **L41–L43** — Temporarily replace cli.vpn, 'status' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L44** — Require self.run\_cli(\['-s'\])\[0\] to equal 0. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L45** — Require exactly one call to status, detecting accidental repeated operations.

#### 13.19.5 L47–L63 · CLITests.test_invalid_options_fail_before_any_operations

```python
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

```

**Line-by-line explanation**

- **L47** — Define test\_invalid\_options\_fail\_before\_any\_operations(self). Try incompatible flags, duplicate actions and unknown options; require status 2, stderr explanation, no stdout and no connect operation.
- **L48–L56** — For each args in (\['--quiet', '-d'\], \['-s', '--quiet'\], \['--quiet', '--setup'\], \['-c', '-s'\], \['--unknown'\], \['-h', '--quiet'\], \['-c', '-c'\]), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L57** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace cli.vpn, 'connect' for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L58** — Store the result as (code, out, err). Call self.run\_cli with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L59** — Require code to equal 2. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L60** — Require out to equal ''. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L61** — Require err to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L62** — Check that connect was never invoked, proving rejection/bypass happened before that side effect.

#### 13.19.6 L64–L69 · CLITests.test_help_needs_no_networkmanager

```python
    def test_help_needs_no_networkmanager(self):
        with patch.object(cli.vpn, "status", side_effect=AssertionError("called")):
            for args in (["--help"], ["-h"]):
                code, out, err = self.run_cli(args)
                self.assertEqual((code, out, err), (0, cli.HELP + "\n", ""))

```

**Line-by-line explanation**

- **L64** — Define test\_help\_needs\_no\_networkmanager(self). Check both help spellings using a backend that would fail if called; require exact help output and success without querying connection state.
- **L65** — Temporarily replace cli.vpn, 'status' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit.
- **L66** — For each args in (\['--help'\], \['-h'\]), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L67** — Store the result as (code, out, err). Call self.run\_cli with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L68** — Require (code, out, err) to equal (0, cli.HELP + '\\n', ''). If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.19.7 L70–L88 · CLITests.test_toggle_preserves_transitional_state_behavior

```python
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

```

**Line-by-line explanation**

- **L70** — Define test\_toggle\_preserves\_transitional\_state\_behavior(self). Fake active/activating/deactivated/empty states and require no-argument toggle to preserve main's disconnect-versus-connect decisions.
- **L71–L76** — For each (state, connects) in \[('activated', False), ('activating', False), ('deactivated', True), ('', True)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L77–L84** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace nm, 'require\_available' for this context so the real external operation/environment does not run. The patch is restored on block exit. Temporarily replace nm, 'profile\_uuid' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace nm, 'state' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace cli, '\_connect' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace cli, '\_disconnect' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L85** — Require self.run\_cli(\[\])\[0\] to equal 0. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L86** — Require connect.called to equal connects. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L87** — Require disconnect.called to equal not connects. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.19.8 L89–L105 · CLITests.test_status_exit_codes_and_details

```python
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

```

**Line-by-line explanation**

- **L89** — Define test\_status\_exit\_codes\_and\_details(self). Convert structured not-configured, inactive, transitional and active statuses to the appropriate CLI code; active output must include returned details.
- **L90–L95** — For each (result, expected) in \[(VPNStatus('not-configured'), 1), (VPNStatus('deactivated'), 1), (VPNStatus('activating'), 1), (VPNStatus('activated', details='GENERAL.DEVICES: tun0'), 0)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L96–L99** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace cli.vpn, 'status' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L100** — Store the result as (code, out, err). Call self.run\_cli with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L101** — Require code to equal expected. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L102** — Require err to equal ''. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L103** — Only run this branch when result.connected is true. The following indented statements implement that condition’s case; later else/elif handles alternatives.
- **L104** — Require result.details to be present in out. The test inspects data/captured calls rather than trusting printed progress alone.

#### 13.19.9 L106–L111 · CLITests.test_failure_exit_code_is_preserved

```python
    def test_failure_exit_code_is_preserved(self):
        with patch.object(
            cli.vpn, "connect", side_effect=NetworkManagerError("failed", returncode=10)
        ):
            self.assertEqual(self.run_cli(["-c"]), (10, "", "tifr VPN: failed\n"))

```

**Line-by-line explanation**

- **L106** — Define test\_failure\_exit\_code\_is\_preserved(self). Raise a backend NetworkManagerError with returncode=10 and require CLI code 10 with the safe expected stderr message.
- **L107–L109** — Temporarily replace cli.vpn, 'connect' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit.
- **L110** — Require self.run\_cli(\['-c'\]) to equal (10, '', 'tifr VPN: failed\\n'). If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.19.10 L112–L124 · CLITests.test_connect_notification_only_when_tunnel_was_started

```python
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

```

**Line-by-line explanation**

- **L112** — Check that a successful newly established connection sends a desktop notification, while an already connected result does not send a duplicate.
- **L113** — For each changed in (False, True), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L114–L121** — Temporarily replace cli.vpn, 'connect' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace cli, '\_notify' for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L122** — Require self.run\_cli(\['-c'\])\[0\] to equal 0. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L123** — Require notify.called to equal changed. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.19.11 L125–L133 · CLITests.test_otp_does_not_dump_unexpected_error_details

```python
    def test_otp_does_not_dump_unexpected_error_details(self):
        with (
            patch.object(
                cli, "load_config", side_effect=OSError("example-master-password")
            ),
            contextlib.redirect_stderr(io.StringIO()) as output,
        ):
            self.assertEqual(cli.otp_main([]), 1)
        self.assertNotIn("example-master-password", output.getvalue())
```

**Line-by-line explanation**

- **L125** — Define test\_otp\_does\_not\_dump\_unexpected\_error\_details(self). Raise an OS error containing an invented password string during config loading; require a generic OTP failure that omits that string.
- **L126–L131** — Temporarily replace cli, 'load\_config' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L132** — Require cli.otp\_main(\[\]) to equal 1. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L133** — Require 'example-master-password' to be absent from output.getvalue(). The test inspects data/captured calls rather than trusting printed progress alone.

[[#4 Package branch — file map|↑ Package file map]]

### 13.20 Package source — tests/test_config.py


Offline regression checks for config. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Relation to main:** [[TIFR Vpn TUI#7.7 tests/test_setup.py|tests/test_setup.py]] — Configuration, parsing and TOTP checks are retained while copy-install tests are removed/replaced.

**Functions and their purpose**

- **ConfigurationTests.setUp**, L19–L30: Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **ConfigurationTests.configure**, L32–L35: Write only the supplied invented JSON configuration under the temporary test HOME.
- **ConfigurationTests.test\_default\_and\_configured\_paths\_and\_environment\_override**, L37–L55: Use a temporary HOME and placeholder vault to verify default paths, ~ expansion, JSON settings and an environment entry override taking precedence.
- **ConfigurationTests.test\_bad\_config\_is\_rejected**, L57–L71: Supply invalid object shape, nonstring values, blank entry, unknown key and relative database path; each must produce a readable configuration failure.
- **ConfigurationTests.test\_login\_parser\_keeps\_fields\_out\_of\_output**, L73–L89: Mock KeePass output with invented credentials; verify the parser returns fields, prints nothing, requests protected values and excludes the master password from argv.
- **ConfigurationTests.test\_missing\_login\_fields\_are\_rejected**, L91–L98: Mock an entry with an empty account password and require a readable missing-Username/Password RuntimeError-family failure.
- **ConfigurationTests.test\_totp\_against\_public\_rfc6238\_vector**, L100–L108: At fixed timestamp 59, calculate the public SHA1/8-digit RFC vector and require 94287082; this tests against an independent expected answer.


#### 13.20.1 L1–L17 · Module documentation, imports and shared definitions


```python
"""Configuration, credential parsing and TOTP checks without personal data."""

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tifrvpn import credentials as OTP
from tifrvpn import totp as QR
from tifrvpn.config import load_config
```

**Line-by-line explanation**

- **L1** — Documentation string describing this module/function or embedded program. Text inside a string is data here; embedded scripts execute only when explicitly passed to another interpreter.
- **L3** — Import contextlib: temporary output redirection and context-manager cleanup. Importing a definition is distinct from calling an operation.
- **L4** — Import io: in-memory text/byte streams for harmless example output. Importing a definition is distinct from calling an operation.
- **L5** — Import json: structured settings/cookie serialization and decoding. Importing a definition is distinct from calling an operation.
- **L6** — Import os: environment variables and low-level operating-system/file-descriptor operations. Importing a definition is distinct from calling an operation.
- **L7** — Import subprocess: direct child-program execution, captured output and explicit failure results. Importing a definition is distinct from calling an operation.
- **L8** — Import tempfile: temporary files/directories that isolate checks from personal configuration. Importing a definition is distinct from calling an operation.
- **L9** — Import unittest: test discovery, isolated test cases and assertions. Importing a definition is distinct from calling an operation.
- **L10** — Import Path from pathlib for path construction and normalization without shell interpolation. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L11** — Import patch from unittest.mock for temporary function/environment replacements and recording fake calls. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L13** — Import credentials as OTP from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L14** — Import totp as QR from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L15** — Import load\_config from tifrvpn.config for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.


#### 13.20.2 L18–L18 · ConfigurationTests — type/state/test structure


```python
class ConfigurationTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L18** — Define ConfigurationTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.


#### 13.20.3 L19–L31 · ConfigurationTests.setUp


```python
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifr setup ")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.home))
        for name in (
            "XDG_CONFIG_HOME",
            "TIFR_KEEPASS_DATABASE",
            "TIFR_KEEPASS_ENTRY",
            "TIFR_KEEPASS_PASSWORD_FILE",
        ):
            self.environment.pop(name, None)
```

**Line-by-line explanation**

- **L19** — Define setUp(self). Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **L20** — Store the result as self.temporary. Create a disposable isolated directory, with a space-containing prefix to exercise correct path/argument handling.
- **L21** — Register cleanup with unittest so the temporary resource or patch is restored even if a later assertion fails.
- **L22** — Store the result as self.home. Call Path with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L23** — Store the result as self.environment. Call dict with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L24–L29** — For each name in ('XDG\_CONFIG\_HOME', 'TIFR\_KEEPASS\_DATABASE', 'TIFR\_KEEPASS\_ENTRY', 'TIFR\_KEEPASS\_PASSWORD\_FILE'), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L30** — Call self.environment.pop with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.20.4 L32–L36 · ConfigurationTests.configure


```python
    def configure(self, settings):
        config = self.home / ".config/tifr-vpn/config.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(settings))
```

**Line-by-line explanation**

- **L32** — Define configure(self, settings). Write only the supplied invented JSON configuration under the temporary test HOME.
- **L33** — Assign self.home / '.config/tifr-vpn/config.json' to config. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L34** — Call config.parent.mkdir with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L35** — Call config.write\_text with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.20.5 L37–L56 · ConfigurationTests.test_default_and_configured_paths_and_environment_override


```python
    def test_default_and_configured_paths_and_environment_override(self):
        database = self.home / "Documents/KeePass/Passwords.kdbx"
        database.parent.mkdir(parents=True)
        database.touch()
        with patch.dict(os.environ, self.environment, clear=True):
            self.assertEqual(load_config().database, database)
            self.configure(
                {
                    "database": str(database),
                    "entry": "VPN/TIFR",
                    "password_file": "~/private/master.gpg",
                }
            )
            self.assertEqual(
                load_config().password_file, self.home / "private/master.gpg"
            )
            self.assertEqual(load_config().entry, "VPN/TIFR")
            with patch.dict(os.environ, {"TIFR_KEEPASS_ENTRY": "Other/TIFR"}):
                self.assertEqual(load_config().entry, "Other/TIFR")
```

**Line-by-line explanation**

- **L37** — Define test\_default\_and\_configured\_paths\_and\_environment\_override(self). Use a temporary HOME and placeholder vault to verify default paths, ~ expansion, JSON settings and an environment entry override taking precedence.
- **L38** — Assign self.home / 'Documents/KeePass/Passwords.kdbx' to database. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L39** — Call database.parent.mkdir with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L40** — Call database.touch with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L41** — Temporarily replace os.environ, self.environment for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L42** — Require load\_config().database to equal database. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L43–L49** — Call self.configure with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L50–L52** — Require load\_config().password\_file to equal self.home / 'private/master.gpg'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L53** — Require load\_config().entry to equal 'VPN/TIFR'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L54** — Temporarily replace os.environ, {'TIFR\_KEEPASS\_ENTRY': 'Other/TIFR'} for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L55** — Require load\_config().entry to equal 'Other/TIFR'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


#### 13.20.6 L57–L72 · ConfigurationTests.test_bad_config_is_rejected


```python
    def test_bad_config_is_rejected(self):
        for settings in (
            [],
            {"database": 42},
            {"entry": ""},
            {"unknown": "value"},
            {"database": "relative.kdbx"},
        ):
            with (
                self.subTest(settings=settings),
                patch.dict(os.environ, self.environment, clear=True),
            ):
                self.configure(settings)
                with self.assertRaises(RuntimeError):
                    load_config()
```

**Line-by-line explanation**

- **L57** — Define test\_bad\_config\_is\_rejected(self). Supply invalid object shape, nonstring values, blank entry, unknown key and relative database path; each must produce a readable configuration failure.
- **L58–L64** — For each settings in (\[\], {'database': 42}, {'entry': ''}, {'unknown': 'value'}, {'database': 'relative.kdbx'}), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L65–L68** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace os.environ, self.environment for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L69** — Call self.configure with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L70** — Expect the enclosed call to raise RuntimeError. A missing/wrong exception makes the test fail.
- **L71** — Call load\_config with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.20.7 L73–L90 · ConfigurationTests.test_login_parser_keeps_fields_out_of_output


```python
    def test_login_parser_keeps_fields_out_of_output(self):
        result = subprocess.CompletedProcess(
            [], 0, "example-user\nexample-password\n123456\n", ""
        )
        output = io.StringIO()
        with (
            patch("shutil.which", return_value="/usr/bin/keepassxc-cli"),
            patch("subprocess.run", return_value=result) as run,
            contextlib.redirect_stdout(output),
        ):
            login = OTP.read_login("example-master", Path("example.kdbx"), "TIFR")
        self.assertEqual(
            login, {"username": "example-user", "password": "example-password"}
        )
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn("example-master", run.call_args.args[0])
        self.assertIn("--show-protected", run.call_args.args[0])
```

**Line-by-line explanation**

- **L73** — Define test\_login\_parser\_keeps\_fields\_out\_of\_output(self). Mock KeePass output with invented credentials; verify the parser returns fields, prints nothing, requests protected values and excludes the master password from argv.
- **L74–L76** — Store the result as result. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L77** — Store the result as output. Create a file-like in-memory text buffer so the test can inspect output without printing example credentials to the real terminal.
- **L78–L82** — Temporarily replace 'shutil.which' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace 'subprocess.run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L83** — Store the result as login. Call OTP.read\_login with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L84–L86** — Require login to equal {'username': 'example-user', 'password': 'example-password'}. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L87** — Require output.getvalue() to equal ''. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L88** — Require 'example-master' to be absent from run.call\_args.args\[0\]. The test inspects data/captured calls rather than trusting printed progress alone.
- **L89** — Require '--show-protected' to be present in run.call\_args.args\[0\]. The test inspects data/captured calls rather than trusting printed progress alone.


#### 13.20.8 L91–L99 · ConfigurationTests.test_missing_login_fields_are_rejected


```python
    def test_missing_login_fields_are_rejected(self):
        result = subprocess.CompletedProcess([], 0, "example-user\n\n123456\n", "")
        with (
            patch("shutil.which", return_value="/usr/bin/keepassxc-cli"),
            patch("subprocess.run", return_value=result),
            self.assertRaisesRegex(RuntimeError, "Username and Password"),
        ):
            OTP.read_login("example-master", Path("example.kdbx"), "TIFR")
```

**Line-by-line explanation**

- **L91** — Define test\_missing\_login\_fields\_are\_rejected(self). Mock an entry with an empty account password and require a readable missing-Username/Password RuntimeError-family failure.
- **L92** — Store the result as result. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L93–L97** — Temporarily replace 'shutil.which' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace 'subprocess.run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise RuntimeError with a message matching 'Username and Password'. A missing/wrong exception makes the test fail.
- **L98** — Call OTP.read\_login with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.20.9 L100–L112 · ConfigurationTests.test_totp_against_public_rfc6238_vector


```python
    def test_totp_against_public_rfc6238_vector(self):
        # Public RFC test key; never use it for a real account.
        account = {
            "secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "period": 30,
            "algorithm": "SHA1",
            "digits": 8,
        }
        self.assertEqual(QR.current_code(account, timestamp=59), "94287082")


if __name__ == "__main__":
    unittest.main()
```

**Line-by-line explanation**

- **L100** — Define test\_totp\_against\_public\_rfc6238\_vector(self). At fixed timestamp 59, calculate the public SHA1/8-digit RFC vector and require 94287082; this tests against an independent expected answer.
- **L101** — Comment for readers: Public RFC test key; never use it for a real account.. The comment documents intent or linter policy and is not executed.
- **L102–L107** — Prepare account as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L108** — Require QR.current\_code(account, timestamp=59) to equal '94287082'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L111** — Only run this branch when \_\_name\_\_ == '\_\_main\_\_' is true. The following indented statements implement that condition’s case; later else/elif handles alternatives.
- **L112** — Call unittest.main with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


[[#4 Package branch — file map|↑ Package file map]]

### 13.21 Package source — tests/test_auth.py


Offline regression checks for auth. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Functions and their purpose**

- **AuthTests.test\_custom\_configuration\_reaches\_worker\_without\_changing\_parent**, L17–L39: Supply explicit Config and fake worker success; verify child-only paths/entry arrive, the parent entry stays unchanged, module invocation uses -m, and the caller's existing PYTHONPATH is preserved rather than prepended to.
- **AuthTests.test\_malformed\_worker\_output\_never\_becomes\_a\_session**, L41–L52: Try empty, unprefixed, multiline and NUL-bearing worker stdout; each must raise AuthenticationError before a token can be used.
- **AuthTests.test\_failure\_does\_not\_expose\_worker\_stdout**, L54–L66: Simulate failed worker execution with sensitive-looking stdout and require the raised error to omit that token.
- **AuthTests.test\_session\_validation\_statuses**, L68–L93: Fake portal HTTP responses/redirects; accept authenticated home access, reject redirects to login/other hosts and unauthorized/forbidden statuses without contacting a gateway.


#### 13.21.1 L1–L15 · Module documentation, imports and shared definitions


```python
"""Authentication protocol checks without a real gateway or browser."""

import io
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from tifrvpn import auth
from tifrvpn.config import Config
from tifrvpn.errors import AuthenticationError
```

**Line-by-line explanation**

- **L1** — Documentation string describing this module/function or embedded program. Text inside a string is data here; embedded scripts execute only when explicitly passed to another interpreter.
- **L3** — Import io: in-memory text/byte streams for harmless example output. Importing a definition is distinct from calling an operation.
- **L4** — Import os: environment variables and low-level operating-system/file-descriptor operations. Importing a definition is distinct from calling an operation.
- **L5** — Import subprocess: direct child-program execution, captured output and explicit failure results. Importing a definition is distinct from calling an operation.
- **L6** — Import unittest: test discovery, isolated test cases and assertions. Importing a definition is distinct from calling an operation.
- **L7** — Import Path from pathlib for path construction and normalization without shell interpolation. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L8** — Import Mock, patch from unittest.mock for temporary function/environment replacements and recording fake calls. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L9** — Import HTTPError from urllib.error for HTTP response failures used to distinguish expired sessions from other errors. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L11** — Import auth from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L12** — Import Config from tifrvpn.config for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L13** — Import AuthenticationError from tifrvpn.errors for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.


#### 13.21.2 L16–L16 · AuthTests — type/state/test structure


```python
class AuthTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L16** — Define AuthTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.


#### 13.21.3 L17–L40 · AuthTests.test_custom_configuration_reaches_worker_without_changing_parent


```python
    def test_custom_configuration_reaches_worker_without_changing_parent(self):
        config = Config(
            Path("/example/custom.kdbx"), Path("/example/master.gpg"), "VPN/custom"
        )
        with (
            patch.object(
                auth.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0, "DSID=example"),
            ) as run,
            patch.dict(
                os.environ,
                {"TIFR_KEEPASS_ENTRY": "original", "PYTHONPATH": "/example/path"},
            ),
        ):
            self.assertEqual(auth.authenticate(config=config), "DSID=example")
            self.assertEqual(os.environ["TIFR_KEEPASS_ENTRY"], "original")
        command = run.call_args.args[0]
        self.assertEqual(command[1:], ["-m", "tifrvpn._sso_worker"])
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["TIFR_KEEPASS_ENTRY"], "VPN/custom")
        self.assertEqual(env["TIFR_KEEPASS_DATABASE"], "/example/custom.kdbx")
        self.assertEqual(env["PYTHONPATH"], "/example/path")
```

**Line-by-line explanation**

- **L17** — Define test\_custom\_configuration\_reaches\_worker\_without\_changing\_parent(self). Supply explicit Config and fake worker success; verify child-only paths/entry arrive, the parent entry stays unchanged, module invocation uses -m, and the caller's existing PYTHONPATH is preserved rather than prepended to.
- **L18–L20** — Store the result as config. Call Config with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L21–L31** — Temporarily replace auth.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace os.environ, {'TIFR\_KEEPASS\_ENTRY': 'original', 'PYTHONPATH': '/example/path'} for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L32** — Require auth.authenticate(config=config) to equal 'DSID=example'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L33** — Require os.environ\['TIFR\_KEEPASS\_ENTRY'\] to equal 'original'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L34** — Assign run.call\_args.args\[0\] to command. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L35** — Require command\[1:\] to equal \['-m', 'tifrvpn.\_sso\_worker'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L36** — Assign run.call\_args.kwargs\['env'\] to env. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L37** — Require env\['TIFR\_KEEPASS\_ENTRY'\] to equal 'VPN/custom'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L38** — Require env\['TIFR\_KEEPASS\_DATABASE'\] to equal '/example/custom.kdbx'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L39** — Require env\['PYTHONPATH'\] to equal '/example/path'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


#### 13.21.4 L41–L53 · AuthTests.test_malformed_worker_output_never_becomes_a_session


```python
    def test_malformed_worker_output_never_becomes_a_session(self):
        for value in ("", "example", "DSID=example\nother", "DSID=example\0"):
            with (
                self.subTest(value=value),
                patch.object(
                    auth.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, value),
                ),
                self.assertRaisesRegex(AuthenticationError, "Invalid SSO session"),
            ):
                auth.authenticate()
```

**Line-by-line explanation**

- **L41** — Define test\_malformed\_worker\_output\_never\_becomes\_a\_session(self). Try empty, unprefixed, multiline and NUL-bearing worker stdout; each must raise AuthenticationError before a token can be used.
- **L42** — For each value in ('', 'example', 'DSID=example\\nother', 'DSID=example\\x00'), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L43–L51** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace auth.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise AuthenticationError with a message matching 'Invalid SSO session'. A missing/wrong exception makes the test fail.
- **L52** — Call auth.authenticate with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.21.5 L54–L67 · AuthTests.test_failure_does_not_expose_worker_stdout


```python
    def test_failure_does_not_expose_worker_stdout(self):
        with (
            patch.object(
                auth.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 1, "DSID=example-sensitive"
                ),
            ),
            self.assertRaises(AuthenticationError) as result,
        ):
            auth.authenticate()
        self.assertNotIn("example-sensitive", str(result.exception))
```

**Line-by-line explanation**

- **L54** — Define test\_failure\_does\_not\_expose\_worker\_stdout(self). Simulate failed worker execution with sensitive-looking stdout and require the raised error to omit that token.
- **L55–L64** — Temporarily replace auth.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise AuthenticationError. A missing/wrong exception makes the test fail.
- **L65** — Call auth.authenticate with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L66** — Require 'example-sensitive' to be absent from str(result.exception). The test inspects data/captured calls rather than trusting printed progress alone.


#### 13.21.6 L68–L93 · AuthTests.test_session_validation_statuses


```python
    def test_session_validation_statuses(self):
        for code, location, expected in [
            (302, "/dana/home/welcome.cgi", True),
            (302, "https://sso.tifr.res.in/login", False),
            (302, "/login", False),
            (401, "", False),
            (403, "", False),
        ]:
            with self.subTest(code=code, location=location):
                opener = Mock()
                error = HTTPError(
                    "https://example",
                    code,
                    "test",
                    {"Location": location},
                    io.BytesIO(),
                )
                self.addCleanup(error.close)
                opener.open.side_effect = error
                with patch.object(auth, "build_opener", return_value=opener):
                    self.assertEqual(auth.valid_session("DSID=example"), expected)
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=Mock(status=200))
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(auth, "build_opener", return_value=opener):
            self.assertTrue(auth.valid_session("DSID=example"))
```

**Line-by-line explanation**

- **L68** — Define test\_session\_validation\_statuses(self). Fake portal HTTP responses/redirects; accept authenticated home access, reject redirects to login/other hosts and unauthorized/forbidden statuses without contacting a gateway.
- **L69–L75** — For each (code, location, expected) in \[(302, '/dana/home/welcome.cgi', True), (302, 'https://sso.tifr.res.in/login', False), (302, '/login', False), (401, '', False), (403, '', False)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L76** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run.
- **L77** — Store the result as opener. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L78–L84** — Store the result as error. Call HTTPError with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L85** — Register cleanup with unittest so the temporary resource or patch is restored even if a later assertion fails.
- **L86** — Assign error to opener.open.side\_effect. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L87** — Temporarily replace auth, 'build\_opener' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L88** — Require auth.valid\_session('DSID=example') to equal expected. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L89** — Store the result as opener. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L90** — Store the result as opener.open.return\_value.\_\_enter\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L91** — Store the result as opener.open.return\_value.\_\_exit\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L92** — Temporarily replace auth, 'build\_opener' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit.
- **L93** — Require auth.valid\_session('DSID=example') to evaluate as true; this is an assertion about the tested behavior, not a real connection request.


[[#4 Package branch — file map|↑ Package file map]]

### 13.22 Package source — tests/test_keyring.py

Secret Service adapter tests replace keyring.Secret directly because the from-import is now executed before individual test setup. The mock records calls without contacting a desktop keyring.

**Functions and their purpose**

- **KeyringTests.setUp**, L14–L18: Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **KeyringTests.test_load_and_store_use_the_existing_schema_and_server**, L20–L43: Replace GI/libsecret with fakes and require the same schema/server/session attributes as main, preserving cache compatibility without accessing a real keyring.
- **KeyringTests.test_browser_state_uses_a_separate_key**, L45–L55: Verify browser-state lookup/storage uses kind=browser independently of the direct session-cookie identity.
- **KeyringTests.test_forgetting_clears_both_kinds**, L57–L65: Require full remembered-state clearing to request session and browser deletion in order.
- **KeyringTests.test_backend_errors_do_not_expose_secret_values**, L67–L77: Make the fake keyring throw an exception containing a sample token; require silent ordinary streams and one safe callback warning excluding that token.
- **KeyringTests.test_clear_failure_is_reported_after_trying_both_kinds**, L79–L86: Fail the first fake keyring clear and succeed the second; require AuthenticationError only after both deletion attempts.

#### 13.22.1 L1–L12 · Module setup and definitions

```python
"""Exercise Secret Service adapters without accessing a real desktop keyring."""

import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from tifrvpn import keyring
from tifrvpn.config import URL
from tifrvpn.errors import AuthenticationError


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import contextlib at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import io at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import unittest at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Bind Mock, patch from unittest.mock at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Bind keyring from tifrvpn at module scope. These names are then available to the functions below without a function-local import.
- **L9** — Bind URL from tifrvpn.config at module scope. These names are then available to the functions below without a function-local import.
- **L10** — Bind AuthenticationError from tifrvpn.errors at module scope. These names are then available to the functions below without a function-local import.

#### 13.22.2 L13–L13 · Module setup and definitions

```python
class KeyringTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L13** — Define KeyringTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.

#### 13.22.3 L14–L19 · KeyringTests.setUp

```python
    def setUp(self):
        self.secret = Mock()
        patcher = patch.object(keyring, "Secret", self.secret)
        patcher.start()
        self.addCleanup(patcher.stop)

```

**Line-by-line explanation**

- **L14** — Define setUp(self). Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **L15** — Store the result as self.secret. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L16** — Replace the Secret name already bound inside keyring.py with this test mock. Replacing sys.modules now would not change the earlier from-import binding.
- **L17** — Call patcher.start with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L18** — Register cleanup with unittest so the temporary resource or patch is restored even if a later assertion fails.

#### 13.22.4 L20–L44 · KeyringTests.test_load_and_store_use_the_existing_schema_and_server

```python
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

```

**Line-by-line explanation**

- **L20** — Define test\_load\_and\_store\_use\_the\_existing\_schema\_and\_server(self). Replace GI/libsecret with fakes and require the same schema/server/session attributes as main, preserving cache compatibility without accessing a real keyring.
- **L21** — Assign 'DSID=example' to self.secret.password\_lookup\_sync.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L22** — Require keyring.load\_session() to equal 'DSID=example'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L23** — Assign self.secret.Schema.new.return\_value to schema. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L24–L31** — Check the recorded call to self.secret.Schema.new used the specified positional/keyword arguments.
- **L32–L34** — Check the recorded call to self.secret.password\_lookup\_sync used the specified positional/keyword arguments exactly once.
- **L35** — Call keyring.save\_session with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L36–L43** — Check the recorded call to self.secret.password\_store\_sync used the specified positional/keyword arguments exactly once.

#### 13.22.5 L45–L56 · KeyringTests.test_browser_state_uses_a_separate_key

```python
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

```

**Line-by-line explanation**

- **L45** — Define test\_browser\_state\_uses\_a\_separate\_key(self). Verify browser-state lookup/storage uses kind=browser independently of the direct session-cookie identity.
- **L46** — Call keyring.load\_browser\_state with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L47–L50** — Require self.secret.password\_lookup\_sync.call\_args.args\[1\] to equal {'server': URL, 'kind': 'browser'}. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L51** — Call keyring.save\_browser\_state with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L52–L55** — Require self.secret.password\_store\_sync.call\_args.args\[1\] to equal {'server': URL, 'kind': 'browser'}. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.22.6 L57–L66 · KeyringTests.test_forgetting_clears_both_kinds

```python
    def test_forgetting_clears_both_kinds(self):
        keyring.clear_saved_login()
        self.assertEqual(
            [
                call.args[1]["kind"]
                for call in self.secret.password_clear_sync.call_args_list
            ],
            ["session", "browser"],
        )

```

**Line-by-line explanation**

- **L57** — Define test\_forgetting\_clears\_both\_kinds(self). Require full remembered-state clearing to request session and browser deletion in order.
- **L58** — Call keyring.clear\_saved\_login with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L59–L65** — Require \[call.args\[1\]\['kind'\] for call in self.secret.password\_clear\_sync.call\_args\_list\] to equal \['session', 'browser'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.22.7 L67–L78 · KeyringTests.test_backend_errors_do_not_expose_secret_values

```python
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

```

**Line-by-line explanation**

- **L67** — Define test\_backend\_errors\_do\_not\_expose\_secret\_values(self). Make the fake keyring throw an exception containing a sample token; require silent ordinary streams and one safe callback warning excluding that token.
- **L68–L70** — Store the result as self.secret.password\_lookup\_sync.side\_effect. Call RuntimeError with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L71** — Prepare events as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L72** — Store the result as output. Create a file-like in-memory text buffer so the test can inspect output without printing example credentials to the real terminal.
- **L73** — Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L74** — Require keyring.load\_session(on\_progress=events.append) to be None, the explicit no-value/failure-or-absent result checked by this test.
- **L75** — Require output.getvalue() to equal ''. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L76** — Require len(events) to equal 1. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L77** — Require 'example-sensitive' to be absent from events\[0\]. The test inspects data/captured calls rather than trusting printed progress alone.

#### 13.22.8 L79–L86 · KeyringTests.test_clear_failure_is_reported_after_trying_both_kinds

```python
    def test_clear_failure_is_reported_after_trying_both_kinds(self):
        self.secret.password_clear_sync.side_effect = [
            RuntimeError("unavailable"),
            True,
        ]
        with self.assertRaises(AuthenticationError):
            keyring.clear_saved_login()
        self.assertEqual(self.secret.password_clear_sync.call_count, 2)
```

**Line-by-line explanation**

- **L79** — Define test\_clear\_failure\_is\_reported\_after\_trying\_both\_kinds(self). Fail the first fake keyring clear and succeed the second; require AuthenticationError only after both deletion attempts.
- **L80–L83** — Prepare self.secret.password\_clear\_sync.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L84** — Expect the enclosed call to raise AuthenticationError. A missing/wrong exception makes the test fail.
- **L85** — Call keyring.clear\_saved\_login with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L86** — Require self.secret.password\_clear\_sync.call\_count to equal 2. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

[[#4 Package branch — file map|↑ Package file map]]

### 13.23 Package source — tests/test_networkmanager.py

Offline regression checks for networkmanager. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Functions and their purpose**

- **NetworkManagerTests.test_duplicate_profile_is_rejected**, L15–L24: Return two UUID lines from fake nmcli and require an ambiguous-profile error rather than picking one arbitrarily.
- **NetworkManagerTests.test_existing_incompatible_profile_is_not_modified**, L26–L34: Return another plugin for an existing named profile; require a clear error after the service query, before any modification call.
- **NetworkManagerTests.test_missing_profile_is_created_with_original_flags**, L36–L52: Fake profile absence then creation; verify user permissions, autoconnect configuration, certificate checks and not-saved cookie flags match the original profile intent.
- **NetworkManagerTests.test_ambiguous_missing_lookup_cannot_create_duplicate**, L54–L62: Simulate lookup failure while the name still exists in the complete listing; require an ambiguity error and no profile-creation operation.
- **NetworkManagerTests.test_profile_gateway_and_protocol_are_validated**, L64–L87: Test the intended gateway/nc combination and mismatched gateway/protocol choices; only the intended profile settings may proceed.
- **NetworkManagerTests.test_command_failure_preserves_exit_status**, L89–L96: Make fake nmcli fail with code 10 and require NetworkManagerError.returncode to retain 10.
- **NetworkManagerTests.test_session_secrets_use_only_an_inherited_memory_file**, L98–L134: Fake TLS/certificate operations, intercept actual anonymous-fd payload, verify cookie/pin/resolve records stay out of argv, force activation failure and require fd cleanup afterward.
- **NetworkManagerTests.test_session_secrets_use_only_an_inherited_memory_file.activate**, L113–L122: Intercept the fake activation call, inspect the anonymous descriptor payload and raise the intended fake failure to exercise cleanup.

#### 13.23.1 L1–L13 · Module setup and definitions

```python
"""Backend checks with mocked commands and TLS, using no live services."""

import os
import subprocess
import unittest
from unittest.mock import Mock, patch

from cryptography import x509

from tifrvpn import networkmanager as nm
from tifrvpn.errors import NetworkManagerError, ProfileNotFound


```

**Line-by-line explanation**

- **L1** — Document this module responsibility and when its actual application operations run; this string does not execute those operations.
- **L3** — Import os at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import subprocess at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Import unittest at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L6** — Bind Mock, patch from unittest.mock at module scope. These names are then available to the functions below without a function-local import.
- **L8** — Bind x509 from cryptography at module scope. These names are then available to the functions below without a function-local import.
- **L10** — Bind networkmanager as nm from tifrvpn at module scope. These names are then available to the functions below without a function-local import.
- **L11** — Bind NetworkManagerError, ProfileNotFound from tifrvpn.errors at module scope. These names are then available to the functions below without a function-local import.

#### 13.23.2 L14–L14 · Module setup and definitions

```python
class NetworkManagerTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L14** — Define NetworkManagerTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.

#### 13.23.3 L15–L25 · NetworkManagerTests.test_duplicate_profile_is_rejected

```python
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

```

**Line-by-line explanation**

- **L15** — Define test\_duplicate\_profile\_is\_rejected(self). Return two UUID lines from fake nmcli and require an ambiguous-profile error rather than picking one arbitrarily.
- **L16–L23** — Temporarily replace nm.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise NetworkManagerError with a message matching 'expected one'. A missing/wrong exception makes the test fail.
- **L24** — Call nm.profile\_uuid with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.

#### 13.23.4 L26–L35 · NetworkManagerTests.test_existing_incompatible_profile_is_not_modified

```python
    def test_existing_incompatible_profile_is_not_modified(self):
        with (
            patch.object(nm, "require_available"),
            patch.object(nm, "profile_uuid", return_value="profile"),
            patch.object(nm, "_run", return_value="different-plugin") as run,
            self.assertRaisesRegex(NetworkManagerError, "different VPN plugin"),
        ):
            nm.setup_profile()
        self.assertEqual(run.call_count, 1)

```

**Line-by-line explanation**

- **L26** — Define test\_existing\_incompatible\_profile\_is\_not\_modified(self). Return another plugin for an existing named profile; require a clear error after the service query, before any modification call.
- **L27–L32** — Temporarily replace nm, 'require\_available' for this context so the real external operation/environment does not run. The patch is restored on block exit. Temporarily replace nm, 'profile\_uuid' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace nm, '\_run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise NetworkManagerError with a message matching 'different VPN plugin'. A missing/wrong exception makes the test fail.
- **L33** — Call nm.setup\_profile with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L34** — Require run.call\_count to equal 1. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.23.5 L36–L53 · NetworkManagerTests.test_missing_profile_is_created_with_original_flags

```python
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

```

**Line-by-line explanation**

- **L36** — Define test\_missing\_profile\_is\_created\_with\_original\_flags(self). Fake profile absence then creation; verify user permissions, autoconnect configuration, certificate checks and not-saved cookie flags match the original profile intent.
- **L37–L45** — Temporarily replace nm, 'require\_available' for this context so the real external operation/environment does not run. The patch is restored on block exit. Temporarily replace nm, 'profile\_uuid' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Temporarily replace nm, '\_run' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit.
- **L46** — Require nm.setup\_profile() to equal 'new-profile'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L47** — Assign run.call\_args.args\[0\] to args. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L48** — Require 'connection.permissions' to be present in args. The test inspects data/captured calls rather than trusting printed progress alone.
- **L49** — Require args\[-2:\] to equal \['vpn.data', nm.VPN\_DATA\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L50** — Require 'prevent\_invalid\_cert=yes' to be present in args\[-1\]. The test inspects data/captured calls rather than trusting printed progress alone.
- **L51** — Require 'cookie-flags=2' to be present in args\[-1\]. The test inspects data/captured calls rather than trusting printed progress alone.
- **L52** — Require 'connection.autoconnect' to be present in args. The test inspects data/captured calls rather than trusting printed progress alone.

#### 13.23.6 L54–L63 · NetworkManagerTests.test_ambiguous_missing_lookup_cannot_create_duplicate

```python
    def test_ambiguous_missing_lookup_cannot_create_duplicate(self):
        with (
            patch.object(nm, "require_available"),
            patch.object(nm, "profile_uuid", side_effect=ProfileNotFound("missing")),
            patch.object(nm, "_run", return_value="tifr-ivanti\nother") as run,
            self.assertRaisesRegex(NetworkManagerError, "ambiguous"),
        ):
            nm.setup_profile()
        self.assertEqual(run.call_count, 1)

```

**Line-by-line explanation**

- **L54** — Define test\_ambiguous\_missing\_lookup\_cannot\_create\_duplicate(self). Simulate lookup failure while the name still exists in the complete listing; require an ambiguity error and no profile-creation operation.
- **L55–L60** — Temporarily replace nm, 'require\_available' for this context so the real external operation/environment does not run. The patch is restored on block exit. Temporarily replace nm, 'profile\_uuid' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Temporarily replace nm, '\_run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise NetworkManagerError with a message matching 'ambiguous'. A missing/wrong exception makes the test fail.
- **L61** — Call nm.setup\_profile with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L62** — Require run.call\_count to equal 1. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.23.7 L64–L88 · NetworkManagerTests.test_profile_gateway_and_protocol_are_validated

```python
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

```

**Line-by-line explanation**

- **L64** — Define test\_profile\_gateway\_and\_protocol\_are\_validated(self). Test the intended gateway/nc combination and mismatched gateway/protocol choices; only the intended profile settings may proceed.
- **L65–L69** — For each (gateway, protocol, valid) in \[(nm.URL, 'nc', True), ('https://example.com', 'nc', False), (nm.URL, 'anyconnect', False)\], run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L70–L80** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run. Temporarily replace nm, '\_run' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit.
- **L81** — Only run this branch when valid is true. The following indented statements implement that condition’s case; later else/elif handles alternatives.
- **L82** — Call nm.validate\_profile with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L83** — Run the alternative branch after the preceding condition did not select its main branch.
- **L84–L86** — Expect the enclosed call to raise NetworkManagerError with a message matching 'Profile settings differ'. A missing/wrong exception makes the test fail.
- **L87** — Call nm.validate\_profile with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.

#### 13.23.8 L89–L97 · NetworkManagerTests.test_command_failure_preserves_exit_status

```python
    def test_command_failure_preserves_exit_status(self):
        result = subprocess.CompletedProcess([], 10, "", "NetworkManager failure\n")
        with (
            patch.object(nm.subprocess, "run", return_value=result),
            self.assertRaises(NetworkManagerError) as raised,
        ):
            nm.deactivate("profile")
        self.assertEqual(raised.exception.returncode, 10)

```

**Line-by-line explanation**

- **L89** — Define test\_command\_failure\_preserves\_exit\_status(self). Make fake nmcli fail with code 10 and require NetworkManagerError.returncode to retain 10.
- **L90** — Store the result as result. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L91–L94** — Temporarily replace nm.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise NetworkManagerError. A missing/wrong exception makes the test fail.
- **L95** — Call nm.deactivate with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L96** — Require raised.exception.returncode to equal 10. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.

#### 13.23.9 L98–L112 · NetworkManagerTests.test_session_secrets_use_only_an_inherited_memory_file

```python
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

```

**Line-by-line explanation**

- **L98** — Define test\_session\_secrets\_use\_only\_an\_inherited\_memory\_file(self). Fake TLS/certificate operations, intercept actual anonymous-fd payload, verify cookie/pin/resolve records stay out of argv, force activation failure and require fd cleanup afterward.
- **L99** — Store the result as connection. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L100** — Store the result as connection.\_\_enter\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L101** — Store the result as connection.\_\_exit\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L102** — Store the result as tls. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L103** — Store the result as tls.\_\_enter\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L104** — Store the result as tls.\_\_exit\_\_. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L105** — Assign b'mock-certificate' to tls.getpeercert.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L106** — Prepare tls.getpeername.return\_value as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L107** — Store the result as context. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L108** — Assign tls to context.wrap\_socket.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L109** — Store the result as cert. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L110** — Assign b'example-public-key' to cert.public\_key.return\_value.public\_bytes.return\_value. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L111** — Prepare captured as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.

#### 13.23.10 L113–L134 · NetworkManagerTests.test_session_secrets_use_only_an_inherited_memory_file.activate

```python
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
```

**Line-by-line explanation**

- **L113** — Define activate(arguments, \*\*kwargs). Intercept the fake activation call, inspect the anonymous descriptor payload and raise the intended fake failure to exercise cleanup.
- **L114** — Assign kwargs\['pass\_fds'\] to (fd,). This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L115** — Assign fd to captured\['fd'\]. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L116** — Require arguments\[-1\] to equal f'/proc/self/fd/{fd}'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L117** — Require 'DSID=example-session' to be absent from repr(arguments). The test inspects data/captured calls rather than trusting printed progress alone.
- **L118** — Store the result as payload. Call os.read(fd, 8192).decode with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L119** — Require 'vpn.secrets.cookie:DSID=example-session\\n' to be present in payload. The test inspects data/captured calls rather than trusting printed progress alone.
- **L120** — Require 'vpn.secrets.resolve:sslvpn.tifr.res.in:192.0.2.1\\n' to be present in payload. The test inspects data/captured calls rather than trusting printed progress alone.
- **L121** — Require 'vpn.secrets.gwcert:pin-sha256:' to be present in payload. The test inspects data/captured calls rather than trusting printed progress alone.
- **L122** — Raise NetworkManagerError('fake activation failure'), transferring control to a matching handler. Deliberate typed failures let the enclosing test/application distinguish this case.
- **L124–L130** — Temporarily replace nm.socket, 'create\_connection' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace nm.ssl, 'create\_default\_context' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace x509, 'load\_der\_x509\_certificate' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace nm, '\_run' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Expect the enclosed call to raise NetworkManagerError with a message matching 'fake activation failure'. A missing/wrong exception makes the test fail.
- **L131** — Call nm.activate with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L132** — Expect the enclosed call to raise OSError. A missing/wrong exception makes the test fail.
- **L133** — Call os.fstat with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L134** — Check the recorded call to context.wrap\_socket used the specified positional/keyword arguments exactly once.

[[#4 Package branch — file map|↑ Package file map]]

### 13.24 Package source — tests/test_quiet.py


Offline regression checks for quiet. Each test purpose below explains its fake inputs, required behavior and protected side effects. Tests use mocks/temporary resources; their assertions and example strings are not personal account data.

**Relation to main:** [[TIFR Vpn TUI#7.8 tests/test_quiet.py|tests/test_quiet.py]] — Quiet-mode checks now import package modules and assert the -m worker path instead of loading scripts by filename.

**Functions and their purpose**

- **QuietAuthenticationTests.test\_quiet\_unlocks\_before\_starting\_virtual\_display**, L19–L46: Fake executables/config/decryption/browser, record event order and require real-desktop unlock before browser startup, correct -m worker arguments and no sample secrets in commands/output.
- **QuietAuthenticationTests.test\_quiet\_unlocks\_before\_starting\_virtual\_display.browser**, L23–L28: Replace real browser execution with a deterministic fake, record startup order and check the module/quiet command shape.
- **QuietAuthenticationTests.test\_missing\_xvfb\_fails\_before\_reading\_credentials**, L48–L57: Pretend Xvfb tools are absent and require a missing-dependency failure before the decryption helper is called.
- **QuietAuthenticationTests.test\_foreground\_keeps\_existing\_browser\_path**, L59–L67: Fake worker success and require ordinary authentication to omit --quiet and avoid the Xvfb supervisor.
- **QuietAuthenticationTests.test\_virtual\_display\_uses\_x11\_and\_owns\_its\_process\_group**, L69–L84: Inspect fake Popen options and require an X11 child environment, no Wayland display, a new session and the 120-second communicate timeout.
- **QuietAuthenticationTests.test\_timeout\_escalates\_cleanup\_of\_browser\_and\_display**, L86–L102: Immediately simulate both deadline and graceful-shutdown timeouts, mock real signaling, and require SIGTERM then SIGKILL plus the readable visible-retry failure.
- **QuietAuthenticationTests.test\_cancel\_cleans\_up\_and\_propagates**, L104–L113: Immediately simulate Ctrl+C then successful cleanup; require one mocked SIGTERM and propagation of KeyboardInterrupt rather than a timeout error.
- **QuietAuthenticationTests.test\_hidden\_gpg\_never\_opens\_a\_pinentry\_prompt**, L115–L126: Use a harmless temporary file and mocked failed GPG result; require --batch, --no-tty and --pinentry-mode error when prompting is forbidden.


#### 13.24.1 L1–L17 · Module documentation, imports and shared definitions


```python
"""Quiet-mode checks without accessing a real vault, keyring or VPN."""

import contextlib
import io
import os
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tifrvpn import auth as AUTH
from tifrvpn import credentials as OTP
from tifrvpn.config import Config
```

**Line-by-line explanation**

- **L1** — Documentation string describing this module/function or embedded program. Text inside a string is data here; embedded scripts execute only when explicitly passed to another interpreter.
- **L3** — Import contextlib: temporary output redirection and context-manager cleanup. Importing a definition is distinct from calling an operation.
- **L4** — Import io: in-memory text/byte streams for harmless example output. Importing a definition is distinct from calling an operation.
- **L5** — Import os: environment variables and low-level operating-system/file-descriptor operations. Importing a definition is distinct from calling an operation.
- **L6** — Import signal: named process-group termination signals for timeout/cancellation. Importing a definition is distinct from calling an operation.
- **L7** — Import subprocess: direct child-program execution, captured output and explicit failure results. Importing a definition is distinct from calling an operation.
- **L8** — Import tempfile: temporary files/directories that isolate checks from personal configuration. Importing a definition is distinct from calling an operation.
- **L9** — Import unittest: test discovery, isolated test cases and assertions. Importing a definition is distinct from calling an operation.
- **L10** — Import Path from pathlib for path construction and normalization without shell interpolation. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L11** — Import Mock, patch from unittest.mock for temporary function/environment replacements and recording fake calls. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L13** — Import auth as AUTH from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L14** — Import credentials as OTP from tifrvpn for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.
- **L15** — Import Config from tifrvpn.config for shared package definitions used by this module. Relative leading dots refer to the package hierarchy, not the shell’s current directory.


#### 13.24.2 L18–L18 · QuietAuthenticationTests — type/state/test structure


```python
class QuietAuthenticationTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L18** — Define QuietAuthenticationTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.


#### 13.24.3 L19–L22 · QuietAuthenticationTests.test_quiet_unlocks_before_starting_virtual_display


```python
    def test_quiet_unlocks_before_starting_virtual_display(self):
        events = []
        config = Config(Path("/example.kdbx"), Path("/example.gpg"))
```

**Line-by-line explanation**

- **L19** — Define test\_quiet\_unlocks\_before\_starting\_virtual\_display(self). Fake executables/config/decryption/browser, record event order and require real-desktop unlock before browser startup, correct -m worker arguments and no sample secrets in commands/output.
- **L20** — Prepare events as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L21** — Store the result as config. Call Config with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


#### 13.24.4 L23–L47 · QuietAuthenticationTests.test_quiet_unlocks_before_starting_virtual_display.browser


```python
        def browser(command, **options):
            events.append("browser")
            self.assertEqual(command[:2], ["xvfb-run", "-a"])
            self.assertEqual(command[-2:], ["tifrvpn._sso_worker", "--quiet"])
            self.assertNotIn("example-master", command)
            return subprocess.CompletedProcess(command, 0, "DSID=example-session")

        output = io.StringIO()
        with (
            patch.object(AUTH.shutil, "which", return_value="/example/executable"),
            patch.object(AUTH, "load_config", return_value=config),
            patch.object(OTP, "validate_config"),
            patch.object(
                OTP,
                "decrypt_password",
                side_effect=lambda path: events.append("unlock") or "example-master",
            ),
            patch.object(AUTH, "background_browser", side_effect=browser),
            contextlib.redirect_stderr(output),
        ):
            self.assertEqual(AUTH.authenticate(quiet=True), "DSID=example-session")
        self.assertEqual(events, ["unlock", "browser"])
        self.assertNotIn("example-master", output.getvalue())
        self.assertNotIn("example-session", output.getvalue())
```

**Line-by-line explanation**

- **L23** — Define browser(command, \*\*options). Replace real browser execution with a deterministic fake, record startup order and check the module/quiet command shape.
- **L24** — Call events.append with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L25** — Require command\[:2\] to equal \['xvfb-run', '-a'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L26** — Require command\[-2:\] to equal \['tifrvpn.\_sso\_worker', '--quiet'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L27** — Require 'example-master' to be absent from command. The test inspects data/captured calls rather than trusting printed progress alone.
- **L28** — Return the called operation’s value to the current Python caller. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L30** — Store the result as output. Create a file-like in-memory text buffer so the test can inspect output without printing example credentials to the real terminal.
- **L31–L42** — Temporarily replace AUTH.shutil, 'which' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace AUTH, 'load\_config' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace OTP, 'validate\_config' for this context so the real external operation/environment does not run. The patch is restored on block exit. Temporarily replace OTP, 'decrypt\_password' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Temporarily replace AUTH, 'background\_browser' for this context so the real external operation/environment does not run. Simulate the supplied exception, callback or sequence of outcomes. The patch is restored on block exit. Temporarily route Python output into the selected in-memory buffer for assertions; this context does not change a real vault or VPN.
- **L43** — Require AUTH.authenticate(quiet=True) to equal 'DSID=example-session'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L44** — Require events to equal \['unlock', 'browser'\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L45** — Require 'example-master' to be absent from output.getvalue(). The test inspects data/captured calls rather than trusting printed progress alone.
- **L46** — Require 'example-session' to be absent from output.getvalue(). The test inspects data/captured calls rather than trusting printed progress alone.


#### 13.24.5 L48–L58 · QuietAuthenticationTests.test_missing_xvfb_fails_before_reading_credentials


```python
    def test_missing_xvfb_fails_before_reading_credentials(self):
        with (
            patch.object(AUTH.shutil, "which", return_value=None),
            patch.object(OTP, "decrypt_password") as helper,
        ):
            with self.assertRaisesRegex(
                RuntimeError, "requires: xvfb-run, Xvfb, xauth"
            ):
                AUTH.authenticate(quiet=True)
            helper.assert_not_called()
```

**Line-by-line explanation**

- **L48** — Define test\_missing\_xvfb\_fails\_before\_reading\_credentials(self). Pretend Xvfb tools are absent and require a missing-dependency failure before the decryption helper is called.
- **L49–L52** — Temporarily replace AUTH.shutil, 'which' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace OTP, 'decrypt\_password' for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L53–L55** — Expect the enclosed call to raise RuntimeError with a message matching 'requires: xvfb-run, Xvfb, xauth'. A missing/wrong exception makes the test fail.
- **L56** — Call AUTH.authenticate with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L57** — Check that helper was never invoked, proving rejection/bypass happened before that side effect.


#### 13.24.6 L59–L68 · QuietAuthenticationTests.test_foreground_keeps_existing_browser_path


```python
    def test_foreground_keeps_existing_browser_path(self):
        result = subprocess.CompletedProcess([], 0, "DSID=example-session")
        with (
            patch.object(AUTH.subprocess, "run", return_value=result) as run,
            patch.object(AUTH, "background_browser") as background,
        ):
            self.assertEqual(AUTH.authenticate(), "DSID=example-session")
            self.assertNotIn("--quiet", run.call_args.args[0])
            background.assert_not_called()
```

**Line-by-line explanation**

- **L59** — Define test\_foreground\_keeps\_existing\_browser\_path(self). Fake worker success and require ordinary authentication to omit --quiet and avoid the Xvfb supervisor.
- **L60** — Store the result as result. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L61–L64** — Temporarily replace AUTH.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace AUTH, 'background\_browser' for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L65** — Require AUTH.authenticate() to equal 'DSID=example-session'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L66** — Require '--quiet' to be absent from run.call\_args.args\[0\]. The test inspects data/captured calls rather than trusting printed progress alone.
- **L67** — Check that background was never invoked, proving rejection/bypass happened before that side effect.


#### 13.24.7 L69–L85 · QuietAuthenticationTests.test_virtual_display_uses_x11_and_owns_its_process_group


```python
    def test_virtual_display_uses_x11_and_owns_its_process_group(self):
        process = Mock(returncode=0)
        process.communicate.return_value = ("DSID=example-session", None)
        with (
            patch.object(AUTH.subprocess, "Popen", return_value=process) as popen,
            patch.dict(
                os.environ,
                {"WAYLAND_DISPLAY": "wayland-example", "GDK_BACKEND": "wayland"},
            ),
        ):
            AUTH.background_browser(["example-browser"])
        options = popen.call_args.kwargs
        self.assertEqual(options["env"]["GDK_BACKEND"], "x11")
        self.assertNotIn("WAYLAND_DISPLAY", options["env"])
        self.assertTrue(options["start_new_session"])
        process.communicate.assert_called_once_with(timeout=120)
```

**Line-by-line explanation**

- **L69** — Define test\_virtual\_display\_uses\_x11\_and\_owns\_its\_process\_group(self). Inspect fake Popen options and require an X11 child environment, no Wayland display, a new session and the 120-second communicate timeout.
- **L70** — Store the result as process. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L71** — Prepare process.communicate.return\_value as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L72–L78** — Temporarily replace AUTH.subprocess, 'Popen' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace os.environ, {'WAYLAND\_DISPLAY': 'wayland-example', 'GDK\_BACKEND': 'wayland'} for this context so the real external operation/environment does not run. The patch is restored on block exit.
- **L79** — Call AUTH.background\_browser with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L80** — Assign popen.call\_args.kwargs to options. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L81** — Require options\['env'\]\['GDK\_BACKEND'\] to equal 'x11'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L82** — Require 'WAYLAND\_DISPLAY' to be absent from options\['env'\]. The test inspects data/captured calls rather than trusting printed progress alone.
- **L83** — Require options\['start\_new\_session'\] to evaluate as true; this is an assertion about the tested behavior, not a real connection request.
- **L84** — Check the recorded call to process.communicate used the specified positional/keyword arguments exactly once.


#### 13.24.8 L86–L103 · QuietAuthenticationTests.test_timeout_escalates_cleanup_of_browser_and_display


```python
    def test_timeout_escalates_cleanup_of_browser_and_display(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [
            subprocess.TimeoutExpired("example-browser", 120),
            subprocess.TimeoutExpired("example-browser", 5),
            ("", None),
        ]
        with (
            patch.object(AUTH.subprocess, "Popen", return_value=process),
            patch.object(AUTH.os, "killpg") as kill,
            self.assertRaisesRegex(RuntimeError, "timed out.*Retry tifrvpn -c"),
        ):
            AUTH.background_browser(["example-browser"])
        self.assertEqual(
            [call.args for call in kill.call_args_list],
            [(123456789, signal.SIGTERM), (123456789, signal.SIGKILL)],
        )
```

**Line-by-line explanation**

- **L86** — Define test\_timeout\_escalates\_cleanup\_of\_browser\_and\_display(self). Immediately simulate both deadline and graceful-shutdown timeouts, mock real signaling, and require SIGTERM then SIGKILL plus the readable visible-retry failure.
- **L87** — Store the result as process. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L88–L92** — Prepare process.communicate.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L93–L97** — Temporarily replace AUTH.subprocess, 'Popen' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace AUTH.os, 'killpg' for this context so the real external operation/environment does not run. The patch is restored on block exit. Expect the enclosed call to raise RuntimeError with a message matching 'timed out.\*Retry tifrvpn -c'. A missing/wrong exception makes the test fail.
- **L98** — Call AUTH.background\_browser with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L99–L102** — Require \[call.args for call in kill.call\_args\_list\] to equal \[(123456789, signal.SIGTERM), (123456789, signal.SIGKILL)\]. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.


#### 13.24.9 L104–L114 · QuietAuthenticationTests.test_cancel_cleans_up_and_propagates


```python
    def test_cancel_cleans_up_and_propagates(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [KeyboardInterrupt(), ("", None)]
        with (
            patch.object(AUTH.subprocess, "Popen", return_value=process),
            patch.object(AUTH.os, "killpg") as kill,
            self.assertRaises(KeyboardInterrupt),
        ):
            AUTH.background_browser(["example-browser"])
        kill.assert_called_once_with(123456789, signal.SIGTERM)
```

**Line-by-line explanation**

- **L104** — Define test\_cancel\_cleans\_up\_and\_propagates(self). Immediately simulate Ctrl+C then successful cleanup; require one mocked SIGTERM and propagation of KeyboardInterrupt rather than a timeout error.
- **L105** — Store the result as process. Create an invented process/service/module stand-in. It can return harmless data and record calls without contacting a real vault, network or desktop service.
- **L106** — Prepare process.communicate.side\_effect as the displayed structured example data, state or ordered fake-outcome collection. It is a Python value, not a shell command string; the surrounding test/function explains why these entries are selected.
- **L107–L111** — Temporarily replace AUTH.subprocess, 'Popen' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Temporarily replace AUTH.os, 'killpg' for this context so the real external operation/environment does not run. The patch is restored on block exit. Expect the enclosed call to raise KeyboardInterrupt. A missing/wrong exception makes the test fail.
- **L112** — Call AUTH.background\_browser with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L113** — Check the recorded call to kill used the specified positional/keyword arguments exactly once.


#### 13.24.10 L115–L130 · QuietAuthenticationTests.test_hidden_gpg_never_opens_a_pinentry_prompt


```python
    def test_hidden_gpg_never_opens_a_pinentry_prompt(self):
        with tempfile.NamedTemporaryFile() as password_file:
            result = subprocess.CompletedProcess([], 1, b"", b"example error")
            with (
                patch.object(OTP.subprocess, "run", return_value=result) as run,
                self.assertRaisesRegex(RuntimeError, "Could not decrypt"),
            ):
                OTP.decrypt_password(Path(password_file.name), allow_prompt=False)
        command = run.call_args.args[0]
        self.assertIn("--batch", command)
        self.assertIn("--no-tty", command)
        self.assertEqual(command[command.index("--pinentry-mode") + 1], "error")


if __name__ == "__main__":
    unittest.main()
```

**Line-by-line explanation**

- **L115** — Define test\_hidden\_gpg\_never\_opens\_a\_pinentry\_prompt(self). Use a harmless temporary file and mocked failed GPG result; require --batch, --no-tty and --pinentry-mode error when prompting is forbidden.
- **L116** — Call tempfile.NamedTemporaryFile with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L117** — Store the result as result. Construct an invented child-program result containing argv, exit status and example output; constructing this record does not execute the command.
- **L118–L121** — Temporarily replace OTP.subprocess, 'run' for this context so the real external operation/environment does not run. Return the specified fake result. The patch is restored on block exit. Expect the enclosed call to raise RuntimeError with a message matching 'Could not decrypt'. A missing/wrong exception makes the test fail.
- **L122** — Call OTP.decrypt\_password with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.
- **L123** — Assign run.call\_args.args\[0\] to command. This records the shown state/input/result for the enclosing operation; it does not by itself run a separate process.
- **L124** — Require '--batch' to be present in command. The test inspects data/captured calls rather than trusting printed progress alone.
- **L125** — Require '--no-tty' to be present in command. The test inspects data/captured calls rather than trusting printed progress alone.
- **L126** — Require command\[command.index('--pinentry-mode') + 1\] to equal 'error'. If not, unittest marks this behavior as failing; an optional third argument supplies diagnostic context.
- **L129** — Only run this branch when \_\_name\_\_ == '\_\_main\_\_' is true. The following indented statements implement that condition’s case; later else/elif handles alternatives.
- **L130** — Call unittest.main with the shown inputs and named options. In this test context, surrounding patches determine which dependencies are harmless recorded fakes.


[[#4 Package branch — file map|↑ Package file map]]

### 13.25 Package source — tests/test_packaging.py


Installation tests replace the old copy-installer checks. They require the package to have been installed into the interpreter running the suite. Temporary unrelated directories and Python isolated mode prove that generated commands, module execution, the private worker and library imports do not accidentally depend on being inside the checkout or on PYTHONPATH. They invoke only --help, invalid-argument parsing and safe import paths, not a real login.

**Functions and their purpose**

- **PackagingTests.setUp**, L13–L19: Prepare isolated fake services or a temporary test home before each test; register cleanup so later failures cannot leave the patches active.
- **PackagingTests.run\_command**, L21–L30: Run a command from the temporary unrelated directory/HOME using the selected interpreter environment, capturing outputs with a bounded timeout.
- **PackagingTests.test\_installed\_commands\_from\_another\_directory**, L32–L42: Use the active interpreter's scripts directory and a temporary unrelated cwd/HOME with no PYTHONPATH; all three installed commands must produce successful clean --help output.
- **PackagingTests.test\_module\_and\_worker\_from\_another\_directory**, L44–L52: Run python -I -m tifrvpn and its private worker from an unrelated directory; both help paths must work using installed package metadata rather than source-directory/PYTHONPATH accidents.
- **PackagingTests.test\_generated\_command\_preserves\_argument\_errors**, L54–L58: Run the installed executable with --quiet -d and require the same status-2, no-stdout, readable-error behavior as direct CLI tests.
- **PackagingTests.test\_library\_import\_from\_another\_directory**, L60–L74: Use isolated Python from an unrelated cwd and require connect/disconnect/status to import as callables with no ordinary output.


#### 13.25.1 L1–L11 · Module documentation, imports and shared definitions


```python
"""Installed package entry points must work outside the source checkout."""

import os
import subprocess
import sys
import sysconfig
import tempfile
import unittest
from pathlib import Path
```

**Line-by-line explanation**

- **L1** — Document the package-installation contract being tested, distinct from merely adding src to a search path.
- **L3** — Import os: environment variables and low-level operating-system/file-descriptor operations. Importing a definition is distinct from calling an operation.
- **L4** — Import subprocess: direct child-program execution, captured output and explicit failure results. Importing a definition is distinct from calling an operation.
- **L5** — Import sys: interpreter identity, arguments, module loading or output/exit boundaries. Importing a definition is distinct from calling an operation.
- **L6** — sysconfig tells this interpreter where its generated executable scripts belong; the test does not guess ~/.local/bin or use another interpreter's installation.
- **L7** — Import tempfile: temporary files/directories that isolate checks from personal configuration. Importing a definition is distinct from calling an operation.
- **L8** — Import unittest: test discovery, isolated test cases and assertions. Importing a definition is distinct from calling an operation.
- **L9** — Import Path from pathlib for path construction and normalization without shell interpolation. Relative leading dots refer to the package hierarchy, not the shell’s current directory.


#### 13.25.2 L12–L12 · PackagingTests — type/state/test structure


```python
class PackagingTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L12** — Define PackagingTests as a subclass of unittest.TestCase. Instances inherit that behavior; the enclosed methods provide this test or application’s particular implementation.


#### 13.25.3 L13–L20 · PackagingTests.setUp


```python
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifrvpn package ")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.directory))
        self.environment.pop("PYTHONPATH", None)
        self.scripts = Path(sysconfig.get_path("scripts"))
```

**Line-by-line explanation**

- **L13** — Define per-test setup so each test gets an isolated temporary directory and environment.
- **L14–L16** — Create a temporary directory, register its cleanup and retain its Path; the prefix includes a space to exercise correct argument handling.
- **L17** — Copy environment values while making the temporary directory the child's HOME, avoiding real user configuration.
- **L18** — Remove PYTHONPATH so inherited manual source-path hacks cannot make the tests pass by accident.
- **L19** — Find the active interpreter's scripts directory for the three installer-generated commands.


#### 13.25.4 L21–L31 · PackagingTests.run_command


```python
    def run_command(self, arguments):
        return subprocess.run(
            arguments,
            check=False,
            cwd=self.directory,
            env=self.environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
```

**Line-by-line explanation**

- **L21** — Define a helper that launches only the explicitly supplied test command in the unrelated temporary cwd.
- **L22–L30** — Run that argv list with isolated HOME/environment, captured text streams, explicit return-code handling and a 20-second command timeout.


#### 13.25.5 L32–L43 · PackagingTests.test_installed_commands_from_another_directory


```python
    def test_installed_commands_from_another_directory(self):
        for command in ("tifrvpn", "tifr-otp", "tifr-import-totp"):
            with self.subTest(command=command):
                executable = self.scripts / command
                self.assertTrue(
                    executable.is_file(), f"Install the package first: {executable}"
                )
                result = self.run_command([str(executable), "--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout.lower())
                self.assertEqual(result.stderr, "")
```

**Line-by-line explanation**

- **L32** — Define test\_installed\_commands\_from\_another\_directory(self). Use the active interpreter's scripts directory and a temporary unrelated cwd/HOME with no PYTHONPATH; all three installed commands must produce successful clean --help output.
- **L33** — For each command in ('tifrvpn', 'tifr-otp', 'tifr-import-totp'), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L34** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run.
- **L35** — Locate each generated console executable under this interpreter's command directory.
- **L36–L38** — Require it to exist as a file. The assertion's instruction distinguishes a missing installation from a product runtime failure.
- **L39** — Ask the installed command for --help, which must exit before real GUI/network/credentials are required.
- **L40–L42** — Require success, a usage message and no stderr for all three commands.


#### 13.25.6 L44–L53 · PackagingTests.test_module_and_worker_from_another_directory


```python
    def test_module_and_worker_from_another_directory(self):
        for module in ("tifrvpn", "tifrvpn._sso_worker"):
            with self.subTest(module=module):
                result = self.run_command(
                    [sys.executable, "-I", "-m", module, "--help"]
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--quiet", result.stdout)
                self.assertEqual(result.stderr, "")
```

**Line-by-line explanation**

- **L44** — Define test\_module\_and\_worker\_from\_another\_directory(self). Run python -I -m tifrvpn and its private worker from an unrelated directory; both help paths must work using installed package metadata rather than source-directory/PYTHONPATH accidents.
- **L45** — For each module in ('tifrvpn', 'tifrvpn.\_sso\_worker'), run the indented body. In tests, this checks every listed case rather than a single happy path.
- **L46** — Label this loop iteration as its own subtest so failures identify the particular argument/state/input case while other cases still run.
- **L47–L49** — Use the same interpreter with -I -m for both public module execution and the private worker help path. -I ignores PYTHONPATH and user-site contamination; installed package availability must suffice.
- **L50–L52** — Require both module entry paths to succeed and mention --quiet with no error output.


#### 13.25.7 L54–L59 · PackagingTests.test_generated_command_preserves_argument_errors


```python
    def test_generated_command_preserves_argument_errors(self):
        result = self.run_command([str(self.scripts / "tifrvpn"), "--quiet", "-d"])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--quiet is only supported when connecting", result.stderr)
```

**Line-by-line explanation**

- **L54** — Define test\_generated\_command\_preserves\_argument\_errors(self). Run the installed executable with --quiet -d and require the same status-2, no-stdout, readable-error behavior as direct CLI tests.
- **L55** — Run the generated tifrvpn executable with an invalid quiet/disconnect combination, testing the real installation wrapper rather than calling cli.main directly.
- **L56–L58** — Require preserved argument-error status 2, no stdout and the expected diagnostic on stderr.


#### 13.25.8 L60–L74 · PackagingTests.test_library_import_from_another_directory


```python
    def test_library_import_from_another_directory(self):
        result = self.run_command(
            [
                sys.executable,
                "-I",
                "-c",
                (
                    "from tifrvpn import connect, disconnect, status; "
                    "assert all(callable(function) for function in (connect, disconnect, status))"
                ),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")
```

**Line-by-line explanation**

- **L60** — Define test\_library\_import\_from\_another\_directory(self). Use isolated Python from an unrelated cwd and require connect/disconnect/status to import as callables with no ordinary output.
- **L61–L71** — Execute a tiny safe import/callable-check script in isolated mode from the unrelated directory. It imports three public operations without invoking them.
- **L72–L74** — Require successful silent library import in that installed environment.


[[#4 Package branch — file map|↑ Package file map]]

### 13.26 Package source — pyproject.toml

The project declares Python>=3.13, its installed command entry points, build backend and Python dependencies. PyGObject is now a declared dependency, providing import gi inside the ordinary uv environment. This metadata cannot install operating-system libraries or services.

**Relation to main:** [[TIFR Vpn TUI#7.9 pyproject.toml|pyproject.toml]] — Replace the greeting entry point with three real commands, remove redundant argparse, and select the actual tifrvpn module.

#### 13.26.1 L1–L28 · File contents

```toml
[project]
name = "tifrvpn-tui"
version = "0.1.0"
description = "TIFR VPN library and terminal tools using NetworkManager/OpenConnect"
readme = "README.md"
authors = [
    { name = "sohamch08", email = "sohamchatterjee999@gmail.com" }
]
requires-python = ">=3.13"
dependencies = [
    "cryptography>=50.0.2",
    "numpy>=2.5.4",
    "pygobject>=3.58.1",
    "pyside6>=6.12.0",
    "zxing-cpp>=3.1.1",
]

[project.scripts]
tifrvpn = "tifrvpn.cli:main"
tifr-otp = "tifrvpn.cli:otp_main"
tifr-import-totp = "tifrvpn.cli:import_totp_main"

[build-system]
requires = ["uv_build>=0.13.6,<0.14.0"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "tifrvpn"
```

**Line-by-line explanation**

- **L1** — Open standard Python project metadata in TOML, which is configuration data rather than executable Python.
- **L2** — Keep the distribution/install metadata name tifrvpn-tui. A distribution name need not equal its import package name or executable command names.
- **L3** — Keep version 0.1.0; all branch refactoring is still under this declared release label.
- **L4** — Replace main's placeholder description with the actual library/terminal-tool purpose.
- **L5** — Use README.md as the long description.
- **L6–L8** — Record the declared author identity as metadata; it is not a VPN account setting or an email-sending operation.
- **L9** — Require Python 3.13 or newer for package installation.
- **L10** — Begin the direct Python dependency list. argparse was removed because it is already in the supported Python standard library.
- **L11** — Require cryptography for certificate/public-key parsing during tunnel activation.
- **L12** — Require NumPy for grayscale QR pixel arrays.
- **L13** — Declare PyGObject as a Python dependency. The installed distribution supplies import gi; uv can build it for this environment Python instead of reusing Fedora Python bindings.
- **L14** — Require PySide6 for local password setup and scanner/camera UI.
- **L15** — Require zxing-cpp for QR decoding.
- **L16** — Close the list of Python dependency requirements.
- **L18** — Open the standard console-script entry-point table. Installers use it to generate executable wrappers in the selected Python environment.
- **L19** — Generate tifrvpn to call tifrvpn.cli.main; importing a module and calling the function replaces the old root Zsh launcher path.
- **L20** — Generate tifr-otp to call cli.otp\_main, the terminal wrapper around shared credential functions.
- **L21** — Generate tifr-import-totp to call cli.import\_totp\_main, which parses options before importing the scanner.
- **L23** — Declare the Python build-system table; these are build dependencies, not OS VPN services.
- **L24** — Use a compatible uv\_build release range for creating wheels/source distributions and editable metadata.
- **L25** — Select uv\_build as the package build backend.
- **L27** — Open uv\_build-specific package-layout configuration.
- **L28** — Set module-name=tifrvpn so the backend packages src/tifrvpn, despite the distribution being named tifrvpn-tui. This removes the old mismatch with the unused src/tifrvpn\_tui greeting scaffold.

[[#4 Package branch — file map|↑ Package file map]]

### 13.27 Package source — config.example.json


The previously missing example config is now present on the package branch. It contains paths and a KeePass entry name, never actual passwords or a TOTP seed. Copying it is a user setup action; importing the library does not automatically create config files.


#### 13.27.1 L1–L5 · Complete file


```json
{
  "database": "~/Documents/KeePass/Passwords.kdbx",
  "password_file": "~/.local/share/tifr-vpn/keepass-password.gpg",
  "entry": "TIFR"
}
```

**Line-by-line explanation**

- **L1** — Open a JSON object. JSON uses double-quoted names and strings and does not accept comments or trailing commas in this parser.
- **L2** — Select the default KeePass database path; config normalization expands a leading ~ to the home directory.
- **L3** — Select the default ciphertext file containing the GPG-encrypted database master password, not the actual master password text.
- **L4** — Select the saved KeePass entry path TIFR; a grouped entry can instead be named VPN/TIFR.
- **L5** — Close the object. Each setting can be overridden by its corresponding TIFR\_KEEPASS environment variable when using load\_config.


[[#4 Package branch — file map|↑ Package file map]]

### 13.28 Package source — README.md

The current README documents the isolated Python 3.13 uv route, native GI build/runtime prerequisites, module-level import behavior, library use and daily commands. This is a verbatim source snapshot; the beginner walkthrough in section15 explains the new installation choices in more detail.

**Relation to main:** [[TIFR Vpn TUI#7.14 README.md|README.md]] — Shared account/SSO instructions remain; installation/library/developer sections now describe a real Python package.

#### 13.28.1 L1–L32 · File contents

````markdown
# TIFR VPN Python package

A Python library and terminal commands for connecting to
**https://sslvpn.tifr.res.in/tifruser** with NetworkManager/OpenConnect.
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
- **Python packages:** `PyGObject` (imported as `gi`), `cryptography`, `PySide6`,
  `numpy`, and `zxing-cpp`.
- **Background sign-in (optional):** Xvfb, the `xvfb-run` wrapper, and `xauth`.

Package names vary between distributions. The project's Python dependencies are
declared in `pyproject.toml`. uv installs PyGObject into the project's own `.venv`,
````

**Line-by-line explanation**

- **L1** — Rename the document to describe the Python package, replacing the earlier terminal-script-only title.
- **L3–L6** — Introduce both the importable library and terminal commands while retaining the same gateway, cached-session reuse and vault-backed SSO purpose.
- **L8** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L9–L12** — A physical line in the README section “TIFR VPN Python package”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L13** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L15** — A physical line in the README section “TIFR VPN Python package”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L17** — Comment for readers: 1. Install dependencies and commands. The comment documents intent or linter policy and is not executed.
- **L19** — A physical line in the README section “1. Install dependencies and commands”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L21** — List Python 3.13+ as the runtime; the old Zsh launcher requirement disappears because command dispatch moved to Python. Other Linux services still remain necessary.
- **L22–L26** — A physical line in the README section “1. Install dependencies and commands”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L27–L28** — List the Python distributions installed into the project environment, including PyGObject, whose import name is gi. QR use is optional, but its declared Python dependencies are installed and imported by the CLI.
- **L29** — A physical line in the README section “1. Install dependencies and commands”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L31** — A physical line in the README section “1. Install dependencies and commands”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L32** — Explain that uv installs/builds the Python bindings in .venv, while their compiler and native development/runtime libraries must already be available from the OS.

#### 13.28.2 L33–L64 · File contents

````markdown
building it and Pycairo for that environment's Python. This requires a C compiler
and the native development libraries in addition to the runtime libraries. On
Fedora, install the GI runtime/build prerequisites with:

```sh
sudo dnf install gcc pkgconf-pkg-config gobject-introspection-devel cairo-gobject-devel gtk3 webkit2gtk4.1 libsoup3 libsecret
```

The chosen Python also needs its development headers. uv-managed CPython includes
these; for Fedora's system Python, install `python3-devel` as well. The packages
above cover GI support; the VPN and credential tools listed earlier are still
required separately.

Imports are grouped at the top of each module. Importing the core package loads
the Secret Service bindings and cryptography; importing the command adapters
also loads Qt and the QR libraries, even for `--help`. The SSO worker loads its
GTK/WebKit bindings at module import. Imports do not open dialogs, access the
keyring, scan a camera, or start a VPN connection.

NetworkManager must be running. Your desktop must provide a working, unlocked
Secret Service keyring, such as GNOME Keyring. Minimal window-manager sessions
may need desktop keyring and PolicyKit authentication-agent setup first.

Install this checkout as a Python package, **as your normal user**, after
installing the system dependencies above:

```sh
uv sync --locked
source .venv/bin/activate
```

uv uses the Python version in `.python-version` (currently 3.13) and creates an
````

**Line-by-line explanation**

- **L33–L35** — Explain that uv installs/builds the Python bindings in .venv, while their compiler and native development/runtime libraries must already be available from the OS.
- **L37** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L38** — Show the Fedora installation command for the GI compiler/build prerequisites and native GTK3/WebKit4.1/Soup 3/Secret libraries. It does not install the separate VPN or credential programs.
- **L39** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L41–L44** — Distinguish interpreter headers from runtime libraries: the chosen Python needs matching development headers; uv-managed CPython provides its own, while Fedora system Python uses python3-devel.
- **L46–L50** — Document the requested module-level imports and their consequence: dependencies load before operations, including CLI help, but imports do not themselves open dialogs, read the keyring, scan or connect.
- **L52–L54** — A physical line in the README section “1. Install dependencies and commands”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L56–L57** — Begin installation after OS dependencies are installed, using the ordinary desktop user rather than a root-owned Python environment.
- **L59** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L60** — Synchronize the isolated project environment from the checked-in lockfile; fail if that lockfile would need changing.
- **L61** — Activate the environment in the current shell so its bin directory is searched before older commands. Activation is a convenience; an explicit environment/bin executable path also works.
- **L62** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L64** — Explain the final Python 3.13 isolated-uv route: local PyGObject supplies gi, so Python 3.14 and system-site-packages are unnecessary. The explicit uv pip command is an alternative for another suitable environment.

#### 13.28.3 L65–L96 · File contents

````markdown
isolated `.venv`. `import gi` comes from its installed PyGObject dependency;
neither Python 3.14 nor `--system-site-packages` is required. If you already
have a suitable environment, you can instead run `uv pip install --python
/path/to/environment/bin/python .`.
The installation creates `tifrvpn`, `tifr-otp` and `tifr-import-totp` in that
environment's command directory and makes `import tifrvpn` available.
Activate the environment whenever you want to use its commands.

Python dependencies are installed from `pyproject.toml`; the system dependencies
listed above must be installed separately. After updating the checkout, rerun
`uv sync --locked`. uv installs this checkout in editable mode; other package
installation routes are described below.

## 2. Save your own login in KeePassXC

1. Create/open a **password-protected** database. The default location expected
   by the package is `~/Documents/KeePass/Passwords.kdbx`.
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

````

**Line-by-line explanation**

- **L65–L68** — Explain the final Python 3.13 isolated-uv route: local PyGObject supplies gi, so Python 3.14 and system-site-packages are unnecessary. The explicit uv pip command is an alternative for another suitable environment.
- **L69–L71** — Explain interpreter suitability, generated command locations and import availability. A preexisting virtual environment can differ from this recommendation; verify its interpreter and native binding visibility rather than assuming its name guarantees suitability.
- **L73–L74** — Separate Python package dependencies from system services/libraries, and distinguish reinstalling a normal installed copy from editable development.
- **L75–L76** — Repeat uv sync --locked after dependency/metadata updates. The uv project installation is editable; Python source edits are visible to new processes.
- **L78** — Comment for readers: 2. Save your own login in KeePassXC. The comment documents intent or linter policy and is not executed.
- **L80–L87** — A physical line in the README section “2. Save your own login in KeePassXC”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L89** — A physical line in the README section “2. Save your own login in KeePassXC”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L91** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L92** — A physical line in the README section “2. Save your own login in KeePassXC”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L93** — Comment for readers: Or, if the webcam is unsuitable:. The comment documents intent or linter policy and is not executed.
- **L94** — A physical line in the README section “Or, if the webcam is unsuitable:”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L95** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.

#### 13.28.4 L97–L128 · File contents

````markdown
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
````

**Line-by-line explanation**

- **L97–L102** — A physical line in the README section “Or, if the webcam is unsuitable:”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L104–L105** — A physical line in the README section “Or, if the webcam is unsuitable:”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L107** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L108** — A physical line in the README section “Or, if the webcam is unsuitable:”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L109** — Copy the now-present config.example.json into the user's config directory when customization is needed. Unlike main's historical snapshot, this example file exists on the branch; the command can replace an existing config, so it is an optional setup step rather than a daily command.
- **L110** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L112–L117** — A physical line in the README section “Or, if the webcam is unsuitable:”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L119** — Comment for readers: 3. Encrypt the database password with GPG. The comment documents intent or linter policy and is not executed.
- **L121** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L123** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L124–L125** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L126** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L128** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.

#### 13.28.5 L129–L160 · File contents

````markdown

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

````

**Line-by-line explanation**

- **L130** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L131** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L132** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L134–L139** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L141–L142** — A physical line in the README section “3. Encrypt the database password with GPG”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L144** — Comment for readers: 4. Connect. The comment documents intent or linter policy and is not executed.
- **L146** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L147–L148** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L149** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L151–L152** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L154–L159** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.

#### 13.28.6 L161–L192 · File contents

````markdown
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
````

**Line-by-line explanation**

- **L161–L166** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L168** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L170–L177** — A Markdown table row mapping the shown command/module to its documented behavior. Pipe characters separate columns; this is reference data rather than runtime code.
- **L179–L181** — A physical line in the README section “4. Connect”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L183** — Comment for readers: Troubleshooting and storage. The comment documents intent or linter policy and is not executed.
- **L185–L192** — A physical line in the README section “Troubleshooting and storage”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.

#### 13.28.7 L193–L224 · File contents

````markdown
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
For development, install the checkout in editable mode inside the environment
created above:

```sh
python -m pip install -e .
```

With uv, the equivalent command is:

```sh
uv pip install --python .venv/bin/python -e .
```

An editable installation uses the source files directly, so Python code changes
are available without reinstalling. Reinstall after changing package metadata
or command entry points. System programs and GTK/WebKit/Secret Service bindings
````

**Line-by-line explanation**

- **L193–L194** — A physical line in the README section “Troubleshooting and storage”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L196–L202** — A physical line in the README section “Troubleshooting and storage”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L204** — A physical line in the README section “Troubleshooting and storage”. Read it with adjacent wrapped lines as one instruction/explanation; the complete branch workflows above explain the operation, assumptions and distinction from main.
- **L206** — Begin the branch's new Python-library/developer instructions.
- **L208** — Distinguish import name tifrvpn from installed distribution metadata name tifrvpn-tui. The console commands are a third naming concern defined by project.scripts.
- **L209–L210** — Introduce editable installation inside the chosen suitable Python environment.
- **L212** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L213** — pip install -e . registers this source checkout as the implementation location for development; new interpreter processes see source edits without recopying these files.
- **L214** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L216** — Introduce uv as an alternative package-installation frontend.
- **L218** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L219** — Target the exact .venv interpreter explicitly when using uv, preventing accidental installation into another environment.
- **L220** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L222–L224** — Explain that source edits and packaging metadata/entry-point edits have different reinstall needs. Editable installation still does not install/replace NetworkManager or GI system packages.

#### 13.28.8 L225–L256 · File contents

````markdown
are still required for the features that use them.

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
````

**Line-by-line explanation**

- **L225** — Explain that source edits and packaging metadata/entry-point edits have different reinstall needs. Editable installation still does not install/replace NetworkManager or GI system packages.
- **L227** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L228** — Importing tifrvpn loads definitions and public names; it does not connect immediately.
- **L230** — Actually call the read-only status operation; this is the point when networking tools/service are queried.
- **L231** — Print state and computed device tuple, showing the library returns data rather than printing status itself.
- **L233** — Comment ties library calls to their equivalent user-facing commands.
- **L234** — Synchronously connect with quiet mode and print progress via an explicitly supplied callback. The worker's captured messages currently arrive after its subprocess finishes, not continuously during its run.
- **L235** — Call synchronous disconnect; this example line performs a real state-changing operation if a reader executes it with their configured environment.
- **L236** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L238–L244** — Document operation results: setup returns UUID; forget\_login returns no value; status/connect/disconnect return VPNStatus with preserved transitions, device parsing and changed flags; expected failures carry VPNError.returncode.
- **L246–L247** — Explain direct Config injection alongside defaults/JSON/environment, without rewriting the caller's process environment to customize one connect attempt.
- **L249** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L250–L251** — Import Path, settings/error types and the public connect operation for the next example.
- **L253–L256** — Construct immutable settings for a particular database/ciphertext/entry. Path('~/...') is normalized by Config.\_\_post\_init\_\_, which expands ~ and checks absolute paths.

#### 13.28.9 L257–L288 · File contents

````markdown
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
````

**Line-by-line explanation**

- **L257** — Construct immutable settings for a particular database/ciphertext/entry. Path('~/...') is normalized by Config.\_\_post\_init\_\_, which expands ~ and checks absolute paths.
- **L258–L261** — Catch expected VPNError while making a real connect call with explicit settings. An embedding application can decide how to present/retry the failure rather than having the library terminate it.
- **L262** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L264–L268** — State import safety and synchronous operation behavior. No callback means no public-controller progress printing; actual operations may still open GPG/sign-in/keyring prompts. Current auth worker stderr is captured and replayed after completion.
- **L270** — Introduce more specialized module APIs below the top-level public VPN operations.
- **L272** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L273** — Import nonprinting current-code retrieval from the credential layer.
- **L274** — Import pure migration decoding and TOTP calculation from the algorithm module; these functions operate on supplied data rather than opening a webcam.
- **L276** — Get the current KeePassXC TOTP as a string. It can unlock GPG/read the vault when actually called, but does not intentionally print the result.
- **L277** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L279–L288** — Map each package module to its single responsibility. The reorganized files expose boundaries for reuse/testing rather than forcing every consumer through one script entry point.

#### 13.28.10 L289–L305 · File contents

````markdown
| `cli` | Arguments, terminal output, notifications and exit codes |
| `_sso_worker` | Private isolated WebKit subprocess entry point |

`python -m tifrvpn` runs the same CLI as `tifrvpn`. All implementation lives
under `src/tifrvpn/`. The three commands are generated during package
installation from the entry points in `pyproject.toml`.

Offline checks after installing the package:

```sh
python -B -m unittest discover -s tests -v
uv build
```

Tests use fake commands and services; they do not access personal credentials,
change NetworkManager profiles or connect to the VPN. A live desktop sign-in
and tunnel connection still need verification with your own TIFR account.
````

**Line-by-line explanation**

- **L289–L290** — Map each package module to its single responsibility. The reorganized files expose boundaries for reuse/testing rather than forcing every consumer through one script entry point.
- **L292–L294** — Document that python -m tifrvpn and the generated command share CLI implementation and that project.scripts replaces the deleted root wrappers/installer in the current snapshot.
- **L296** — The following test commands assume the package is installed in the interpreter running them; PYTHONPATH=src alone is not sufficient for the installation tests.
- **L298** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L299** — Run unittest discovery using the selected interpreter, suppress bytecode writes with -B and print test names with -v.
- **L300** — Build distributable artifacts with uv; this guide separately verified an offline build into a temporary documentation directory.
- **L301** — Open/close the displayed Markdown fenced example block. Its contents are instructions/examples for the reader, not code automatically executed by opening README.
- **L303–L305** — Clarify test scope: fakes/temporary locations avoid live credentials and VPN changes. Passing 50 offline tests and building a wheel does not establish a real desktop sign-in/tunnel on this machine.

[[#4 Package branch — file map|↑ Package file map]]

### 13.29 Package source — uv.lock

The lockfile records the exact dependency selection and artifact metadata, now including PyGObject 3.58.1 and its Pycairo 1.29.2 dependency. It is generated project data, not code to execute and not an installation of GTK or NetworkManager. The complete selected package records are preserved below.

**Relation to main:** [[TIFR Vpn TUI#7.15 uv.lock|uv.lock]] — The redundant separately distributed argparse package and its references disappear; other locked dependencies remain.

#### 13.29.1 L1–L32 · File contents

```toml
version = 1
revision = 5
requires-python = ">=3.13"

[[package]]
name = "cffi"
version = "2.1.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pycparser", marker = "implementation_name != 'PyPy'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9e/ef/008a1939e372c06329a3fce4279c02f328488f3526744906eeec3da7ad5f/cffi-2.1.1.tar.gz", hash = "sha256:dd31f52ea1086513bb9df30f8fcee9b8918323ae067a3d5b78bc826a000712be", size = 530807, upload-time = "2026-08-03T21:21:18.939Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/9d/f4/035513d4117049066b4779dc3b7c0c0fdad175fa13731c9f4003f1cd1478/cffi-2.1.1-cp313-cp313-ios_13_0_arm64_iphoneos.whl", hash = "sha256:b5bdfd1c873d4e093aabc0ca84c4ca6dbc4f752afb5c86f146d9742580c9da2e", size = 194248, upload-time = "2026-08-03T21:19:59.399Z" },
    { url = "https://files.pythonhosted.org/packages/76/af/2aeb4dbb5fc41a04161ae9ff1518de7cec08e164f44a8ce6a4cf7fd2cd1d/cffi-2.1.1-cp313-cp313-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:31348097ff5bbe827ccc41795d4dd099d9f0625e7def00ee653c137a490c2a6c", size = 196908, upload-time = "2026-08-03T21:20:00.746Z" },
    { url = "https://files.pythonhosted.org/packages/a7/46/2e5fdde8555706dd98139a910ca11be02809f3f605ce956f655d0214e100/cffi-2.1.1-cp313-cp313-macosx_10_15_x86_64.whl", hash = "sha256:9d2055050ea716bd38b7f7f1579c275386646b4894c155a3e2f3cd62ed41b7c6", size = 184805, upload-time = "2026-08-03T21:20:02.02Z" },
    { url = "https://files.pythonhosted.org/packages/55/41/4c7042f317b9217502988f0873af87e16ad606dc20f84e546e3e6ce9764c/cffi-2.1.1-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:19ee6127ee34de7d83ce3d371ebc5ed91addbdcc39f9ab15ce4eb35a4e534971", size = 184764, upload-time = "2026-08-03T21:20:03.141Z" },
    { url = "https://files.pythonhosted.org/packages/43/1f/1c3d90d91811c8f86ced9ed637956c54bfe5b79ca98fe976d7f8c8979f6b/cffi-2.1.1-cp313-cp313-manylinux1_i686.manylinux2014_i686.manylinux_2_17_i686.manylinux_2_5_i686.whl", hash = "sha256:6a8dddef476fab96d066d578fc88526767b836ab5ab21754e1d5bf3879c31c7c", size = 214722, upload-time = "2026-08-03T21:20:04.377Z" },
    { url = "https://files.pythonhosted.org/packages/37/6f/3b5ce4c3b2192d250f04908f2bfd91ef34552ec8f7716a5d4abdb8d67bb2/cffi-2.1.1-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:f16c709686a78c727bbbf059f92b0bf41c6fc60deec706d2dc19f529175a6125", size = 222369, upload-time = "2026-08-03T21:20:05.544Z" },
    { url = "https://files.pythonhosted.org/packages/02/10/4b3c75dde3d9663c9e02ba05c2668b954f671d4bbe346413ca8c696b295a/cffi-2.1.1-cp313-cp313-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:fcd22650c908d7b7da162bbfaab594a1227a15d1643a98c68b122ac642fa2264", size = 210175, upload-time = "2026-08-03T21:20:06.75Z" },
    { url = "https://files.pythonhosted.org/packages/df/62/14f74b9543e605d17701dc797b815958b8bb70b7624ce1b832ddad48ed6c/cffi-2.1.1-cp313-cp313-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:aa9511c62d14da7aacc9b4bf51f3f697a621e83b2d6919008243c3aad168eea3", size = 208670, upload-time = "2026-08-03T21:20:08.04Z" },
    { url = "https://files.pythonhosted.org/packages/95/95/86342356ff5953b3fb06f7ef7c5bee212d45e770abc7218d451b9148313c/cffi-2.1.1-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:a931079504ecc49efed7744c476a5c343a92fabf66dec2db95edb1b2fdc770e2", size = 221824, upload-time = "2026-08-03T21:20:09.274Z" },
    { url = "https://files.pythonhosted.org/packages/eb/ff/7b3429ff53aafe931ed8a5fc69f481bbef7ba6de87ddcbb63d08f483f613/cffi-2.1.1-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:a2d7755bef5a12ed488f4ef1f1b69ee9191d7396083b755a5d2295f6edb4768b", size = 225148, upload-time = "2026-08-03T21:20:10.7Z" },
    { url = "https://files.pythonhosted.org/packages/34/34/a95870b9221e09cf4f2ce3178b1a210abdfe63a1bd357da940418d7b8d15/cffi-2.1.1-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:e0bcb7e0f677f543555d2adff3bf19c05f66cdb4796e5ff602442ab2fe3c4ef7", size = 223564, upload-time = "2026-08-03T21:20:12.165Z" },
    { url = "https://files.pythonhosted.org/packages/70/ea/839b50531021a647fb5e929f72cf97bc1ff702b5472166164b5b6e76b851/cffi-2.1.1-cp313-cp313-win32.whl", hash = "sha256:334644fbac4eff73d985a17a91226df55d0f394160c4cfb880e084c8f7161cac", size = 175263, upload-time = "2026-08-03T21:20:13.559Z" },
    { url = "https://files.pythonhosted.org/packages/60/a6/8b149b2c3f2e11aaa1618ef64500b45f50f22c57a977a4dff1aff1f91042/cffi-2.1.1-cp313-cp313-win_amd64.whl", hash = "sha256:1aa5645c30469b09530c4ebca77ebf8f17618293c58f8549cb1a543a50236e7d", size = 185688, upload-time = "2026-08-03T21:20:14.69Z" },
    { url = "https://files.pythonhosted.org/packages/01/9a/11f687cb39d6a3504060d5242f04f48c735afb4d3d533958a20594890cb2/cffi-2.1.1-cp313-cp313-win_arm64.whl", hash = "sha256:63bbfd5ded17c4840ac07cd8f1c21ba9d9708141f840b324f422f41b207e3973", size = 180078, upload-time = "2026-08-03T21:20:15.917Z" },
    { url = "https://files.pythonhosted.org/packages/d3/7b/d6bbf82b8b96e7391438898c42f5bd96dd02030fd5b64937d248220003e2/cffi-2.1.1-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:7dbb61fe3a7699468030f71bbe5f8a0e326a151daa91beb11a6fc1f980c55e1c", size = 194064, upload-time = "2026-08-03T21:20:17.148Z" },
    { url = "https://files.pythonhosted.org/packages/94/e6/bcc91b283be94735e268487a054004f0aa19947b6348fa367db53230abc8/cffi-2.1.1-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:f24fb43132a4c6b4cb4eb029492919b2db645be6808d738f244fd146c03c32cb", size = 196720, upload-time = "2026-08-03T21:20:18.268Z" },
    { url = "https://files.pythonhosted.org/packages/d9/99/c4b0c17cacdc9c3b8f280026286a9826d6a208c0f047591a3c3ce99b91fd/cffi-2.1.1-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:d28630f5854ab07ab1fd4aba756de52326c82e6be15d414b12793f1975048b54", size = 184964, upload-time = "2026-08-03T21:20:19.708Z" },
    { url = "https://files.pythonhosted.org/packages/b3/a9/9db617d05d7367c1ad0ab00b3aa6e6f9281edd689b4ee9ea0e5a84e89c97/cffi-2.1.1-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:661c298b4821edebead0c91edd2b00374d67ad7c5a1f7a91d4442633b79d6a72", size = 184962, upload-time = "2026-08-03T21:20:20.833Z" },
    { url = "https://files.pythonhosted.org/packages/67/b8/b42132ca113dc567d37684437b46ca1dafc885902b02a110a02d5b511857/cffi-2.1.1-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:58acb8ab8e295e6c5ea12f888cbb13cf21511ef2a3303a23f4325c29d17fe5c1", size = 222328, upload-time = "2026-08-03T21:20:22.118Z" },
```

**Line-by-line explanation**

- **L1** — Lockfile format version, not your project version or Python version. uv reads it to understand the file structure.
- **L2** — Record the lockfile format revision used by the generating uv version. This is tooling metadata, not a count of Git commits.
- **L3** — Record that the resolved project targets Python 3.13 or newer. Different wheel filenames below can describe compatible build tags rather than changing that overall requirement.
- **L5** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L6** — Name this locked distribution cffi. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L7** — Pin cffi to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L8** — Record the package registry from which cffi is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L9** — Begin cffi dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L10** — Reference the dependency named pycparser. marker is a condition limiting when the dependency is needed; here the referenced condition distinguishes Python implementations such as PyPy. It is needed by cffi; dependency resolution also follows that package's own dependency references.
- **L11** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L12** — Record the source archive for cffi: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L13** — Begin the list of prebuilt wheel artifacts available for cffi across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L14** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L15** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L16** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L17** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L18** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux1\_i686.manylinux2014\_i686.manylinux\_2\_17\_i686.manylinux\_2\_5\_i686.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L19** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L20** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L21** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L22** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L23** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L24** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L25** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L26** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L27** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L28** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L29** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L30** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L31** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L32** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.

#### 13.29.2 L33–L64 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/80/10/c5c0cbf0a657aecf59ef511409734230bf556f05a0d6c9eed7aa5c0a0166/cffi-2.1.1-cp314-cp314-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:456a61fa52d579ebf9df2e9552ead5129855dbaff6c1e5a9b1bc408809bdc062", size = 209985, upload-time = "2026-08-03T21:20:23.401Z" },
    { url = "https://files.pythonhosted.org/packages/d5/6c/bfa0b87b03b9238148beca990292843c9396ba069b54496596594173de7b/cffi-2.1.1-cp314-cp314-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:a4f00aa42f75d6e4595e8866e748cc1705adc0cddfeb2ca86d0d03993d63ba03", size = 208530, upload-time = "2026-08-03T21:20:24.628Z" },
    { url = "https://files.pythonhosted.org/packages/e9/02/4e7d553a7ac4b4238b38b3c1b80d486e9d4436f8d2acbf87a0997fe3f402/cffi-2.1.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:b0431303acaea1089ad4b3e9ce4e6518193def1118d4073ca848635ee4ea2e96", size = 221525, upload-time = "2026-08-03T21:20:25.758Z" },
    { url = "https://files.pythonhosted.org/packages/82/1d/a4aaf9babd75acb4d5f223bff71533bee748dd770a382619a798960ee9ba/cffi-2.1.1-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:64faea20f4e2613363a1a9b9c7dd73058f3ecd00133a511e72ad7c511658f527", size = 225053, upload-time = "2026-08-03T21:20:26.985Z" },
    { url = "https://files.pythonhosted.org/packages/81/10/5dc0e7bdd18e22107054288283380fc97a06ae3f1656a106908d666a3c88/cffi-2.1.1-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:5c58fe613dc5e5336357eff555824a314d8e43282600435c8d1cb6a7a2fedd13", size = 223213, upload-time = "2026-08-03T21:20:28.277Z" },
    { url = "https://files.pythonhosted.org/packages/0b/e9/d0061c364cde06ee43168a0d076ac1da512cbc380d44767b844ba34fe2b6/cffi-2.1.1-cp314-cp314-win32.whl", hash = "sha256:1a18a57b58cfb21fc28d72e876acf10eaed67a1ed96226f92af4df681d571c4c", size = 177682, upload-time = "2026-08-03T21:20:44.288Z" },
    { url = "https://files.pythonhosted.org/packages/a7/06/1c3e01e3ba14c39f6d10bfbac52753b7e22259e38088e5cfe1d704918690/cffi-2.1.1-cp314-cp314-win_amd64.whl", hash = "sha256:3222ba5d678f80a030e6afbcc33dc1ae5cb45facabb61cee2c7016b8432fde48", size = 187949, upload-time = "2026-08-03T21:20:45.623Z" },
    { url = "https://files.pythonhosted.org/packages/87/5b/da4e39efe18eeb89cf580ea9cfc66b6a7c3eadb808fc0cc1d3a295cb5a5d/cffi-2.1.1-cp314-cp314-win_arm64.whl", hash = "sha256:ab36d55f9ed2d067327667c2fea18dda018eb628dd6347aa01dda6cf1f5d3836", size = 182947, upload-time = "2026-08-03T21:20:46.955Z" },
    { url = "https://files.pythonhosted.org/packages/23/59/40338bf421c5accea1d45158170c87006ef1cd371b05c077e76476949728/cffi-2.1.1-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:7750c6449dff7864bb9bb27ddfb0267756189201a3afc911d82b3caacd70dfc3", size = 188504, upload-time = "2026-08-03T21:20:29.495Z" },
    { url = "https://files.pythonhosted.org/packages/7d/47/5ecf1023850036e674c77ec4de86182d309ae344e39e7cba984b7df5d647/cffi-2.1.1-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:0beceaabe56af686895136a2de78db54ecd8e4046b236b8fd6d6cb61389e9bf2", size = 188259, upload-time = "2026-08-03T21:20:31.291Z" },
    { url = "https://files.pythonhosted.org/packages/2a/9c/92934c3bea9f785b23eba304538c0b4d37a2a96d2431eb3a1bc87a11aa19/cffi-2.1.1-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:49cbc70e6542d4ccccb936558d1064a8012541e78f821f955cff24e357776c94", size = 223864, upload-time = "2026-08-03T21:20:32.571Z" },
    { url = "https://files.pythonhosted.org/packages/4d/45/ba4c93527bc38616a8bd36488acb69a2212d60486794f0c1f318949bbb76/cffi-2.1.1-cp314-cp314t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:e2d65b31f36619cda3999b78b2aa9632e76b78448e7a56fc4240824200e7c4fc", size = 211538, upload-time = "2026-08-03T21:20:33.808Z" },
    { url = "https://files.pythonhosted.org/packages/80/e9/b6ef565e452acb932fb0cb5443f44a78efbd1233e566f02b5a83855e9115/cffi-2.1.1-cp314-cp314t-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:28907ab9bfb6aa13184cfc17c6b8e1023c5ab6fd7076d8c20a35e59fe04f8f29", size = 210688, upload-time = "2026-08-03T21:20:34.974Z" },
    { url = "https://files.pythonhosted.org/packages/9a/95/eff5f0cee78d2eabc7eebffec40d3fc1876b5f3c95582e018bb4b99601f2/cffi-2.1.1-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:51b31d1c98274844cfd7838ce00bfc27c7423a4dc00fc0772fc3331c2cc90676", size = 223803, upload-time = "2026-08-03T21:20:36.564Z" },
    { url = "https://files.pythonhosted.org/packages/fa/01/579d39fb8bef00a335a23d83757b44feb24cd6345a2c451b64cb67b9c362/cffi-2.1.1-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:5e7cecbaadb83884793e05828cee59b210b24583b9c7425d0ba6a754fe22eb4e", size = 226763, upload-time = "2026-08-03T21:20:37.816Z" },
    { url = "https://files.pythonhosted.org/packages/8d/b0/0b44f47c60b01b57b6e2bbd92343f13a85a1d93bc46ccf6e47e244acd99c/cffi-2.1.1-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:25792eac27877609e7bb06d42ff88278a6624fff2ba9bbb523c09616b117e80f", size = 225688, upload-time = "2026-08-03T21:20:38.959Z" },
    { url = "https://files.pythonhosted.org/packages/eb/d2/3b7176cb570a1d3e27faf67b72f591af508036e0d8b2be2ef9af9e8c84bb/cffi-2.1.1-cp314-cp314t-win32.whl", hash = "sha256:8ef53b2de9bcb9197d31854256575d59dbac0cba72ac627bb291ef5eceb74be4", size = 182868, upload-time = "2026-08-03T21:20:40.388Z" },
    { url = "https://files.pythonhosted.org/packages/56/78/31f00c1bcd97c9bbf55f1bfdf5bc809a5de8887473e90bb9960dca825e80/cffi-2.1.1-cp314-cp314t-win_amd64.whl", hash = "sha256:616f097f2fe415bc92a247f02e11f634e1f9e9a83d327e3c915c15089c87869e", size = 194104, upload-time = "2026-08-03T21:20:41.725Z" },
    { url = "https://files.pythonhosted.org/packages/7b/1b/58496f2ed0a35de575250c02a43ab3cc2c04d494a88fed31c1cabc0fd176/cffi-2.1.1-cp314-cp314t-win_arm64.whl", hash = "sha256:ad2c86c495b899d862ea0f4b42891b8713a3bd45dd4105c7fd51c2a72f39f3a5", size = 186402, upload-time = "2026-08-03T21:20:43.042Z" },
    { url = "https://files.pythonhosted.org/packages/c1/8f/9ebe220eab48a093d1a5a5e339ab0dc7316eef3bb04d63c42f0251b61f50/cffi-2.1.1-cp315-cp315-ios_13_0_arm64_iphoneos.whl", hash = "sha256:dddad92b554513a31f272570678ba307fb9f618f05e3d4a5eacafff9eae03e1d", size = 194043, upload-time = "2026-08-03T21:20:48.179Z" },
    { url = "https://files.pythonhosted.org/packages/ff/69/844bad3ece306c4782c2ecb93597035b6690d48704b803914c199da1e8b3/cffi-2.1.1-cp315-cp315-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:da0e573f9f97159390c89d9f1a9e41908b66d408cc5b58d08cf3847d844c531b", size = 196737, upload-time = "2026-08-03T21:20:49.457Z" },
    { url = "https://files.pythonhosted.org/packages/1b/8a/af668013284634733f02d683458a0728739c7d6ddb5e14cb0c20832266fe/cffi-2.1.1-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:fb92203a88b3d3053034db775110081c49d28be6551923805e039924093761e4", size = 184933, upload-time = "2026-08-03T21:20:50.639Z" },
    { url = "https://files.pythonhosted.org/packages/0c/75/2f5207ff6d1a613133b23a5203cc0c2a628313b5eb3974d7956ae3c57950/cffi-2.1.1-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:2ae64be792b8966f2c69538199728b290e34726562896df1e5dc8ffd8d8188e8", size = 185002, upload-time = "2026-08-03T21:20:52.173Z" },
    { url = "https://files.pythonhosted.org/packages/e2/31/9e1313b0a6e30e91b3b3d3fff51ae99c857c07738e3afcce1f7334e1b7ab/cffi-2.1.1-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:507a24c282e0f42f8ed737cf048572cbf580468da5555764a8331735e9c736b6", size = 222271, upload-time = "2026-08-03T21:20:53.462Z" },
    { url = "https://files.pythonhosted.org/packages/50/e3/f6234a833e6e08c7007003074723c406559eecf9b48dfc97471e5a8eb7a0/cffi-2.1.1-cp315-cp315-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:246fa40ce8645a614ff682e0b70f37134e460eaf93a775e0cbe3cca585a67a80", size = 209919, upload-time = "2026-08-03T21:20:54.783Z" },
    { url = "https://files.pythonhosted.org/packages/0d/fc/5f74e293fced6edb51af3a46c4ccf6c23c9943774ecb375ddbd522c76add/cffi-2.1.1-cp315-cp315-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:471cee653ae88de62096552e6d24ccb4a5adb8c8c9f10b5054d0122c15bf2779", size = 208529, upload-time = "2026-08-03T21:20:56.066Z" },
    { url = "https://files.pythonhosted.org/packages/44/16/29e6d01b388bef055ecd6ca8244b3f4d336bd09e92d5d892187b9601084e/cffi-2.1.1-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:aeae0e330c9f6acd681f647d46cefd30c29f93e3392882e792e82080c9691399", size = 221630, upload-time = "2026-08-03T21:20:57.336Z" },
    { url = "https://files.pythonhosted.org/packages/a4/18/fa7f1f6857d5eb88a4ca99ffcbfb7c387a287ccc154c64a73e86314745d7/cffi-2.1.1-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:42a494cee34437f05546455144f2b5d9ac09b1face62bcfce597d2e521066688", size = 225134, upload-time = "2026-08-03T21:20:58.675Z" },
    { url = "https://files.pythonhosted.org/packages/e0/9f/e8e3dfa04a1b4c241f8c91faacad872b4d4efd051d49764ad4e2fd4b9fea/cffi-2.1.1-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:cc572dace3f60ef98d7b12ff411d20f5362feb31a0439eab0085bbfd349982d7", size = 223197, upload-time = "2026-08-03T21:20:59.968Z" },
    { url = "https://files.pythonhosted.org/packages/f8/7e/8debeb04f1ab9fe2a6963964cd6f1aaf7192627b83926586a6a4e089c9fa/cffi-2.1.1-cp315-cp315-win32.whl", hash = "sha256:4f42141fc14250de6dde5ee7ea4432be017252d91f19c5ad043c084cea629cac", size = 177683, upload-time = "2026-08-03T21:21:14.901Z" },
    { url = "https://files.pythonhosted.org/packages/e0/31/5158704cc474ab65c1647932e88be78dc0873f47130e253be38bcaf13d01/cffi-2.1.1-cp315-cp315-win_amd64.whl", hash = "sha256:e6e8cff14d6fb0be70a09c0bdc58096f501952d04624ebf867e0e56da2df8960", size = 187897, upload-time = "2026-08-03T21:21:16.108Z" },
    { url = "https://files.pythonhosted.org/packages/cc/4b/b3a2da8570c704ffc0f9762cdc3ec0f02c8573798e0b5cf7f11c82bbb70f/cffi-2.1.1-cp315-cp315-win_arm64.whl", hash = "sha256:27350daa11d4f10c540e6e89dada4c54feb7256ad03e9a4dc075ebad7ba360d1", size = 182935, upload-time = "2026-08-03T21:21:17.271Z" },
```

**Line-by-line explanation**

- **L33** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L34** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L35** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L36** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L37** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L38** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L39** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L40** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L41** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L42** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L43** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L44** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L45** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L46** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L47** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L48** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L49** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L50** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L51** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L52** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L53** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L54** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L55** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L56** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L57** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L58** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L59** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L60** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L61** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L62** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L63** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L64** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.

#### 13.29.3 L65–L96 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/d0/ef/5443574510a1207e6f6bc38ba6e1f1de36cb48fef07b2728bb896a21f430/cffi-2.1.1-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:c26608d2222fb1e94487e4a387d85f13eb55d5ed725cb25a0c589ac4ee60e7bc", size = 188464, upload-time = "2026-08-03T21:21:01.163Z" },
    { url = "https://files.pythonhosted.org/packages/7e/ae/a56fa8c4686ad50e148fcbc8d3ae0d03915ff5c30d795058988c24118cef/cffi-2.1.1-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:4be96343e422f2dfcd12ab5c9f5aebe03f82f737c6bffeca6830b3875cb44aab", size = 188262, upload-time = "2026-08-03T21:21:02.382Z" },
    { url = "https://files.pythonhosted.org/packages/53/b2/6187f46f2912276a3ae284076109cc5c8680482f11f766ccf26db4a86427/cffi-2.1.1-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:937c0052c05a31ca1daf18de3158eed4dbfcb9cc107adbea227728d647be701e", size = 223779, upload-time = "2026-08-03T21:21:03.553Z" },
    { url = "https://files.pythonhosted.org/packages/8a/f6/c3ad28bd19f77047a03084424fbd4cbe997303267c14423737324be0385d/cffi-2.1.1-cp315-cp315t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:df423d40ee8654634421812bc3b196da3f9bd7d32929da813f8394c4348a5358", size = 211520, upload-time = "2026-08-03T21:21:04.863Z" },
    { url = "https://files.pythonhosted.org/packages/a0/cd/ccac9013a5bd9fd764de118674ab9c805b5ca10c19270d90ee273f8b2240/cffi-2.1.1-cp315-cp315t-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:a730a083190634c65cca36ba5f489531576ebd79bcd5c8e172130f6453127231", size = 210673, upload-time = "2026-08-03T21:21:06.223Z" },
    { url = "https://files.pythonhosted.org/packages/52/86/2976131c639aead931c5bee5aba67e4b09fbeb8018b6f282f70803f923a7/cffi-2.1.1-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:363e05fa78e15116c3c32c210ee36884fd6b9afa6d440e47112c3bd511d64cb6", size = 223835, upload-time = "2026-08-03T21:21:07.539Z" },
    { url = "https://files.pythonhosted.org/packages/ac/0c/33a7aeab2f9c76918c52e084beb39c570db3588133412929e8ec06fab90b/cffi-2.1.1-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:770de9db11e84213beec501cfcaa013b019820ca881e03344dea5844f7876d94", size = 226705, upload-time = "2026-08-03T21:21:08.774Z" },
    { url = "https://files.pythonhosted.org/packages/e3/26/2cde30fdde421130bfc18f70395731a6e6b2053c6a1978a5258ff04e72fa/cffi-2.1.1-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:7da0c5eff80f0197f3b3d1232ec5a682a9325f4ae9016a78f5f5ca35f9ced1f5", size = 225539, upload-time = "2026-08-03T21:21:09.911Z" },
    { url = "https://files.pythonhosted.org/packages/6d/cd/a361394c94b2129d604bb846f624a8e88255a3ee33129c434a00d715e64f/cffi-2.1.1-cp315-cp315t-win32.whl", hash = "sha256:06c72bb76605a4b0cd0aad6930b69d4baf7dd5d806cfc409b824191099700e66", size = 182707, upload-time = "2026-08-03T21:21:11.226Z" },
    { url = "https://files.pythonhosted.org/packages/9b/b5/ba2b299993c26577d529b6ae29841f9e15b9fcf004d65f423f4fcf94ade9/cffi-2.1.1-cp315-cp315t-win_amd64.whl", hash = "sha256:d9c275eaacd24aa73f94ffd6de08fc3f932424d8b6c376f4bed7cde376fe7bc3", size = 193772, upload-time = "2026-08-03T21:21:12.39Z" },
    { url = "https://files.pythonhosted.org/packages/aa/29/35e016098c814cd93de9cd320c66b5bfba14dc6ecedd3cb518fa7c408c69/cffi-2.1.1-cp315-cp315t-win_arm64.whl", hash = "sha256:d18e5ac0f2f03f4f518d3e23db0f0cad7faa1da8620e9c09461d443bbf6e6692", size = 186360, upload-time = "2026-08-03T21:21:13.636Z" },
]

[[package]]
name = "cryptography"
version = "50.0.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "cffi", marker = "platform_python_implementation != 'PyPy'" },
]
sdist = { url = "https://files.pythonhosted.org/packages/9d/af/182eb91b0df3fe75c4d9f26fe70684569566745f6ba7e5c9c73a862c5252/cryptography-50.0.2.tar.gz", hash = "sha256:7b46165bb56eb4704e2eaaf86f3c940d19154535d9b0ca7d6d590b04060e00d5", size = 880623, upload-time = "2026-09-30T15:30:04.884Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/e5/56/d194340cc4a57535e82e1bee9e89667ac4b7c13b5d3f59686deae3094dd5/cryptography-50.0.2-cp311-abi3-macosx_11_0_arm64.whl", hash = "sha256:fa8f5efb344d6908a1ce62f4a24e2e5780f825d6f53f5f50ec5ffacac72936cb", size = 3914904, upload-time = "2026-09-30T14:43:44.339Z" },
    { url = "https://files.pythonhosted.org/packages/d9/69/c9bd862c3bf43d6399c433caf002df16e2dffd4be49bdf515cda38038711/cryptography-50.0.2-cp311-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:79def8d059362e7831389ed3be0ecdf58a89386e1271e35dd9f5af84e81bffd0", size = 4731146, upload-time = "2026-09-30T14:43:47.113Z" },
    { url = "https://files.pythonhosted.org/packages/21/69/64cef1f702bf6657e0cc186ed1a2891d50d29fb41586b254e1c07adea261/cryptography-50.0.2-cp311-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:630ebfea3bf689d075f82316324ff7433dc447fe6bc1bfc76524b74b4a9567d2", size = 4719841, upload-time = "2026-09-30T14:43:49.01Z" },
    { url = "https://files.pythonhosted.org/packages/38/6b/61a3f8d8c5e1e49a6cddccafc4015cc1c0021360ab0acb4080e7a423644a/cryptography-50.0.2-cp311-abi3-manylinux_2_28_aarch64.whl", hash = "sha256:f9f6143a8c75945eb960d9eb98905a441394abfa24afaae239d514ffb2586480", size = 4738340, upload-time = "2026-09-30T14:43:50.932Z" },
    { url = "https://files.pythonhosted.org/packages/7b/2e/7212ca32fd43dc91f2f41db20160b268098874b4c9a0e7be94d6835f5b2e/cryptography-50.0.2-cp311-abi3-manylinux_2_28_ppc64le.whl", hash = "sha256:a582ab2ae1d34f67112cadc86702774c9ea4374df6bca6afe672817203c99134", size = 5367029, upload-time = "2026-09-30T14:43:52.911Z" },
    { url = "https://files.pythonhosted.org/packages/1a/f1/b474e930c4d910328780e3940da76f5aa5cbc48ce1fc14e44d239d9ea9db/cryptography-50.0.2-cp311-abi3-manylinux_2_28_x86_64.whl", hash = "sha256:4061c0079120205fb760c58acab6443e217307dcf05e3702cf970e0689972856", size = 4753050, upload-time = "2026-09-30T14:43:55.272Z" },
    { url = "https://files.pythonhosted.org/packages/7c/52/9af10e80ac16b0fcc2123f9cbd5e7afbd0fd5075bb7a607c592258a39cda/cryptography-50.0.2-cp311-abi3-manylinux_2_31_armv7l.whl", hash = "sha256:ac9ed99d81760c62fe89d5f0815cdfa1ba9a35141cf30f1c2d044f04b4803d2e", size = 4376724, upload-time = "2026-09-30T14:43:57.24Z" },
    { url = "https://files.pythonhosted.org/packages/71/37/6202e488cc1eb625ea110c292c6bda92823176e023f427d8d5660ce8d632/cryptography-50.0.2-cp311-abi3-manylinux_2_34_aarch64.whl", hash = "sha256:87e9ce85beb6b328ba370cc6e6aea483c92617b4c95b1d33a49297eb662bfb04", size = 4737859, upload-time = "2026-09-30T14:43:59.541Z" },
    { url = "https://files.pythonhosted.org/packages/8f/30/e86d7d518489b0ae2497091a35287abcb1a2ce4037837a34afbe9b1d6964/cryptography-50.0.2-cp311-abi3-manylinux_2_34_ppc64le.whl", hash = "sha256:f265528741e048bce55c3463ed721fb0aa45a5888d8add8cfeccb3035451bbdc", size = 5324103, upload-time = "2026-09-30T14:44:01.901Z" },
    { url = "https://files.pythonhosted.org/packages/d3/69/2c833a049475e0a3444e94c7d0aca0aa51d166374a449b09e92ac98138de/cryptography-50.0.2-cp311-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:9dab55f57c74c3cad24c323bacbbd04be4705ba6eb0d92e920b1fc4837ed5079", size = 4752576, upload-time = "2026-09-30T14:44:04.545Z" },
```

**Line-by-line explanation**

- **L65** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L66** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L67** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L68** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L69** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L70** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L71** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L72** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L73** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L74** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L75** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L76** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L78** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L79** — Name this locked distribution cryptography. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L80** — Pin cryptography to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L81** — Record the package registry from which cryptography is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L82** — Begin cryptography dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L83** — Reference the dependency named cffi. marker is a condition limiting when the dependency is needed; here the referenced condition distinguishes Python implementations such as PyPy. It is needed by cryptography; dependency resolution also follows that package's own dependency references.
- **L84** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L85** — Record the source archive for cryptography: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L86** — Begin the list of prebuilt wheel artifacts available for cryptography across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L87** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L88** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L89** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L90** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L91** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L92** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L93** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L94** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L95** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L96** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.

#### 13.29.4 L97–L128 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/6c/5d/906970b83bbfc1f5bbfb677a143c181f2801f23b6a7204a3b47c42c97e65/cryptography-50.0.2-cp311-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:25784ce8b9621c90c643efb9e1e2162ab3b0224cae446ad5e70e7fcb1ce18b51", size = 4870819, upload-time = "2026-09-30T14:44:06.884Z" },
    { url = "https://files.pythonhosted.org/packages/68/e3/f2298d3bb55e0c4a91841ec4d01b3f020ba8c5fbf15ccdcc6dcf03f97025/cryptography-50.0.2-cp311-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:85d0d9a31b9098e98534226d5686b47264b95e62ce459dc2e62fdfc809f9fe93", size = 5030152, upload-time = "2026-09-30T14:44:09.443Z" },
    { url = "https://files.pythonhosted.org/packages/9a/4f/adfc442765721292fff86d314ce385d3249d22db42295c0dd057727b60f3/cryptography-50.0.2-cp311-abi3-win_amd64.whl", hash = "sha256:7afa5a6602a9f29af1f3a2965f831bae7c9d5d597b7cbb716d41ab3b7d89879c", size = 3824692, upload-time = "2026-09-30T14:44:11.671Z" },
    { url = "https://files.pythonhosted.org/packages/ce/cb/52eb3770c0d0be2702a98c6e96065ddc0a2877cf0845aa9c23397c142cd4/cryptography-50.0.2-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:f785f6161f202ab04d8ca194158968798e480ca058943907972da5f12e2881e8", size = 3892731, upload-time = "2026-09-30T14:44:13.485Z" },
    { url = "https://files.pythonhosted.org/packages/19/8e/aa1fc533d4546b127b45de8aa024eb5933d23eff9debfe25931e56861095/cryptography-50.0.2-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:0ecbc5652bdb6fc9eaf89a7d196e20941adfe812f43bc4ca05d9150496821047", size = 4710431, upload-time = "2026-09-30T14:44:15.427Z" },
    { url = "https://files.pythonhosted.org/packages/6a/64/72bc3f75176e7e406b748a3e3830432b8c51297b38368713df04dc04898a/cryptography-50.0.2-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:ab50ee449bf968271e820086f10a33d101dd060370abc10bcd22279be2656539", size = 4694824, upload-time = "2026-09-30T14:44:17.69Z" },
    { url = "https://files.pythonhosted.org/packages/4e/c6/62c77550edfa5ca3f14bf44a1e6739b9fa09d6e998a11d97ed8213bccc98/cryptography-50.0.2-cp314-cp314t-manylinux_2_28_aarch64.whl", hash = "sha256:a9f7355e6fab51f6c369b86fb7571cffa05edee2c2121e0380a37fb9ac1cd5c1", size = 4716967, upload-time = "2026-09-30T14:44:19.661Z" },
    { url = "https://files.pythonhosted.org/packages/f4/37/cce70f150c432914460157a6ecc161752e053aa5ec0ef3b3f7dc6e31039a/cryptography-50.0.2-cp314-cp314t-manylinux_2_28_ppc64le.whl", hash = "sha256:94e5e9f108ee10471288214d3d233fbfbb492840a8457eb85178d643ddeb32c7", size = 5328676, upload-time = "2026-09-30T14:44:21.744Z" },
    { url = "https://files.pythonhosted.org/packages/aa/9a/6f2f0304d634ceafdeaf23e84537336664ac419b5d07611675c2ad3f6b7a/cryptography-50.0.2-cp314-cp314t-manylinux_2_28_x86_64.whl", hash = "sha256:241449bf940a5d27309bd317e6f9a2af6932113818bb2b8f5c59ddc7ef16da18", size = 4727698, upload-time = "2026-09-30T14:44:24.178Z" },
    { url = "https://files.pythonhosted.org/packages/1d/de/66bcf9244d118663b2e1aaded8990f4640e3d7b7411870a5765f252074d2/cryptography-50.0.2-cp314-cp314t-manylinux_2_31_armv7l.whl", hash = "sha256:d8947001be83df1394050758ce0e745dd74fb134eef0a4b5124208dfc3a68c37", size = 4354821, upload-time = "2026-09-30T14:44:26.263Z" },
    { url = "https://files.pythonhosted.org/packages/bd/e6/db28a28c7b6c676addce89136de3d8db49ea825a8c863472e36e42ead4ad/cryptography-50.0.2-cp314-cp314t-manylinux_2_34_aarch64.whl", hash = "sha256:4a20ce1e5cb4284a86692fdcba7cb8754185c6b2e5c56fcef3751cf451d3cdc2", size = 4716748, upload-time = "2026-09-30T14:44:28.447Z" },
    { url = "https://files.pythonhosted.org/packages/30/96/01546c7f69ea0e2ab790a2e4f0934a4052fb9b388147fbf83c2fd72f1e57/cryptography-50.0.2-cp314-cp314t-manylinux_2_34_ppc64le.whl", hash = "sha256:84f964e537f916e2cc85199e5a88742e964939b575ac8598b3f9d6cc416cdaf1", size = 5285085, upload-time = "2026-09-30T14:44:30.704Z" },
    { url = "https://files.pythonhosted.org/packages/6c/01/03263395f74d50b071e9e66daace3f8bef80493e5d410726f2ba8554736b/cryptography-50.0.2-cp314-cp314t-manylinux_2_34_x86_64.whl", hash = "sha256:828d49b0ff5a0e3975865571c5d91dbbdd0d38d8289b249a163e9425413a5e05", size = 4727268, upload-time = "2026-09-30T14:44:32.92Z" },
    { url = "https://files.pythonhosted.org/packages/eb/94/2bfe8f29ec0cc9c0d99359c4161adf32858e4934b72c6d100d2ac0bbe962/cryptography-50.0.2-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:deb9fde5c60e437ee4821bc9bc39ff31b42135c27e1dc61ef0a629389c1de62e", size = 4849503, upload-time = "2026-09-30T14:44:34.969Z" },
    { url = "https://files.pythonhosted.org/packages/54/44/e80651ecbf0e42b62e2bb5f5768916e07eea72e1297338956a61df361f88/cryptography-50.0.2-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:8c71ba2cd31fc93748c38e1b613200ff1c2665cbfd5341fe3a61cfde35a1430e", size = 5004057, upload-time = "2026-09-30T14:44:37.064Z" },
    { url = "https://files.pythonhosted.org/packages/f8/cc/1d33befb3cd7ea7e77d2d73f43f2066471da1b21f24a6156efcaabf6d2e8/cryptography-50.0.2-cp314-cp314t-win_amd64.whl", hash = "sha256:78198641e5be9521beea5aa782bb551a58068d10e6eb04c9c680c1b69f2e7d45", size = 3795868, upload-time = "2026-09-30T14:44:39.71Z" },
    { url = "https://files.pythonhosted.org/packages/2d/49/93f6a6e7a87c9aa68d44d3e1cdb5fe8f60c90d5d2f46acae9a56892816b8/cryptography-50.0.2-cp315-abi3.abi3t-macosx_11_0_arm64.whl", hash = "sha256:edc3342adf8f697fc5f59c887a304356f147b397809440ed64e2fa6af2f50f37", size = 4133708, upload-time = "2026-09-30T14:44:41.807Z" },
    { url = "https://files.pythonhosted.org/packages/8c/75/32ac2a56243d778805c16ca6a32b8f74fb757df7e28d7ecb560afafb59cf/cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:d370b8d1dfcdf7130178137f6fbee6140774a1acc6cacefc4b42643ec11d0a3a", size = 4956267, upload-time = "2026-09-30T14:44:43.693Z" },
    { url = "https://files.pythonhosted.org/packages/aa/a4/2c8d734e43d97f0842ee9f1b7b4bfb3d0cf5e19edebf43c2afe6675c2320/cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:f2f9bd7f90c64fe89253f0a2c05e3c4856072660429ce8831b4235bf29403a67", size = 4966465, upload-time = "2026-09-30T14:44:45.769Z" },
    { url = "https://files.pythonhosted.org/packages/c2/58/ee288c829a6f41f6235ae9dd33d82fd19b45442b65b4c8a3da36963d9f7a/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_28_aarch64.whl", hash = "sha256:e275096ea1e60cc595cda2836fd4a6c725d1125108b868be17f53684d164e2cc", size = 4959356, upload-time = "2026-09-30T14:44:48.211Z" },
    { url = "https://files.pythonhosted.org/packages/92/20/9ded6d51ddd9897f6b6e81fb9ebea7951d7cc5d6c890b0ed8abf77a51a80/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_28_ppc64le.whl", hash = "sha256:b13478603dcd0a2479ff8e87e2c19a7d525734686fe3c49542472293a204212d", size = 5548822, upload-time = "2026-09-30T14:44:50.86Z" },
    { url = "https://files.pythonhosted.org/packages/02/a8/8df951850d6b31d2a00218f19e2b3f999523437ed7a819df7fa427942fca/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_28_x86_64.whl", hash = "sha256:58a0c478eeca76fe5e07993c5a0703def34a6dc6a0cda4f5564639b33112ffe7", size = 5001199, upload-time = "2026-09-30T14:44:53.379Z" },
    { url = "https://files.pythonhosted.org/packages/8b/f9/36b3022218ce75b7cdf068fb95f809f9bd0d820e4955ef43b90c255cc7ac/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_31_armv7l.whl", hash = "sha256:d38cdff612d06fa6a32840d5e1b1f7a27cee4a349aa9085d94a67789d6bfd408", size = 4629333, upload-time = "2026-09-30T14:44:55.635Z" },
    { url = "https://files.pythonhosted.org/packages/8c/72/20f99a219f6af47cdd1cbd978c243b92d71496e168a746138af44ded4f29/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_34_aarch64.whl", hash = "sha256:fdd28f912fccfec1846a94e2e1e8f9b0012f557f0c46fe4f3eb0d7a87afcf90b", size = 4958822, upload-time = "2026-09-30T14:44:59.639Z" },
    { url = "https://files.pythonhosted.org/packages/f2/20/196f112617fb08eb4d608a2a6c422373d46f9cc2857f38fc0667033c0899/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_34_ppc64le.whl", hash = "sha256:cbc8738fd8526d80f35cb3a40d41f41a2e7030bb3b18b09a6778ef63d291c2fd", size = 5506351, upload-time = "2026-09-30T14:45:02.267Z" },
    { url = "https://files.pythonhosted.org/packages/24/95/83378121ef3eaaaf71d4b781577ff794acb39b9e1b87a3f156898c8497ed/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_34_x86_64.whl", hash = "sha256:e105ab60406787da31fccc883fc0f733af1efd78f0136a4599692c4083a73d0c", size = 5000859, upload-time = "2026-09-30T14:45:05.009Z" },
    { url = "https://files.pythonhosted.org/packages/22/f7/70fd7ae4d1dbfa7ba29b02e1b9068771519a86027756510b700ce81086a8/cryptography-50.0.2-cp315-abi3.abi3t-musllinux_1_2_aarch64.whl", hash = "sha256:6f8700550aa1474a91e5dc07049c46f98b423b5b1ddd0483e0b51362eeeaf5be", size = 5092151, upload-time = "2026-09-30T15:29:15.932Z" },
    { url = "https://files.pythonhosted.org/packages/d4/be/688367b74de86984bd58d8efacfc7c9e68b89a6a22ced0fb4f38db50254a/cryptography-50.0.2-cp315-abi3.abi3t-musllinux_1_2_x86_64.whl", hash = "sha256:c71be1cbfa5cd9a41ee452acf1eccd82b2c05950358b106ec8ceb83411d1a020", size = 5286120, upload-time = "2026-09-30T15:29:18.309Z" },
    { url = "https://files.pythonhosted.org/packages/39/d1/55f8a3f2ef5d1529e16835ef10cf0fe3d559ce237b46dddc440c0bba3649/cryptography-50.0.2-cp315-abi3.abi3t-win_amd64.whl", hash = "sha256:c423ab384a46c4dff7217b2ea5ba2e11cffdeab6441acd04cf65a369caf0366c", size = 4111557, upload-time = "2026-09-30T15:29:20.155Z" },
    { url = "https://files.pythonhosted.org/packages/23/ad/ac987755d00e1e64273760228d2635ae38dae2be83e3c6e0d3289d91dec3/cryptography-50.0.2-cp39-abi3-macosx_11_0_arm64.whl", hash = "sha256:0ec5f09541743261e66e291b4a0cbf0fb2997aeaab6d9e9c740b9dba1b58d1c2", size = 3943588, upload-time = "2026-09-30T15:29:22.265Z" },
    { url = "https://files.pythonhosted.org/packages/d5/8d/6d585339bedf85d45044c85d8412dac53f2bb6f918e8b7777efba1787844/cryptography-50.0.2-cp39-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:c5e67125c7dca78d199ec4e116aa93dbb83494808ecbb8211a2cb09b1bf41dbd", size = 4756166, upload-time = "2026-09-30T15:29:24.58Z" },
    { url = "https://files.pythonhosted.org/packages/bf/f1/1c1f6874e8550cfddd4b688ceb38cefb6ed15ceed224d56f133f3d88c214/cryptography-50.0.2-cp39-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:ee247f5c245c9a2fe7c8e2214e295918838e44e00a45a6718451e4004219e767", size = 4749145, upload-time = "2026-09-30T15:29:26.807Z" },
```

**Line-by-line explanation**

- **L97** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L98** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L99** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L100** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L101** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L102** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L103** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L104** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L105** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L106** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L107** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L108** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L109** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L110** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L111** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L112** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L113** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L114** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L115** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L116** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L117** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L118** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L119** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L120** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L121** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L122** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L123** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L124** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L125** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L126** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L127** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L128** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.

#### 13.29.5 L129–L160 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/c1/63/61b15dc1a8de03fe0adbe3fd7608b3ad5c73bf50993bbcb1faaa930afe33/cryptography-50.0.2-cp39-abi3-manylinux_2_28_aarch64.whl", hash = "sha256:dfe9763530994147d9af1def057a5b9658b00e8f8fe8743d144d1e0911c2e454", size = 4763638, upload-time = "2026-09-30T15:29:28.588Z" },
    { url = "https://files.pythonhosted.org/packages/fc/35/b345bdfa40c9126df1a9d33236aa98418367931b8725f84fc3ae2b98dc59/cryptography-50.0.2-cp39-abi3-manylinux_2_28_ppc64le.whl", hash = "sha256:58ddb5a8e3179d12f19e4ea34d2d32e9d63a4baa142c875c1eb59f41b7243acd", size = 5382217, upload-time = "2026-09-30T15:29:30.589Z" },
    { url = "https://files.pythonhosted.org/packages/4f/87/ef344a9e616871f2519c22d6afcda79ddd5d35e9592d95eb6e677608d055/cryptography-50.0.2-cp39-abi3-manylinux_2_28_x86_64.whl", hash = "sha256:f21e8a22c8605750c7af886bab299a363721264061b4ac0a30efb73cfd58efc5", size = 4781387, upload-time = "2026-09-30T15:29:32.605Z" },
    { url = "https://files.pythonhosted.org/packages/90/5b/f2fdb13cd0b96f6f932c8627bb292a45f11c64d21620a8e120aee9a3b848/cryptography-50.0.2-cp39-abi3-manylinux_2_31_armv7l.whl", hash = "sha256:9c8402a82ea0dc4ceeab793db05f0fafa8ca139ca34fcde5df0f596103c74107", size = 4403790, upload-time = "2026-09-30T15:29:34.374Z" },
    { url = "https://files.pythonhosted.org/packages/bc/ce/7e4f662b1e3c393513569e402cfc85ac7da0bd3d5435e122a3140219eb2d/cryptography-50.0.2-cp39-abi3-manylinux_2_34_aarch64.whl", hash = "sha256:0ddc924c04591c2811ca024d62ecad4f7f6f08af8939c211438f48a16bd23602", size = 4764319, upload-time = "2026-09-30T15:29:36.149Z" },
    { url = "https://files.pythonhosted.org/packages/3c/3f/86ff33ce34cc0de6847fb96e035a1a760d81652e38643f617c02ad32ef7a/cryptography-50.0.2-cp39-abi3-manylinux_2_34_ppc64le.whl", hash = "sha256:a6557e5f38e065ca9fbdaf7cfc7435ecb1d113aa81a022d1b51921ee7432e227", size = 5338560, upload-time = "2026-09-30T15:29:39.053Z" },
    { url = "https://files.pythonhosted.org/packages/40/cf/6b5c8e2fd9202d98988ab7cb5cc5c991704c4ad55f492ff408e4969f83f1/cryptography-50.0.2-cp39-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:1981f1db4630889b9ef7803fadef12b056f428cb6b85c27ba57b774793b6093c", size = 4780973, upload-time = "2026-09-30T15:29:41.251Z" },
    { url = "https://files.pythonhosted.org/packages/10/bf/8d6ebc7dded797bd0f0160d52188021211f011a2b164ef0ae1dac4587465/cryptography-50.0.2-cp39-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:7a8701d6b584d76e909e3d305b7d126b41439876a5aaf76cddc67fc230eafa2e", size = 4897738, upload-time = "2026-09-30T15:29:43.106Z" },
    { url = "https://files.pythonhosted.org/packages/d4/aa/f3f6e0de7e6253b8baa8b2d8fb9d50924fa75cee3d4624bd4bc1208ee923/cryptography-50.0.2-cp39-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:ce47f66801c20ec6c6632453bb5960fe38939e9306970b48b3a5a26de7745d94", size = 5058280, upload-time = "2026-09-30T15:29:44.827Z" },
    { url = "https://files.pythonhosted.org/packages/f6/b6/a1faf3a27ae9405fb34b1713cc73b2d8a26b04d5c561578fa2e6ef3e5bb9/cryptography-50.0.2-cp39-abi3-win_amd64.whl", hash = "sha256:4e81d95e5bafc2d6e34e4bed780e53e4d5b9a2f928573428aa4d35fbec1eb0de", size = 3854095, upload-time = "2026-09-30T15:29:46.782Z" },
]

[[package]]
name = "numpy"
version = "2.5.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/95/b0/c7453d0b6e2073c3264468b106ee1563750cecc910965e67357e3698c83e/numpy-2.5.4.tar.gz", hash = "sha256:9a94cf751c9ad8ebaa835bcd3d40dacf8534ad086b88c38029b65123c7999d2a", size = 20866315, upload-time = "2026-10-10T20:05:31.422Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/67/14/1c3ee0118a8fce08565a5d8482631608426a33af10a01077fada5dc7c119/numpy-2.5.4-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:2377da2dd3ba2c1200956acbab2a358c83b8e1f8531191672d1cd6ad83250d53", size = 16997729, upload-time = "2026-10-10T20:03:09.291Z" },
    { url = "https://files.pythonhosted.org/packages/83/8c/b0ea9477fb1f0d4484bbc5cba21678cc9969704d8d7f3f158d1db35f8e14/numpy-2.5.4-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:7415db95818b39ec475a5eea54d9e3b6bc83e3912158e46da3438cdce399804d", size = 12009826, upload-time = "2026-10-10T20:03:11.946Z" },
    { url = "https://files.pythonhosted.org/packages/e2/84/6a3d75b3ba3dfe84ac0053450753d1e6d250a8bf80f66474cc46d1fb643f/numpy-2.5.4-cp313-cp313-macosx_14_0_arm64.whl", hash = "sha256:6d6a71b9d9a97c03633aa12565ef2825ffa036cc1d99cfd50dacf0f128af4fe2", size = 5445803, upload-time = "2026-10-10T20:03:14.329Z" },
    { url = "https://files.pythonhosted.org/packages/61/18/bb993f267ca20b376e07092a16793a5b31ed3138751e9ba480011a14d742/numpy-2.5.4-cp313-cp313-macosx_14_0_x86_64.whl", hash = "sha256:d8200f16437b289a5bb927c6e184eccc3e8389bc0070fea4cd5b9e13c1757959", size = 6786220, upload-time = "2026-10-10T20:03:16.602Z" },
    { url = "https://files.pythonhosted.org/packages/db/b6/135bb0953b61dc21c6cafa14b424ae666944e4899cf140e00c2b322a1a45/numpy-2.5.4-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:1c2e71b04c6cad90026e544501bbe0ab9290fa8a4d845e7e8c0d124fb429c988", size = 15689178, upload-time = "2026-10-10T20:03:18.721Z" },
    { url = "https://files.pythonhosted.org/packages/da/24/3bd070f3269dc609d8f26b2643f62ef91bb415841c0b294805aaf7fe06da/numpy-2.5.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:6ffa07666f8da0eef81d149934a626d0d95fbd6838432a33e66245423a9062c0", size = 16718044, upload-time = "2026-10-10T20:03:21.386Z" },
    { url = "https://files.pythonhosted.org/packages/c7/8e/9d15bd356b0a019c965312b1a3c6a727cac4cae5bc40045fbc12ce4cff9c/numpy-2.5.4-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:2fa3328f784fc8277fc48026f6cad516f5c561c5d8e2e39b3c9e0c8f23223b34", size = 17048364, upload-time = "2026-10-10T20:03:24.468Z" },
    { url = "https://files.pythonhosted.org/packages/dc/fe/9d5b560db964f15871885f2250795d15945f8699e17ef90c0c2ff4c875b2/numpy-2.5.4-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:b86966fbe4ad7de710422175572bcdc75fdedadfb54bc6fab7deabccddd7780b", size = 18474904, upload-time = "2026-10-10T20:03:27.895Z" },
    { url = "https://files.pythonhosted.org/packages/e9/98/d27552990f1bd611ef3e7466adadc78312ea2df63b83aad47fdc3d3ca8df/numpy-2.5.4-cp313-cp313-win32.whl", hash = "sha256:5258bc06526964be5face2fc6f756857a3f24f21ec3e72ca131337a75b165d6c", size = 6134537, upload-time = "2026-10-10T20:03:30.511Z" },
    { url = "https://files.pythonhosted.org/packages/90/8c/140a40398a66b4471211be1affdb6ed24c486d581bd28d07b7f2fcb69540/numpy-2.5.4-cp313-cp313-win_amd64.whl", hash = "sha256:8b4d2fd2d34e5f8c9235ee787de5631a37a28402b15cb80814df973d2be54129", size = 12566113, upload-time = "2026-10-10T20:03:32.612Z" },
    { url = "https://files.pythonhosted.org/packages/34/52/01d205e5e8ccb27b2b0b141e801f22b830198c979111b0fa44771438d9a9/numpy-2.5.4-cp313-cp313-win_arm64.whl", hash = "sha256:bc39ac66a7a9a3fbd6134fda43136b60ffde99c8f4501e64e0d2b24da137babf", size = 10519523, upload-time = "2026-10-10T20:03:35.163Z" },
    { url = "https://files.pythonhosted.org/packages/99/ba/005cb5edd580d2f84d7ca3206b92dc17d4388e56e6f87ffe8f2762f83139/numpy-2.5.4-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:c668b2f0d651605b58892644b0e302c7157f7159544227758c896982ef384b18", size = 17005499, upload-time = "2026-10-10T20:03:37.961Z" },
    { url = "https://files.pythonhosted.org/packages/f3/49/fee7587c33ee35f7977f9051d7f2023d4e7246d62710c80f20c2361ea232/numpy-2.5.4-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:ffa6ce09a1c6a08e9667dd9c97aa0b14184e8d18f2a14b78b2a2328c9147f076", size = 12019666, upload-time = "2026-10-10T20:03:40.606Z" },
    { url = "https://files.pythonhosted.org/packages/d5/b2/c6ce165acffceb15a82c07b9cc77d391f86b3f379ba62911908ae5d34b91/numpy-2.5.4-cp314-cp314-macosx_14_0_arm64.whl", hash = "sha256:956555e0603a4d38019ae6925711cb9dc43195c076a928accf7ea5d50bddfe53", size = 5455617, upload-time = "2026-10-10T20:03:43.138Z" },
```

**Line-by-line explanation**

- **L129** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L130** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L131** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L132** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L133** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L134** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L135** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L136** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L137** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L138** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L139** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L141** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L142** — Name this locked distribution numpy. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L143** — Pin numpy to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L144** — Record the package registry from which numpy is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L145** — Record the source archive for numpy: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L146** — Begin the list of prebuilt wheel artifacts available for numpy across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L147** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_10\_13\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L148** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L149** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L150** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L151** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L152** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L153** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L154** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L155** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L156** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L157** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L158** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L159** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L160** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.

#### 13.29.6 L161–L192 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/77/7f/dd85ce260a669a89be06842cf355d7353a33e6cfbc590fb8ebb947d88dc9/numpy-2.5.4-cp314-cp314-macosx_14_0_x86_64.whl", hash = "sha256:2c2c4afffdeb7920e445028dd71eb932cac3e704792e964bc2a232426d4f1255", size = 6791932, upload-time = "2026-10-10T20:03:44.874Z" },
    { url = "https://files.pythonhosted.org/packages/63/d6/34b0a2b0741386a63025a65a2c09caaaaaad6d0ca95b66cd65c30dd7fcb5/numpy-2.5.4-cp314-cp314-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4054173604cd8658796053f1f3bc0befb68ec1c0762c57fdad61e199256a8617", size = 15710899, upload-time = "2026-10-10T20:03:46.839Z" },
    { url = "https://files.pythonhosted.org/packages/16/d5/928078d2b28f26829b138b4a6c3980045022fb409f570657a224ae60ef4e/numpy-2.5.4-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d549420b8858885cea8838a727842249218b9c1da24dd517e25c9c7a948310a3", size = 16721710, upload-time = "2026-10-10T20:03:49.489Z" },
    { url = "https://files.pythonhosted.org/packages/f9/cf/673fd1b8f4cd78eb6320e87ec4c90ac19c095644259e3749853a405c70f4/numpy-2.5.4-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:823874a507a84af050493b622affde94b6f7c3a0dc22cb2801381bc03b871c00", size = 17066182, upload-time = "2026-10-10T20:03:52.25Z" },
    { url = "https://files.pythonhosted.org/packages/f3/92/a77b5061b1b3e2643928c37976d79ee173e1b171ed158b7a3c61056b41bc/numpy-2.5.4-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:4e263278bfb5ee6409db8aedbc4cc32973b1b82bc1e8d3c668551d04d83a7e37", size = 18480315, upload-time = "2026-10-10T20:03:55.39Z" },
    { url = "https://files.pythonhosted.org/packages/bb/1d/1486ef3d3fb2279fd93c4c43c1bbbf1ca389a19816696684409f71babaab/numpy-2.5.4-cp314-cp314-win32.whl", hash = "sha256:cfd73180400042a7c532d30c5e287bdd03c59ff9ee1b4c0316af0539e29dfe23", size = 6185739, upload-time = "2026-10-10T20:03:58.186Z" },
    { url = "https://files.pythonhosted.org/packages/52/9a/e1e512ebc948d5b9dd33b08736760f0ebbed2848fd4eda1f553088a6dcee/numpy-2.5.4-cp314-cp314-win_amd64.whl", hash = "sha256:2ca144f15135b6212a5c47b1e2aeca6e412f102f95a2d5d88d8aec77eb255de3", size = 12703552, upload-time = "2026-10-10T20:04:00.28Z" },
    { url = "https://files.pythonhosted.org/packages/2c/05/de709a982d7bbcd688a3fad71f002e9ff80c2db39e03ee726609b610f1d1/numpy-2.5.4-cp314-cp314-win_arm64.whl", hash = "sha256:468397ba3c64427474706e5c9123fe266395496714dc684294eac75cd4930d1e", size = 10803901, upload-time = "2026-10-10T20:04:02.659Z" },
    { url = "https://files.pythonhosted.org/packages/13/34/083570ada3bb2a30fbe5d77c8c6fef9141144a15d33e6f793a67e9749ab8/numpy-2.5.4-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:1ef3aa6d7e29bb13677323114280b05acc57607fa2300e66432d665d5418a162", size = 12138695, upload-time = "2026-10-10T20:04:05.012Z" },
    { url = "https://files.pythonhosted.org/packages/94/06/1f9c24db48eef0c2d1207e3b11fffb0478e39dfd8c1e1be7476936885eed/numpy-2.5.4-cp314-cp314t-macosx_14_0_arm64.whl", hash = "sha256:98b053943e5a0474ec0da309d2cb9d3f18ea57f8a2067c2ab7b5f763d1068380", size = 5574615, upload-time = "2026-10-10T20:04:07.316Z" },
    { url = "https://files.pythonhosted.org/packages/da/0f/593fba2e1560e949123bc7d2fc48b5893d56e58cd4bd5a273d2fbf60b220/numpy-2.5.4-cp314-cp314t-macosx_14_0_x86_64.whl", hash = "sha256:b64a85f40e154983960a4167d4c1d57a50c7f109b3d3264a3a984154e90a8454", size = 6889383, upload-time = "2026-10-10T20:04:09.918Z" },
    { url = "https://files.pythonhosted.org/packages/eb/9f/b799dfdce4e05e80ed4bc815c71ff343a11533b2c0ffc221cae8538cda63/numpy-2.5.4-cp314-cp314t-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:a813ed7719bf45463c51779e6a98d0385fe905e48447526938a4b8337333d551", size = 15753763, upload-time = "2026-10-10T20:04:12.278Z" },
    { url = "https://files.pythonhosted.org/packages/34/88/16c5f12f86f5ad2817c4d103205131fc6c8acb3d1878af05a1a4f23ec859/numpy-2.5.4-cp314-cp314t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c9b80cdf5cedba0e90d93fa5f9a333c4d65bd545cd669b71bb97ce2b703c9d73", size = 16757212, upload-time = "2026-10-10T20:04:14.799Z" },
    { url = "https://files.pythonhosted.org/packages/ff/4f/a1fe40e18a898e6a5089f4f0d891f0a493eb0574d5b34458f0fbe5aa3e5c/numpy-2.5.4-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:2199ed071f460487c8db2c0e5c0b564494190edb4772fe80f9aad88b2604def5", size = 17116471, upload-time = "2026-10-10T20:04:17.58Z" },
    { url = "https://files.pythonhosted.org/packages/aa/46/e923a11c78e65c1722e7aaad817c06bd591324174b9d28ce5d31eee4d432/numpy-2.5.4-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:64f9c9878c1938476365e11ccfb6b770f3b9e5f045ccddc514235041e6959365", size = 18524063, upload-time = "2026-10-10T20:04:20.365Z" },
    { url = "https://files.pythonhosted.org/packages/5a/fa/84ab064514440c1f64a1b21088f2c82756defdd05e07c75ab233899565b2/numpy-2.5.4-cp314-cp314t-win32.whl", hash = "sha256:64d1c8ac28a4077cf987e0a71a7a0ef7e2df70722f07f0baa42dbb7eb6938647", size = 6340926, upload-time = "2026-10-10T20:04:22.865Z" },
    { url = "https://files.pythonhosted.org/packages/7e/7e/6cd886876f435b10685db9b9f7eeb70356f99e052116f4e5f11c5792c714/numpy-2.5.4-cp314-cp314t-win_amd64.whl", hash = "sha256:067374eb538c34c745436365cf7b0112595c1d326f21ce4ff340f61230239fbb", size = 12901584, upload-time = "2026-10-10T20:04:24.99Z" },
    { url = "https://files.pythonhosted.org/packages/38/1b/3c1684f6a06f7307f2335fca6e486cb162847fb97e91d65f8eb5cabad213/numpy-2.5.4-cp314-cp314t-win_arm64.whl", hash = "sha256:e94aef2c639da4a960ad0db8e06471208d8589974953d78b61d345b4eb99e394", size = 10891152, upload-time = "2026-10-10T20:04:27.52Z" },
    { url = "https://files.pythonhosted.org/packages/08/f4/3224deff3af2bef6bc0b175369698d8cb348f3d91d9bb0286cd5c9eae9e0/numpy-2.5.4-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:8dddfbee2e68d26d0d7d7d9cb247b1fd4409241cce32d815a11d97ec2cfde179", size = 17003231, upload-time = "2026-10-10T20:04:30.021Z" },
    { url = "https://files.pythonhosted.org/packages/be/75/fee0b8c6d94b44b2fdfae74f6a4ad5a138739589a8aebaec28ce4e713ed5/numpy-2.5.4-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:81e3420b27048b65eb14c3acf0c174a8cb0e023277716110347d2dcb26026dad", size = 12018300, upload-time = "2026-10-10T20:04:32.519Z" },
    { url = "https://files.pythonhosted.org/packages/47/c0/d0b335a499a04b65f532c3f034346ef390f81299060f928492dabc1e0272/numpy-2.5.4-cp315-cp315-macosx_14_0_arm64.whl", hash = "sha256:0b4724a19de67bea8cfc4970798efa78bcbbe2ac2613cfac16721a42d44de2a5", size = 5454250, upload-time = "2026-10-10T20:04:34.943Z" },
    { url = "https://files.pythonhosted.org/packages/5a/0e/461b3783c03d668052e6a21b01b673db6ffcb7831fd32d9aa5368c1cd426/numpy-2.5.4-cp315-cp315-macosx_14_0_x86_64.whl", hash = "sha256:2132418bf8dd124a427ca9e6a1daf9ee1a87185344c95119ceae868b99466da1", size = 6789644, upload-time = "2026-10-10T20:04:37.258Z" },
    { url = "https://files.pythonhosted.org/packages/b3/02/5dad269b02166965a7b4ca14adaddd75dbee0de42435bfecf561b84ba5a6/numpy-2.5.4-cp315-cp315-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:325518d4245b9e331387702aa58c2ce1dc4cdcbb41dfb4ccd5dcbc7e08db1266", size = 15704353, upload-time = "2026-10-10T20:04:39.616Z" },
    { url = "https://files.pythonhosted.org/packages/93/3a/01360c8036822ed9f7aa32189a77d1476567ec1e8e1383522389e4faac45/numpy-2.5.4-cp315-cp315-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:56733449d2544178beaa4545cee357370440cf056c197f9c7bfb19dbfdd0e86d", size = 16718648, upload-time = "2026-10-10T20:04:42.383Z" },
    { url = "https://files.pythonhosted.org/packages/7d/5c/b863a2c093c4d6f21a597fcaf24ead0835c09ab16a8312d5a5a8868af683/numpy-2.5.4-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:5ec3753760c1a6d8bb91200666e545c3a9728e6269dfb5d6ce02340996698aa3", size = 17059053, upload-time = "2026-10-10T20:04:44.976Z" },
    { url = "https://files.pythonhosted.org/packages/0a/60/ced4f57f9a1258a0af74f17cb0b0c2700b5c67cd6678823c803b263e4df3/numpy-2.5.4-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:b1185012870173de7ae33d370bd45b1cf5baee747ea4b97036b65f4e93016877", size = 18477406, upload-time = "2026-10-10T20:04:47.863Z" },
    { url = "https://files.pythonhosted.org/packages/f9/bd/0ef22dafaafcc7d4bb3ca26b8d2afbd55dedad8eaba99a8c864e1997456f/numpy-2.5.4-cp315-cp315-win32.whl", hash = "sha256:298eca75243f2cbbfdb460560b9fb2a1792a33cf2ab4286efd43d92e8d3df508", size = 6185133, upload-time = "2026-10-10T20:04:50.467Z" },
    { url = "https://files.pythonhosted.org/packages/50/bc/d2651b155ecc608a77e6f4d15495c11f14f19bb98f8bf0c5b0d38f86dda1/numpy-2.5.4-cp315-cp315-win_amd64.whl", hash = "sha256:332f3378fe077dd850e677ec01bdcc4f22368fb5d50ef10b2c79230b1bf5a592", size = 12703085, upload-time = "2026-10-10T20:04:52.63Z" },
    { url = "https://files.pythonhosted.org/packages/dc/d2/45e404f8abb26fb9eda12b94012936873e827b1be76f2ee7890be128312e/numpy-2.5.4-cp315-cp315-win_arm64.whl", hash = "sha256:d4cccbbc78717966f764cd3af4fb70276fa01fc7a2688af11c78901fa5c04f05", size = 10801451, upload-time = "2026-10-10T20:04:55.677Z" },
    { url = "https://files.pythonhosted.org/packages/c6/c3/2ae14e09cfdb67dc187a342e15308a21c15bf4d2071f8079e6aee5fe56dc/numpy-2.5.4-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:950ea81d57ef070665581b6e1b5f6a029306423cd1739c5b95fe78aa30db6b9d", size = 17097121, upload-time = "2026-10-10T20:04:58.403Z" },
    { url = "https://files.pythonhosted.org/packages/f5/cf/305ae624ef8a039414317224abe9ec9c2fe7ea3c2e1cf204d43ff6b2ffb9/numpy-2.5.4-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:c05ede731b03fb1b7591faca9389ade3267d2bddf1ad8882bb3f2cc5e101694f", size = 12135439, upload-time = "2026-10-10T20:05:01.65Z" },
    { url = "https://files.pythonhosted.org/packages/a9/a8/f75c63813aef95827bb2c0d13b12803016853056e8792c280058cdbfe783/numpy-2.5.4-cp315-cp315t-macosx_14_0_arm64.whl", hash = "sha256:5fbf7141bbfd63aea22f435c9062a032b9ea0082fe9845dad7f021d3f1234e71", size = 5571451, upload-time = "2026-10-10T20:05:04.135Z" },
```

**Line-by-line explanation**

- **L161** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L162** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L163** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L164** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L165** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L166** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L167** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L168** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L169** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L170** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L171** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L172** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L173** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L174** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L175** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L176** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L177** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L178** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L179** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L180** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L181** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L182** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L183** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L184** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L185** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L186** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L187** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L188** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L189** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L190** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L191** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L192** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.

#### 13.29.7 L193–L224 · File contents

```toml
    { url = "https://files.pythonhosted.org/packages/6f/0f/f17763f983868b5c49b4101ebd7e00760bd1769478a6bb6a8de6e085bbac/numpy-2.5.4-cp315-cp315t-macosx_14_0_x86_64.whl", hash = "sha256:3573cd22564692a5b899ec344e5d5b9cc4576f2985b96f22af3564ed54f2710f", size = 6883356, upload-time = "2026-10-10T20:05:06.249Z" },
    { url = "https://files.pythonhosted.org/packages/67/a7/8af04c5a79e047996cfa38854dcfbececdd0343a7c933a46fdd03ef6f5da/numpy-2.5.4-cp315-cp315t-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6c109eac9cd439193678f69d70733c1108487546ca8eafc107b510ae10c1aecd", size = 15750991, upload-time = "2026-10-10T20:05:08.376Z" },
    { url = "https://files.pythonhosted.org/packages/57/7a/648254290d0c504faa8f2d07aa206660c728802c781a6f3fc68ab7cb5d71/numpy-2.5.4-cp315-cp315t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:80d6ef6e8620eb2c2b4c4caad50b5935d6db3cde2d51581b55dcc79e14016d1d", size = 16757675, upload-time = "2026-10-10T20:05:11.393Z" },
    { url = "https://files.pythonhosted.org/packages/b8/fe/4a8c3cdb0c70400cfe4c5bec42d3099a5673802a95064614b33e07b82aa1/numpy-2.5.4-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:77045a4b175bbf5316ec08003880804336c78f92281a1b72222b274ea85ec5ac", size = 17113846, upload-time = "2026-10-10T20:05:14.49Z" },
    { url = "https://files.pythonhosted.org/packages/1b/7e/619692bb67778702c0e9eb2d468568a7573f4e269386ea61aed01ee4e557/numpy-2.5.4-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:0f02a46e49cfb6c73bdb7aea1c0d3461dbae9aba613542b65f657cd3d17b9fab", size = 18522915, upload-time = "2026-10-10T20:05:17.33Z" },
    { url = "https://files.pythonhosted.org/packages/b7/b5/4da41c328788f575838f97a098fe8ca691ebc6f6fd73ad4a262ee40b184d/numpy-2.5.4-cp315-cp315t-win32.whl", hash = "sha256:ad62a416ddcf863bf44bba76fbf6b53366ab0692e294f51cae4b5fbe0d246788", size = 6335804, upload-time = "2026-10-10T20:05:19.921Z" },
    { url = "https://files.pythonhosted.org/packages/98/94/6482ddfa3d312490cb9358f375bf2ad56427dbea8769187158e94d653753/numpy-2.5.4-cp315-cp315t-win_amd64.whl", hash = "sha256:38f47be9f74ab870d2633b5456ae519c43758a8d1fd05342f0ce4ecc034396ee", size = 12890095, upload-time = "2026-10-10T20:05:21.875Z" },
    { url = "https://files.pythonhosted.org/packages/48/7f/c2d1b436b6e7cfebac140c2579a298344b85f2991a2ce5c3615cefb29400/numpy-2.5.4-cp315-cp315t-win_arm64.whl", hash = "sha256:7a14a461d9340f1b46b8648578aed9cdb8b3b018a8fac6c1dde2c9192a01a87f", size = 10883718, upload-time = "2026-10-10T20:05:28.547Z" },
]

[[package]]
name = "pycairo"
version = "1.29.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/bb/5e/19ab2572981a996ce96b853a189d2dcced40506b67d9555a7568457abcf2/pycairo-1.29.2.tar.gz", hash = "sha256:3e69fff74fe64f5ba2dfa31f67c6bdf26413342574047437d2ac520d35e9a489", size = 666308, upload-time = "2026-10-04T19:11:03.81Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/03/e9/03a625a9da4f0f0f5cb9420b7e6419478363d27c91888d82717d38a224d2/pycairo-1.29.2-cp313-cp313-win32.whl", hash = "sha256:50c30f88fa12b722ac8f997b67f83f5ea8fad06bc1d6c33dbdab504eb9978e56", size = 751443, upload-time = "2026-10-04T19:11:35.895Z" },
    { url = "https://files.pythonhosted.org/packages/23/44/7f39568959f5b2997bb888728423aeab00617cf8844f8126ec9ddeee86c2/pycairo-1.29.2-cp313-cp313-win_amd64.whl", hash = "sha256:0b87aa05a50a2c8cf2489dffc1b12f88b6e2fe384075f8c799367625081ca3cd", size = 845293, upload-time = "2026-10-04T19:11:37.541Z" },
    { url = "https://files.pythonhosted.org/packages/8f/90/83ebe0ae1d66378306085c505e7bf7abd0060714695e303877c800ff6d5c/pycairo-1.29.2-cp313-cp313-win_arm64.whl", hash = "sha256:806cd0f1266776fb6e881ce322569f0439993d66df0eeb8a255b1316f947acd0", size = 694636, upload-time = "2026-10-04T19:11:39.185Z" },
    { url = "https://files.pythonhosted.org/packages/53/d4/48e4b327563beae41c5eabea70c4b8b9aec790361dec02c338d4e8e2ac21/pycairo-1.29.2-cp314-cp314-win32.whl", hash = "sha256:98360270afaa909bcc1769f299160123322da29d2a7310763b0ddc16e624d5c6", size = 767785, upload-time = "2026-10-04T19:11:43.794Z" },
    { url = "https://files.pythonhosted.org/packages/42/bf/9d9eb2d0780440b1b5fe916e6a3abfa11e05f750b0ad643987cb9c0761d2/pycairo-1.29.2-cp314-cp314-win_amd64.whl", hash = "sha256:786373ba1bd78fbdec02cb1c99254eef12438bf942dd13534fe61b948becb527", size = 872750, upload-time = "2026-10-04T19:11:45.545Z" },
    { url = "https://files.pythonhosted.org/packages/78/36/f785d5a974809f36247ee56d15ca135433d1bf3c2adf1eb8fd66150b6a5e/pycairo-1.29.2-cp314-cp314-win_arm64.whl", hash = "sha256:9bb09bca782b5e21a4beb698075b5504f234af0597920f0c0439979226a76182", size = 720245, upload-time = "2026-10-04T19:11:47.69Z" },
    { url = "https://files.pythonhosted.org/packages/4f/74/c751bab17d770a3092d79b111281a7dca420b1490dd6e6f5408faab884ee/pycairo-1.29.2-cp314-cp314t-win_amd64.whl", hash = "sha256:bc9e26b7e9577d3655509766275653aa945f101fb28c197496facf8c9ba90321", size = 875205, upload-time = "2026-10-04T19:11:40.692Z" },
    { url = "https://files.pythonhosted.org/packages/b8/61/2d6f8361ba8497bb23bbb8ec8b91959b2e71366a3af2830c5a758663eabd/pycairo-1.29.2-cp314-cp314t-win_arm64.whl", hash = "sha256:29e3389c0b6d3dafda1b2360a8938790c2c7b6971b78e109a565c1cb91f8ae9a", size = 721982, upload-time = "2026-10-04T19:11:42.146Z" },
    { url = "https://files.pythonhosted.org/packages/92/05/427798a6722ee60ff9e1dbde0d6b67d56bdf4362c48c3239cf790804359e/pycairo-1.29.2-cp315-cp315-win_amd64.whl", hash = "sha256:c5dfa99afdde95b82325f240d144008a6b5be99405e74070540a1b7a857eb2a7", size = 872704, upload-time = "2026-10-04T19:11:53.589Z" },
    { url = "https://files.pythonhosted.org/packages/5e/58/708d622971b11215d113a27b8a3ca21815383ff2441eac8922b03a22aa0a/pycairo-1.29.2-cp315-cp315-win_arm64.whl", hash = "sha256:6b0410280b82bf60a84185392f720c099d71524dd7983f93d9abe18c8b2cd3a6", size = 720251, upload-time = "2026-10-04T19:11:55.606Z" },
    { url = "https://files.pythonhosted.org/packages/a9/db/fb0d756cc1966a3e5f3c903f14136690d567983a571d1864e6e7ca1f8c21/pycairo-1.29.2-cp315-cp315t-win_amd64.whl", hash = "sha256:88cbf5632be0b9255822b457d3bfe4f9eb0bc24e5520f54b6c4334e4f5b0f5aa", size = 875248, upload-time = "2026-10-04T19:11:50.36Z" },
    { url = "https://files.pythonhosted.org/packages/0f/ec/3c2700abac22e3ea70c67cb27caa6c2960372ebb7361127328471a39fa7f/pycairo-1.29.2-cp315-cp315t-win_arm64.whl", hash = "sha256:0e49de5b93fc1e76e670f368b9bd0ffc881c72f506e4293c4b4d79f52cbe4c47", size = 721983, upload-time = "2026-10-04T19:11:51.895Z" },
]

[[package]]
name = "pycparser"
```

**Line-by-line explanation**

- **L193** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L194** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L195** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L196** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L197** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L198** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L199** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L200** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L201** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L203** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L204** — Identify the new Pycairo package record.
- **L205** — Lock Pycairo to 1.29.2 for this snapshot.
- **L206** — Record the package registry from which cffi is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L207** — Record the source archive for pycairo, its download location, integrity hash, size and publication metadata. uv may build this archive locally when there is no suitable wheel.
- **L208** — Begin the list of prebuilt wheel artifacts available for cffi across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L209–L220** — Record one prebuilt pycairo wheel with its platform/Python compatibility in the filename and its integrity metadata. A wheel listed for another OS is not automatically suitable for this Linux environment.
- **L221** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L223** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L224** — Name this locked distribution pycparser. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).

#### 13.29.8 L225–L256 · File contents

```toml
version = "3.12"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/cb/27/eeb9f307bf07060f3d9f9aa0fb8c15b01bdfded0a941e4b2719c7f94cacd/pycparser-3.12.tar.gz", hash = "sha256:f03387877eab82ce01bbdfd0ba7252ee55a90b1c708d5129e2ce915475cf1db6", size = 158785, upload-time = "2026-10-22T13:40:03.56Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b6/ae/315bbeee126a769cbde43cf4908acb4b40408d8bf8bbf334dd7368d8dadf/pycparser-3.12-py3-none-any.whl", hash = "sha256:a076f3f489b39b43ed13563a1dafe42447445bec2e294154ec5c57fcdda4c85e", size = 62600, upload-time = "2026-10-22T13:40:02.021Z" },
]

[[package]]
name = "pygobject"
version = "3.58.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pycairo" },
]
sdist = { url = "https://files.pythonhosted.org/packages/65/1e/d590f82e14db75945b03f6b63e0f19662e0340babd8f574fdb1bb5a015e2/pygobject-3.58.1.tar.gz", hash = "sha256:4c80598ade17fbaa7798e01a25d0bf29ce109740786026a074c5c62bb3e79d23", size = 1408671, upload-time = "2026-10-09T11:29:48.929Z" }

[[package]]
name = "pyside6"
version = "6.12.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyside6-addons" },
    { name = "pyside6-essentials" },
    { name = "pyside6-pdf" },
    { name = "pyside6-webengine" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/fa/db/0722bbb81c3515dd0847fd66a7fb4760b13ad59c89e40b27b362ab5624e2/pyside6-6.12.0-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:efea4c2f2aa54403c45de825865a902a1960a1cc9d5aaa92d4ebb8f4c4cd0708", size = 577475, upload-time = "2026-10-08T09:11:15.222Z" },
    { url = "https://files.pythonhosted.org/packages/2f/53/db0cabed1e70d0bc4666b8cbc2611b72bff2f9d2c4813820182621a8c6ee/pyside6-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:d13ed4d0053cc20f3e4e0fdbf12790a9b7f958d7e22c0843411ecfa8c799e2a9", size = 577709, upload-time = "2026-10-08T09:11:17.345Z" },
    { url = "https://files.pythonhosted.org/packages/4d/8c/dfd4f339285d2e6c31067789b9b7dd2cee26c098ecc78ac7200fb04aa344/pyside6-6.12.0-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:8920e163f60493e18822d20f1e01c7c4bcf9c1c5cfbc68284788896f692594f8", size = 577708, upload-time = "2026-10-08T09:11:18.705Z" },
    { url = "https://files.pythonhosted.org/packages/a1/da/8e8514fc29ea916c3cd71a524480b77409e19ed12d709e8a5d73be089b81/pyside6-6.12.0-cp310-abi3-win_amd64.whl", hash = "sha256:31a8d2893f2f28ab483b1534dde0438f27af6e234593de30425cb4729052d8f8", size = 578958, upload-time = "2026-10-08T09:11:20.179Z" },
    { url = "https://files.pythonhosted.org/packages/5f/2e/3ebafaf7f4ccea6f6ea9d017f7fc7d9484b79e6b31d1cb92f5f5262055f0/pyside6-6.12.0-cp310-abi3-win_arm64.whl", hash = "sha256:22e2ec6407f32b61955a28f91ab55676e60017210285c28f0c381bfeed389414", size = 562743, upload-time = "2026-10-08T09:11:21.552Z" },
```

**Line-by-line explanation**

- **L225** — Pin pycparser to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L226** — Record the package registry from which pycparser is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L227** — Record the source archive for pycparser: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L228** — Begin the list of prebuilt wheel artifacts available for pycparser across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L229** — One prebuilt wheel choice: pycparser-3.12-py3-none-any.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pycparser and is data, not VPN logic.
- **L230** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L232** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L233** — Identify the new PyGObject package record.
- **L234** — Lock PyGObject to 3.58.1 for this snapshot.
- **L235** — Record the package registry from which cffi is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L236** — Begin cffi dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L237** — Record Pycairo as the Python dependency of PyGObject.
- **L238** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L239** — Record the source archive for pygobject, its download location, integrity hash, size and publication metadata. uv may build this archive locally when there is no suitable wheel.
- **L241** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L242** — Name this locked distribution pyside6. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L243** — Pin pyside6 to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L244** — Record the package registry from which pyside6 is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L245** — Begin pyside6 dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L246** — Reference the dependency named pyside6-addons. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L247** — Reference the dependency named pyside6-essentials. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L248** — Reference the dependency named pyside6-pdf. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L249** — Reference the dependency named pyside6-webengine. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L250** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L251** — Begin the list of prebuilt wheel artifacts available for pyside6 across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L252** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L253** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L254** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L255** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L256** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.

#### 13.29.9 L257–L288 · File contents

```toml
]

[[package]]
name = "pyside6-addons"
version = "6.12.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyside6-essentials" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/c3/16/c401d6455dbf49df37a8b142883e12d446abf51919c3e0ef5d9570e29160/pyside6_addons-6.12.0-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:1d9bcd294ce1c9829194c7d13b01f771a2254b86cb3462cc3399321d2797fdac", size = 90545550, upload-time = "2026-10-08T09:08:14.778Z" },
    { url = "https://files.pythonhosted.org/packages/ff/3e/0d6c5934de575286ac0699a701d4155048185035b8da0ee78d57a38bc7ef/pyside6_addons-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:4ab38c0017f0453671a9313d3a53ca1c0e378924f54b07e596bcea94a9642391", size = 59192702, upload-time = "2026-10-08T09:08:21.13Z" },
    { url = "https://files.pythonhosted.org/packages/94/14/b6c5683614601448c3ea8f19613ca378db75158ba594b662a8a8041e3e5f/pyside6_addons-6.12.0-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:48cd0b639c06c9f79685f340ccae4319614b66d6efcdf06c2ce3836790d8c46e", size = 63646547, upload-time = "2026-10-08T09:08:26.921Z" },
    { url = "https://files.pythonhosted.org/packages/02/41/ba3d52fe2acd942ebf71eb02b3bdf0897f7f6f4ce8f52289cb50228e48d3/pyside6_addons-6.12.0-cp310-abi3-win_amd64.whl", hash = "sha256:98d8d62010da6605344cee83e5c96fb846170a1f2d924523f10f5d92078b02b0", size = 40522402, upload-time = "2026-10-08T09:08:31.678Z" },
    { url = "https://files.pythonhosted.org/packages/ea/73/860ab764368cd59b1a09cb891a9a4519425395ad1f6c47d83fde908fe603/pyside6_addons-6.12.0-cp310-abi3-win_arm64.whl", hash = "sha256:3c079cbaad2ad28bc5bfa92fd6bac4ba28d622b825825e3b4220f0682599b2db", size = 35940682, upload-time = "2026-10-08T09:08:35.424Z" },
]

[[package]]
name = "pyside6-essentials"
version = "6.12.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "shiboken6" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/e1/90/d528f8dd3f9f20712bc719e10c698d27c998e1dd76ed3f33b6fb606d0972/pyside6_essentials-6.12.0-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:0867b709a724db28b161227c7d6ecb5ed10cc09226a53542417ac6dee1308239", size = 116002775, upload-time = "2026-10-08T09:09:54.453Z" },
    { url = "https://files.pythonhosted.org/packages/7b/3c/7597d8dcb36aa8315427635ec6ec9d850ffbad4ce78b9118ac854889f2d3/pyside6_essentials-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:16f4b5e41daf49235ae048458243da9efe5f3d8040f9cc5aa454ce69893d3bd9", size = 84346433, upload-time = "2026-10-08T09:10:02.825Z" },
    { url = "https://files.pythonhosted.org/packages/5e/4e/f4fd4c016719be832ec49d3c87940459e87fd666179a0a199a3998d07916/pyside6_essentials-6.12.0-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:08c5841063fc1df69b7fa1ee405f539e66576a83fc48004be3e2c5e35ccbfa69", size = 83810102, upload-time = "2026-10-08T09:10:09.13Z" },
    { url = "https://files.pythonhosted.org/packages/03/61/9a7e32a37b224f68506785bfb0f288d516098ec71681782d72b695a6c95d/pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl", hash = "sha256:c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42", size = 82153795, upload-time = "2026-10-08T09:10:15.104Z" },
    { url = "https://files.pythonhosted.org/packages/92/11/43afb3d0e7c25dd09f0eb7e44f1283dadb5fa8d8b517249fe3fde02e6702/pyside6_essentials-6.12.0-cp310-abi3-win_arm64.whl", hash = "sha256:c76aa689989bf9bb9b45535e0a81c6733294df720b0eed1308fa30d2606b98cc", size = 62073456, upload-time = "2026-10-08T09:10:20.202Z" },
]

```

**Line-by-line explanation**

- **L257** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L259** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L260** — Name this locked distribution pyside6-addons. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L261** — Pin pyside6-addons to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L262** — Record the package registry from which pyside6-addons is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L263** — Begin pyside6-addons dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L264** — Reference the dependency named pyside6-essentials. It is needed by pyside6-addons; dependency resolution also follows that package's own dependency references.
- **L265** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L266** — Begin the list of prebuilt wheel artifacts available for pyside6-addons across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L267** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L268** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L269** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L270** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L271** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L272** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L274** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L275** — Name this locked distribution pyside6-essentials. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L276** — Pin pyside6-essentials to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L277** — Record the package registry from which pyside6-essentials is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L278** — Begin pyside6-essentials dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L279** — Reference the dependency named shiboken6. It is needed by pyside6-essentials; dependency resolution also follows that package's own dependency references.
- **L280** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L281** — Begin the list of prebuilt wheel artifacts available for pyside6-essentials across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L282** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L283** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L284** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L285** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L286** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L287** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.

#### 13.29.10 L289–L320 · File contents

```toml
[[package]]
name = "pyside6-pdf"
version = "6.12.0.140"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyside6-essentials" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/58/33/23949c3b48af4b96b618e0502b7313ac52a782615db8dceae5bc2c516831/pyside6_pdf-6.12.0.140-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:74287989dd24a82ac1604e27a2d4530a0ab71ff03cdf878c16fdbcf5144373fb", size = 8644803, upload-time = "2026-10-08T09:07:36.716Z" },
    { url = "https://files.pythonhosted.org/packages/b4/f0/9b4f3cb0506641ea53210c7b635703f1c2c1e81c27074438105ff118f8e7/pyside6_pdf-6.12.0.140-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:0c94370b6b9d65fbfe54f9d6d25df0677db0cdcfd0a842a63958a3603a42007c", size = 2843877, upload-time = "2026-10-08T09:07:39.208Z" },
    { url = "https://files.pythonhosted.org/packages/39/cb/4a8cf3edb3f1b2396935573c02255be75f5605dcc77e9e3a201a6d6f26d7/pyside6_pdf-6.12.0.140-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:2b63ee1f8ce3d3b2b648be2ebda483dd0fbca8d44c92a6c6f924033ac7fbde8c", size = 2837165, upload-time = "2026-10-08T09:07:40.756Z" },
    { url = "https://files.pythonhosted.org/packages/0e/8a/3f5eab9eb9e6486f0334b100322bbd0aff432dd90ad7977a3910979a163f/pyside6_pdf-6.12.0.140-cp310-abi3-win_amd64.whl", hash = "sha256:4971ba1a0ca15e7c29cfd808e9600aeb46b2305dad01456eb09fa3197166268e", size = 2983516, upload-time = "2026-10-08T09:07:42.312Z" },
    { url = "https://files.pythonhosted.org/packages/b2/87/5c29bdaf47bf0b0cee7f467e86ffeb07be5bf8aa2afd2ff6f0785d0515b4/pyside6_pdf-6.12.0.140-cp310-abi3-win_arm64.whl", hash = "sha256:ce6e4d858df1eb4e2adcbd8ba212f3611ce60f9978881fe10d417f36013a6ff9", size = 2758117, upload-time = "2026-10-08T09:07:43.936Z" },
]

[[package]]
name = "pyside6-webengine"
version = "6.12.0.140"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "pyside6-addons" },
]
wheels = [
    { url = "https://files.pythonhosted.org/packages/08/37/3b50067bdcba5c22e20a8d7a029c919850c6d94f8398175b330c3b8765ad/pyside6_webengine-6.12.0.140-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:9a1de2da360d1817c08e9400a2a2fc5234beb3022a22123e15355169e183074e", size = 249778242, upload-time = "2026-10-08T09:06:03.602Z" },
    { url = "https://files.pythonhosted.org/packages/ce/e0/cb8b68b962afc253709ed61555d0a4f297fd6786c0e77921d2e951504210/pyside6_webengine-6.12.0.140-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:c041c9921d7c91c9e51a2c027f434d05c3c59baa2c8f17b71dc8194e77791f06", size = 116741921, upload-time = "2026-10-08T09:06:13.408Z" },
    { url = "https://files.pythonhosted.org/packages/1b/34/75944ed126293868fcbcc589fa2254e3310016920e5d32d21c29be021524/pyside6_webengine-6.12.0.140-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:66a842ccb7f06fa7e357f6d4d63bc2739e3cbc1f93583f314e38c43024fe5f74", size = 114053128, upload-time = "2026-10-08T09:06:21.275Z" },
    { url = "https://files.pythonhosted.org/packages/21/0d/260c7c286f2d4e8a49c099152a385414a872f022117f937824ca0a3f38e5/pyside6_webengine-6.12.0.140-cp310-abi3-win_amd64.whl", hash = "sha256:f9b61b1d457a591ee590a6b80515f25a3e61e2576a2a0a70566380f9d9de4ab0", size = 131697708, upload-time = "2026-10-08T09:06:29.606Z" },
    { url = "https://files.pythonhosted.org/packages/76/34/7a2d1d7b95c96adf173c77d1862c2587789f7afb8754430fcfc2c9e4e47a/pyside6_webengine-6.12.0.140-cp310-abi3-win_arm64.whl", hash = "sha256:44d1fac2a057a71b8f947fc5177a95fab8a0ea4e2fda068f223a00fd0193a8c7", size = 65723, upload-time = "2026-10-08T09:06:32.559Z" },
]

[[package]]
name = "shiboken6"
```

**Line-by-line explanation**

- **L289** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L290** — Name this locked distribution pyside6-pdf. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L291** — Pin pyside6-pdf to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L292** — Record the package registry from which pyside6-pdf is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L293** — Begin pyside6-pdf dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L294** — Reference the dependency named pyside6-essentials. It is needed by pyside6-pdf; dependency resolution also follows that package's own dependency references.
- **L295** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L296** — Begin the list of prebuilt wheel artifacts available for pyside6-pdf across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L297** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L298** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L299** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L300** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L301** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L302** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L304** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L305** — Name this locked distribution pyside6-webengine. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L306** — Pin pyside6-webengine to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L307** — Record the package registry from which pyside6-webengine is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L308** — Begin pyside6-webengine dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L309** — Reference the dependency named pyside6-addons. It is needed by pyside6-webengine; dependency resolution also follows that package's own dependency references.
- **L310** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L311** — Begin the list of prebuilt wheel artifacts available for pyside6-webengine across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L312** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L313** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L314** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L315** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L316** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L317** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L319** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L320** — Name this locked distribution shiboken6. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).

#### 13.29.11 L321–L352 · File contents

```toml
version = "6.12.0"
source = { registry = "https://pypi.org/simple" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b5/45/11536fba5f50a57671eb14441c6098096f3e57074e54c9d7d66039a5831e/shiboken6-6.12.0-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:47105e05baf57d35453e07d240bbe59cb4b8d9565377ea5134ff9fb37d4f5c02", size = 479653, upload-time = "2026-10-08T09:10:41.506Z" },
    { url = "https://files.pythonhosted.org/packages/49/c2/a04fa003b4360e99d8e3fc2829abacf37396ace63ea1cd616402209ec7c6/shiboken6-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:3bde565bb0890044b5c7f63808adddede5abc241e9395a2bfed61919884d6240", size = 279268, upload-time = "2026-10-08T09:10:42.982Z" },
    { url = "https://files.pythonhosted.org/packages/97/ca/a4415e6218e0dff764fe2b2d30db2fc8f499a08ace07634232ade3f73adc/shiboken6-6.12.0-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:ff72a72b3277b418902d562b987b33a6f6818bed9fe40a49d634d09bc67f620e", size = 276562, upload-time = "2026-10-08T09:10:44.25Z" },
    { url = "https://files.pythonhosted.org/packages/2a/b6/bee97e7a2edeab72aafabb46ee5adc939790a638d107860b4cad7a20e407/shiboken6-6.12.0-cp310-abi3-win_amd64.whl", hash = "sha256:a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e", size = 1265476, upload-time = "2026-10-08T09:10:45.627Z" },
    { url = "https://files.pythonhosted.org/packages/8c/d5/5894d35f8a470ca8acff0d1cd8f15b1c94cbfdfe0ce4a6ec0fcf10b95bd1/shiboken6-6.12.0-cp310-abi3-win_arm64.whl", hash = "sha256:da382e68f0815b31b6dc2bce11a465b148c4f42c37b91546a361de1576567d10", size = 1838851, upload-time = "2026-10-08T09:10:47.123Z" },
]

[[package]]
name = "tifrvpn-tui"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "cryptography" },
    { name = "numpy" },
    { name = "pygobject" },
    { name = "pyside6" },
    { name = "zxing-cpp" },
]

[package.metadata]
requires-dist = [
    { name = "cryptography", specifier = ">=50.0.2" },
    { name = "numpy", specifier = ">=2.5.4" },
    { name = "pygobject", specifier = ">=3.58.1" },
    { name = "pyside6", specifier = ">=6.12.0" },
    { name = "zxing-cpp", specifier = ">=3.1.1" },
]

[[package]]
```

**Line-by-line explanation**

- **L321** — Pin shiboken6 to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L322** — Record the package registry from which shiboken6 is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L323** — Begin the list of prebuilt wheel artifacts available for shiboken6 across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L324** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L325** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L326** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L327** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L328** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L329** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L331** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L332** — Name this locked distribution tifrvpn-tui. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L333** — Pin tifrvpn-tui to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L334** — Use the current local project directory as an editable package source. Changes to that package source can be reflected without building a separate installed copy; this does not update the five scripts copied by install.sh.
- **L335** — Begin tifrvpn-tui dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L336** — Reference the dependency named cryptography. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L337** — Reference the dependency named numpy. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L338** — Include PyGObject in this local project selected dependency list.
- **L339** — Reference the dependency named pyside6. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L340** — Reference the dependency named zxing-cpp. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L341** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L343** — Open additional metadata for the preceding local project package, including its originally declared dependency constraints.
- **L344** — Begin the local project's declared dependency requirements, retaining the minimum-version constraints from its metadata.
- **L345** — Reference the dependency named cryptography. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L346** — Reference the dependency named numpy. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L347** — Record the project requirement pygobject>=3.58.1 alongside the exact selected PyGObject record.
- **L348** — Reference the dependency named pyside6. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L349** — Reference the dependency named zxing-cpp. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L350** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.
- **L352** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.

#### 13.29.12 L353–L376 · File contents

```toml
name = "zxing-cpp"
version = "3.1.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/b9/30/ad0e0352c593712ebb47143571ff11b130812e2852d7540e7c80cdf23340/zxing_cpp-3.1.1.tar.gz", hash = "sha256:1051a521b21a9fe206702ad4186aeb195154e3e1badcd99576d030723f36382b", size = 1437030, upload-time = "2026-07-29T08:50:59.019Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/56/57/ac717270db6888973eba83e9832fe800808b555df0ebe34e37b6a6e07545/zxing_cpp-3.1.1-cp312-abi3-macosx_10_13_x86_64.whl", hash = "sha256:09dea611a7c9dc7c713a82303b15b733dc71abb1a77454b26b779e33671cef05", size = 911430, upload-time = "2026-07-29T08:50:32.625Z" },
    { url = "https://files.pythonhosted.org/packages/12/70/f14831dd92d5c844a39c03ebe9ba185e073d4467d50b48dcf2a816cae0c5/zxing_cpp-3.1.1-cp312-abi3-macosx_11_0_arm64.whl", hash = "sha256:037cbcaeb0cb12497fc15ced23f6b778fce8a6a1d1bbffddbffd004c6225744d", size = 863740, upload-time = "2026-07-29T08:50:34.23Z" },
    { url = "https://files.pythonhosted.org/packages/0d/f3/3fb2c6c48e6f58382fbbd31965c7caafd81f75b7e6707b011bdb940adb5f/zxing_cpp-3.1.1-cp312-abi3-manylinux_2_26_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:f4dae01111f323f46736fc21f05c14dcaaac06cea5fdc8fd994ba19f6f918c6e", size = 1024253, upload-time = "2026-07-29T08:50:35.599Z" },
    { url = "https://files.pythonhosted.org/packages/0c/30/79683cf7139ee5325fbc68169eb8dc1cb2033ec43339b5f39de990f909a7/zxing_cpp-3.1.1-cp312-abi3-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:9cf67341949946307d086b302cefd453fb47bc6d6ddc7d088839e9481982757b", size = 1096795, upload-time = "2026-07-29T08:50:36.896Z" },
    { url = "https://files.pythonhosted.org/packages/7d/14/055c5a68a50bdde8378ced94e63f9ce340311e51c87b947f9b95fe69f51a/zxing_cpp-3.1.1-cp312-abi3-win_amd64.whl", hash = "sha256:29f98a91148171460b47a942d137ecc90c4b8097636f23cca65263a56bb025d3", size = 1003677, upload-time = "2026-07-29T08:50:38.328Z" },
    { url = "https://files.pythonhosted.org/packages/5d/32/a827a99fa5e0aee382b5d464cbd2075e1911a69500116705f6695a6accd8/zxing_cpp-3.1.1-cp312-abi3-win_arm64.whl", hash = "sha256:04a8f8b78779ab9b637853a0329770791cfc3095d232c768dc4824b63901ebd0", size = 931324, upload-time = "2026-07-29T08:50:39.632Z" },
    { url = "https://files.pythonhosted.org/packages/b0/30/e98ce9c56bd1f1fe0a1fd0e5c39202da49baa3620031cb80ac7a04759ffb/zxing_cpp-3.1.1-cp313-cp313t-macosx_10_15_x86_64.whl", hash = "sha256:9d291fd958c26066aca97c4a416a9f15475a99c97b253cd4d2c6754a485b01e6", size = 915582, upload-time = "2026-07-29T08:50:41.286Z" },
    { url = "https://files.pythonhosted.org/packages/3d/d8/ab1db4571348e8756c2019425c72b3cb936f72c4a7c2af35687396381c36/zxing_cpp-3.1.1-cp313-cp313t-macosx_11_0_arm64.whl", hash = "sha256:670e2946232128b1ebba5b1f623e016ac8f8ad743ae3a0fb2e50b33180f216a2", size = 867699, upload-time = "2026-07-29T08:50:42.815Z" },
    { url = "https://files.pythonhosted.org/packages/6a/09/78a038367fd3d4fc00fa1f696672bfff002b4771814c3b20b1c392872043/zxing_cpp-3.1.1-cp313-cp313t-manylinux_2_26_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:9efc7ed301846a8c060720f09bed8a29fefccef54b5106c291e4136ffe87d089", size = 1030204, upload-time = "2026-07-29T08:50:44.356Z" },
    { url = "https://files.pythonhosted.org/packages/90/7b/0fc91d2d0463164268d06dd3e9b97520f9fe5c79dc6a954c92cd9ac92fbf/zxing_cpp-3.1.1-cp313-cp313t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:0f37e714ad4fd0ae4dd759b19fef25bd524a2865bc3ca8730b4e318c0cc7800e", size = 1104920, upload-time = "2026-07-29T08:50:45.639Z" },
    { url = "https://files.pythonhosted.org/packages/3b/9d/2adb3c88894b1e018739aae9bd2725733b55c14e3df090a0e01b2bffff14/zxing_cpp-3.1.1-cp313-cp313t-win_amd64.whl", hash = "sha256:93918148c1ed7ec60ff172b183ddc9dddfcb59e40867b0e98d79cc2d62a2b41d", size = 1009395, upload-time = "2026-07-29T08:50:47.118Z" },
    { url = "https://files.pythonhosted.org/packages/f8/f1/c7c93c2123701c12cda01ef02662ff010a79d31e86f67e9080d10d19013b/zxing_cpp-3.1.1-cp313-cp313t-win_arm64.whl", hash = "sha256:68b8cbd6797228eb983ab616b876cc744db319c64a9491a4806324afd04a8c48", size = 934267, upload-time = "2026-07-29T08:50:48.463Z" },
    { url = "https://files.pythonhosted.org/packages/d2/a8/8c005a5251734f57a30f1e85fa2a8965d53cd0df99d1abf642956153410e/zxing_cpp-3.1.1-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:5b4bd34f71868af0e34b000da4fc885c85a7f0ef37eecc0ec433ff27b263a5b7", size = 915637, upload-time = "2026-07-29T08:50:50.129Z" },
    { url = "https://files.pythonhosted.org/packages/5d/31/a2e693c9771b88e45dd7e52b56c85c169649123cf0eebfb32151efdfb356/zxing_cpp-3.1.1-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:94e342d390933b9678f71bf6005cf2125cdb27c2355c21fa194e3a672502aac6", size = 867750, upload-time = "2026-07-29T08:50:51.788Z" },
    { url = "https://files.pythonhosted.org/packages/f0/30/d2f7e626b4216bbb47783d7431cd27b151cfe5abeb22aa06f0b130095841/zxing_cpp-3.1.1-cp314-cp314t-manylinux_2_26_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:71df8523deb2fb40b834238e6fa739e210e3a6e27c5b94a99b4106c08e339b9b", size = 1030274, upload-time = "2026-07-29T08:50:53.535Z" },
    { url = "https://files.pythonhosted.org/packages/4e/b9/c4b6db45a3a9f7e34a3faadcce78c2084f0bc2ce0ee8344d61f1149d2318/zxing_cpp-3.1.1-cp314-cp314t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:388626ac8df24f63c2bb17dcd42fd21daeeea6fd6759bd9b1c064b71142da07e", size = 1104873, upload-time = "2026-07-29T08:50:54.941Z" },
    { url = "https://files.pythonhosted.org/packages/c8/8e/8dbf8fcf4d466c7d9b5023ae4cf17da22f328efabd4d7107109ac7737155/zxing_cpp-3.1.1-cp314-cp314t-win_amd64.whl", hash = "sha256:fe8172f3c9b17f8fd40fba2ae0ba9728228caeff3587eabf5d99888891d02e62", size = 1032030, upload-time = "2026-07-29T08:50:56.169Z" },
    { url = "https://files.pythonhosted.org/packages/47/38/e547ea4f9a7c8c24a1d3a59869540029e4bad467f9544084c3cee94eb6e0/zxing_cpp-3.1.1-cp314-cp314t-win_arm64.whl", hash = "sha256:1992231c161c3eaf5857f7bc35193b8ca621eba0debc51e752403657b88d542a", size = 956213, upload-time = "2026-07-29T08:50:57.524Z" },
]
```

**Line-by-line explanation**

- **L353** — Name this locked distribution zxing-cpp. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L354** — Pin zxing-cpp to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L355** — Record the package registry from which zxing-cpp is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L356** — Record the source archive for zxing-cpp: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L357** — Begin the list of prebuilt wheel artifacts available for zxing-cpp across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L358** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-macosx\_10\_13\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L359** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L360** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L361** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L362** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L363** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L364** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L365** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L366** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L367** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L368** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L369** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L370** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L371** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L372** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L373** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L374** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L375** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L376** — Generated dependency-lock data. This record’s exact package/version/artifact or requirement is preserved here; the main guide explains the shared TOML schema, wheel compatibility, SHA-256 hashes and registry metadata. The package branch removes the redundant argparse dependency.

[[#4 Package branch — file map|↑ Package file map]]

### 13.30 Package source — .envrc


The developer-environment instruction remains unchanged; it is independent of the old script installer.

**Relation to main:** [[TIFR Vpn TUI#7.11 .envrc|.envrc]] — The developer-environment instruction remains unchanged; it is independent of the old script installer.


#### 13.30.1 L1–L1 · Complete file


```sh
layout uv
```

**Line-by-line explanation**

- **L1** — Ask a direnv setup supporting layout uv to prepare/load a uv-managed Python environment for this directory. It affects development command lookup and Python package availability when that integration is active; the line does not itself contain or load VPN credentials.


[[#4 Package branch — file map|↑ Package file map]]

### 13.31 Package source — .python-version


The preferred development Python series remains unchanged.

**Relation to main:** [[TIFR Vpn TUI#7.12 .python-version|.python-version]] — The preferred development Python series remains unchanged.


#### 13.31.1 L1–L1 · Complete file


```text
3.13
```

**Line-by-line explanation**

- **L1** — Request the Python 3.13 series. The actual interpreter invoked by the scripts depends on PATH or sys.executable at runtime.


[[#4 Package branch — file map|↑ Package file map]]

### 13.32 Package source — .gitignore


The existing ignore patterns remain unchanged in this branch snapshot.

**Relation to main:** [[TIFR Vpn TUI#7.13 .gitignore|.gitignore]] — The existing ignore patterns remain unchanged in this branch snapshot.


#### 13.32.1 L1–L32 · Complete file · section 1


```text
# Python-generated files
__pycache__/
*.py[cod]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv/
venv/

# Python tool caches and coverage
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
.coverage.*
htmlcov/

# Local configuration and credentials
.env
.env.*
!.env.example
/config.json
*.kdbx*
*.gpg
*.asc
*.key
*.pem
*.p12
*.pfx
```

**Line-by-line explanation**

- **L1** — Comment identifying generated Python files in the following group.
- **L2** — Ignore directories named \_\_pycache\_\_, which Python uses for bytecode caches.
- **L3** — Ignore filenames matching .pyc, .pyo or .pyd via the character class \[cod\]. \* matches preceding name text.
- **L4** — Ignore build directories, which hold generated package build products.
- **L5** — Ignore dist directories, which typically hold built distribution archives.
- **L6** — Ignore wheels directories containing generated/downloaded Python wheel files.
- **L7** — Ignore package metadata paths ending .egg-info.
- **L9** — Comment grouping virtual-environment directories.
- **L10** — Ignore the common .venv local Python environment directory.
- **L11** — Ignore the alternative venv environment directory.
- **L13** — Comment grouping tool caches and test-coverage results.
- **L14** — Ignore pytest's cached test metadata.
- **L15** — Ignore Ruff's linter cache.
- **L16** — Ignore mypy's static-type-checker cache.
- **L17** — Ignore the default coverage data file.
- **L18** — Ignore suffixed coverage data files, often created by parallel coverage runs.
- **L19** — Ignore generated HTML coverage reports.
- **L21** — Comment introducing local settings and secret-bearing file patterns.
- **L22** — Ignore the standard .env local environment configuration file, which often contains private settings.
- **L23** — Ignore names beginning .env. such as .env.local.
- **L24** — The leading ! is a negation rule: allow a shareable .env.example despite the previous broad rule, provided other Git rules do not exclude it.
- **L25** — Ignore config.json only at the repository root because of the leading /. This does not match every nested config.json file.
- **L26** — Ignore KeePass database filenames containing .kdbx and any following suffix, including backups.
- **L27** — Ignore .gpg encrypted-data files. Encryption does not make your personal ciphertext a necessary repository asset.
- **L28** — Ignore .asc files, often ASCII-armored GPG material.
- **L29** — Ignore .key files, often private key material.
- **L30** — Ignore .pem files, which can contain certificates or keys.
- **L31** — Ignore .p12 bundles, which can include private keys.
- **L32** — Ignore .pfx bundles, another certificate/key-container extension.


#### 13.32.2 L33–L38 · Complete file · section 2


```text

# Authenticator QR images must stay local
*.png
*.jpg
*.jpeg
*.webp
```

**Line-by-line explanation**

- **L34** — Comment explains why broad image patterns are present: authenticator QR images can contain long-term seeds.
- **L35** — Ignore PNG images anywhere matched by this pattern.
- **L36** — Ignore JPG images.
- **L37** — Ignore JPEG images.
- **L38** — Ignore WebP images. These rules do not cover every possible image format; for example, the scanner can open BMP too, but no \*.bmp ignore rule exists here.


[[#4 Package branch — file map|↑ Package file map]]

### 13.33 Package source — LICENSE


The license text remains unchanged, including its unfilled copyright placeholders.

**Relation to main:** [[TIFR Vpn TUI#7.16 LICENSE|LICENSE]] — The license text remains unchanged, including its unfilled copyright placeholders.


#### 13.33.1 L1–L21 · Complete file


```text
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Line-by-line explanation**

- **L1** — Name of the license text included in the repository.
- **L3** — Copyright notice line. \[year\] and \[fullname\] are unfilled template placeholders in the actual source, not values automatically substituted by Git or Python.
- **L5–L10** — A physical line in the permission paragraph. Taken together, this paragraph lists permissions to use, copy, change and distribute the software, subject to the following condition. The line wrapping is for readability, not distinct program instructions.
- **L12–L13** — A physical line in the condition paragraph requiring retention of the copyright and permission notice in the described copies/portions. Read the actual license text for its complete wording.
- **L15–L21** — A physical line in the all-capital warranty/liability paragraph. These are words in the license document, not settings that affect runtime error handling or network security.


[[#4 Package branch — file map|↑ Package file map]]


### 13.34 Package source — tests/test_totp.py

Three test methods exercise valid export decoding, optional metadata/single-part batches, and nine invalid field-type or multi-part-batch inputs. The byte fixtures use a public RFC test key and are never personal authentication data.

**Functions and their purpose**

- **export_url**, L14–L16: Build migration-URL text from serialized test payload bytes.
- **account_payload**, L19–L20: Wrap a small test account in the outer export field.
- **ExportTests.test_decode_without_optional_metadata_and_generate_code**, L24–L37: Decode a public-key fixture without optional metadata and check its fixed-time six-digit code.
- **ExportTests.test_decode_with_metadata_and_single_export_batch**, L39–L43: Decode metadata and an explicitly one-part export.
- **ExportTests.test_wrong_field_types_and_multiple_batches_raise_value_error**, L45–L59: Require ValueError for nine labeled malformed or unsupported payloads.

#### 13.34.1 L1–L13 · Module setup and definitions

```python
"""Export decoding checks using a public test key and malformed field types."""

import base64
import unittest
from urllib.parse import urlencode

from tifrvpn.totp import current_code, decode_export


# Public RFC 6238 test key, followed by SHA1, six digits and TOTP fields.
ACCOUNT = b"\x0a\x1412345678901234567890\x20\x01\x28\x01\x30\x02"


```

**Line-by-line explanation**

- **L1** — Describe export-decoder regression checks using only public test data and deliberately malformed field types.
- **L3** — Import base64 at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L4** — Import unittest at module scope, so the dependency is loaded when this module is imported. Importing its names does not call the later application operations.
- **L5** — Bind urlencode from urllib.parse at module scope. These names are then available to the functions below without a function-local import.
- **L7** — Bind current_code, decode_export from tifrvpn.totp at module scope. These names are then available to the functions below without a function-local import.
- **L10–L11** — Define a minimal serialized TOTP account using the public RFC6238 SHA1 test key and the six-digit/TOTP enum fields. The b prefix and backslash-x escapes specify bytes, not a personal credential.

#### 13.34.2 L14–L18 · export_url

```python
def export_url(payload):
    query = urlencode({"data": base64.b64encode(payload).decode("ascii")})
    return f"otpauth-migration://offline?{query}"


```

**Line-by-line explanation**

- **L14** — Define a test helper converting serialized export bytes into migration-URL text.
- **L15** — Encode payload bytes as Base64 ASCII text and URL-escape the data query parameter.
- **L16** — Return the migration URL format expected by the production decoder.

#### 13.34.3 L19–L22 · account_payload

```python
def account_payload(account):
    return b"\x0a" + bytes([len(account)]) + account


```

**Line-by-line explanation**

- **L19** — Define a helper wrapping one nested account in outer export field 1.
- **L20** — Write the field-1 byte tag, a one-byte length and the account bytes. These deliberately small fixtures fit in a one-byte length; this helper is not a general export encoder.

#### 13.34.4 L23–L23 · Module setup and definitions

```python
class ExportTests(unittest.TestCase):
```

**Line-by-line explanation**

- **L23** — Group three export-decoding test methods in a unittest.TestCase class.

#### 13.34.5 L24–L38 · ExportTests.test_decode_without_optional_metadata_and_generate_code

```python
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

```

**Line-by-line explanation**

- **L24** — Test that an account can omit optional name/issuer metadata and still produce the expected current code.
- **L25** — Construct one valid export fixture and decode it through the real decoder.
- **L26–L36** — Require the complete decoded account dictionary to match the public seed, empty metadata, SHA1, six digits and 30-second period. These are assertions on returned data, not printed secrets.
- **L37** — Check the six-digit RFC-derived result at timestamp 59: 287082. The timestamp is fixed so the test does not depend on the current clock.

#### 13.34.6 L39–L44 · ExportTests.test_decode_with_metadata_and_single_export_batch

```python
    def test_decode_with_metadata_and_single_export_batch(self):
        account = ACCOUNT + b"\x12\x04TIFR\x1a\x03VPN"
        decoded = decode_export(export_url(account_payload(account) + b"\x18\x01"))
        self.assertEqual(decoded["name"], "TIFR")
        self.assertEqual(decoded["issuer"], "VPN")

```

**Line-by-line explanation**

- **L39** — Test optional metadata and an explicitly single-part export batch.
- **L40** — Append the serialized name TIFR and issuer VPN to the valid account bytes.
- **L41** — Append outer batch-size field3 with integer value1, then decode the resulting valid URL.
- **L42** — Require the decoded account name to equal TIFR.
- **L43** — Require the decoded issuer to equal VPN.

#### 13.34.7 L45–L63 · ExportTests.test_wrong_field_types_and_multiple_batches_raise_value_error

```python
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
```

**Line-by-line explanation**

- **L45** — Test nine malformed/unsupported payload cases that must consistently raise ValueError.
- **L46** — Build a labeled dictionary of failing inputs; labels make a failing subtest easy to identify.
- **L47** — Put an integer where the outer account byte payload is required.
- **L48** — Replace the nested secret field with an integer instead of bytes.
- **L49** — Replace the nested account-name field with an integer instead of UTF-8 bytes.
- **L50** — Replace the nested issuer field with an integer instead of bytes.
- **L51** — Replace the algorithm integer identifier with a byte field.
- **L52** — Replace the digit-format integer identifier with a byte field.
- **L53** — Replace the OTP-kind integer identifier with a byte field.
- **L54** — Supply an outer batch-size field encoded as bytes instead of an integer.
- **L55** — Supply integer batch-size2, which this single-part importer rejects.
- **L56** — Close the table of failing inputs.
- **L57** — Run the same rejection assertion for each labeled fixture.
- **L58** — Report the case label separately and require ValueError. TypeError or a successful return would fail this assertion.
- **L59** — Invoke the production decoder with that malformed fixture.
- **L62** — Only start unittest directly when this test file is executed as a program.
- **L63** — Ask unittest to discover/run the tests in this module during direct execution.

[[#4 Package branch — file map|↑ Package file map]]

## 14 Package branch — transitional launchers explained

These are **historical files at ade9780**, removed by 3275bad. They are included to explain the migration rather than recommended as the current installation path. The current branch uses package-generated commands.

### 14.1 Historical package wrapper — tifrvpn


```python
#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import main
    raise SystemExit(main())
```

**L1:** Use Python from PATH; the original Zsh command name temporarily became a Python forwarding wrapper.

**L2:** State that the reusable implementation now lives in the importable package.

**L3–L4:** Import path/interpreter-search-path helpers without running the VPN.

**L6:** Only forward when the wrapper is executed as a program.

**L7:** Resolve the wrapper’s actual directory, including symlinks.

**L8–L9:** Prefer adjacent src/tifrvpn for source checkout use; otherwise choose adjacent lib for the offline copied install. Prepend that directory to sys.path so this process can import the library.

**L10:** from tifrvpn.cli import main — select the appropriate CLI function for this old executable name.

**L11:** Invoke it and turn its returned integer into this wrapper process’s exit status.

The wrapper is deliberately thin: the actual behavior is in package modules. In 3275bad all five wrappers are removed, along with the compatibility-only auth_main adapter, because the supported package installation generates the three public command wrappers from metadata instead.

### 14.2 Historical package wrapper — tifr-otp.py


```python
#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import otp_main
    raise SystemExit(otp_main())
```

**L1:** Use Python from PATH; the original Zsh command name temporarily became a Python forwarding wrapper.

**L2:** State that the reusable implementation now lives in the importable package.

**L3–L4:** Import path/interpreter-search-path helpers without running the VPN.

**L6:** Only forward when the wrapper is executed as a program.

**L7:** Resolve the wrapper’s actual directory, including symlinks.

**L8–L9:** Prefer adjacent src/tifrvpn for source checkout use; otherwise choose adjacent lib for the offline copied install. Prepend that directory to sys.path so this process can import the library.

**L10:** from tifrvpn.cli import otp_main — select the appropriate CLI function for this old executable name.

**L11:** Invoke it and turn its returned integer into this wrapper process’s exit status.

The wrapper is deliberately thin: the actual behavior is in package modules. In 3275bad all five wrappers are removed, along with the compatibility-only auth_main adapter, because the supported package installation generates the three public command wrappers from metadata instead.

### 14.3 Historical package wrapper — tifr-vpn-auth.py


```python
#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import auth_main
    raise SystemExit(auth_main())
```

**L1:** Use Python from PATH; the original Zsh command name temporarily became a Python forwarding wrapper.

**L2:** State that the reusable implementation now lives in the importable package.

**L3–L4:** Import path/interpreter-search-path helpers without running the VPN.

**L6:** Only forward when the wrapper is executed as a program.

**L7:** Resolve the wrapper’s actual directory, including symlinks.

**L8–L9:** Prefer adjacent src/tifrvpn for source checkout use; otherwise choose adjacent lib for the offline copied install. Prepend that directory to sys.path so this process can import the library.

**L10:** from tifrvpn.cli import auth_main — select the appropriate CLI function for this old executable name.

**L11:** Invoke it and turn its returned integer into this wrapper process’s exit status.

The wrapper is deliberately thin: the actual behavior is in package modules. In 3275bad all five wrappers are removed, along with the compatibility-only auth_main adapter, because the supported package installation generates the three public command wrappers from metadata instead.

### 14.4 Historical package wrapper — tifr-import-totp


```python
#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import import_totp_main
    raise SystemExit(import_totp_main())
```

**L1:** Use Python from PATH; the original Zsh command name temporarily became a Python forwarding wrapper.

**L2:** State that the reusable implementation now lives in the importable package.

**L3–L4:** Import path/interpreter-search-path helpers without running the VPN.

**L6:** Only forward when the wrapper is executed as a program.

**L7:** Resolve the wrapper’s actual directory, including symlinks.

**L8–L9:** Prefer adjacent src/tifrvpn for source checkout use; otherwise choose adjacent lib for the offline copied install. Prepend that directory to sys.path so this process can import the library.

**L10:** from tifrvpn.cli import import_totp_main — select the appropriate CLI function for this old executable name.

**L11:** Invoke it and turn its returned integer into this wrapper process’s exit status.

The wrapper is deliberately thin: the actual behavior is in package modules. In 3275bad all five wrappers are removed, along with the compatibility-only auth_main adapter, because the supported package installation generates the three public command wrappers from metadata instead.

### 14.5 Historical package wrapper — tifr-import-totp.py


```python
#!/usr/bin/env python3
"""Compatibility launcher; reusable implementation lives in tifrvpn."""
from pathlib import Path
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    # A source checkout uses src; install.sh places the package under lib.
    sys.path.insert(0, str(root / ("src" if (root / "src/tifrvpn").is_dir() else "lib")))
    from tifrvpn.cli import import_totp_main
    raise SystemExit(import_totp_main())
```

**L1:** Use Python from PATH; the original Zsh command name temporarily became a Python forwarding wrapper.

**L2:** State that the reusable implementation now lives in the importable package.

**L3–L4:** Import path/interpreter-search-path helpers without running the VPN.

**L6:** Only forward when the wrapper is executed as a program.

**L7:** Resolve the wrapper’s actual directory, including symlinks.

**L8–L9:** Prefer adjacent src/tifrvpn for source checkout use; otherwise choose adjacent lib for the offline copied install. Prepend that directory to sys.path so this process can import the library.

**L10:** from tifrvpn.cli import import_totp_main — select the appropriate CLI function for this old executable name.

**L11:** Invoke it and turn its returned integer into this wrapper process’s exit status.

The wrapper is deliberately thin: the actual behavior is in package modules. In 3275bad all five wrappers are removed, along with the compatibility-only auth_main adapter, because the supported package installation generates the three public command wrappers from metadata instead.

### 14.6 Historical package wrapper — install.sh


```sh
#!/bin/sh
# Install commands for the current user; never change shell startup files.
set -eu

if [ "${1:-}" = --help ]; then
    cat <<'EOF'
Usage: ./install.sh
Copies the package and launchers to ~/bin/tifr and links commands into ~/.local/bin.
Override with TIFR_INSTALL_DIR and TIFR_COMMAND_DIR (absolute paths).
Run again after updating the checkout to install the new version.
EOF
    exit 0
fi
if [ "$#" -ne 0 ]; then
    echo 'Usage: ./install.sh [--help]' >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$(dirname -- "$(readlink -f -- "$0")")" && pwd)
install_dir=${TIFR_INSTALL_DIR:-"$HOME/bin/tifr"}
command_dir=${TIFR_COMMAND_DIR:-"$HOME/.local/bin"}
for directory in "$install_dir" "$command_dir"; do
    case "$directory" in
        /*) ;;
        *) echo 'Installation directories must be absolute paths.' >&2; exit 2 ;;
    esac
done
if [ "$install_dir" = "$command_dir" ]; then
    echo 'Use separate helper and command directories.' >&2
    exit 2
fi

# Check all command names before copying anything. Existing links from a previous
# installation can be updated; unrelated commands are left alone.
for command in tifrvpn tifr-otp tifr-import-totp; do
    target=$command
    [ "$command" != tifr-otp ] || target=tifr-otp.py
    destination=$command_dir/$command
    if [ -e "$destination" ] || [ -L "$destination" ]; then
        if [ ! -L "$destination" ] || [ "$(readlink -- "$destination")" != "$install_dir/$target" ]; then
            echo "Command already exists: $destination. Choose another TIFR_COMMAND_DIR." >&2
            exit 1
        fi
    fi
done

mkdir -p -- "$install_dir" "$command_dir"
for file in tifrvpn tifr-vpn-auth.py tifr-otp.py tifr-import-totp tifr-import-totp.py; do
    if [ "$(readlink -f -- "$source_dir/$file")" != "$(readlink -f -- "$install_dir/$file")" ]; then
        install -m 755 -- "$source_dir/$file" "$install_dir/$file"
    fi
done
# Keep the importable package beside the launchers without downloading packages.
# Python dependencies and system bindings must already be installed.
mkdir -p -- "$install_dir/lib/tifrvpn/gui"
for module in "$source_dir"/src/tifrvpn/*.py; do
    install -m 644 -- "$module" "$install_dir/lib/tifrvpn/"
done
for module in "$source_dir"/src/tifrvpn/gui/*.py; do
    install -m 644 -- "$module" "$install_dir/lib/tifrvpn/gui/"
done
ln -sfn -- "$install_dir/tifrvpn" "$command_dir/tifrvpn"
ln -sfn -- "$install_dir/tifr-otp.py" "$command_dir/tifr-otp"
ln -sfn -- "$install_dir/tifr-import-totp" "$command_dir/tifr-import-totp"
printf 'Installed helpers: %s\nCommands: %s\n' "$install_dir" "$command_dir"
printf 'Ensure the command directory is on PATH, then follow README.md to set up credentials.\n'
```

The original copy installer was temporarily retained. It checked conflicts and copied five compatibility wrappers, then also copied src/tifrvpn/*.py and gui/*.py into ~/bin/tifr/lib/tifrvpn. This kept old command paths working during the first refactor commit, without registering the distribution in site-packages.

Lines 53–54 explain the added package-copy intent; L55 creates lib/tifrvpn/gui; L56–58 copy core modules with ordinary readable 644 permissions; L59–61 copy GUI modules; the final links still expose the old command names. The wrapper adds lib to sys.path so it can find that manually copied package. The main guide explains the unchanged conflict checks/copy/link mechanics line by line.

This entire installer was deleted in 3275bad because normal package installation now registers imports and generates command entry points in one place. Manually copied modules and manual sys.path/PYTHONPATH support are no longer another installation model to maintain.

### 14.7 Historical package adapter — auth_main


```python
def auth_main(argv=None):
    """Compatibility for the former standalone authentication helper."""
    argv = sys.argv[1:] if argv is None else argv
    if argv in (["--sso-window"], ["--sso-window", "--quiet"]):
        from ._sso_worker import sso_window_process

        sso_window_process(quiet="--quiet" in argv)
    if argv == ["--forget-login"]:
        return main(argv)
    parser = argparse.ArgumentParser(
        description="Sign in to TIFR SSO, then hand an in-memory session to NetworkManager."
    )
    parser.add_argument("uuid", metavar="NETWORKMANAGER_PROFILE_UUID")
    parser.add_argument(
        "--quiet", action="store_true", help="hide the SSO browser using Xvfb"
    )
    args = parser.parse_args(argv)
    from . import auth, keyring
    from . import networkmanager as nm

    try:
        nm.validate_profile(args.uuid)
        cookie = keyring.load_session(on_progress=_progress)
        if cookie and auth.valid_session(cookie):
            _progress("tifr VPN: reusing saved session")
        else:
            if cookie:
                keyring.clear_session(on_progress=_progress)
                _progress(
                    "tifr VPN: saved session expired; TIFR requires sign-in again."
                )
            cookie = auth.authenticate(quiet=args.quiet, on_progress=_progress)
            keyring.save_session(cookie, on_progress=_progress)
        nm.activate(args.uuid, cookie, on_progress=_progress)
        return 0
    except KeyboardInterrupt:
        print("\ntifr VPN: cancelled", file=sys.stderr)
        return 130
    except VPNError as error:
        print(f"tifr VPN: {error}", file=sys.stderr)
        return error.returncode
    except ImportError:
        print(
            "tifr VPN: install dependencies: sudo dnf install python3-gobject webkit2gtk4.1 python3-cryptography",
            file=sys.stderr,
        )
        return 1
    except (ValueError, OSError, subprocess.SubprocessError):
        print(
            "tifr VPN: could not prepare the VPN session; check the preceding errors.",
            file=sys.stderr,
        )
        return 1
```

This function began at L245 in ade9780’s cli.py. It existed only to preserve the old root tifr-vpn-auth.py calling convention: a profile UUID, internal --sso-window mode, optional quiet, or --forget-login. It parsed those legacy arguments, validated the profile, reused or refreshed a keyring session, activated NetworkManager, and translated failures to terminal codes. The first internal-worker branch called sso_window_process; cache clearing delegated to the normal CLI. Its try/except paths mirrored the old script’s cancellation/readable/import/general-error messages.

The current branch no longer needs this second orchestration/argument path because the root compatibility caller was removed. cli.main plus vpn.connect own the supported command and reusable orchestration flow, while _sso_worker owns the private browser entry. Removing the adapter avoids maintaining another nearly duplicate session/activation sequence.

### 14.8 Historical worker import-path support


```python
    # Source launchers and the offline installer add a package search path only
    # in the controller. Carry it into the isolated Python interpreter too.
    package_root = str(Path(__file__).resolve().parent.parent)
    environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, (package_root, environment.get("PYTHONPATH")))
    )
```

The initial refactor’s copied/root launchers inserted a source or lib directory into the controller’s sys.path. That process-local change would not automatically appear in a new Python interpreter. These lines therefore calculated the package root from auth.py, prepended it to the child’s PYTHONPATH and preserved any existing values. os.pathsep is the platform’s search-path separator; filter(None, ...) omitted empty components.

Once standard package installation became the supported model, the same interpreter can import tifrvpn in both parent and worker through its installed/editable registration. The injection was deleted, and the auth test now checks that a caller-supplied PYTHONPATH is preserved. Installed-module tests run from another directory with -I to verify availability independently of that variable.




[[#1 Package branch — start here|↑ Current package branch overview]] · [[TIFR Vpn TUI#TIFR VPN — Complete Code Guide|↑ Original guide]]

## 15 Understanding the November fixes — a beginner's walkthrough

Read this section in order before using the source appendix as a reference. Examples containing `example` or the public RFC test key are teaching data. They are not your TIFR password, database master password or real authenticator seed.

### 15.1 The five different things that were getting mixed together

A **Python interpreter** is the program that runs Python code. A **module** is code that Python can load with `import`. A **package distribution** is something a package manager installs. A **native library** is compiled code supplied by your operating system. A **virtual environment** is a directory that gives one project its own Python executable links and installed Python packages.

| Name in this project | What it is | Where it comes from |
| --- | --- | --- |
| Python 3.13 | The interpreter selected by `.python-version` | uv can supply a managed CPython installation. |
| `.venv` | This checkout's local Python environment | `uv sync --locked` creates or synchronizes it. |
| `PyGObject` / normalized name `pygobject` | The Python distribution providing GI bindings | Declared in `pyproject.toml`; installed by uv. |
| `gi` | The Python import name exposed by PyGObject | You write `import gi` in Python. |
| GTK 3, WebKitGTK 4.1, libsoup 3, libsecret | Native Linux libraries used by those bindings | Fedora packages, installed separately from Python packages. |
| `Secret`, `Gtk`, `WebKit2`, `Soup` | Namespaces exposing particular native libraries through GI | Selected with `gi.require_version`, then imported from `gi.repository`. |
| `pygobject-stubs` | Extra type descriptions for editor tools | Optional developer tooling; it is not in this snapshot's dependencies. |

The crucial name difference is **install `PyGObject`, import `gi`**. Similar differences already exist elsewhere: install `PySide6`, import `PySide6.QtWidgets`; install `zxing-cpp`, import `zxingcpp`; install this distribution as `tifrvpn-tui`, import it as `tifrvpn`.

`uv add gi` therefore does not name the binding distribution we need. The command used here was:

```sh
uv add PyGObject
```

That command added `pygobject>=3.58.1` to `pyproject.toml`, updated `uv.lock`, and installed PyGObject plus its Pycairo dependency into `.venv`. This dependency addition is already committed as `bf6fa28`. On a fresh clone you normally run `uv sync --locked`; you do not need to add the dependency again.

The [PyGObject installation guide](https://pygobject.gnome.org/getting_started.html#fedora) documents both distribution-provided bindings and building the Python package inside a virtual environment.

### 15.2 Why Python 3.14 was suggested earlier, and why it is not needed now

The first environment problem was specific: Fedora's existing `gi` package lived under system Python 3.14, but the project's isolated environment used Python 3.13. Python 3.13 did not automatically search Python 3.14's packages, and compiled extensions built for one version cannot simply be assumed to work with another.

There were two possible routes:

| Route | What happens | Status in this guide |
| --- | --- | --- |
| Reuse Fedora's Python bindings | Use a compatible system interpreter and expose its site-packages to the environment. | Earlier troubleshooting alternative; not required by the final setup. |
| Build PyGObject inside the project environment | Keep uv's Python 3.13 and compile the binding package for that interpreter. | The route now installed and documented. |

The second route worked because your machine already had the native development libraries, compiler and Python 3.13 headers needed for the build. The resulting `gi` package now lives inside `.venv/lib/python3.13/site-packages/gi/`.

The verified final state is **Python 3.13.18, PyGObject 3.58.1, and `include-system-site-packages = false`**. False is correct here: the environment contains its own Python bindings. Those bindings still call native Linux libraries installed outside `.venv`; an isolated Python environment does not contain an entire Linux operating system.

### 15.3 Set up a fresh Fedora machine, step by step

First install the project's runtime programs: NetworkManager with its OpenConnect VPN plugin, OpenConnect, KeePassXC including its CLI, GnuPG, a pinentry program and an unlocked desktop Secret Service keyring. Section 5 explains their separate jobs. Quiet browser sign-in also requires Xvfb, `xvfb-run` and `xauth`.

For the GI libraries and their build prerequisites, the README records:

```sh
sudo dnf install gcc pkgconf-pkg-config gobject-introspection-devel cairo-gobject-devel gtk3 webkit2gtk4.1 libsoup3 libsecret
```

The compiler turns binding source code into a Python extension. Development packages provide declarations and build information the compiler needs. The GTK/WebKit/Soup/Secret runtime libraries provide the actual native functionality. If you choose Fedora's system Python rather than uv-managed CPython, it also needs matching Python development headers, normally supplied by `python3-devel`. The uv-managed Python used in this checkout already had its own headers.

After cloning the repository, enter its actual directory and run:

```sh
cd /home/soham/projects/tifrvpn-tui
uv sync --locked
source .venv/bin/activate
```

On another person's computer, replace the `cd` path with that person's clone location. The directory name `.venv` is relative to the project directory in these commands.

| Command part | Meaning |
| --- | --- |
| `uv` | The Python project/package manager. |
| `sync` | Make the environment match the project's dependency selection and install the local project. |
| `--locked` | Require the existing lockfile to be up to date; fail rather than silently changing the dependency selection. |
| `source` | Execute the activation script in the current shell so its environment changes affect that shell. |
| `.venv/bin/activate` | The script that puts this environment's command directory at the front of shell command lookup. |

The [uv syncing documentation](https://docs.astral.sh/uv/concepts/projects/sync/) explains lock checking, environment synchronization and editable project installation. A source edit is visible to a new Python process because uv installs this checkout in editable mode; an already running process may need restarting.

You can also use `uv run` without activating the shell:

```sh
uv run tifrvpn --help
uv run python -c 'import sys, gi; print(sys.executable); print(gi.__file__)'
```

Do not keep recreating `.venv` every day. Use `uv sync --locked` after dependency or metadata updates, and `uv run ...` to run the selected environment's commands. `uv add` is for changing the project's dependency list, not a substitute for every ordinary launch.

The native package names above are Fedora-specific. An Ubuntu/Debian/Arch setup needs equivalent libraries and development packages from that distribution; changing `dnf` to another command without changing package names is not a reliable installation recipe. A new machine must also meet the native library versions required by the locked PyGObject release.

### 15.4 Check GI without signing in or reading your keyring

Run this from the checkout after synchronization:

```sh
uv run python - <<'PY'
import sys
import gi

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)
print("GI package:", gi.__file__)
for name, version in [
    ("Secret", "1"),
    ("Gtk", "3.0"),
    ("WebKit2", "4.1"),
    ("Soup", "3.0"),
]:
    gi.require_version(name, version)

from gi.repository import Secret, Gtk, WebKit2, Soup
print("All four GI namespaces loaded")
PY
```

The loop selects namespace versions; the `from` statement actually loads them. This verifies availability. It does not call `Secret.password_lookup_sync`, create a browser window or connect the VPN.

If `import gi` fails, first inspect the interpreter and run `uv sync --locked`. If building PyGObject fails, read the first missing native dependency in the build output. If `gi` imports but a namespace is unavailable, check that namespace's native library/introspection package and requested version. Installing `pygobject-stubs` cannot replace a missing runtime library.

### 15.5 Imports at the top: loading a function is different from calling it

The source and test files now place their import statements at module scope, before function/class definitions. This was a requested style change. A **function definition** creates a function object. A **function call** executes that function's body.

```python
from tifrvpn import connect

# The import above loads the function and its dependencies.
# A later, explicit connect() call would perform the VPN operation.
```

For example, `keyring.py` now imports GI and Secret when Python loads that module. It still waits until a keyring function is called before looking up, saving or deleting a credential. `qr_import.py` imports Qt/NumPy/ZXing at module load but creates the window and starts scanning only inside `run()`.

This has a practical tradeoff: dependencies must be available sooner. Importing `tifrvpn` now loads Secret bindings and cryptography. Importing `cli.py` also loads the Qt/QR libraries, including when asking for help. Missing dependencies can therefore fail during import, before the later function's `try` block is entered. A `try` block inside a function does not catch an exception that occurred earlier while importing its module.

GI needs one small setup step between imports:

```python
import gi

gi.require_version("Secret", "1")
from gi.repository import Secret
```

`require_version` must happen before loading that namespace so GI knows which API version to use. These statements are together at the top of the file, not inside `_saved_login`. The `# noqa: E402` comment on the actual `from` line explains the deliberate exception to Ruff's general rule about imports preceding executable statements.

The SSO worker uses the same ordering for GTK 3.0, WebKit2 4.1 and Soup 3.0. Namespace versions such as `"1"` and `"3.0"` are API identifiers; they are not the Python version.

### 15.6 Read the type-checker errors before trying to silence them

A **type** describes the kind of value: `str` is text, `int` is an integer, `bytes` is raw byte data, and `None` means no value. `int | bytes` means either kind is possible. It does not mean a value is both kinds at once.

| Diagnostic | What the checker is telling you | Actual repair |
| --- | --- | --- |
| `str | None` cannot be passed to `Path` | This expression might have no string value. | In `config.py`, record the validated dictionary type after checking the JSON. |
| `>` is unsupported for `bytes` and an integer | The decoder might compare raw data to a count. | Check `isinstance(value, int)` before the comparison. |
| `.decode()` is unavailable on an integer | A serialized text field might contain the wrong kind of value. | Require bytes before interpreting them as UTF-8 text. |
| `None` is not subscriptable | The account might not exist when looking up `account["secret"]`. | Return immediately if no account has been decoded. |
| `QCoreApplication` has no `clipboard` | The general application instance type is too broad. | Require a `QApplication` and obtain its clipboard. |
| `BarcodeFormat` is not `BarcodeFormats` | A single format identifier is not the collection type expected by the installed API's stubs. | Explicitly construct `BarcodeFormats(BarcodeFormat.QRCode)`. |

Most fixes add real validation. `cast` is a different tool used only where earlier validation already proves the type. In `config.py`, the JSON must be a dictionary containing only the three permitted string keys and nonblank string values; then `cast(dict[str, str], settings)` tells the checker what has been established. It returns the same dictionary. It does not turn an integer into text or make invalid JSON safe. See [Python's typing documentation](https://docs.python.org/3.13/library/typing.html#typing.cast).

### 15.7 How the authenticator decoder works and why each new check exists

The QR image does not directly contain a ready-to-use Python dictionary. The program processes several representations in order:

```text
Image pixels
  → ZXing finds QR text
  → otpauth-migration://offline?... URL
  → Base64 text in the data query parameter
  → serialized bytes
  → numbered fields containing integers or bytes
  → one validated account dictionary
  → current TOTP code
```

**Base64** represents byte data as text suitable for the URL. **Base32** is the textual representation used for the extracted authenticator seed. These encodings are not encryption: encoding the seed does not protect it from someone who can read it.

`_fields(data: bytes) -> Iterator[tuple[int, int | bytes]]` describes the parser's output. Read it from the inside outward: each yielded item is a pair; the first part is an integer field number, and the second is an integer or bytes. An `Iterator` supplies those pairs one at a time. `yield` emits one pair and preserves the parser's position for the next request.

A **wire type** is the serialized format's instruction for reading the next value. Type 0 reads a variable-length integer. Type 2 reads a length and then that many bytes. Types 1 and 5 preserve fixed-size byte sequences. The parser's supported wire types are checked explicitly, and it rejects invalid/truncated input.

Do not confuse the outer export field numbers with the inner account field numbers:

| Level | Field number | Meaning used by this decoder | Required kind |
| --- | ---: | --- | --- |
| Outer export | 1 | Serialized account data | bytes |
| Outer export | 3 | Export batch size, when supplied | integer; a value greater than 1 is rejected |
| Inner account | 1 | Authenticator secret | nonempty bytes |
| Inner account | 2 | Account name | bytes; defaults to empty bytes if absent |
| Inner account | 3 | Issuer | bytes; defaults to empty bytes if absent |
| Inner account | 4 | Algorithm identifier | supported integer: 1, 2 or 3 |
| Inner account | 5 | Digit-format identifier | supported integer: 1 or 2 |
| Inner account | 6 | OTP kind | must equal 2, the TOTP kind used here |

The decoder requires exactly one account. It rejects multi-part batches when the batch-size field indicates more than one part. Then it checks each value before using operations that require a particular kind. For example, `.decode("utf-8")` converts byte-encoded name/issuer text to Python strings; it cannot operate on an integer.

Local variables such as `secret`, `name`, `issuer`, `algorithm` and `digit_format` make the validation visible to both the reader and type checker. The program validates that variable, then uses that same variable, rather than repeatedly performing dictionary lookups whose types can be difficult to track.

The supported algorithm identifiers map to SHA1/SHA256/SHA512. Digit-format 1 maps to 6 displayed digits and 2 maps to 8 digits; the identifier is not itself the final number of digits. The returned account uses a 30-second period, matching this implementation's assumption. Decoding prepares data for manual KeePassXC setup; it does not write the vault or create a new enrollment at TIFR.

### 15.8 Why `ValueError` remains despite the Ruff warning

There are two different situations to distinguish. If a caller supplies an inappropriate argument type to a public function, `TypeError` is normally the relevant exception. If the caller supplies a text QR export but its internal serialized fields are malformed, this decoder reports invalid input with `ValueError`.

Ruff's `TRY004` rule recognizes an `isinstance` check followed by a non-`TypeError` exception. Its recommendation is useful in general, but it does not decide the decoder's public error convention. The two checks in `totp.py` use:

```python
raise ValueError("Invalid export QR.")  # noqa: TRY004 - Malformed QR data.
```

Here `#` starts a Python comment. `noqa: TRY004` asks Ruff to skip that one rule for this line. The explanation records why. This does not disable the validation, catch the exception, suppress all warnings or alter execution. The malformed-export tests explicitly require `ValueError`.

This is a deliberate project choice; it is not a claim that Ruff recommends `ValueError` for every type check. See the [TRY004 rule](https://docs.astral.sh/ruff/rules/type-check-without-type-error/).

### 15.9 The QR window, application object and clipboard fixes

Qt offers a general `QCoreApplication` and richer graphical application classes. A returned base-class object is not automatically known to support every subclass feature. Widgets require `QApplication`. The scanner now creates or reuses an instance, verifies its class and then obtains the clipboard:

```python
app = QApplication.instance() or QApplication([])
if not isinstance(app, QApplication):
    raise RuntimeError("The QR importer requires a QApplication instance.")
clipboard = app.clipboard()
```

If an existing application object is unsuitable, the program reports that condition before trying to create widgets. The local `clipboard` variable refers to the same clipboard interface used by the copy and cleanup handlers. It is not a copy of the clipboard's contents. The [QApplication documentation](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QApplication.html) describes the widget application object.

Initially `self.account` is `None`. After a valid scan it becomes the decoded dictionary. Normally the Copy button is disabled until then, but the handler must also be safe if called directly or before decoding. The new guard returns without reading a missing account:

```python
if self.account is None:
    return
```

Once an account exists, the handler copies its seed and schedules cleanup after 60,000 milliseconds. Cleanup clears the live clipboard only if it still contains the seed this window copied. If you copied other text afterward, that text is left alone. Closing the window also requests cleanup. The timer depends on the event loop running; clipboard-manager history is independent of the live clipboard.

The ZXing fix is an explicit wrapper:

```python
formats=zxingcpp.BarcodeFormats(zxingcpp.BarcodeFormat.QRCode)
```

`BarcodeFormat.QRCode` identifies QR format. `BarcodeFormats(...)` constructs the format-selection object required by the installed `read_barcodes` signature. The native scan was checked with an in-memory QR carrying the public RFC test key, not personal credentials.

### 15.10 What the tests prove, and what the editor tools prove

| Tool/check | Question answered | Result recorded for this snapshot |
| --- | --- | --- |
| Pyright on `config.py`, `totp.py`, `gui/qr_import.py` | Are these checked expressions compatible with the available type information? | Zero errors/warnings for these targets. |
| Ruff `TRY004` check on `totp.py` | Are there unsuppressed violations of this one selected rule? | Pass. This is not an all-rules Ruff result. |
| `unittest` suite | Do the defined offline behaviors match their assertions? | 53 test methods pass. |
| GI namespace import check | Can this Python environment load Secret, GTK, WebKit2 and Soup? | All four load with Python 3.13.18 and local PyGObject. |
| Offscreen scanner check | Can native QR decoding and copy/cleanup behavior work with a mocked clipboard? | Pass; no real desktop clipboard or camera used. |

Three new test methods live in `tests/test_totp.py`. They check decoding without optional name/issuer metadata, decoding with metadata and a one-part export, and rejecting malformed field types/multiple batches. The last method loops through nine cases using `subTest`, so “53 tests” means 53 methods, not merely 53 individual assertions or input examples. The public RFC key yields `287082` at the specified test timestamp in the six-digit case.

Moving keyring imports changed how tests replace dependencies. Patching `sys.modules` inside a test is too late to replace a name already imported into `keyring.py`. `patch.object(keyring, "Secret", self.secret)` replaces the name the production function actually looks up, then restores it after the test.

The import test now supplies fake dependency modules to an isolated child interpreter. Importing names is permitted; starting application operations is forbidden. The fake `gi.require_version` accepts version selection because that belongs to import setup. Calls to external programs, sockets and configuration-file reads are blocked. This proves the application's import behavior under the supplied test interfaces; it does not prove that missing native dependencies can be ignored on a real installation.

For editor warnings about GI names, first verify the real interpreter and binding imports. GI creates some namespaces dynamically, so optional PyGObject stubs can improve static analysis. Stubs describe interfaces to tools; they do not install GTK, WebKit or a keyring service. Restart Neovim's Python language server with `:LspRestart` after changing the environment. A checker producing no errors is useful evidence, but it does not prove a live VPN login works.

### 15.11 Understand the four commits and inspect their exact lines

The four recommended commits are now present. They are recorded history, not commands that still need to be repeated:

| Commit | Message | Files/purpose |
| --- | --- | --- |
| `bf6fa28` | `fix: install PyGObject in the uv environment` | `pyproject.toml` and `uv.lock`: declare and lock the Python GI dependency. |
| `41d6410` | `fix: validate authenticator export field types` | `src/tifrvpn/totp.py` and new `tests/test_totp.py`: validation, annotations, narrow Ruff exceptions and regression tests. |
| `6d5aa1a` | `refactor: move imports to module scope and fix QR scanner types` | Seven source files and four tests: import placement, revised import mocks, Qt/ZXing/copy fixes. |
| `589be0d` | `docs: explain uv installation and native GI dependencies` | `README.md`: install through ordinary uv with native build prerequisites. |

The earlier configuration fix is already committed separately as `507b4b3`. Line numbers in the source appendix refer to the current file. Commit diffs show the before/after locations at that point in history. If later edits insert lines, an old line number can move while the commit's recorded diff remains available.

Inspect the actual committed patches without modifying anything:

```sh
cd /home/soham/projects/tifrvpn-tui
git show --stat bf6fa28
git show --format=fuller --unified=3 41d6410 -- src/tifrvpn/totp.py tests/test_totp.py
git show --format=fuller --unified=3 6d5aa1a -- src/tifrvpn/gui/qr_import.py
git show --format=fuller --unified=3 589be0d -- README.md
git status --short
```

`--` separates Git options/revisions from the following file paths. `--unified=3` requests three surrounding context lines. In a diff, `-` marks old removed text and `+` marks new added text; those symbols are not prefixes to paste into the Python file.

### 15.12 How to commit future edits without confusing Git with installation

A **working tree** contains the files you are editing. The **staging area**, also called the index, holds the version selected for the next commit. A **commit** saves that staged snapshot to local Git history. A **push** sends commits to a remote repository. Installing/synchronizing a Python environment is a separate operation.

```text
edit a file
  → inspect with git diff
  → select changes with git add
  → inspect with git diff --cached
  → record with git commit
```

For a future dependency change, a typical sequence is:

```sh
uv add SOME_PACKAGE
git diff -- pyproject.toml uv.lock
git add -- pyproject.toml uv.lock
git diff --cached
git commit -m "build: add SOME_PACKAGE dependency"
```

`SOME_PACKAGE` is a placeholder; replace it with the real distribution name. `uv add` changes the dependency files and environment. `git add` selects file content for a commit. They are different commands despite sharing the word “add”.

For future code changes, choose a concrete message describing the resulting behavior. Example command structure:

```sh
git diff -- src/tifrvpn/totp.py
git add -p -- src/tifrvpn/totp.py
git diff --cached
git commit -m "fix: describe the actual decoder behavior changed"
```

`git add -p` offers **hunks**, which are groups of nearby changed lines. `y` stages the displayed hunk; `n` leaves it unstaged; `s` splits it when possible; `e` opens manual patch editing; `q` stops the selection session. A numeric line reference is a navigation aid, not a direct staging command. Stage whole files with `git add -- path/to/file` when all their changes belong together. For a new untracked file, `git add -N -- path/to/file` makes it available to interactive patch selection; ordinary `git add` is simpler when the whole new file belongs in the commit.

Always inspect `git diff --cached`: it shows what will be recorded, including anything staged before your most recent command. If you stage a file and then edit it again, the later edit is not automatically added to the staged copy. Stage again if that later edit belongs in the same commit. [The Git book](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) explains this working-tree/index distinction.

To record changes only to this external Research note, first find which repository, if any, tracks it:

```sh
git -C "/home/soham/projects/Research/Linux/TIFR Vpn" rev-parse --show-toplevel
```

If that directory is in a repository and the note belongs there, review and stage it using that repository's root and the actual tracked file path. If Git says it is not a repository, the note is still saved normally; it simply is not part of Git history there. Do not try to add this external path from the `tifrvpn-tui` repository, and do not create a new repository just to clear that message unless you intend to start managing the Research notes with Git.

### 15.13 Read the copy handler one symbol at a time

This short fragment combines several unfamiliar Python ideas, so read it as a sequence of actions:

```python
if self.account is None:
    return
self.copied = self.account["secret"]
clipboard.setText(self.copied)
QTimer.singleShot(60000, self.clear_clipboard)
```

| Part | Meaning in this window |
| --- | --- |
| `class Scanner(QWidget)` | Define a kind of window based on Qt's QWidget class. A class describes objects; creating `Scanner()` makes one actual window object. |
| `self` | The particular Scanner object whose method is running. It is how the method accesses that window's stored state. |
| `self.account` | An attribute stored on that window. Initially it holds None; after successful decoding it holds a dictionary. |
| `None` | The special value meaning no account has been stored yet. It is not the text `"None"` and is not an empty dictionary. |
| `is None` | Check specifically for that no-value state. |
| `if ...:` and indentation | Run the indented statements only when the condition is true. The indentation is part of Python's syntax. |
| `return` | Finish this handler immediately. Here it does not close the window, exit Python or disconnect a VPN. |
| `self.account["secret"]` | Look up the value under the dictionary key named `"secret"`. The preceding guard ensures the account is not None. |
| `self.copied = ...` | Store that value as the window's remembered copied seed. One equals sign assigns a value; it is not an equality test. |
| `clipboard.setText(...)` | Call the clipboard object's setText method now, passing the seed as its argument. |
| `60000` | Sixty thousand milliseconds, which is 60 seconds. |
| `self.clear_clipboard` without `()` | Pass the method itself as a callback for Qt to call later. |
| `self.clear_clipboard()` with `()` | Call the method immediately instead. That is not what the timer line does. |

A **callback** is a function or method handed to another component so that component can call it at the appropriate time. The Qt **event loop** waits for events such as button clicks and timer deadlines and runs their callbacks. `app.exec()` starts that loop. The handler returns quickly; the future cleanup is scheduled rather than implemented by blocking the window for a minute.

Two related dictionary forms also appear in the decoder: `account.get(2, b"")` reads a field with an explicit fallback when absent, while `account[1]` requires that key to exist. The `b` prefix creates bytes; ordinary quotes create text. `bytes.decode("utf-8")` turns encoded text bytes into a Python string, and Base32 encoding gives the seed its setup-key text representation. These conversions change representation; they do not encrypt the data.

When reading a line, first ask which value it reads, then which check establishes that the value is usable, then which operation actually changes something. That order makes the guard, dictionary lookup and clipboard write easier to distinguish.

### 15.14 File-and-line commit reference with the exact Git commands

This table preserves the file/line breakdown behind the four commits. Line numbers refer to the source at `589be0d`. A range can include unchanged context. For moved imports, a listed later line may be the current location beside a deletion rather than a line containing newly added code. Use `git show COMMIT -- FILE` to see the precise historical patch.

| Commit | File relative to the checkout | Current lines affected or beside deleted imports |
| --- | --- | --- |
| `bf6fa28` | `pyproject.toml` | 13 |
| `bf6fa28` | `uv.lock` | 203–222, 232–240, 338, 347 |
| `41d6410` | `src/tifrvpn/totp.py` | 8, 12, 15, 28, 47, 66–100 |
| `41d6410` | `tests/test_totp.py` | 1–63; the complete new test file |
| `6d5aa1a` | `src/tifrvpn/_sso_worker.py` | 8–12 |
| `6d5aa1a` | `src/tifrvpn/cli.py` | 8–12, 138, 197, 231 |
| `6d5aa1a` | `src/tifrvpn/gui/credential_setup.py` | 1–8 |
| `6d5aa1a` | `src/tifrvpn/gui/qr_import.py` | 1–33, 174, 212–220 |
| `6d5aa1a` | `src/tifrvpn/gui/sso.py` | 8–20, 63 |
| `6d5aa1a` | `src/tifrvpn/keyring.py` | 3–13 |
| `6d5aa1a` | `src/tifrvpn/networkmanager.py` | 4, 12–14, 89, 166 |
| `6d5aa1a` | `tests/test_cli.py` | 9, 70 |
| `6d5aa1a` | `tests/test_imports.py` | 1–37 |
| `6d5aa1a` | `tests/test_keyring.py` | 4–5, 16 |
| `6d5aa1a` | `tests/test_networkmanager.py` | 8–9, 98 |
| `589be0d` | `README.md` | 27–28, 32–50, 56–68, 75–76 |

The stage/commit commands below show how these changes were grouped. **The commits already exist. Do not repeat them as an installation step.** Use them as a reference when you have equivalent pending edits, or inspect the existing commits with `git show` as explained above. `git add` stages whole named files; the table's line numbers do not restrict what it stages. To select only some changed lines, use the interactive staging procedure in section 15.12.

**Dependency declaration and lockfile:**

```sh
cd /home/soham/projects/tifrvpn-tui
git add -- pyproject.toml uv.lock
git diff --cached
git commit -m "fix: install PyGObject in the uv environment"
```

**Export decoder and regression tests:**

```sh
git add -- src/tifrvpn/totp.py tests/test_totp.py
git diff --cached
git commit -m "fix: validate authenticator export field types"
```

**Import organization, matching tests and QR scanner fixes:**

```sh
git add -- \
  src/tifrvpn/_sso_worker.py \
  src/tifrvpn/cli.py \
  src/tifrvpn/gui/credential_setup.py \
  src/tifrvpn/gui/qr_import.py \
  src/tifrvpn/gui/sso.py \
  src/tifrvpn/keyring.py \
  src/tifrvpn/networkmanager.py \
  tests/test_cli.py \
  tests/test_imports.py \
  tests/test_keyring.py \
  tests/test_networkmanager.py

git diff --cached
git commit -m "refactor: move imports to module scope and fix QR scanner types"
```

The backslash at the end of each continued shell line joins it to the next line, making this one `git add` command. This grouping includes the entire QR importer because its import movement, application check, format wrapper and clipboard guard share that file.

**Installation documentation:**

```sh
git add -- README.md
git diff --cached
git commit -m "docs: explain uv installation and native GI dependencies"
```

After any real future changes, run the checks and inspect what remains:

```sh
uv run python -B -m unittest discover -s tests -v
git status --short
git log -4 --oneline
```

A successful commit normally consumes the staged changes. If you repeat a commit command in a clean checkout, Git reports there is nothing new to commit; it does not recreate the old commit. This Research guide is a separate file from README and from the repository documentation copy. Recording future edits to either copy requires selecting the actual file that changed in its owning repository.
