/* NOAA raw TEMP decoder for TNCC (78988) Skew-T
   Live sources (mirrored hourly into sonde-latest.json for the PWA):
   TTAA https://tgftp.nws.noaa.gov/data/raw/us/usnu01.tncc..txt
   TTBB https://tgftp.nws.noaa.gov/data/raw/uk/uknu01.tncc..txt
   PPBB https://tgftp.nws.noaa.gov/data/raw/ug/ugnu01.tncc..txt
   TTCC https://tgftp.nws.noaa.gov/data/raw/ul/ulnu01.tncc..txt
   TTDD https://tgftp.nws.noaa.gov/data/raw/ue/uenu01.tncc..txt
   PPDD https://tgftp.nws.noaa.gov/data/raw/uq/uqnu01.tncc..txt
*/
const SONDE_NOAA_RAW={
  TTAA:'https://tgftp.nws.noaa.gov/data/raw/us/usnu01.tncc..txt',
  TTBB:'https://tgftp.nws.noaa.gov/data/raw/uk/uknu01.tncc..txt',
  PPBB:'https://tgftp.nws.noaa.gov/data/raw/ug/ugnu01.tncc..txt',
  TTCC:'https://tgftp.nws.noaa.gov/data/raw/ul/ulnu01.tncc..txt',
  TTDD:'https://tgftp.nws.noaa.gov/data/raw/ue/uenu01.tncc..txt',
  PPDD:'https://tgftp.nws.noaa.gov/data/raw/uq/uqnu01.tncc..txt'
};
function sondeLooksLikeTemp(text){
  const t=String(text||'');
  if(t.length<40) return false;
  if(/valid API key|AuthenticationRequired|AccessDenied/i.test(t)) return false;
  return /\b(TTAA|TTBB|TTCC|TTDD|PPBB|PPDD|78988|TNCC)\b/i.test(t);
}
async function sondeFetchOneNoaa(url){
  if(typeof fetchWithRetries==='function'){
    const o=await fetchWithRetries(url,2);
    if(o&&o.ok&&sondeLooksLikeTemp(o.text)) return o.text.trim();
  }
  const encoded=encodeURIComponent(url);
  const proxies=[
    'https://api.allorigins.win/raw?url='+encoded,
    'https://corsproxy.io/?url='+encoded
  ];
  for(const p of proxies){
    try{
      const r=await fetch(p,{cache:'no-store'});
      if(!r||!r.ok) continue;
      const t=await r.text();
      if(sondeLooksLikeTemp(t)) return t.trim();
    }catch(e){}
  }
  throw new Error('noaa fetch failed '+url);
}
function sondeTempGroups(text){
  return String(text||'').replace(/=\s*$/m,'').split(/\s+/).map(t=>t.replace(/=/g,'')).filter(t=>t.length===5);
}
function sondeTempT(ttt){
  if(!ttt||/[^0-9]/.test(ttt)) return null;
  const v=parseInt(ttt,10);
  const t=v/10;
  return (v%2)?-t:t;
}
function sondeTempDD(dd){
  if(!dd||/[^0-9]/.test(dd)) return null;
  const v=parseInt(dd,10);
  return v<=50?v/10:v-50;
}
function sondeTempWind(g){
  if(!g||g.length!==5||/[^0-9]/.test(g)) return {drct:null,sknt:null};
  let ddd=parseInt(g.slice(0,3),10), ff=parseInt(g.slice(3,5),10);
  const rem=ddd%5;
  if(rem===1){ ddd-=1; ff+=100; }
  else if(rem===2){ ddd-=2; ff+=200; }
  if(ddd>360) ddd-=360;
  if(!(ddd>=0&&ddd<=360&&ff>=0&&ff<300)) return {drct:null,sknt:null};
  return {drct:ddd,sknt:ff};
}
function sondeTempHeight(code,hhh,high){
  if(!hhh||/[^0-9]/.test(hhh)) return null;
  const h=parseInt(hhh,10);
  if(high){
    if(code==='70') return h*10+10000;
    if(code==='50') return h<500?h*10+20000:h*10+10000;
    if(code==='30'||code==='20') return h*10+20000;
    if(code==='10') return h<500?h*10+30000:h*10+20000;
  }
  if(code==='00') return h<500?h:-(h-500);
  if(code==='92') return h;
  if(code==='85') return h+1000;
  if(code==='70') return h<500?h+3000:h+2000;
  if(code==='50'||code==='40') return h*10;
  if(code==='30'||code==='25') return h<500?h*10+10000:h*10;
  if(code==='20'||code==='15'||code==='10') return h*10+10000;
  return null;
}
function sondeTempHeaderMeta(text){
  const m=String(text||'').match(/\b(\d{2})(\d{2})(\d{2})\b/);
  if(!m) return {day:null,hour:null};
  let day=parseInt(m[1],10), hour=parseInt(m[2],10);
  if(day>50) day-=50;
  if(day<1||day>31||hour>23) return {day:null,hour:null};
  return {day,hour};
}
function sondeTempMergeLevel(map,p,extra){
  if(!(isFinite(p)&&p>=10&&p<=1100)) return;
  const key=Math.round(p*10)/10;
  const prev=map.get(key)||{p:key,t:null,td:null,hgt:null,drct:null,sknt:null};
  for(const k of ['t','td','hgt','drct','sknt']){
    if(prev[k]==null&&extra[k]!=null) prev[k]=extra[k];
  }
  map.set(key,prev);
}
function parseTempAA(text,high){
  const groups=sondeTempGroups(text);
  const map=new Map();
  const mand=high
    ?{'70':70,'50':50,'30':30,'20':20,'10':10}
    :{'00':1000,'92':925,'85':850,'70':700,'50':500,'40':400,'30':300,'25':250,'20':200,'15':150,'10':100};
  let i=0;
  while(i<groups.length && !groups[i].startsWith('99') && !(groups[i].slice(0,2) in mand) && !groups[i].startsWith('88')) i++;
  if(!high && i<groups.length && groups[i].startsWith('99')){
    let p=parseInt(groups[i].slice(2),10); if(p<500) p+=1000;
    const t=groups[i+1]?sondeTempT(groups[i+1].slice(0,3)):null;
    const dd=groups[i+1]?sondeTempDD(groups[i+1].slice(3,5)):null;
    const w=groups[i+2]?sondeTempWind(groups[i+2]):{drct:null,sknt:null};
    sondeTempMergeLevel(map,p,{t,td:(t!=null&&dd!=null)?t-dd:null,drct:w.drct,sknt:w.sknt});
    i+=3;
  }
  while(i+1<groups.length){
    const g=groups[i];
    if(g.startsWith('88')||g.startsWith('77')||g.startsWith('66')||g==='31313'||g.startsWith('51')) break;
    const code=g.slice(0,2);
    if(!(code in mand)){ i++; continue; }
    const p=mand[code];
    const hgt=sondeTempHeight(code,g.slice(2,5),!!high);
    const t=groups[i+1]?sondeTempT(groups[i+1].slice(0,3)):null;
    const dd=groups[i+1]?sondeTempDD(groups[i+1].slice(3,5)):null;
    const w=groups[i+2]?sondeTempWind(groups[i+2]):{drct:null,sknt:null};
    sondeTempMergeLevel(map,p,{t,td:(t!=null&&dd!=null)?t-dd:null,hgt,drct:w.drct,sknt:w.sknt});
    i+=3;
  }
  while(i<groups.length){
    if(groups[i].startsWith('88') && groups[i]!=='88999'){
      let p=parseInt(groups[i].slice(2),10);
      if(high && p>150) p=p/10;
      const t=groups[i+1]?sondeTempT(groups[i+1].slice(0,3)):null;
      const dd=groups[i+1]?sondeTempDD(groups[i+1].slice(3,5)):null;
      const w=groups[i+2]?sondeTempWind(groups[i+2]):{drct:null,sknt:null};
      sondeTempMergeLevel(map,p,{t,td:(t!=null&&dd!=null)?t-dd:null,drct:w.drct,sknt:w.sknt});
      break;
    }
    if(groups[i]==='88999'||groups[i].startsWith('77')||groups[i]==='31313') break;
    i++;
  }
  return map;
}
function parseTempBB(text,high){
  const groups=sondeTempGroups(text).filter(g=>g!=='78988');
  const map=new Map();
  let i=0;
  const startRe=high?/^11\d{3}$/:/^00\d{3}$/;
  while(i<groups.length && !startRe.test(groups[i])) i++;
  if(i>=groups.length){
    i=0;
    while(i<groups.length){
      const nn=groups[i].slice(0,2);
      if(/^\d\d$/.test(nn) && parseInt(nn,10)%11===0 && groups[i].slice(0,2)!=='55') break;
      i++;
    }
  }
  while(i+1<groups.length){
    const g=groups[i];
    if(g==='21212'||g==='31313'||g.startsWith('41')||g.startsWith('51')) break;
    if(!/^\d{5}$/.test(g)){ i++; continue; }
    const nn=parseInt(g.slice(0,2),10);
    if(nn%11!==0){ i++; continue; }
    let p=parseInt(g.slice(2),10);
    if(high){
      if(p>150) p=p/10;
    }else if(p<50){
      p+=1000;
    }
    const t=sondeTempT(groups[i+1].slice(0,3));
    const dd=sondeTempDD(groups[i+1].slice(3,5));
    sondeTempMergeLevel(map,p,{t,td:(t!=null&&dd!=null)?t-dd:null});
    i+=2;
  }
  const w212=groups.indexOf('21212', i);
  if(w212>=0){
    let j=w212+1;
    while(j+1<groups.length){
      const g=groups[j];
      if(g==='31313'||g.startsWith('41')||g.startsWith('51')) break;
      if(!/^\d{5}$/.test(g)){ j++; continue; }
      const nn=parseInt(g.slice(0,2),10);
      if(nn%11!==0){ j++; continue; }
      let p=parseInt(g.slice(2),10);
      if(high){ if(p>150) p=p/10; }
      else if(p<50) p+=1000;
      const w=sondeTempWind(groups[j+1]);
      sondeTempMergeLevel(map,p,{drct:w.drct,sknt:w.sknt});
      j+=2;
    }
  }
  return map;
}
function parseNoaaTempParts(parts){
  const maps=[];
  if(parts.TTAA) maps.push(parseTempAA(parts.TTAA,false));
  if(parts.TTBB) maps.push(parseTempBB(parts.TTBB,false));
  if(parts.TTCC) maps.push(parseTempAA(parts.TTCC,true));
  if(parts.TTDD) maps.push(parseTempBB(parts.TTDD,true));
  const merged=new Map();
  for(const m of maps){
    for(const [k,v] of m) sondeTempMergeLevel(merged,k,v);
  }
  const profile=[...merged.values()].filter(lv=>{
      if(lv.t==null||!(lv.p>=50&&lv.p<=1100)) return false;
      if(lv.t>45||lv.t<-90) return false;
      if(lv.p>=850 && lv.t<-5) return false;
      if(lv.p>=700 && lv.t<-20) return false;
      if(lv.p>=400 && lv.t<-50) return false;
      return true;
    }).sort((a,b)=>b.p-a.p);
  if(profile.length<8) return null;
  const meta=sondeTempHeaderMeta(parts.TTAA||parts.TTBB||'');
  let obsTime=null, dt=null;
  if(meta.day!=null){
    const now=new Date();
    let y=now.getUTCFullYear(), mo=now.getUTCMonth();
    if(meta.day>now.getUTCDate()+1){ mo-=1; if(mo<0){ mo=11; y-=1; } }
    dt=new Date(Date.UTC(y,mo,meta.day,meta.hour||0,0,0));
    const mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][dt.getUTCMonth()];
    obsTime=`${meta.day} ${mon} ${y} · ${String(meta.hour).padStart(2,'0')}:00Z`;
  }
  return {obsTime,ind:{},profile,dt};
}
async function sondeFetchLocalMirror(){
  try{
    const href=new URL('sonde-latest.json', (typeof document!=='undefined'&&document.baseURI)||(typeof location!=='undefined'?location.href:'./')).href;
    const r=await fetch(href+'?t='+Date.now(),{cache:'no-store'});
    if(!r||!r.ok) return null;
    const j=await r.json();
    if(!j||!j.parts||!j.parts.TTAA) return null;
    const parsed=parseNoaaTempParts(j.parts);
    if(!parsed) return null;
    parsed.source='NOAA tgftp raw TEMP (TTAA/TTBB/TTCC/TTDD)';
    return {parsed,url:SONDE_NOAA_RAW.TTAA,dt:parsed.dt||new Date()};
  }catch(e){ return null; }
}
async function sondeFetchNoaaRaw(){
  const local=await sondeFetchLocalMirror();
  if(local) return local;
  const entries=Object.entries(SONDE_NOAA_RAW);
  const settled=await Promise.allSettled(entries.map(([,url])=>sondeFetchOneNoaa(url)));
  const parts={};
  entries.forEach(([k],i)=>{ if(settled[i].status==='fulfilled') parts[k]=settled[i].value; });
  if(!parts.TTAA && !parts.TTBB) return null;
  const parsed=parseNoaaTempParts(parts);
  if(!parsed) return null;
  parsed.source='NOAA tgftp raw TEMP (live)';
  return {parsed,url:SONDE_NOAA_RAW.TTAA,dt:parsed.dt||((typeof sondeCycles==='function'&&sondeCycles()[0])||new Date())};
}
