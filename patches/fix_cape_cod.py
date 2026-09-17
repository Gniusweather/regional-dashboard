from pathlib import Path
p=Path('index.html'); h=p.read_text(encoding='utf-8')

old_cape = '''function sondeCapeCin(parcel){
  const {prof,P0,Ptop,Plcl,parcelT,parcelW,envT,envTd}=parcel;
  const Rd=287.05, g=9.80665;
  const levels=new Set([P0]);
  prof.forEach(r=>{ if(r.p<P0&&r.p>=Ptop) levels.add(r.p); });
  if(Plcl<P0&&Plcl>Ptop) levels.add(Plcl);
  const uniq=[...levels].sort((a,b)=>b-a);
  const layers=[];
  for(let i=0;i<uniq.length-1;i++){
    const Pa=uniq[i],Pb=uniq[i+1];
    const TaEnv=envT(Pa),TbEnv=envT(Pb);
    if(TaEnv==null||TbEnv==null||Pa===Pb)continue;
    const TaEnvV=sondeVirtualT(TaEnv,envTd(Pa)!=null?sondeMixR(envTd(Pa),Pa):0);
    const TbEnvV=sondeVirtualT(TbEnv,envTd(Pb)!=null?sondeMixR(envTd(Pb),Pb):0);
    const TaP=parcelT(Pa),TbP=parcelT(Pb);
    const TaPV=sondeVirtualT(TaP,parcelW(Pa)), TbPV=sondeVirtualT(TbP,parcelW(Pb));
    const TvAvgK=(TaEnvV+TbEnvV)/2+273.15;
    const dz=Rd*TvAvgK/g*Math.log(Pa/Pb);
    const dT=((TaPV-TaEnvV)+(TbPV-TbEnvV))/2;
    layers.push({dE:g*dT/TvAvgK*dz});
  }
  let CAPE=0,CIN=0,bestSum=0,bestStart=-1,i=0;
  while(i<layers.length){
    if(layers[i].dE>0){
      let j=i,sum=0;
      while(j<layers.length&&layers[j].dE>0){ sum+=layers[j].dE; j++; }
      if(sum>bestSum){ bestSum=sum; bestStart=i; }
      i=j;
    } else i++;
  }
  CAPE=bestSum;
  if(bestStart>0) for(let k=0;k<bestStart;k++) if(layers[k].dE<0) CIN+=layers[k].dE;
  return {CAPE,CIN};
}'''

new_cape = '''function sondeCapeCin(parcel){
  const {prof,P0,Ptop,Plcl,parcelT,parcelW,envT,envTd}=parcel;
  const Rd=287.05, g=9.80665;
  const levels=new Set([P0]);
  for(let P=P0;P>=Math.max(Ptop,100);P-=10) levels.add(P);
  prof.forEach(r=>{ if(r.p<=P0&&r.p>=Ptop) levels.add(r.p); });
  if(Plcl<P0&&Plcl>Ptop) levels.add(Plcl);
  const uniq=[...levels].sort((a,b)=>b-a);
  const samples=[];
  for(const P of uniq){
    const Te=envT(P), Tp=parcelT(P);
    if(Te==null||Tp==null) continue;
    const TeV=sondeVirtualT(Te,envTd(P)!=null?sondeMixR(envTd(P),P):0);
    const TpV=sondeVirtualT(Tp,parcelW(P));
    samples.push({P,dT:TpV-TeV,Tv:TeV});
  }
  let LFC=null,EL=null;
  for(let i=1;i<samples.length;i++){
    if(samples[i-1].dT<=0 && samples[i].dT>0 && samples[i].P<=Plcl+1){
      const f=samples[i-1].dT/(samples[i-1].dT-samples[i].dT||1e-6);
      LFC=samples[i-1].P+(samples[i].P-samples[i-1].P)*f;
      break;
    }
  }
  if(LFC==null){
    const firstPos=samples.find(s=>s.dT>0 && s.P<=Plcl);
    if(firstPos) LFC=firstPos.P;
  }
  if(LFC!=null){
    for(let i=1;i<samples.length;i++){
      if(samples[i-1].P<=LFC && samples[i-1].dT>0 && samples[i].dT<=0){
        const f=samples[i-1].dT/(samples[i-1].dT-samples[i].dT||1e-6);
        EL=samples[i-1].P+(samples[i].P-samples[i-1].P)*f;
      }
    }
  }
  let CAPE=0,CIN=0;
  for(let i=0;i<samples.length-1;i++){
    const a=samples[i], b=samples[i+1];
    if(a.P===b.P) continue;
    const TvAvgK=(a.Tv+b.Tv)/2+273.15;
    const dz=Rd*TvAvgK/g*Math.log(a.P/b.P);
    const dT=(a.dT+b.dT)/2;
    const dE=g*dT/TvAvgK*dz;
    const pmid=(a.P+b.P)/2;
    if(LFC!=null && pmid<=LFC && (EL==null || pmid>=EL) && dE>0) CAPE+=dE;
    if((LFC==null || pmid>=LFC) && dE<0) CIN+=dE;
  }
  return {CAPE,CIN,LFC,EL};
}'''

