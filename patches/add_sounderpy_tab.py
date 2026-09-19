from pathlib import Path
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')

btn='      <button class="tab-btn" data-tab="atc" role="tab" aria-selected="false">ATC</button>'
btn2=btn+'\n      <button class="tab-btn" data-tab="sounderpy" role="tab" aria-selected="false">SounderPy</button>'
if 'data-tab="sounderpy"' not in h:
    if btn in h:
        h=h.replace(btn,btn2,1)
        print('tab button')
    else:
        print('WARN button')
else:
    print('button exists')

sec='''    <div id="sounderpySection" class="table-wrapper fade-in hidden">
      <div class="section-header">
        <div class="section-title">SounderPy · TNCC 78988</div>
        <div class="section-controls" style="font-size:12px;color:var(--muted)">Wyoming RAOB · full · dark · updates 00Z/12Z</div>
      </div>
      <div style="background:#0b1220;border-radius:12px;overflow:auto;border:1px solid var(--border);padding:8px">
        <img id="sounderpyImg" alt="SounderPy TNCC sounding" style="width:100%;max-width:1200px;display:block;margin:0 auto;background:#111" src="plots/sounderpy-78988.png">
        <p id="sounderpyStamp" style="color:#8ea0b8;font-size:12px;margin:8px"></p>
      </div>
    </div>
'''
if 'id="sounderpySection"' not in h:
    mark='    <div id="atcSection"'
    if mark in h:
        h=h.replace(mark,sec+mark,1)
        print('section')
    else:
        print('WARN section')

h=h.replace('const atcSectionEl=document.getElementById(\'atcSection\');',
            'const atcSectionEl=document.getElementById(\'atcSection\');\nconst sounderpySectionEl=document.getElementById(\'sounderpySection\');',1)

old='  [metarSectionEl,tafSectionEl,synopSectionEl,knmiSectionEl,mapsSectionEl,atcSectionEl].forEach(s=>s?.classList.add(\'hidden\'));'
new='  [metarSectionEl,tafSectionEl,synopSectionEl,knmiSectionEl,mapsSectionEl,atcSectionEl,sounderpySectionEl].forEach(s=>s?.classList.add(\'hidden\'));'
if old in h:
    h=h.replace(old,new,1)
    print('hide list')

old2="  else if(name==='atc'){atcSectionEl?.classList.remove('hidden');}"
new2="  else if(name==='atc'){atcSectionEl?.classList.remove('hidden');}\n  else if(name==='sounderpy'){sounderpySectionEl?.classList.remove('hidden');loadSounderpyPlot();}"
if old2 in h and 'loadSounderpyPlot' not in h:
    h=h.replace(old2,new2,1)
    print('switch branch')

fn='''
function loadSounderpyPlot(){
  const img=document.getElementById('sounderpyImg');
  const st=document.getElementById('sounderpyStamp');
  if(img) img.src='plots/sounderpy-78988.png?t='+Date.now();
  fetch('plots/sounderpy-78988.txt?t='+Date.now()).then(r=>r.ok?r.text():'').then(t=>{ if(st) st.textContent=t||'Waiting for first SounderPy plot (00Z/12Z workflow).'; }).catch(()=>{ if(st) st.textContent='Plot not generated yet.'; });
}
'''
if 'function loadSounderpyPlot' not in h:
    h=h.replace('function switchTab(name){', fn+'function switchTab(name){',1)
    print('loader')

hp.write_text(h,encoding='utf-8')
print('ok', 'sounderpySection' in h)
