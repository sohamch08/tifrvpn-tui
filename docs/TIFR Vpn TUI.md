---
title: TIFR VPN — Complete Code Guide
aliases:
  - TIFR VPN beginner guide
  - TIFR VPN line-by-line explanation
tags:
  - learning/programming
  - linux
  - python
  - shell
  - networking/vpn
created: 2026-11-07
source_snapshot: 2026-11-07
source_revision: 41b2346c8af8da7e1f224bdf9de10f50a946a261
source_files: 16
source_lines: 2064
repository: /home/soham/projects/tifrvpn-tui
installed_helpers: /home/soham/bin/tifr
updated: 2026-11-08
documented_branch: main
main_branch_revision: 41b2346c8af8da7e1f224bdf9de10f50a946a261
number headings: auto, first-level 1, max 5, _.1.1
---

# TIFR VPN — Complete Code Guide

## 1 Versions covered

**Current branch guide:** [[TIFR Vpn TUI Package|tifrvpn/package at 075f9cd3cfb9]] covers installation, daily use, migration reasons, public API, workflows, tests and every current source file.

**Preserved original guide below:** main at `41b2346c8af8`. Its root scripts, Zsh launcher, copy installer, 16-file count and 16-test result are historical descriptions of that snapshot. Current package code and its recorded 50-test validation are explained in [[TIFR Vpn TUI Package|the separate package guide]]. Your old `~/bin/tifr` copies still match main at the recorded inspection.


## 2 Main branch — original guide

A beginner-friendly explanation of the complete repository and the five matching installed helpers. **16 files · 2,064 source lines · all original explanations retained.** The source is a snapshot of Git `41b2346c8af8` from **7 November 2026**.

**Learning route:** command basics → Zsh launcher → KeePass/GPG helper → authentication controller → browser callbacks → QR importer → tests and packaging.

**Navigate:** [[#Quick reference|Commands]] · [[#Foundations|Concepts]] · [[#File index|Files]] · [[#Every file explained|Line-by-line guide]] · [[#Learning checkpoints|Review]] · [[#References|References]]


## 3 How to use this compact note in Obsidian

The explanations use ordinary headings, paragraphs, lists and tables. Everything remains in this one note, with no required attachments or community plugins. Use the internal navigation links or Obsidian’s Outline to reach a topic.

Each file has its own heading, followed by smaller headings for related functions or steps. Each code section’s title gives its original line range; explanations use **L76**, **L77**, and so on. Code keeps its original indentation and syntax highlighting. Blank source lines are preserved; where consecutive lines share exactly the same explanation, one labeled range covers them. To keep long source sections compact, enable **Settings → Editor → Fold heading**, then fold the file or function headings. The Command palette also provides **Fold all headings and lists** and **Unfold all headings and lists**.

Use Obsidian's note search for a symbol or phrase, such as `DSID`, `read_code`, `pinentry`, `uuid`, or `timeout`. The heading links are internal to this note, so you can rename or move the note within your vault without relying on its original export location.

## 4 Quick reference

| Command | Meaning |
| --- | --- |
| `tifrvpn -c` | Connect; show status if already active. |
| `tifrvpn -c --quiet` | Connect with fresh sign-in on a private virtual display. |
| `tifrvpn --quiet` | Same quiet-connect action. |
| `tifrvpn -s` | Show state, addresses, devices and DNS. |
| `tifrvpn -d` | Disconnect. |
| `tifrvpn` | Toggle connection state. |
| `tifrvpn --setup` | Prepare the NetworkManager connection profile. |
| `tifrvpn --forget-login` | Clear cached sessions; leave an existing tunnel active. |
| `tifr-otp --setup` | Verify vault access and encrypt its master password. |
| `tifr-otp` | Print the current short-lived authenticator code. |
| `tifr-import-totp` | Open the optional local QR importer. |
| `tifr-import-totp --image` | Use an existing QR image without starting the webcam. |
| `./install.sh` | Copy runtime helpers and create public command links. |


### 4.1 The two most important distinctions

**Source versus installation:** a Git commit records the repository; `install.sh` updates copied executables. Your `~/bin` is a symlink into `~/projects/dotfiles/bin`. At the recorded snapshot, all five installed runtime files exactly matched this repository.

**Different secrets:** the TIFR password signs in to the account; the KeePass master password unlocks the vault; the TOTP seed generates codes; a DSID cookie represents an accepted temporary session. A GPG passphrase may separately unlock the GPG private key.

## 5 Foundations

These topics use regular sections and preserve the full conceptual explanations from the original guide.


### 5.1 Start here: what the project does


When you type `tifrvpn -c`, these scripts arrange a sign-in to your institution and ask your Linux networking service to establish a VPN tunnel. A VPN is an encrypted network connection to a gateway. The operating system can route traffic through that connection according to the installed connection settings. This code does not tell us that every packet from every application necessarily uses the tunnel: routing and DNS behavior belong to the active NetworkManager/OpenConnect configuration.

The project is mainly coordination code. It joins existing tools: Zsh for command dispatch, Python for authentication and integration, KeePassXC for stored credentials, GPG for unlocking the vault password, WebKit for the login page, and NetworkManager/OpenConnect for the connection. You do not need to learn the internals of all these tools at once to understand how they cooperate.


### 5.2 Your source checkout and installed files


The Git repository is `/home/soham/projects/tifrvpn-tui`. This is where you edit and commit the source. Your installed helpers are reached through `/home/soham/bin/tifr`. On your machine, `/home/soham/bin` is a symbolic link to `/home/soham/projects/dotfiles/bin`. A symbolic link is a filesystem entry that points to another path. Therefore `~/bin/tifr/tifrvpn` reaches the file at `~/projects/dotfiles/bin/tifr/tifrvpn`.

The five installed files currently have exactly the same bytes as the five repository runtime files. They are installed copies, not automatic live views of this repository. Editing or committing the repository later does not automatically copy changes into the installed directory. The repository's `install.sh` implements that copy/update step. Its default `~/.local/bin` command links describe how a fresh installation is arranged; this inspection found no `tifr*` entries there, so your actual command lookup may be provided by your other shell configuration or PATH entries.

`~` means your home directory, `/home/soham`. A path beginning `/` is absolute: it starts at the filesystem root. `./install.sh` is relative: it means the file in the current directory. `PATH` is a list of directories the shell searches when you type a command without a full path. A filename extension is a convention; a script's shebang tells the operating system which interpreter to start.


### 5.3 The program map


```text
You type tifrvpn -c [--quiet]
  → tifrvpn (Zsh): choose action, check/find/create profile
  → tifr-vpn-auth.py (Python controller): check cached session
      ├─ valid saved session → activate tunnel
      └─ fresh sign-in needed
          → launch another Python process in --sso-window mode
          → GTK + WebKit load the TIFR portal and SSO forms
          → tifr-otp.py supplies login fields and a fresh TOTP
              → GPG decrypts the database master password
              → keepassxc-cli opens the KeePass vault
          → validate the returned DSID cookie
          → return cookie to the Python controller through a pipe
      → verify gateway TLS certificate and derive a public-key pin
      → put transient secrets in an anonymous file descriptor
      → nmcli asks NetworkManager/OpenConnect to activate the tunnel
  → show connection status and try a desktop notification

Optional enrollment import (separate one-time activity):
  tifr-import-totp → tifr-import-totp.py → phone export QR/local image
    → decode seed and settings → YOU paste them into KeePassXC and save
```


### 5.4 Four secret values that do different jobs


| Value | Purpose | Where this implementation keeps/uses it |
| --- | --- | --- |
| TIFR account password | Proves the account password during the web sign-in. | Stored in the encrypted KeePass database; read into process/browser memory to fill the trusted login form. |
| KeePass database master password | Unlocks the entire configured vault, not just TIFR. | Stored separately as GPG ciphertext; decrypted into memory, then supplied to the KeePass CLI on standard input. |
| TOTP setup seed | A long-term shared secret from which current and future authenticator codes can be calculated. | Stored with the KeePass entry. The optional importer extracts it from a migration QR for you to paste manually. |
| DSID session cookie | A temporary reusable token the server issues after sign-in; it lets the VPN start without resending the password/OTP every time. | Used in memory and cached in the desktop keyring along with selected browser state. |

A fifth secret may be involved: the passphrase protecting your GPG private key. GPG's pinentry asks for it when needed, and gpg-agent can temporarily cache an unlock. The script does not ask for that passphrase as a normal command-line argument. The word “password” alone is ambiguous here: always ask which of these roles a line refers to.

**Encryption** transforms readable data into ciphertext using a key and can be reversed with the right key. **Encoding** such as Base32/Base64 changes representation and can be reversed by anyone; it does not hide a seed. A **hash** makes a fixed-size digest used for fingerprints/integrity checks. **HMAC** is a keyed hash used here to calculate authenticator codes. A **certificate** associates a server identity with a public key under a trust system. A **fingerprint** is a digest identifying particular certificate/key bytes; the code verifies normal TLS trust before deriving a per-activation public-key pin.


### 5.5 What a terminal command consists of


```text
tifrvpn -c --quiet
│       │  └─ an option changing how fresh sign-in is displayed
│       └──── an option choosing the connect action
└──────────── the command name the shell must locate
```

A terminal is the text interface; the shell is the program interpreting the command. A process is one running program instance. Python is both a language and an interpreter that executes that language. A subprocess is a program started by another process. The controller and embedded browser deliberately run in different processes; a function call inside one process is not the same thing as creating another process.

Programs have conventional streams: **stdin** (input, descriptor 0), **stdout** (ordinary output/data, descriptor 1), and **stderr** (diagnostics, descriptor 2). A pipe connects streams between processes. This project uses captured stdout for secret results and inherited stderr for human progress. For example, the browser child writes its DSID to stdout, which the controller captures; it prints “submitting saved password” to stderr without printing the password itself.

Every process also has an integer exit status. Here `0` means success, `1` ordinary failure, `2` invalid arguments, and `130` cancellation. In shell arithmetic flags such as `quiet=1`, however, nonzero means “on.” These are two different conventions used in different contexts.


### 5.6 Shell syntax used repeatedly


| Syntax | Meaning here |
| --- | --- |
| `# comment` | Explanation ignored by the shell. On line 1, `#!` instead forms the special interpreter directive. |
| `name=value`, `$name` | Assign a shell variable with no spaces around =; later expand its value with $. Python variables do not use $. |
| `"$name"` | Expand while preserving the argument boundary, including spaces. Single quotes instead preserve literal text without variable expansion. |
| `$(command)` | Run a command and capture its stdout as text; trailing newlines are removed by shell command substitution. |
| `"$@"`, `$1`, `$#`, `$?` | All positional arguments as separate words; the first positional argument; argument count; previous command's exit status. |
| `command \|\| return 1` | If the command fails, return failure from the current function. The right side is skipped on success. |
| `A && B` | Run/test B only when A succeeds/is true, depending on the shell context. |
| `[[ ... ]]`, `(( ... ))` | Zsh condition/pattern tests versus arithmetic/logical evaluation. POSIX install.sh instead uses `[ ... ]` tests. |
| `-z`, `-n`, `-x`, `-e`, `-L` | Empty string, nonempty string, executable path, existing path and symbolic-link path tests. |
| `>/dev/null`, `2>/dev/null` | Discard stdout versus stderr. /dev/null is the operating system's discard device. |
| `A \| B` | In a command pipeline, send A's stdout into B's stdin. A \| inside a case pattern means alternatives instead. |
| `\` at end of line | Continue a command across physical source lines; do not type trailing spaces after that backslash. |
| `return` versus `exit` | Leave the current function versus terminate the current script/process. An argumentless return preserves the last command's status. |
| `${value:-fallback}` | Use the fallback if the variable is unset or empty. |


### 5.7 Python syntax used repeatedly


| Syntax | Meaning here |
| --- | --- |
| `import module` | Load a library's definitions for reuse. Standard-library modules come with Python; others need installation. |
| `def f(argument):` | Define a reusable function. Indentation identifies its body. `f(value)` calls it; merely writing `f` passes the function object, useful for callbacks. |
| `return value` | Give a Python value back to the caller and leave the function. It becomes a process exit status only when passed to something such as `sys.exit`. |
| `=`, `==`, `!=`, `is None` | Assign, compare equality, compare inequality, and test for the special no-value object. |
| `True`, `False`, `None` | Boolean yes/no values and the absence of a meaningful value. JavaScript uses `true`, `false`, `null` instead. |
| `[a, b]`, `(a, b)`, `{'key': value}`, `set()` | A mutable ordered list, a tuple, a key/value dictionary and a set of unique values. Empty `{}` is a dictionary, not a set. |
| `items[0]`, `items[-1]`, `items[1:3]` | The first item, the final item, and a slice containing indices 1 and 2 (end excluded). Python indexing starts at zero. |
| `for item in items:` | Repeat the indented body for each value. `continue` starts the next iteration; `break` leaves the loop. |
| `try / except / finally` | Attempt work, handle a raised problem, and always run cleanup. `raise` signals a problem, interrupting ordinary flow. |
| `with resource as name:` | Use a context manager that arranges cleanup/restoration after the block, including many error paths. |
| `f"Hello {name}"` | Build a string by inserting the expression's current value. `\n` inside a string represents a newline. |
| `def f(*, quiet=False):` | Require the optional quiet parameter to be supplied by name; `False` is its default. |
| `if __name__ == '__main__':` | Run CLI behavior when executed directly, while allowing tests/helpers to load definitions without starting the full app. |
| `lambda x: expression` | A short unnamed function, often passed for future event handling or as a comparison key. |
| `class Scanner(QWidget):` | Define a custom object type inheriting window behavior. `self` refers to one instance; `self.account` stores its own account state. |

A multiline function call remains one statement even when written across several lines inside parentheses. A closing `)` finishes that call; it is not an extra action. Blank lines separate ideas and do no computation. In Python, changing indentation can change meaning. In shell, closing words such as `fi`, `done` and `esac` identify structure explicitly.


### 5.8 Why callbacks and event loops appear


A browser cannot stop responding every time a network request, page script or cookie operation is pending. Instead, the code starts an operation and supplies a callback: “when you finish, call this function with the result.” `Gtk.main()` or `app.exec()` enters an event loop, which waits for events and dispatches handlers. For example, `view.evaluate_javascript(..., form_ready)` starts JavaScript evaluation; later `form_ready` reads the returned result. A callback is not necessarily another thread or process. Several callbacks in login_cookie share the enclosing dictionaries, which act as a small state machine.

A state machine means behavior depends on remembered state. Here “busy” prevents overlapping work, “submitted” remembers form steps already attempted, “stopped” prevents retrying rejected credentials, and “cookie” records successful authentication. A timer regularly asks whether the next step is ready. `return True` from these GLib timer callbacks keeps the timer alive; it does not by itself mean “VPN connected.”


### 5.9 Follow a fresh normal connection


1. `tifrvpn` line 169 calls the dispatcher at line 113. It parses `-c` and calls `tifr-on`.
2. `tifr-on` checks tools and NetworkManager, gets/creates the profile, and avoids starting again if it is already active.
3. It runs `tifr-vpn-auth.py UUID`. The Python controller validates the profile's gateway/protocol/plugin before using any session.
4. The controller retrieves a cached session from the desktop keyring. If the gateway accepts it, jump directly to tunnel activation. Otherwise discard the stale token.
5. `authenticate()` launches the same Python file in internal browser mode. That child creates a temporary WebKit context and restores allowed TIFR browser cookies from the keyring when available.
6. The browser loads the portal. Its login flow can reach `sso.tifr.res.in`. This is a different host from `sslvpn.tifr.res.in`, so the code has separate rules for SSO form filling and portal-session detection.
7. When a recognized allowed SSO form is ready, load the OTP helper's functions. Read config, decrypt the database master password through GPG, and ask the KeePass CLI for the saved account fields.
8. Inspect/fill the recognized form using JavaScript. For an OTP step, wait if the 30-second window has fewer than five seconds left, then request a fresh code.
9. The portal may ask you to confirm replacing an existing session. This code has no auto-confirm action for that warning. In visible mode you can review it yourself.
10. When a DSID appears, probe portal access before accepting it. Save selected browser state in the keyring and return the token through captured stdout to the controller.
11. `activate()` opens a normally verified TLS connection, extracts the server public key, makes its SHA-256 pin, and records the contacted IP.
12. Write transient nmcli secrets to an anonymous memory-backed descriptor, rewind it, and pass it only to the nmcli child. nmcli activates the profile through NetworkManager/OpenConnect.
13. Return the connection status to the shell, show assigned addresses/DNS, and attempt a desktop notification.


### 5.10 What changes with --quiet


Argument parsing accepts `-c --quiet`, `--quiet -c`, and `--quiet`. It rejects quiet combined with status/disconnect/setup. If a cached session is valid, no new browser or Xvfb display is needed. For fresh sign-in, the parent first checks the Xvfb tools and attempts GPG unlocking on your real desktop. It then runs a real graphical browser on a private X11 virtual display. The child forces the X11 backend and forbids new GPG pinentry prompts there.

Xvfb is a virtual display server: it supplies a display in memory even though no ordinary monitor window shows it. It does not remove GTK/WebKit or turn this into a purely text-based authentication protocol. The supervisor waits up to 120 seconds for that child process's communication, then sends group SIGTERM, waits five more seconds, and can escalate to SIGKILL. Ctrl+C uses cleanup too. The GPG unlock beforehand and nmcli activation afterward are outside that 120-second browser wait. Desktop keyring unlocking is a separate service interaction and can still require input.


### 5.11 How authenticator codes are made


The phone and KeePassXC can show the same code because they have the same long-term seed, compatible settings and roughly the same time. No SMS or network fetch is required to calculate a TOTP. The server also knows the enrollment secret and verifies the submitted code according to its own rules. A common 30-second configuration divides time into windows; all times within one window share a counter. A keyed hash mixes the secret and that counter, truncation selects part of the result, and modulo/padding produces the six/eight displayed digits.

```text
long-term secret + current time window + algorithm/settings
  → HMAC bytes → truncation → reduce to digit count → zero-padded code
```

A QR export contains the seed and metadata, not merely the digits currently shown. Replacing a code with a later one does not make an exposed seed harmless: the seed can calculate future codes too. The importer decodes that seed locally, shows a code for comparison, and expects you to paste the seed/settings into KeePassXC. Daily VPN login usually asks KeePassXC to generate the current code; the local current_code implementation is used by the importer and its tests.


### 5.12 Optional configuration example


The README's `config.example.json` is absent. The parser accepts the following shape in `~/.config/tifr-vpn/config.json` (or under your explicitly chosen XDG_CONFIG_HOME). This is an example to study, not a file I created in your personal config directory:

```json
{
  "database": "~/Documents/KeePass/Passwords.kdbx",
  "password_file": "~/.local/share/tifr-vpn/keepass-password.gpg",
  "entry": "TIFR"
}
```

JSON uses double-quoted property names/text, commas between properties and braces for an object. It has no comments in this parser and does not allow a trailing comma. Environment overrides win over each corresponding JSON property; a missing property uses the code's default. Do not put the actual master password, TIFR password, code or seed in this config.


### 5.13 Which setup command does what?


| Command | What it prepares | What it does not prepare |
| --- | --- | --- |
| `./install.sh` | Copies helper executables and creates public command links. | System packages, GPG keys, a vault or the NetworkManager profile. |
| `tifr-import-totp` | Displays one locally decoded enrollment seed/settings for manual import. | An automatic KeePass database write or an actual VPN connection. |
| `tifr-otp --setup` | Verifies local vault access and saves its master password as GPG ciphertext. | A server-side account login, VPN profile, or tunnel. |
| `tifrvpn --setup` | Creates/updates the NetworkManager OpenConnect connection recipe. | Credential enrollment or an immediate active tunnel. |
| `tifrvpn -c` | Uses a valid cached/fresh session and activates the tunnel. | A guarantee that future sessions never require user input. |


### 5.14 Tests, Git and dependencies


A unit test automatically compares a specific behavior with an expected outcome. A mock temporarily stands in for an external function/program: it returns invented data and remembers its calls. Temporary directories isolate installation/configuration tests from your actual home. The published RFC TOTP vector provides an independent expected answer. All 16 tests passed during this inspection; they do not test a real TIFR server, real passwords or actual GUI sign-in.

A Git commit records selected source-file contents in repository history, along with a message. `git add` chooses contents for the next commit (the staging area); `git commit` records them; `git push` sends commits to a remote. These operations do not deploy copied scripts to ~/bin/tifr. Your checkout currently includes the three quiet-mode commits suggested in the prior conversation: implementation, tests and documentation.

A dependency is software your program relies on. Direct Python dependencies are declared in pyproject.toml; dependencies of those packages are transitive dependencies. uv.lock records chosen versions and artifact hashes across environments. A virtual environment is a separate directory of Python interpreter/package configuration, letting projects avoid sharing every Python dependency. It does not replace system services such as NetworkManager or automatically supply native GI libraries. Python already includes argparse; its separate dependency declaration here is redundant for the project's Python 3.13 minimum.


### 5.15 Observations about this exact snapshot


- The working command is the root-level Zsh/Python toolchain. The src package's main function only prints a greeting.
- The README's example config file is missing, and the license's author/year placeholders are unfilled. These were observed, not changed.
- The NetworkManager service executable path is hardcoded, and several error hints use Fedora's dnf package names. This is Linux/desktop-specific code rather than a cross-platform application.
- The automatic OTP timing and migration import assume 30-second periods; the CLI output checks allow 6–8 ASCII digits.
- The browser is ephemeral but selected cookies are intentionally persisted in the desktop keyring. “Ephemeral browser profile” does not mean no sign-in state is ever saved.
- Process memory, clipboard clearing, permission bits and .gitignore address different concerns. Assigning a Python secret variable to None does not securely erase every copy; an anonymous file avoids a named plaintext secret file but is not an absolute no-disk/no-inspection guarantee.


### 5.16 A comfortable learning order


1. Understand commands, paths, arguments, exit statuses and the five-file map.
2. Read tifrvpn line 169, then the dispatcher, then status/disconnect, then connect and setup.
3. Learn Python functions, dictionaries, strings, if/for and subprocess with tifr-otp.py.
4. Read the authentication main/activate/authenticate functions before the long browser callback section.
5. Study the QR importer's current_code function, then its UI, then the binary parser.
6. Read tests to see examples of expected behavior, then packaging/lock metadata.

You can inspect source without executing the VPN: `nl -ba tifrvpn` prints numbered lines; `sed -n '58,77p' tifrvpn` prints the connect function; `git diff` shows working changes; and `python3 -B -m unittest discover -s tests -v` runs the existing offline checks. The full source/explanations below are a snapshot, so compare the recorded revision if the repository changes later.


## 6 File index

| File | Lines | Responsibility |
| --- | ---: | --- |
| [[#tifrvpn\|tifrvpn]] | 169 | Zsh command dispatch, profile setup, connect/disconnect/status |
| [[#tifr-otp.py\|tifr-otp.py]] | 199 | GPG-protected vault access, login fields and current TOTP |
| [[#tifr-vpn-auth.py\|tifr-vpn-auth.py]] | 496 | SSO browser, session cache, verified tunnel handoff |
| [[#tifr-import-totp\|tifr-import-totp]] | 6 | Symlink-aware QR importer launcher |
| [[#tifr-import-totp.py\|tifr-import-totp.py]] | 256 | Local QR decoding, TOTP calculation and Qt window |
| [[#install.sh\|install.sh]] | 57 | User installation, copied helpers and command symlinks |
| [[#tests/test_setup.py\|tests/test_setup.py]] | 112 | Offline installation, configuration, parsing and TOTP checks |
| [[#tests/test_quiet.py\|tests/test_quiet.py]] | 145 | Offline quiet-mode, prompt and cleanup checks |
| [[#pyproject.toml\|pyproject.toml]] | 23 | Python metadata, dependency ranges and placeholder package command |
| [[#src/tifrvpn_tui/__init__.py\|src/tifrvpn_tui/__init__.py]] | 2 | Two-line Python package placeholder |
| [[#.envrc\|.envrc]] | 1 | Optional direnv/uv development environment |
| [[#.python-version\|.python-version]] | 1 | Preferred development interpreter series |
| [[#.gitignore\|.gitignore]] | 38 | Generated-file and accidental secret-file exclusions |
| [[#README.md\|README.md]] | 182 | Installation, enrollment, usage and troubleshooting instructions |
| [[#uv.lock\|uv.lock]] | 356 | Exact dependency versions, artifacts, compatibility and hashes |
| [[#LICENSE\|LICENSE]] | 21 | Included license text and unfilled copyright placeholders |

## 7 Every file explained

The source below is embedded in this note. It does not depend on the repository remaining at the same path. Comments, imports, control flow, cleanup, error handling, tests, dependency records and documentation are all included.

### 7.1 tifrvpn

**169 lines** · Zsh command dispatch, profile setup, connect/disconnect/status.


This is the command dispatcher, written in Zsh. It checks your tools, creates or finds the NetworkManager connection profile, chooses connect/disconnect/status, and calls Python for authentication. It does not implement packet encryption itself. A function definition records a recipe; the recipe runs only when called. Read line 169, then function tifrvpn at 113, then the selected action. All five installed runtime files currently match the repository byte for byte.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.1.1 L1–L4 · Interpreter and adjacent helper path


```sh
#!/usr/bin/zsh -f
# NetworkManager/OpenConnect implementation; loaded only when invoked.
typeset _tifr_auth_helper="${0:A:h}/tifr-vpn-auth.py"
```

**Line-by-line explanation**

- **L1** — The shebang tells Linux to run this executable using /usr/bin/zsh. The -f option disables ordinary Zsh startup-file loading, reducing dependence on personal shell customizations; the system zshenv is an exception. This file requires Zsh syntax even if your interactive shell is Bash.
- **L2** — A comment for people. NetworkManager manages connection state; its OpenConnect plugin creates the VPN tunnel. Nothing on a comment line is executed.
- **L3** — typeset creates a shell variable. $0 is this script's name; :A makes its path absolute and resolves symbolic links; :h takes the containing directory. Appending /tifr-vpn-auth.py locates the neighboring helper without depending on your current directory. Double quotes preserve spaces in paths. The leading underscore is a naming convention, not privacy enforcement.


#### 7.1.2 L5–L13 · Check required networking tools


```sh
function _tifr_require_nm() {
  if ! (( $+commands[nmcli] && $+commands[openconnect] && $+commands[python3] )) ||
      [[ ! -x /usr/libexec/nm-openconnect-service ]]; then
    print -u2 -- 'Install dependencies listed in README.md (NetworkManager-openconnect, OpenConnect and system Python bindings).'
    return 1
  fi
  nmcli general status >/dev/null
}
```

**Line-by-line explanation**

- **L5** — Define the dependency-check function. The opening brace begins its body. Its commands execute when another function calls \_tifr\_require\_nm.
- **L6** — (( ... )) evaluates arithmetic/logical expressions. Zsh's $+commands\[name\] is 1 when that command is available in its command table, otherwise 0. && requires all three tools. ! negates the result: enter the error branch if any are missing. The trailing || also enters that branch if the next line's file check fails.
- **L7** — \[\[ ! -x path \]\] checks that the NetworkManager OpenConnect service executable is unavailable or not executable. This hardcoded path assumes a particular Linux packaging layout; other distributions may place it elsewhere. then begins the error branch.
- **L8** — print is Zsh's output command. -u2 sends this message to standard error, channel 2. -- ends print's options so the following text is treated literally as an argument.
- **L9** — Return failure status 1 from this function. Shell status 0 means success; nonzero means failure. This does not exit your interactive shell.
- **L10** — fi closes the if statement; shell uses if ... then ... fi rather than Python indentation.
- **L11** — Ask NetworkManager for its general state to check that it responds. >/dev/null discards standard output, while errors can still appear. Because this is the function's final command, its exit status becomes the function's status.
- **L12** — Close the dependency-check function.


#### 7.1.3 L14–L23 · Find one profile UUID


```sh
function _tifr_profile_uuid() {
  local uuid
  uuid=$(nmcli --get-values connection.uuid connection show id tifr-ivanti 2>/dev/null) || return 1
  if [[ -z "$uuid" || "$uuid" == *$'\n'* ]]; then
    print -u2 -- 'tifr VPN: expected one NetworkManager profile named tifr-ivanti.'
    return 1
  fi
  print -r -- "$uuid"
}
```

**Line-by-line explanation**

- **L14** — Define a function that prints the unique identifier of the saved connection profile named tifr-ivanti. A profile is a saved recipe for a connection; it can exist while disconnected.
- **L15** — Declare a function-local variable named uuid. UUID means universally unique identifier: a stable identifier that avoids relying on possibly duplicate display names.
- **L16** — $(...) captures a command's standard output. nmcli asks for only connection.uuid on the profile named tifr-ivanti. 2>/dev/null hides diagnostic messages here. || return 1 stops this helper if the lookup fails. Assignment itself adopts the substitution's exit status.
- **L17** — Reject an empty UUID (-z) or one containing a newline. \* is a pattern matching any characters; $'\\n' represents an actual newline. Multiple returned identifiers would mean the profile name is ambiguous.
- **L18** — Explain the uniqueness requirement on standard error.
- **L19** — Return a failure status for an absent or ambiguous identifier.
- **L20** — End the UUID validation condition.
- **L21** — Print the identifier for the caller's $(...) to capture. -r avoids interpreting backslash escapes. This printed value is data, not just a progress message.
- **L22** — End the UUID helper.


#### 7.1.4 L24–L38 · Validate and update an existing profile


```sh
function tifr-setup() {
  if (( $# != 0 )); then
    print -u2 -- 'Usage: tifr-setup'
    return 2
  fi
  _tifr_require_nm || return 1
  local uuid service
  if uuid=$(_tifr_profile_uuid); then
    service=$(nmcli --get-values vpn.service-type connection show uuid "$uuid") || return 1
    if [[ "$service" != org.freedesktop.NetworkManager.openconnect ]]; then
      print -u2 -- 'tifr VPN: tifr-ivanti exists but uses a different VPN plugin; rename it before setup.'
      return 1
    fi
    nmcli connection modify uuid "$uuid" connection.autoconnect no \
      +vpn.data 'gateway=https://sslvpn.tifr.res.in/tifruser,protocol=nc,prevent_invalid_cert=yes,cookie-flags=2,gateway-flags=2,gwcert-flags=2,resolve-flags=2' || return 1
```

**Line-by-line explanation**

- **L24** — Define setup of the NetworkManager profile. This differs from tifr-otp --setup, which prepares encrypted access to the password database.
- **L25** — $# is the number of function arguments. Setup accepts exactly zero, so any nonzero count is an argument error.
- **L26** — Print the expected standalone function syntax to standard error.
- **L27** — Return status 2, the convention this project uses for invalid command arguments.
- **L28** — Finish the argument check.
- **L29** — Run the dependency check; || return 1 means stop immediately if it fails.
- **L30** — Declare local variables for profile identifier and plugin service name.
- **L31** — Look up the existing profile and capture its identifier. The if condition tests the lookup's status, not whether the text happens to look truthy.
- **L32** — Read the profile's vpn.service-type. Stop if nmcli fails. This identifies the backend plugin configured for that saved profile.
- **L33** — Require the OpenConnect service identifier; a same-name profile for a different VPN backend must not be silently rewritten.
- **L34** — Explain the naming conflict and how the user can resolve it.
- **L35** — Return failure without modifying the mismatched profile.
- **L36** — End the plugin check.
- **L37** — Modify the existing profile by UUID and disable automatic connection. The final backslash joins this physical line to the next, making one long command.
- **L38** — Merge (+vpn.data) the gateway URL, nc protocol, certificate-verification setting and secret flags into existing plugin data. nc selects the Juniper Network Connect/Ivanti-compatible OpenConnect protocol. Values ending -flags=2 request that these transient secrets not be saved in the profile. Stop if modification fails.


#### 7.1.5 L39–L53 · Create a profile without duplicate names


```sh
  else
    # Do not create a second profile if the name is ambiguous or NM is unavailable.
    local names
    names=$(nmcli --get-values NAME connection show) || return 1
    if print -r -- "$names" | grep -Fxq -- tifr-ivanti; then
      print -u2 -- 'tifr VPN: ambiguous tifr-ivanti profile; resolve duplicate names before setup.'
      return 1
    fi
    nmcli connection add type vpn vpn-type openconnect con-name tifr-ivanti \
      connection.permissions "user:$(id -un)" connection.autoconnect no \
      vpn.data 'gateway=https://sslvpn.tifr.res.in/tifruser,protocol=nc,prevent_invalid_cert=yes,cookie-flags=2,gateway-flags=2,gwcert-flags=2,resolve-flags=2' || return 1
  fi
  print -P '%F{green}✔%f tifr VPN: Ivanti profile ready (NetworkManager/OpenConnect)'
}
```

**Line-by-line explanation**

- **L39** — Otherwise, no unambiguous existing profile was found, so consider creating one.
- **L40** — This comment explains the extra lookup: a failed lookup can indicate duplicate names or an unavailable service, not just a missing profile.
- **L41** — Declare a local variable to hold all existing connection names.
- **L42** — Retrieve profile names from NetworkManager; if this fails, stop rather than guessing that the profile is absent.
- **L43** — Pipe the names into grep. -F means literal text, -x requires an entire line, and -q suppresses output while preserving match status. If tifr-ivanti is already listed, the earlier lookup failure must not be treated as a clean absence.
- **L44** — Report an ambiguous profile name, avoiding creation of another duplicate.
- **L45** — Return failure before creating anything.
- **L46** — End the duplicate-name check.
- **L47** — Create a VPN profile using the OpenConnect plugin and give it the human-readable connection name tifr-ivanti. The backslash continues its arguments.
- **L48** — Restrict profile permissions to the current user, whose account name comes from id -un, and disable autoconnect. The operating system's authorization policy still applies; this is not a privilege bypass.
- **L49** — Set the same gateway, protocol, certificate check and transient-secret flags as in the update branch. || return 1 propagates creation failure.
- **L50** — Finish the update-or-create choice.
- **L51** — Print success. -P enables Zsh prompt formatting: %F{green} changes foreground color and %f resets it. The check mark is just a display character.
- **L52** — End setup.


#### 7.1.6 L54–L57 · Read connection state


```sh
function _tifr_nm_state() {
  LC_ALL=C nmcli --get-values GENERAL.STATE connection show uuid "$1"
}
```

**Line-by-line explanation**

- **L54** — Define the profile-state lookup helper.
- **L55** — Set LC\_ALL=C only for this nmcli invocation so state words are predictable English-like machine values. $1 is the first function argument, the UUID. GENERAL.STATE describes the current active connection state.
- **L56** — End the helper; nmcli's status is returned automatically.


#### 7.1.7 L58–L78 · Connect and invoke Python authentication


```sh
function tifr-on() {
  _tifr_require_nm || return 1
  local uuid state
  uuid=$(_tifr_profile_uuid) || {
    tifr-setup || return 1
    uuid=$(_tifr_profile_uuid) || return 1
  }
  state=$(_tifr_nm_state "$uuid") || return 1
  if [[ "$state" == activated ]]; then
    tifr-status
    return
  elif [[ -n "$state" && "$state" != deactivated ]]; then
    print -r -- "tifr VPN: $state; wait or run tifrvpn -d before retrying."
    return 1
  fi
  print -P '%F{yellow}⋯%f tifr VPN: checking saved sign-in for sslvpn.tifr.res.in'
  python3 "$_tifr_auth_helper" "$uuid" "$@" || return $?
  tifr-status || return 1
  notify-send -a tifrvpn 'tifr VPN' 'Connected' 2>/dev/null || true
}
```

**Line-by-line explanation**

- **L58** — Define the connect operation.
- **L59** — Stop if dependencies or NetworkManager access are unavailable.
- **L60** — Declare the identifier and state variables local to this call.
- **L61** — Try to locate the profile. If lookup fails, execute the brace group that follows ||. The braces group commands; they do not launch a separate subprocess.
- **L62** — Create/update the profile if needed, stopping on failure.
- **L63** — Retry lookup now that setup completed, and stop if still unsuccessful.
- **L64** — Close the fallback command group.
- **L65** — Capture the current connection state and stop if the query fails.
- **L66** — If already activated, avoid starting a second tunnel or new login.
- **L67** — Show the current connection details instead.
- **L68** — Return with the status from tifr-status; an argumentless return preserves the preceding command's status.
- **L69** — If the state is nonempty and is neither activated nor deactivated, a transition or another condition is in progress. -n means nonempty.
- **L70** — Show that state and suggest waiting or disconnecting before retrying.
- **L71** — Return failure instead of racing another activation.
- **L72** — End the state decision.
- **L73** — Print yellow progress text. This line reports what happens next, without printing a password or session cookie.
- **L74** — Run the neighboring Python authentication helper with the UUID and every argument supplied to tifr-on. "$@" preserves each original argument separately; this is how --quiet reaches Python. If it fails, $? is its exact status and is returned.
- **L75** — Confirm and show final connection status; fail if it does not report an active connection.
- **L76** — Try a desktop notification. Standard-error output is discarded, and || true prevents a missing notification service from turning a successful VPN connection into a failure.
- **L77** — End the connect function.


#### 7.1.8 L79–L95 · Disconnect


```sh
function tifr-off() {
  _tifr_require_nm || return 1
  local uuid state
  uuid=$(_tifr_profile_uuid) || {
    print -- 'tifr VPN: no tifr-ivanti profile; nothing to disconnect.'
    return 0
  }
  state=$(_tifr_nm_state "$uuid") || return 1
  if [[ -z "$state" || "$state" == deactivated ]]; then
    print -- 'tifr VPN: already disconnected'
    return 0
  fi
  nmcli --wait 20 connection down uuid "$uuid" || return $?
  print -P '%F{yellow}○%f tifr VPN: Disconnected'
  notify-send -a tifrvpn 'tifr VPN' 'Disconnected' 2>/dev/null || true
}
```

**Line-by-line explanation**

- **L79** — Define disconnect.
- **L80** — Check the required tools and NetworkManager.
- **L81** — Declare local identifier/state variables.
- **L82** — Attempt profile lookup and run the following group if no unique profile is found.
- **L83** — Tell the user that no identified profile is available to disconnect.
- **L84** — Return success because there is nothing to turn off. Notice that this branch also handles other lookup failures; it does not distinguish every possible cause.
- **L85** — Close that fallback group.
- **L86** — Ask for current state; stop if the query itself fails.
- **L87** — An empty state or deactivated state is treated as already disconnected.
- **L88** — Print that no disconnect operation is necessary.
- **L89** — Return success for an already disconnected connection.
- **L90** — Close this check.
- **L91** — Ask NetworkManager to bring this exact UUID down, waiting up to 20 seconds for the nmcli operation. Propagate its failure status.
- **L92** — Print the successful disconnect result in yellow.
- **L93** — Attempt a desktop notification, but ignore notification failure.
- **L94** — End disconnect.


#### 7.1.9 L96–L112 · Show status, addresses and DNS


```sh
function tifr-status() {
  _tifr_require_nm || return 1
  local uuid state
  uuid=$(_tifr_profile_uuid) || {
    print -- 'tifr VPN: not configured; run tifrvpn --setup'
    return 1
  }
  state=$(_tifr_nm_state "$uuid") || return 1
  if [[ "$state" != activated ]]; then
    print -r -- "tifr VPN: ${state:-disconnected}"
    return 1
  fi
  print -P '%F{green}●%f tifr VPN: Connected (Ivanti/OpenConnect)'
  nmcli --fields GENERAL.STATE,GENERAL.DEVICES,IP4.ADDRESS,IP4.DNS,IP6.ADDRESS,IP6.DNS \
    connection show uuid "$uuid"
}
```

**Line-by-line explanation**

- **L96** — Define the status-reporting operation.
- **L97** — Check access to the required tools and service.
- **L98** — Declare local identifier/state variables.
- **L99** — Find the unique saved profile or enter the explanatory error group.
- **L100** — Tell the user that setup is needed when the lookup fails.
- **L101** — Return failure because an active connection cannot be reported.
- **L102** — Close the lookup failure group.
- **L103** — Capture the connection state or stop if nmcli fails.
- **L104** — Any state other than activated is reported as not connected.
- **L105** — Print the actual state; ${state:-disconnected} substitutes disconnected when state is empty or unset. -r avoids backslash interpretation.
- **L106** — Return failure for a nonactive connection. This makes status usable in shell conditionals, not just by human readers.
- **L107** — Finish the nonactive-state branch.
- **L108** — Print a green connected marker.
- **L109** — Request selected details: state, devices, IPv4/IPv6 addresses and DNS servers. IP addresses identify interfaces; DNS servers translate names into addresses. A backslash continues the command.
- **L110** — Show those fields for the exact profile UUID.
- **L111** — End status.


#### 7.1.10 L113–L127 · Parse command arguments


```sh
function tifrvpn() {
  local action='' argument
  local -i quiet=0
  for argument in "$@"; do
    case "$argument" in
      --quiet) quiet=1 ;;
      -c|-d|-s|--setup|--forget-login|-h|--help)
        if [[ -n "$action" ]]; then
          print -u2 -- 'Choose one action: -c, -d, -s, --setup, --forget-login or --help.'
          return 2
        fi
        action=$argument ;;
      *) print -u2 -- 'Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login|--help]'; return 2 ;;
    esac
  done
```

**Line-by-line explanation**

- **L113** — Define the main dispatcher, sharing the executable's name. Defining a function does not itself call it; line 169 performs that call.
- **L114** — Start with no selected action and declare the variable used to inspect each command-line argument. '' is an empty string.
- **L115** — Create an integer variable quiet initialized to 0. Here 0/1 represents an off/on flag; do not confuse that convention with shell success status, where 0 means success.
- **L116** — Loop over the original arguments, one at a time. Quoted "$@" keeps arguments containing spaces intact.
- **L117** — Begin pattern-based dispatch for the current argument.
- **L118** — The --quiet option switches quiet to 1; ;; terminates this case arm.
- **L119** — These alternative patterns are the accepted main actions. A | within a case pattern means any listed alternative matches.
- **L120** — If a main action has already been chosen, a second action is rejected, even if it repeats the first.
- **L121** — Explain that one main action must be chosen.
- **L122** — Return argument-error status 2.
- **L123** — Close the duplicate-action check.
- **L124** — Store the selected action and finish this case arm. The parser does not act immediately, so --quiet can appear before or after -c.
- **L125** — The \* fallback matches any unrecognized argument, prints usage and returns status 2. Semicolons separate multiple commands on one physical line.
- **L126** — esac closes a case statement; it is case spelled backwards.
- **L127** — done closes the argument loop.


#### 7.1.11 L128–L142 · Validate quiet mode and dispatch actions


```sh
  if (( quiet )); then
    if [[ -n "$action" && "$action" != -c ]]; then
      print -u2 -- '--quiet is only supported when connecting (-c).'
      return 2
    fi
    action=-c
  fi
  case "$action" in
    -c)
      if (( quiet )); then tifr-on --quiet; else tifr-on; fi
      return ;;
    -d) tifr-off; return ;;
    -s) tifr-status; return ;;
    --setup) tifr-setup; return ;;
    --forget-login) python3 "$_tifr_auth_helper" --forget-login; return ;;
