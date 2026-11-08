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
        + ")"
    )


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

    def fill_ready(source, result):
        autofill["busy"] = False
        try:
            source.evaluate_javascript_finish(result)
        except Exception:  # noqa: BLE001, S110 - Navigation can invalidate the JavaScript context.
            # Navigation can destroy the previous page's JS context.
            pass

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

    def tls_error(_view, _uri, _certificate, _errors):
        session["error"] = "SSO certificate verification failed. Contact TIFR IT."
        Gtk.main_quit()
        return False

    def close(*_args):
        Gtk.main_quit()
        return False

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
