/* Leaderboard read/write against SnakeScore alone (the SnakeLeaderboard and
   SnakeLeaderboardState resources are gone). Covers ranking, tie-breaking,
   envelope tolerance, the POST body, and clearing. */
const fs = require('fs');
const { webcrypto } = require('crypto');
let issues = [];
const ok = (c,m)=>{ if(!c){ issues.push(m); console.log("FAIL:",m);} else console.log("ok:",m); };

const ORIGIN="https://eda.test";
globalThis.crypto = webcrypto;
globalThis.btoa=(x)=>Buffer.from(x,'binary').toString('base64');
globalThis.atob=(x)=>Buffer.from(x,'base64').toString('binary');
globalThis.location={ href:ORIGIN+"/core/httpproxy/v1/snake/", search:"", origin:ORIGIN };
const mk=()=>new Proxy({},{get:(t,p)=>{ if(p in t) return t[p]; if(p==='canvas') return {}; return ()=>{}; },set:(t,p,v)=>{t[p]=v;return true;}});
let msgFns=[];
globalThis.window={ devicePixelRatio:1,
  addEventListener(e,f){ if(e==="message") msgFns.push(f); },
  removeEventListener(e,f){ if(e==="message") msgFns=msgFns.filter(x=>x!==f); },
  localStorage:{_d:{},getItem(k){return this._d[k]||null;},setItem(k,v){this._d[k]=v;}} };
globalThis.addEventListener=window.addEventListener;
globalThis.removeEventListener=window.removeEventListener;
const made={};
const el=(id)=>{ if(!made[id]) made[id]={ style:{setProperty(){}},classList:{add(){},remove(){},toggle(){}},
  textContent:'',innerHTML:'',appendChild(){},onclick:null,getContext:mk,width:0,height:0,addEventListener(){} }; return made[id]; };
globalThis.document={ getElementById:el,
  createElement:(t)=> t==="iframe" ? ({style:{},setAttribute(){},remove(){},
    set src(v){ setTimeout(()=>{ const q=new URL(v,ORIGIN).searchParams;
      for(const f of msgFns.slice()) f({origin:ORIGIN,data:{type:"eda-snake-auth",state:q.get("state"),code:"C"}}); },1); },
    get src(){return null;} }) : el("tmp"),
  documentElement:{style:{setProperty(){}}},
  body:{style:{},classList:{add(){},remove(){},toggle(){}},appendChild(){}},
  querySelectorAll:()=>[] };
globalThis.navigator={getGamepads:()=>[]};
globalThis.requestAnimationFrame=()=>{};
globalThis.console.info=()=>{};
globalThis.fetch=async()=>{ throw new Error("offline"); };
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));
OIDC.timeoutMs=120;

const b=(o)=>Buffer.from(JSON.stringify(o)).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const TOKEN=b({alg:"RS256"})+"."+b({preferred_username:"admin"})+".sig";

const cr=(player,score,level,at,diff="normal")=>({
  metadata:{name:`score-${at}-${player.toLowerCase()}`,namespace:"eda"},
  spec:{player,score,level,difficulty:diff,edaUser:"admin",recordedAt:at}});

let store, posted, deleted;
function server(envelope){
  return async (url, opts) => {
    const u=String(url); const j=(o)=>({ok:true,status:200,json:async()=>o});
    if(u.includes("/openid-connect/token")) return j({access_token:TOKEN,expires_in:300});
    if(/\/core\/query\/v1/.test(u)) return j({data:[]});
    if(/\/snakescores\/.+/.test(u) && opts && opts.method==="DELETE"){
      deleted.push(decodeURIComponent(u.split("/snakescores/")[1]));
      return j({});
    }
    if(/\/snakescores$/.test(u)){
      if(opts && opts.method==="POST"){ posted.push(JSON.parse(opts.body)); return j({}); }
      return j(envelope(store));
    }
    throw new Error("unexpected "+u);
  };
}
const route=(f)=>async(url,opts)=>{ const r=await f(url,opts);
  if(String(url).includes("/openid-connect/token")) return r;
  if(!r.ok) throw new Error(url+" -> "+r.status); return r; };
function reset(){
  msgFns=[]; posted=[]; deleted=[];
  Auth.token=null; Auth.claims=null; Auth.error=null;
  clearTimeout(Auth.renewTimer); Auth.renewTimer=null;
  EDA.token=null; EDA.online=false; EDA.fabric=null; EDA.lastError=null;
  Board.list=[]; Board.lastIdx=-1; Board.backend="local";
}