```

**Line-by-line explanation**

- **L128** — If the integer flag quiet is nonzero, apply its action restrictions.
- **L129** — Reject combining quiet with an explicitly chosen action other than -c. This prevents --quiet -d or --quiet --setup from being silently accepted.
- **L130** — Explain the allowed quiet-mode combination.
- **L131** — Return invalid-arguments status 2.
- **L132** — Finish quiet-mode compatibility checking.
- **L133** — Make quiet alone mean connect. Thus tifrvpn --quiet and tifrvpn -c --quiet select the same action.
- **L134** — Finish quiet-mode handling.
- **L135** — Dispatch the validated action.
- **L136** — Begin the explicit connect case.
- **L137** — Call tifr-on with --quiet when requested, otherwise call it without arguments. The shell's if can be written on one line using semicolons.
- **L138** — Return the action's status and end this case arm.
- **L139** — For -d call disconnect, return its status and end the arm.
- **L140** — For -s call status, return its status and end the arm.
- **L141** — For --setup create/update the NetworkManager profile and return its status.
- **L142** — For --forget-login call Python's special state-clearing mode. This clears cached sessions, not the password vault and not an existing tunnel.


#### 7.1.12 L143–L155 · Print help


```sh
    -h|--help)
      print -r -- 'Usage: tifrvpn [-c [--quiet]|-d|-s|--setup|--forget-login] (no option: toggle)'
      print -r -- 'Server: https://sslvpn.tifr.res.in/tifruser (Ivanti SSL VPN)'
      print -r -- 'Reuses a valid saved session; otherwise fills TIFR SSO from KeePassXC/GPG.'
      print -r -- 'TIFR may ask you to confirm replacing another active session.'
      print -r -- '--quiet hides the SSO browser using Xvfb (120-second limit); terminal messages remain visible.'
      print -r -- '--quiet alone connects. GPG can prompt before background sign-in; retry without --quiet if TIFR needs input.'
      print -r -- '--forget-login clears remembered sign-in state from the desktop keyring.'
      print -r -- 'TOTP from KeePassXC/GPG: tifr-otp (first run: tifr-otp --setup)'
      return 0 ;;
    '') ;;
    *) print -u2 -- 'Usage: tifrvpn [-c|-d|-s|--setup|--forget-login|--help]'; return 2 ;;
  esac
```

**Line-by-line explanation**

- **L143** — Either -h or --help enters the help arm.
- **L144** — Print syntax. Brackets describe optional arguments in help text; they are not characters to type as part of the command.
- **L145** — Print the intended VPN portal address.
- **L146** — Explain the cached-session-first behavior.
- **L147** — Explain that the server can require an explicit decision about an existing session.
- **L148** — Describe quiet mode's hidden graphical browser and 120-second browser-process limit. This limit excludes earlier GPG prompting and later tunnel activation.
- **L149** — Document quiet-alone behavior and the visible fallback for required user input.
- **L150** — Describe clearing cached login state from the desktop keyring.
- **L151** — Point to the separate OTP command and its credential setup action.
- **L152** — Help is a successful operation, so return 0.
- **L153** — An empty action matches this arm, which deliberately does nothing. Execution then continues below to implement toggle behavior.
- **L154** — Defensive fallback for an unexpected internal action value; ordinary unknown arguments have already been rejected earlier.
- **L155** — End the action case statement.


#### 7.1.13 L156–L169 · Toggle behavior and actual entry point


```sh
  _tifr_require_nm || return 1
  local uuid state
  if uuid=$(_tifr_profile_uuid); then
    state=$(_tifr_nm_state "$uuid") || return 1
    if [[ -n "$state" && "$state" != deactivated ]]; then
      tifr-off
      return
    fi
  fi
  tifr-on
}


tifrvpn "$@"
```

**Line-by-line explanation**

- **L156** — The remaining path is toggle mode: first verify tools/service.
- **L157** — Declare local variables for toggle's profile/state lookup.
- **L158** — If a unique profile exists, inspect its state.
- **L159** — Get state or return failure if the query fails.
- **L160** — If there is a nonempty state other than deactivated, choose disconnect. This includes connecting transitions, not just fully active connections.
- **L161** — Run disconnect.
- **L162** — Return its status so toggle does not then reconnect.
- **L163** — Close the state test.
- **L164** — Close the profile-exists test.
- **L165** — Otherwise connect, creating the profile if necessary through tifr-on.
- **L166** — End the dispatcher function.
- **L169** — Call the dispatcher with the script's original arguments. This is the entry point after all function definitions have been read. Without this line, executing the file would mostly define functions and then exit.


[[#File index|↑ File index]]

### 7.2 tifr-otp.py

**199 lines** · GPG-protected vault access, login fields and current TOTP.


This helper reads credentials and time-based one-time codes from KeePassXC. The KeePass database contains the VPN username, VPN password and TOTP seed. A separate GPG-encrypted file contains the database master password. configuration() chooses paths; decrypt_password() obtains the master password; read_login()/read_code() ask keepassxc-cli to open the vault. --setup asks for the master password in a local graphical dialog, verifies it locally and encrypts it. The graphical KeePassXC application need not be running because the CLI opens the database itself.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.2.1 L1–L14 · Interpreter, documentation and imports


```python
#!/usr/bin/env python3
"""Read a TIFR TOTP from KeePassXC using a GPG-encrypted database password."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
```

**Line-by-line explanation**

- **L1** — Use env to find python3 on PATH and run this executable with that interpreter. The interpreter found can depend on an active virtual environment.
- **L2** — A module docstring: explanatory text Python stores as \_\_doc\_\_. argparse later reuses it as help text.
- **L4** — Import argparse, Python's standard command-line argument parser; it understands options such as --setup and --recipient.
- **L5** — Import JSON conversion support for reading a small settings file.
- **L6** — Import operating-system features: environment variables, file synchronization and atomic replacement.
- **L7** — Import Path, a class for filesystem paths. The / operator on Paths joins path components rather than dividing numbers.
- **L8** — Import regular expressions for checking that generated codes contain the expected digits.
- **L9** — Import shutil, used here to locate external programs on PATH.
- **L10** — Import subprocess to start gpg, keepassxc-cli or flatpak and communicate through pipes.
- **L11** — Import Python process information and input/output streams, including stdin, stderr and exit status handling.
- **L12** — Import temporary-file support for writing ciphertext safely before replacing the final file.


#### 7.2.2 L15–L24 · Build the KeePassXC command


```python
def keepass_command(database, entry):
    if shutil.which("keepassxc-cli"):
        command = ["keepassxc-cli"]
    elif shutil.which("flatpak"):
        command = ["flatpak", "run", "--command=keepassxc-cli", "org.keepassxc.KeePassXC"]
    else:
        raise RuntimeError("Install KeePassXC or its Flatpak first.")
    return command + ["show", "--quiet", "--totp", str(database), entry]
```

**Line-by-line explanation**

- **L15** — Define a function accepting a database path and an entry name. It returns a list of command arguments; it does not yet run KeePassXC.
- **L16** — shutil.which returns the path of an available executable, or None. Prefer a natively installed KeePassXC CLI.
- **L17** — Start the command argument list with keepassxc-cli.
- **L18** — If the native CLI was not found, check whether Flatpak is available as an alternative launcher.
- **L19** — Construct a Flatpak command that runs keepassxc-cli inside the KeePassXC application. Flatpak being installed does not itself prove that this application is installed; execution can still fail later.
- **L20** — Neither launcher was found, so take the error branch.
- **L21** — Raise a human-readable RuntimeError. Raising interrupts normal flow until an appropriate except handler catches it.
- **L22** — Append show, quiet output, --totp, database filename and entry name. str(database) converts the Path object into text. List + concatenates argument lists; each element becomes one argument, so spaces in paths stay intact.


#### 7.2.3 L25–L37 · Read the current TOTP


```python
def read_code(password, database, entry):
    if any(char in password for char in "\r\n\0"):
        raise RuntimeError("The database password must be a single line.")
    result = subprocess.run(
        keepass_command(database, entry), input=password + "\n",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    code = result.stdout.strip()
    if result.returncode or not re.fullmatch(r"[0-9]{6,8}", code):
        raise RuntimeError("Could not unlock KeePassXC or read the entry's TOTP. Check the password, database and entry name.")
    return code
```

**Line-by-line explanation**

- **L25** — Define the function for obtaining the current TOTP using the database master password.
- **L26** — Reject carriage return, newline or NUL in the password. any(...) tests whether any character in this group appears. The CLI input protocol uses a single password line.
- **L27** — Raise an error when that one-line assumption is not satisfied.
- **L28** — Start the subprocess.run call, which waits for the child command to finish.
- **L29** — Obtain the command list and feed the master password plus a terminating newline to the child through standard input. The password is not an argument in the process command line.
- **L30** — Capture both normal output and diagnostic output in pipes; text=True converts captured output into Python strings. These pipes are process communication channels, not terminal output files.
- **L31** — Close the call and assign its CompletedProcess result to result.
- **L32** — Remove surrounding whitespace from output to obtain the candidate numeric code.
- **L33** — Reject a failed child command or output that does not fully match 6 through 8 ASCII digits. r"..." is a raw string, useful for regular expressions. The regex also technically accepts 7 digits.
- **L34** — Give a generic diagnostic rather than printing captured secret-bearing output.
- **L35** — Return the validated code to the caller. Only main() explicitly prints it for the standalone OTP command.


#### 7.2.4 L38–L54 · Read login fields without printing them


```python
def read_login(password, database, entry):
    """Return login fields in memory; never expose them as CLI output."""
    if any(char in password for char in "\r\n\0"):
        raise RuntimeError("The database password must be a single line.")
    command = keepass_command(database, entry)
    # Explicitly request the protected value, captured only in this process.
    command = command[:-2] + ["--show-protected", "-a", "UserName", "-a", "Password"] + command[-2:]
    result = subprocess.run(command, input=password + "\n", stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    fields = result.stdout.splitlines()
    if result.returncode or len(fields) != 3 or not re.fullmatch(r"[0-9]{6,8}", fields[2]):
        raise RuntimeError("Could not read the KeePassXC login entry and TOTP.")
    if not fields[0].strip() or not fields[1]:
        raise RuntimeError("Fill the Username and Password fields of the TIFR entry in KeePassXC, then save the database.")
    return {"username": fields[0].strip(), "password": fields[1]}
```

**Line-by-line explanation**

- **L38** — Define the function that returns the saved username/password in memory.
- **L39** — Docstring explains the intended output boundary: this function returns fields; it does not print them to the terminal.
- **L40** — Repeat the one-line master-password validation before using the CLI.
- **L41** — Raise the corresponding input-protocol error.
- **L42** — Get the ordinary show/--totp command arguments.
- **L43** — Comment explains that protected password data must be requested explicitly and captured.
- **L44** — Insert --show-protected and two -a attribute selections just before the database and entry arguments. command\[:-2\] is all but the last two elements; command\[-2:\] is those final two. It asks for UserName and Password while retaining TOTP output.
- **L45** — Run KeePassXC, supplying the master password on stdin and capturing stdout.
- **L46** — Also capture diagnostic output and request text conversion.
- **L47** — Split the returned text into lines: expected username, password and a current TOTP.
- **L48** — Require successful execution, exactly three output lines, and a 6-to-8-digit code on line three. Python's or short-circuits, so fields\[2\] is not accessed if the line count is wrong.
- **L49** — Raise a generic vault-entry parsing error.
- **L50** — Require a nonblank username and a nonempty password. Username whitespace is stripped; password whitespace is preserved because it can be meaningful.
- **L51** — Explain that the user must fill and save the entry's login fields.
- **L52** — Return a dictionary containing username and password. The code from this CLI call validated the entry but is deliberately not returned here; fresh codes are requested later at the OTP form step.


#### 7.2.5 L55–L75 · Load and validate configuration


```python
def configuration():
    config_path = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))).expanduser() / "tifr-vpn/config.json"
    try:
        settings = json.loads(config_path.read_text()) if config_path.exists() else {}
    except (OSError, ValueError):
        raise RuntimeError(f"Could not read valid JSON configuration: {config_path}") from None
    if (not isinstance(settings, dict) or set(settings) - {"database", "password_file", "entry"}
            or any(not isinstance(value, str) or not value.strip() for value in settings.values())):
        raise RuntimeError("Configuration accepts only nonempty database, entry and password_file strings.")
    database = Path(os.environ.get("TIFR_KEEPASS_DATABASE", settings.get("database", "~/Documents/KeePass/Passwords.kdbx"))).expanduser()
    password_file = Path(os.environ.get("TIFR_KEEPASS_PASSWORD_FILE", settings.get("password_file", "~/.local/share/tifr-vpn/keepass-password.gpg"))).expanduser()
    entry = os.environ.get("TIFR_KEEPASS_ENTRY", settings.get("entry", "TIFR"))
    if not database.is_absolute() or not password_file.is_absolute() or not entry.strip():
        raise RuntimeError("Use absolute paths (or ~/ paths) and a nonempty KeePassXC entry name.")
    if not database.is_file():
        raise RuntimeError(f"Database not found: {database}. Set TIFR_KEEPASS_DATABASE to its path.")
    if not shutil.which("gpg"):
        raise RuntimeError("GPG is required.")
    return database, password_file, entry
```

**Line-by-line explanation**

- **L55** — Define configuration loading and validation.
- **L56** — Use XDG\_CONFIG\_HOME when provided, otherwise ~/.config, then append tifr-vpn/config.json. Path.home() finds the home directory, expanduser() expands a leading ~, and / joins directory components.
- **L57** — Begin handling potential file/JSON errors.
- **L58** — If the optional file exists, read and decode it as JSON; otherwise use an empty dictionary and later defaults. A conditional expression is 'value\_if\_true if condition else value\_if\_false'.
- **L59** — Catch file access errors or invalid JSON/value errors.
- **L60** — Raise a concise configuration error. 'from None' hides a chained traceback context when the exception is eventually displayed.
- **L61** — Require a dictionary and reject any keys outside database, password\_file and entry. set(settings) is the set of dictionary keys; set subtraction reveals unsupported keys.
- **L62** — Require every supplied JSON value to be a string with nonwhitespace content. A generator expression checks all values without building a list.
- **L63** — Report invalid configuration shape or values.
- **L64** — Select the database path by precedence: TIFR\_KEEPASS\_DATABASE environment variable, then JSON database field, then the default vault path. Expand ~ in the chosen value.
- **L65** — Choose the encrypted master-password file using the same environment → config → default precedence. This file contains GPG ciphertext, not the VPN password in plaintext.
- **L66** — Choose the KeePassXC entry path, defaulting to TIFR. A grouped entry can instead be named VPN/TIFR.
- **L67** — Require absolute resolved-style paths after ~ expansion and a nonblank entry. is\_absolute checks path form; it does not guarantee the path exists.
- **L68** — Explain unsupported relative paths or an empty entry name.
- **L69** — Check that the chosen database is an existing regular file.
- **L70** — Report the missing database's path and the relevant override variable. f"...{database}..." inserts a Python value into text.
- **L71** — Require an available gpg executable.
- **L72** — Raise a clear missing-dependency error.
- **L73** — Return three values as a tuple: database, encrypted password path, entry. The caller can unpack them into three variables.


#### 7.2.6 L76–L93 · Decrypt the vault master password


```python
def decrypt_password(password_file, *, allow_prompt=True):
    if not password_file.is_file():
        raise RuntimeError("Encrypted password file not found. Run tifr-otp --setup first.")
    if sys.stdin.isatty():
        os.environ["GPG_TTY"] = os.ttyname(sys.stdin.fileno())
    command = ["gpg", "--quiet"]
    if not allow_prompt:
        # A pinentry window on Xvfb would be invisible. Fail instead of waiting.
        command += ["--batch", "--no-tty", "--pinentry-mode", "error"]
    decrypted = subprocess.run(
        command + ["--decrypt", "--", str(password_file)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if decrypted.returncode:
        raise RuntimeError("Could not decrypt the password file. Unlock your GPG key and retry.")
    return decrypted.stdout.decode("utf-8").removesuffix("\n").removesuffix("\r")
```

**Line-by-line explanation**

- **L76** — Define decryption. The \* means allow\_prompt is keyword-only: callers must write allow\_prompt=False rather than passing an unexplained positional boolean. It defaults to allowing prompts.
- **L77** — Require the ciphertext file to exist before invoking GPG.
- **L78** — Explain the setup step if ciphertext is absent.
- **L79** — Check whether standard input is attached to a terminal, rather than a pipe or file.
- **L80** — When attached, tell GPG the terminal device name through GPG\_TTY so a terminal pinentry can use it.
- **L81** — Begin a gpg command with reduced routine output.
- **L82** — When prompting is forbidden, add flags for noninteractive failure instead of waiting for an invisible unlock window.
- **L83** — The comment explains the quiet-mode hazard: pinentry must not appear on the hidden display.
- **L84** — --batch and --no-tty avoid interactive command-line input; --pinentry-mode error asks GPG to fail if a new pinentry prompt would be necessary. A cached unlock may still work.
- **L85** — Run decryption and capture its result.
- **L86** — --decrypt selects decryption; -- ends option parsing before the filename. The ciphertext pathname can appear in arguments, but the decrypted master password does not.
- **L87** — Capture output/error as bytes because text=True is omitted. This avoids printing the plaintext result to the terminal.
- **L88** — End the subprocess call.
- **L89** — A nonzero return code means decryption failed.
- **L90** — Give a generic unlock instruction without exposing decrypted data or raw GPG output.
- **L91** — Decode the decrypted UTF-8 bytes and remove at most one final newline then one final carriage return. This tolerates a conventional line ending while preserving other password characters; strip() would remove meaningful spaces.


#### 7.2.7 L94–L116 · Select a GPG recipient


```python
def recipient_key(explicit):
    if explicit:
        return explicit
    result = subprocess.run(
        ["gpg", "--batch", "--with-colons", "--list-secret-keys", "--fingerprint"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
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
        raise RuntimeError("Specify your GPG encryption key: tifr-otp --setup --recipient FINGERPRINT")
    return keys[0]
```

**Line-by-line explanation**

- **L94** — Define recipient-key selection for setup. A recipient identifies whose GPG public key encrypts the master password; the corresponding secret key decrypts it later.
- **L95** — If the user explicitly supplied a recipient, use that value.
- **L96** — Return the explicit identifier without trying automatic selection.
- **L97** — Otherwise ask GPG for available secret-key records.
- **L98** — --with-colons requests machine-parseable records; --fingerprint includes stable key identifiers; --list-secret-keys lists locally available private-key records. --batch avoids interactive selection.
- **L99** — Capture text output; check=True raises CalledProcessError if GPG exits unsuccessfully.
- **L100** — Finish the command invocation.
- **L101** — Start a list for candidate fingerprints.
- **L102** — Track whether the most recent primary-key record qualifies for encryption.
- **L103** — Process the machine-readable output one line at a time.
- **L104** — Split a record into colon-separated fields. Python indexes start at 0: parts\[1\] is the second field.
- **L105** — sec identifies a primary secret-key record.
- **L106** — Accept a primary record unless its validity flag is revoked, expired or disabled, and require encryption capability in field 12. .lower() accepts both e and E capability markers. This is this program's selection heuristic, not a full replacement for GPG's own key validation.
- **L107** — ssb identifies a secret subkey record.
- **L108** — Do not collect the following subkey fingerprint as a separate primary-key candidate.
- **L109** — When a fingerprint record follows an eligible primary record, collect it.
- **L110** — The fingerprint is in the tenth colon-separated field.
- **L111** — Reset eligibility so the same primary key is not collected repeatedly.
- **L112** — Require exactly one automatically selected key. Zero or multiple candidates require an explicit user choice.
- **L113** — Explain the command syntax for selecting a recipient fingerprint.
- **L114** — Return the sole candidate's fingerprint; index 0 selects the first list element.


#### 7.2.8 L117–L145 · Prompt and verify the vault password


```python
def setup(password_file, database, entry, recipient):
    from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox

    app = QApplication.instance() or QApplication([])
    if password_file.exists() or password_file.is_symlink():
        answer = QMessageBox.question(
            None, "TIFR OTP setup", f"Replace the encrypted password file?\n{password_file}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return 130
    recipient = recipient_key(recipient)
    while True:
        password, accepted = QInputDialog.getText(
            None, "TIFR OTP — encrypt KeePassXC password",
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

- **L117** — Define interactive setup for encrypting the database master password.
- **L118** — Import Qt widgets only when setup is actually used, so ordinary code retrieval does not need to import the whole Qt GUI here.
- **L120** — Reuse a running QApplication or create one. The or expression selects the existing application if it is present.
- **L121** — If a destination file or even a broken symlink already exists, ask before replacing it.
- **L122** — Open a graphical question dialog and store the user's chosen button.
- **L123** — Supply no parent window, a title and a message containing the destination pathname. \\n inserts a line break in the displayed message.
- **L124** — Offer Yes and No buttons. | combines Qt button flags; it is a bitwise operation, not shell piping.
- **L125** — Make No the default, so an accidental Enter does not approve replacement.
- **L126** — Finish the dialog call.
- **L127** — If the answer is anything other than Yes, treat it as cancellation.
- **L128** — Return 130, this project's cancellation status convention.
- **L129** — Resolve the chosen encryption recipient before collecting the master password.
- **L130** — Loop until a correct database password is verified or the user cancels.
- **L131** — Open a text-input dialog and unpack its result into entered password and accepted/cancelled flag.
- **L132** — Give the local dialog a descriptive title.
- **L133** — Show the database pathname and clearly ask for its master password.
- **L134** — Explain that verification happens locally and the result will be encrypted with GPG. Adjacent string literals join automatically in Python.
- **L135** — Distinguish the vault master password from the TIFR account's separate password.
- **L136** — Mask the input field using Qt's Password echo mode.
- **L137** — Finish the input dialog call.
- **L138** — Check for cancellation rather than trying to use cancelled input.
- **L139** — Return cancellation status.
- **L140** — Begin an attempt that may fail because the password or entry is incorrect.
- **L141** — Verify that the master password opens the configured database and that the entry provides username/password/TOTP. This does not submit a login to TIFR or prove that the server accepts the saved VPN password.
- **L142** — Catch a readable local verification error.
- **L143** — Display that reason in a warning dialog.
- **L144** — continue restarts the while loop so the user can correct the input.
- **L145** — break exits the loop once verification succeeded.


#### 7.2.9 L146–L172 · Encrypt and atomically save ciphertext


```python
    result = subprocess.run(
        ["gpg", "--batch", "--encrypt", "--recipient", recipient, "--output", "-"],
        input=password.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    password = None
    if result.returncode or not result.stdout:
        raise RuntimeError("GPG encryption failed; no password file was written. Check the recipient key.")
    password_file.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if password_file.parent == Path.home() / ".local/share/tifr-vpn":
        password_file.parent.chmod(0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=password_file.parent, prefix=".keepass-password-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(result.stdout)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, password_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Verified the TOTP entry and saved the GPG-encrypted database password: {password_file}", flush=True)
    QMessageBox.information(None, "TIFR OTP ready", "The encrypted password file is ready.\n\nRun tifr-otp to get the current code.")
    return 0
```

**Line-by-line explanation**

- **L146** — Start a GPG encryption subprocess.
- **L147** — Encrypt for the selected recipient; --output - sends ciphertext to stdout so Python can capture it rather than having GPG write the final destination directly.
- **L148** — Encode the master password as UTF-8 bytes and send it on stdin. Capture both ciphertext and diagnostics as bytes.
- **L149** — Finish the encryption call.
- **L150** — Remove this variable's reference to the plaintext password. This is not guaranteed secure memory erasure: Python/Qt/operating-system copies may remain until reclaimed.
- **L151** — Require successful encryption and a nonempty ciphertext result before any destination replacement.
- **L152** — Explain encryption failure while leaving the old password file unchanged.
- **L153** — Create the parent directory with requested mode 700: owner-only read/write/traverse. exist\_ok=True tolerates an existing directory; creation mode alone does not change permissions of an existing one.
- **L154** — Check whether this is the standard private application directory.
- **L155** — For that standard directory, explicitly enforce owner-only 700 permissions even when it already exists. Custom directory permissions are not forcibly rewritten here.
- **L156** — Initialize temporary to None so cleanup knows whether a temporary pathname was created.
- **L157** — Begin a try/finally block, ensuring cleanup runs even on failure.
- **L158** — Create a temporary ciphertext file in the destination directory. delete=False keeps it until explicit replacement/cleanup. Same-directory placement allows atomic filesystem replacement under normal local-filesystem behavior.
- **L159** — Remember the temporary file's pathname for permissions and cleanup.
- **L160** — Write encrypted bytes, never the plaintext password, to that temporary file.
- **L161** — Flush Python's buffered bytes to the underlying operating-system file handle.
- **L162** — Ask the operating system to synchronize the file contents using fsync. This improves durability; the code does not additionally fsync the parent directory.
- **L163** — Set file permissions to 600: owner can read/write; group and others have no permission bits.
- **L164** — Atomically replace the destination pathname with the completed temporary ciphertext file. This avoids leaving a half-written target during an ordinary interrupted write.
- **L165** — The finally body executes whether writing/replacement succeeds or raises an exception.
- **L166** — Only attempt temporary-path cleanup if a pathname was actually created.
- **L167** — Delete a leftover temporary file; missing\_ok=True tolerates it already having been renamed into place.
- **L168** — Print the ciphertext location, not the master password. flush=True sends output immediately rather than waiting in a buffer.
- **L169** — Show a completion dialog explaining how to obtain the current OTP.
- **L170** — Return success.


#### 7.2.10 L173–L187 · Parse arguments and choose setup or code output


```python
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true", help="prompt locally and encrypt the database password")
    parser.add_argument("--recipient", help="GPG recipient fingerprint for setup")
    args = parser.parse_args()
    if args.recipient and not args.setup:
        parser.error("--recipient requires --setup")
    database, password_file, entry = configuration()
    if args.setup:
        return setup(password_file, database, entry, args.recipient)
    password = decrypt_password(password_file)
    print(read_code(password, database, entry))
    return 0
```

**Line-by-line explanation**

- **L173** — Define the standalone command's top-level behavior.
- **L174** — Create an argument parser using the module docstring for its description.
- **L175** — Register --setup as an on/off flag; store\_true makes it False when absent and True when supplied.
- **L176** — Register --recipient as an option that takes a following value.
- **L177** — Parse command-line arguments into an object with attributes such as args.setup.
- **L178** — Reject a recipient selection when setup was not requested, because ordinary code retrieval does not encrypt anything.
- **L179** — argparse prints its usage/error and exits with its argument-error status.
- **L180** — Load and validate configuration, unpacking the three returned values.
- **L181** — If setup was selected, run the interactive encryption workflow.
- **L182** — Return setup's success/cancellation/failure result.
- **L183** — Otherwise decrypt the saved database master password, allowing an ordinary GPG unlock prompt if required.
- **L184** — Ask KeePassXC for a fresh code and explicitly print it. This command intentionally exposes the short-lived code in your terminal; read\_login itself does not print login fields.
- **L185** — Return success after code output.


#### 7.2.11 L188–L199 · Main guard and safe error messages


```python
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTIFR OTP: cancelled.", file=sys.stderr)
        sys.exit(130)
    except RuntimeError as error:
        print(f"TIFR OTP: {error}", file=sys.stderr)
        sys.exit(1)
    except (OSError, UnicodeError, subprocess.SubprocessError, ImportError):
        print("TIFR OTP: operation failed. No password or code was logged.", file=sys.stderr)
        sys.exit(1)
```

**Line-by-line explanation**

- **L188** — The main guard runs the following block only when this file is executed as a program. Loading its definitions with runpy without run\_name='\_\_main\_\_' does not run this CLI workflow.
- **L189** — Begin top-level error handling.
- **L190** — Run main and turn its integer result into the process exit status.
- **L191** — Catch Ctrl+C, represented by KeyboardInterrupt in Python.
- **L192** — Write a cancellation message to standard error, starting on a fresh line.
- **L193** — Exit with cancellation status 130.
- **L194** — Catch the readable RuntimeError errors deliberately raised by helper functions.
- **L195** — Display only the exception's intended message with a command prefix.
- **L196** — Exit with ordinary failure status 1.
- **L197** — Catch common filesystem, encoding, subprocess and missing-library problems without exposing exception internals that might contain sensitive data.
- **L198** — Print a generic failure diagnostic. This describes intended logging behavior; it is not a guarantee against every external program or OS-level trace.
- **L199** — Exit failure.


[[#File index|↑ File index]]

### 7.3 tifr-vpn-auth.py

**496 lines** · SSO browser, session cache, verified tunnel handoff.


This is the bridge between web login and VPN tunnel activation. main() validates the saved NetworkManager profile, tries a cached session, and otherwise starts this same Python file in a separate browser mode. login_cookie() creates a small GTK/WebKit browser, restores remembered TIFR cookies, fills only the specified TIFR SSO forms, validates a DSID session, and returns it. activate() verifies the VPN server certificate and hands transient credentials to nmcli using a Linux anonymous file descriptor. The actual tunnel is managed by NetworkManager/OpenConnect. Much of this file defines callbacks: functions the graphical event loop calls later, after a browser operation finishes.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.3.1 L1–L24 · Interpreter, libraries and gateway constants


```python
#!/usr/bin/env python3
"""Sign in to TIFR SSO, then hand an in-memory session to NetworkManager."""

import argparse
import base64
import hashlib
import json
import os
import runpy
import shutil
import signal
import socket
import ssl
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, HTTPSHandler

URL = "https://sslvpn.tifr.res.in/tifruser"
HOST = "sslvpn.tifr.res.in"
BACKGROUND_TIMEOUT = 120
```

**Line-by-line explanation**

- **L1** — Run using the python3 executable found by env on PATH.
- **L2** — Module docstring summarizes the helper's responsibility and becomes its argument-parser description.
- **L4** — argparse reads the profile UUID and optional --quiet flag.
- **L5** — base64 converts binary fingerprint bytes into transport-friendly text. Base64 is encoding, not encryption.
- **L6** — hashlib computes SHA-256 for the server public-key fingerprint.
- **L7** — json converts browser status, cookie records and credential data between structured values and text.
- **L8** — os provides environment variables, process groups and Linux file-descriptor operations.
- **L9** — runpy loads definitions from the adjacent hyphenated tifr-otp.py filename, which is inconvenient to import using an ordinary Python module name.
- **L10** — shutil locates quiet-mode executables on PATH.
- **L11** — signal supplies named Unix signals such as SIGTERM and SIGKILL.
- **L12** — socket opens a TCP network connection to the gateway for TLS certificate inspection.
- **L13** — ssl verifies HTTPS/TLS certificates using the system's trusted certificate authorities.
- **L14** — subprocess launches browser child processes and nmcli.
- **L15** — sys provides the current interpreter path, argument list, streams and exit functions.
- **L16** — time provides the current time for OTP boundaries and cookie expiry checks.
- **L17** — HTTPError represents HTTP error responses, including redirects deliberately not followed by this code.
- **L18** — urlsplit separates a URL into scheme, hostname, port, path and related pieces.
- **L19** — Import HTTP request/opener components so a saved cookie can be tested without a full graphical browser.
- **L21** — Constant for the portal URL used for sign-in and profile validation. Uppercase names conventionally indicate constants; Python does not enforce immutability.
- **L22** — Constant for the gateway hostname alone, without a scheme or path.
- **L23** — Set a 120-second timeout for communication with the quiet browser process. GPG unlocking before that call and tunnel activation afterward have separate behavior and limits.


#### 7.3.2 L25–L30 · Detect session replacement warnings


```python
CONFIRMATION_SCRIPT = """(() => {
  if (location.origin !== 'https://sslvpn.tifr.res.in') return false;
  return /There are already other user sessions in progress|Continue will result in termination of the other session/i.test(document.body?.innerText || '');
})()"""
```

**Line-by-line explanation**

- **L25** — Begin a Python multiline string containing JavaScript. (() => {...})() creates and immediately calls a JavaScript arrow function inside the web page.
- **L26** — Only inspect confirmation text on the exact HTTPS VPN origin. An origin combines scheme, host and effective port.
- **L27** — Test visible page text for either of two known concurrent-session warnings, ignoring letter case with /i. ?. safely handles a missing body; || '' uses empty text if needed. This detects known wording; it does not automatically click a confirmation button.
- **L28** — Close the JavaScript function, immediately invoke it, and close the Python string. Its result is a JavaScript boolean.


#### 7.3.3 L31–L62 · Build restricted form inspection and autofill JavaScript


```python
def signin_script(values=None):
    """Autofill only TIFR's Keycloak forms, returning status without field values."""
    return """((values) => {
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
    })(""" + json.dumps(values) + ")"
