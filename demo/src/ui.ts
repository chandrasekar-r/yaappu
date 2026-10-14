export const CSS = String.raw`
:root{--bg:#f7f5f0;--fg:#1d1b18;--muted:#6b665d;--card:#fff;--line:#e6e1d6;--acc:#b5482a;--acc2:#2f6f6a;--ner:#e7f0ff;--nerb:#3d6fd1;--nir:#fff1dd;--nirb:#c27a12;--ok:#167a3e;--bad:#c0262d;--sh:0 1px 2px rgba(0,0,0,.05),0 8px 24px rgba(0,0,0,.05)}
[data-theme=dark]{--bg:#121212;--fg:#ece8e1;--muted:#a19b90;--card:#1c1b19;--line:#2e2c28;--acc:#ff8a65;--acc2:#6cc5bd;--ner:#1b2a45;--nerb:#7aa5ff;--nir:#3a2a12;--nirb:#f0b357;--ok:#4cc77e;--bad:#ff6b70;--sh:none}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Inter,"Mukta Malar",system-ui,sans-serif;transition:background .2s,color .2s}
.ta,[lang=ta] .kural{font-family:"Mukta Malar","Noto Serif Tamil",sans-serif}
a{color:var(--acc)}main{max-width:1040px;margin:0 auto;padding:0 20px 40px}
.top{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:20px;padding:12px 20px;background:color-mix(in srgb,var(--bg) 85%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.brand{font-weight:700;font-size:1.15rem;text-decoration:none;color:var(--fg)}.brand .ta{font-family:"Noto Serif Tamil",serif;color:var(--acc);margin-right:4px}
.top nav{display:flex;gap:4px;flex:1;overflow-x:auto}.top nav a{padding:6px 12px;border-radius:999px;text-decoration:none;color:var(--muted);font-weight:600;white-space:nowrap}
.top nav a[aria-current]{background:var(--card);color:var(--fg);box-shadow:var(--sh)}
.icon{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;width:38px;height:38px;font-size:1.1rem;cursor:pointer}
.hero{padding:56px 0 28px;text-align:center}.hero.sm{padding:40px 0 16px}
.hero h1{font-size:clamp(1.8rem,4.5vw,3rem);line-height:1.2;margin:0 0 12px;letter-spacing:-.02em}.hero h1 .ta{font-family:"Noto Serif Tamil",serif;color:var(--acc)}
.lead{font-size:1.15rem;color:var(--muted);max-width:680px;margin:0 auto}.stat{margin-top:14px;color:var(--muted)}.stat b{color:var(--acc2);font-size:1.2rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:var(--sh)}
.lbl{display:block;font-weight:600;margin-bottom:8px}
textarea,input[type=search]{width:100%;font-size:1.2rem;line-height:1.7;padding:12px 14px;border-radius:12px;border:1px solid var(--line);background:var(--bg);color:var(--fg);resize:vertical}
textarea:focus,input:focus{outline:2px solid var(--acc2);outline-offset:1px}
.row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;align-items:center}
button{font:inherit;cursor:pointer;border-radius:999px;padding:8px 16px;border:1px solid var(--line);background:var(--card);color:var(--fg);font-weight:600}
button.primary{background:var(--acc);border-color:var(--acc);color:#fff}button:hover{filter:brightness(1.05)}
.tog{margin-left:auto;color:var(--muted);font-size:.9rem;display:flex;gap:6px;align-items:center}
#out{margin-top:20px}.verdict{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:12px;margin-bottom:16px}
.verdict.ok{background:color-mix(in srgb,var(--ok) 12%,transparent);color:var(--ok)}.verdict.bad{background:color-mix(in srgb,var(--bad) 12%,transparent);color:var(--bad)}
.verdict b{font-size:1.1rem}.verdict p{margin:4px 0 0;color:var(--fg)}.verdict small{color:var(--muted)}
.line{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:10px 0}
.seer{border:1px solid var(--line);border-radius:14px;padding:10px 12px;background:var(--bg);min-width:96px;text-align:center}
.seer.badseer{border-color:var(--bad);box-shadow:0 0 0 2px color-mix(in srgb,var(--bad) 25%,transparent)}
.seer .w{font-family:"Mukta Malar",sans-serif;font-size:1.25rem;font-weight:600}
.seer .n{font-family:"Noto Serif Tamil",serif;color:var(--acc2);font-size:.95rem;margin-top:4px}
.chips{display:flex;gap:4px;justify-content:center;margin-top:6px;flex-wrap:wrap}
.chip{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 8px;border-radius:999px;letter-spacing:.02em}
.chip.ner{background:var(--ner);color:var(--nerb)}.chip.nirai{background:var(--nir);color:var(--nirb)}
.lk{font-weight:800;font-size:1rem;width:22px;text-align:center}.lk.ok{color:var(--ok)}.lk.bad{color:var(--bad)}.lk.na{color:var(--muted)}
.legend{margin:18px 0;color:var(--muted);font-size:.9rem;text-align:center}
.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;position:sticky;top:64px;z-index:4}.tools input{flex:1;min-width:220px}
.seg{display:flex;border:1px solid var(--line);border-radius:999px;overflow:hidden}.seg button{border:0;border-radius:0;background:transparent}.seg button.on{background:var(--acc2);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin-top:8px}
.kcard{padding:16px}.kcard .top2{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.num{font-weight:700;color:var(--muted)}.kural{font-size:1.15rem;line-height:1.75;margin:4px 0 8px}
.badge{font-size:.75rem;font-weight:700;padding:3px 10px;border-radius:999px}.badge.ok{background:color-mix(in srgb,var(--ok) 15%,transparent);color:var(--ok)}.badge.bad{background:color-mix(in srgb,var(--bad) 15%,transparent);color:var(--bad)}.badge.fix{background:color-mix(in srgb,var(--acc) 15%,transparent);color:var(--acc);margin-left:4px}
.mini{font-size:.8rem;color:var(--muted)}.kcard button{font-size:.8rem;padding:4px 12px}
.pager{display:flex;justify-content:center;gap:6px;margin-top:20px;flex-wrap:wrap}.pager button.on{background:var(--acc2);color:#fff}
.muted{color:var(--muted)}.small{font-size:.85rem}
.glist{display:grid;gap:16px}.gcard h3{margin:0 0 10px;font-size:1.15rem}.gpair{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.gcol{border-radius:12px;padding:12px 14px;background:var(--bg);border:1px solid var(--line)}.gcol.c{border-color:color-mix(in srgb,var(--acc2) 50%,var(--line))}
.ghead{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:.85rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.prose{max-width:760px;margin:0 auto}.prose pre{background:var(--bg);padding:12px;border-radius:10px;overflow-x:auto}
footer{text-align:center;color:var(--muted);padding:30px;font-size:.85rem}
@media (max-width:640px){.top{gap:6px;padding:8px 10px}.brand{font-size:.95rem}.top nav a{padding:5px 8px;font-size:.85rem}.icon{width:34px;height:34px}.hero{padding:32px 0 18px}.gpair{grid-template-columns:1fr}.tog{margin-left:0}.seer{min-width:80px;padding:8px}.seer .w{font-size:1.1rem}.tools{top:58px}main{padding:0 12px 30px}}
`;

