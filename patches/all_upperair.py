from pathlib import Path
p=Path('sonde-noaa.js')
js=p.read_text(encoding='utf-8')

add = r'''
function parseTempPP(text){
  const groups=sondeTempGroups(text).filter(g=>g!=='78988'&&g!=='NIL'&&g!=='nil');
  const out=[];
  let i=0;
  while(i<groups.length){
    const g=groups[i];
    if(g==='31313'||g.startsWith('51515')||g.startsWith('41414')) break;
    if(!(g[0]==='9'||g[0]==='8') || !/^\d\d/.test(g)){ i++; continue; }
    const decade=parseInt(g[1],10);
    if(!isFinite(decade)){ i++; continue; }
    const heights=[];
    for(const ch of g.slice(2)){
      if(ch==='/') continue;
      if(!/\d/.test(ch)) continue;
      heights.push((decade*10+parseInt(ch,10))*1000);
    }
    i++;
    for(const hft of heights){
      if(i>=groups.length) break;
      const w=sondeTempWind(groups[i]); i++;
      if(w.drct!=null||w.sknt!=null) out.push({hft,drct:w.drct,sknt:w.sknt});
    }
  }
  return out;
}
function sondePFromHeightM(profile,hm){
  const pts=(profile||[]).filter(r=>r.hgt!=null&&isFinite(r.hgt)&&isFinite(r.p)).sort((a,b)=>a.hgt-b.hgt);
  if(!pts.length||hm==null) return null;
  if(hm<=pts[0].hgt) return pts[0].p;
  if(hm>=pts[pts.length-1].hgt) return pts[pts.length-1].p;
  for(let i=0;i<pts.length-1;i++){
    const a=pts[i],b=pts[i+1];
    if(hm>=a.hgt&&hm<=b.hgt){
      const f=(hm-a.hgt)/((b.hgt-a.hgt)||1);
      return a.p+(b.p-a.p)*f;
    }
  }
  return null;
}
'''

if 'function parseTempPP' not in js:
    js=js.replace('function parseNoaaTempParts(parts){', add+'function parseNoaaTempParts(parts){',1)
    print('added PP parser')
else:
    print('PP parser exists')

old = '''  if(parts.TTAA) maps.push(parseTempAA(parts.TTAA,false));
  if(parts.TTBB) maps.push(parseTempBB(parts.TTBB,false));
  if(parts.TTCC) maps.push(parseTempAA(parts.TTCC,true));
  if(parts.TTDD) maps.push(parseTempBB(parts.TTDD,true));
  const merged=new Map();
  for(const m of maps){
    for(const [k,v] of m) sondeTempMergeLevel(merged,k,v);
  }
  const profile=[...merged.values()].filter(lv=>{
      if(lv.t==null||!(lv.p>=70&&lv.p<=1100)) return false;
      if(lv.t>48||lv.t<-95) return false;
      return true;
    }).sort((a,b)=>b.p-a.p);'''

new = '''  if(parts.TTAA) maps.push(parseTempAA(parts.TTAA,false));
  if(parts.TTBB) maps.push(parseTempBB(parts.TTBB,false));
  if(parts.TTCC) maps.push(parseTempAA(parts.TTCC,true));
  if(parts.TTDD) maps.push(parseTempBB(parts.TTDD,true));
  const merged=new Map();
  for(const m of maps){
    for(const [k,v] of m) sondeTempMergeLevel(merged,k,v);
  }
  let profile=[...merged.values()].filter(lv=>{
      if(!(lv.p>=100&&lv.p<=1075)) return false;
      if(lv.t!=null && (lv.t>50||lv.t<-90)) return false;
      return lv.t!=null || lv.td!=null || lv.drct!=null;
    }).sort((a,b)=>b.p-a.p);
  const pp=[...(parts.PPBB?parseTempPP(parts.PPBB):[]), ...(parts.PPDD?parseTempPP(parts.PPDD):[])];
  pp.forEach(w=>{
    const p=sondePFromHeightM(profile, w.hft*0.3048);
    if(p==null) return;
    let best=null, dBest=1e9;
    profile.forEach(lv=>{ const d=Math.abs(lv.p-p); if(d<dBest){ dBest=d; best=lv; } });
    if(best && dBest<=12){
      if(best.drct==null) best.drct=w.drct;
      if(best.sknt==null) best.sknt=w.sknt;
    } else {
      sondeTempMergeLevel(merged,p,{drct:w.drct,sknt:w.sknt});
    }
  });
  profile=[...merged.values()].filter(lv=>{
      if(!(lv.p>=100&&lv.p<=1075)) return false;
      if(lv.t!=null && (lv.t>50||lv.t<-90)) return false;
      return lv.t!=null || lv.td!=null || lv.drct!=null;
    }).sort((a,b)=>b.p-a.p);'''

if old in js:
    js=js.replace(old,new,1)
    print('merged all parts')
else:
    print('WARN merge block missing')

js=js.replace("parsed.source='NOAA tgftp raw TEMP (TTAA/TTBB/TTCC/TTDD)';",
              "parsed.source='NOAA tgftp raw TEMP (TTAA/TTBB/TTCC/TTDD/PPBB/PPDD)';",1)

p.write_text(js,encoding='utf-8')
print('parseTempPP', 'function parseTempPP' in js)
print('PPBB merge', 'parts.PPBB' in js)
