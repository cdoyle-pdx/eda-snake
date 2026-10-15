/* Tests for the OIDC silent-auth path.
   Mocks Keycloak as a hidden iframe that redirects to callback.html, plus the
   token endpoint. Verifies PKCE correctness, every failure mode degrades to
   standalone, and that a token actually reaches the API calls. */
const fs = require('fs');
const { webcrypto } = require('crypto');

const ORIGIN = "https://192.168.0.50:9443";
const PAGE   = ORIGIN + "/core/httpproxy/v1/snake/";

let issues = [];
const ok = (c, m) => { if(!c){ issues.push(m); console.log("FAIL:", m); } else console.log("ok:", m); };

// ---- browser-ish globals -------------------------------------------------
globalThis.crypto = webcrypto;
globalThis.btoa = (s) => Buffer.from(s, 'binary').toString('base64');
globalThis.atob = (s) => Buffer.from(s, 'base64').toString('binary');
globalThis.location = { href: PAGE, origin: ORIGIN };

const mk = () => new Proxy({}, { get:(t,p)=>{ if(p in t) return t[p]; if(p==='canvas') return {}; return ()=>{}; },
                                 set:(t,p,v)=>{t[p]=v;return true;} });

let messageListeners = [];
globalThis.window = {
  devicePixelRatio: 1,
  addEventListener(ev, fn){ if(ev === "message") messageListeners.push(fn); },
  removeEventListener(ev, fn){ if(ev === "message") messageListeners = messageListeners.filter(f => f !== fn); },
  localStorage: { _d:{}, getItem(k){ return this._d[k] || null; }, setItem(k,v){ this._d[k]=v; } },
};
globalThis.addEventListener    = window.addEventListener;
globalThis.removeEventListener = window.removeEventListener;

// Keycloak stand-in. Behaviour is swapped per test via KC.
let KC = {};
const appendedFrames = [];

function makeIframe(){
  const frame = {
    style:{}, setAttribute(){}, remove(){},
    _src: null,
    get src(){ return this._src; },
    set src(v){
      this._src = v;
      appendedFrames.push(v);
      // Simulate the browser loading the authorize URL and Keycloak
      // redirecting to callback.html, which posts back to the parent.
      setTimeout(() => {
        const u = new URL(v, ORIGIN);
        const q = u.searchParams;
        const reply = KC.respond ? KC.respond(q) : null;
        if(reply === null) return;              // silence: exercises the timeout
        for(const fn of messageListeners.slice()){
          fn({ origin: reply.origin !== undefined ? reply.origin : ORIGIN,
               data:   reply.data });
        }
      }, 1);
    },
  };
  return frame;
}

const made = {};
const el = (id) => {
  if(!made[id]) made[id] = { style:{setProperty(){}}, classList:{add(){},remove(){},toggle(){}},
    textContent:'', innerHTML:'', appendChild(){}, onclick:null, getContext:mk,
    width:0, height:0, addEventListener(){} };
  return made[id];
};
globalThis.document = {
  getElementById: el,
  createElement: (tag) => tag === "iframe" ? makeIframe() : el("tmp"),
  documentElement: { style:{setProperty(){}} },
  body: { style:{}, classList:{add(){},remove(){},toggle(){}}, appendChild(){} },
};
globalThis.navigator = { getGamepads: () => [] };
globalThis.requestAnimationFrame = () => {};
globalThis.console.info = () => {};
globalThis.fetch = async () => { throw new Error("offline"); };

(0, eval)(fs.readFileSync('eda_globals.js', 'utf8'));
OIDC.timeoutMs = 120;   // keep the suite fast

// ---- fixtures ------------------------------------------------------------
const NODES = [{name:"leaf1","operating-system":"srlinux",status:"Connected"},
               {name:"leaf2","operating-system":"srlinux",status:"Connected"},
               {name:"spine1","operating-system":"srlinux",status:"Connected"}];
const IFS   = [{".namespace.node.name":"leaf1",name:"ethernet-1/1","admin-state":"enable","oper-state":"up"}];

function jwt(claims){
  const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64')
                     .replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  return b64({alg:"RS256",typ:"JWT"}) + "." + b64(claims) + ".sig";
}

