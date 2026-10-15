"""Serve the split build with the exact CSP EDA uses, and verify the game runs."""
import http.server, socketserver, threading, functools, pathlib
from playwright.sync_api import sync_playwright

CSP = "default-src 'self'; frame-ancestors 'self'; form-action 'self';"

class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        super().end_headers()
    def log_message(self, *a): pass

d = str(pathlib.Path('split').resolve())
Handler = functools.partial(H, directory=d)
with socketserver.TCPServer(("127.0.0.1", 8099), Handler) as httpd:
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    errors, violations = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = b.new_page(viewport={"width":1100,"height":860})
        pg.on("console", lambda m: (violations.append(m.text)
               if "Content Security Policy" in m.text or "Refused" in m.text else None))
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://127.0.0.1:8099/", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        # did the JS actually run?
        ok_js = pg.evaluate("typeof G !== 'undefined' && G.state === 'menu'")
        letters = pg.inner_text("#lettersV")
        styled = pg.evaluate("getComputedStyle(document.querySelector('#stage')).position")
        cols = pg.evaluate("G.cols")
        pg.screenshot(path="csp_menu.png")
        pg.evaluate("G.diff='hez'; renderDiffSel();"); pg.wait_for_timeout(250)
        pg.screenshot(path="csp_menu_hez.png")
        b.close()
    httpd.shutdown()

print("JS executed:        ", ok_js)
print("letters HUD:        ", letters, "(JS-updated value, markup says 0/15)")
print("CSS applied:        ", styled, "(stage position, from snake.css)")
print("menu arena cols:    ", cols)
print("CSP violations:     ", len(violations))
for v in violations[:5]: print("   ", v[:120])
print("page errors:        ", len(errors))
for e in errors[:5]: print("   ", e[:160])
