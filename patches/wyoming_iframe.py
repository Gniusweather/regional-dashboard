from pathlib import Path
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')

h=h.replace('>SounderPy</button>','>Wyoming</button>',1)

old='''      <div class="section-header">
        <div class="section-title">SounderPy · TNCC 78988</div>
        <div class="section-controls" style="font-size:12px;color:var(--muted)">Wyoming RAOB · full · dark · updates 00Z/12Z</div>
      </div>
      <div style="background:#0b1220;border-radius:12px;overflow:auto;border:1px solid var(--border);padding:8px">
        <img id="sounderpyImg" alt="SounderPy TNCC sounding" style="width:100%;max-width:1200px;display:block;margin:0 auto;background:#111" src="plots/sounderpy-78988.png">
        <p id="sounderpyStamp" style="color:#8ea0b8;font-size:12px;margin:8px"></p>
      </div>'''

new='''      <div class="section-header">
        <div class="section-title">Wyoming Skew-T · 78988 TNCC</div>
        <div class="section-controls" style="font-size:12px;color:var(--muted)">Official UWyo plot · latest 00Z/12Z · iframe</div>
      </div>
      <div style="background:#fff;border-radius:12px;overflow:hidden;border:1px solid var(--border)">
        <iframe id="wyomingSkewtFrame" title="University of Wyoming Skew-T 78988" style="width:100%;height:min(92vh,1200px);border:0;background:#fff" src="about:blank"></iframe>
        <p id="sounderpyStamp" style="color:#8ea0b8;font-size:12px;margin:8px;background:#0b1220"></p>
      </div>'''

if old in h:
    h=h.replace(old,new,1)
    print('section html')
else:
    print('WARN section')
    i=h.find('SounderPy')
    print(h[i:i+200] if i>=0 else 'no sounderpy text')

fn='''function wyomingLatestUrl(){
  const now=new Date();
  let y=now.getUTCFullYear(), mo=now.getUTCMonth(), d=now.getUTCDate(), hr=now.getUTCHours();
  let hour=12;
  if(hr>=13) hour=12;
  else if(hr>=1) hour=0;
  else { hour=12; const t=new Date(Date.UTC(y,mo,d)-12*3600*1000); y=t.getUTCFullYear(); mo=t.getUTCMonth(); d=t.getUTCDate(); }
  const iso=y+'-'+String(mo+1).padStart(2,'0')+'-'+String(d).padStart(2,'0')+'%20'+String(hour).padStart(2,'0')+':00:00';
  return {
    page:'https://weather.uwyo.edu/wsgi/sounding?src=BUFR&datetime='+iso+'&id=78988&type=GIF:SKEWT',
    png:'https://weather.uwyo.edu/wsgi/sounding?src=BUFR&datetime='+iso+'&id=78988&type=PNG:SKEWT',
    label:y+'-'+String(mo+1).padStart(2,'0')+'-'+String(d).padStart(2,'0')+' '+String(hour).padStart(2,'0')+'Z  station 78988'
  };
}
function loadSounderpyPlot(){
  const u=wyomingLatestUrl();
  const fr=document.getElementById('wyomingSkewtFrame');
  const st=document.getElementById('sounderpyStamp');
  if(fr) fr.src=u.page;
  if(st) st.innerHTML=u.label+' · <a href="'+u.page+'" target="_blank" rel="noopener" style="color:#55c1ff">open Wyoming</a> · <a href="'+u.png+'" target="_blank" rel="noopener" style="color:#55c1ff">PNG</a>';
}
'''

if 'function wyomingLatestUrl' not in h:
    if 'function loadSounderpyPlot(){' in h:
        import re
        h=re.sub(r'function loadSounderpyPlot\(\)\{.*?\n\}', fn.rstrip()+'\n', h, count=1, flags=re.S)
        print('replaced loader')
    else:
        h=h.replace('function switchTab(name){', fn+'function switchTab(name){',1)
        print('inserted loader')
else:
    print('loader exists')

hp.write_text(h,encoding='utf-8')
print('wyoming frame', 'wyomingSkewtFrame' in h)
print('wyoming fn', 'wyomingLatestUrl' in h)