let tokenCalls = [];
function apiFetch({ tokenStatus = 200, claims = {preferred_username:"admin"}, expiresIn = 300 } = {}){
  return async (url, opts) => {
    const u = decodeURIComponent(String(url));
    const j = (o) => ({ ok:true, status:200, json: async () => o });

    if(u.includes("/protocol/openid-connect/token")){
      tokenCalls.push(Object.fromEntries(new URLSearchParams(opts.body)));
      if(tokenStatus !== 200) return { ok:false, status: tokenStatus };
      return j({ access_token: jwt(claims), expires_in: expiresIn, token_type:"Bearer" });
    }
    if(/query/.test(u)){
      const auth = opts && opts.headers && opts.headers["Authorization"];
      if(!auth) return { ok:false, status:400 };      // EDA's real behaviour
      if(/interface/.test(u)) return j(IFS);
      return j(NODES);
    }
    if(/snakeleaderboard|snakescores/.test(u)) return j({items:[]});
    throw new Error("unexpected " + u);
  };
}
const wrap = (f) => async (url, opts) => {
  const r = await f(url, opts);
  if(!r.ok) throw new Error(url + " -> " + r.status);
  return r;
};
// EDA.api throws on !ok; the token POST checks r.ok itself, so it must not be wrapped
const route = (f) => async (url, opts) => {
  const r = await f(url, opts);
  if(String(url).includes("/openid-connect/token")) return r;
  if(!r.ok) throw new Error(url + " -> " + r.status);
  return r;
};

function reset(){
  Auth.token = null; Auth.claims = null; Auth.error = null; Auth.attempted = false;
  clearTimeout(Auth.renewTimer); Auth.renewTimer = null;
  EDA.token = null; EDA.online = false; EDA.fabric = null; EDA.lastError = null;
  EDA.user = { name:"", endpoint:null, canReset:true, canPlay:true };
  tokenCalls = []; appendedFrames.length = 0; messageListeners = [];
}

const sha = async (v) => {
  const h = await webcrypto.subtle.digest("SHA-256", new TextEncoder().encode(v));
  return Buffer.from(h).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
};