(async()=>{

// --- path constant --------------------------------------------------------
ok(Config.scoresPath() === "/apps/eda.cdoyle.dev/v1alpha1/namespaces/eda/snakescores",
   "default scores path matches the one the lab accepted: " + Config.scoresPath());

// --- ranking --------------------------------------------------------------
reset();
store=[cr("AAA",100,3,"2026-10-02T10:00:00Z"), cr("BBB",900,9,"2026-10-02T10:05:00Z"),
       cr("CCC",400,5,"2026-10-02T10:02:00Z")];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
let board=await EDA.listScores();
ok(board.length===3,                 "all three scores returned");
ok(board[0].name==="BBB" && board[0].score===900, "highest score first");
ok(board[2].name==="AAA",            "lowest score last");
ok(board[0].level===9,               "level carried through");
ok(board[0].name==="BBB",            "board name comes from spec.player");
ok(board[0].edaUser==="admin",       "EDA login carried separately as edaUser");

// --- ties go to whoever got there first -----------------------------------
reset();
store=[cr("LAT",500,5,"2026-10-02T12:00:00Z"), cr("ERL",500,5,"2026-10-02T09:00:00Z")];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
board=await EDA.listScores();
ok(board[0].name==="ERL", "equal scores: earlier recordedAt ranks higher");

// --- only ten ------------------------------------------------------------
reset();
store=Array.from({length:25},(_,i)=>cr("P"+String(i).padStart(2,"0"), i*10, 1, "2026-10-02T10:00:0"+(i%10)+"Z"));
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
board=await EDA.listScores();
ok(board.length===Config.boardSize, "capped at the configured board size: "+board.length);
ok(board[0].score===240,    "top entry is the real maximum");

// --- envelope tolerance ---------------------------------------------------
for(const [label, env] of [["{items:[...]}", s=>({items:s})],
                           ["{data:[...]}",  s=>({data:s})],
                           ["bare array",    s=>s]]){
  reset();
  store=[cr("ONE",10,1,"2026-10-02T10:00:00Z")];
  globalThis.fetch=route(server(env));
  await Auth.ensure(); EDA.online=true;
  const r=await EDA.listScores();
  ok(r.length===1 && r[0].name==="ONE", "reads "+label);
}

// --- flattened rows (no spec wrapper) ------------------------------------
reset();
store=[{metadata:{name:"score-flat"}, player:"FLT", score:77, level:2, difficulty:"hard", recordedAt:"2026-10-02T10:00:00Z"}];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
board=await EDA.listScores();
ok(board.length===1 && board[0].name==="FLT" && board[0].score===77,
   "handles rows without a spec wrapper");

// --- malformed rows are dropped, not rendered as blanks -------------------
reset();
store=[cr("GUD",50,1,"2026-10-02T10:00:00Z"), {metadata:{name:"junk"}, spec:{score:999}}];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
board=await EDA.listScores();
ok(board.length===1 && board[0].name==="GUD", "row with no player name dropped rather than shown blank");

// --- the write ------------------------------------------------------------
reset();
store=[];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true; EDA.user.name="admin";
EDA.fabric={name:"eda",nodes:[{name:"a"},{name:"b"}],links:[]};
await EDA.postScore("CDY", 1234, 7, "hez");
ok(posted.length===1, "one POST issued");
const p=posted[0];
ok(p.kind==="SnakeScore" && p.apiVersion==="eda.cdoyle.dev/v1alpha1", "correct kind and apiVersion");
ok(p.metadata.namespace==="eda",   "written to the scores namespace");
ok(/^score-\d+-cdy$/.test(p.metadata.name), "unique CR name: "+p.metadata.name);
ok(p.spec.player==="CDY" && p.spec.score===1234 && p.spec.level===7, "spec carries the run, name in player");
ok(!("initials" in p.spec), "the retired initials field is no longer sent");
ok(p.spec.difficulty==="hez",      "difficulty recorded");
ok(p.spec.edaUser==="admin",       "EDA login recorded separately as edaUser");
ok(p.spec.player!==p.spec.edaUser,  "player and edaUser are independent (typed name vs login)");
ok(p.spec.fabricNodes===2,         "fabric size captured alongside the score");
ok(!isNaN(Date.parse(p.spec.recordedAt)), "recordedAt is a valid timestamp");

// --- clearing -------------------------------------------------------------
reset();
store=[cr("AAA",1,1,"2026-10-02T10:00:00Z"), cr("BBB",2,1,"2026-10-02T10:00:01Z")];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
await EDA.deleteAllScores();
ok(deleted.length===2, "every score CR deleted: "+deleted.length);
ok(deleted.every(n=>n.startsWith("score-")), "deleted by CR name: "+deleted.join(","));

// --- Board falls back to local storage when EDA is down -------------------
reset();
EDA.online=false;
await Board.load();
ok(Board.backend==="local", "offline -> local storage backend");

reset();
store=[cr("WEB",42,2,"2026-10-02T10:00:00Z")];
globalThis.fetch=route(server(s=>({items:s})));
await Auth.ensure(); EDA.online=true;
await Board.load();
ok(Board.backend==="eda",        "online -> EDA backend");
ok(Board.list.length===1 && Board.list[0].name==="WEB", "board populated from SnakeScore CRs");

clearTimeout(Auth.renewTimer);
console.log(issues.length ? "\n"+issues.length+" FAILURES" : "\nall leaderboard checks passed");
process.exit(issues.length?1:0);
})();
