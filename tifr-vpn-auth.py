#!/usr/bin/env python3
"""Sign in to TIFR SSO, then hand an in-memory session to NetworkManager."""

import base64
import hashlib
import json
import os
import runpy
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


def login_cookie():
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

    def fill_ready(source, result):
        autofill["busy"] = False
        try:
            source.evaluate_javascript_finish(result)
        except Exception:
            # Navigation can destroy the previous page's JS context.
            pass

    def form_ready(source, result):
        try:
            state = json.loads(source.evaluate_javascript_finish(result).to_string())
            if state.get("error"):
                autofill["stopped"] = True
                print("tifr VPN: SSO reported an error; autofill stopped. Check the sign-in window and saved credentials.", file=sys.stderr)
                return
            step = state.get("step")
            if not step or step in autofill["submitted"]:
                return
            if autofill["provider"] is None:
                helper = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tifr-otp.py"))
                database, password_file, entry = helper["configuration"]()
                master = helper["decrypt_password"](password_file)
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
        except RuntimeError as error:
            session["error"] = str(error)
            Gtk.main_quit()
        except Exception:
            autofill["stopped"] = True
            print("tifr VPN: automatic sign-in could not continue; check the sign-in window.", file=sys.stderr)
        finally:
            autofill["busy"] = False

    def autofill_tick():
        page = urlsplit(view.get_uri() or "")
        if (not autofill["busy"] and not autofill["stopped"] and not view.is_loading()
                and page.scheme == "https" and page.hostname == "sso.tifr.res.in"
                and page.port in (None, 443) and page.path.startswith("/realms/TIFRSSO2/")):
            autofill["busy"] = True
            view.evaluate_javascript(signin_script(), -1, None, None, None, form_ready)
        return True

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

    def check_cookies(*_args):
        page = urlsplit(view.get_uri() or "")
        # A DSID may exist before the concurrent-session confirmation finishes;
        # cookies_ready checks portal access before accepting it.
        if (not view.is_loading() and page.hostname == HOST
                and not session["busy"] and not session["cookie"]):
            session["busy"] = True
            manager.get_cookies("https://" + HOST + "/dana/home/index.cgi", None, cookies_ready)

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
        except Exception:
            pass
        pending["count"] -= 1
        if not pending["count"]:
            load_page()

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


def authenticate():
    # Isolate WebKit from the tunnel controller, including its native shutdown.
    result = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--sso-window"],
        stdout=subprocess.PIPE, text=True,
    )
    if result.returncode:
        raise RuntimeError("SSO sign-in did not complete; no tunnel was started.")
    cookie = result.stdout.strip()
    if not cookie.startswith("DSID=") or any(char in cookie for char in "\r\n\0"):
        raise RuntimeError("Invalid SSO session; no tunnel was started.")
    return cookie


def sso_window_process():
    code = 1
    try:
        cookie = login_cookie()
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


def main():
    if sys.argv[1:] == ["--forget-login"]:
        cleared = [saved_login("session", forget=True), saved_login("browser", forget=True)]
        if any(result is None for result in cleared):
            print("tifr VPN: could not clear all saved sign-in state.", file=sys.stderr)
            return 1
        print("tifr VPN: saved sign-in state cleared; an active tunnel is unaffected.")
        return 0
    if len(sys.argv) != 2:
        print("Usage: tifr-vpn-auth.py NETWORKMANAGER_PROFILE_UUID", file=sys.stderr)
        return 2
    uuid = sys.argv[1]
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
    cookie = saved_login("session")
    if cookie and valid_session(cookie):
        print("tifr VPN: reusing saved session", flush=True)
        return activate(uuid, cookie)
    if cookie:
        saved_login("session", forget=True)
        print("tifr VPN: saved session expired; TIFR requires sign-in again.", flush=True)
    cookie = authenticate()
    saved_login("session", cookie)
    return activate(uuid, cookie)


if __name__ == "__main__":
    if sys.argv[1:] == ["--sso-window"]:
        sso_window_process()
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