```

**Line-by-line explanation**

- **L31** — Define a function that builds JavaScript for inspecting or filling the known sign-in form. values=None means inspect without supplying credentials.
- **L32** — Docstring describes a boundary: return form state, not the fields' secret values, to Python.
- **L33** — Start a JavaScript function taking a values argument. Python will append a JSON-encoded argument at the end.
- **L34** — Require the exact TIFR SSO HTTPS origin. || means JavaScript logical OR, so either invalid origin or invalid path stops processing.
- **L35** — Also require the intended Keycloak realm path. Return JSON text with step:null if this is not an allowed page. This helps prevent filling credentials into an unexpected page.
- **L36** — Define a small JavaScript predicate: an input must exist, be enabled, and have layout rectangles to count as visible. This is a practical visibility check rather than a complete browser-perception model.
- **L37** — Select known validation/error elements. \[...nodeList\] turns results into an array; .some(visible) checks if any selected error is visible.
- **L38** — Return an error status when the page reports a known visible validation error, avoiding repeated blind submissions.
- **L39** — Locate one of the expected Keycloak login/OTP form IDs. CSS # selects an element ID; commas mean alternatives.
- **L40** — Require a form whose submission destination has the same origin as the current page. new URL resolves a relative form.action against the page address.
- **L41** — Return no actionable step if that destination check fails.
- **L42** — Locate the username input inside the chosen form using its name attribute.
- **L43** — Locate the password input similarly.
- **L44** — Locate either supported OTP input name: otp or totp.
- **L45** — Choose the current form step by visibility, preferring OTP, then password, then username. The ? : syntax is JavaScript's conditional expression.
- **L46** — Ignore unknown steps and a form already marked by this helper as submitted. dataset accesses HTML data-\* properties.
- **L47** — If no values were supplied, return only which form step is ready. This separates inspection from loading the password vault.
- **L48** — Define a helper that sets one input and dispatches browser events so the login page can notice the change.
- **L49** — Do nothing when the input is not visible or no value was provided for it.
- **L50** — Use the native HTMLInputElement value setter to update the field, including pages that wrap input handling. The secret is inserted into a DOM input, so it is present in the browser process during login.
- **L51** — Dispatch a bubbling input event. Bubbling lets handlers on parent elements see the event.
- **L52** — Dispatch a change event for login-page code listening for completed edits.
- **L53** — End the setter function.
- **L54** — Attempt to fill all three possible fields. Missing or hidden fields are skipped by the setter, so the same script supports multi-page and combined forms.
- **L55** — Do not submit an OTP form if a fresh OTP value was not supplied.
- **L56** — Mark this particular form as submitted to reduce duplicate submissions.
- **L57** — Find an explicit submit input or button when available.
- **L58** — Use requestSubmit with the submit button if found, otherwise requestSubmit without an argument. This respects normal browser form-submission behavior better than bypassing it with a raw submit call.
- **L59** — Return status naming the submitted step, without returning credentials.
- **L60** — Close/invoke the JavaScript function, inserting json.dumps(values). Python None becomes JavaScript null, and dictionaries become JSON objects. JSON encoding quotes values as data; it does not mean the credentials are encrypted inside the browser memory.


#### 7.3.4 L63–L87 · Read, store or clear desktop-keyring secrets


```python
def saved_login(kind, value=None, *, forget=False):
    """Keep only this helper's session state in the desktop Secret Service."""
    import gi
    gi.require_version("Secret", "1")
    from gi.repository import Secret

    schema = Secret.Schema.new("in.res.tifr.vpn", Secret.SchemaFlags.NONE, {
        "server": Secret.SchemaAttributeType.STRING,
        "kind": Secret.SchemaAttributeType.STRING,
    })
    attributes = {"server": URL, "kind": kind}
    try:
        if forget:
            return Secret.password_clear_sync(schema, attributes, None)
        if value is not None:
            return Secret.password_store_sync(
                schema, attributes, Secret.COLLECTION_DEFAULT,
                "TIFR VPN " + kind, value, None,
            )
        return Secret.password_lookup_sync(schema, attributes, None)
    except Exception:
        print("tifr VPN: desktop keyring unavailable; saved login could not be accessed.", file=sys.stderr)
        return None
```

**Line-by-line explanation**

- **L63** — Define desktop-keyring access. kind distinguishes cached VPN session versus browser cookies; value=None means read; forget=True means delete. \* makes forget keyword-only.
- **L64** — Docstring limits the intended namespace to this helper's state in the desktop Secret Service.
- **L65** — Import PyGObject's gi bridge only when keyring support is used.
- **L66** — Require the Secret API namespace version 1 before importing it.
- **L67** — Import libsecret's Python-accessible bindings for the desktop keyring service.
- **L69** — Create a keyring schema named in.res.tifr.vpn with no extra schema flags. A schema defines how stored secrets are identified, not an encryption algorithm.
- **L70** — Declare server as a string lookup attribute.
- **L71** — Declare kind as another string lookup attribute.
- **L72** — Close the schema definition and constructor call.
- **L73** — Use the fixed portal URL and requested kind as attributes, so browser/session entries are distinct and scoped to this portal.
- **L74** — Handle keyring operation errors without leaking raw secret values.
- **L75** — Give deletion priority when forget is requested.
- **L76** — Synchronously clear matching secrets. None means no cancellation object. A successful call may report that nothing needed deleting.
- **L77** — If value is supplied, choose storage rather than lookup. 'is not None' allows even an explicitly provided empty string to count as a value.
- **L78** — Begin storing a password-like secret through libsecret's synchronous API.
- **L79** — Supply the schema, lookup attributes and default desktop secret collection.
- **L80** — Supply a human-readable label, the secret value, and no cancellation object. Despite the API's password name, this project stores session state here, not the KeePass master password.
- **L81** — Finish storage and return its result.
- **L82** — Otherwise synchronously look up the matching secret; return its text, or None if absent.
- **L83** — Catch keyring operation exceptions. Imports/schema construction above this try have their own top-level handling instead.
- **L84** — Warn that cached state cannot be accessed, without printing the value. A keyring prompt may still be possible independently of the quiet browser.
- **L85** — Return None so callers can proceed without a cache where possible.


#### 7.3.5 L88–L107 · Validate portal access using a candidate session


```python
def valid_session(cookie):
    """Ask the gateway whether the saved session still grants portal access."""
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None

    request = Request("https://" + HOST + "/dana/home/index.cgi", headers={"Cookie": cookie})
    opener = build_opener(NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=15) as response:
            return response.status == 200
    except HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            location = urlsplit(error.headers.get("Location", ""))
            return location.hostname in (None, HOST) and location.path.startswith("/dana/home/")
        if error.code in (401, 403):
            return False
        raise
```

**Line-by-line explanation**

- **L88** — Define a function that asks whether a cookie still grants portal access. Having a DSID-shaped string alone does not prove login completed.
- **L89** — Explain the purpose of probing the portal.
- **L90** — Define a custom HTTP redirect handler inside this function.
- **L91** — Override redirect\_request. \*\_args and \*\*\_kwargs accept arbitrary positional and named parameters without needing to use them.
- **L92** — Return None instead of a redirected request, preventing automatic navigation from silently turning a login page's success response into apparent authenticated success.
- **L94** — Build an HTTPS request to the gateway's home page and include the candidate cookie in the Cookie header. Headers are protocol metadata sent to that server.
- **L95** — Build an opener with the no-redirect handler and a default TLS-verification context. Certificate verification is not disabled for the probe.
- **L96** — Begin handling expected server responses.
- **L97** — Open the request with a 15-second network timeout and ensure the response is closed using with.
- **L98** — An HTTP 200 response to that probe is accepted by this implementation as valid portal access. This is the program's heuristic, not a universal proof about every possible server behavior.
- **L99** — Catch HTTP status errors, including redirects intentionally not followed.
- **L100** — Handle common HTTP redirect status codes separately.
- **L101** — Parse the redirect Location header, defaulting to empty text if absent.
- **L102** — Accept a relative redirect or redirect to the same gateway host only when its path begins /dana/home/. The code inspects this location; it does not follow it.
- **L103** — HTTP 401 means unauthorized; 403 means forbidden. Treat either as an invalid cached session.
- **L104** — Return False so the caller can perform a fresh login.
- **L105** — Reraise other HTTP errors for top-level handling instead of treating every server outage as an expired session.


#### 7.3.6 L108–L131 · Build the GTK and WebKit sign-in window


```python
def login_cookie(*, quiet=False):
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("WebKit2", "4.1")
    gi.require_version("Soup", "3.0")
    from gi.repository import GLib, Gtk, Soup, WebKit2

    if not Gtk.init_check()[0]:
        raise RuntimeError("A graphical session is required for TIFR SSO login.")
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

- **L108** — Define graphical sign-in and return an authenticated DSID cookie. quiet changes behavior when input is needed; the window itself still exists on a display.
- **L109** — Load the GI bridge used by GTK/WebKit.
- **L110** — Select GTK version 3.0.
- **L111** — Select WebKit2 namespace 4.1. This is the GTK web engine API namespace, not a Python package version string.
- **L112** — Select libsoup namespace version 3.0 for cookie objects.
- **L113** — Import the event-loop utilities, window toolkit, HTTP-cookie library and embedded browser bindings.
- **L115** — Attempt GTK initialization and inspect its success flag. A usable display is required, either the real desktop or an Xvfb virtual display.
- **L116** — Fail clearly if graphical initialization is impossible.
- **L117** — Create an ephemeral WebKit context: it avoids an ordinary persistent browser profile on disk. This program still deliberately saves selected cookies separately in the keyring.
- **L118** — Get this context's cookie manager, which can read and restore HTTP cookies.
- **L119** — Create a WebView, an embeddable browser widget, using that context.
- **L120** — Create a GTK top-level window and title it for TIFR sign-in.
- **L121** — Set its initial window size to 900 by 720 pixels.
- **L122** — Create a vertical layout box with 8 pixels between children.
- **L123** — Create a label displaying the initial portal address.
- **L124** — Allow selecting/copying the address label's text.
- **L125** — Allow the label to wrap instead of forcing an excessively wide window.
- **L126** — Add the address label to the layout without giving it expandable vertical space, with padding 8.
- **L127** — Add the browser, letting it expand to fill the remaining space.
- **L128** — Put the layout inside the window.
- **L129** — Initialize shared sign-in state: no accepted cookie, no pending cookie lookup and no error. Nested callbacks mutate this dictionary.
- **L130** — Initialize autofill state: busy/stopped flags, a set of submitted step names, and no loaded credential provider. A set keeps unique values and supports quick membership checks.


#### 7.3.7 L132–L139 · Finish asynchronous form filling


```python
    def fill_ready(source, result):
        autofill["busy"] = False
        try:
            source.evaluate_javascript_finish(result)
        except Exception:
            # Navigation can destroy the previous page's JS context.
            pass
```

**Line-by-line explanation**

- **L132** — Define the callback invoked after the JavaScript filling operation finishes. 'source' is the WebView and result is its asynchronous result handle.
- **L133** — Allow later autofill work by clearing the busy marker.
- **L134** — Begin handling completion errors.
- **L135** — Finish the WebKit asynchronous JavaScript operation. The return value is not needed here.
- **L136** — Catch completion errors.
- **L137** — Comment explains a normal race: submitting a form can navigate away before its old JavaScript context returns.
- **L138** — Ignore that completion error; pass is a deliberate do-nothing statement.


#### 7.3.8 L140–L153 · Inspect the current form and avoid duplicate submissions


```python
    def form_ready(source, result):
        try:
            state = json.loads(source.evaluate_javascript_finish(result).to_string())
            if state.get("error"):
                autofill["stopped"] = True
                if quiet:
                    session["error"] = "SSO rejected the saved login. Retry tifrvpn -c to see the error."
                    Gtk.main_quit()
                    return
                print("tifr VPN: SSO reported an error; autofill stopped. Check the sign-in window and saved credentials.", file=sys.stderr)
                return
            step = state.get("step")
            if not step or step in autofill["submitted"]:
                return
```

**Line-by-line explanation**

- **L140** — Define the callback that receives inspected form status and decides whether to load credentials and fill it.
- **L141** — Begin guarded status processing.
- **L142** — Finish JavaScript evaluation, convert its result to a string, then parse that JSON string into a Python dictionary.
- **L143** — Check whether the page reported a visible validation error.
- **L144** — Stop further automatic filling to avoid repeated rejected submissions.
- **L145** — In quiet mode there is no visible window for the user to inspect, so stop with a readable diagnostic.
- **L146** — Save a message suggesting an ordinary visible connection attempt.
- **L147** — Ask GTK's event loop to stop.
- **L148** — Return from this callback immediately.
- **L149** — In visible mode explain that autofill stopped so the user can inspect/correct the page manually.
- **L150** — Return without further submission.
- **L151** — Get the current recognized form step, or None if absent.
- **L152** — If no actionable step exists or that named step was already submitted during this attempt, do nothing. This set-level guard spans navigations as well as the DOM marker.
- **L153** — Return from the callback in that case.


#### 7.3.9 L154–L170 · Load credentials and submit the appropriate step


```python
            if autofill["provider"] is None:
                helper = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tifr-otp.py"))
                database, password_file, entry = helper["configuration"]()
                master = helper["decrypt_password"](password_file, allow_prompt=not quiet)
                login = helper["read_login"](master, database, entry)
                autofill["provider"] = (helper, database, entry, master, login)
            helper, database, entry, master, login = autofill["provider"]
            values = dict(login)
            if step == "otp":
                # Leave enough time to unlock the vault and submit this code.
                if 30 - time.time() % 30 < 5:
                    return
                values["otp"] = helper["read_code"](master, database, entry)
            autofill["submitted"].add(step)
            label = "authenticator code" if step == "otp" else step
            print(f"tifr VPN: submitting saved {label}", file=sys.stderr, flush=True)
            view.evaluate_javascript(signin_script(values), -1, None, None, None, fill_ready)
```

**Line-by-line explanation**

- **L154** — Load vault support only once and only when a usable recognized form requires it.
- **L155** — Execute the adjacent tifr-otp.py definitions with runpy and keep its global names in a dictionary. \_\_file\_\_ is this source file's pathname; dirname finds its directory. This runpy call does not select that helper's CLI main block.
- **L156** — Call the loaded configuration function and unpack the selected vault, ciphertext path and entry name.
- **L157** — Decrypt the vault master password. Visible mode allows pinentry; quiet browser mode passes allow\_prompt=False so unlock cannot hide on Xvfb.
- **L158** — Read saved TIFR username/password from KeePassXC using that master password.
- **L159** — Cache the helper definitions, paths, entry, master password and login dictionary in this browser process for later form steps. The master password is therefore in process memory during the attempt.
- **L160** — Unpack the cached provider tuple for convenient use.
- **L161** — Make a new dictionary containing login values so an OTP can be added without altering the original login dictionary.
- **L162** — Only request a fresh authenticator code when the page is at the OTP step.
- **L163** — Comment describes avoiding a code that would expire during vault access and form submission.
- **L164** — time.time()%30 gives elapsed seconds within the current 30-second window; 30 minus that is remaining time. If fewer than 5 seconds remain, wait for a later timer tick. This hardcodes a 30-second period for automatic login.
- **L165** — Return without marking this step submitted, allowing the next timer tick to try in the next time window.
- **L166** — Read a fresh TOTP from KeePassXC and add it to the values sent to the allowed SSO page.
- **L167** — Record the step as submitted before asynchronously filling/submitting the form, preventing duplicate timer-triggered work.
- **L168** — Choose a readable progress label, using authenticator code rather than the internal otp name.
- **L169** — Print the step label to standard error immediately. The actual username/password/code is not included.
- **L170** — Evaluate generated fill JavaScript asynchronously, then call fill\_ready. -1 indicates a null-terminated script length; the None arguments use defaults/no cancellation for optional parameters.


#### 7.3.10 L171–L183 · Handle autofill errors


```python
        except RuntimeError as error:
            session["error"] = str(error)
            Gtk.main_quit()
        except Exception:
            autofill["stopped"] = True
            if quiet:
                session["error"] = "Automatic sign-in could not continue. Retry tifrvpn -c to see the sign-in window."
                Gtk.main_quit()
                return
            print("tifr VPN: automatic sign-in could not continue; check the sign-in window.", file=sys.stderr)
        finally:
            autofill["busy"] = False
```

**Line-by-line explanation**

- **L171** — Catch deliberate configuration/vault RuntimeErrors.
- **L172** — Store the readable error text in shared session state.
- **L173** — Stop the GUI loop so the outer function can raise that error.
- **L174** — Catch other autofill processing errors.
- **L175** — Disable further automatic attempts.
- **L176** — For quiet mode, stop because the user cannot inspect the hidden page.
- **L177** — Record a visible-mode retry instruction.
- **L178** — Stop the event loop.
- **L179** — Return from this error path.
- **L180** — For a visible browser, print a generic diagnostic and leave the window available for manual sign-in.
- **L181** — The finally block always runs, including after return or an exception.
- **L182** — Release the autofill busy flag, allowing later ticks where autofill has not been stopped.


#### 7.3.11 L184–L192 · Poll only the allowed SSO page


```python
    def autofill_tick():
        page = urlsplit(view.get_uri() or "")
        if (not autofill["busy"] and not autofill["stopped"] and not view.is_loading()
                and page.scheme == "https" and page.hostname == "sso.tifr.res.in"
                and page.port in (None, 443) and page.path.startswith("/realms/TIFRSSO2/")):
            autofill["busy"] = True
            view.evaluate_javascript(signin_script(), -1, None, None, None, form_ready)
        return True
```

**Line-by-line explanation**

- **L184** — Define the repeating timer callback that looks for a ready SSO form.
- **L185** — Parse the current page address, using empty text if WebKit has no URI yet.
- **L186** — Only inspect when no fill is pending, autofill has not been stopped and the page has finished loading.
- **L187** — Require HTTPS and the exact sso.tifr.res.in hostname.
- **L188** — Require default HTTPS port or explicit 443 and the expected realm path. Python indentation groups this multiline if condition and its body.
- **L189** — Mark an inspection as pending before starting the asynchronous operation.
- **L190** — Run the inspection version of signin\_script, with no supplied credentials, and use form\_ready to process its response.
- **L191** — Return True so GLib keeps the timer active. Returning False would remove that repeating timer.


#### 7.3.12 L193–L211 · Remember allowed browser cookies


```python
    def remember_browser(source, result):
        try:
            records = []
            for cookie in source.get_all_cookies_finish(result):
                domain = cookie.get_domain()
                if domain.lstrip(".") != "tifr.res.in" and not domain.endswith(".tifr.res.in"):
                    continue
                expires = cookie.get_expires()
                records.append({
                    "name": cookie.get_name(), "value": cookie.get_value(),
                    "domain": domain, "path": cookie.get_path(),
                    "secure": cookie.get_secure(), "http_only": cookie.get_http_only(),
                    "expires": expires.to_unix() if expires else None,
                })
            saved_login("browser", json.dumps(records))
        except Exception:
            print("tifr VPN: browser session could not be remembered.", file=sys.stderr)
        Gtk.main_quit()
```

**Line-by-line explanation**

- **L193** — Define the callback that stores allowed browser cookies after a valid VPN session has been identified.
- **L194** — Guard cookie export and keyring storage.
- **L195** — Create a list of cookie records to save.
- **L196** — Complete asynchronous retrieval of all cookies and iterate through them.
- **L197** — Read each cookie's domain.
- **L198** — Allow only tifr.res.in itself or subdomains ending .tifr.res.in. lstrip('.') handles cookie-domain notation with a leading dot; suffix matching includes a dot boundary to avoid unrelated names such as faketifr.res.in.
- **L199** — Skip cookies outside that domain scope.
- **L200** — Read a possible expiry timestamp; session-only cookies may have no explicit expiry.
- **L201** — Append a plain Python dictionary representing this cookie.
- **L202** — Store its name and value. Values can be authentication secrets; this list is not printed.
- **L203** — Store domain and path, which constrain where a browser sends the cookie.
- **L204** — Store secure and HttpOnly attributes. Secure restricts normal browser transport to HTTPS; HttpOnly prevents ordinary page JavaScript from reading that cookie through document.cookie.
- **L205** — Serialize an expiry as Unix seconds when present, otherwise None. Unix time counts seconds from the conventional 1970 epoch.
- **L206** — Close the cookie dictionary/append call.
- **L207** — JSON-encode the records and store them as the browser-kind secret in the desktop keyring. This is intentional persistence despite the ephemeral WebKit profile.
- **L208** — Catch unexpected cookie conversion/storage errors.
- **L209** — Explain that browser state could not be remembered; failure to cache is separate from whether this login succeeded.
- **L210** — Stop the GTK loop now that the current successful session has been collected.


#### 7.3.13 L212–L238 · Identify and validate the DSID cookie


