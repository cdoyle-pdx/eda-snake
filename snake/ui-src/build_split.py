"""Split the single-file game into index.html + snake.css + snake.js.

EDA's proxy sets `default-src 'self'` with no unsafe-inline, so inline <style>
and <script> are blocked. Same-origin external files satisfy the policy.
The single file remains the authoring source; this generates the deployable form.
"""
import re, pathlib, sys

src = pathlib.Path('nokia-snake-eda.html').read_text()
out = pathlib.Path('split'); out.mkdir(exist_ok=True)

style = re.search(r'<style>(.*?)</style>', src, re.S)
script = re.search(r'<script>(.*?)</script>', src, re.S)
if not style or not script:
    sys.exit("could not find the inline style/script blocks")

(out / 'snake.css').write_text(style.group(1).strip() + '\n')
(out / 'snake.js').write_text(script.group(1).strip() + '\n')

html = src.replace(style.group(0), '<link rel="stylesheet" href="snake.css">')
html = html.replace(script.group(0), '<script src="snake.js"></script>')
(out / 'index.html').write_text(html)

assert '<style>' not in html and '<script>' not in html.replace('<script src=', '')
print("index.html  %6d bytes" % len((out/'index.html').read_text()))
print("snake.css   %6d bytes" % len((out/'snake.css').read_text()))
print("snake.js    %6d bytes" % len((out/'snake.js').read_text()))

# --- OIDC callback page -------------------------------------------------
# Loaded only inside the hidden auth iframe. It reads the authorization code
# off the query string and posts it to the opener. Kept as its own two files
# because the same CSP (default-src 'self', no unsafe-inline) applies here.
CALLBACK_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<title>Snake - authentication</title>
</head>
<body>
<script src="callback.js"></script>
</body>
</html>
"""

CALLBACK_JS = """/* Runs inside the hidden iframe created by Auth.codeFromHiddenFrame().
   Keycloak redirects here with ?code=...&state=... on success, or
   ?error=login_required&state=... when prompt=none cannot be satisfied.
   Either way we hand the result to the parent and do nothing else. */
(function(){
  var q = new URLSearchParams(location.search);
  var code  = q.get("code");
  var state = q.get("state");
  var error = q.get("error");
  if(!code && !error) error = "callback reached with no code";
  var target = window.parent && window.parent !== window ? window.parent : window.opener;
  if(!target) return;
  try{
    target.postMessage({ type:"eda-snake-auth", state:state, code:code, error:error },
                       location.origin);
  }catch(e){ /* nothing useful to do here */ }
})();
"""

(out / 'callback.html').write_text(CALLBACK_HTML)
(out / 'callback.js').write_text(CALLBACK_JS)
print("callback.html %6d bytes" % len((out/'callback.html').read_text()))
print("callback.js   %6d bytes" % len((out/'callback.js').read_text()))
