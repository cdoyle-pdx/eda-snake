/* v1.1.0: 10-letter names, soundtrack complete by level 5, medal-pace head
   colours, and gold/silver/bronze ranks on the board. */
const fs=require('fs');
let issues=[];
const ok=(c,m)=>{ if(!c){issues.push(m);console.log("FAIL:",m);} else console.log("ok:",m); };

const mk=()=>new Proxy({},{get:(t,p)=>{ if(p in t) return t[p]; if(p==='canvas') return {}; return ()=>{}; },
                           set:(t,p,v)=>{t[p]=v;return true;}});
const OV={innerHTML:"",classList:{add(){},remove(){},toggle(){}},style:{}};
const made={};
const el=(id)=>{ if(id==="overlay") return OV;
  if(!made[id]) made[id]={style:{setProperty(){}},classList:{add(){},remove(){},toggle(){}},
    textContent:'',innerHTML:'',appendChild(){},onclick:null,getContext:mk,width:0,height:0,addEventListener(){}};
  return made[id]; };
globalThis.document={getElementById:el,createElement:()=>el("tmp"),
  documentElement:{style:{setProperty(){}}},
  body:{style:{},classList:{add(){},remove(){},toggle(){}},appendChild(){}},querySelectorAll:()=>[]};
globalThis.window={devicePixelRatio:1,addEventListener(){},removeEventListener(){},
  localStorage:{_d:{},getItem(k){return this._d[k]||null;},setItem(k,v){this._d[k]=v;}}};
globalThis.location={href:"https://eda.test/core/httpproxy/v1/snake/",search:"",origin:"https://eda.test"};
globalThis.navigator={getGamepads:()=>[]};
globalThis.requestAnimationFrame=()=>{};
globalThis.console.info=()=>{};
globalThis.fetch=async()=>{throw new Error("offline");};
(0,eval)(fs.readFileSync('eda_globals.js','utf8'));

// ───────────── 1. soundtrack complete by level 5 ─────────────
const INSTR=["kick","bass","arp","hat","pad","snare","lead"];
function heard(level){
  const got=new Set(); const fired={};
  const saved={};
  for(const k of INSTR){ saved[k]=Music[k]; Music[k]=function(){ got.add(k); fired[k]=(fired[k]||0)+1; }; }
  const prev={level:Music.level, muted:Music.muted, onBeat:Music.onBeat};
  Music.level=level; Music.muted=false; Music.onBeat=null;
  for(let s=0;s<64;s++) Music.schedule(s,0);
  Object.assign(Music,prev);
  for(const k of INSTR) Music[k]=saved[k];
  return {got,fired};
}
const L1=heard(1), L5=heard(5), L20=heard(20);
ok([...L1.got].join()==="kick", "level 1 is kick only: "+[...L1.got].join());
ok(INSTR.every(k=>L5.got.has(k)), "every layer is playing by level 5: "+[...L5.got].join());
ok(JSON.stringify(L5.fired)===JSON.stringify(L20.fired),
   "level 20 adds nothing over level 5 (same arrangement, only tempo rises)");
let monotone=true, prevSet=new Set();
for(let L=1;L<=20;L++){ const g=heard(L).got; for(const k of prevSet) if(!g.has(k)) monotone=false; prevSet=g; }
ok(monotone, "layers only ever add as levels rise, never drop out");
const counts=[1,2,3,4,5].map(L=>heard(L).got.size);
ok(counts.every((c,i)=>i===0||c>counts[i-1]), "each of levels 1-5 adds something new: "+counts.join("→"));
ok(heard(5).fired.arp===64 && heard(4).fired.arp===32, "level 5 doubles the arp to 16ths");

// ───────────── 2. medal pace ─────────────
const setBoard=(scores)=>{ Board.list=scores.map((s,i)=>({name:"P"+i,score:s})); };
setBoard([]);
ok(projectedRank(0)===0,   "score 0 never ranks (no medal for just starting)");
ok(projectedRank(5)===1,   "empty board: any points rank 1st");
setBoard([900,500,300,100]);
ok(medalRank(50)===0,      "below 4th place: no medal");
ok(medalRank(101)===0,     "beating 4th makes you 4th: still no medal");
ok(medalRank(300)===0,     "TYING 3rd doesn't pass them (earlier run wins ties)");
ok(medalRank(301)===3,     "one point past 3rd -> bronze");
ok(medalRank(501)===2,     "past 2nd -> silver");
ok(medalRank(900)===2,     "tying 1st is still silver");
ok(medalRank(901)===1,     "past 1st -> gold");
setBoard([400]);
ok(medalRank(10)===2,      "one entry on the board: any score is on pace for 2nd");

// popups fire on improvement only
setBoard([900,500,300]);
G.snake=[{x:5,y:5}]; G.cols=15; G.rows=11; G.popups=[]; G.medal=0; G.score=0;
let sfx=0; const realSfx=Music.sfx; Music.sfx=()=>{sfx++;};
G.score=320; updateMedal();
ok(G.medal===3 && G.popups.length===1 && G.popups[0].label==="BRONZE PACE", "bronze announced on reaching it");
ok(G.popups[0].color===MEDALS[3].mid, "medal popup carries its medal colour");
G.score=330; updateMedal();
ok(G.popups.length===1, "no repeat announcement while staying bronze");
G.score=950; updateMedal();
ok(G.medal===1 && G.popups[1].label==="GOLD PACE", "jumping straight to gold announces gold");
G.score=600; updateMedal();
ok(G.medal===2 && G.popups.length===2, "dropping gold->silver is silent (a stolen letter isn't celebrated)");
G.score=950; updateMedal();
ok(G.popups.length===3 && G.popups[2].label==="GOLD PACE", "regaining gold is announced again");
Music.sfx=realSfx;