```python
    def cookies_ready(source, result):
        session["busy"] = False
        try:
            cookies = source.get_cookies_finish(result)
        except Exception:
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

- **L212** — Define the callback for a cookie lookup associated with the gateway portal.
- **L213** — Release the pending-cookie-lookup flag.
- **L214** — Handle asynchronous cookie lookup completion.
- **L215** — Get the cookies returned for the portal URL.
- **L216** — If retrieval fails, handle it without aborting visible login immediately.
- **L217** — Return, leaving later browser/timer events able to retry.
- **L218** — Inspect each returned cookie.
- **L219** — Look specifically for a nonempty DSID cookie, the session token expected by this VPN portal.
- **L220** — Get its raw value.
- **L221** — Reject carriage returns, newlines or NUL, which could corrupt headers or the line-based nmcli secret format later.
- **L222** — Store an invalid-cookie error for the outer sign-in function.
- **L223** — Otherwise construct and validate a candidate session.
- **L224** — Prefix the value with DSID= to form the Cookie-header text expected by the gateway.
- **L225–L226** — Comments explain why a portal-access probe is more reliable here than assuming that a particular final page URL always means login completion.
- **L227** — Guard the network validation attempt.
- **L228** — Probe whether the candidate actually grants portal access. A DSID can exist before concurrent-session confirmation is complete.
- **L229** — If not valid yet, leave the browser open and return; later events may retry after the user completes sign-in.
- **L230** — Handle network/system errors while probing.
- **L231** — Leave the browser running for later checks rather than accepting an unverified cookie.
- **L232** — Save a validated session string in shared state. Its presence is how login\_cookie ultimately knows it succeeded.
- **L233** — If earlier validation recorded an invalid-cookie error, stop rather than export state.
- **L234** — Stop the event loop on that error.
- **L235** — Otherwise remember selected browser cookies before exiting.
- **L236** — Asynchronously retrieve all browser cookies, with remember\_browser as the completion callback.
- **L237** — Finish after handling the first relevant DSID cookie.


#### 7.3.14 L239–L247 · Stop quiet sign-in when confirmation is required


```python
    def confirmation_ready(source, result):
        try:
            required = source.evaluate_javascript_finish(result).to_boolean()
        except Exception:
            return
        if required:
            session["error"] = "TIFR requires confirmation to replace another session. Retry tifrvpn -c and review the warning."
            Gtk.main_quit()
```

**Line-by-line explanation**

- **L239** — Define the completion callback for quiet-mode concurrent-session warning detection.
- **L240** — Handle potential JavaScript completion failures.
- **L241** — Convert the warning-inspection JavaScript result to a boolean.
- **L242** — If evaluation fails, ignore this particular check; other checks and the quiet timeout remain active.
- **L243** — Return from that failed inspection.
- **L244** — If a known replacement-session warning is present, require an ordinary visible attempt.
- **L245** — Record an error explaining that the user must review the warning. This code does not automatically confirm replacing another session.
- **L246** — Stop the GTK loop.


#### 7.3.15 L248–L258 · Schedule cookie and confirmation checks


```python
    def check_cookies(*_args):
        page = urlsplit(view.get_uri() or "")
        # A DSID may exist before the concurrent-session confirmation finishes;
        # cookies_ready checks portal access before accepting it.
        if (not view.is_loading() and page.hostname == HOST
                and not session["busy"] and not session["cookie"]):
            session["busy"] = True
            if quiet:
                view.evaluate_javascript(CONFIRMATION_SCRIPT, -1, None, None, None, confirmation_ready)
            manager.get_cookies("https://" + HOST + "/dana/home/index.cgi", None, cookies_ready)
```

**Line-by-line explanation**

- **L248** — Define an event callback accepting any extra signal arguments, which it does not need. Different GTK signals supply different argument lists.
- **L249** — Read and parse the current browser location.
- **L250–L251** — Comments explain that a DSID alone is insufficient; cookies\_ready probes portal access before accepting it.
- **L252** — Only inspect the gateway after loading finishes.
- **L253** — Avoid overlapping cookie operations or continuing after an accepted cookie already exists.
- **L254** — Mark a cookie check as pending.
- **L255** — If quiet, also inspect the page for a known session-replacement warning.
- **L256** — Evaluate the confirmation-detection script asynchronously and route its result to confirmation\_ready.
- **L257** — Asynchronously retrieve cookies applicable to the gateway portal path and send them to cookies\_ready. Browser cookie scope includes URL paths.


#### 7.3.16 L259–L267 · Handle certificate errors and closing the window


```python
    def tls_error(_view, _uri, _certificate, _errors):
        session["error"] = "SSO certificate verification failed. Contact TIFR IT."
        Gtk.main_quit()
        return False

    def close(*_args):
        Gtk.main_quit()
        return False
```

**Line-by-line explanation**

- **L259** — Define handling for TLS certificate errors from the embedded browser. Leading underscores indicate arguments intentionally unused.
- **L260** — Record a certificate failure and tell the user to contact TIFR IT; this does not offer an insecure certificate bypass.
- **L261** — Stop the event loop.
- **L262** — Return False to indicate that the certificate-load error has not been overridden/handled by accepting it.
- **L264** — Define the callback for closing the sign-in window.
- **L265** — Stop GTK's event loop when the user closes the window.
- **L266** — Return False to permit the default close-event handling.


#### 7.3.17 L268–L286 · Register browser events and restoration callbacks


```python
    manager.connect("changed", check_cookies)
    view.connect("load-changed", check_cookies)
    view.connect("notify::uri", lambda *_: address.set_text(view.get_uri() or URL))
    view.connect("load-failed-with-tls-errors", tls_error)
    window.connect("delete-event", close)
    def load_page():
        view.load_uri(URL)

    pending = {"count": 0}

    def restored(source, result):
        try:
            source.add_cookie_finish(result)
        except Exception:
            pass
        pending["count"] -= 1
        if not pending["count"]:
            load_page()
```

**Line-by-line explanation**

- **L268** — Register check\_cookies to run when the cookie manager reports a change. Here connect means attach an event handler, not open a VPN.
- **L269** — Also check cookies when the browser's load state changes.
- **L270** — When the URI changes, update the address label. lambda \*\_: ... is an anonymous function ignoring all supplied signal arguments.
- **L271** — Connect certificate-failure events to the strict TLS error handler.
- **L272** — Connect a user window-close request to the close callback.
- **L273** — Define a small function that begins portal navigation after any cookie restoration finishes.
- **L274** — Tell the WebView to load the fixed portal URL.
- **L276** — Initialize a mutable counter for outstanding asynchronous cookie-restoration operations.
- **L278** — Define the callback called after each restored cookie has been added to WebKit.
- **L279** — Guard completion of one cookie-add operation.
- **L280** — Finish that asynchronous add operation; any error is handled below.
- **L281** — Catch a failed restoration for this cookie.
- **L282** — Ignore the single-cookie failure so a fresh sign-in is still possible.
- **L283** — Decrease the number of outstanding restores whether this one succeeded or failed.
- **L284** — When all restore operations have completed, it is safe to start loading the portal.
- **L285** — Begin navigation using whatever cookies were successfully restored.


#### 7.3.18 L287–L307 · Validate and reconstruct saved browser cookies


```python
    try:
        records = json.loads(saved_login("browser") or "[]")
    except (ValueError, TypeError):
        records = []
    cookies = []
    for record in records:
        try:
            domain = record["domain"]
            if domain.lstrip(".") != "tifr.res.in" and not domain.endswith(".tifr.res.in"):
                continue
            expires = record.get("expires")
            if expires is not None and expires <= time.time():
                continue
            cookie = Soup.Cookie.new(record["name"], record["value"], domain, record["path"], -1)
            cookie.set_secure(record["secure"])
            cookie.set_http_only(record["http_only"])
            if expires is not None:
                cookie.set_expires(GLib.DateTime.new_from_unix_utc(expires))
            cookies.append(cookie)
        except (KeyError, TypeError, ValueError):
            continue
```

**Line-by-line explanation**

- **L287** — Attempt to retrieve and decode previously remembered browser cookies.
- **L288** — Read the keyring's browser secret; if absent/falsy use the JSON text \[\] for an empty list, then parse it.
- **L289** — Catch malformed JSON or an invalid input type.
- **L290** — Discard malformed cached records and continue with an empty list.
- **L291** — Build a fresh list of actual libsoup cookie objects to restore.
- **L292** — Loop through saved records. Cached data is still checked rather than blindly used.
- **L293** — Handle missing or malformed fields on each individual record.
- **L294** — Read the saved domain field.
- **L295** — Apply the same allowed-domain check used when saving browser cookies.
- **L296** — Skip out-of-scope cookies.
- **L297** — Read an optional expiry timestamp.
- **L298** — Reject cookies whose explicit expiry is already in the past. time.time() gives current Unix seconds.
- **L299** — Skip the expired cookie without attempting to restore it.
- **L300** — Construct a Soup.Cookie using name, value, domain and path. The -1 max-age argument leaves initial lifetime unspecified for this reconstruction, then explicit saved expiry is set when available.
- **L301** — Restore the Secure flag.
- **L302** — Restore the HttpOnly flag.
- **L303** — If the saved cookie had a persistent expiry, restore it.
- **L304** — Convert saved Unix seconds to a GLib UTC date/time and attach it to the cookie.
- **L305** — Append the constructed cookie to the restoration list.
- **L306** — Catch common malformed-record errors.
- **L307** — Skip that record and continue with others.


#### 7.3.19 L308–L334 · Restore cookies, run timers and clean up GTK


```python
    pending["count"] = len(cookies)
    for cookie in cookies:
        manager.add_cookie(cookie, None, restored)
    if not cookies:
        load_page()
    window.show_all()
    autofill_timer = GLib.timeout_add(500, autofill_tick)
    # WebKit's load-changed signal can arrive before is_loading becomes false.
    # Check again after navigation has settled, including delayed portal redirects.
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
        raise RuntimeError(session["error"])
    if not session["cookie"]:
        raise RuntimeError("Sign-in cancelled; no VPN tunnel was started.")
    return session["cookie"]
```

**Line-by-line explanation**

- **L308** — Set the pending counter before starting callbacks; this avoids incorrectly navigating after only the first addition finishes.
- **L309** — Loop over all validated reconstructed cookies.
- **L310** — Begin each asynchronous addition with restored as its completion callback.
- **L311** — If there are no cookies, no callbacks will arrive to start navigation.
- **L312** — Load the portal immediately in that empty-cache case.
- **L313** — Show the GTK widgets. In quiet mode the same graphical window appears on the private Xvfb display rather than the real desktop.
- **L314** — Schedule autofill\_tick every 500 milliseconds, twice per second; store the timer ID for later removal.
- **L315–L316** — Comments explain the second timer: load-change events may fire before the page truly settles, especially with delayed redirects.
- **L317** — Define a periodic portal-cookie check callback.
- **L318** — Run the same guarded cookie-check logic used by browser events.
- **L319** — Return True to keep the timer repeating.
- **L321** — Schedule portal\_tick roughly every 2 seconds and remember its ID.
- **L322** — Begin event-loop execution with guaranteed cleanup.
- **L323** — Enter GTK's event loop. It waits for browser/network/user/timer events and invokes callbacks until Gtk.main\_quit is called. Code after this line waits for the loop to finish.
- **L324** — Always perform GUI/timer cleanup when the event loop exits or an exception escapes.
- **L325** — Remove the autofill timer by its ID.
- **L326** — Remove the portal-cookie timer.
- **L327** — Destroy the sign-in window and its widgets.
- **L328** — After the loop, check whether a callback recorded an error.
- **L329** — Raise that readable error so the browser-process wrapper can report it.
- **L330** — If no accepted cookie exists, the loop ended without successful authentication.
- **L331** — Report cancellation/incomplete sign-in rather than starting a tunnel without a valid session.
- **L332** — Return the validated DSID string to this process's caller.


#### 7.3.20 L335–L346 · Verify the gateway and derive its public-key pin


```python
def activate(uuid, cookie):
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    # Verify the gateway with the system trust store before pinning this session.
    context = ssl.create_default_context()
    with socket.create_connection((HOST, 443), timeout=15) as connection:
        with context.wrap_socket(connection, server_hostname=HOST) as tls:
            public_key = x509.load_der_x509_certificate(tls.getpeercert(binary_form=True)).public_key()
            spki = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
            fingerprint = "pin-sha256:" + base64.b64encode(hashlib.sha256(spki).digest()).decode()
            gateway_ip = tls.getpeername()[0]
```

**Line-by-line explanation**

- **L335** — Define tunnel activation using an already obtained session. uuid is the exact NetworkManager profile; cookie is the authentication token.
- **L336** — Import X.509 certificate parsing only when activation is needed.
- **L337** — Import constants defining DER binary encoding and SubjectPublicKeyInfo public-key format.
- **L339** — Comment explains the order: validate the server through normal certificate trust first, then derive a pin for this activation.
- **L340** — Create a default TLS context that verifies certificate trust and hostname through Python's standard facilities.
- **L341** — Open a TCP connection to gateway port 443 with a 15-second socket timeout; with ensures closure afterward.
- **L342** — Wrap the socket in TLS and provide server\_hostname for hostname verification and Server Name Indication. An untrusted/incorrect certificate fails here.
- **L343** — Get the peer's binary DER certificate, parse it as X.509 and extract its public key.
- **L344** — Serialize that key in DER SubjectPublicKeyInfo format. This pins the public key representation rather than hashing the entire certificate file.
- **L345** — Compute a SHA-256 digest, Base64-encode it and prefix pin-sha256:. This fingerprint is passed to OpenConnect for this session; it is derived from a normally verified connection, not accepted blindly from an untrusted server.
- **L346** — Record the actual gateway IP used by this verified TLS connection so tunnel setup can use that address.


#### 7.3.21 L347–L365 · Hand transient secrets to nmcli using an anonymous descriptor


```python
    secrets = {
        "cookie": cookie, "gateway": "https://" + HOST, "gwcert": fingerprint,
        "resolve": f"{HOST}:{gateway_ip}",
    }
    fd = os.memfd_create("tifr-vpn-session", os.MFD_CLOEXEC)
    try:
        with os.fdopen(os.dup(fd), "w") as stream:
            stream.write("".join(f"vpn.secrets.{key}:{value}\n" for key, value in secrets.items()))
        os.lseek(fd, 0, os.SEEK_SET)
        print("tifr VPN: starting NetworkManager tunnel", flush=True)
        return subprocess.run(
            ["nmcli", "--wait", "90", "connection", "up", "uuid", uuid,
             "passwd-file", f"/proc/self/fd/{fd}"],
            pass_fds=(fd,),
        ).returncode
    finally:
        os.close(fd)
```

**Line-by-line explanation**

- **L347** — Prepare a dictionary of transient VPN activation secrets.
- **L348** — Include the authenticated session cookie, gateway HTTPS URL and public-key pin.
- **L349** — Include a resolve override pairing the intended hostname with the verified connection's IP. An f-string inserts both values.
- **L350** — Close the secrets dictionary.
- **L351** — Create a Linux anonymous memory-backed file and receive its integer file descriptor fd. MFD\_CLOEXEC normally closes it across executable replacement; pass\_fds below deliberately passes this one to nmcli. This avoids a named plaintext password file, but is not a guarantee that secrets can never enter swap, dumps or privileged inspection.
- **L352** — Ensure the descriptor is closed even if activation fails.
- **L353** — Duplicate fd, wrap the duplicate as a text stream and close that duplicate at the end of with. Duplication lets the original descriptor remain available for nmcli.
- **L354** — Write one line per secret in nmcli's vpn.secrets.key:value format. A generator builds each line and ''.join concatenates them. These values are not printed to the terminal.
- **L355** — Rewind the shared file position to byte 0 so nmcli reads from the beginning after Python wrote the contents.
- **L356** — Print progress immediately without including the secrets.
- **L357** — Start a synchronous nmcli activation and return its status.
- **L358** — Ask nmcli to bring up this UUID and wait up to 90 seconds for its operation.
- **L359** — Supply passwd-file as /proc/self/fd/N. In the child, self refers to nmcli's own process and N is the inherited descriptor, letting a file-reading interface consume the anonymous secret data.
- **L360** — Explicitly inherit this fd in the child despite the normal close-on-exec/default descriptor-closing behavior. (fd,) is a one-element Python tuple; the comma matters.
- **L361** — Read the child result's returncode and return it to the caller.
- **L362** — Always perform cleanup after subprocess execution or error.
- **L363** — Close the original descriptor owned by Python. The child and stream duplicates are handled by their respective lifetimes.


#### 7.3.22 L366–L373 · Start the isolated quiet browser environment


```python
def background_browser(command):
    """Run a disposable virtual display and clean up its entire process group."""
    environment = dict(os.environ, GDK_BACKEND="x11")
    environment.pop("WAYLAND_DISPLAY", None)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, text=True, env=environment,
        start_new_session=True,
    )
```

**Line-by-line explanation**

- **L366** — Define the process supervisor for an Xvfb-backed sign-in attempt.
- **L367** — Docstring describes the temporary display and intended cleanup of its process group.
- **L368** — Copy the parent environment and force GDK\_BACKEND=x11, selecting the X11 GTK backend used with Xvfb. Do not globally alter the parent's environment.
- **L369** — Remove WAYLAND\_DISPLAY from the child's environment to avoid choosing the real Wayland display. pop(..., None) does not fail if the variable is absent.
- **L370** — Start a subprocess without immediately waiting; Popen gives more lifecycle control than a basic run call.
- **L371** — Pass the command list, capture stdout as text, and supply the prepared child-only environment. stderr is inherited, so progress/errors remain visible in the terminal.
- **L372** — Start a new Unix session/process group, enabling group-directed cleanup of the virtual display wrapper and its same-group descendants.
- **L373** — Finish process creation.


#### 7.3.23 L374–L394 · Wait, handle timeout or cancellation and terminate the group


```python
    try:
        output, _ = process.communicate(timeout=BACKGROUND_TIMEOUT)
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
        raise RuntimeError("Background sign-in timed out. Retry tifrvpn -c to see whether TIFR needs input.") from None
    return subprocess.CompletedProcess(command, process.returncode, output)
```

**Line-by-line explanation**

- **L374** — Wait for success or handle timeout/cancellation.
- **L375** — communicate drains captured stdout and waits for termination, with a 120-second limit. '\_' receives the unused stderr result because stderr was not captured. Unlike run(timeout=...), Popen.communicate(timeout=...) needs explicit cleanup when it times out.
- **L376** — Handle either timeout or Ctrl+C using a common cleanup path while keeping the actual exception in error.
- **L377** — Attempt cooperative group termination first.
- **L378** — Send SIGTERM to the process group whose ID is the new-session child's PID. Same-group descendants receive it too; arbitrary detached descendants are not universally guaranteed to remain in that group.
- **L379** — The group may have exited just before the signal, causing ProcessLookupError.
- **L380** — Ignore that harmless already-gone case.
- **L381** — Allow time for graceful shutdown and drain remaining output.
- **L382** — Wait up to 5 additional seconds for cleanup. Therefore observed cancellation/timeout handling can take longer than the nominal 120-second browser limit.
- **L383** — If shutdown still has not completed, escalate.
- **L384** — Guard the stronger termination signal against a concurrent exit.
- **L385** — Send SIGKILL to the same process group. Unlike SIGTERM, this cannot be handled or ignored by a process that receives it.
- **L386** — Handle a group that has already disappeared.
- **L387** — Ignore that case.
- **L388** — Reap the process and drain the pipe after escalation, avoiding an unreaped child. This final communicate has no further explicit timeout in the code.
- **L389** — Distinguish a user cancellation from a deadline expiry.
- **L390** — Reraise KeyboardInterrupt so outer handling uses the cancellation exit/message path.
- **L391** — For a deadline expiry, raise a concise error suggesting visible retry. 'from None' suppresses noisy timeout exception chaining.
- **L392** — For normal completion, wrap command/status/output in a CompletedProcess object, making the result resemble subprocess.run's return value.


#### 7.3.24 L395–L410 · Choose background or visible authentication


```python
def authenticate(*, quiet=False):
    # Isolate WebKit from the tunnel controller, including its native shutdown.
    command = [sys.executable, os.path.abspath(__file__), "--sso-window"]
    if quiet:
        missing = [name for name in ("xvfb-run", "Xvfb", "xauth") if not shutil.which(name)]
        if missing:
            raise RuntimeError("Background sign-in requires: " + ", ".join(missing) + ". Install Xvfb and xauth, or retry without --quiet.")
        # Unlock on the real desktop before changing DISPLAY. The child only
        # uses cached GPG access, so it can never hide a pinentry prompt.
        helper = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tifr-otp.py"))
        _, password_file, _ = helper["configuration"]()
        helper["decrypt_password"](password_file)
        print("tifr VPN: signing in in the background (120-second limit)", file=sys.stderr, flush=True)
        result = background_browser(["xvfb-run", "-a"] + command + ["--quiet"])
    else:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
```

**Line-by-line explanation**

- **L395** — Define authentication orchestration, with quiet keyword-only and False by default.
- **L396** — Comment explains process isolation: browser/GUI native cleanup should not disrupt the process responsible for tunnel activation.
- **L397** — Build a command invoking this same file using the exact currently running Python interpreter and internal --sso-window mode. sys.executable preserves the interpreter/environment choice.
- **L398** — Use Xvfb supervision only when quiet was requested and a fresh sign-in is actually needed.
- **L399** — Build a list of missing executables: wrapper xvfb-run, virtual X server Xvfb and X authorization utility xauth. A list comprehension filters names whose executable lookup fails.
- **L400** — If any dependency is missing, stop before trying vault access or starting a display.
- **L401** — List missing programs and offer an ordinary visible connection attempt.
- **L402–L403** — Comments explain prompting order: attempt GPG unlock on the real desktop, then let the hidden child use cached access without opening pinentry.
- **L404** — Load adjacent OTP helper definitions in the parent process.
- **L405** — Get configuration and keep only password\_file. '\_' is a conventional unused-variable name, not special Python syntax; repeated assignment simply overwrites it.
- **L406** — Decrypt once while the real desktop environment is still active, allowing a GPG unlock prompt. The returned string is not saved in a named variable here, but decryption still creates it in parent memory temporarily. This relies on GPG-agent caching; if cached access is unavailable in the child, the child's no-prompt decryption fails clearly.
- **L407** — Explain background progress and the browser's nominal timeout on stderr, flushing immediately. GPG prompting happened before this timer starts.
- **L408** — Run xvfb-run -a followed by the Python browser command and --quiet. -a asks the wrapper to choose an available display number; the supervisor handles waiting/cancellation.
- **L409** — Without quiet, use the ordinary desktop browser subprocess.
- **L410** — Run it synchronously with stdout captured as text; terminal stderr is inherited. There is no explicit browser timeout for this visible path.


#### 7.3.25 L411–L420 · Validate the browser subprocess result


```python
    if result.returncode:
        if quiet:
            raise RuntimeError("Background sign-in did not complete. Retry tifrvpn -c to see the sign-in window.")
        raise RuntimeError("SSO sign-in did not complete; no tunnel was started.")
    cookie = result.stdout.strip()
    if not cookie.startswith("DSID=") or any(char in cookie for char in "\r\n\0"):
        raise RuntimeError("Invalid SSO session; no tunnel was started.")
    return cookie
```

**Line-by-line explanation**

- **L411** — Check whether the browser process reported failure.
- **L412** — Choose a quiet-specific diagnostic if appropriate.
- **L413** — Recommend a visible attempt when hidden sign-in failed. More specific child diagnostics may already have appeared on inherited stderr.
- **L414** — Otherwise report ordinary incomplete SSO sign-in.
- **L415** — Get the child process's stdout and trim surrounding whitespace. This channel is reserved for the session-cookie result.
- **L416** — Require a DSID= prefix and reject embedded carriage return/newline/NUL. This checks output shape; login\_cookie performed portal validation earlier.
- **L417** — Reject malformed child output before tunnel activation.
- **L418** — Return the accepted session string to main.


#### 7.3.26 L421–L443 · Internal browser-process entry point and immediate shutdown


```python
def sso_window_process(*, quiet=False):
    code = 1
    try:
        cookie = login_cookie(quiet=quiet)
        sys.stdout.write(cookie)
        sys.stdout.flush()
        code = 0
    except KeyboardInterrupt:
        print("tifr VPN: sign-in cancelled", file=sys.stderr)
        code = 130
    except RuntimeError as error:
        print(f"tifr VPN: {error}", file=sys.stderr)
    except ImportError:
        print("tifr VPN: install SSO support: sudo dnf install python3-gobject webkit2gtk4.1", file=sys.stderr)
    except Exception:
        print("tifr VPN: the SSO window could not complete sign-in.", file=sys.stderr)
    finally:
        # WebKit uses native worker processes. Avoid interpreter finalization
        # of its GI wrappers after the window closes.
        sys.stderr.flush()
        os._exit(code)
```

**Line-by-line explanation**

- **L421** — Define the internal browser-process entry point.
- **L422** — Assume failure unless sign-in finishes successfully.
- **L423** — Begin guarded browser operation.
- **L424** — Run graphical login, using quiet-specific failure handling when requested.
- **L425** — Write the cookie to stdout, which the parent captures through its pipe. The user normally sees progress on stderr, not this token.
- **L426** — Flush stdout explicitly because the process will use immediate os.\_exit instead of normal interpreter shutdown.
- **L427** — Set successful exit status only after writing the result.
- **L428** — Handle user interruption.
- **L429** — Print cancellation to stderr, keeping stdout free of human messages.
- **L430** — Use conventional cancellation status 130.
- **L431** — Handle deliberate readable login errors.
- **L432** — Print their intended diagnostic text to stderr; default code remains failure.
- **L433** — Handle missing imported support libraries.
- **L434** — Give a Fedora/dnf-specific installation hint. These package names are not a universal command for every Linux distribution.
- **L435** — Handle other unexpected browser errors without printing raw traceback data.
- **L436** — Print a generic incomplete-sign-in diagnostic.
- **L437** — Always end this dedicated child process after its result/error is handled.
- **L438–L439** — Comments explain avoiding ordinary Python finalization of WebKit's native GI wrappers, which have caused shutdown issues in this design.
- **L440** — Flush diagnostic output before immediate termination.
- **L441** — os.\_exit terminates immediately with code, bypassing ordinary Python cleanup/atexit handlers. It is appropriate to this deliberately isolated child path and would be hazardous as a general replacement for sys.exit.


#### 7.3.27 L444–L456 · Clear cached state or parse controller arguments


```python
def main():
    if sys.argv[1:] == ["--forget-login"]:
        cleared = [saved_login("session", forget=True), saved_login("browser", forget=True)]
        if any(result is None for result in cleared):
            print("tifr VPN: could not clear all saved sign-in state.", file=sys.stderr)
            return 1
        print("tifr VPN: saved sign-in state cleared; an active tunnel is unaffected.")
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("uuid", metavar="NETWORKMANAGER_PROFILE_UUID")
    parser.add_argument("--quiet", action="store_true", help="hide the SSO browser using Xvfb")
    args = parser.parse_args()
    uuid = args.uuid
```

**Line-by-line explanation**

- **L444** — Define the controller process's top-level workflow.
- **L445** — Recognize the exact special command --forget-login before parsing a required profile UUID.
- **L446** — Attempt to clear both cached VPN session and browser-cookie records. These calls execute sequentially and return a two-element list.
- **L447** — Treat None results as a keyring-access failure. False can mean no matching entry, which is different from the helper's None-on-error result.
- **L448** — Report incomplete cache clearing.
- **L449** — Return failure if either operation could not be completed.
- **L450** — Report success and explain that a currently active tunnel is not disconnected by clearing cache.
- **L451** — Return successful completion of the special mode.
- **L452** — Create an argument parser using the module description.
- **L453** — Require a positional NetworkManager profile UUID. metavar changes the word shown in help, not the attribute name args.uuid.
- **L454** — Register the --quiet boolean flag.
- **L455** — Parse arguments; argparse also supports generated --help handling.
- **L456** — Read the profile identifier from parsed arguments.


#### 7.3.28 L457–L466 · Validate the selected NetworkManager profile


```python
    service = subprocess.check_output(
        ["nmcli", "-g", "vpn.service-type", "connection", "show", "uuid", uuid], text=True,
    ).strip()
    data = subprocess.check_output(
        ["nmcli", "--escape", "no", "-g", "vpn.data", "connection", "show", "uuid", uuid], text=True,
    )
    settings = dict(item.strip().split(" = ", 1) for item in data.strip().split(",") if " = " in item)
    if (service != "org.freedesktop.NetworkManager.openconnect"
            or settings.get("gateway") != URL or settings.get("protocol") != "nc"):
        raise RuntimeError("Profile settings differ; run tifrvpn --setup.")
```

**Line-by-line explanation**

- **L457** — Ask NetworkManager which plugin the given profile uses, raising if the command fails.
- **L458** — Select only vpn.service-type and decode output as text.
- **L459** — Strip the final newline from the plugin name.
- **L460** — Retrieve profile plugin data for validation as well.
- **L461** — Disable nmcli output escaping so the following parser can read its comma-separated 'key = value' representation.
- **L462** — Finish the subprocess call.
- **L463** — Split nonempty key/value items into a dictionary: first comma-separated items, then strip outer whitespace, then split once on ' = '. This parser assumes this nmcli representation for the expected values.
- **L464** — Check that the service is OpenConnect.
- **L465** — Also require the exact configured portal URL and nc protocol. The controller refuses to feed login state into an unexpected profile configuration.
- **L466** — Suggest rerunning setup if these required settings differ.


#### 7.3.29 L467–L478 · Reuse a valid session or obtain a fresh one


```python
    cookie = saved_login("session")
    if cookie and valid_session(cookie):
        print("tifr VPN: reusing saved session", flush=True)
        return activate(uuid, cookie)
    if cookie:
        saved_login("session", forget=True)
        print("tifr VPN: saved session expired; TIFR requires sign-in again.", flush=True)
    cookie = authenticate(quiet=args.quiet)
    saved_login("session", cookie)
    return activate(uuid, cookie)
```

**Line-by-line explanation**

- **L467** — Try reading the reusable VPN session string from the desktop keyring.
- **L468** — If a cookie exists and the gateway accepts it, no new browser login is needed—even when --quiet was requested.
- **L469** — Print that a cached session is being reused, without printing its value.
- **L470** — Activate the tunnel using that session and return nmcli's status.
- **L471** — If a cached cookie existed but failed the validity test, discard it.
- **L472** — Clear the obsolete cached session record.
- **L473** — Explain that fresh server authentication is required.
- **L474** — Run fresh sign-in, using the requested quiet/visible behavior.
- **L475** — Attempt to store the returned session in the desktop keyring for a future connection. Cache storage failure warns but does not itself prevent trying the current tunnel.
- **L476** — Activate the tunnel with the current session and return its status.


#### 7.3.30 L479–L496 · Main guard and controller error handling


```python
if __name__ == "__main__":
    if sys.argv[1:] in (["--sso-window"], ["--sso-window", "--quiet"]):
        sso_window_process(quiet="--quiet" in sys.argv[1:])
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\ntifr VPN: cancelled", file=sys.stderr)
        sys.exit(130)
    except RuntimeError as error:
        print(f"tifr VPN: {error}", file=sys.stderr)
        sys.exit(1)
    except ImportError:
        print("tifr VPN: install dependencies: sudo dnf install python3-gobject webkit2gtk4.1 python3-cryptography", file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError, subprocess.CalledProcessError):
        # Never dump authentication data or session cookies on failure.
        print("tifr VPN: could not prepare the VPN session; check the preceding errors.", file=sys.stderr)
        sys.exit(1)
