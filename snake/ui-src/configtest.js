/* SnakeConfig: operator-editable settings read from a CR, with a URL override
   and working defaults when no CR exists. */
const fs=require('fs');
const { webcrypto }=require('crypto');
let issues=[];
const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

const ORIGIN="https://eda.test";
let SEARCH="";
globalThis.crypto=webcrypto;
globalThis.btoa=(x)=>Buffer.from(x,'binary').toString('base64');
globalThis.atob=(x)=>Buffer.from(x,'base64').toString('binary');
globalThis.location={ get href(){return ORIGIN+"/core/httpproxy/v1/snake/"+SEARCH;},
                      get search(){return SEARCH;}, origin:ORIGIN };
const mk=()=>new Proxy({},{get:(t,p)=>{if(p in t)return t[p];if(p==='canvas')return{};return()=>{};},set:(t,p,v)=>{t[p]=v;return true;}});
let msgFns=[];
globalThis.window={devicePixelRatio:1,
  addEventListener(e,f){if(e==="message")msgFns.push(f);},
  removeEventListener(e,f){if(e==="message")msgFns=msgFns.filter(x=>x!==f);},
  localStorage:{_d:{},getItem(k){return this._d[k]||null;},setItem(k,v){this._d[k]=v;}}};
globalThis.addEventListener=window.addEventListener;
globalThis.removeEventListener=window.removeEventListener;
const made={};
const el=(id)=>{if(!made[id])made[id]={style:{setProperty(){}},classList:{add(){},remove(){},toggle(){}},
  textContent:'',innerHTML:'',appendChild(){},onclick:null,getContext:mk,width:0,height:0,addEventListener(){}};return made[id];};
globalThis.document={getElementById:el,
  createElement:(t)=>t==="iframe"?({style:{},setAttribute(){},remove(){},
    set src(v){setTimeout(()=>{const q=new URL(v,ORIGIN).searchParams;
      for(const f of msgFns.slice())f({origin:ORIGIN,data:{type:"eda-snake-auth",state:q.get("state"),code:"C"}});},1);},
    get src(){return null;}}):el("tmp"),
  documentElement:{style:{setProperty(){}}},
  body:{style:{},classList:{add(){},remove(){},toggle(){}},appendChild(){}},
  querySelectorAll:()=>[]};
globalThis.navigator={getGamepads:()=>[]};
globalThis.requestAnimationFrame=()=>{};
globalThis.console.info=()=>{};
globalThis.fetch=async()=>{throw new Error("offline");};
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));
OIDC.timeoutMs=120;

const b=(o)=>Buffer.from(JSON.stringify(o)).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const TOKEN=b({alg:"RS256"})+"."+b({preferred_username:"admin"})+".sig";

let cfgRows, posted;
function server(){
  return async (url,opts)=>{
    const u=decodeURIComponent(String(url)); const j=(o)=>({ok:true,status:200,json:async()=>o});
    if(u.includes("/openid-connect/token")) return j({access_token:TOKEN,expires_in:300});
    if(/query\/v1/.test(u)){
      if(/snakeconfig/.test(u)){
        if(cfgRows === "error") return {ok:false,status:500};
        return j({data:cfgRows});
      }
      return j({data:[]});
    }
    if(/snakescores$/.test(u)){
      if(opts&&opts.method==="POST"){ posted.push({url:u, body:JSON.parse(opts.body)}); return j({}); }
      return j({items:[]});
    }
    throw new Error("unexpected "+u);
  };
}
const route=(f)=>async(url,opts)=>{const r=await f(url,opts);
  if(String(url).includes("/openid-connect/token"))return r;
  if(!r.ok)throw new Error(url+" -> "+r.status);return r;};
