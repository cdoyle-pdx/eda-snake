/* Namespace scoping for fabric discovery.
   `.namespace.node` spans every namespace the token can read, so these tests
   pin down which one the arena is built from and prove that a same-named node
   in another namespace cannot contribute links. */
const fs = require('fs');
const { webcrypto } = require('crypto');

let issues = [];
const ok = (c, m) => { if(!c){ issues.push(m); console.log("FAIL:", m); } else console.log("ok:", m); };

const ORIGIN = "https://eda.test";
let SEARCH = "";
globalThis.crypto = webcrypto;
globalThis.btoa = (x)=>Buffer.from(x,'binary').toString('base64');
globalThis.atob = (x)=>Buffer.from(x,'base64').toString('binary');
globalThis.location = { get href(){ return ORIGIN+"/core/httpproxy/v1/snake/"+SEARCH; },
                        get search(){ return SEARCH; }, origin: ORIGIN };

const mk = () => new Proxy({}, { get:(t,p)=>{ if(p in t) return t[p]; if(p==='canvas') return {}; return ()=>{}; },
                                 set:(t,p,v)=>{t[p]=v;return true;} });
let msgFns = [];
globalThis.window = { devicePixelRatio:1,
  addEventListener(e,f){ if(e==="message") msgFns.push(f); },
  removeEventListener(e,f){ if(e==="message") msgFns = msgFns.filter(x=>x!==f); },
  localStorage:{ _d:{}, getItem(k){return this._d[k]||null;}, setItem(k,v){this._d[k]=v;} } };
globalThis.addEventListener = window.addEventListener;
globalThis.removeEventListener = window.removeEventListener;
const made = {};
const el = (id) => { if(!made[id]) made[id] = { style:{setProperty(){}},
  classList:{add(){},remove(){},toggle(){}}, textContent:'', innerHTML:'',
  appendChild(){}, onclick:null, getContext:mk, width:0, height:0, addEventListener(){} }; return made[id]; };
globalThis.document = { getElementById: el,
  createElement:(tag)=> tag==="iframe" ? ({ style:{}, setAttribute(){}, remove(){},
    set src(v){ setTimeout(()=>{ const q=new URL(v,ORIGIN).searchParams;
      for(const f of msgFns.slice()) f({origin:ORIGIN,
        data:{type:"eda-snake-auth", state:q.get("state"), code:"C"}}); },1); },
    get src(){ return null; } }) : el("tmp"),
  documentElement:{style:{setProperty(){}}},
  body:{ style:{}, classList:{add(){},remove(){},toggle(){}}, appendChild(){} },
  querySelectorAll: () => [] };
globalThis.navigator = { getGamepads: () => [] };
globalThis.requestAnimationFrame = () => {};
globalThis.console.info = () => {};
globalThis.fetch = async () => { throw new Error("offline"); };
(0, eval)(fs.readFileSync('eda_globals.js','utf8'));
OIDC.timeoutMs = 120;

const b = (o)=>Buffer.from(JSON.stringify(o)).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const TOKEN = b({alg:"RS256"})+"."+b({preferred_username:"admin"})+".sig";