```

**Line-by-line explanation**

- **L479** — Run this block only when this file is executed as the main program, not when test code loads its definitions.
- **L480** — Recognize only the exact supported internal browser-mode argument combinations before normal profile parsing.
- **L481** — Run the dedicated browser entry point; 'in' checks whether --quiet is present. Its finally calls os.\_exit, so a normal controller invocation does not continue from that child branch.
- **L482** — Begin top-level controller error handling.
- **L483** — Run main and use its result as the process's exit status.
- **L484** — Catch Ctrl+C.
- **L485** — Print a fresh-line cancellation message to stderr.
- **L486** — Exit with cancellation status 130.
- **L487** — Catch deliberately raised readable RuntimeErrors.
- **L488** — Print only the intended error message with a prefix.
- **L489** — Exit failure.
- **L490** — Catch missing Python/GI imports.
- **L491** — Give Fedora-oriented installation suggestions for GUI and cryptography support. The generic dependency list is in README.
- **L492** — Exit failure for missing dependencies.
- **L493** — Catch expected parsing, network/filesystem and failed-child-command problems.
- **L494** — Comment explains why a raw exception/traceback is not printed: it may contain authentication data.
- **L495** — Give a generic preparation failure diagnostic while allowing preceding safe child messages to supply context.
- **L496** — Exit with failure status 1.


[[#File index|↑ File index]]

### 7.4 tifr-import-totp

**6 lines** · Symlink-aware QR importer launcher.


A small executable wrapper gives the QR importer a friendly command name without .py. It resolves symlinks to find its adjacent Python implementation. The file is Python despite having no extension; the shebang determines the interpreter.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.4.1 L1–L6 · Resolve the wrapper and execute the adjacent implementation


```python
#!/usr/bin/env python3
"""Launch the adjacent QR importer, including when invoked through a symlink."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().with_suffix(".py")), run_name="__main__")
```

**Line-by-line explanation**

- **L1** — Ask env to locate and run python3.
- **L2** — Module docstring explains the wrapper's location-independent purpose.
- **L3** — Import Path for resolving this file's real location and changing its filename suffix.
- **L4** — Import runpy for executing another Python source file as a program.
- **L6** — \_\_file\_\_ is this wrapper's pathname; resolve() follows symbolic links, with\_suffix('.py') selects the neighboring tifr-import-totp.py, and str converts that Path to text. run\_name='\_\_main\_\_' makes the implementation run its guarded main block. This wrapper therefore launches the scanner rather than merely importing definitions.


[[#File index|↑ File index]]

### 7.5 tifr-import-totp.py

**256 lines** · Local QR decoding, TOTP calculation and Qt window.


This optional desktop tool imports one Google Authenticator migration QR locally. It reads a QR from a camera or an existing image, extracts a TOTP setup seed and settings, and displays a locally calculated code for comparison. You manually paste the seed into KeePassXC and save that database; this tool does not write the KeePass database. fields() parses a limited protobuf binary format, decode_export() interprets the migration payload, current_code() computes TOTP, and Scanner provides the Qt window. Most users can understand the VPN workflow before learning this binary parser. The line-by-line material below includes it for completeness.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.5.1 L1–L13 · Interpreter and binary, crypto and URL libraries


```python
#!/usr/bin/env python3
"""Read one Google Authenticator migration QR locally; never log its contents."""

import base64
import argparse
import hashlib
import hmac
import struct
import sys
import time
from urllib.parse import parse_qs, urlsplit
```

**Line-by-line explanation**

- **L1** — Use python3 from PATH to execute the importer.
- **L2** — Docstring states the single-account, local-processing intent.
- **L4** — base64 converts the migration URL's Base64 payload and the seed's Base32 representation. Neither encoding encrypts the seed.
- **L5** — argparse handles the optional --image switch.
- **L6** — hashlib supplies SHA1/SHA256/SHA512 hash functions used by TOTP.
- **L7** — hmac provides the keyed hash operation used by HOTP/TOTP.
- **L8** — struct packs the time counter into an exact binary representation.
- **L9** — sys supplies command arguments, process exit and stderr.
- **L10** — time supplies Unix time for TOTP and a monotonic clock for scan throttling.
- **L11** — urlsplit parses the QR's URI; parse\_qs decodes its query parameters.


#### 7.5.2 L14–L29 · Decode variable-length integers


```python
def fields(data):
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
```

**Line-by-line explanation**

- **L14** — Define a generator that reads selected protobuf wire-format fields from a byte sequence. It yields one (field number, decoded value) pair at a time rather than returning a fully interpreted account.
- **L15** — Start the byte-reading position at 0.
- **L17** — Define a nested reader for a variable-length unsigned integer, called a varint.
- **L18** — nonlocal offset means assignments update the containing fields function's position instead of creating a new local position inside varint.
- **L19** — Initialize the integer being reconstructed.
- **L20** — Read up to ten 7-bit groups, shifting by 0, 7, 14, ... 63 bits. This bounds parsing effort for a malformed endless integer.
- **L21** — Before accessing a byte, check that input remains.
- **L22** — Fail clearly if the integer extends beyond the supplied bytes.
- **L23** — Read one byte as an integer from 0 to 255.
- **L24** — Advance to the next byte.
- **L25** — Keep the byte's lower seven bits with &127, shift them into position with <<shift, and combine them with the current value using |=. These are bit operations on binary digits.
- **L26** — The upper bit, value 128, indicates that another varint byte follows. If it is absent, this integer is complete. 'not byte & 128' is evaluated as not (byte & 128).
- **L27** — Return the decoded integer, preserving the updated enclosing offset.
- **L28** — If ten groups never completed the integer, reject the encoding rather than looping forever.


#### 7.5.3 L30–L47 · Parse supported protobuf field wire types


```python
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
            value = data[offset:offset + size]
            offset += size
        else:
            raise ValueError("Unsupported export QR format.")
        yield number, value
```

**Line-by-line explanation**

- **L30** — Continue reading fields while unconsumed bytes remain.
- **L31** — Read the field tag as a varint.
- **L32** — The tag's upper bits encode the field number (>>3); its low three bits encode the wire type (&7). Python can assign both extracted values at once.
- **L33** — Protobuf field number 0 is invalid.
- **L34** — Reject that malformed tag.
- **L35** — Wire type 0 means the field value is another varint.
- **L36** — Decode that numeric value with the nested helper.
- **L37** — Handle fixed-width 64-bit fields (wire 1), length-delimited fields (wire 2), and fixed-width 32-bit fields (wire 5).
- **L38** — For wire 2, read the byte length; for fixed widths use 8 or 4 bytes. This line contains nested conditional expressions.
- **L39** — Check that the requested byte count fits the remaining input.
- **L40** — Reject truncated field data before slicing it.
- **L41** — Extract that byte range. Python slices use start inclusive/end exclusive indices.
- **L42** — Advance the current reading position by that many bytes.
- **L43** — Unsupported wire types take the error path; this is a deliberately limited parser, not a complete protobuf library.
- **L44** — Report the unsupported format.
- **L45** — yield returns one field pair to the caller and suspends this generator; iteration later resumes at the next field.


#### 7.5.4 L48–L64 · Decode and validate one migration export


```python
def decode_export(text):
    uri = urlsplit(text)
    if uri.scheme != "otpauth-migration" or uri.netloc != "offline":
        raise ValueError("Show the Google Authenticator export QR, selecting only TIFR.")
    encoded = parse_qs(uri.query).get("data", [""])[0].replace(" ", "+")
    if not encoded or len(encoded) > 32000:
        raise ValueError("Invalid export QR.")
    try:
        payload = list(fields(base64.b64decode(encoded + "=" * (-len(encoded) % 4), validate=True)))
    except Exception:
        raise ValueError("Could not decode this export QR.") from None
    accounts = [value for number, value in payload if number == 1]
    if len(accounts) != 1 or any(number == 3 and value > 1 for number, value in payload):
        raise ValueError("Export only the TIFR entry, then scan the new QR.")
    account = dict(fields(accounts[0]))
    if not isinstance(account.get(1), bytes) or not account[1]:
        raise ValueError("The export contains no setup key.")
```

**Line-by-line explanation**

- **L48** — Define interpretation of the text decoded from a Google Authenticator export QR.
- **L49** — Split the URI into its parts without making any network request.
- **L50** — Require the migration URI scheme and the offline authority name. Despite looking like a URL, this payload is treated as local data here.
- **L51** — Explain that this tool expects a Google Authenticator migration export containing only the TIFR entry, not an arbitrary QR or a normal webpage.
- **L52** — Get the first data query value, defaulting to empty text. parse\_qs normally treats + as spaces, so replace spaces with + before decoding this Base64 payload.
- **L53** — Reject an empty payload or one longer than 32,000 encoded characters to bound input size.
- **L54** — Raise a format error for that invalid size/content condition.
- **L55** — Try Base64 decoding and binary-field parsing.
- **L56** — Restore Base64 '=' padding to a multiple of 4, decode with validation, then consume fields into a list. -len(encoded)%4 calculates needed padding characters.
- **L57** — Catch decoding or wire-parser problems.
- **L58** — Replace detailed internals with a generic invalid-export error and suppress exception chaining.
- **L59** — Collect field-1 values, which this migration format uses for account messages.
- **L60** — Require exactly one account and reject a batch-size field (number 3) above 1. This avoids accidentally importing a collection of unrelated accounts or an incomplete multi-QR batch.
- **L61** — Ask the user to export only the TIFR entry.
- **L62** — Parse the sole embedded account message and map field numbers to decoded values. dict keeps the last value for repeated keys; this code expects the account's scalar fields.
- **L63** — Require field 1 to contain a nonempty bytes object, the raw shared secret.
- **L64** — Reject an account without a usable seed.


#### 7.5.5 L65–L76 · Normalize supported account settings


```python
    algorithms = {1: "SHA1", 2: "SHA256", 3: "SHA512"}
    digits = {1: 6, 2: 8}
    if account.get(6) != 2 or account.get(4) not in algorithms or account.get(5) not in digits:
        raise ValueError("This export is not a supported time-based authenticator entry.")
    return {
        "secret": base64.b32encode(account[1]).decode().rstrip("="),
        "name": account.get(2, b"").decode("utf-8"),
        "issuer": account.get(3, b"").decode("utf-8"),
        "algorithm": algorithms[account[4]], "digits": digits[account[5]], "period": 30,
    }
```

**Line-by-line explanation**

- **L65** — Map the migration format's algorithm enumeration numbers to hash names.
- **L66** — Map its digit enumeration numbers to six or eight displayed digits.
- **L67** — Require account type 2 (TOTP) and one supported algorithm/digit setting. HOTP counter-based entries and unsupported enum values are rejected.
- **L68** — Explain that only the supported time-based entries can be imported.
- **L69** — Return a normalized account dictionary rather than the raw numbered protobuf fields.
- **L70** — Encode the binary seed using Base32, convert to text and remove '=' padding for display/pasting. Anyone holding this setup seed can derive future codes; it is much more sensitive than one short-lived code.
- **L71** — Decode the optional account name as UTF-8, falling back to empty bytes if missing.
- **L72** — Decode the optional issuer label similarly.
- **L73** — Translate hash/digit enums and set the period to 30 seconds. This importer assumes that period rather than discovering an arbitrary period from this migration payload.
- **L74** — End the normalized dictionary.


#### 7.5.6 L77–L86 · Calculate a current TOTP from seed and time


```python
def current_code(account, timestamp=None):
    secret = account["secret"]
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    step = int(time.time() if timestamp is None else timestamp) // account["period"]
    digest = hmac.new(key, struct.pack(">Q", step), getattr(hashlib, account["algorithm"].lower())).digest()
    offset = digest[-1] & 15
    value = int.from_bytes(digest[offset:offset + 4], "big") & 0x7fffffff
    return str(value % 10 ** account["digits"]).zfill(account["digits"])
```

**Line-by-line explanation**

- **L77** — Define local TOTP calculation. timestamp=None uses the real clock; a supplied timestamp makes deterministic tests possible.
- **L78** — Get the Base32 seed text from the normalized account.
- **L79** — Restore padding to a multiple of 8 characters and decode the text back to raw key bytes.
- **L80** — Choose current/specified Unix time, convert to whole seconds and integer-divide by the period. // is floor division. Every instant in the same time window produces the same counter.
- **L81** — Pack that counter as big-endian unsigned 8-byte integer ('>Q'), select the account's lowercase hash function through getattr, and compute HMAC using the seed. digest() returns raw bytes. HMAC is a keyed hash, not encryption of the timestamp.
- **L82** — Use the low four bits of the final digest byte to select an offset from 0 to 15, the HOTP dynamic-truncation step.
- **L83** — Read four bytes at that offset in big-endian order and clear the highest bit with &0x7fffffff, yielding a nonnegative 31-bit number.
- **L84** — Reduce the number modulo 10 raised to the number of digits, convert to text and pad leading zeros. For example, a 6-digit numeric value 123 must display as 000123. These steps implement the time-based algorithm tested against RFC 6238.


#### 7.5.7 L87–L102 · Arguments and optional GUI/scanner imports


```python
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="store_true", help="use a local QR image without starting the webcam")
    args = parser.parse_args()

    import numpy as np
    import zxingcpp
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices, QVideoSink
    from PySide6.QtWidgets import (
        QApplication, QCheckBox, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
    )

    app = QApplication(sys.argv)
```

**Line-by-line explanation**

- **L87** — Define the desktop command's main function.
- **L88** — Create a command-line parser from the module description.
- **L89** — Register --image as a boolean flag that skips webcam initialization and lets the user choose a local image.
- **L90** — Parse arguments before importing heavy GUI/scanner libraries; --help can therefore work without loading the camera stack.
- **L92** — Import NumPy under the alias np for viewing grayscale image memory as a numeric array.
- **L93** — Import the ZXing C++ Python bindings for detecting and decoding QR codes.
- **L94** — Import Qt timers and namespace constants for alignment and display flags.
- **L95** — Import Qt's image and display-pixmap types.
- **L96** — Import camera discovery, camera device, capture session and frame-receiving classes.
- **L97** — Begin importing window/control widgets.
- **L98** — List the application, checkbox, file dialog, labels, text field, button, vertical layout and generic window widget needed below.
- **L99** — End the multiline import statement.
- **L101** — Create the Qt application object using this process's arguments. It owns the GUI event loop and clipboard access.


#### 7.5.8 L103–L125 · Scanner state, instructions and image selection


```python
    class Scanner(QWidget):
        def __init__(self):
            super().__init__()
            self.account = None
            self.last_scan = 0
            self.copied = None
            self.setWindowTitle("TIFR — import Google Authenticator locally")
            self.resize(860, 700)
            layout = QVBoxLayout(self)
            intro = QLabel("On your phone: Google Authenticator → Transfer codes → Export → select only TIFR.\n"
                           "Use a local QR image or hold the QR toward the camera. Everything stays on this laptop.")
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
```

**Line-by-line explanation**

- **L103** — Define Scanner as a subclass of QWidget, inheriting ordinary window behavior while adding scanning state and methods.
- **L104** — Define the object initializer. self refers to the particular Scanner instance being initialized.
- **L105** — Initialize the inherited QWidget part before configuring this custom window.
- **L106** — No decoded account exists yet.
- **L107** — Initialize the last-scan time for throttling camera processing.
- **L108** — Track which setup key this tool placed on the clipboard so it can avoid erasing unrelated later clipboard text.
- **L109** — Set the window title.
- **L110** — Choose its initial size: 860 by 700 pixels.
- **L111** — Create a vertical layout owned by this window.
- **L112** — Start the instruction label with the phone-side export steps.
- **L113** — Continue the same label with local image/camera choices and the tool's local-processing intent. This implementation has no upload call in the scanning path.
- **L114** — Wrap long instructions to the available width.
- **L115** — Add that label to the layout.
- **L116** — Create a label that will show camera preview frames or status text.
- **L117** — Center its content using a Qt alignment flag.
- **L118** — Give the preview a minimum area of 640 by 360 pixels.
- **L119** — Add it to the layout with stretch factor 1, letting it take available space.
- **L120** — Create a button for choosing an existing local QR image.
- **L121** — Connect its clicked signal to this instance's open\_image method. The method is passed without () so it runs on future clicks rather than immediately.
- **L122** — Add the file-selection button to the window layout.
- **L123** — Create a status label stating that this program does not save captured frames/setup keys as files. Selecting an image does not remove the original image file.
- **L124** — Allow status messages to wrap.
- **L125** — Add the status label.


#### 7.5.9 L126–L146 · Masked seed field, reveal option and copy controls


```python
            self.key = QLineEdit()
            self.key.setReadOnly(True)
            self.key.setEchoMode(QLineEdit.EchoMode.Password)
            self.key.setPlaceholderText("The setup key will appear here after a successful scan")
            layout.addWidget(self.key)
            show = QCheckBox("Reveal setup key in this window")
            show.toggled.connect(lambda checked: self.key.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password))
            layout.addWidget(show)
            self.copy = QPushButton("Copy setup key for KeePassXC (clears after 60 seconds)")
            self.copy.setEnabled(False)
            self.copy.clicked.connect(self.copy_key)
            layout.addWidget(self.copy)
            self.code = QLabel()
            self.code.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(self.code)
            instructions = QLabel("After scanning: KeePassXC → right-click TIFR → TOTP → Set up TOTP.\n"
                                  "Paste the setup key and match the displayed digits, period and algorithm.\n"
                                  "Compare the codes with your phone, then save the KeePassXC database.")
            instructions.setWordWrap(True)
            layout.addWidget(instructions)
```

**Line-by-line explanation**

- **L126** — Create a single-line field for the decoded setup seed.
- **L127** — Make it read-only so accidental typing cannot alter the displayed seed.
- **L128** — Mask its text by default, like a password field.
- **L129** — Show placeholder instructions until a seed is available.
- **L130** — Add the masked field to the layout.
- **L131** — Create a checkbox controlling whether the seed is visibly revealed.
- **L132** — Connect the checkbox toggle to an anonymous callback that changes the seed field's echo mode.
- **L133** — Use Normal when checked and Password when unchecked. This changes visual masking, not whether the seed exists in process memory.
- **L134** — Add the reveal checkbox.
- **L135** — Create the clipboard-copy button and describe its intended 60-second cleanup.
- **L136** — Disable the button until a valid account has been decoded.
- **L137** — Connect future clicks to copy\_key.
- **L138** — Add the copy button.
- **L139** — Create a label for the currently calculated TOTP and countdown.
- **L140** — Allow selecting/copying that displayed code with the mouse.
- **L141** — Add the code label.
- **L142** — Create instructions describing where the user must paste the seed in KeePassXC.
- **L143** — Explain matching digits, period and algorithm rather than assuming the seed alone specifies everything.
- **L144** — Remind the user to compare phone codes and save the database. The importer does not perform that save itself.
- **L145** — Wrap these instructions.
- **L146** — Add them to the layout.


#### 7.5.10 L147–L167 · Timers, video sink and camera setup


```python
            self.session = QMediaCaptureSession(self)
            self.sink = QVideoSink(self)
            self.session.setVideoSink(self.sink)
            self.sink.videoFrameChanged.connect(self.frame)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_code)
            self.timer.start(1000)
            cameras = QMediaDevices.videoInputs() if not args.image else []
            if not cameras:
                self.preview.setText("Open the QR image using the button below")
                self.status.setText("Image mode: the webcam is off. No decoded setup keys are saved to files.")
                return
            self.camera = QCamera(cameras[0], self)
            formats = [fmt for fmt in cameras[0].videoFormats()
                       if 640 <= fmt.resolution().width() <= 1920]
            if formats:
                self.camera.setCameraFormat(max(formats, key=lambda fmt: fmt.resolution().width()))
            self.session.setCamera(self.camera)
            self.camera.errorOccurred.connect(lambda *_: self.status.setText("Camera error: " + self.camera.errorString()))
            self.camera.start()
```

**Line-by-line explanation**

- **L147** — Create a media capture session associated with this window.
- **L148** — Create a video sink that receives camera frames for Python processing.
- **L149** — Route session video output to that sink.
- **L150** — Connect each new-frame event to this instance's frame method. This 'connect' is Qt event registration, unrelated to establishing a VPN.
- **L151** — Create a timer owned by this window.
- **L152** — Connect each timer event to refresh\_code.
- **L153** — Run the timer every 1000 milliseconds, updating the current code/countdown once per second.
- **L154** — Discover camera inputs only when --image was not given; in explicit image mode use an empty list and do not enumerate/start a camera here.
- **L155** — If there are no cameras, fall back to image selection.
- **L156** — Replace preview text with a prompt to use the image button.
- **L157** — Explain that the webcam is off and no decoded seeds are written by the tool.
- **L158** — Return from \_\_init\_\_, leaving the window and image button ready to use. This does not exit the application.
- **L159** — Create a camera object for the first detected device, owned by this window.
- **L160** — Begin collecting available formats for that camera.
- **L161** — Keep formats with widths between 640 and 1920 pixels to avoid extremely tiny/huge frame sizes.
- **L162** — Only set a preferred format when the filtered list is nonempty.
- **L163** — Pick the format with greatest width from the filtered list. lambda fmt: ... supplies the comparison key to max; it does not explicitly choose by frame rate or height.
- **L164** — Attach the camera to the capture session.
- **L165** — On camera errors, update the status with Qt's camera error string; ignore unused signal arguments.
- **L166** — Start the camera asynchronously.


#### 7.5.11 L168–L184 · Choose and read an existing QR image


```python
        def open_image(self):
            if self.account:
                return
            if hasattr(self, "camera"):
                self.camera.stop()
            path, _ = QFileDialog.getOpenFileName(self, "Open Google Authenticator export QR", "",
                                                 "Images (*.png *.jpg *.jpeg *.webp *.bmp);;All files (*)")
            if not path:
                return
            image = QImage(path)
            if image.isNull():
                self.status.setText("Could not open this image. Select a PNG or JPEG containing the export QR.")
                return
            self.scan_image(image)
            if not self.account:
                self.status.setText("No supported single-entry export QR was found. Use the original full-resolution image and select only TIFR when exporting.")
```

**Line-by-line explanation**

- **L168** — Define the image-file selection handler.
- **L169** — If an account has already been accepted, ignore further import requests.
- **L170** — Return in that completed state.
- **L171** — Check whether this Scanner ever initialized a camera attribute; image-only instances may not have one.
- **L172** — Stop the camera before opening the file chooser.
- **L173** — Open a native-style file-selection dialog; unpack chosen path and selected-filter text, ignoring the latter with \_.
- **L174** — Offer common image extension filters and an all-files option. These filters guide selection; QImage still validates whether the chosen file can be loaded.
- **L175** — An empty path means the user cancelled.
- **L176** — Return on cancellation. If a camera was stopped above, this code does not restart it automatically.
- **L177** — Load the selected file into a Qt image in memory.
- **L178** — Check whether image loading failed.
- **L179** — Show a readable image-format error.
- **L180** — Return without attempting QR decoding on a null image.
- **L181** — Try scanning the loaded image.
- **L182** — If no account was accepted, provide a more specific single-entry/full-resolution suggestion.
- **L183** — Update the status message accordingly.


#### 7.5.12 L185–L196 · Throttle and preview camera frames


```python
        def frame(self, frame):
            if self.account or time.monotonic() - self.last_scan < 0.2:
                return
            self.last_scan = time.monotonic()
            image = frame.toImage()
            if image.isNull():
                return
            self.preview.setPixmap(QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            self.scan_image(image)
```

**Line-by-line explanation**

- **L185** — Define the per-camera-frame callback. The argument named frame is a Qt video frame, separate from this method's own name.
- **L186** — Skip work if an account is already accepted, or if fewer than 0.2 seconds elapsed since the last scan. This caps scanning near five attempts per second without blocking the camera's own frame delivery.
- **L187** — Return for that skipped frame.
- **L188** — Record the current monotonic time, a clock suitable for elapsed durations because normal wall-clock adjustments do not make it jump backwards.
- **L189** — Convert the received video frame to a QImage for preview and scanning.
- **L190** — If conversion produced no usable image, skip it.
- **L191** — Return for an unusable frame.
- **L192** — Convert the image to a display pixmap and scale it for the preview label.
- **L193** — Fit to the current preview dimensions while keeping the original aspect ratio.
- **L194** — Request smooth scaling for display. This affects the preview; scan\_image below still receives the original image.
- **L195** — Attempt QR detection on that frame's full image.


#### 7.5.13 L197–L208 · Scan grayscale pixel data for a migration QR


```python
        def scan_image(self, image):
            gray = image.convertToFormat(QImage.Format.Format_Grayscale8)
            pixels = np.frombuffer(gray.constBits(), dtype=np.uint8).reshape(
                gray.height(), gray.bytesPerLine())[:, :gray.width()]
            try:
                results = zxingcpp.read_barcodes(pixels, formats=zxingcpp.BarcodeFormat.QRCode)
                for result in results:
                    self.account = decode_export(result.text)
                    break
            except Exception:
                self.status.setText("Could not import this QR. Export only the TIFR entry from Google Authenticator and try again.")
                return
```

**Line-by-line explanation**

- **L197** — Define the common scanner used by both camera frames and selected image files.
- **L198** — Convert to an 8-bit grayscale image, giving one intensity byte per pixel rather than separate red/green/blue channels.
- **L199** — View the image's memory as unsigned 8-bit numbers and begin shaping it into rows. frombuffer avoids an unnecessary full copy while the QImage remains alive.
- **L200** — Use bytesPerLine as the real row stride, then slice each row to gray.width() to remove alignment padding. Height × stride may exceed height × visible width.
- **L201** — Guard the external QR decoder and migration parsing operations.
- **L202** — Ask ZXing to look specifically for QRCode format in the grayscale pixel array.
- **L203** — Loop over detected QR results.
- **L204** — Parse one QR's text as a supported single-account migration export and save the normalized account.
- **L205** — Stop after the first successfully parsed account. An exception on an earlier unsupported result enters the error handler instead of continuing through all results.
- **L206** — Catch decoder/parser failures without dumping QR contents.
- **L207** — Show a generic instruction to export just TIFR and retry.
- **L208** — Return from this failed scan.


#### 7.5.14 L209–L222 · Display accepted seed metadata and stop the camera


```python
            if self.account:
                if hasattr(self, "camera"):
                    self.camera.stop()
                self.open_button.setEnabled(False)
                print("QR decoded locally; camera stopped. Complete the import in KeePassXC.", flush=True)
                self.preview.clear()
                self.preview.setText("QR scanned — camera is off")
                self.key.setText(self.account["secret"])
                self.copy.setEnabled(True)
                self.status.setText(
                    f"Account: {self.account['name']} | Issuer: {self.account['issuer']}\n"
                    f"Settings: {self.account['algorithm']}, {self.account['digits']} digits, {self.account['period']} seconds")
                self.refresh_code()
```

**Line-by-line explanation**

- **L209** — If an account was decoded, update the UI into the completed/import-ready state.
- **L210** — Check whether camera hardware was initialized.
- **L211** — Stop it immediately after successful decoding.
- **L212** — Disable choosing another image during this instance's completed state.
- **L213** — Print a generic success message without the seed or code; flush so it appears promptly.
- **L214** — Remove the camera image from the preview label.
- **L215** — Replace it with a camera-off success message.
- **L216** — Put the sensitive Base32 seed in the read-only masked field. Masking reduces casual viewing, but the value is still stored in GUI/process memory.
- **L217** — Enable copying the setup seed.
- **L218** — Begin a status message showing account metadata and TOTP settings.
- **L219** — Display the account and issuer labels, which may identify the account but are not the secret seed.
- **L220** — Display the hash algorithm, number of digits and period so KeePassXC can be configured to match.
- **L221** — Update the code/countdown immediately instead of waiting for the next one-second timer event.


#### 7.5.15 L223–L237 · Refresh the code and manage clipboard lifetime


```python
        def refresh_code(self):
            if self.account:
                remaining = self.account["period"] - int(time.time()) % self.account["period"]
                self.code.setText(f"Current code: {current_code(self.account)}   ({remaining} seconds remaining)")

        def copy_key(self):
            self.copied = self.account["secret"]
            app.clipboard().setText(self.copied)
            QTimer.singleShot(60000, self.clear_clipboard)

        def clear_clipboard(self):
            if self.copied and app.clipboard().text() == self.copied:
                app.clipboard().clear()
            self.copied = None
```

**Line-by-line explanation**

- **L223** — Define code-display refresh.
- **L224** — Only calculate/display a code if an account is available.
- **L225** — Compute seconds until the current period ends using modulo (%). At an exact boundary it displays a full period, e.g. 30 seconds.
- **L226** — Calculate and display the current local code with the countdown. This calculation uses seed and time; it does not ask Google's or TIFR's server for a code.
- **L228** — Define the copy-button handler.
- **L229** — Remember the seed this window is copying, so cleanup can check ownership of the current clipboard text.
- **L230** — Put it on the system clipboard for manual paste into KeePassXC. A clipboard manager can retain its own history; clearing the live clipboard cannot revoke independent copies.
- **L231** — Schedule a one-time clear\_clipboard callback 60,000 milliseconds later. It requires the GUI event loop to keep running normally.
- **L233** — Define guarded clipboard cleanup.
- **L234** — Clear only if this window previously copied a nonempty seed and the current clipboard still equals it. This avoids deleting different text the user copied afterward.
- **L235** — Clear the current clipboard content.
- **L236** — Drop the stored copied-value reference after attempting cleanup.


#### 7.5.16 L238–L250 · Close the camera/window and run the application


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

- **L238** — Override QWidget's close-event handler so closing the window cleans up devices and displayed state.
- **L239** — If a camera object exists, stop it.
- **L240** — Request camera stop.
- **L241** — Attempt clipboard cleanup immediately rather than waiting for the timer.
- **L242** — Clear the seed field.
- **L243** — Drop the normalized account reference. This is not guaranteed secure wiping of every copy of the seed in memory.
- **L244** — Accept the close event so the window may close.
- **L246** — Construct one Scanner window, running its initializer and choosing camera or image mode.
- **L247** — Make the window visible.
- **L248** — Run Qt's event loop until the application closes, then return its exit status. Signals/timers/camera events drive the methods while this waits.


#### 7.5.17 L251–L256 · Main guard and generic startup error


```python
if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        print("The local QR scanner could not start. No QR contents were logged.", file=sys.stderr)
        sys.exit(1)
```

**Line-by-line explanation**

- **L251** — Execute this guarded block when invoked as a program, including through the extensionless wrapper's run\_name='\_\_main\_\_'.
- **L252** — Begin top-level startup handling.
- **L253** — Run main and turn its return value into the process exit status.
- **L254** — Catch ordinary startup/runtime Exceptions without exposing QR contents in a traceback. KeyboardInterrupt and SystemExit are not subclasses of Exception, so they are not caught by this specific handler.
- **L255** — Write a generic scanner-startup diagnostic to stderr.
- **L256** — Exit failure.


[[#File index|↑ File index]]

### 7.6 install.sh

**57 lines** · User installation, copied helpers and command symlinks.


This POSIX shell installer copies the five working commands/helpers to a user directory and creates three convenient command-name links. It does not install system packages, configure a VPN account, or build the placeholder Python package. Defaults are ~/bin/tifr for helpers and ~/.local/bin for command links. Your ~/bin itself is a symlink into ~/projects/dotfiles/bin, so the default helper location reaches that directory on your machine. I observed no tifr* command links in ~/.local/bin during this inspection; the installer describes defaults, not proof that you currently invoke those defaults.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.6.1 L1–L18 · Interpreter, strict options and help


```sh
#!/bin/sh
# Install commands for the current user; never change shell startup files.
set -eu

if [ "${1:-}" = --help ]; then
    cat <<'EOF'
Usage: ./install.sh
Copies the helpers to ~/bin/tifr and links commands into ~/.local/bin.
Override with TIFR_INSTALL_DIR and TIFR_COMMAND_DIR (absolute paths).
Run again after updating the checkout to install the new version.
EOF
    exit 0
fi
if [ "$#" -ne 0 ]; then
    echo 'Usage: ./install.sh [--help]' >&2
    exit 2
fi
```

**Line-by-line explanation**

- **L1** — Run with /bin/sh, the system's POSIX-compatible shell. Unlike tifrvpn, this script avoids Zsh-specific syntax.
- **L2** — Comment describing intended scope: install for the current user without rewriting shell startup files.
- **L3** — set -e stops on many unhandled command failures; set -u treats expansion of an unset variable as an error. Conditional commands have special -e rules, so it is not a universal exception mechanism.
- **L5** — ${1:-} safely expands the first argument, or empty text when no argument exists. This avoids set -u errors. Check whether help was requested.
- **L6** — Start a here-document fed to cat. Quoting 'EOF' prevents variable and command expansion inside the following help text.
- **L7–L10** — A literal help-text line printed by cat. These lines describe the command and its defaults; they are not shell instructions executed here.
- **L11** — The matching EOF ends the here-document; it is a delimiter, not part of the printed help.
- **L12** — Exit the installer successfully after displaying help.
- **L13** — Close the help condition.
- **L14** — $# counts arguments; -ne is numeric not-equal. Any remaining argument is invalid.
- **L15** — Print usage to standard error using >&2, which redirects echo's output to file descriptor 2.
- **L16** — Exit with invalid-arguments status 2.
- **L17** — Close argument checking.


#### 7.6.2 L19–L32 · Resolve source and validate destination paths


```sh
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
```

**Line-by-line explanation**

- **L19** — Find the installer's own directory even when invoked elsewhere or through a symlink. readlink -f resolves the executable path, dirname removes its filename, cd enters that directory inside command substitution, and pwd prints the absolute directory. CDPATH= suppresses a user's special cd-search setting for this operation. The outer $(...) captures the result without changing the caller's working directory.
- **L20** — Choose the helper destination: TIFR\_INSTALL\_DIR when nonempty, otherwise $HOME/bin/tifr. HOME is the user's home directory; the script reads it rather than changing it.
- **L21** — Choose command-link destination from TIFR\_COMMAND\_DIR, falling back to $HOME/.local/bin.
- **L22** — Loop over both destinations to validate them before copying anything.
- **L23** — Begin pattern matching on the directory string.
- **L24** — A string beginning with / is an absolute Linux path and is accepted. /\* is a pattern, not a division operation.
- **L25** — Reject all other paths, explain why and exit status 2. Absolute paths make the outcome independent of the current directory.
- **L26** — End the case statement.
- **L27** — End destination validation loop.
- **L28** — Check that helper and command-link destination strings are different.
- **L29** — Explain why they must be separate directories: a command link must not replace its own helper file.
- **L30** — Exit on that invalid configuration.
- **L31** — Close the check. This comparison checks strings, not every possible alias of the same real directory.


#### 7.6.3 L33–L46 · Check existing public commands before copying


```sh
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
```

**Line-by-line explanation**

- **L33–L34** — Comments explain that command-name conflicts are checked before file copying. Existing links pointing to this installation may be refreshed; unrelated commands are rejected.
- **L35** — Loop over the three public command names the installer creates.
- **L36** — By default, each command links to a same-name helper.
- **L37** — Special-case tifr-otp: its helper filename ends in .py. The test succeeds for other commands; for tifr-otp it fails and || assigns the .py target.
- **L38** — Build the full destination path for this public command link.
- **L39** — Check either that a target exists (-e) or that it is a symlink (-L). The second test also catches broken symlinks, which -e alone does not.
- **L40** — Reject a regular existing file or a symlink whose stored link text differs from the expected helper path. This checks the link text using readlink, rather than resolving every equivalent spelling.
- **L41** — Explain the conflict and suggest selecting a different command directory.
- **L42** — Exit failure before any helper is copied.
- **L43** — Finish the conflict condition.
- **L44** — Finish the destination-exists condition.
- **L45** — End public-command preflight loop.


#### 7.6.4 L47–L57 · Copy helpers, create symlinks and report destinations


```sh
mkdir -p -- "$install_dir" "$command_dir"
for file in tifrvpn tifr-vpn-auth.py tifr-otp.py tifr-import-totp tifr-import-totp.py; do
    if [ "$(readlink -f -- "$source_dir/$file")" != "$(readlink -f -- "$install_dir/$file")" ]; then
        install -m 755 -- "$source_dir/$file" "$install_dir/$file"
    fi
done
ln -sfn -- "$install_dir/tifrvpn" "$command_dir/tifrvpn"
ln -sfn -- "$install_dir/tifr-otp.py" "$command_dir/tifr-otp"
ln -sfn -- "$install_dir/tifr-import-totp" "$command_dir/tifr-import-totp"
printf 'Installed helpers: %s\nCommands: %s\n' "$install_dir" "$command_dir"
printf 'Ensure the command directory is on PATH, then follow README.md to set up credentials.\n'
```

**Line-by-line explanation**

- **L47** — Create helper and command directories, including missing parents. -p tolerates existing directories. -- ends command options to treat later text as paths.
- **L48** — Loop over the five actual runtime files copied by this installer; README, tests and packaging files are not installed here.
- **L49** — Compare resolved source/destination filenames. If they name the same actual file, skip copying to avoid a same-file error.
- **L50** — install is a system command that copies a file and sets permissions. Mode 755 gives the owner read/write/execute, and group/others read/execute. Scripts need execute permission for direct invocation.
- **L51** — Close the same-file guard.
- **L52** — End file-copy loop.
- **L53** — Create/update the tifrvpn symlink. -s means symbolic link, -f replaces an existing permitted link, and -n avoids treating a link to a directory as the directory itself. Earlier checks prevent intentional replacement of unrelated command names.
- **L54** — Link the friendly tifr-otp command name to tifr-otp.py.
- **L55** — Link the QR import command name to its extensionless Python wrapper.
- **L56** — Print the two chosen directory paths using %s placeholders. \\n means a newline in printf's format string.
- **L57** — Remind the user that command lookup requires the command directory in PATH and that credential setup is a separate step.


[[#File index|↑ File index]]

### 7.7 tests/test_setup.py

**112 lines** · Offline installation, configuration, parsing and TOTP checks.


Tests are programs that exercise other programs and check expected results. These tests use temporary directories and invented credentials. They install into an artificial HOME, not your real helper directory, and mock vault command responses. They verify installation, configuration precedence, output handling and a published TOTP example. They do not demonstrate a successful live TIFR connection. unittest discovers methods whose names begin test_. setUp runs before each test; addCleanup schedules cleanup even if an assertion fails.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.7.1 L1–L17 · Imports and loading definitions without launching the tools


```python
"""Offline packaging/configuration checks; no real vault, keyring or VPN access."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
OTP = runpy.run_path(str(ROOT / "tifr-otp.py"))
QR = runpy.run_path(str(ROOT / "tifr-import-totp.py"))
```

**Line-by-line explanation**

- **L1** — Docstring states that checks are offline and do not access a personal vault/keyring/VPN.
- **L2** — contextlib temporarily redirects Python stdout to an in-memory buffer.
- **L3** — io provides StringIO, a file-like string buffer for output assertions.
- **L4** — json serializes invented configuration dictionaries for test files.
- **L5** — os gives access to environment variables for patching isolated configuration.
- **L6** — Path builds paths for temporary homes and repository files.
- **L7** — runpy loads helper definitions without running their CLI main guards.
- **L8** — subprocess runs the installer/help commands and supplies invented CompletedProcess responses for mocked vault reads.
- **L9** — tempfile creates automatically cleaned isolated test directories.
- **L10** — unittest provides test discovery, test cases and assertions.
- **L11** — patch temporarily replaces environment contents or functions, restoring them when its with block ends.
- **L13** — Resolve this test file and move up two path components using parents\[1\] to find the repository root. parents\[0\] is the tests directory.
- **L14** — Load tifr-otp.py's global definitions into a dictionary, so OTP\['configuration'\] refers to the function without running the OTP command.
- **L15** — Load the importer's functions without launching Qt because its main guard is not activated.


#### 7.7.2 L18–L27 · Isolated temporary HOME for each test


```python
class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tifr setup ")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = dict(os.environ, HOME=str(self.home))
        for name in ("TIFR_INSTALL_DIR", "TIFR_COMMAND_DIR", "XDG_CONFIG_HOME",
                     "TIFR_KEEPASS_DATABASE", "TIFR_KEEPASS_ENTRY", "TIFR_KEEPASS_PASSWORD_FILE"):
            self.environment.pop(name, None)
