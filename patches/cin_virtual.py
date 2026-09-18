from pathlib import Path
p=Path('index.html')
h=p.read_text(encoding='utf-8')

old='''  const levels=new Set([P0]);
  for(let P=P0;P>=Math.max(Ptop,100);P-=10) levels.add(P);
  prof.forEach(r=>{ if(r.p<=P0&&r.p>=Ptop) levels.add(r.p); });
  if(Plcl<P0&&Plcl>Ptop) levels.add(Plcl);
  const uniq=[...levels].sort((a,b)=>b-a);
  const samples=[];
  for(const P of uniq){
    const Te=envT(P), Tp=parcelT(P);
    if(Te==null||Tp==null) continue;
    samples.push({P,dT:Tp-Te,Tv:Te});
  }'''

new='''  const levels=new Set([P0]);
  for(let P=P0;P>=Math.max(Ptop,100);P-=2) levels.add(P);
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
  }'''

if old in h:
    h=h.replace(old,new,1)
    print('virtual T + 2hPa')
else:
    print('WARN block')

# LFC: first neg->pos from the surface, not only at LCL
old_lfc='''    if(samples[i-1].dT<=0 && samples[i].dT>0 && samples[i].P<=Plcl+1){'''
new_lfc='''    if(samples[i-1].dT<=0 && samples[i].dT>0){'''
if old_lfc in h:
    h=h.replace(old_lfc,new_lfc,1)
    print('LFC scan')

h=h.replace("'NOAA v34 · '+prof.length+' lvls · heights ft'","'NOAA v35 · '+prof.length+' lvls · heights ft'",1)
p.write_text(h,encoding='utf-8')
print('v35','NOAA v35' in h)
print('virtual in cape','TpV-TeV' in h)
