"""Private subprocess entry point; never exits a process merely on import."""

import argparse
import json
import os
import sys


def sso_window_process(*, quiet=False):
    from .config import Config
    from .gui.sso import login_cookie

    raw = os.environ.get("_TIFR_WORKER_CONFIG")
    config = Config(**json.loads(raw)) if raw is not None else None
    _run(login_cookie, quiet=quiet, config=config)


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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    sso_window_process(quiet=args.quiet)


if __name__ == "__main__":
    main()