```

**Line-by-line explanation**

- **L18** — Create a test class inheriting unittest.TestCase and its assertion/cleanup helpers.
- **L19** — Define setup performed independently before each test method.
- **L20** — Create a temporary directory whose prefix deliberately includes a space, exercising correct path quoting.
- **L21** — Register its cleanup with the test framework, including if a later assertion raises.
- **L22** — Store this temporary location as the artificial user's home directory.
- **L23** — Copy the environment and override HOME only in this test's dictionary. The real user's HOME is not changed globally here.
- **L24–L25** — Enumerate installation/configuration variables that must not leak from the real user's environment into test behavior.
- **L26** — Remove each override from the test environment if present; None avoids an error when missing.


#### 7.7.3 L28–L31 · Run the installer from another directory


```python
    def install(self):
        return subprocess.run([str(ROOT / "install.sh")], cwd="/", env=self.environment,
                              capture_output=True, text=True)
```

**Line-by-line explanation**

- **L28** — Define a convenience method that executes the repository installer in the isolated home.
- **L29** — Run the installer from / rather than its source directory, proving it finds adjacent source files itself. Pass the test-specific environment.
- **L30** — Capture stdout/stderr as strings so assertions can inspect results without displaying routine test subprocess output.


#### 7.7.4 L32–L43 · Verify installation, symlinks, help and repeatability


```python
    def test_install_from_another_directory_and_command_symlinks(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("tifrvpn", "tifr-otp", "tifr-import-totp"):
            executable = self.home / ".local/bin" / command
            self.assertTrue(executable.is_symlink())
            result = subprocess.run([str(executable), "--help"], cwd="/", env=self.environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / ".zshrc").exists())
        self.assertEqual(self.install().returncode, 0)
```

**Line-by-line explanation**

- **L32** — Test installation from another current directory, command symlinks, help behavior and repeat installation.
- **L33** — Perform the first isolated installation.
- **L34** — Require successful exit. If it fails, include stderr as the assertion message to aid diagnosis.
- **L35** — Check each public command created by the installer.
- **L36** — Build its path under the temporary ~/.local/bin.
- **L37** — Require it to be a symbolic link, rather than an unintended duplicate script file.
- **L38** — Run that installed command with --help from / in the isolated environment. This checks wrapper location handling without launching a real login.
- **L39** — Capture its output for assertions.
- **L40** — Require successful help output for every command.
- **L41** — Verify that the installer did not create a .zshrc file in the artificial home.
- **L42** — Require a second installation to succeed, checking repeatability/idempotent behavior for this situation.


#### 7.7.5 L44–L51 · Preserve unrelated commands before copying


```python
    def test_unrelated_command_is_preserved_before_any_copy(self):
        command = self.home / ".local/bin/tifrvpn"
        command.parent.mkdir(parents=True)
        command.write_text("existing command")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(command.read_text(), "existing command")
        self.assertFalse((self.home / "bin/tifr").exists())
```

**Line-by-line explanation**

- **L44** — Test that an unrelated existing public command is preserved and copying has not started before conflict detection.
- **L45** — Choose the public tifrvpn command location in the isolated home.
- **L46** — Create its parent directories.
- **L47** — Write a dummy existing file that represents an unrelated user's command.
- **L48** — Require the installer to reject the conflict with a nonzero status.
- **L49** — Verify the preexisting file's content is unchanged.
- **L50** — Verify helper copying did not create ~/bin/tifr before the conflict was reported.


#### 7.7.6 L52–L58 · Custom installation paths with spaces


```python
    def test_custom_install_locations(self):
        self.environment.update(TIFR_INSTALL_DIR=str(self.home / "custom helpers"),
                                TIFR_COMMAND_DIR=str(self.home / "custom commands"))
        self.assertEqual(self.install().returncode, 0)
        command = self.home / "custom commands/tifrvpn"
        self.assertEqual(command.resolve(), self.home / "custom helpers/tifrvpn")
```

**Line-by-line explanation**

- **L52** — Test custom helper/command destinations, including spaces in their names.
- **L53** — Override helper destination in the isolated environment dictionary.
- **L54** — Override command destination too; this continues the same update call.
- **L55** — Require successful installation to those custom paths.
- **L56** — Select the custom public command path.
- **L57** — Resolve its symlink and require it to reach the expected custom helper file.


#### 7.7.7 L59–L63 · Write temporary configuration


```python
    def configure(self, settings):
        config = self.home / ".config/tifr-vpn/config.json"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(json.dumps(settings))
```

**Line-by-line explanation**

- **L59** — Define a utility for writing a test JSON configuration file.
- **L60** — Choose the default config path inside the artificial home.
- **L61** — Create its parent directory if necessary.
- **L62** — Serialize the supplied settings as JSON text and save them there. This utility writes invented settings only.


#### 7.7.8 L64–L76 · Defaults, JSON settings and environment precedence


```python
    def test_default_and_configured_paths_and_environment_override(self):
        database = self.home / "Documents/KeePass/Passwords.kdbx"
        database.parent.mkdir(parents=True)
        database.touch()
        with patch.dict(os.environ, self.environment, clear=True):
            self.assertEqual(OTP["configuration"]()[0], database)
            self.configure({"database": str(database), "entry": "VPN/TIFR",
                            "password_file": "~/private/master.gpg"})
            self.assertEqual(OTP["configuration"]()[1:],
                             (self.home / "private/master.gpg", "VPN/TIFR"))
            with patch.dict(os.environ, {"TIFR_KEEPASS_ENTRY": "Other/TIFR"}):
                self.assertEqual(OTP["configuration"]()[2], "Other/TIFR")
```

**Line-by-line explanation**

- **L64** — Test default paths, JSON customization, and the higher-priority environment override.
- **L65** — Choose the default KeePass database pathname under the artificial home.
- **L66** — Create its parent directories.
- **L67** — Create an empty placeholder file; configuration checks file existence but this test does not open a real vault.
- **L68** — Temporarily replace os.environ with the isolated test environment, restoring it afterward. clear=True prevents unrelated real settings from surviving.
- **L69** — Require configuration to choose the expected default database.
- **L70** — Write a JSON config selecting the placeholder database and a grouped entry path.
- **L71** — Set a custom encrypted-password pathname beginning with ~ to test home expansion.
- **L72** — Check the last two tuple values from configuration, using \[1:\] to exclude the database element.
- **L73** — Require the expanded encrypted-file path and configured entry name.
- **L74** — Temporarily set an entry environment variable on top of the JSON config.
- **L75** — Verify the environment-selected entry takes precedence over the JSON-selected one.


#### 7.7.9 L77–L84 · Reject invalid configurations


```python
    def test_bad_config_is_rejected(self):
        for settings in ([], {"database": 42}, {"entry": ""}, {"unknown": "value"},
                         {"database": "relative.kdbx"}):
            with self.subTest(settings=settings), patch.dict(os.environ, self.environment, clear=True):
                self.configure(settings)
                with self.assertRaises(RuntimeError):
                    OTP["configuration"]()
```

**Line-by-line explanation**

- **L77** — Test rejecting malformed or unsupported config objects.
- **L78–L79** — Try a JSON list, nonstring path, empty entry, unknown key and relative database path. Each represents a different configuration requirement.
- **L80** — Label each iteration as a subtest and isolate environment variables so all bad cases can be reported separately.
- **L81** — Write the current invalid config to the temporary home.
- **L82** — Require the configuration call to raise RuntimeError; absence of that exception is a failing test.
- **L83** — Invoke the parser being tested.


#### 7.7.10 L85–L96 · Keep parsed login fields out of output and command arguments


```python
    def test_login_parser_keeps_fields_out_of_output(self):
        result = subprocess.CompletedProcess([], 0, "example-user\nexample-password\n123456\n", "")
        output = io.StringIO()
        with patch("shutil.which", return_value="/usr/bin/keepassxc-cli"), \
                patch("subprocess.run", return_value=result) as run, \
                contextlib.redirect_stdout(output):
            login = OTP["read_login"]("example-master", Path("example.kdbx"), "TIFR")
        self.assertEqual(login, {"username": "example-user", "password": "example-password"})
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn("example-master", run.call_args.args[0])
        self.assertIn("--show-protected", run.call_args.args[0])
