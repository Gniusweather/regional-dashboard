from pathlib import Path
p=Path('index.html')
h=p.read_text(encoding='utf-8')

fn = r'''
function sondeThetaE(T,Td,P){
  if(T==null||Td==null||P==null) return null;
  const w=sondeMixR(Td,P)/1000;
  let Tlcl=T, Plcl=P;
  const th=sondeTheta(T,P);
  for(let p=P;p>=100;p-=2){
    const Tp=sondeTOnDryAdiabat(th,p);
    Tlcl=Tp; Plcl=p;
    if(sondeMixR(Tp,p)<=sondeMixR(Td,P)) break;
  }
  return (th+273.15)*Math.exp((2.501e6*w)/((1005.7)*(Tlcl+273.15)))-273.15;
}
function sondeMostUnstableParcel(profileRaw){
  const prof=(profileRaw||[]).filter(r=>isFinite(r.p)&&isFinite(r.t)&&r.td!=null).sort((a,b)=>b.p-a.p);
  if(prof.length<3) return sondeSurfaceParcel(profileRaw);
  const Pbot=prof[0].p;
  const Pcut=Pbot-300;
  let best=null, bestTe=-1e9;
  prof.forEach(r=>{
    if(r.p<Pcut) return;
    const te=sondeThetaE(r.t,r.td,r.p);
    if(te!=null && te>bestTe){ bestTe=te; best=r; }
  });
  if(!best) return sondeSurfaceParcel(profileRaw);
  const Ptop=Math.min.apply(null, (profileRaw||[]).filter(r=>isFinite(r.p)).map(r=>r.p));
  return sondeParcelAscent((profileRaw||[]).filter(r=>isFinite(r.p)&&isFinite(r.t)).sort((a,b)=>b.p-a.p), best.p, Ptop, best.t, best.td);
}
'''

if 'function sondeMostUnstableParcel' not in h:
    h=h.replace('function sondeComputeIndices(profileRaw){', fn+'function sondeComputeIndices(profileRaw){',1)
    print('added MU helpers')
else:
    print('MU helpers exist')

old='''  const parcel=sondeSurfaceParcel(profileRaw);
  if(!parcel||parcel.prof.length<5) return null;
  const {prof,Plcl,parcelT,envT}=parcel;
  const {CAPE,CIN,LFC,EL}=sondeCapeCin(parcel);'''

new='''  const sfc=sondeSurfaceParcel(profileRaw);
  const parcel=sondeMostUnstableParcel(profileRaw)||sfc;
  if(!parcel||parcel.prof.length<5) return null;
  const {prof,Plcl,parcelT,envT}=parcel;
  const {CAPE,CIN,LFC,EL}=sondeCapeCin(parcel);
  const sfcCape=sfc?sondeCapeCin(sfc):null;'''

if old in h:
    h=h.replace(old,new,1)
    print('switched CAPE to MU')
else:
    print('WARN compute start missing')

# Virtual LI (LFVT) using MU parcel at 500 vs env virtual T
oldli='  const LI=(T500!=null)?(T500-parcelT(500)):null;'
newli='''  const LI=(T500!=null)?(T500-parcelT(500)):null;
  let LFVT=null;
  if(T500!=null){
    const Td500=sondeInterpEnv(prof,500,'td');
    const envV=sondeVirtualT(T500,Td500!=null?sondeMixR(Td500,500):0);
    const parV=sondeVirtualT(parcelT(500),parcel.parcelW?parcel.parcelW(500):sondeMixR(parcelT(500),500));
    LFVT=+(envV-parV).toFixed(1);
  }'''
if oldli in h:
    h=h.replace(oldli,newli,1)
    print('LFVT')

oldret='''    LI:LI!=null?+LI.toFixed(1):null,
    SI:SI,'''
newret='''    LI:LFVT!=null?LFVT:(LI!=null?+LI.toFixed(1):null),
    SI:SI,
    SBCAPE:sfcCape&&sfcCape.CAPE!=null?Math.round(sfcCape.CAPE):null,'''
if oldret in h:
    h=h.replace(oldret,newret,1)
    print('return LI as virtual / SBCAPE extra')
else:
    print('WARN return')

# label CAPE as MUCAPE on the chart
h=h.replace("rows.push(['CAPE',Math.round(idx.cape)+' J/kg'",
            "rows.push(['MUCAPE',Math.round(idx.cape)+' J/kg'",1)

p.write_text(h,encoding='utf-8')
print('MUCAPE label', "['MUCAPE'" in h)
print('sondeMostUnstableParcel', 'function sondeMostUnstableParcel' in h)
