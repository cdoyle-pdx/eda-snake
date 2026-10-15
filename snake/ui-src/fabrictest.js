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
globalThis.requestAnimationFrame=()=>{};

// ---- EXACT shapes reported from the live lab: BARE ARRAYS, real field names ----
const NODES=[
  {name:"leaf11", "ip-port":"10.0.0.11:57400", "operating-system":"srlinux", status:"Connected"},
  {name:"leaf12", "ip-port":"10.0.0.12:57400", "operating-system":"srlinux", status:"Connected"},
  {name:"leaf13", "ip-port":"10.0.0.13:57400", "operating-system":"srlinux", status:"Connected"},
  {name:"spine11","ip-port":"10.0.0.21:57400", "operating-system":"srlinux", status:"Connected"},
  {name:"spine12","ip-port":"10.0.0.22:57400", "operating-system":"srlinux", status:"Connected"}
];
const IFS=[
  {".namespace.node.name":"leaf11", name:"ethernet-1/1", "admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"leaf11", name:"ethernet-1/2", "admin-state":"enable","oper-state":"down","oper-down-reason":"port-down"},
  {".namespace.node.name":"leaf12", name:"ethernet-1/1", "admin-state":"disable","oper-state":"down","oper-down-reason":"admin-disabled"},
  {".namespace.node.name":"leaf13", name:"mgmt0",        "admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"leaf13", name:"lo0",          "admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"leaf13", name:"system0",      "admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"spine11",name:"ethernet-1/1", "admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"spine11",name:"lag1",         "admin-state":"enable","oper-state":"up","oper-down-reason":""}
];
let queries=[];
globalThis.fetch=async(url,opts)=>{
  const j=(o)=>({ok:true,json:async()=>o});
  const u=decodeURIComponent(url);
  if(/whoami/.test(u)) return j({username:"colin",permissions:["snake-admin"]});
  if(/query/.test(u)){
    queries.push(u.split("query=")[1]);
    if(/\.namespace\.node fields/.test(u)) return j(NODES);          // bare array
    if(/\.namespace\.node\.srl\.interface/.test(u)) return j(IFS);   // bare array
    if(/\.namespace\.node\.sros\.interface/.test(u)) throw new Error("404 no sros table");
    return j([]);
  }
  if(/snakeleaderboards\/default/.test(u)) return j({status:{entries:[],totalRuns:0,topScore:0}});
  if(/snakescores/.test(u)) return j({items:[]});
  throw new Error("unexpected "+u);
};
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));
let issues=[]; const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

(async()=>{
await EDA.connect();
ok(EDA.online===true,"connected");
ok(!!EDA.fabric,"fabric parsed from bare-array payloads");
ok(EDA.fabric.nodes.length===5,"5 nodes parsed (got "+(EDA.fabric.nodes?EDA.fabric.nodes.length:0)+")");
ok(EDA.fabric.nodes[0].name==="leaf11","node name read from 'name'");
ok(EDA.fabric.nodes[0].os==="srlinux","operating-system captured");
ok(EDA.fabric.nodes[0].status==="Connected","status captured");
ok(EDA.fabric.nodes[3].role==="spine","spine role inferred from name");
ok(EDA.fabric.nodes[0].role==="leaf","leaf role inferred from name");

// query text correctness
ok(queries.some(q=>/^\.namespace\.node fields \[\.namespace\.name, name, operating-system, status\]/.test(q)),
   "node query uses verified fields, namespace column included");
ok(queries.some(q=>/\.namespace\.node\.srl\.interface fields \[\.namespace\.name, \.namespace\.node\.name, name, admin-state, oper-state, oper-down-reason\]/.test(q)),
   "interface query uses verified fields, namespace column included");
ok(!queries.some(q=>/platform/.test(q)),"the bogus .platform table is gone");
ok(!queries.some(q=>/sros/.test(q)),"sros table not queried for an all-srlinux fabric");

// link filtering
const L=EDA.fabric.links;
ok(L.length===5,"only fabric ports kept (ethernet-*/lag), got "+L.length);
ok(!L.some(l=>/mgmt|lo0|system/.test(l.id)),"mgmt/loopback/system excluded from links");
ok(L.some(l=>l.id==="lag1"),"lag ports counted as fabric links");
ok(L.filter(l=>!l.up).length===2,"2 down ports detected");
ok(L.filter(l=>l.adminDown).length===1,"1 admin-disabled port flagged");
ok(L.find(l=>l.id==="ethernet-1/2").node==="leaf11","link carries its node name");
ok(L.find(l=>l.id==="ethernet-1/2").reason==="port-down","oper-down-reason captured");

// downstream game wiring
buildLevel(1);
ok(Prov.arena==="fabric","L1 arena seeded from fabric");
ok(Prov.fabricNodes===5,"provenance records node count");
ok(Prov.downLinks===2,"provenance records down links");
ok(Prov.adminDown===1,"provenance records admin-down separately");
ok(Prov.walls==="fabric+synthetic","walls marked as fabric-derived");
spawnLetter();
ok(NODES.some(n=>n.name===G.letter.node),"letters spawn on real node names");
showExplainer(null);
ok(/leaf11/.test(OV.innerHTML),"explainer names real nodes");
ok(/2 down link/.test(OV.innerHTML),"explainer reports the real down-link count");
ok(/admin-disabled/.test(OV.innerHTML),"explainer distinguishes admin-disabled");
ok(/fabric ports/.test(OV.innerHTML),"explainer reports port count");

// mixed-OS fabric picks up both tables
EDA.fabric=null; queries=[];
NODES.push({name:"pe1","ip-port":"10.0.0.31:57400","operating-system":"sros",status:"Connected"});
await EDA.connect();
ok(queries.some(q=>/sros\.interface/.test(q)),"sros table queried when an SR OS node is present");
ok(EDA.fabric && EDA.fabric.nodes.length===6,"mixed-OS fabric still parses after the sros query fails");

// empty fabric degrades, never throws into the UI
globalThis.fetch=async(url)=>{ const u=decodeURIComponent(url);
  if(/whoami/.test(u)) return {ok:true,json:async()=>({username:"c",permissions:[]})};
  if(/query/.test(u)) return {ok:true,json:async()=>[]};
  throw new Error("x"); };
EDA.fabric=null; await EDA.connect();
ok(EDA.fabric===null,"empty node list -> no fabric, no crash");
buildLevel(1);
ok(Prov.arena==="synthetic" && G.cols===15,"falls back to the synthetic arena");
console.log(issues.length?("ISSUES: "+issues.join("; ")):"ALL FABRIC CHECKS PASSED");
process.exit(issues.length?1:0);   // was exiting 0 regardless, hiding real failures
})();
