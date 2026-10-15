const fs=require('fs');
const mk=()=>new Proxy({},{get:(t,p)=>{ if(p in t) return t[p]; if(p==='canvas') return {}; return ()=>{}; },set:(t,p,v)=>{t[p]=v;return true;}});
const createCanvas=()=>({getContext:mk,width:0,height:0,style:{},classList:{add(){},remove(){}}});
const real=createCanvas();
let OV={innerHTML:"",classList:{add(){},remove(){},toggle(){}},style:{}};
const made={};
const el=(id)=>{ if(id==="game")return real; if(id==="overlay")return OV;
  if(!made[id]) made[id]={ style:{setProperty(){}}, classList:{add(){},remove(){},toggle(){}},
    textContent:'', innerHTML:'', appendChild(){}, onclick:null, getContext:mk, width:0,height:0, addEventListener(){} };
  return made[id]; };
globalThis.document={ getElementById:el, createElement:()=>el("tmp"),
  documentElement:{style:{setProperty(){}}}, body:{style:{},classList:{add(){},remove(){},toggle(){}}} };
globalThis.window={ devicePixelRatio:1, addEventListener(){},
  localStorage:{_d:{},getItem(k){return this._d[k]||null;},setItem(k,v){this._d[k]=v;}} };
globalThis.navigator={ getGamepads:()=>[] };
// The auth path needs a secure-context-ish environment. Identity now comes from
// a token claim rather than a whoami endpoint, so these tests stub the OIDC
// round trip and assert on what connect() does with the result.
const { webcrypto } = require('crypto');
globalThis.crypto = webcrypto;
globalThis.btoa = (x)=>Buffer.from(x,'binary').toString('base64');
globalThis.atob = (x)=>Buffer.from(x,'base64').toString('binary');
globalThis.location = { href:"https://eda.test/core/httpproxy/v1/snake/", origin:"https://eda.test" };
let msgFns=[];
globalThis.window.addEventListener=(e,f)=>{ if(e==="message") msgFns.push(f); };
globalThis.window.removeEventListener=(e,f)=>{ if(e==="message") msgFns=msgFns.filter(x=>x!==f); };
globalThis.addEventListener=globalThis.window.addEventListener;
globalThis.removeEventListener=globalThis.window.removeEventListener;
let KC_CODE="CODE";
document.createElement=(tag)=>{
  if(tag!=="iframe") return el("tmp");
  return { style:{}, setAttribute(){}, remove(){}, set src(v){
    setTimeout(()=>{ const q=new URL(v,"https://eda.test").searchParams;
      for(const f of msgFns.slice())
        f({ origin:"https://eda.test",
            data:{ type:"eda-snake-auth", state:q.get("state"), code:KC_CODE } }); },1);
  }, get src(){ return null; } };
};
document.body.appendChild=()=>{};
const mkJwt=(claims)=>{ const b=(o)=>Buffer.from(JSON.stringify(o)).toString('base64')
  .replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  return b({alg:"RS256"})+"."+b(claims)+".sig"; };
let CLAIMS={};
const resetAuth=()=>{ Auth.token=null; Auth.claims=null; Auth.error=null;
  clearTimeout(Auth.renewTimer); Auth.renewTimer=null; msgFns=[]; };
globalThis.requestAnimationFrame=()=>{};
globalThis.console.info=()=>{};
globalThis.fetch=async()=>{ throw new Error("offline"); };
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));
let issues=[]; const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

const NODES=[{name:"leaf1","operating-system":"srlinux",status:"Connected"},
             {name:"leaf2","operating-system":"srlinux",status:"Connected"},
             {name:"spine1","operating-system":"srlinux",status:"Connected"}];
const IFS=[{".namespace.node.name":"leaf1",name:"ethernet-1/1","admin-state":"enable","oper-state":"up"}];

