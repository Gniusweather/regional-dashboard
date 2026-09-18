from pathlib import Path

js_path=Path('sonde-noaa.js')
js=js_path.read_text(encoding='utf-8')
old_ok='''  function sondeLevelOk(lv){
    if(!(lv.p>=100&&lv.p<=1075)) return false;
    if(lv.t==null||!isFinite(lv.t)) return false;
    if(lv.t>40||lv.t<-90) return false;
    if(lv.p<=850 && lv.t>35) return false;
    if(lv.p<=500 && lv.t>10) return false;
    if(lv.p<=300 && lv.t>0) return false;
    if(lv.td!=null && lv.td>lv.t+0.6) lv.td=lv.t;
    return true;
  }'''
new_ok='''  function sondeLevelOk(lv){
    if(!(lv.p>=100&&lv.p<=1075)) return false;
    if(lv.t==null||!isFinite(lv.t)) return false;
    if(lv.t>45||lv.t<-90) return false;
    if(lv.td!=null && lv.td>lv.t+1) lv.td=lv.t;
    return true;
  }'''
if old_ok in js:
    js=js.replace(old_ok,new_ok,1)
    print('relaxed level filter')
else:
    print('WARN level filter')
js_path.write_text(js,encoding='utf-8')

hp=Path('index.html')
h=hp.read_text(encoding='utf-8')

old_t='''    const tPts=prof.filter(r=>isFinite(r.t)&&isFinite(r.p)&&r.t<=40&&!(r.p<=500&&r.t>10)&&!(r.p<=300&&r.t>0));
    tPts.forEach((r,i)=>{
      if(i>0&&i<tPts.length-1){
        const prev=tPts[i-1], next=tPts[i+1];
        if(Math.abs(r.t-prev.t)>18 && Math.abs(r.t-next.t)>18) return;
      }
      const x=g.xOf(r.t,r.p),y=g.yOf(r.p); ctx.lineTo?null:null;
      i===0||!ctx._tStarted?(ctx.moveTo(x,y),ctx._tStarted=1):ctx.lineTo(x,y);
    });
    ctx.stroke(); ctx._tStarted=0;'''
new_t='''    const tPts=prof.filter(r=>isFinite(r.t)&&isFinite(r.p)).sort((a,b)=>b.p-a.p);
    tPts.forEach((r,i)=>{
      const x=g.xOf(r.t,r.p),y=g.yOf(r.p);
      i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    });
    ctx.stroke();'''
if old_t in h:
    h=h.replace(old_t,new_t,1)
    print('full T trace')
else:
    print('WARN tPts')

# desktop chart size
old_css='''.skewt-box{
  position:relative;border-radius:12px;overflow:hidden;
  border:1px solid var(--border-bright);background:#fff;
  box-shadow:var(--shadow);
  width:100%;height:860px;display:block;background:#e8f4ea;
}
.skewt-box canvas{position:absolute;inset:0;width:100%;height:100%;display:block;}


@media(max-width:600px){.skewt-box{height:860px;}}
@media(max-width:400px){.skewt-box{height:860px;}}'''
new_css='''.skewt-box{
  position:relative;border-radius:12px;overflow:hidden;
  border:1px solid var(--border-bright);background:#fff;
  box-shadow:var(--shadow);
  width:100%;height:860px;display:block;background:#e8f4ea;
}
.skewt-box canvas{position:absolute;inset:0;width:100%;height:100%;display:block;}
@media(min-width:1100px){.skewt-box{height:min(92vh,1040px);}}
@media(min-width:1400px){.skewt-box{height:min(94vh,1120px);}}
@media(max-width:600px){.skewt-box{height:860px;}}
@media(max-width:400px){.skewt-box{height:860px;}}'''
if old_css in h:
    h=h.replace(old_css,new_css,1)
    print('desktop css')
else:
    print('WARN css')

# slightly larger left/right plot padding and type on desktop geom
old_pad='const pad={l:(W>=900?52:38)+indicesW,r:W>=900?56:46,t:12+titleLines*13+4,b:W>=900?34:28};'
new_pad='const pad={l:(W>=1200?64:(W>=900?52:38))+indicesW,r:W>=1200?72:(W>=900?56:46),t:12+titleLines*(W>=1100?15:13)+4,b:W>=1200?40:(W>=900?34:28)};'
if old_pad in h:
    h=h.replace(old_pad,new_pad,1)
    print('geom pad')
else:
    print('WARN pad')

h=h.replace("'NOAA v33 · '+prof.length+' lvls · heights ft'","'NOAA v34 · '+prof.length+' lvls · heights ft'",1)
h=h.replace("'NOAA v32 · '+prof.length+' lvls · heights ft'","'NOAA v34 · '+prof.length+' lvls · heights ft'",1)

hp.write_text(h,encoding='utf-8')
print('v34', 'NOAA v34' in h)