// steal path updates the medal
ok(/G\.score=Math\.max\(0, G\.score-pen\);[\s\S]{0,200}updateMedal\(\)/.test(fs.readFileSync('check-eda.js','utf8')),
   "a stolen letter re-evaluates the medal");
ok(/G\.score=0; G\.medal=0;/.test(fs.readFileSync('check-eda.js','utf8')), "a new run starts with no medal");

// ───────────── 3. leaderboard rank colours ─────────────
Board.backend="local"; Board.lastIdx=-1;
setBoard([900,500,300,100,50]);
Board.render();
const html=el("sideBoard").innerHTML;
const rows=[...html.matchAll(/<div class="([^"]+)"><span class="rk">(\d+)<\/span>/g)].map(m=>[m[2],m[1]]);
ok(rows[0][1]==="row r1" && rows[1][1]==="row r2" && rows[2][1]==="row r3", "ranks 1-3 get r1/r2/r3: "+rows.slice(0,3).map(r=>r[1]).join(" | "));
ok(rows[3][1]==="row" && rows[4][1]==="row", "rank 4+ is uncoloured");
setBoard([900]); Board.render();
const rows2=[...el("sideBoard").innerHTML.matchAll(/<div class="([^"]+)"><span class="rk">(\d+)<\/span>/g)].map(m=>m[1]);
ok(rows2[0]==="row r1" && rows2[1]==="row" && rows2[2]==="row", "empty placeholder slots 2-3 are NOT medal-coloured");
setBoard([900,500,300]); Board.lastIdx=0; Board.render();
ok(/class="row new r1"/.test(el("sideBoard").innerHTML), "a freshly-added #1 is both new and gold");
const css=fs.readFileSync('nokia-snake-eda.html','utf8');
ok(css.indexOf("#sideBoard .row.r1{")>css.indexOf("body:not(.darkui) #sideBoard .row.new{"),
   "medal rules come after .new so a new top-3 entry still shows its medal colour");
ok(/body:not\(\.darkui\) #sideBoard \.row\.r1\{color:#A8780A\}/.test(css), "darker gold for the light (white) levels");

// ───────────── 4. 10-letter name entry ─────────────
let added=null; const realAdd=Board.add; Board.add=(n,s)=>{added=n;};
globalThis.showMenu=()=>{};     // the real one rebuilds the arena; not under test here
EDA.user={name:"",endpoint:null,canReset:true,canPlay:true}; EDA.online=false;
G.score=1234;

showEntry("Game over");
ok(G.entry.chars.length===10, "ten slots");
ok(entryName(G.entry)==="A", "no username: starts on a single A");
"COLINDOYLE".split("").forEach(c=>{ if(G.entry.slot===0&&entryName(G.entry)==="A") {} entryType(c); });
ok(entryName(G.entry)==="CCOLINDOYL" || entryName(G.entry).length===10, "typing fills up to 10: "+entryName(G.entry));
entryType("X");
ok(entryName(G.entry).length===10, "an 11th letter overwrites the last slot rather than growing the name");

showEntry("Game over");
entryBackspace();
ok(entryName(G.entry)==="", "backspace clears the A");
entryConfirm();
ok(added===null && G.entry.empty===true, "empty name can't be saved");
ok(/enter at least one letter/.test(OV.innerHTML), "and says why");
"SNAKE".split("").forEach(entryType);
entryConfirm();
ok(added==="SNAKE", "typed name saved: "+added);

added=null; showEntry("Game over");          // ▲▼ from a blank wraps sensibly
G.entry.slot=1; entryNav({x:0,y:-1});
ok(AZ[G.entry.chars[1]]==="A", "▲ on a blank slot gives A");
entryNav({x:0,y:-1}); entryNav({x:0,y:1}); entryNav({x:0,y:1});
ok(G.entry.chars[1]===BLANK, "▼ from A returns to blank");
entryNav({x:0,y:1});
ok(AZ[G.entry.chars[1]]==="Z", "▼ from blank gives Z");
for(let i=0;i<20;i++) entryNav({x:1,y:0});
ok(G.entry.slot===9, "◀▶ is bounded to the 10 slots");

showEntry("Game over");                       // gap in the middle closes up
["C","O","L"].forEach(entryType); G.entry.slot=1; G.entry.chars[1]=BLANK;
entryConfirm();
ok(added==="CL", "a blanked middle slot closes the gap: "+added);

EDA.user.name="admin"; EDA.online=true;
showEntry("Game over");
ok(entryName(G.entry)==="ADMIN" && G.entry.prefilled, "prefilled from the token username");
ok(G.entry.slot===5, "cursor lands after the prefill, ready to keep typing");
entryConfirm();
ok(added==="ADMIN", "Enter saves the prefill in one press");

EDA.user.name="Christopher.Montgomery";
ok(nameFromUser()==="CHRISTOPHE", "long usernames are cut at 10 letters");
EDA.user.name="o'brien-smith 2";
ok(nameFromUser()==="OBRIENSMIT", "punctuation and digits dropped");

// what reaches the API must satisfy the widened CRD and a Kubernetes name
const PATTERN=/^[A-Z]{1,10}$/;
for(const n of ["A","SNAKE","CHRISTOPHE","ADMIN"]){
  const crName=`score-${Date.now()}-${n.toLowerCase()}`;
  ok(PATTERN.test(n) && /^[a-z0-9]([-a-z0-9]*[a-z0-9])?$/.test(crName) && crName.length<=63,
     `"${n}" passes ^[A-Z]{1,10}$ and makes a valid CR name (${crName.length} chars)`);
}
Board.add=realAdd;

console.log(issues.length?"\n"+issues.length+" FAILURES":"\nall v1.1.0 checks passed");
process.exit(issues.length?1:0);