if old_cape in h:
    h=h.replace(old_cape,new_cape,1)
    print('replaced sondeCapeCin')
else:
    print('WARN cape block not exact')

# Use LFC/EL from cape helper in compute indices + Showalter/SWEAT/L57
old_comp='''  const {CAPE,CIN}=sondeCapeCin(parcel);

  // K-index / Total Totals need T & Td at the 850/700/500 hPa mandatory levels.
  const T850=envT(850),T700=envT(700),T500=envT(500);
  const Td850=sondeInterpEnv(prof,850,'td'),Td700=sondeInterpEnv(prof,700,'td');
  const K=(T850!=null&&T500!=null&&Td850!=null&&T700!=null&&Td700!=null)?(T850-T500)+Td850-(T700-Td700):null;
  const TT=(T850!=null&&Td850!=null&&T500!=null)?(T850+Td850)-2*T500:null;
  const LI=(T500!=null)?(T500-parcelT(500)):null;'''

new_comp='''  const {CAPE,CIN,LFC,EL}=sondeCapeCin(parcel);

  // K-index / Total Totals need T & Td at the 850/700/500 hPa mandatory levels.
  const T850=envT(850),T700=envT(700),T500=envT(500);
  const Td850=sondeInterpEnv(prof,850,'td'),Td700=sondeInterpEnv(prof,700,'td');
  const K=(T850!=null&&T500!=null&&Td850!=null&&T700!=null&&Td700!=null)?(T850-T500)+Td850-(T700-Td700):null;
  const TT=(T850!=null&&Td850!=null&&T500!=null)?(T850+Td850)-2*T500:null;
  const LI=(T500!=null)?(T500-parcelT(500)):null;
  let SI=null;
  if(T850!=null&&Td850!=null&&T500!=null){
    const p850=sondeParcelAscent(prof,850,100,T850,Td850);
    if(p850) SI=+(T500-p850.parcelT(500)).toFixed(1);
  }
  const f850=sondeInterpEnv(prof,850,'sknt'), f500=sondeInterpEnv(prof,500,'sknt');
  const d850=sondeInterpEnv(prof,850,'drct'), d500=sondeInterpEnv(prof,500,'drct');
  let SWEAT=null;
  if(Td850!=null&&TT!=null){
    const termTd=12*Math.max(Td850,0);
    const termTT=20*Math.max(TT-49,0);
    const termF2=2*(f850||0)+(f500||0);
    let shear=0;
    if(d850!=null&&d500!=null&&f850!=null&&f500!=null&&f850>=15&&f500>=15){
      const ang=((d500-d850)+360)%360;
      const s=Math.sin(ang*Math.PI/180);
      if(s>0) shear=125*(s+0.2);
    }
    SWEAT=Math.round(termTd+termTT+termF2+shear);
  }'''

if old_comp in h:
    h=h.replace(old_comp,new_comp,1)
    print('expanded compute')
else:
    print('WARN compute block not exact')

old_ret='''  return {
    CAPE:Math.round(CAPE), CIN:Math.round(CIN),
    LI:LI!=null?+LI.toFixed(1):null,
    K:K!=null?Math.round(K):null,
    TT:TT!=null?Math.round(TT):null,
    PW:PW>0?+PW.toFixed(1):null,
    LCL:Math.round(Plcl) // hPa
  };'''
new_ret='''  return {
    CAPE:Math.round(CAPE), CIN:Math.round(CIN),
    LI:LI!=null?+LI.toFixed(1):null,
    SI:SI,
    K:K!=null?Math.round(K):null,
    TT:TT!=null?Math.round(TT):null,
    SWEAT:SWEAT,
    PW:PW>0?+PW.toFixed(1):null,
    LCL:Math.round(Plcl),
    LFC:LFC!=null?Math.round(LFC):null,
    EL:EL!=null?Math.round(EL):null
  };'''
