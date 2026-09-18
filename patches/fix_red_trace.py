from pathlib import Path

# 1) NOAA parser: thermo-only profile, no wind-only holes, tighter T sanity
p=Path('sonde-noaa.js')
js=p.read_text(encoding='utf-8')

old='''  let profile=[...merged.values()].filter(lv=>{
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

new='''  function sondeLevelOk(lv){
    if(!(lv.p>=100&&lv.p<=1075)) return false;
    if(lv.t==null||!isFinite(lv.t)) return false;
    if(lv.t>40||lv.t<-90) return false;
    if(lv.p<=850 && lv.t>35) return false;
    if(lv.p<=500 && lv.t>10) return false;
    if(lv.p<=300 && lv.t>0) return false;
    if(lv.td!=null && lv.td>lv.t+0.6) lv.td=lv.t;
    return true;
  }
  let profile=[...merged.values()].filter(sondeLevelOk).sort((a,b)=>b.p-a.p);
  const pp=[...(parts.PPBB?parseTempPP(parts.PPBB):[]), ...(parts.PPDD?parseTempPP(parts.PPDD):[])];
  pp.forEach(w=>{
    const p=sondePFromHeightM(profile, w.hft*0.3048);
    if(p==null) return;
    let best=null, dBest=1e9;
    profile.forEach(lv=>{ const d=Math.abs(lv.p-p); if(d<dBest){ dBest=d; best=lv; } });
    if(best && dBest<=15){
      if(best.drct==null) best.drct=w.drct;
      if(best.sknt==null) best.sknt=w.sknt;
    }
  });'''

if old in js:
    js=js.replace(old,new,1)
    print('parser cleaned')
else:
    print('WARN parser block')
    print('has first filter', 'lv.p>=100&&lv.p<=1075' in js)

p.write_text(js,encoding='utf-8')

# 2) Draw T trace from despiked thermo levels only
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')
oldd='''    ctx.strokeStyle='#d21f1f';
    ctx.beginPath();
    prof.forEach((r,i)=>{ const x=g.xOf(r.t,r.p),y=g.yOf(r.p); i===0?ctx.moveTo(x,y):ctx.lineTo(x,y); });
    ctx.stroke();'''
newd='''    ctx.strokeStyle='#d21f1f';
    ctx.beginPath();
    const tPts=prof.filter(r=>isFinite(r.t)&&isFinite(r.p)&&r.t<=40&&!(r.p<=500&&r.t>10)&&!(r.p<=300&&r.t>0));
    tPts.forEach((r,i)=>{
      if(i>0&&i<tPts.length-1){
        const prev=tPts[i-1], next=tPts[i+1];
        if(Math.abs(r.t-prev.t)>18 && Math.abs(r.t-next.t)>18) return;
      }
      const x=g.xOf(r.t,r.p),y=g.yOf(r.p); ctx.lineTo?null:null;
      i===0||!ctx._tStarted?(ctx.moveTo(x,y),ctx._tStarted=1):ctx.lineTo(x,y);
    });
    ctx.stroke(); ctx._tStarted=0;'''
if oldd in h:
    h=h.replace(oldd,newd,1)
    print('draw despike')
else:
    print('WARN draw block')

# PW: skip missing-td layers instead of aborting the whole column
h=h.replace(
    'if(a.td==null||b.td==null){ if(started)break; continue; }',
    'if(a.td==null||b.td==null||a.t==null||b.t==null){ continue; }',
    1)
print('pw skip')
hp.write_text(h,encoding='utf-8')
