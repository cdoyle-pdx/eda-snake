/* Contract: what the game POSTs must match what the SnakeScore CRD declares.
   A mismatch fails silently in production -- the API rejects the score and the
   game falls back to local storage -- so it is checked here against the Go
   types file that generates the CRD. Needs snakescore_api_types.go alongside
   (in the repo: ../api/v1alpha1/snakescore_api_types.go). */
const fs=require('fs'), path=require('path');
let issues=[];
const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

const typesPath = [ 'snakescore_api_types.go', '../api/v1alpha1/snakescore_api_types.go' ]
  .find(p => fs.existsSync(p));
if(!typesPath){ console.log("FAIL: snakescore_api_types.go not found"); process.exit(1); }
const go = fs.readFileSync(typesPath,'utf8');

// parse SnakeScoreSpec's fields: json name, required (no omitempty), Pattern marker
const specBody = go.split('type SnakeScoreSpec struct {')[1].split('\n}')[0];
const fields = {};
let pending = {};
for(const line of specBody.split('\n')){
  const pm = line.match(/\+kubebuilder:validation:Pattern=`([^`]+)`/);
  if(pm) pending.pattern = new RegExp(pm[1]);
  const em = line.match(/\+kubebuilder:validation:Enum=([\w;]+)/);
  if(em) pending.enum = em[1].split(';');
  const fm = line.match(/^\s*\w+\s+\w+\s+`json:"([^",]+)(,omitempty)?"`/);
  if(fm){ fields[fm[1]] = { required: !fm[2], ...pending }; pending = {}; }
}
console.log("CRD spec fields:", Object.keys(fields).join(", "));

// the default-columns markers must name real fields, or `edabuilder generate` fails
for(const m of go.matchAll(/\+eda:ui:defaultcolumns=\.spec\.(\w+)/g))
  ok(m[1] in fields, `defaultcolumns marker .spec.${m[1]} names a real field`);

// capture a real POST from the game
const mk=()=>new Proxy({},{get:(t,p)=>{if(p in t)return t[p];if(p==='canvas')return{};return()=>{};},set:(t,p,v)=>{t[p]=v;return true;}});
const made={}; const el=(id)=>{ if(!made[id]) made[id]={style:{setProperty(){}},classList:{add(){},remove(){},toggle(){}},textContent:'',innerHTML:'',appendChild(){},getContext:mk,addEventListener(){}}; return made[id]; };
globalThis.document={getElementById:el,createElement:()=>el("tmp"),documentElement:{style:{setProperty(){}}},body:{style:{},classList:{add(){},remove(){},toggle(){}},appendChild(){}},querySelectorAll:()=>[]};
globalThis.window={devicePixelRatio:1,addEventListener(){},removeEventListener(){},localStorage:{_d:{},getItem(){return null;},setItem(){}}};
globalThis.location={href:"https://eda.test/",search:"",origin:"https://eda.test"};
globalThis.navigator={getGamepads:()=>[]}; globalThis.requestAnimationFrame=()=>{}; globalThis.console.info=()=>{};
let posted=null;
globalThis.fetch=async(u,o)=>{ if(o&&o.method==="POST") posted=JSON.parse(o.body); return {ok:true,json:async()=>({})}; };
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));

(async()=>{
  EDA.user.name="booth-laptop-3"; EDA.fabric={nodes:[{},{},{}],links:[]};
  for(const name of ["A","COLIN","CHRISTOPHE"]){
    posted=null;
    await EDA.postScore(name, 4321, 12, "hez");
    const spec=posted && posted.spec;
    ok(!!spec, `game posted a SnakeScore for ${name}`);
    for(const k of Object.keys(spec))
      ok(k in fields, `posted field "${k}" is declared in the CRD`);
    for(const [k,f] of Object.entries(fields))
      if(f.required) ok(k in spec && spec[k]!=="" && spec[k]!=null, `required field "${k}" is sent`);
    for(const [k,f] of Object.entries(fields)){
      if(f.pattern && k in spec) ok(f.pattern.test(spec[k]), `"${k}"=${JSON.stringify(spec[k])} matches ${f.pattern}`);
      if(f.enum && k in spec)    ok(f.enum.includes(spec[k]), `"${k}"=${spec[k]} is one of ${f.enum.join("/")}`);
    }
  }
  ok(posted.spec.player==="CHRISTOPHE" && posted.spec.edaUser==="booth-laptop-3",
     "player = typed name, edaUser = EDA login, never mixed up");
  ok(!/initials/.test(go.split('type SnakeScoreSpec')[1].split('\n}')[0]),
     "the CRD no longer declares an initials field");
  ok(!/Rank|Accepted/.test(go.split('type SnakeScoreStatus struct {')[1].split('}')[0]),
     "status no longer has the always-empty rank/accepted fields");

  console.log(issues.length?"\n"+issues.length+" FAILURES":"\ncontract holds: game and CRD agree");
  process.exit(issues.length?1:0);
})();
