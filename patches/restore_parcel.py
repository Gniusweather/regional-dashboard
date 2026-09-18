from pathlib import Path
p=Path('index.html')
h=p.read_text(encoding='utf-8')
old='  /* Wyoming-style: no parcel trace or CAPE fill on the chart */\n'
new='''  const parcel=sondeSurfaceParcel(profile);
  if(parcel){
    sondeShadeParcelArea(ctx,g,parcel.envT,parcel.parcelT,parcel.P0,parcel.Ptop);
    ctx.strokeStyle='#1d4ed8';ctx.lineWidth=2;ctx.setLineDash([]);
    ctx.beginPath();
    for(let P=parcel.P0;P>=Math.max(parcel.Ptop,100);P-=10){
      const Tp=parcel.parcelT(P);
      if(Tp==null||!isFinite(Tp)) continue;
      const x=g.xOf(Tp,P),y=g.yOf(P);
      P===parcel.P0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    }
    ctx.stroke();
    const lx=g.xOf(parcel.Tlcl,parcel.Plcl),ly=g.yOf(parcel.Plcl);
    ctx.beginPath();ctx.arc(lx,ly,3,0,Math.PI*2);ctx.fillStyle='#000';ctx.fill();
  }
'''
if old in h:
    h=h.replace(old,new,1)
    print('restored parcel')
else:
    print('WARN placeholder missing')
h=h.replace("'NOAA v32 · '+prof.length+' lvls · heights ft'","'NOAA v33 · '+prof.length+' lvls · heights ft'",1)
p.write_text(h,encoding='utf-8')
print('parcel draw', 'sondeShadeParcelArea(ctx' in h)
print('v33', 'NOAA v33' in h)