export const JS = String.raw`
(()=>{const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
$('#theme').onclick=()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;localStorage.theme=t};
const page=document.body.dataset.page;
function render(r){const a=r.analysis||{seers:[],links:[]};const S=a.seers;let bad=-1;const m=(r.detail||'').match(/seer(\d)/);if(m)bad=+m[1]-1;
 const seer=(s,i)=>'<div class="seer'+(i===bad?' badseer':'')+'"><div class="w">'+esc(s.word)+'</div><div class="chips">'+(s.asai?s.asai.map(x=>'<span class="chip '+(x==='bu'?'ner':x)+'">'+x+'</span>').join(''):'<span class="chip" style="color:var(--bad)">?</span>')+'</div><div class="n">'+esc(s.name||'—')+'</div></div>';
 const link=i=>{const v=a.links[i];return '<span class="lk '+(v===true?'ok':v===false?'bad':'na')+'" title="venthalai">'+(v===true?'✓':v===false?'✗':'·')+'</span>'};
 let lines='';if(S.length){const cut=S.length===7?4:Math.ceil(S.length/2);const L=(from,to)=>{let h='';for(let i=from;i<to;i++){h+=seer(S[i],i);if(i<to-1)h+=link(i)}return h};
  lines='<div class="line">'+L(0,cut)+'</div>'+(cut<S.length?'<div class="line">'+link(cut-1)+L(cut,S.length)+'</div>':'')}
 $('#out').innerHTML='<div class="verdict '+(r.ok?'ok':'bad')+'"><div><b>'+(r.ok?'✓ Valid kural venba':'✗ Not a valid kural venba')+'</b>'+(r.ok?'<p>'+esc((r.seers||[]).join(' · '))+'</p>':'<p>'+esc(a.explain)+'</p>')+(r.detail?'<small>'+esc(r.detail)+'</small>':'')+'</div></div>'+lines}
async function run(){const t=$('#kt').value.trim();if(!t){$('#out').innerHTML='';return}const r=await fetch('/api/check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:t,mode:$('#lic').checked?'licensed':'base'})}).then(x=>x.json());render(r);history.replaceState(null,'','#'+encodeURIComponent(t))}
if(page==='/'){const EX=['அகர முதல எழுத்தெல்லாம் ஆதி\nபகவன் முதற்றே உலகு.','அகர முதல எழுத்தெல்லாம் ஆதி\nபகவன் கருவிளங்கனி உலகு.','அஃகாமை செல்வத்திற்கு யாதெனின் வெஃகாமை\nவேண்டும் பிறன்கைப் பொருள்.'];
 $('#go').onclick=run;$('#lic').onchange=run;document.querySelectorAll('.ex').forEach(b=>b.onclick=()=>{$('#kt').value=EX[+b.dataset.ex];run()});
 $('#kt').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.metaKey||e.ctrlKey))run()});
 const h=decodeURIComponent(location.hash.slice(1));$('#kt').value=h||EX[0];run()}
if(page==='/corpus'){let D=[],f='all',q='',p=0;const PER=24;
 const draw=()=>{const ql=q.trim();let R=D.filter(k=>f==='all'||(f==='pass'?k.ok:f==='fail'?!k.ok:!!k.raw));
  if(ql)R=R.filter(k=>String(k.n)===ql||(k.l1+' '+k.l2+' '+(k.raw||'')).includes(ql));
  const pages=Math.max(1,Math.ceil(R.length/PER));p=Math.min(p,pages-1);$('#count').textContent=R.length+' kurals'+(ql?' matching “'+ql+'”':'');
  $('#grid').innerHTML=R.slice(p*PER,p*PER+PER).map(k=>'<article class="card kcard"><div class="top2"><span class="num">#'+k.n+'</span><span><span class="badge '+(k.ok?'ok':'bad')+'">'+(k.ok?'✓ pass':'✗ '+esc(k.error))+'</span>'+(k.raw?'<span class="badge fix" title="'+esc('source: '+k.raw)+'">corrected</span>':'')+'</span></div><p class="kural ta">'+esc(k.l1)+'<br>'+esc(k.l2)+'</p><div class="mini">'+esc(k.ok?k.seers.join(' · '):k.detail)+'</div>'+(k.raw?'<div class="mini">raw: <span class="ta">'+esc(k.raw.replace('\n',' / '))+'</span></div>':'')+'<div class="row"><a href="/#'+encodeURIComponent(k.l1+'\n'+k.l2)+'"><button>Open in checker</button></a></div></article>').join('')||'<p class="muted">No matches.</p>';
  let pg='';const btn=(i,l)=>'<button data-p="'+i+'"'+(i===p?' class="on"':'')+'>'+l+'</button>';if(pages>1){if(p>0)pg+=btn(p-1,'‹');for(let i=Math.max(0,p-2);i<Math.min(pages,p+3);i++)pg+=btn(i,i+1);if(p<pages-1)pg+=btn(p+1,'›')}
  $('#pager').innerHTML=pg+(pages>1?'<span class="muted small" style="align-self:center">page '+(p+1)+' / '+pages+'</span>':'');
  document.querySelectorAll('#pager button').forEach(b=>b.onclick=()=>{p=+b.dataset.p;draw();scrollTo({top:0,behavior:'smooth'})})};
 $('#q').oninput=e=>{q=e.target.value;p=0;draw()};document.querySelectorAll('#flt button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#flt button').forEach(x=>x.classList.remove('on'));b.classList.add('on');f=b.dataset.f;p=0;draw()});
 fetch('/api/corpus').then(r=>r.json()).then(d=>{D=d;draw()})}
})();
`;