function reset(search=""){
  SEARCH=search; msgFns=[]; posted=[]; cfgRows=[];
  Auth.token=null;Auth.claims=null;Auth.error=null;
  clearTimeout(Auth.renewTimer);Auth.renewTimer=null;
  EDA.token=null;EDA.online=false;EDA.fabric=null;EDA.lastError=null;
  Config.scoreNamespace="eda"; Config.boardSize=10;
  Config.defaultDifficulty="normal"; Config.source="built-in defaults"; Config.configNamespace=null;
}

(async()=>{

// --- defaults when no CR exists ------------------------------------------
reset();
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.scoreNamespace==="eda",    "defaults to eda with no SnakeConfig");
ok(Config.boardSize===10,            "default board size 10");
ok(Config.defaultDifficulty==="normal", "default difficulty normal");
ok(Config.scoresPath()==="/apps/eda.cdoyle.dev/v1alpha1/namespaces/eda/snakescores",
   "default scores path unchanged: "+Config.scoresPath());

// --- a SnakeConfig CR is honoured ----------------------------------------
reset();
cfgRows=[{".namespace.name":"eda-telemetry",
          spec:{scoreNamespace:"booth",boardSize:20,defaultDifficulty:"hez"}}];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.scoreNamespace==="booth",      "scoreNamespace read from the CR");
ok(Config.boardSize===20,                "boardSize read from the CR");
ok(Config.defaultDifficulty==="hez",     "defaultDifficulty read from the CR");
ok(Config.configNamespace==="eda-telemetry", "records where the config was found");
ok(/SnakeConfig in eda-telemetry/.test(Config.source), "source is reportable: "+Config.source);
ok(Config.scoresPath().includes("/namespaces/booth/"), "scores path follows the config");

// --- the write lands in the configured namespace -------------------------
EDA.user.name="admin";
await EDA.postScore("CFG",10,1,"normal");
ok(posted.length===1, "score posted");
ok(posted[0].url.includes("/namespaces/booth/snakescores"), "POSTed to the configured namespace");
ok(posted[0].body.metadata.namespace==="booth", "CR metadata namespace matches");

// --- URL override beats the CR -------------------------------------------
reset("?scorens=demo");
cfgRows=[{spec:{scoreNamespace:"booth"}}];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.scoreNamespace==="demo",        "?scorens= overrides the CR");
ok(/URL override/.test(Config.source),    "source names the override");

// --- hyphenated field names also work ------------------------------------
reset();
cfgRows=[{spec:{"score-namespace":"kebab","board-size":5,"default-difficulty":"hard"}}];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.scoreNamespace==="kebab", "accepts kebab-case field names too");
ok(Config.boardSize===5,            "kebab boardSize honoured");

// --- nonsense values are clamped, not trusted ----------------------------
reset();
cfgRows=[{spec:{boardSize:9999,defaultDifficulty:"impossible"}}];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.boardSize===10,               "absurd board size rejected, default kept: "+Config.boardSize);
ok(Config.defaultDifficulty==="normal", "unknown difficulty rejected");

reset();
cfgRows=[{spec:{boardSize:1}}];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.boardSize===10, "board size below the floor rejected");

// --- a failing config query must not break the game ----------------------
reset();
cfgRows="error";
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
let threw=false;
try{ await Config.load(); }catch(e){ threw=true; }
ok(!threw,                        "a 500 on the config query does not throw");
ok(Config.scoreNamespace==="eda", "falls back to defaults after a failed query");

// --- offline: defaults, no query attempted -------------------------------
reset();
EDA.online=false;
globalThis.fetch=route(server());
await Config.load();
ok(Config.scoreNamespace==="eda", "standalone mode uses defaults");

// --- CRD not installed (empty rows) --------------------------------------
reset();
cfgRows=[];
globalThis.fetch=route(server());
await Auth.ensure(); EDA.online=true;
await Config.load();
ok(Config.scoreNamespace==="eda" && Config.source==="built-in defaults",
   "no CR -> built-in defaults, reported honestly");

clearTimeout(Auth.renewTimer);
console.log(issues.length?"\n"+issues.length+" FAILURES":"\nall config checks passed");
process.exit(issues.length?1:0);
})();