```

**Line-by-line explanation**

- **L85** — Test that login parsing returns credentials without printing them or putting the vault master password in the command arguments.
- **L86** — Create a fake successful CLI result with invented username/password/code lines. These are examples, not account data.
- **L87** — Create an in-memory string buffer for anything Python prints.
- **L88** — Pretend keepassxc-cli is available so the tested code takes that command path.
- **L89** — Replace subprocess.run with a fake returning the invented result, and retain its call-recording mock as run.
- **L90** — Redirect stdout into the string buffer during the tested operation.
- **L91** — Read the fake login through the real parsing function. No real vault command executes because subprocess.run is patched.
- **L92** — Require exactly the intended returned username/password dictionary.
- **L93** — Require no stdout output from read\_login.
- **L94** — Inspect the first positional argument to the mocked subprocess call (the command list), confirming the database master password is absent from that list. The real implementation supplies it on stdin instead.
- **L95** — Require protected-value retrieval to be requested explicitly from KeePassXC.


#### 7.7.11 L97–L103 · Reject missing login fields


```python
    def test_missing_login_fields_are_rejected(self):
        result = subprocess.CompletedProcess([], 0, "example-user\n\n123456\n", "")
        with patch("shutil.which", return_value="/usr/bin/keepassxc-cli"), \
                patch("subprocess.run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "Username and Password"):
                OTP["read_login"]("example-master", Path("example.kdbx"), "TIFR")
```

**Line-by-line explanation**

- **L97** — Test rejecting missing login fields.
- **L98** — Build fake output with an empty second line, representing an absent VPN password.
- **L99** — Pretend the native KeePassXC CLI exists.
- **L100** — Return the fake incomplete output instead of executing an external vault command.
- **L101** — Require a RuntimeError whose message mentions Username and Password.
- **L102** — Call the real parsing function with invented inputs.


#### 7.7.12 L104–L112 · Check the published TOTP vector and test entry point


```python
    def test_totp_against_public_rfc6238_vector(self):
        # Public RFC test key; never use it for a real account.
        account = {"secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", "period": 30,
                   "algorithm": "SHA1", "digits": 8}
        self.assertEqual(QR["current_code"](account, timestamp=59), "94287082")


if __name__ == "__main__":
    unittest.main()
```

**Line-by-line explanation**

- **L104** — Test the TOTP implementation against an independently published known-answer example, which is stronger than calculating an expected value with the same implementation under test.
- **L105** — Clarify that this seed is public test data and unsuitable for a real account.
- **L106** — Build an account using the RFC's public seed and 30-second time step.
- **L107** — Choose SHA1 and 8 digits for this test vector.
- **L108** — At Unix timestamp 59, require the published output 94287082. A fixed timestamp makes the test deterministic regardless of the current clock.
- **L111** — When this file is directly executed, launch its own tests. Test discovery imports it and finds the class without requiring this block.
- **L112** — Run unittest's command-line test runner.


[[#File index|↑ File index]]

### 7.8 tests/test_quiet.py

**145 lines** · Offline quiet-mode, prompt and cleanup checks.


These tests verify quiet-mode orchestration without starting a real VPN, unlocking real credentials or launching a real Xvfb browser. Mock objects remember how functions were called; side_effect can imitate a callback or exception sequence. The launcher test writes a temporary Zsh harness with dummy network actions, then checks real argument dispatch. Passing these tests checks the specified offline behaviors; it does not cover every real GUI, server response or process-lifecycle possibility.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.8.1 L1–L22 · Load modules and offline test tools


```python
"""Quiet-mode checks without accessing a real vault, keyring or VPN."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("tifr_auth_test", ROOT / "tifr-vpn-auth.py")
AUTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTH)
OTP_SPEC = importlib.util.spec_from_file_location("tifr_otp_test", ROOT / "tifr-otp.py")
OTP = importlib.util.module_from_spec(OTP_SPEC)
OTP_SPEC.loader.exec_module(OTP)
```

**Line-by-line explanation**

- **L1** — Docstring identifies the offline quiet-mode test scope.
- **L2** — contextlib is used to capture Python stderr output safely in memory.
- **L3** — importlib.util loads files with hyphenated names as test modules under safe internal module names.
- **L4** — io supplies StringIO for captured output.
- **L5** — os lets tests inspect/temporarily change environment variables.
- **L6** — Path handles repository and temporary-file paths.
- **L7** — shutil checks whether Zsh exists for the real launcher harness test.
- **L8** — signal supplies the SIGTERM/SIGKILL constants asserted in cleanup tests.
- **L9** — subprocess supplies fake result/timeout objects and runs the isolated Zsh harness.
- **L10** — tempfile creates disposable placeholder files and harness directories.
- **L11** — unittest supplies the test framework.
- **L12** — Mock creates stand-in process objects; patch temporarily replaces real functions and environment values.
- **L14** — Find the project root by resolving the test file and selecting its grandparent directory.
- **L15** — Create an import specification for the authentication helper using a valid Python test-module name and its actual source path.
- **L16** — Create an unexecuted module object from that specification.
- **L17** — Execute the source into that module. Its \_\_name\_\_ is tifr\_auth\_test, so the CLI main guard does not run.
- **L18** — Prepare the corresponding module specification for the OTP helper.
- **L19** — Create its module object.
- **L20** — Execute only its definitions and module setup, leaving its CLI inactive.


#### 7.8.2 L23–L45 · Require unlocking before virtual-display startup


```python
class QuietAuthenticationTests(unittest.TestCase):
    def test_quiet_unlocks_before_starting_virtual_display(self):
        events = []
        helper = {
            "configuration": lambda: (Path("example.kdbx"), Path("example.gpg"), "TIFR"),
            "decrypt_password": lambda path: events.append("unlock") or "example-master",
        }
        def browser(command):
            events.append("browser")
            self.assertEqual(command[:2], ["xvfb-run", "-a"])
            self.assertEqual(command[-2:], ["--sso-window", "--quiet"])
            self.assertNotIn("example-master", command)
            return subprocess.CompletedProcess(command, 0, "DSID=example-session")
        output = io.StringIO()
        with patch.object(AUTH.shutil, "which", return_value="/example/executable"), \
                patch.object(AUTH.runpy, "run_path", return_value=helper), \
                patch.object(AUTH, "background_browser", side_effect=browser), \
                contextlib.redirect_stderr(output):
            self.assertEqual(AUTH.authenticate(quiet=True), "DSID=example-session")
        self.assertEqual(events, ["unlock", "browser"])
        self.assertNotIn("example-master", output.getvalue())
        self.assertNotIn("example-session", output.getvalue())
```

**Line-by-line explanation**

- **L23** — Define a TestCase grouping Python authentication/supervision checks.
- **L24** — Check that quiet mode unlocks GPG before starting the virtual display and does not expose example secret values in command arguments or progress.
- **L25** — Create a list recording the order of important operations.
- **L26** — Start a fake dictionary resembling runpy's loaded OTP-helper definitions.
- **L27** — Provide a no-argument lambda returning example database/ciphertext paths and an entry name.
- **L28** — Provide a lambda that records unlock and returns an invented master password. list.append returns None, so 'or example-master' produces the desired fake return string.
- **L29** — Finish the fake helper dictionary.
- **L30** — Define a fake background\_browser replacement that also asserts its received command.
- **L31** — Record that browser startup occurred.
- **L32** — Require xvfb-run -a to be the first two command arguments.
- **L33** — Require internal browser mode and --quiet to be the final two arguments.
- **L34** — Ensure the example database master password was not embedded in command arguments.
- **L35** — Return a fake successful child result containing an invented DSID string on stdout.
- **L36** — Create the stderr capture buffer.
- **L37** — Pretend all needed executables exist by replacing shutil.which in the helper module.
- **L38** — Replace loading the real OTP-helper definitions with the fake helper dictionary.
- **L39** — Replace background\_browser with the fake callable via side\_effect so it records order and validates its command.
- **L40** — Capture stderr while the operation runs; each context manager is restored at block exit.
- **L41** — Call the real authenticate orchestration and require the fake browser session string to be returned.
- **L42** — Require unlock to precede browser in the event list.
- **L43** — Ensure the example master password did not appear in captured progress output.
- **L44** — Ensure the example session value did not appear there either.


#### 7.8.3 L46–L52 · Fail on missing tools before vault access


```python
    def test_missing_xvfb_fails_before_reading_credentials(self):
        with patch.object(AUTH.shutil, "which", return_value=None), \
                patch.object(AUTH.runpy, "run_path") as helper:
            with self.assertRaisesRegex(RuntimeError, "requires: xvfb-run, Xvfb, xauth"):
                AUTH.authenticate(quiet=True)
            helper.assert_not_called()
```

**Line-by-line explanation**

- **L46** — Test missing quiet-mode dependencies before vault helpers are accessed.
- **L47** — Make every executable lookup return None.
- **L48** — Replace runpy.run\_path with a recording mock so real helper loading cannot occur.
- **L49** — Require the readable missing-dependency RuntimeError to mention all three tools.
- **L50** — Call quiet authentication through the real orchestration function.
- **L51** — Confirm credential-helper loading was never attempted.


#### 7.8.4 L53–L60 · Preserve the foreground browser path


```python
    def test_foreground_keeps_existing_browser_path(self):
        result = subprocess.CompletedProcess([], 0, "DSID=example-session")
        with patch.object(AUTH.subprocess, "run", return_value=result) as run, \
                patch.object(AUTH, "background_browser") as background:
            self.assertEqual(AUTH.authenticate(), "DSID=example-session")
            self.assertNotIn("--quiet", run.call_args.args[0])
            background.assert_not_called()
```

**Line-by-line explanation**

- **L53** — Test that ordinary foreground authentication still uses its existing subprocess path.
- **L54** — Prepare a fake successful subprocess result.
- **L55** — Replace subprocess.run and retain its call history.
- **L56** — Replace background\_browser with a mock so an accidental quiet-path call is detectable.
- **L57** — Run foreground authentication and require the expected cookie result.
- **L58** — Check the recorded command omitted --quiet.
- **L59** — Confirm the virtual-display wrapper was not called.


#### 7.8.5 L61–L72 · Use X11 and a separate process group


```python
    def test_virtual_display_uses_x11_and_owns_its_process_group(self):
        process = Mock(returncode=0)
        process.communicate.return_value = ("DSID=example-session", None)
        with patch.object(AUTH.subprocess, "Popen", return_value=process) as popen, \
                patch.dict(os.environ, {"WAYLAND_DISPLAY": "wayland-example", "GDK_BACKEND": "wayland"}):
            AUTH.background_browser(["example-browser"])
        options = popen.call_args.kwargs
        self.assertEqual(options["env"]["GDK_BACKEND"], "x11")
        self.assertNotIn("WAYLAND_DISPLAY", options["env"])
        self.assertTrue(options["start_new_session"])
        process.communicate.assert_called_once_with(timeout=120)
```

**Line-by-line explanation**

- **L61** — Test child environment isolation and process-group ownership.
- **L62** — Create a fake process object whose returncode is success.
- **L63** — Make its communicate method return fake cookie stdout and no captured stderr.
- **L64** — Replace Popen so no real process is created, retaining construction arguments for inspection.
- **L65** — Temporarily make the parent look like a Wayland session to test that child-only X11 overrides are applied correctly.
- **L66** — Call background\_browser with an example command; it uses the fake process.
- **L67** — Read keyword arguments supplied to the mocked Popen constructor.
- **L68** — Require the child's GDK\_BACKEND to be x11.
- **L69** — Require the child's environment not to include WAYLAND\_DISPLAY.
- **L70** — Require start\_new\_session=True for process-group cleanup.
- **L71** — Verify communicate was called exactly once with timeout=120 in this successful path.


#### 7.8.6 L73–L86 · Escalate cleanup after timeout


```python
    def test_timeout_escalates_cleanup_of_browser_and_display(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [
            subprocess.TimeoutExpired("example-browser", 120),
            subprocess.TimeoutExpired("example-browser", 5),
            ("", None),
        ]
        with patch.object(AUTH.subprocess, "Popen", return_value=process), \
                patch.object(AUTH.os, "killpg") as kill:
            with self.assertRaisesRegex(RuntimeError, "timed out.*Retry tifrvpn -c"):
                AUTH.background_browser(["example-browser"])
        self.assertEqual([call.args for call in kill.call_args_list],
                         [(123456789, signal.SIGTERM), (123456789, signal.SIGKILL)])
```

**Line-by-line explanation**

- **L73** — Test cleanup escalating from SIGTERM to SIGKILL after timeout.
- **L74** — Create a fake process with an intentionally example PID. Real os.killpg will be patched, so no actual process is signaled.
- **L75** — Give successive communicate calls a list of simulated outcomes/exceptions.
- **L76** — The first call represents the browser's 120-second deadline expiring immediately in the test.
- **L77** — The next represents the 5-second graceful-cleanup wait expiring immediately too.
- **L78** — The final call succeeds with empty output after forced termination.
- **L79** — End the simulated outcomes list.
- **L80** — Replace actual process creation with that fake process.
- **L81** — Replace os.killpg with a recording mock; this is essential to keep the test from sending real signals.
- **L82** — Require a readable timeout error containing a visible-retry instruction.
- **L83** — Run the real supervisor logic against the fake process.
- **L84** — Extract every recorded signal call's positional arguments.
- **L85** — Require SIGTERM first and SIGKILL second, both addressed to the fake process group.


#### 7.8.7 L87–L95 · Clean up and propagate cancellation


```python
    def test_cancel_cleans_up_and_propagates(self):
        process = Mock(pid=123456789)
        process.communicate.side_effect = [KeyboardInterrupt(), ("", None)]
        with patch.object(AUTH.subprocess, "Popen", return_value=process), \
                patch.object(AUTH.os, "killpg") as kill:
            with self.assertRaises(KeyboardInterrupt):
                AUTH.background_browser(["example-browser"])
        kill.assert_called_once_with(123456789, signal.SIGTERM)
```

**Line-by-line explanation**

- **L87** — Test Ctrl+C cleanup while preserving the cancellation exception.
- **L88** — Create another fake process, never a live process with this example PID.
- **L89** — Simulate KeyboardInterrupt on the first wait, then successful graceful cleanup on the second.
- **L90** — Mock process creation.
- **L91** — Mock group signaling again so no real signals are sent.
- **L92** — Require KeyboardInterrupt to propagate after cleanup instead of being converted into a timeout RuntimeError.
- **L93** — Run the supervisor against those simulated events.
- **L94** — Require one SIGTERM and no escalation on this successful cleanup path.


#### 7.8.8 L96–L107 · Forbid hidden GPG pinentry prompts


```python
    def test_hidden_gpg_never_opens_a_pinentry_prompt(self):
        with tempfile.NamedTemporaryFile() as password_file:
            result = subprocess.CompletedProcess([], 1, b"", b"example error")
            with patch.object(OTP.subprocess, "run", return_value=result) as run:
                with self.assertRaisesRegex(RuntimeError, "Could not decrypt"):
                    OTP.decrypt_password(Path(password_file.name), allow_prompt=False)
        command = run.call_args.args[0]
        self.assertIn("--batch", command)
        self.assertIn("--no-tty", command)
        self.assertEqual(command[command.index("--pinentry-mode") + 1], "error")
```

**Line-by-line explanation**

- **L96** — Test that hidden-browser GPG decryption is configured to fail instead of opening pinentry when an unlock is needed.
- **L97** — Create a harmless existing temporary file so the decrypt function passes its input-file-exists check.
- **L98** — Create a fake failed GPG result with empty plaintext output and example stderr bytes.
- **L99** — Replace GPG subprocess execution with that result and record command arguments.
- **L100** — Require a readable decryption failure.
- **L101** — Call decryption with prompting explicitly forbidden.
- **L102** — Extract the command argument list supplied to the mocked subprocess.
- **L103** — Require --batch.
- **L104** — Require --no-tty.
- **L105** — Find --pinentry-mode in the argument list and require its following value to be error.


#### 7.8.9 L108–L121 · Build a harmless Zsh launcher harness


```python
@unittest.skipUnless(shutil.which("zsh"), "Zsh is required for the launcher")
class QuietLauncherTests(unittest.TestCase):
    def test_option_order_and_forwarding_without_real_network_access(self):
        with tempfile.TemporaryDirectory(prefix="tifr quiet ") as temporary:
            directory = Path(temporary)
            # Source just the functions, then override network-dependent helpers.
            source = (ROOT / "tifrvpn").read_text().removesuffix('tifrvpn "$@"\n')
            harness = directory / "launcher.zsh"
            harness.write_text(source + '''
function tifr-on() { print -r -- "connect:$*"; }
function tifr-off() { print -- disconnect; }
function tifr-status() { print -- status; }
tifrvpn "$@"
''')
```

**Line-by-line explanation**

- **L108** — The @ line is a decorator: skip the launcher test class if Zsh is unavailable. The reason appears in test output instead of producing a misleading failure.
- **L109** — Define the launcher-dispatch test class.
- **L110** — Test valid option order/forwarding and invalid combinations without touching actual network actions.
- **L111** — Create a disposable directory with spaces in its name, exercising path handling.
- **L112** — Convert its pathname to Path for convenient joins.
- **L113** — Comment explains the harness strategy: load function definitions, then replace operations that could touch the network.
- **L114** — Read the real launcher source and remove its final dispatcher invocation. This lets the test define harmless overrides before anything is called.
- **L115** — Choose a temporary Zsh harness filename.
- **L116** — Write the launcher definitions plus a multiline string of replacement functions and one final dispatcher invocation.
- **L117** — Inside that string, redefine connect to print connect: followed by received arguments. This line is text written into the harness, then later executed by Zsh, not Python syntax executed directly here.
- **L118** — Redefine disconnect as a harmless printed marker.
- **L119** — Redefine status as a harmless printed marker.
- **L120** — Invoke the real dispatcher after harmless operation replacements are in place.
- **L121** — Close the Python multiline string and write\_text call.


#### 7.8.10 L122–L134 · Check valid option order and forwarding


```python
            for arguments, expected in [
                (["-c", "--quiet"], "connect:--quiet"),
                (["--quiet", "-c"], "connect:--quiet"),
                (["--quiet"], "connect:--quiet"),
                (["-c"], "connect:"),
                (["-d"], "disconnect"),
                (["-s"], "status"),
            ]:
                with self.subTest(arguments=arguments):
                    result = subprocess.run(["zsh", "-f", str(harness), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), expected)
```

**Line-by-line explanation**

- **L122** — Loop over valid argument lists paired with their expected harmless marker output.
- **L123** — Explicit -c followed by --quiet must forward --quiet to connect.
- **L124** — --quiet before -c must behave identically.
- **L125** — --quiet alone must select connect and forward quiet.
- **L126** — Ordinary -c must connect without extra options.
- **L127** — -d must select disconnect.
- **L128** — -s must select status.
- **L129** — End the list of valid cases and begin its loop body.
- **L130** — Label each case as a subtest so failures show the responsible argument combination.
- **L131** — Actually execute Zsh -f on the temporary harness. \*arguments expands the Python list into separate command arguments.
- **L132** — Capture harness output as strings.
- **L133** — Require success and include stderr if the assertion fails.
- **L134** — Require exactly the expected harmless action marker after trimming trailing whitespace.


#### 7.8.11 L135–L145 · Reject invalid combinations and run tests


```python
            for arguments in (["--quiet", "-d"], ["-s", "--quiet"],
                              ["--quiet", "--setup"], ["-c", "-s"], ["--unknown"]):
                with self.subTest(arguments=arguments):
                    result = subprocess.run(["zsh", "-f", str(harness), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
```

**Line-by-line explanation**

- **L135–L136** — Loop over invalid cases: quiet with disconnect/status/setup, two conflicting actions, and an unknown option.
- **L137** — Label each invalid argument case as a separate subtest.
- **L138** — Run the same harmless harness with that invalid list.
- **L139** — Capture its output for assertions.
- **L140** — Require status 2 for invalid command arguments.
- **L141** — Require no action marker on stdout, proving rejection happened before any selected action ran.
- **L144** — Only invoke unittest's CLI runner when this test file is directly executed.
- **L145** — Run the tests in that direct-execution case.


[[#File index|↑ File index]]

### 7.9 pyproject.toml

**23 lines** · Python metadata, dependency ranges and placeholder package command.


TOML is a configuration format, not Python code. [section] opens a settings table, key = value stores a setting, quoted text is a string, and [...] is an array. This file describes a Python package and its declared Python dependencies. It does not install NetworkManager, GTK, KeePassXC, GPG or Zsh. The declared tifrvpn-tui package command currently leads to a two-line placeholder; the functioning VPN command comes from install.sh and the root-level scripts.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.9.1 L1–L9 · Project identity, author metadata and Python requirement


```toml
[project]
name = "tifrvpn-tui"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "sohamch08", email = "sohamchatterjee999@gmail.com" }
]
requires-python = ">=3.13"
```

**Line-by-line explanation**

- **L1** — Open the standard project-metadata table.
- **L2** — Set the distribution/package project name to tifrvpn-tui. A distribution name can contain a hyphen even though Python import names generally use underscores.
- **L3** — Declare package version 0.1.0, a release label rather than the Python interpreter version.
- **L4** — The description remains generated placeholder text; it does not describe the actual working VPN scripts yet.
- **L5** — Point packaging tools to README.md as the long project description.
- **L6** — Begin the array of author records.
- **L7** — Store the declared author name and contact email as metadata. This does not configure VPN login or send email.
- **L8** — Close the author array.
- **L9** — Declare Python 3.13 or newer for this package. This is a requirement recorded by packaging tools, not a command that upgrades your Python automatically.


#### 7.9.2 L10–L17 · Declared Python dependencies


```toml
dependencies = [
    "argparse>=1.4.0",
    "cryptography>=50.0.2",
    "numpy>=2.5.4",
    "pyside6>=6.12.0",
    "zxing-cpp>=3.1.1",
]
```

**Line-by-line explanation**

- **L10** — Begin declared direct Python runtime dependencies.
- **L11** — Declare the separately distributed argparse package. Python 3.13 already includes argparse in its standard library, so the core import in these scripts does not require this extra dependency declaration.
- **L12** — Require cryptography at least 50.0.2; activate() uses it to parse the verified server certificate and serialize its public key. >= is a minimum requirement, not an exact pin.
- **L13** — Require NumPy at least 2.5.4 for the optional QR importer's pixel arrays.
- **L14** — Require PySide6 at least 6.12.0 for Qt dialogs and the scanner window/camera UI. Normal SSO browsing instead uses GTK/WebKit through GI.
- **L15** — Require zxing-cpp at least 3.1.1 for QR detection/decoding.
- **L16** — Close dependency array.


#### 7.9.3 L18–L23 · Console entry point and build system


```toml
[project.scripts]
tifrvpn-tui = "tifrvpn_tui:main"

[build-system]
requires = ["uv_build>=0.13.6,<0.14.0"]
build-backend = "uv_build"
```

**Line-by-line explanation**

- **L18** — Open the console-script entry-point table for Python package installation.
- **L19** — Tell packaging tools to create a tifrvpn-tui command that imports tifrvpn\_tui and calls main. In this repository that function only prints a greeting; it is separate from the real tifrvpn launcher installed by install.sh.
- **L21** — Open build-system configuration: how tools build/install the Python distribution.
- **L22** — Specify a compatible uv\_build build-backend version range: at least 0.13.6 and below 0.14.0. These are build-tool requirements, not the VPN connection program itself.
- **L23** — Select uv\_build as the backend implementing Python package build operations.


[[#File index|↑ File index]]

### 7.10 src/tifrvpn_tui/__init__.py

**2 lines** · Two-line Python package placeholder.


The src directory contains a minimal Python package scaffold. It is not the current VPN implementation. __init__.py defines the package's initial code, and the package entry point in pyproject.toml refers to its main function.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.10.1 L1–L2 · The package command currently prints a greeting


```python
def main() -> None:
    print("Hello from tifrvpn-tui!")
```

**Line-by-line explanation**

- **L1** — Define main with no parameters. -> None is a return-type annotation indicating no meaningful returned value; it does not run the function or enforce types at runtime by itself.
- **L2** — Print a greeting. There is no VPN state check, browser, KeePass access or tunnel activation in this function.


[[#File index|↑ File index]]

### 7.11 .envrc

**1 lines** · Optional direnv/uv development environment.


This optional developer-environment file is read by direnv when that tool is configured and the directory is trusted/allowed. It is not executed by the VPN launcher. It is a one-line shell-style instruction for direnv's uv integration, not part of authentication.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.11.1 L1–L1 · Optional developer-environment instruction


```sh
layout uv
```

**Line-by-line explanation**

- **L1** — Ask a direnv setup supporting layout uv to prepare/load a uv-managed Python environment for this directory. It affects development command lookup and Python package availability when that integration is active; the line does not itself contain or load VPN credentials.


[[#File index|↑ File index]]

### 7.12 .python-version

**1 lines** · Preferred development interpreter series.


This plain-text file records the preferred development Python version for tools that recognize it, such as uv. It does not change an explicitly chosen /usr/bin/python or install the VPN system dependencies on its own.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.12.1 L1–L1 · Preferred Python version


```text
3.13
```

**Line-by-line explanation**

- **L1** — Request the Python 3.13 series. The actual interpreter invoked by the scripts depends on PATH or sys.executable at runtime.


[[#File index|↑ File index]]

### 7.13 .gitignore

**38 lines** · Generated-file and accidental secret-file exclusions.


Git reads these patterns to decide which untracked files to leave out of ordinary git add operations. This helps avoid committing generated files or secrets, but it does not encrypt anything, remove previously tracked files, or prevent an explicit forced add. The actual vault, GPG data and QR images should remain outside the repository. Blank lines and comments organize rules.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.13.1 L1–L8 · Generated Python files


```text
# Python-generated files
__pycache__/
*.py[cod]
build/
dist/
wheels/
*.egg-info
```

**Line-by-line explanation**

- **L1** — Comment identifying generated Python files in the following group.
- **L2** — Ignore directories named \_\_pycache\_\_, which Python uses for bytecode caches.
- **L3** — Ignore filenames matching .pyc, .pyo or .pyd via the character class \[cod\]. \* matches preceding name text.
- **L4** — Ignore build directories, which hold generated package build products.
- **L5** — Ignore dist directories, which typically hold built distribution archives.
- **L6** — Ignore wheels directories containing generated/downloaded Python wheel files.
- **L7** — Ignore package metadata paths ending .egg-info.


#### 7.13.2 L9–L12 · Virtual environments


```text
# Virtual environments
.venv/
venv/
```

**Line-by-line explanation**

- **L9** — Comment grouping virtual-environment directories.
- **L10** — Ignore the common .venv local Python environment directory.
- **L11** — Ignore the alternative venv environment directory.


#### 7.13.3 L13–L20 · Tool caches and coverage


```text
# Python tool caches and coverage
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
.coverage.*
htmlcov/
```

**Line-by-line explanation**

- **L13** — Comment grouping tool caches and test-coverage results.
- **L14** — Ignore pytest's cached test metadata.
- **L15** — Ignore Ruff's linter cache.
- **L16** — Ignore mypy's static-type-checker cache.
- **L17** — Ignore the default coverage data file.
- **L18** — Ignore suffixed coverage data files, often created by parallel coverage runs.
- **L19** — Ignore generated HTML coverage reports.


#### 7.13.4 L21–L33 · Local configuration and secret-bearing formats


```text
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


#### 7.13.5 L34–L38 · Authenticator image exclusions


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


[[#File index|↑ File index]]

### 7.14 README.md

**182 lines** · Installation, enrollment, usage and troubleshooting instructions.


README.md is the human instruction manual, written in Markdown. Markdown headings use #, backticks mark code, ** makes bold text, and fenced code blocks show terminal examples. None of its commands execute just because you open this file. Its instructions should be read alongside what the implementation actually does. One concrete mismatch: line 84 refers to config.example.json, but that file is absent from the inspected repository. A working optional JSON example is given in this guide's foundations section.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.14.1 L1–L15 · Purpose and quick commands


````markdown
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
````

**Line-by-line explanation**

- **L1** — Markdown's # begins the document title; it is rendered as a heading rather than executed as a shell comment here.
- **L3** — Name the intended VPN portal and the tunnel-management tools used.
- **L4–L5** — Explain that the tool first reuses a valid session and otherwise retrieves username/password/TOTP support from KeePassXC.
- **L7** — Open a fenced code block labeled sh for shell syntax highlighting.
- **L8** — Example explicit connect command; the # and following text are a shell comment within this example.
- **L9** — Example background-browser connect command. quiet hides the sign-in window but preserves progress/errors.
- **L10** — Example status command.
- **L11** — Example disconnect command.
- **L12** — Close the fenced example block.
- **L14** — State the README author's tested platform/version claims and unofficial status. These are documented claims, not fresh verification on every listed version. The implementation still needs a graphical browser engine/display, including Xvfb for quiet sign-in.


#### 7.14.2 L16–L52 · 1. Install dependencies and commands


````markdown
## 1. Install dependencies and commands

Install these dependencies using your preferred package manager:

- **Runtime:** Zsh and Python 3.13 or newer.
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

The installer copies five helpers into `~/bin/tifr/` and links `tifrvpn`,
`tifr-otp` and `tifr-import-totp` into `~/.local/bin/`. Keep that directory on
your shell's `PATH`. No helper needs sourcing; nothing runs at shell startup.
Your login shell can be Bash, Zsh or another shell; the VPN launcher uses Zsh.

Re-run `./install.sh` after updating this checkout. Installation directories can
be overridden with `TIFR_INSTALL_DIR` and `TIFR_COMMAND_DIR` (absolute paths).
````

**Line-by-line explanation**

- **L16** — Second-level Markdown heading for installation.
- **L18** — Introduce dependencies, whose package-manager names depend on Linux distribution.
- **L20** — List interpreters: Zsh for the launcher and Python for helpers.
- **L21** — List tunnel components: NetworkManager, its OpenConnect integration and the OpenConnect implementation.
- **L22–L23** — List credential components: KeePassXC CLI, GPG and a pinentry program that asks to unlock a GPG secret key.
- **L24–L25** — List embedded-browser/keyring GUI libraries and the GI bridge Python uses to call them.
- **L26–L27** — List Python packages and distinguish optional QR import libraries from the main runtime needs.
- **L28** — List the extra programs needed only when a fresh sign-in uses quiet mode.
- **L30–L32** — Explain Python versus system dependency installation and visibility of system-installed GI bindings inside a virtual environment. Merely running install.sh does not install these libraries.
- **L34–L36** — Require a running NetworkManager and working desktop keyring/authorization agents. A minimal window manager may not start these desktop services automatically.
- **L38** — Specify running the installer as your ordinary account.
- **L40** — Begin an example command block.
- **L41** — Run the repository's installer from the checkout.
- **L42** — Prepend ~/.local/bin to PATH in this shell environment. $HOME expands your home directory and $PATH preserves previously searched directories.
- **L43** — End the command block.
- **L45–L46** — Describe the installer's default five-file copy and three public symlinks. These defaults describe intended installation, not a claim that those command links currently exist on your machine.
- **L47–L48** — Explain ordinary executable command lookup, avoiding sourcing these helpers into shell startup files. The launcher's shebang chooses Zsh independently of the interactive shell.
- **L50–L51** — Explain that source updates need reinstallation of copied files and that environment variables can select absolute install locations.


#### 7.14.3 L53–L93 · 2. Save your own login in KeePassXC


````markdown
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
````

**Line-by-line explanation**

- **L53** — Heading for storing the user's TIFR login in the encrypted vault.
- **L55–L56** — Describe opening/creating a password-protected vault at the default expected path, or configuring another path.
- **L57–L58** — Create/save a TIFR entry and fill the account username/password; these differ from the vault's own master password.
- **L59–L61** — Configure TOTP with the enrollment seed and matching settings. Automatic login's time-boundary logic assumes 30-second codes.
- **L62** — Compare with the phone to check settings/clock, then actually save the KeePass database so the CLI can read changes.
- **L64** — Introduce the optional migration importer for an existing Google Authenticator enrollment.
- **L66** — Open a shell example block.
- **L67** — Launch the local QR importer with webcam mode when a camera is available.
- **L68** — A comment introducing image mode.
- **L69** — Launch with --image to skip webcam initialization and choose an already local file.
- **L70** — End the example block.
- **L72–L74** — Explain exporting only TIFR from the phone and manually pasting the decoded setup seed/settings into KeePassXC.
- **L75–L76** — State the tool's local processing and lack of frame/seed file saving. An image selected from disk is still the user's preexisting sensitive file, and the program does not delete it for you.
- **L77** — Explain that transferring the same seed does not remove the phone entry and that the QR/seed must not be publicly posted.
- **L79–L80** — Introduce optional config for a nondefault database or entry path.
- **L82** — Open a shell example block.
- **L83** — Create the normal config directory, including missing parents.
- **L84** — This copy command would require config.example.json in the current directory. That example file is missing from this checkout, so this exact command will fail here. You can create the documented three-field JSON yourself; see this guide's example.
- **L85** — Close the example block.
- **L87–L89** — Describe allowed path forms, grouped entry names and XDG\_CONFIG\_HOME override. Configuration contains locations/entry names, not actual passwords.
- **L90–L91** — List environment variables with higher priority than config JSON values.
- **L92** — Document unsupported vault-unlock methods: this implementation supplies only a master password to the CLI, not additional key-file/hardware-token options.


#### 7.14.4 L94–L118 · 3. Encrypt the database password with GPG


````markdown
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
````

**Line-by-line explanation**

- **L94** — Heading for storing GPG-encrypted access to the database master password.
- **L96** — Require a usable encryption-capable GPG key belonging to the user.
- **L98** — Open a command example block.
- **L99** — Example interactive GPG key-generation command. This guide explains it; no key generation was performed during inspection.
- **L100** — Example command listing secret-key records with long IDs/fingerprints to identify the correct key.
- **L101** — Close the block.
- **L103** — Explain protecting the GPG secret key with its own passphrase; that passphrase is distinct from the vault master password and TIFR password.
- **L105** — Open an example command block.
- **L106** — Run the OTP helper's interactive master-password encryption setup.
- **L107** — Close the block.
- **L109–L110** — Show explicit fingerprint selection when automatic key selection is ambiguous.
- **L111–L112** — Explain local verification and encryption. Verification checks the database entry/TOTP output, not an actual server login.
- **L113** — Give default ciphertext path and owner-only read/write permission mode 600.
- **L114** — Clarify that the TIFR account password remains in the encrypted vault, rather than being copied into this ciphertext file as its direct contents.
- **L116–L117** — Describe intentionally printing the current short-lived OTP for a phone comparison.


#### 7.14.5 L119–L157 · 4. Connect


````markdown
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
````

**Line-by-line explanation**

- **L119** — Heading for normal connection workflow.
- **L121** — Open an example block.
- **L122** — Create/update NetworkManager's profile, a different action from tifr-otp --setup.
- **L123** — Connect using the launcher.
- **L124** — End the example block.
- **L126–L127** — Explain ordinary-user execution and possible PolicyKit authorization prompts controlled by desktop/system policy.
- **L129–L130** — Describe cache reuse first, then visible browser autofill when a fresh sign-in is needed.
- **L131–L132** — Explain GPG unlock and the user's explicit choice when the portal warns that another session would be terminated.
- **L133** — Describe successful sign-in closing the browser and enabling tunnel activation. In the implementation, the browser returns first and the controller then calls activate.
- **L134** — KeePassXC GUI/phone need not remain open: local CLI access and a copied enrollment seed provide credentials/codes.
- **L136** — Show both supported quiet-connect syntaxes.
- **L137–L138** — Describe attempting GPG unlock on the real desktop before launching the Xvfb browser, with terminal diagnostics remaining visible.
- **L139–L141** — Explain hidden-mode failure on known input/error cases and its 120-second browser wait. Cleanup adds a grace period, and earlier GPG prompts/later tunnel activation are outside that browser deadline. Known session-replacement warnings are detected; the helper has no automatic confirmation-click action.
- **L143** — Show a shell alias: a short command expansion defined in a shell. It is optional convenience, not required runtime code.
- **L145** — Markdown table header naming the command and its behavior columns.
- **L146** — Markdown delimiter row separating table headings from data rows.
- **L147** — Table entry for explicit connect, which shows status if already active.
- **L148** — Table entry for disconnect.
- **L149** — Table entry for status and network configuration output.
- **L150** — Table entry for no-argument toggle, which disconnects a nondeactivated state or otherwise connects.
- **L151** — Table entry for clearing this helper's desktop-keyring sessions without stopping a live tunnel.
- **L152** — Table entry for replacing encrypted master-password storage after changing the vault password.
- **L154–L156** — Explain why the NetworkManager applet alone cannot replace this browser-assisted authentication flow. Its ordinary OpenConnect form handling may not understand Keycloak forms.


#### 7.14.6 L158–L182 · Troubleshooting and storage


```markdown
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

Offline checks: `python3 -B -m unittest discover -s tests -v` (no VPN or personal
credentials are used).
```

**Line-by-line explanation**

- **L158** — Heading introducing troubleshooting and data locations.
- **L160–L162** — Suggest checking saved credentials, file saving and clock agreement when autofill stops; login-form changes can require code maintenance.
- **L163–L164** — Explain that GPG/keyring unlock and portal confirmation can require user input even with automation.
- **L165–L167** — Show status and NetworkManager journal inspection. journalctl -b selects the current boot, -u selects the service, and --since limits the time interval. Logs may contain personal data, so inspect before sharing.
- **L168–L169** — Document the hardcoded NetworkManager service path, a portability assumption in the launcher.
- **L171–L172** — Describe the encrypted vault and separate GPG ciphertext file. During execution the scripts must decrypt necessary values into process memory to use them.
- **L173–L174** — Describe reusable sessions in the desktop keyring and the anonymous-file-descriptor handoff rather than a named plaintext secret file. This does not guarantee that secrets can never enter swap/core dumps or be inspected by privileged software.
- **L175** — Describe the fixed-origin/path checks before automatic SSO field entry.
- **L176–L177** — Keep actual secret assets out of the repository. .gitignore is an accidental-add safeguard, not an access-control/encryption system.
- **L179** — A Markdown link to the external KeePassXC TOTP guide. The line is a reference, not code run by this repository.
- **L181–L182** — Document offline tests. -B prevents new Python bytecode-cache writes; -m runs unittest as a module; discover scans the tests directory; -v prints test names. These tests use fake credentials and temporary directories.


[[#File index|↑ File index]]

### 7.15 uv.lock

**356 lines** · Exact dependency versions, artifacts, compatibility and hashes.


This is uv's generated dependency lockfile in TOML. pyproject.toml expresses acceptable ranges; the lock records the selected exact package versions and downloadable artifacts used for reproducibility. Many lines differ only because Python versions, operating systems and CPU architectures need different wheel builds. They are annotated here individually as data records; they are not commands you should type or handwritten VPN logic. A Windows/macOS wheel appearing here does not make these Linux-specific scripts work on those systems. Prefer updating a lock with its package-management tool instead of manually editing hashes.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.15.1 L1–L4 · Lockfile format and Python requirement


```toml
version = 1
revision = 5
requires-python = ">=3.13"
```

**Line-by-line explanation**

- **L1** — Lockfile format version, not your project version or Python version. uv reads it to understand the file structure.
- **L2** — Record the lockfile format revision used by the generating uv version. This is tooling metadata, not a count of Git commits.
- **L3** — Record that the resolved project targets Python 3.13 or newer. Different wheel filenames below can describe compatible build tags rather than changing that overall requirement.


#### 7.15.2 L5–L13 · Locked package — argparse


```toml
[[package]]
name = "argparse"
version = "1.4.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/18/dd/e617cfc3f6210ae183374cd9f6a26b20514bbb5a792af97949c5aacddf0f/argparse-1.4.0.tar.gz", hash = "sha256:62b089a55be1d8949cd2bc7e0df0bddb9e028faefc8c32038cc84862aefdd6e4", size = 70508, upload-time = "2015-09-12T20:22:16.217Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/f2/94/3af39d34be01a24a6e65433d19e107099374224905f1e0cc6bbe1fd22a2f/argparse-1.4.0-py2.py3-none-any.whl", hash = "sha256:c31647edb69fd3d465a847ea3157d37bed1f95f19760b11a47aa91c04b666314", size = 23000, upload-time = "2015-09-14T16:03:16.137Z" },
]
```

**Line-by-line explanation**

- **L5** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L6** — Name this locked distribution argparse. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L7** — Pin argparse to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L8** — Record the package registry from which argparse is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L9** — Record the source archive for argparse: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L10** — Begin the list of prebuilt wheel artifacts available for argparse across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L11** — One prebuilt wheel choice: argparse-1.4.0-py2.py3-none-any.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to argparse and is data, not VPN logic.
- **L12** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.3 L14–L35 · Locked package — cffi · records 1


```toml
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
```

**Line-by-line explanation**

- **L14** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L15** — Name this locked distribution cffi. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L16** — Pin cffi to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L17** — Record the package registry from which cffi is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L18** — Begin cffi dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L19** — Reference the dependency named pycparser. marker is a condition limiting when the dependency is needed; here the referenced condition distinguishes Python implementations such as PyPy. It is needed by cffi; dependency resolution also follows that package's own dependency references.
- **L20** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L21** — Record the source archive for cffi: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L22** — Begin the list of prebuilt wheel artifacts available for cffi across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L23** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L24** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L25** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L26** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L27** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux1\_i686.manylinux2014\_i686.manylinux\_2\_17\_i686.manylinux\_2\_5\_i686.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L28** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L29** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L30** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L31** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L32** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L33** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L34** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L35** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.


#### 7.15.4 L36–L57 · Locked package — cffi · records 2


```toml
    { url = "https://files.pythonhosted.org/packages/01/9a/11f687cb39d6a3504060d5242f04f48c735afb4d3d533958a20594890cb2/cffi-2.1.1-cp313-cp313-win_arm64.whl", hash = "sha256:63bbfd5ded17c4840ac07cd8f1c21ba9d9708141f840b324f422f41b207e3973", size = 180078, upload-time = "2026-08-03T21:20:15.917Z" },
    { url = "https://files.pythonhosted.org/packages/d3/7b/d6bbf82b8b96e7391438898c42f5bd96dd02030fd5b64937d248220003e2/cffi-2.1.1-cp314-cp314-ios_13_0_arm64_iphoneos.whl", hash = "sha256:7dbb61fe3a7699468030f71bbe5f8a0e326a151daa91beb11a6fc1f980c55e1c", size = 194064, upload-time = "2026-08-03T21:20:17.148Z" },
    { url = "https://files.pythonhosted.org/packages/94/e6/bcc91b283be94735e268487a054004f0aa19947b6348fa367db53230abc8/cffi-2.1.1-cp314-cp314-ios_13_0_arm64_iphonesimulator.whl", hash = "sha256:f24fb43132a4c6b4cb4eb029492919b2db645be6808d738f244fd146c03c32cb", size = 196720, upload-time = "2026-08-03T21:20:18.268Z" },
    { url = "https://files.pythonhosted.org/packages/d9/99/c4b0c17cacdc9c3b8f280026286a9826d6a208c0f047591a3c3ce99b91fd/cffi-2.1.1-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:d28630f5854ab07ab1fd4aba756de52326c82e6be15d414b12793f1975048b54", size = 184964, upload-time = "2026-08-03T21:20:19.708Z" },
    { url = "https://files.pythonhosted.org/packages/b3/a9/9db617d05d7367c1ad0ab00b3aa6e6f9281edd689b4ee9ea0e5a84e89c97/cffi-2.1.1-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:661c298b4821edebead0c91edd2b00374d67ad7c5a1f7a91d4442633b79d6a72", size = 184962, upload-time = "2026-08-03T21:20:20.833Z" },
    { url = "https://files.pythonhosted.org/packages/67/b8/b42132ca113dc567d37684437b46ca1dafc885902b02a110a02d5b511857/cffi-2.1.1-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:58acb8ab8e295e6c5ea12f888cbb13cf21511ef2a3303a23f4325c29d17fe5c1", size = 222328, upload-time = "2026-08-03T21:20:22.118Z" },
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
```

**Line-by-line explanation**

- **L36** — One prebuilt wheel choice: cffi-2.1.1-cp313-cp313-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L37** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L38** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L39** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L40** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L41** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L42** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L43** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L44** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L45** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L46** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L47** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L48** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L49** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L50** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L51** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L52** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L53** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L54** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L55** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L56** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L57** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.


#### 7.15.5 L58–L79 · Locked package — cffi · records 3


```toml
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
    { url = "https://files.pythonhosted.org/packages/d0/ef/5443574510a1207e6f6bc38ba6e1f1de36cb48fef07b2728bb896a21f430/cffi-2.1.1-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:c26608d2222fb1e94487e4a387d85f13eb55d5ed725cb25a0c589ac4ee60e7bc", size = 188464, upload-time = "2026-08-03T21:21:01.163Z" },
    { url = "https://files.pythonhosted.org/packages/7e/ae/a56fa8c4686ad50e148fcbc8d3ae0d03915ff5c30d795058988c24118cef/cffi-2.1.1-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:4be96343e422f2dfcd12ab5c9f5aebe03f82f737c6bffeca6830b3875cb44aab", size = 188262, upload-time = "2026-08-03T21:21:02.382Z" },
    { url = "https://files.pythonhosted.org/packages/53/b2/6187f46f2912276a3ae284076109cc5c8680482f11f766ccf26db4a86427/cffi-2.1.1-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:937c0052c05a31ca1daf18de3158eed4dbfcb9cc107adbea227728d647be701e", size = 223779, upload-time = "2026-08-03T21:21:03.553Z" },
    { url = "https://files.pythonhosted.org/packages/8a/f6/c3ad28bd19f77047a03084424fbd4cbe997303267c14423737324be0385d/cffi-2.1.1-cp315-cp315t-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl", hash = "sha256:df423d40ee8654634421812bc3b196da3f9bd7d32929da813f8394c4348a5358", size = 211520, upload-time = "2026-08-03T21:21:04.863Z" },
    { url = "https://files.pythonhosted.org/packages/a0/cd/ccac9013a5bd9fd764de118674ab9c805b5ca10c19270d90ee273f8b2240/cffi-2.1.1-cp315-cp315t-manylinux2014_s390x.manylinux_2_17_s390x.whl", hash = "sha256:a730a083190634c65cca36ba5f489531576ebd79bcd5c8e172130f6453127231", size = 210673, upload-time = "2026-08-03T21:21:06.223Z" },
    { url = "https://files.pythonhosted.org/packages/52/86/2976131c639aead931c5bee5aba67e4b09fbeb8018b6f282f70803f923a7/cffi-2.1.1-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:363e05fa78e15116c3c32c210ee36884fd6b9afa6d440e47112c3bd511d64cb6", size = 223835, upload-time = "2026-08-03T21:21:07.539Z" },
```

**Line-by-line explanation**

- **L58** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L59** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L60** — One prebuilt wheel choice: cffi-2.1.1-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L61** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-ios\_13\_0\_arm64\_iphoneos.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L62** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-ios\_13\_0\_arm64\_iphonesimulator.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L63** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L64** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L65** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L66** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L67** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L68** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L69** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L70** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L71** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L72** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L73** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L74** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L75** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L76** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L77** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_ppc64le.manylinux\_2\_17\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L78** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_s390x.manylinux\_2\_17\_s390x.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L79** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.


#### 7.15.6 L80–L86 · Locked package — cffi · records 4


```toml
    { url = "https://files.pythonhosted.org/packages/ac/0c/33a7aeab2f9c76918c52e084beb39c570db3588133412929e8ec06fab90b/cffi-2.1.1-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:770de9db11e84213beec501cfcaa013b019820ca881e03344dea5844f7876d94", size = 226705, upload-time = "2026-08-03T21:21:08.774Z" },
    { url = "https://files.pythonhosted.org/packages/e3/26/2cde30fdde421130bfc18f70395731a6e6b2053c6a1978a5258ff04e72fa/cffi-2.1.1-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:7da0c5eff80f0197f3b3d1232ec5a682a9325f4ae9016a78f5f5ca35f9ced1f5", size = 225539, upload-time = "2026-08-03T21:21:09.911Z" },
    { url = "https://files.pythonhosted.org/packages/6d/cd/a361394c94b2129d604bb846f624a8e88255a3ee33129c434a00d715e64f/cffi-2.1.1-cp315-cp315t-win32.whl", hash = "sha256:06c72bb76605a4b0cd0aad6930b69d4baf7dd5d806cfc409b824191099700e66", size = 182707, upload-time = "2026-08-03T21:21:11.226Z" },
    { url = "https://files.pythonhosted.org/packages/9b/b5/ba2b299993c26577d529b6ae29841f9e15b9fcf004d65f423f4fcf94ade9/cffi-2.1.1-cp315-cp315t-win_amd64.whl", hash = "sha256:d9c275eaacd24aa73f94ffd6de08fc3f932424d8b6c376f4bed7cde376fe7bc3", size = 193772, upload-time = "2026-08-03T21:21:12.39Z" },
    { url = "https://files.pythonhosted.org/packages/aa/29/35e016098c814cd93de9cd320c66b5bfba14dc6ecedd3cb518fa7c408c69/cffi-2.1.1-cp315-cp315t-win_arm64.whl", hash = "sha256:d18e5ac0f2f03f4f518d3e23db0f0cad7faa1da8620e9c09461d443bbf6e6692", size = 186360, upload-time = "2026-08-03T21:21:13.636Z" },
]
```

**Line-by-line explanation**

- **L80** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L81** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L82** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L83** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L84** — One prebuilt wheel choice: cffi-2.1.1-cp315-cp315t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cffi and is data, not VPN logic.
- **L85** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.7 L87–L108 · Locked package — cryptography · records 1


```toml
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
    { url = "https://files.pythonhosted.org/packages/6c/5d/906970b83bbfc1f5bbfb677a143c181f2801f23b6a7204a3b47c42c97e65/cryptography-50.0.2-cp311-abi3-musllinux_1_2_aarch64.whl", hash = "sha256:25784ce8b9621c90c643efb9e1e2162ab3b0224cae446ad5e70e7fcb1ce18b51", size = 4870819, upload-time = "2026-09-30T14:44:06.884Z" },
    { url = "https://files.pythonhosted.org/packages/68/e3/f2298d3bb55e0c4a91841ec4d01b3f020ba8c5fbf15ccdcc6dcf03f97025/cryptography-50.0.2-cp311-abi3-musllinux_1_2_x86_64.whl", hash = "sha256:85d0d9a31b9098e98534226d5686b47264b95e62ce459dc2e62fdfc809f9fe93", size = 5030152, upload-time = "2026-09-30T14:44:09.443Z" },
    { url = "https://files.pythonhosted.org/packages/9a/4f/adfc442765721292fff86d314ce385d3249d22db42295c0dd057727b60f3/cryptography-50.0.2-cp311-abi3-win_amd64.whl", hash = "sha256:7afa5a6602a9f29af1f3a2965f831bae7c9d5d597b7cbb716d41ab3b7d89879c", size = 3824692, upload-time = "2026-09-30T14:44:11.671Z" },
```

**Line-by-line explanation**

- **L87** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L88** — Name this locked distribution cryptography. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L89** — Pin cryptography to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L90** — Record the package registry from which cryptography is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L91** — Begin cryptography dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L92** — Reference the dependency named cffi. marker is a condition limiting when the dependency is needed; here the referenced condition distinguishes Python implementations such as PyPy. It is needed by cryptography; dependency resolution also follows that package's own dependency references.
- **L93** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L94** — Record the source archive for cryptography: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L95** — Begin the list of prebuilt wheel artifacts available for cryptography across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L96** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L97** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L98** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L99** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L100** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L101** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L102** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L103** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L104** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L105** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L106** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L107** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L108** — One prebuilt wheel choice: cryptography-50.0.2-cp311-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.


#### 7.15.8 L109–L130 · Locked package — cryptography · records 2


```toml
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
```

**Line-by-line explanation**

- **L109** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L110** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L111** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L112** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L113** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L114** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L115** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L116** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L117** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L118** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L119** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L120** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L121** — One prebuilt wheel choice: cryptography-50.0.2-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L122** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L123** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L124** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L125** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L126** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L127** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L128** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L129** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L130** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.


#### 7.15.9 L131–L149 · Locked package — cryptography · records 3


```toml
    { url = "https://files.pythonhosted.org/packages/24/95/83378121ef3eaaaf71d4b781577ff794acb39b9e1b87a3f156898c8497ed/cryptography-50.0.2-cp315-abi3.abi3t-manylinux_2_34_x86_64.whl", hash = "sha256:e105ab60406787da31fccc883fc0f733af1efd78f0136a4599692c4083a73d0c", size = 5000859, upload-time = "2026-09-30T14:45:05.009Z" },
    { url = "https://files.pythonhosted.org/packages/22/f7/70fd7ae4d1dbfa7ba29b02e1b9068771519a86027756510b700ce81086a8/cryptography-50.0.2-cp315-abi3.abi3t-musllinux_1_2_aarch64.whl", hash = "sha256:6f8700550aa1474a91e5dc07049c46f98b423b5b1ddd0483e0b51362eeeaf5be", size = 5092151, upload-time = "2026-09-30T15:29:15.932Z" },
    { url = "https://files.pythonhosted.org/packages/d4/be/688367b74de86984bd58d8efacfc7c9e68b89a6a22ced0fb4f38db50254a/cryptography-50.0.2-cp315-abi3.abi3t-musllinux_1_2_x86_64.whl", hash = "sha256:c71be1cbfa5cd9a41ee452acf1eccd82b2c05950358b106ec8ceb83411d1a020", size = 5286120, upload-time = "2026-09-30T15:29:18.309Z" },
    { url = "https://files.pythonhosted.org/packages/39/d1/55f8a3f2ef5d1529e16835ef10cf0fe3d559ce237b46dddc440c0bba3649/cryptography-50.0.2-cp315-abi3.abi3t-win_amd64.whl", hash = "sha256:c423ab384a46c4dff7217b2ea5ba2e11cffdeab6441acd04cf65a369caf0366c", size = 4111557, upload-time = "2026-09-30T15:29:20.155Z" },
    { url = "https://files.pythonhosted.org/packages/23/ad/ac987755d00e1e64273760228d2635ae38dae2be83e3c6e0d3289d91dec3/cryptography-50.0.2-cp39-abi3-macosx_11_0_arm64.whl", hash = "sha256:0ec5f09541743261e66e291b4a0cbf0fb2997aeaab6d9e9c740b9dba1b58d1c2", size = 3943588, upload-time = "2026-09-30T15:29:22.265Z" },
    { url = "https://files.pythonhosted.org/packages/d5/8d/6d585339bedf85d45044c85d8412dac53f2bb6f918e8b7777efba1787844/cryptography-50.0.2-cp39-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl", hash = "sha256:c5e67125c7dca78d199ec4e116aa93dbb83494808ecbb8211a2cb09b1bf41dbd", size = 4756166, upload-time = "2026-09-30T15:29:24.58Z" },
    { url = "https://files.pythonhosted.org/packages/bf/f1/1c1f6874e8550cfddd4b688ceb38cefb6ed15ceed224d56f133f3d88c214/cryptography-50.0.2-cp39-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl", hash = "sha256:ee247f5c245c9a2fe7c8e2214e295918838e44e00a45a6718451e4004219e767", size = 4749145, upload-time = "2026-09-30T15:29:26.807Z" },
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
```

**Line-by-line explanation**

- **L131** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L132** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L133** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L134** — One prebuilt wheel choice: cryptography-50.0.2-cp315-abi3.abi3t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L135** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L136** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux2014\_aarch64.manylinux\_2\_17\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L137** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux2014\_x86\_64.manylinux\_2\_17\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L138** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L139** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L140** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L141** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_31\_armv7l.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L142** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L143** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_ppc64le.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L144** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L145** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L146** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L147** — One prebuilt wheel choice: cryptography-50.0.2-cp39-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to cryptography and is data, not VPN logic.
- **L148** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.10 L150–L171 · Locked package — numpy · records 1


```toml
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
    { url = "https://files.pythonhosted.org/packages/77/7f/dd85ce260a669a89be06842cf355d7353a33e6cfbc590fb8ebb947d88dc9/numpy-2.5.4-cp314-cp314-macosx_14_0_x86_64.whl", hash = "sha256:2c2c4afffdeb7920e445028dd71eb932cac3e704792e964bc2a232426d4f1255", size = 6791932, upload-time = "2026-10-10T20:03:44.874Z" },
    { url = "https://files.pythonhosted.org/packages/63/d6/34b0a2b0741386a63025a65a2c09caaaaaad6d0ca95b66cd65c30dd7fcb5/numpy-2.5.4-cp314-cp314-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:4054173604cd8658796053f1f3bc0befb68ec1c0762c57fdad61e199256a8617", size = 15710899, upload-time = "2026-10-10T20:03:46.839Z" },
```

**Line-by-line explanation**

- **L150** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L151** — Name this locked distribution numpy. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L152** — Pin numpy to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L153** — Record the package registry from which numpy is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L154** — Record the source archive for numpy: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L155** — Begin the list of prebuilt wheel artifacts available for numpy across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L156** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_10\_13\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L157** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L158** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L159** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L160** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L161** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L162** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L163** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L164** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L165** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L166** — One prebuilt wheel choice: numpy-2.5.4-cp313-cp313-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L167** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L168** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L169** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L170** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L171** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.


#### 7.15.11 L172–L193 · Locked package — numpy · records 2


```toml
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
```

**Line-by-line explanation**

- **L172** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L173** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L174** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L175** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L176** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L177** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L178** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L179** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L180** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L181** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L182** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L183** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L184** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L185** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L186** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L187** — One prebuilt wheel choice: numpy-2.5.4-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L188** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L189** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L190** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L191** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L192** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L193** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.


#### 7.15.12 L194–L211 · Locked package — numpy · records 3


```toml
    { url = "https://files.pythonhosted.org/packages/7d/5c/b863a2c093c4d6f21a597fcaf24ead0835c09ab16a8312d5a5a8868af683/numpy-2.5.4-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:5ec3753760c1a6d8bb91200666e545c3a9728e6269dfb5d6ce02340996698aa3", size = 17059053, upload-time = "2026-10-10T20:04:44.976Z" },
    { url = "https://files.pythonhosted.org/packages/0a/60/ced4f57f9a1258a0af74f17cb0b0c2700b5c67cd6678823c803b263e4df3/numpy-2.5.4-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:b1185012870173de7ae33d370bd45b1cf5baee747ea4b97036b65f4e93016877", size = 18477406, upload-time = "2026-10-10T20:04:47.863Z" },
    { url = "https://files.pythonhosted.org/packages/f9/bd/0ef22dafaafcc7d4bb3ca26b8d2afbd55dedad8eaba99a8c864e1997456f/numpy-2.5.4-cp315-cp315-win32.whl", hash = "sha256:298eca75243f2cbbfdb460560b9fb2a1792a33cf2ab4286efd43d92e8d3df508", size = 6185133, upload-time = "2026-10-10T20:04:50.467Z" },
    { url = "https://files.pythonhosted.org/packages/50/bc/d2651b155ecc608a77e6f4d15495c11f14f19bb98f8bf0c5b0d38f86dda1/numpy-2.5.4-cp315-cp315-win_amd64.whl", hash = "sha256:332f3378fe077dd850e677ec01bdcc4f22368fb5d50ef10b2c79230b1bf5a592", size = 12703085, upload-time = "2026-10-10T20:04:52.63Z" },
    { url = "https://files.pythonhosted.org/packages/dc/d2/45e404f8abb26fb9eda12b94012936873e827b1be76f2ee7890be128312e/numpy-2.5.4-cp315-cp315-win_arm64.whl", hash = "sha256:d4cccbbc78717966f764cd3af4fb70276fa01fc7a2688af11c78901fa5c04f05", size = 10801451, upload-time = "2026-10-10T20:04:55.677Z" },
    { url = "https://files.pythonhosted.org/packages/c6/c3/2ae14e09cfdb67dc187a342e15308a21c15bf4d2071f8079e6aee5fe56dc/numpy-2.5.4-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:950ea81d57ef070665581b6e1b5f6a029306423cd1739c5b95fe78aa30db6b9d", size = 17097121, upload-time = "2026-10-10T20:04:58.403Z" },
    { url = "https://files.pythonhosted.org/packages/f5/cf/305ae624ef8a039414317224abe9ec9c2fe7ea3c2e1cf204d43ff6b2ffb9/numpy-2.5.4-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:c05ede731b03fb1b7591faca9389ade3267d2bddf1ad8882bb3f2cc5e101694f", size = 12135439, upload-time = "2026-10-10T20:05:01.65Z" },
    { url = "https://files.pythonhosted.org/packages/a9/a8/f75c63813aef95827bb2c0d13b12803016853056e8792c280058cdbfe783/numpy-2.5.4-cp315-cp315t-macosx_14_0_arm64.whl", hash = "sha256:5fbf7141bbfd63aea22f435c9062a032b9ea0082fe9845dad7f021d3f1234e71", size = 5571451, upload-time = "2026-10-10T20:05:04.135Z" },
    { url = "https://files.pythonhosted.org/packages/6f/0f/f17763f983868b5c49b4101ebd7e00760bd1769478a6bb6a8de6e085bbac/numpy-2.5.4-cp315-cp315t-macosx_14_0_x86_64.whl", hash = "sha256:3573cd22564692a5b899ec344e5d5b9cc4576f2985b96f22af3564ed54f2710f", size = 6883356, upload-time = "2026-10-10T20:05:06.249Z" },
    { url = "https://files.pythonhosted.org/packages/67/a7/8af04c5a79e047996cfa38854dcfbececdd0343a7c933a46fdd03ef6f5da/numpy-2.5.4-cp315-cp315t-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6c109eac9cd439193678f69d70733c1108487546ca8eafc107b510ae10c1aecd", size = 15750991, upload-time = "2026-10-10T20:05:08.376Z" },
    { url = "https://files.pythonhosted.org/packages/57/7a/648254290d0c504faa8f2d07aa206660c728802c781a6f3fc68ab7cb5d71/numpy-2.5.4-cp315-cp315t-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:80d6ef6e8620eb2c2b4c4caad50b5935d6db3cde2d51581b55dcc79e14016d1d", size = 16757675, upload-time = "2026-10-10T20:05:11.393Z" },
    { url = "https://files.pythonhosted.org/packages/b8/fe/4a8c3cdb0c70400cfe4c5bec42d3099a5673802a95064614b33e07b82aa1/numpy-2.5.4-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:77045a4b175bbf5316ec08003880804336c78f92281a1b72222b274ea85ec5ac", size = 17113846, upload-time = "2026-10-10T20:05:14.49Z" },
    { url = "https://files.pythonhosted.org/packages/1b/7e/619692bb67778702c0e9eb2d468568a7573f4e269386ea61aed01ee4e557/numpy-2.5.4-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:0f02a46e49cfb6c73bdb7aea1c0d3461dbae9aba613542b65f657cd3d17b9fab", size = 18522915, upload-time = "2026-10-10T20:05:17.33Z" },
    { url = "https://files.pythonhosted.org/packages/b7/b5/4da41c328788f575838f97a098fe8ca691ebc6f6fd73ad4a262ee40b184d/numpy-2.5.4-cp315-cp315t-win32.whl", hash = "sha256:ad62a416ddcf863bf44bba76fbf6b53366ab0692e294f51cae4b5fbe0d246788", size = 6335804, upload-time = "2026-10-10T20:05:19.921Z" },
    { url = "https://files.pythonhosted.org/packages/98/94/6482ddfa3d312490cb9358f375bf2ad56427dbea8769187158e94d653753/numpy-2.5.4-cp315-cp315t-win_amd64.whl", hash = "sha256:38f47be9f74ab870d2633b5456ae519c43758a8d1fd05342f0ce4ecc034396ee", size = 12890095, upload-time = "2026-10-10T20:05:21.875Z" },
    { url = "https://files.pythonhosted.org/packages/48/7f/c2d1b436b6e7cfebac140c2579a298344b85f2991a2ce5c3615cefb29400/numpy-2.5.4-cp315-cp315t-win_arm64.whl", hash = "sha256:7a14a461d9340f1b46b8648578aed9cdb8b3b018a8fac6c1dde2c9192a01a87f", size = 10883718, upload-time = "2026-10-10T20:05:28.547Z" },
]
```

**Line-by-line explanation**

- **L194** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L195** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L196** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L197** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L198** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L199** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L200** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L201** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_14\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L202** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-macosx\_14\_0\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L203** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-manylinux\_2\_27\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L204** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L205** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-musllinux\_1\_2\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L206** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-musllinux\_1\_2\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L207** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win32.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L208** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L209** — One prebuilt wheel choice: numpy-2.5.4-cp315-cp315t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to numpy and is data, not VPN logic.
- **L210** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.13 L212–L220 · Locked package — pycparser


```toml
[[package]]
name = "pycparser"
version = "3.12"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/cb/27/eeb9f307bf07060f3d9f9aa0fb8c15b01bdfded0a941e4b2719c7f94cacd/pycparser-3.12.tar.gz", hash = "sha256:f03387877eab82ce01bbdfd0ba7252ee55a90b1c708d5129e2ce915475cf1db6", size = 158785, upload-time = "2026-10-22T13:40:03.56Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b6/ae/315bbeee126a769cbde43cf4908acb4b40408d8bf8bbf334dd7368d8dadf/pycparser-3.12-py3-none-any.whl", hash = "sha256:a076f3f489b39b43ed13563a1dafe42447445bec2e294154ec5c57fcdda4c85e", size = 62600, upload-time = "2026-10-22T13:40:02.021Z" },
]
```

**Line-by-line explanation**

- **L212** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L213** — Name this locked distribution pycparser. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L214** — Pin pycparser to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L215** — Record the package registry from which pycparser is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L216** — Record the source archive for pycparser: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L217** — Begin the list of prebuilt wheel artifacts available for pycparser across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L218** — One prebuilt wheel choice: pycparser-3.12-py3-none-any.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pycparser and is data, not VPN logic.
- **L219** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.14 L221–L238 · Locked package — pyside6


```toml
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
]
```

**Line-by-line explanation**

- **L221** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L222** — Name this locked distribution pyside6. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L223** — Pin pyside6 to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L224** — Record the package registry from which pyside6 is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L225** — Begin pyside6 dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L226** — Reference the dependency named pyside6-addons. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L227** — Reference the dependency named pyside6-essentials. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L228** — Reference the dependency named pyside6-pdf. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L229** — Reference the dependency named pyside6-webengine. It is needed by pyside6; dependency resolution also follows that package's own dependency references.
- **L230** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L231** — Begin the list of prebuilt wheel artifacts available for pyside6 across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L232** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L233** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L234** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L235** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L236** — One prebuilt wheel choice: pyside6-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6 and is data, not VPN logic.
- **L237** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.15 L239–L253 · Locked package — pyside6-addons


```toml
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
```

**Line-by-line explanation**

- **L239** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L240** — Name this locked distribution pyside6-addons. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L241** — Pin pyside6-addons to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L242** — Record the package registry from which pyside6-addons is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L243** — Begin pyside6-addons dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L244** — Reference the dependency named pyside6-essentials. It is needed by pyside6-addons; dependency resolution also follows that package's own dependency references.
- **L245** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L246** — Begin the list of prebuilt wheel artifacts available for pyside6-addons across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L247** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L248** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L249** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L250** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L251** — One prebuilt wheel choice: pyside6\_addons-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-addons and is data, not VPN logic.
- **L252** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.16 L254–L268 · Locked package — pyside6-essentials


```toml
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

- **L254** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L255** — Name this locked distribution pyside6-essentials. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L256** — Pin pyside6-essentials to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L257** — Record the package registry from which pyside6-essentials is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L258** — Begin pyside6-essentials dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L259** — Reference the dependency named shiboken6. It is needed by pyside6-essentials; dependency resolution also follows that package's own dependency references.
- **L260** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L261** — Begin the list of prebuilt wheel artifacts available for pyside6-essentials across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L262** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L263** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L264** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L265** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L266** — One prebuilt wheel choice: pyside6\_essentials-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-essentials and is data, not VPN logic.
- **L267** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.17 L269–L283 · Locked package — pyside6-pdf


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
```

**Line-by-line explanation**

- **L269** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L270** — Name this locked distribution pyside6-pdf. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L271** — Pin pyside6-pdf to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L272** — Record the package registry from which pyside6-pdf is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L273** — Begin pyside6-pdf dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L274** — Reference the dependency named pyside6-essentials. It is needed by pyside6-pdf; dependency resolution also follows that package's own dependency references.
- **L275** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L276** — Begin the list of prebuilt wheel artifacts available for pyside6-pdf across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L277** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L278** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L279** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L280** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L281** — One prebuilt wheel choice: pyside6\_pdf-6.12.0.140-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-pdf and is data, not VPN logic.
- **L282** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.18 L284–L298 · Locked package — pyside6-webengine


```toml
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
```

**Line-by-line explanation**

- **L284** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L285** — Name this locked distribution pyside6-webengine. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L286** — Pin pyside6-webengine to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L287** — Record the package registry from which pyside6-webengine is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L288** — Begin pyside6-webengine dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L289** — Reference the dependency named pyside6-addons. It is needed by pyside6-webengine; dependency resolution also follows that package's own dependency references.
- **L290** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L291** — Begin the list of prebuilt wheel artifacts available for pyside6-webengine across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L292** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L293** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L294** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L295** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L296** — One prebuilt wheel choice: pyside6\_webengine-6.12.0.140-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to pyside6-webengine and is data, not VPN logic.
- **L297** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.19 L299–L310 · Locked package — shiboken6


```toml
[[package]]
name = "shiboken6"
version = "6.12.0"
source = { registry = "https://pypi.org/simple" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/b5/45/11536fba5f50a57671eb14441c6098096f3e57074e54c9d7d66039a5831e/shiboken6-6.12.0-cp310-abi3-macosx_14_0_universal2.whl", hash = "sha256:47105e05baf57d35453e07d240bbe59cb4b8d9565377ea5134ff9fb37d4f5c02", size = 479653, upload-time = "2026-10-08T09:10:41.506Z" },
    { url = "https://files.pythonhosted.org/packages/49/c2/a04fa003b4360e99d8e3fc2829abacf37396ace63ea1cd616402209ec7c6/shiboken6-6.12.0-cp310-abi3-manylinux_2_34_x86_64.whl", hash = "sha256:3bde565bb0890044b5c7f63808adddede5abc241e9395a2bfed61919884d6240", size = 279268, upload-time = "2026-10-08T09:10:42.982Z" },
    { url = "https://files.pythonhosted.org/packages/97/ca/a4415e6218e0dff764fe2b2d30db2fc8f499a08ace07634232ade3f73adc/shiboken6-6.12.0-cp310-abi3-manylinux_2_39_aarch64.whl", hash = "sha256:ff72a72b3277b418902d562b987b33a6f6818bed9fe40a49d634d09bc67f620e", size = 276562, upload-time = "2026-10-08T09:10:44.25Z" },
    { url = "https://files.pythonhosted.org/packages/2a/b6/bee97e7a2edeab72aafabb46ee5adc939790a638d107860b4cad7a20e407/shiboken6-6.12.0-cp310-abi3-win_amd64.whl", hash = "sha256:a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e", size = 1265476, upload-time = "2026-10-08T09:10:45.627Z" },
    { url = "https://files.pythonhosted.org/packages/8c/d5/5894d35f8a470ca8acff0d1cd8f15b1c94cbfdfe0ce4a6ec0fcf10b95bd1/shiboken6-6.12.0-cp310-abi3-win_arm64.whl", hash = "sha256:da382e68f0815b31b6dc2bce11a465b148c4f42c37b91546a361de1576567d10", size = 1838851, upload-time = "2026-10-08T09:10:47.123Z" },
]
```

**Line-by-line explanation**

- **L299** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L300** — Name this locked distribution shiboken6. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L301** — Pin shiboken6 to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L302** — Record the package registry from which shiboken6 is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L303** — Begin the list of prebuilt wheel artifacts available for shiboken6 across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L304** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-macosx\_14\_0\_universal2.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L305** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-manylinux\_2\_34\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L306** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-manylinux\_2\_39\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L307** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L308** — One prebuilt wheel choice: shiboken6-6.12.0-cp310-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to shiboken6 and is data, not VPN logic.
- **L309** — Close the wheels TOML array. The bracket is structure, not a command.


#### 7.15.20 L311–L331 · Locked package — tifrvpn-tui


```toml
[[package]]
name = "tifrvpn-tui"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "argparse" },
    { name = "cryptography" },
    { name = "numpy" },
    { name = "pyside6" },
    { name = "zxing-cpp" },
]

[package.metadata]
requires-dist = [
    { name = "argparse", specifier = ">=1.4.0" },
    { name = "cryptography", specifier = ">=50.0.2" },
    { name = "numpy", specifier = ">=2.5.4" },
    { name = "pyside6", specifier = ">=6.12.0" },
    { name = "zxing-cpp", specifier = ">=3.1.1" },
]
```

**Line-by-line explanation**

- **L311** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L312** — Name this locked distribution tifrvpn-tui. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L313** — Pin tifrvpn-tui to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L314** — Use the current local project directory as an editable package source. Changes to that package source can be reflected without building a separate installed copy; this does not update the five scripts copied by install.sh.
- **L315** — Begin tifrvpn-tui dependency references: packages this package itself needs. Some are indirect/transitive dependencies you did not explicitly list in pyproject.toml.
- **L316** — Reference the dependency named argparse. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L317** — Reference the dependency named cryptography. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L318** — Reference the dependency named numpy. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L319** — Reference the dependency named pyside6. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L320** — Reference the dependency named zxing-cpp. It is needed by tifrvpn-tui; dependency resolution also follows that package's own dependency references.
- **L321** — Close the dependencies TOML array. The bracket is structure, not a command.
- **L323** — Open additional metadata for the preceding local project package, including its originally declared dependency constraints.
- **L324** — Begin the local project's declared dependency requirements, retaining the minimum-version constraints from its metadata.
- **L325** — Reference the dependency named argparse. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L326** — Reference the dependency named cryptography. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L327** — Reference the dependency named numpy. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L328** — Reference the dependency named pyside6. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L329** — Reference the dependency named zxing-cpp. specifier records the required version range, whereas that dependency's own package record gives its exact locked version.
- **L330** — Close the requires-dist TOML array. The bracket is structure, not a command.


#### 7.15.21 L332–L353 · Locked package — zxing-cpp · records 1


```toml
[[package]]
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
```

**Line-by-line explanation**

- **L332** — Start another package record in the TOML array of packages. Each record will name one exact resolved distribution and its source/dependencies/artifacts.
- **L333** — Name this locked distribution zxing-cpp. Names identify packages to install; they are not necessarily identical to Python import names (for example pyside6 is imported as PySide6).
- **L334** — Pin zxing-cpp to this exact release version. A lock chooses one version within the declared constraints; it does not mean this is the newest release available.
- **L335** — Record the package registry from which zxing-cpp is resolved. The https://pypi.org/simple address is package-index metadata, not the TIFR VPN server.
- **L336** — Record the source archive for zxing-cpp: URL gives its location, hash gives the expected SHA-256 bytes fingerprint, size is the archive size in bytes, and upload-time is registry metadata. A source archive may need building if used; this record does not itself download it.
- **L337** — Begin the list of prebuilt wheel artifacts available for zxing-cpp across supported Python/platform combinations. The installer selects an applicable artifact; it does not install every wheel listed.
- **L338** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-macosx\_10\_13\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L339** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L340** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L341** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L342** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L343** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp312-abi3-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L344** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L345** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L346** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L347** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L348** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L349** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp313-cp313t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L350** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-macosx\_10\_15\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L351** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-macosx\_11\_0\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L352** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-manylinux\_2\_26\_aarch64.manylinux\_2\_28\_aarch64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L353** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-manylinux\_2\_27\_x86\_64.manylinux\_2\_28\_x86\_64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.


#### 7.15.22 L354–L356 · Locked package — zxing-cpp · records 2


```toml
    { url = "https://files.pythonhosted.org/packages/c8/8e/8dbf8fcf4d466c7d9b5023ae4cf17da22f328efabd4d7107109ac7737155/zxing_cpp-3.1.1-cp314-cp314t-win_amd64.whl", hash = "sha256:fe8172f3c9b17f8fd40fba2ae0ba9728228caeff3587eabf5d99888891d02e62", size = 1032030, upload-time = "2026-07-29T08:50:56.169Z" },
    { url = "https://files.pythonhosted.org/packages/47/38/e547ea4f9a7c8c24a1d3a59869540029e4bad467f9544084c3cee94eb6e0/zxing_cpp-3.1.1-cp314-cp314t-win_arm64.whl", hash = "sha256:1992231c161c3eaf5857f7bc35193b8ca621eba0debc51e752403657b88d542a", size = 956213, upload-time = "2026-07-29T08:50:57.524Z" },
]
```

**Line-by-line explanation**

- **L354** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-win\_amd64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L355** — One prebuilt wheel choice: zxing\_cpp-3.1.1-cp314-cp314t-win\_arm64.whl. The filename includes distribution/release, Python compatibility, ABI compatibility and platform tags. Common tags: cp313 means CPython 3.13; abi3 is a stable-ABI wheel; none-any means pure-Python/platform-independent; x86\_64 and aarch64/arm64 distinguish CPU architectures; win, macosx and manylinux distinguish platform families. url locates this exact file, hash is its expected SHA-256 fingerprint, size counts bytes, and upload-time records publication metadata. This entry belongs to zxing-cpp and is data, not VPN logic.
- **L356** — Close the wheels TOML array. The bracket is structure, not a command.


[[#File index|↑ File index]]

### 7.16 LICENSE

**21 lines** · Included license text and unfilled copyright placeholders.


This is the repository's declared MIT license text. It is not executable code and is not involved in connecting the VPN. The annotations identify the text's sections rather than offering a legal assessment. The copyright line still contains literal [year] and [fullname] placeholders.

**Read the source by function or step.** Each subsection contains the original code and its associated explanations.


#### 7.16.1 L1–L4 · License name and copyright template


```text
MIT License

Copyright (c) [year] [fullname]
```

**Line-by-line explanation**

- **L1** — Name of the license text included in the repository.
- **L3** — Copyright notice line. \[year\] and \[fullname\] are unfilled template placeholders in the actual source, not values automatically substituted by Git or Python.


#### 7.16.2 L5–L11 · Permission paragraph


```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

**Line-by-line explanation**

- **L5–L10** — A physical line in the permission paragraph. Taken together, this paragraph lists permissions to use, copy, change and distribute the software, subject to the following condition. The line wrapping is for readability, not distinct program instructions.


#### 7.16.3 L12–L14 · Notice-retention condition


```text
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**Line-by-line explanation**

- **L12–L13** — A physical line in the condition paragraph requiring retention of the copyright and permission notice in the described copies/portions. Read the actual license text for its complete wording.


#### 7.16.4 L15–L21 · Warranty and liability paragraph


```text
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Line-by-line explanation**

- **L15–L21** — A physical line in the all-capital warranty/liability paragraph. These are words in the license document, not settings that affect runtime error handling or network security.


[[#File index|↑ File index]]

## 8 Learning checkpoints


### 8.1 A gentle study plan

- [ ] Explain what the terminal, shell, process and subprocess do.
- [ ] Explain the difference between a source checkout and installed script copies.
- [ ] Trace `tifrvpn -c` from line 169 into the dispatcher and connection function.
- [ ] Read `$@`, `$?`, `$(...)`, `||`, `[[...]]` and `((...))` aloud in plain language.
- [ ] Identify the TIFR password, vault master password, TOTP seed, session cookie and possible GPG passphrase.
- [ ] Follow `configuration()` → `decrypt_password()` → `read_login()` / `read_code()`.
- [ ] Explain why the master password goes through stdin and results are captured.
- [ ] Read the authentication `main()` before studying the individual browser callbacks.
- [ ] Describe why a DSID cookie is probed before it is accepted.
- [ ] Explain the difference between a callback, an event loop and a subprocess.
- [ ] Explain where the quiet-mode timer starts and which operations are outside it.
- [ ] Explain why the QR export seed is different from one currently displayed code.
- [ ] Understand what mocks verify and what the offline tests do not verify.
- [ ] Distinguish `pyproject.toml` version requirements from `uv.lock` exact versions.


### 8.2 Check your understanding

**Why can reconnecting avoid a browser?** A saved DSID may still grant portal access; the controller tests it before starting a fresh sign-in.

**Does `--quiet` remove the graphical browser?** It runs the same graphical browser on a private Xvfb display. Its terminal diagnostics remain visible.

**Does `tifrvpn --setup` encrypt the database password?** It prepares a NetworkManager profile. `tifr-otp --setup` prepares encrypted access to the vault master password.

**Does committing a change update `~/bin/tifr`?** The installed helpers are copies. Reinstallation is a separate copy/update step.

**Why can the phone and KeePassXC show matching codes?** They share the enrollment seed and compatible settings/time; neither needs to fetch each code from a server.

**Does `src/tifrvpn_tui` contain the current VPN implementation?** Its `main()` currently prints a greeting. The working commands are the root-level Zsh and Python files.


### 8.3 Safe source-reading exercises

These commands inspect the checkout or run its existing offline tests. Run them from the repository directory.

```sh
# Show source with original line numbers.
nl -ba tifrvpn

# Read the connect function only.
sed -n '58,77p' tifrvpn

# Inspect your uncommitted changes and recent history.
git diff
git log -3 --oneline

# Run the repository's existing offline checks.
python3 -B -m unittest discover -s tests -v
```

At the recorded snapshot, all **16 offline tests passed**. They use invented credentials and temporary directories; they do not perform a real TIFR login or prove every live GUI/server behavior.

## 9 References

The repository source is the evidence for this project's behavior. These official references explain the underlying tools and algorithms:

- [Zsh expansion documentation](https://zsh.sourceforge.io/Doc/Release/Expansion.html) explains the path modifiers used to find the adjacent helper.
- [Python subprocess documentation](https://docs.python.org/3.13/library/subprocess.html) explains child processes, captured streams, timeouts and inherited file descriptors.
- [Python's os.memfd_create documentation](https://docs.python.org/3.13/library/os.html#os.memfd_create) describes the anonymous file API used for transient tunnel secrets.
- [Python argparse documentation](https://docs.python.org/3.13/library/argparse.html) explains the standard-library command-line parser.
- [RFC 6238](https://www.rfc-editor.org/rfc/rfc6238) specifies TOTP and includes the known-answer example exercised by this repository's test.
- [NetworkManager secret flags](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-keyfile.html) documents the not-saved flag value 2.
- [WebKit JavaScript evaluation API](https://webkitgtk.org/reference/webkit2gtk/stable/method.WebView.evaluate_javascript.html) explains the asynchronous browser operation used by the form callbacks.
- [GnuPG agent options](https://www.gnupg.org/documentation/manuals/gnupg/Agent-OPTION.html) describes pinentry modes relevant to avoiding hidden prompts.


**Obsidian formatting references:** [Heading folding](https://obsidian.md/help/folding) · [Internal links and headings](https://obsidian.md/help/links) · [Properties](https://obsidian.md/help/properties).


### 9.1 Snapshot and completeness

This note was converted from the complete HTML source guide. All 16 source files and 2,064 lines are embedded. Repeated identical adjacent explanations are combined under their line range, and blank lines retain their original spacing in code. All substantive original explanation text remains included.

The inspection found a README reference to a missing `config.example.json`, an unused placeholder package command and unfilled license copyright placeholders. Those are documented observations, not changes made to your project. Findings describe the recorded revision and can become outdated when the source changes.

[[#TIFR VPN — Complete Code Guide|↑ Back to the beginning]]

**Current implementation:** [[TIFR Vpn TUI Package|Open the package guide]].