// eda:        leaf1, leaf2, spine1      (3 nodes)
// fabric-demo: leaf1, leaf2, spine1, spine2 (4 nodes) - note the duplicate names
const NODES = [
  {".namespace.name":"eda", name:"leaf1",  "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"eda", name:"leaf2",  "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"eda", name:"spine1", "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"fabric-demo", name:"leaf1",  "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"fabric-demo", name:"leaf2",  "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"fabric-demo", name:"spine1", "operating-system":"srlinux", status:"Connected"},
  {".namespace.name":"fabric-demo", name:"spine2", "operating-system":"srlinux", status:"Connected"},
];
const IFS = [
  {".namespace.name":"eda", ".namespace.node.name":"leaf1", name:"ethernet-1/1", "admin-state":"enable","oper-state":"up"},
  {".namespace.name":"eda", ".namespace.node.name":"leaf1", name:"mgmt0",        "admin-state":"enable","oper-state":"up"},
  {".namespace.name":"fabric-demo", ".namespace.node.name":"leaf1",  name:"ethernet-1/1","admin-state":"enable","oper-state":"up"},
  {".namespace.name":"fabric-demo", ".namespace.node.name":"leaf2",  name:"ethernet-1/2","admin-state":"enable","oper-state":"down","oper-down-reason":"port-down"},
  {".namespace.name":"fabric-demo", ".namespace.node.name":"spine2", name:"ethernet-1/3","admin-state":"enable","oper-state":"up"},
];

function server(nodes = NODES, ifs = IFS){
  return async (url, opts) => {
    const u = decodeURIComponent(String(url));
    const j = (o) => ({ ok:true, status:200, json: async () => o });
    if(u.includes("/openid-connect/token")) return j({access_token:TOKEN, expires_in:300});
    if(/query/.test(u)) return j(/interface/.test(u) ? ifs : nodes);
    return j({items:[]});
  };
}
const route = (f) => async (url, opts) => {
  const r = await f(url, opts);
  if(String(url).includes("/openid-connect/token")) return r;
  if(!r.ok) throw new Error(url+" -> "+r.status);
  return r;
};
function reset(search=""){
  SEARCH = search; msgFns = [];
  Auth.token=null; Auth.claims=null; Auth.error=null;
  clearTimeout(Auth.renewTimer); Auth.renewTimer=null;
  EDA.token=null; EDA.online=false; EDA.fabric=null; EDA.lastError=null;
  EDA.namespace=null; EDA.namespaces=[];
}

(async () => {

// --- 1. largest namespace wins by default -------------------------------
reset();
globalThis.fetch = route(server());
await EDA.connect();
ok(EDA.online === true,                "online with two namespaces present");
ok(EDA.namespace === "fabric-demo",    "picked the namespace with the most nodes: " + EDA.namespace);
ok(EDA.fabric.nodes.length === 4,      "exactly that namespace's nodes (4), not all 7: " + EDA.fabric.nodes.length);
ok(EDA.namespaces.join(",") === "eda,fabric-demo", "records every namespace seen: " + EDA.namespaces.join(","));
ok(EDA.fabric.name === "fabric-demo",  "fabric is named for its namespace");

// --- 2. no cross-namespace link bleed ------------------------------------
const owners = EDA.fabric.links.map(l => l.node).sort();
ok(EDA.fabric.links.length === 3,      "3 fabric links (mgmt0 excluded, other namespace excluded): " + EDA.fabric.links.length);
ok(!EDA.fabric.links.some(l => l.id === "mgmt0"), "mgmt0 is not a fabric port");
ok(owners.join(",") === "leaf1,leaf2,spine2", "links owned only by nodes in the chosen namespace: " + owners.join(","));
const down = EDA.fabric.links.filter(l => !l.up);
ok(down.length === 1 && down[0].node === "leaf2", "the down link is the one from fabric-demo, not eda's duplicate leaf1");

// --- 3. ?ns= override ----------------------------------------------------
reset("?ns=eda");
globalThis.fetch = route(server());
await EDA.connect();
ok(EDA.namespace === "eda",       "?ns= overrides the size heuristic: " + EDA.namespace);
ok(EDA.fabric.nodes.length === 3, "scoped to the requested namespace");
ok(EDA.fabric.links.length === 1, "only eda's fabric ports: " + EDA.fabric.links.length);

// --- 4. ?ns= naming a namespace with no nodes ----------------------------
reset("?ns=does-not-exist");
globalThis.fetch = route(server());
await EDA.connect();
ok(EDA.online === true,             "unknown ?ns= does not break discovery");
ok(EDA.namespace === "fabric-demo", "falls back to the largest namespace");
ok(/does-not-exist/.test(EDA.lastError||""), "says why it ignored the request: " + EDA.lastError);

// --- 5. single namespace behaves exactly as before ------------------------
reset();
globalThis.fetch = route(server(NODES.filter(n=>n[".namespace.name"]==="eda"),
                                IFS.filter(i=>i[".namespace.name"]==="eda")));
await EDA.connect();
ok(EDA.namespace === "eda",        "single namespace selected");
ok(EDA.fabric.nodes.length === 3,  "all 3 of its nodes");
ok(EDA.namespaces.length === 1,    "one namespace recorded");

// --- 6. cluster omits the namespace column -------------------------------
reset();
const bare = NODES.filter(n=>n[".namespace.name"]==="eda").map(n=>{ const c={...n}; delete c[".namespace.name"]; return c; });
const bareIfs = IFS.filter(i=>i[".namespace.name"]==="eda").map(i=>{ const c={...i}; delete c[".namespace.name"]; return c; });
globalThis.fetch = route(server(bare, bareIfs));
await EDA.connect();
ok(EDA.online === true,           "missing namespace column is not fatal");
ok(EDA.fabric.nodes.length === 3, "all nodes kept when there is nothing to group by");
ok(EDA.fabric.links.length === 1, "links still resolve");

// --- 7. ties resolve deterministically ------------------------------------
reset();
const tied = [
  {".namespace.name":"zulu",  name:"n1","operating-system":"srlinux",status:"Connected"},
  {".namespace.name":"alpha", name:"n2","operating-system":"srlinux",status:"Connected"},
];
globalThis.fetch = route(server(tied, []));
await EDA.connect();
ok(EDA.namespace === "alpha", "equal-sized namespaces break alphabetically, so reloads agree: " + EDA.namespace);

// --- 8. the badge names the namespace ------------------------------------
reset();
globalThis.fetch = route(server());
await EDA.connect();
const label = sourceLabel();
ok(/fabric-demo/.test(label),  "badge names the namespace: " + label);
ok(/4 nodes/.test(label),      "badge counts only that namespace's nodes");
ok(/2 namespaces/.test(label), "badge hints that other namespaces exist");

reset();
globalThis.fetch = route(server(NODES.filter(n=>n[".namespace.name"]==="eda"), []));
await EDA.connect();
ok(!/namespaces\)/.test(sourceLabel()), "no parenthetical when there is only one namespace: " + sourceLabel());

EDA.online = false; EDA.fabric = null;
ok(sourceLabel() === "Standalone — no fabric", "offline label unchanged");

clearTimeout(Auth.renewTimer);
console.log(issues.length ? "\n" + issues.length + " FAILURES" : "\nall namespace checks passed");
process.exit(issues.length ? 1 : 0);
})();