function api({whoami404=true, identityPath=null}={}){
  return async (url)=>{
    const u=decodeURIComponent(url);
    const j=(o)=>({ok:true,json:async()=>o});
    if(u.includes("/openid-connect/token")){
      return j({ access_token: mkJwt(CLAIMS), expires_in:300, token_type:"Bearer" });
    }
    if(/whoami|userinfo/.test(u)){
      if(identityPath && u.includes(identityPath)) return j({username:"colin"});
      return {ok:false,status:404};
    }
    if(/query/.test(u)){
      if(/interface/.test(u)) return j(IFS);
      return j(NODES);
    }
    if(/snakeleaderboard/.test(u)) return j({status:{entries:[]}});
    if(/snakescores/.test(u)) return j({items:[]});
    throw new Error("unexpected "+u);
  };
}
// the api() helper throws on !ok, so model that
const wrap=(f)=>async(url,opts)=>{ const r=await f(url,opts);
  if(String(url).includes("/openid-connect/token")) return r;
  if(!r.ok) throw new Error(url+" -> "+r.status); return r; };

(async()=>{
// --- the exact failure the user hit: whoami 404, everything else fine ---
// (kept as a regression guard: identity trouble must never force standalone)
resetAuth(); CLAIMS={};
globalThis.fetch=wrap(api({}));
await EDA.connect();
ok(EDA.online===true, "whoami 404 no longer forces standalone");
ok(!!EDA.fabric, "topology still read despite missing identity");
ok(EDA.fabric.nodes.length===3, "3 nodes discovered");
ok(EDA.user.name==="", "no identity -> empty username, not a crash");
ok(EDA.user.endpoint===null, "records that no identity endpoint worked");
ok(EDA.user.canReset===true, "reset offered; the API is the real gate");

// initials fall back sensibly with no username
const ini = nameFromUser();
ok(ini === "", "no username -> no prefill (entry starts the player on A): "+JSON.stringify(ini));

// --- identity from the access token's claims ---
// 25.8 has no whoami endpoint (confirmed by sweeping the core OpenAPI spec),
// so the username is read from preferred_username in the token we already hold.
resetAuth(); CLAIMS={preferred_username:"colin"};
globalThis.fetch=wrap(api({}));
await EDA.connect();
ok(EDA.user.name==="colin", "identity read from token claims");
ok(EDA.user.endpoint==="oidc:access_token", "records the claim as the source");
ok(nameFromUser()==="COLIN", "prefill uses the whole username, up to 10 letters");

// --- API genuinely unreachable (with a valid token in hand) ---
resetAuth(); CLAIMS={preferred_username:"colin"};
globalThis.fetch=async(url)=>{
  if(String(url).includes("/openid-connect/token"))
    return {ok:true,json:async()=>({access_token:mkJwt(CLAIMS),expires_in:300})};
  throw new Error("connection refused"); };
await EDA.connect();
ok(EDA.online===false, "unreachable API -> standalone");
ok(/api unreachable/.test(EDA.lastError), "error names the cause: "+EDA.lastError);
buildLevel(1);
ok(G.cols===15 && Prov.arena==="synthetic", "falls back to synthetic arena");

// --- API up, topology empty ---
resetAuth(); CLAIMS={preferred_username:"colin"};
globalThis.fetch=wrap(async(url)=>{
  const u=decodeURIComponent(url); const j=(o)=>({ok:true,json:async()=>o});
  if(u.includes("/openid-connect/token")) return j({access_token:mkJwt(CLAIMS),expires_in:300});
  if(/whoami|userinfo/.test(u)) return {ok:false,status:404};
  if(/query/.test(u)) return j([]);
  return j({});
});
await EDA.connect();
ok(EDA.online===true, "empty topology still counts as online");
ok(EDA.fabric===null, "no fabric when no nodes");
clearTimeout(Auth.renewTimer);   // otherwise the pending renewal keeps node alive
console.log(issues.length?("ISSUES: "+issues.join("; ")):"ALL CONNECT TESTS PASSED");
process.exit(issues.length?1:0);
})();
