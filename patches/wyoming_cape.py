from pathlib import Path
h=Path('index.html').read_text(encoding='utf-8')

# 1) Moist adiabat by conserved theta-e (Bolton) instead of RK4 lapse
old='''  const moistPts=[{p:Plcl,t:Tlcl}];
  { let T=Tlcl,P=Plcl; const dP=-5;
    while(P+dP>=Ptop){
      const k1=sondeMoistLapse(T,P);
      const k2=sondeMoistLapse(T+dP/2*k1,P+dP/2);
      const k3=sondeMoistLapse(T+dP/2*k2,P+dP/2);
      const k4=sondeMoistLapse(T+dP*k3,P+dP);
      T=T+dP/6*(k1+2*k2+2*k3+k4); P=P+dP;
      moistPts.push({p:P,t:T});
    }
  }'''

new='''  const teLcl=(function(){
    const w=sondeMixR(Tlcl,Plcl)/1000, Tk=Tlcl+273.15;
    return Tk*Math.pow(1000/Plcl,0.2854*(1-0.28*w))*Math.exp(w*(3376/Tk-2.54));
  })();
  function sondeTFromThetaE(P,teTarget){
    let lo=-90, hi=50, T=Tlcl;
    for(let n=0;n<24;n++){
      T=(lo+hi)/2;
      const w=sondeMixR(T,P)/1000, Tk=T+273.15;
      const te=Tk*Math.pow(1000/P,0.2854*(1-0.28*w))*Math.exp(w*(3376/Tk-2.54));
      if(te>teTarget) hi=T; else lo=T;
    }
    return T;
  }
  const moistPts=[{p:Plcl,t:Tlcl}];
  for(let P=Plcl-5;P>=Ptop;P-=5) moistPts.push({p:P,t:sondeTFromThetaE(P,teLcl)});'''

if old in h:
    h=h.replace(old,new,1)
    print('theta-e moist')
else:
    print('WARN moist block')

# 2) CAPE from plain T (MetPy-like magnitude); keep virtual only as secondary
# Leave sondeCapeCin but subtract less buoyancy: use T not Tv
oldc='''    const TaEnvV=sondeVirtualT(Te,envTd(P)!=null?sondeMixR(envTd(P),P):0);
    const TpV=sondeVirtualT(Tp,parcelW(P));
    samples.push({P,dT:TpV-TeV,Tv:TeV});'''
# current code uses different var names - read after patch land by replacing virtual in cape
h2=h
if 'sondeVirtualT(Te,' in h:
    print('has virtual in cape samples')

# Replace virtual buoyancy with plain T difference inside sondeCapeCin sample loop
h=h.replace(
'''    const TeV=sondeVirtualT(Te,envTd(P)!=null?sondeMixR(envTd(P),P):0);
    const TpV=sondeVirtualT(Tp,parcelW(P));
    samples.push({P,dT:TpV-TeV,Tv:TeV});''',
'''    samples.push({P,dT:Tp-Te,Tv:Te});''',
1)
print('plain-T CAPE', 'dT:Tp-Te' in h)

# 3) Wyoming look: black T/Td, no parcel, no shade, heights in meters
h=h.replace("ctx.strokeStyle='#0a7a28';","ctx.strokeStyle='#111';",1)
h=h.replace("ctx.strokeStyle='#d21f1f';","ctx.strokeStyle='#111';",1)

# skip drawing parcel + shade
oldp='''  const parcel=sondeSurfaceParcel(profile);
  if(parcel){
    sondeShadeParcelArea(ctx,g,parcel.envT,parcel.parcelT,parcel.P0,parcel.Ptop);
    ctx.strokeStyle='#1d4ed8';ctx.lineWidth=2;ctx.setLineDash([]);
    ctx.beginPath();
    for(let P=parcel.P0;P>=parcel.Ptop;P-=10){
      const x=g.xOf(parcel.parcelT(P),P),y=g.yOf(P);
      P===parcel.P0?ctx.moveTo(x,y):ctx.lineTo(x,y);
    }
    ctx.stroke();
    const lx=g.xOf(parcel.Tlcl,parcel.Plcl),ly=g.yOf(parcel.Plcl);
    ctx.beginPath();ctx.arc(lx,ly,3,0,Math.PI*2);ctx.fillStyle='#000';ctx.fill();
  }'''
if oldp in h:
    h=h.replace(oldp,'  /* Wyoming-style: no parcel trace or CAPE fill on the chart */',1)
    print('removed parcel draw')
else:
    print('WARN parcel draw')
    i=h.find('sondeSurfaceParcel(profile)')
    print('idx',i, h[i:i+200] if i>=0 else '')

# heights: meters like Wyoming
h=h.replace(
'''    const ft=h*3.28084;
    const ftStr=ft>=1000?(ft/1000).toFixed(1)+'k':String(Math.round(ft));
    const label=ftStr+'ft';''',
'''    const label=String(Math.round(h));''',
1)
print('meters', 'label=String(Math.round(h))' in h)

h=h.replace("'NOAA v30 · '+prof.length+' lvls · heights ft'","'NOAA v31 · '+prof.length+' lvls · heights m'",1)

Path('index.html').write_text(h,encoding='utf-8')
print('black T', h.count("strokeStyle='#111'"))
