"""End-to-end check of the OIDC silent-auth path in a real browser, under the
exact CSP EDA sets. Stands up a mock Keycloak (authorize -> 302 to callback,
token endpoint) and a mock EQL endpoint that rejects unauthenticated calls the
way EDA does (HTTP 400 InvalidAuthHeader, not 401)."""
import http.server, socketserver, threading, functools, pathlib, json, base64, urllib.parse, sys
from playwright.sync_api import sync_playwright

CSP = "default-src 'self'; frame-ancestors 'self'; form-action 'self';"
REALM = "/core/proxy/v1/identity/realms/eda/protocol/openid-connect"

def b64u(o):
    return base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip("=")

TOKEN = b64u({"alg":"RS256"}) + "." + b64u({"preferred_username":"admin","sub":"u1"}) + ".sig"

# Mirrors the real lab: two namespaces, with leaf1 present in BOTH. The arena
# must come from exactly one of them.
NODES = [{".namespace.name":"eda","name":"leaf1","operating-system":"srlinux","status":"Connected"},
         {".namespace.name":"eda","name":"leaf2","operating-system":"srlinux","status":"Connected"},
         {".namespace.name":"eda","name":"spine1","operating-system":"srlinux","status":"Connected"},
         {".namespace.name":"eda-telemetry","name":"leaf1","operating-system":"srlinux","status":"Connected"}]
IFS   = [{".namespace.name":"eda",".namespace.node.name":"leaf1","name":"ethernet-1/1","admin-state":"enable","oper-state":"up"},
         {".namespace.name":"eda",".namespace.node.name":"leaf2","name":"ethernet-1/1","admin-state":"enable","oper-state":"down",
          "oper-down-reason":"port-down"},
         {".namespace.name":"eda-telemetry",".namespace.node.name":"leaf1","name":"ethernet-1/9","admin-state":"enable","oper-state":"up"}]

seen = {"authorize":0, "token":0, "query_noauth":0, "query_auth":0}

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()
    def log_message(self, *a): pass

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == REALM + "/auth":
            seen["authorize"] += 1
            # Keycloak with an existing session + prompt=none: straight redirect back
            target = q["redirect_uri"][0] + "?code=TESTCODE&state=" + q["state"][0]
            self.send_response(302); self.send_header("Location", target)
            self.send_header("Content-Length","0"); self.end_headers()
            return
        if u.path == "/core/query/v1":
            if not self.headers.get("Authorization"):
                seen["query_noauth"] += 1
                return self._json({"type":"InvalidAuthHeader","message":"Invalid authorization header.",
                                   "causeSimple":"no token present in request"}, 400)
            if "query" not in q:
                return self._json({"type":"QueryNotSpecified",
                                   "message":"Unable to run query. Query string not specified."}, 404)
            seen["query_auth"] += 1
            eql = q.get("query",[""])[0]
            return self._json({"data": IFS if "interface" in eql else NODES})
        return super().do_GET()

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == REALM + "/token":
            seen["token"] += 1
            n = int(self.headers.get("Content-Length","0"))
            form = urllib.parse.parse_qs(self.rfile.read(n).decode())
            # PKCE + client identity must be present and correct
            assert form["grant_type"][0] == "authorization_code", form
            assert form["client_id"][0] == "auth", form
            assert form["code"][0] == "TESTCODE", form
            assert "code_verifier" in form, form
            return self._json({"access_token":TOKEN,"expires_in":300,"token_type":"Bearer"})
        self.send_response(404); self.send_header("Content-Length","0"); self.end_headers()

d = str(pathlib.Path('split').resolve())
Handler = functools.partial(H, directory=d)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8098), Handler) as httpd:
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    violations, errors = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = b.new_page(viewport={"width":1100,"height":860})
        pg.on("console", lambda m: violations.append(m.text)
              if ("Content Security Policy" in m.text or "Refused" in m.text) else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://127.0.0.1:8098/", wait_until="networkidle")
        pg.wait_for_timeout(2500)
        res = pg.evaluate("""() => ({
            online:   EDA.online,
            hasToken: !!EDA.token,
            user:     EDA.user.name,
            endpoint: EDA.user.endpoint,
            nodes:    EDA.fabric ? EDA.fabric.nodes.length : 0,
            ns:       EDA.namespace,
            allNs:    EDA.namespaces,
            ports:    EDA.fabric ? EDA.fabric.links.map(l=>l.node+":"+l.id) : [],
            links:    EDA.fabric ? EDA.fabric.links.length : 0,
            authErr:  Auth.error,
            lastErr:  EDA.lastError,
            badge:    (document.querySelector('#srcTag')||{}).textContent,
            frames:   document.querySelectorAll('iframe').length
        })""")
        pg.screenshot(path="csp_auth_menu.png")
        b.close()
    httpd.shutdown()

print(json.dumps(res, indent=2))
print("server saw:", seen)
print("CSP violations:", len(violations));  [print("   ", v[:140]) for v in violations[:6]]
print("page errors:   ", len(errors));      [print("   ", e[:200]) for e in errors[:6]]

fail = []
if not res["online"]:                      fail.append("not online")
if not res["hasToken"]:                    fail.append("no token")
if res["user"] != "admin":                 fail.append("username not from claims: %r" % res["user"])
if res["nodes"] != 3:                      fail.append("fabric nodes != 3 (namespace not scoped?)")
if res["ns"] != "eda":                     fail.append("wrong namespace: %r" % res["ns"])
if sorted(res["allNs"]) != ["eda","eda-telemetry"]: fail.append("namespaces not recorded: %r" % res["allNs"])
if any(":ethernet-1/9" in p for p in res["ports"]): fail.append("link bled in from the other namespace")
if "eda" not in (res["badge"] or ""):      fail.append("badge does not name the namespace: %r" % res["badge"])
if seen["authorize"] != 1:                 fail.append("authorize calls = %d" % seen["authorize"])
if seen["token"] != 1:                     fail.append("token calls = %d" % seen["token"])
if seen["query_auth"] < 1:                 fail.append("no authenticated query")
if violations:                             fail.append("%d CSP violations" % len(violations))
if errors:                                 fail.append("%d page errors" % len(errors))
if res["frames"] != 0:                     fail.append("auth iframe left in the DOM")
print("\nRESULT:", "FAIL -> " + "; ".join(fail) if fail else "PASS")
sys.exit(1 if fail else 0)