(async () => {

// --- 1. happy path --------------------------------------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"AUTH_CODE_1" } }) };
globalThis.fetch = route(apiFetch());
await EDA.connect();
ok(EDA.online === true,                      "silent auth -> online");
ok(!!EDA.token,                              "token stored on EDA");
ok(EDA.fabric && EDA.fabric.nodes.length===3,"fabric read with the token");
ok(EDA.user.name === "admin",                "username from token claims: " + EDA.user.name);
ok(EDA.user.endpoint === "oidc:access_token","identity source recorded");

// --- 2. PKCE is correct ---------------------------------------------------
const authUrl = new URL(appendedFrames[0], ORIGIN);
const sent = authUrl.searchParams;
ok(sent.get("client_id") === "auth",             "client_id is the EDA UI client");
ok(sent.get("prompt") === "none",                "prompt=none (no visible login)");
ok(sent.get("response_type") === "code",         "authorization code flow");
ok(sent.get("code_challenge_method") === "S256", "PKCE S256");
ok(sent.get("redirect_uri") === PAGE + "callback.html",
   "redirect_uri derived from page location: " + sent.get("redirect_uri"));
ok(tokenCalls.length === 1,                      "exactly one token exchange");
const tc = tokenCalls[0];
ok(tc.grant_type === "authorization_code",       "grant_type correct");
ok(tc.code === "AUTH_CODE_1",                    "code forwarded to token endpoint");
ok(tc.redirect_uri === sent.get("redirect_uri"), "redirect_uri matches between legs");
ok(await sha(tc.code_verifier) === sent.get("code_challenge"),
   "code_challenge is S256(code_verifier) - PKCE actually valid");

// --- 3. API calls carry the bearer header --------------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" } }) };
let sawAuthHeader = false;
globalThis.fetch = route(async (url, opts) => {
  if(String(url).includes("/query/")) sawAuthHeader = !!(opts.headers && opts.headers["Authorization"]);
  return apiFetch()(url, opts);
});
await EDA.connect();
ok(sawAuthHeader, "Authorization: Bearer sent on EQL queries");

// --- 4. prompt=none rejected (no Keycloak session) ------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), error:"login_required" } }) };
globalThis.fetch = route(apiFetch());
await EDA.connect();
ok(EDA.online === false,                   "login_required -> standalone, not a crash");
ok(/no token/.test(EDA.lastError || ""),   "lastError names the cause: " + EDA.lastError);
ok(/login_required/.test(Auth.error || ""),"Auth.error keeps the OIDC reason");
ok(tokenCalls.length === 0,                "no token exchange attempted after a failed authorize");

// --- 5. iframe never answers (timeout) -----------------------------------
reset();
KC = { respond: () => null };
globalThis.fetch = route(apiFetch());
const t0 = Date.now();
await EDA.connect();
const elapsed = Date.now() - t0;
ok(EDA.online === false,          "timeout -> standalone");
ok(/timed out/.test(Auth.error||""), "timeout recorded: " + Auth.error);
ok(elapsed < 1000,                "gave up promptly (" + elapsed + "ms), no indefinite hang");

// --- 6. state mismatch is ignored (CSRF guard) ---------------------------
reset();
KC = { respond: () => ({ data:{ type:"eda-snake-auth", state:"ATTACKER", code:"EVIL" } }) };
globalThis.fetch = route(apiFetch());
await EDA.connect();
ok(EDA.online === false,     "mismatched state rejected");
ok(tokenCalls.length === 0,  "no exchange on a forged state");

// --- 7. message from a foreign origin is ignored -------------------------
reset();
KC = { respond: (q) => ({ origin:"https://evil.example", data:{ type:"eda-snake-auth", state:q.get("state"), code:"EVIL" } }) };
globalThis.fetch = route(apiFetch());
await EDA.connect();
ok(EDA.online === false,    "cross-origin postMessage ignored");
ok(tokenCalls.length === 0, "no exchange from a foreign origin");

// --- 8. token endpoint failure -------------------------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" } }) };
globalThis.fetch = route(apiFetch({ tokenStatus: 503 }));
await EDA.connect();
ok(EDA.online === false,                      "token endpoint 503 -> standalone");
ok(/token endpoint -> 503/.test(Auth.error||""), "status surfaced: " + Auth.error);

// --- 9. renewal is scheduled before expiry -------------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" } }) };
globalThis.fetch = route(apiFetch({ expiresIn: 300 }));
await EDA.connect();
ok(!!Auth.renewTimer, "renewal timer armed for a long-running booth session");
clearTimeout(Auth.renewTimer);

// --- 10. claims fallbacks -------------------------------------------------
reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" } }) };
globalThis.fetch = route(apiFetch({ claims:{ sub:"abc-123" } }));
await EDA.connect();
ok(EDA.user.name === "abc-123", "falls back through claim names when preferred_username is absent");

reset();
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" } }) };
globalThis.fetch = route(apiFetch({ claims:{ preferred_username:"Åsa Lindqvist" } }));
await EDA.connect();
ok(EDA.user.name === "Åsa Lindqvist", "non-ASCII claims decode correctly: " + EDA.user.name);
const ini = nameFromUser();
ok(ini === "ASALINDQVI", "unicode name folds accents and caps at 10 letters: " + ini);

// --- 10b. renewal keeps EDA.token in step -------------------------------
// Regression: EDA.token is a copy taken during connect(). If a renewal only
// updated Auth.token, every call after the first expiry failed TokenExpired.
reset();
let issued = 0;
KC = { respond: (q) => ({ data:{ type:"eda-snake-auth", state:q.get("state"), code:"C" + (++issued) } }) };
globalThis.fetch = route(apiFetch({ expiresIn: 90 }));   // -> renew in 30s
await EDA.connect();
const first = EDA.token;
ok(!!first && first === Auth.token, "EDA.token and Auth.token agree after connect");
clearTimeout(Auth.renewTimer);
await Auth.renew();                                   // force the renewal path
ok(Auth.token && Auth.token === EDA.token, "EDA.token follows Auth.token through a renewal");
ok(tokenCalls.length === 2, "renewal performed a second exchange: " + tokenCalls.length);
ok(tokenCalls[1].code === "C2", "renewal used a freshly issued code");
clearTimeout(Auth.renewTimer);

// --- 10c. a failed renewal retries instead of giving up ------------------
reset();
KC = { respond: () => null };                          // authorize never answers
globalThis.fetch = route(apiFetch());
const got = await Auth.renew(1);
ok(got === null,          "renewal reports failure");
ok(!!Auth.renewTimer,     "another attempt is scheduled rather than failing permanently");
ok(EDA.token === null,    "stale token cleared so nothing sends an expired bearer");
clearTimeout(Auth.renewTimer);

reset();
KC = { respond: () => null };
globalThis.fetch = route(apiFetch());
await Auth.renew(5);
ok(/gave up/.test(Auth.error || ""), "stops after a bounded number of attempts: " + Auth.error);
clearTimeout(Auth.renewTimer);

// --- 11. no web crypto (insecure context) --------------------------------
reset();
const realSubtle = crypto.subtle;
Object.defineProperty(globalThis, 'crypto', { value: { getRandomValues: webcrypto.getRandomValues.bind(webcrypto) }, configurable: true });
globalThis.fetch = route(apiFetch());
await EDA.connect();
ok(EDA.online === false,                    "no crypto.subtle -> standalone rather than an exception");
ok(/secure context/.test(Auth.error || ""), "explains why: " + Auth.error);
Object.defineProperty(globalThis, 'crypto', { value: webcrypto, configurable: true });

console.log(issues.length ? "\n" + issues.length + " FAILURES" : "\nall checks passed");
process.exit(issues.length ? 1 : 0);
})();