if old_ret in h:
    h=h.replace(old_ret,new_ret,1)
    print('return fields')
else:
    print('WARN return not exact')

# merged aliases
if "if(c.LCL!=null)merged['Pres [hPa] of the Lifted Condensation Level']=c.LCL;" in h:
    h=h.replace(
        "if(c.LCL!=null)merged['Pres [hPa] of the Lifted Condensation Level']=c.LCL;",
        "if(c.LCL!=null)merged['Pres [hPa] of the Lifted Condensation Level']=c.LCL;\n  if(c.SI!=null)merged['Showalter index']=c.SI;\n  if(c.SWEAT!=null)merged['SWEAT index']=c.SWEAT;\n  if(c.LFC!=null)merged['LFC hPa']=c.LFC;\n  if(c.EL!=null)merged['EL hPa']=c.EL;",
        1)
    print('merged extras')

# plot style: white bg, green isotherms, blue parcel
h=h.replace("ctx.fillStyle=(opt&&opt.bw)?'#ffffff':'#e8f4ea';","ctx.fillStyle='#ffffff';",1)
h=h.replace("ctx.strokeStyle='rgba(130,130,130,0.75)';ctx.lineWidth=1;\n  for(let T=-140;T<=60;T+=10){",
            "ctx.strokeStyle='rgba(20,160,70,0.45)';ctx.lineWidth=1;\n  for(let T=-140;T<=60;T+=10){",1)
h=h.replace("ctx.strokeStyle='rgba(150,80,20,0.9)';ctx.lineWidth=1.6;ctx.setLineDash([]);",
            "ctx.strokeStyle='#1d4ed8';ctx.lineWidth=2;ctx.setLineDash([]);",1)

# sidebar extra rows
old_rows='''    if(idx.pw!=null)rows.push(['PW',idx.pw.toFixed(0)+' mm'+(trendGlyph[tr.pw]||'')]);'''
new_rows='''    if(idx.pw!=null)rows.push(['PW',idx.pw.toFixed(0)+' mm / '+(idx.pw/25.4).toFixed(2)+' in'+(trendGlyph[tr.pw]||'')]);
    if(idx.si!=null)rows.push(['SI',Number(idx.si).toFixed(1)]);
    if(idx.sweat!=null)rows.push(['SW',String(Math.round(idx.sweat))]);
    if(idx.lcl!=null)rows.push(['LCL',Math.round(idx.lcl)+' hPa']);
    if(idx.lfc!=null)rows.push(['LFC',Math.round(idx.lfc)+' hPa']);
    if(idx.el!=null)rows.push(['EL',Math.round(idx.el)+' hPa']);'''
if old_rows in h:
    h=h.replace(old_rows,new_rows,1)
    print('sidebar rows')
else:
    print('WARN sidebar rows')

# pass new fields into meta.indices
h=h.replace(
    'cape:capeV,cin:cinV,li:liV,k:kV,tt:ttV,pw:pwV,',
    'cape:capeV,cin:cinV,li:liV,k:kV,tt:ttV,pw:pwV,si:siV,sweat:swV,lcl:lclV,lfc:lfcV,el:elV,',
    1)

if "const pwV=sondeVal(ind,['Precipitable water']);" in h and 'const siV=' not in h:
    h=h.replace(
        "const pwV=sondeVal(ind,['Precipitable water']);",
        "const pwV=sondeVal(ind,['Precipitable water']);\n  const siV=sondeVal(ind,['Showalter index']);\n  const swV=sondeVal(ind,['SWEAT index']);\n  const lclV=sondeVal(ind,['Pres [hPa] of the Lifted']);\n  const lfcV=sondeVal(ind,['LFC hPa']);\n  const elV=sondeVal(ind,['EL hPa']);",
        1)
    print('capeV extras')

# CIN display as positive magnitude like COD
h=h.replace("if(idx.cin!=null)rows.push(['CIN',Math.round(idx.cin)+' J/kg'",
            "if(idx.cin!=null)rows.push(['CIN',Math.abs(Math.round(idx.cin))+' J/kg'",1)

p.write_text(h,encoding='utf-8')
print('parcel blue', "strokeStyle='#1d4ed8'" in h)
print('white bg', "fillStyle='#ffffff'" in h)
print('LFC field', 'LFC hPa' in h)
