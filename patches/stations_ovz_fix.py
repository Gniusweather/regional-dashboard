from pathlib import Path
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')
old='''function stationsSub(which){
  const ovz=document.getElementById('ovz-wrap');
  const list=document.getElementById('stationsList');
  if(ovz) ovz.style.display=which==='ovz'?'block':'none';
  if(list) list.style.display=which==='ovz'?'none':'grid';
  document.querySelectorAll('.summary,.stations-header #toggleMap').forEach(function(){});
'''
new='''function stationsSub(which){
  const ovz=document.getElementById('ovz-wrap');
  const list=document.getElementById('stationsList');
  const map=document.getElementById('stationsMapCard');
  if(ovz) ovz.style.display=which==='ovz'?'block':'none';
  if(list) list.style.display=which==='ovz'?'none':'grid';
  document.querySelectorAll('#stationsSection .summary').forEach(function(el){ el.style.display=which==='ovz'?'none':'flex'; });
  const tog=document.getElementById('toggleMap');
  if(tog) tog.style.display=which==='ovz'?'none':'inline-flex';
  if(map && which==='ovz') map.classList.add('hidden');
'''
if old in h:
    h=h.replace(old,new,1)
    print('stationsSub patched')
else:
    print('WARN stationsSub pattern')
    i=h.find('function stationsSub')
    print(h[i:i+400])
Path('index.html').write_text(h,encoding='utf-8')
