const CITIES={Ibadan:[7.38,3.95],Kano:[12.0,8.52],Kaduna:[10.52,7.44],Abuja:[9.06,7.49],Enugu:[6.46,7.55],Makurdi:[7.73,8.52],Ilorin:[8.5,4.55],"Lagos":[6.52,3.38],"Port Harcourt":[4.82,7.05],"Benin City":[6.34,5.63],"Abeokuta":[7.16,3.35],"Akure":[7.25,5.19],"Osogbo":[7.77,4.56],"Owerri":[5.48,7.03],"Calabar":[4.95,8.33],"Minna":[9.61,6.55],"Jos":[9.9,8.86],"Yola":[9.2,12.48],"Maiduguri":[11.85,13.16],"Sokoto":[13.06,5.24]};
const SAMPLE={
Ibadan:{rain:[0,12,18,6,0,9,14],pop:[20,65,80,50,15,45,70],hi:[32,31,30,31,33,32,31],lo:[22,22,22,22,23,22,22]},
Kano:{rain:[0,0,0,0,2,0,0],pop:[5,5,10,10,25,5,5],hi:[36,37,38,37,36,37,38],lo:[22,23,24,23,23,23,24]},
Kaduna:{rain:[0,0,4,0,0,0,3],pop:[10,15,40,10,10,10,35],hi:[35,36,37,36,37,38,36],lo:[21,22,23,22,22,23,22]},
Abuja:{rain:[8,14,6,0,12,10,5],pop:[55,70,50,20,60,55,40],hi:[31,30,31,32,30,31,32],lo:[22,22,21,22,22,22,22]},
Enugu:{rain:[15,22,10,18,6,0,12],pop:[75,80,60,75,50,20,65],hi:[30,29,30,29,31,32,30],lo:[22,22,22,22,22,22,22]},
Makurdi:{rain:[2,64,38,22,9,5,0],pop:[30,95,90,80,55,40,15],hi:[32,28,28,29,31,32,33],lo:[23,22,22,22,22,22,23]},
Ilorin:{rain:[5,10,0,15,8,0,20],pop:[40,55,20,65,50,15,70],hi:[33,31,32,30,31,33,30],lo:[22,22,22,22,22,22,22]}};
const CROPS={maize:{n:'Maize',need:25,over:45,yo:'àgbàdo',ha:'masara'},cassava:{n:'Cassava',need:15,over:50,yo:'gbágùdá',ha:'rogo'},rice:{n:'Rice',need:45,over:80,yo:'ìrẹsì',ha:'shinkafa'},tomato:{n:'Tomato',need:20,over:35,yo:'tòmátò',ha:'tumatir'}};
const MSG={
en:{plant:'Good rain is coming. Plant {c} from today.',wait:'Heavy rain is coming. Wait {n} days before planting {c}.',dry:'Rain will be too low this week. Delay planting {c} or irrigate if you can.'},
pcm:{plant:'Good rain dey come. You fit plant {c} from today.',wait:'Heavy rain dey come. Wait {n} days before you plant {c}.',dry:'Rain no go reach this week. Delay to plant {c} or water am if you fit.'},
yo:{plant:'Òjò rere ń bọ̀. Ẹ lè gbin {c} láti òní.',wait:'Òjò ńlá ń bọ̀. Ẹ dúró ọjọ́ {n} kí ẹ tó gbin {c}.',dry:'Òjò kò ní tó ní ọ̀sẹ̀ yìí. Ẹ dádúró gbígbin {c}, tàbí kí ẹ bomi rin ín.'},
ha:{plant:'Ruwan sama mai kyau na zuwa. Ku shuka {c} daga yau.',wait:'Ruwan sama mai yawa na zuwa. Ku jira kwana {n} kafin ku shuka {c}.',dry:'Ruwan sama ba zai isa a wannan mako ba. Ku jinkirta shuka {c} ko ku yi ban ruwa.'}};
const st={city:'Ibadan',crop:'maize',lang:'en',tab:'today'};
let D=null,A=null,W=null,last='';
const dl=i=>i==0?'today':i==1?'tomorrow':new Date(Date.now()+i*864e5).toLocaleDateString('en-GB',{weekday:'long'});
const ds=i=>i==0?'Today':new Date(Date.now()+i*864e5).toLocaleDateString('en-GB',{weekday:'short'});
const R=Math.round;
function judge(d,c){
 const sum=d.rain.reduce((a,b)=>a+b,0),hv=d.rain.findIndex((r,i)=>i<3&&r>=c.over);
 if(hv>-1){let n=hv+1;while(n<7&&d.rain[n]>=c.over/2)n++;return{k:'wait',n,why:`Heavy rain of ${R(d.rain[hv])} mm is forecast ${dl(hv)}. It could wash the seeds away.`}}
 if(sum<c.need)return{k:'dry',n:0,why:`Only ${R(sum)} mm of rain is forecast this week. ${c.n} needs about ${c.need} mm.`};
 return{k:'plant',n:0,why:`${R(sum)} mm of steady rain is forecast this week, with no flood-level downpour.`};
}
function alerts(d){
 const a=[];
 d.rain.forEach((r,i)=>{if(r>=40)a.push(`Flood risk: ${R(r)} mm of rain ${dl(i)}.`)});
 let run=0,mx=0;d.rain.forEach(r=>{run=r<1?run+1:0;mx=Math.max(mx,run)});
 if(mx>=4)a.push(`Dry spell: ${mx} days in a row with almost no rain.`);
 if(Math.max(...d.hi)>=36)a.push(`Heat: up to ${R(Math.max(...d.hi))}°C. Water crops early in the morning.`);
 return a;
}
function home(){
 const c=CROPS[st.crop],sum=D.rain.reduce((x,y)=>x+y,0);
 let j=judge(D,c),a=alerts(D);
 const cn=st.lang=='yo'?c.yo:st.lang=='ha'?c.ha:c.n.toLowerCase();
 last=`PlantWise ${st.city}: `+MSG[st.lang][j.k].replace('{c}',cn).replace('{n}',j.n);
 if(A){j={k:A.verdict,n:A.days_to_wait,why:A.reason};a=A.alerts;last=A.message}
 const title={plant:`Plant ${c.n.toLowerCase()} now`,wait:`Wait ${j.n} days to plant`,dry:'Too dry: delay or irrigate'}[j.k];
 const n=W&&W.current,temp=n?n.temp:D.hi[0],cond=n?n.label:'Forecast high';
 const now=new Date().toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short',year:'numeric'});
 return `<section class="hero">
 <div class="hr1"><span class="loc"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>${st.city}, Nigeria</span><span class="cond">${cond}</span></div>
 <div class="hr2"><b>${R(temp)}°C</b><small>${now}</small></div>
 <div class="hr3"><div><small>Humidity</small><b>${n?R(n.humidity)+'%':'–'}</b></div><div><small>Precipitation</small><b>${R(D.rain[0])} mm</b></div><div><small>Wind</small><b>${n?R(n.wind)+' km/h':'–'}</b></div></div></section>
 <div class="sec"><h3>My Crops</h3><a onclick="go('crops')">See all</a></div>
 <div class="chips">${Object.keys(CROPS).map(k=>`<button class="chip${k==st.crop?' on':''}" onclick="pick('crop','${k}')">${CROPS[k].n}</button>`).join('')}</div>
 <div class="card verdict"><small>Today’s advice</small><h2>${title}</h2><p>${j.why}</p></div>
 <div class="stats"><div><b>${R(D.hi[0])}°C</b>High today</div><div><b>${R(sum)} mm</b>Rain this week</div><div><b>${D.pop[0]}%</b>Rain chance today</div></div>
 ${a.length?a.map(x=>`<div class="alert">${x}</div>`).join(''):'<div class="calm">No weather alerts this week.</div>'}
 <h3>Message for farmers</h3><div class="bubble" id="msg">${last}</div>
 <button class="btn" id="cp" onclick="copyMsg()">Copy message</button>
 <p class="note">Send this by SMS or WhatsApp. Change the language in Settings.</p>`;
}
function crops(){
 const lbl={plant:'Plant now',wait:'Wait',dry:'Too dry'},cls={plant:'p',wait:'w',dry:'d'};
 return `<div class="sec"><h3>My Crops</h3></div>`+Object.keys(CROPS).map(k=>{
  const c=CROPS[k],j=judge(D,c);
  return `<div class="card crop"><div class="cr1"><span class="av">${c.n[0]}</span><div><b>${c.n}</b><small>${st.city}</small></div><span class="pill ${cls[j.k]}">${j.k=='wait'?'Wait '+j.n+' days':lbl[j.k]}</span></div><p>${j.why}</p><button class="btn" onclick="pick('crop','${k}');go('today')">View advice</button></div>`}).join('');
}
function week(){
 return `<div class="card">${D.rain.map((r,i)=>`<div class="row"><b>${ds(i)}</b><div class="bar"><i style="width:${Math.min(100,r*100/40)}%"></i></div><span>${R(r)} mm · ${R(D.hi[i])}°/${R(D.lo[i])}° · ${D.pop[i]}%</span></div>`).join('')}</div>
 <p class="note">Bars show rain per day. Right side: rain, high/low temperature, chance of rain.</p>`;
}
function sets(){
 const o=(obj,v,f)=>Object.keys(obj).map(k=>`<option value="${k}"${k==v?' selected':''}>${f(k)}</option>`).join('');
 const L={en:'English',pcm:'Nigerian Pidgin',yo:'Yorùbá',ha:'Hausa'};
 return `<label>Town or city</label><select onchange="pick('city',this.value)">${o(CITIES,st.city,k=>k)}</select>
 <label>Crop</label><select onchange="pick('crop',this.value)">${o(CROPS,st.crop,k=>CROPS[k].n)}</select>
 <label>Message language</label><select onchange="pick('lang',this.value)">${o(L,st.lang,k=>L[k])}</select>
 <h3>Daily alerts on WhatsApp</h3>
 <input id="ph" type="tel" placeholder="2348012345678" autocomplete="tel">
 <button class="btn" onclick="subscribe()">Get daily alerts</button>
 <p class="note" id="ps">Use your WhatsApp number with country code. Reply STOP any time to stop.</p>
 <p class="note">Weather and advice come from the PlantWise server (Open-Meteo data). If it can’t be reached, the app shows sample data and says so in the top corner. Local-language messages should be checked by native speakers before real use.</p>`;
}
function render(){
 document.getElementById('bd').textContent=D.live?'Live weather':'Sample data';
 const mm=document.getElementById('m');mm.innerHTML={today:home,ore,week,crops,set:sets}[st.tab]();if(st.tab=='ore')mm.scrollTop=mm.scrollHeight;
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on',b.dataset.t==st.tab));
}
async function load(){
 if(!D||D.city!==st.city){D={...(SAMPLE[st.city]||SAMPLE.Ibadan),live:false,city:st.city};A=null;W=null}
 render();
 const city=st.city,c=encodeURIComponent(city),q=`city=${c}&crop=${st.crop}&lang=${st.lang}`;
 const get=u=>fetch(API_BASE+u).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()});
 get(`/api/weather?city=${c}`).then(w=>{if(city==st.city){W=w;render()}}).catch(()=>{});
 try{
  const [x,y]=await Promise.all([get(`/api/forecast?city=${c}`),get(`/api/advice?${q}`)]);
  if(city==st.city){D={...x,live:true,city};A=y;render()}
 }catch(e){}
}
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let chat=[],busy=false;
function ore(){
 return `<div id="chat">${chat.length?chat.map(m=>`<div class="${m.role=='user'?'me':'bot'}">${esc(m.content)}</div>`).join(''):'<div class="bot">Hello, I’m Ore. Ask me about planting, rain or your farm. You can write in English, Pidgin, Yorùbá or Hausa.</div>'}${busy?'<div class="bot">…</div>':''}</div>
 <div class="ask"><input id="q" placeholder="Ask Ore…" onkeydown="if(event.key=='Enter')ask()"><button class="btn" onclick="ask()">Send</button></div>`;
}
async function ask(){
 const i=document.getElementById('q'),t=i.value.trim();if(!t||busy)return;
 const history=chat.slice();chat.push({role:'user',content:t});busy=true;render();
 try{
  const r=await fetch(API_BASE+'/api/ore',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t,history:history,city:st.city,crop:st.crop,lang:st.lang})});
  if(!r.ok)throw new Error(r.status);
  chat.push({role:'assistant',content:(await r.json()).reply});
 }catch(e){chat.push({role:'assistant',content:'I can’t reach my brain right now. Please try again.'})}
 busy=false;render();const q=document.getElementById('q');if(q)q.focus();
}
function go(t){st.tab=t;render()}
function pick(k,v){st[k]=v;load()}
function start(){document.getElementById('splash').style.display='none'}
async function openWx(){
 document.getElementById('wxc').innerHTML=Object.keys(CITIES).sort().map(k=>`<option${k==st.city?' selected':''}>${k}</option>`).join('');
 document.getElementById('wx').hidden=false;loadWx();
}
function closeWx(){document.getElementById('wx').hidden=true}
async function loadWx(){
 const c=document.getElementById('wxc').value,b=document.getElementById('wxb');
 b.innerHTML='<p class="note">Loading weather…</p>';
 try{
  const r=await fetch(`${API_BASE}/api/weather?city=${encodeURIComponent(c)}`);
  if(!r.ok)throw new Error(r.status);
  const w=await r.json();
  if(document.getElementById('wxc').value!==c)return;
  const n=w.current,d=w.daily;
  b.innerHTML=`<div class="wxnow"><div><b>${R(n.temp)}°C</b><span>${n.label}</span></div><small>${c}, Nigeria</small></div>
  <div class="stats"><div><b>${R(n.humidity)}%</b>Humidity</div><div><b>${R(n.wind)} km/h</b>Wind</div><div><b>${d.pop[0]}%</b>Rain chance today</div></div>
  <h3>Next 7 days</h3><div class="card">${d.rain.map((x,i)=>`<div class="row"><b>${ds(i)}</b><span class="lb">${d.label[i]}</span><span class="v">${R(d.hi[i])}°/${R(d.lo[i])}° · ${R(x)} mm</span></div>`).join('')}</div>`;
 }catch(e){
  if(document.getElementById('wxc').value===c)b.innerHTML='<div class="calm">Couldn’t load the weather. Check your connection and try again.</div><button class="btn" onclick="loadWx()">Try again</button>';
 }
}
document.addEventListener('keydown',e=>{if(e.key=='Escape')closeWx()});
async function subscribe(){
 const p=document.getElementById('ph').value,s=document.getElementById('ps');
 if(p.replace(/\D/g,'').length<10){s.textContent='Enter your full number with country code, for example 2348012345678.';return}
 try{
  const r=await fetch(API_BASE+'/api/farmers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:p,city:st.city,crop:st.crop,lang:st.lang})});
  s.textContent=r.ok?'Done. You will get daily advice on WhatsApp. Reply STOP any time to stop.':'Could not save your number. Please check it and try again.';
 }catch(e){s.textContent='Could not reach the server. Please try again.'}
}
async function copyMsg(){
 try{await navigator.clipboard.writeText(last);document.getElementById('cp').textContent='Copied'}
 catch(e){const r=document.createRange();r.selectNodeContents(document.getElementById('msg'));const s=getSelection();s.removeAllRanges();s.addRange(r);document.getElementById('cp').textContent='Message selected. Tap Copy.'}
}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{st.tab=b.dataset.t;render()});
load();
