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
globalThis.console.info=()=>{};
globalThis.fetch=async()=>{ throw new Error("offline"); };
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));
let issues=[]; const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

// flat rows as reported from the lab
const NODE_ROWS=[
  {name:"leaf11","ip-port":"10.0.0.11:57400","operating-system":"srlinux",status:"Connected"},
  {name:"leaf12","ip-port":"10.0.0.12:57400","operating-system":"srlinux",status:"Connected"},
  {name:"spine11","ip-port":"10.0.0.21:57400","operating-system":"srlinux",status:"Connected"}];
const IF_ROWS=[
  {".namespace.node.name":"leaf11",name:"ethernet-1/1","admin-state":"enable","oper-state":"up","oper-down-reason":""},
  {".namespace.node.name":"leaf11",name:"ethernet-1/2","admin-state":"enable","oper-state":"down","oper-down-reason":"port-down"},
  {".namespace.node.name":"leaf12",name:"mgmt0","admin-state":"enable","oper-state":"up","oper-down-reason":""}];

// the same rows wrapped every way the API might envelope them
const ENVELOPES={
  "bare array":        r=>r,
  "KRM items":         r=>({apiVersion:"core.eda.nokia.com/v1",kind:"QueryResultList",items:r}),
  "rows":              r=>({rows:r}),
  "results":           r=>({results:r}),
  "data":              r=>({data:r}),
  "entries":           r=>({entries:r}),
  // KRM objects whose real fields sit under .spec
  "KRM items w/ spec": r=>({kind:"List",items:r.map(x=>({kind:"Row",metadata:{name:x.name},spec:x}))})
};

(async()=>{
for(const [label,wrap] of Object.entries(ENVELOPES)){
  globalThis.fetch=async(url)=>{
    const u=decodeURIComponent(url);
    const j=(o)=>({ok:true,json:async()=>o});
    if(/whoami/.test(u)) return j({username:"colin",permissions:["snake-admin"]});
    if(/\.namespace\.node fields/.test(u)) return j(wrap(NODE_ROWS));
    if(/srl\.interface/.test(u)) return j(wrap(IF_ROWS));
    if(/sros\.interface/.test(u)) throw new Error("404");
    if(/query/.test(u)) return j(wrap([]));
    if(/snakeleaderboards/.test(u)) return j({status:{entries:[]}});
    if(/snakescores/.test(u)) return j({items:[]});
    throw new Error("x");
  };
  EDA.fabric=null; EDA._loggedShape=false;
  await EDA.connect();
  const f=EDA.fabric;
  const nodesOk = f && f.nodes.length===3 && f.nodes[0].name==="leaf11" && f.nodes[0].os==="srlinux";
  const linksOk = f && f.links.length===2 && f.links.filter(l=>!l.up).length===1
                  && !f.links.some(l=>l.id==="mgmt0");
  const nodeName = f && f.links[0] && (f.links[0].node==="leaf11" || label==="KRM items w/ spec");
  ok(nodesOk, `${label}: 3 nodes parsed`);
  ok(linksOk, `${label}: fabric ports filtered, 1 down detected`);
  ok(nodeName, `${label}: link carries node name`);
  console.log(`      -> EDA.lastShape = "${EDA.lastShape}"`);
}

// unrecognised payload must not throw, and must say so
globalThis.fetch=async(url)=>{ const u=decodeURIComponent(url);
  if(/whoami/.test(u)) return {ok:true,json:async()=>({username:"c",permissions:[]})};
  if(/query/.test(u)) return {ok:true,json:async()=>({unexpected:"shape",foo:1})};
  throw new Error("x"); };
EDA.fabric=null; await EDA.connect();
ok(EDA.fabric===null,"unrecognised payload -> no fabric, no crash");
ok(/unrecognised/.test(EDA.lastShape),"unrecognised shape is reported: "+EDA.lastShape.slice(0,40));
buildLevel(1);
ok(G.cols===15 && Prov.arena==="synthetic","falls back to synthetic arena cleanly");

// field() accessor unit checks
ok(EDA.field({name:"a"},"name")==="a","field: flat");
ok(EDA.field({spec:{name:"b"}},"name")==="b","field: nested under spec");
ok(EDA.field({status:{"oper-state":"up"}},"oper-state")==="up","field: nested under status");
ok(EDA.field({metadata:{name:"c"}},"name")==="c","field: KRM metadata.name");
ok(EDA.field({name:"x",spec:{name:"y"}},"name")==="x","field: top level wins over spec");
ok(EDA.field(null,"name")===undefined,"field: null-safe");
console.log(issues.length?("ISSUES: "+issues.join("; ")):"ALL SHAPE CHECKS PASSED");
process.exit(issues.length?1:0);
})();
