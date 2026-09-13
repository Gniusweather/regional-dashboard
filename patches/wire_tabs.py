from pathlib import Path
p=Path('index.html'); t=p.read_text()

nav_old='    <button class="tab-btn" data-tab="stations" role="tab" aria-selected="false">⊎ Stations</button>'
nav_new=nav_old+'\n    <button class="tab-btn" data-tab="atc" role="tab" aria-selected="false">🛫 ATC</button>'
if 'data-tab="atc"' not in t:
    t=t.replace(nav_old, nav_new, 1)
    print('nav atc', nav_old in t or True)

synop_old='''    <div id="synopSection" class="table-wrapper fade-in hidden">
      <div class="section-header">
        <div class="section-title">SYNOP Reports</div>'''
synop_new='''    <div id="synopSection" class="table-wrapper fade-in hidden">
      <div class="section-header">
        <div class="section-title">SYNOP Reports</div>
        <div class="section-controls" style="display:flex;gap:6px;flex-wrap:wrap">
          <button type="button" class="btn-primary" id="synop-sub-reports" onclick="synopSub('reports')" style="font-size:12px;height:28px;padding:4px 10px">Reports</button>
          <button type="button" class="btn-primary" id="synop-sub-encode" onclick="synopSub('encode')" style="font-size:12px;height:28px;padding:4px 10px;opacity:.75">Encode</button>
        </div>'''
if 'synopSub(' not in t:
    t=t.replace(synop_old, synop_new, 1)
    t=t.replace(
      '<div id="synop-table">',
      '<div id="synop-encode-wrap" style="display:none;height:min(78vh,820px);border-radius:10px;overflow:hidden;border:1px solid var(--border);margin-bottom:10px"><iframe src="encoders.html" title="SYNOP encoder" style="width:100%;height:100%;border:0;background:#0b1220"></iframe></div>\n        <div id="synop-table">',
      1)

stations_old='    <div id="stationsList" class="stations" aria-live="polite">'
stations_bar='''    <div style="display:flex;gap:6px;flex-wrap:wrap;margin:0 0 10px">
      <button type="button" class="btn-primary" id="st-sub-net" onclick="stationsSub('net')" style="font-size:12px;height:28px;padding:4px 10px">Network</button>
      <button type="button" class="btn-primary" id="st-sub-ovz" onclick="stationsSub('ovz')" style="font-size:12px;height:28px;padding:4px 10px;opacity:.75">Overzicht</button>
    </div>
    <div id="ovz-wrap" style="display:none;min-height:60vh;border-radius:10px;overflow:hidden;border:1px solid var(--border);margin-bottom:12px">
      <iframe src="overzicht.html" title="Overzicht Weersgesteldheid" style="width:100%;height:min(80vh,900px);border:0;background:#fff"></iframe>
    </div>
'''
if 'stationsSub(' not in t:
    t=t.replace(stations_old, stations_bar+stations_old, 1)

atc_sec='''    <div id="atcSection" class="table-wrapper fade-in hidden">
      <div class="section-header"><div class="section-title">Live ATC · ABC / TNCC</div></div>
      <div style="height:min(82vh,920px);border-radius:10px;overflow:hidden;border:1px solid var(--border)">
        <iframe src="atc.html" title="Live ATC" style="width:100%;height:100%;border:0;background:#0b1220"></iframe>
      </div>
    </div>
'''
if 'id="atcSection"' not in t:
    t=t.replace('    <!-- KNMI Section -->', atc_sec+'    <!-- KNMI Section -->', 1)

if 'atcSectionEl' not in t:
    t=t.replace(
      "const stationsSectionEl=document.getElementById('stationsSection');",
      "const stationsSectionEl=document.getElementById('stationsSection');\nconst atcSectionEl=document.getElementById('atcSection');",
      1)
    t=t.replace(
      '[metarSectionEl,tafSectionEl,synopSectionEl,knmiSectionEl,mapsSectionEl]',
      '[metarSectionEl,tafSectionEl,synopSectionEl,knmiSectionEl,mapsSectionEl,atcSectionEl]',
      1)
    t=t.replace(
      "else if(name==='stations'){",
      "else if(name==='atc'){atcSectionEl?.classList.remove('hidden');}\n  else if(name==='stations'){",
      1)

helpers='''
function synopSub(which){
  const enc=document.getElementById('synop-encode-wrap');
  const tbl=document.getElementById('synop-table');
  const bar=document.getElementById('synop-updated');
  if(enc) enc.style.display=which==='encode'?'block':'none';
  if(tbl) tbl.style.display=which==='encode'?'none':'block';
  if(bar) bar.style.display=which==='encode'?'none':'block';
  const a=document.getElementById('synop-sub-encode'), b=document.getElementById('synop-sub-reports');
  if(a) a.style.opacity=which==='encode'?'1':'.75';
  if(b) b.style.opacity=which==='encode'?'.75':'1';
}
function stationsSub(which){
  const ovz=document.getElementById('ovz-wrap');
  const list=document.getElementById('stationsList');
  if(ovz) ovz.style.display=which==='ovz'?'block':'none';
  if(list) list.style.display=which==='ovz'?'none':'grid';
  document.querySelectorAll('.summary,.stations-header #toggleMap').forEach(function(){});
  const net=document.getElementById('st-sub-net'), o=document.getElementById('st-sub-ovz');
  if(net) net.style.opacity=which==='ovz'?'.75':'1';
  if(o) o.style.opacity=which==='ovz'?'1':'.75';
  if(which==='ovz'){ try{ var f=ovz&&ovz.querySelector('iframe'); if(f&&(!f.dataset.loaded)){ f.src=f.src; f.dataset.loaded='1'; } }catch(e){} }
}
window.synopSub=synopSub; window.stationsSub=stationsSub;
'''
if 'function synopSub' not in t:
    t=t.replace('function switchTab(name){', helpers+'function switchTab(name){', 1)

p.write_text(t)
print('atc tab', 'data-tab="atc"' in t)
print('atcSection', 'id="atcSection"' in t)
print('synopSub', 'function synopSub' in t)
print('stationsSub', 'function stationsSub' in t)
