from pathlib import Path
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')

# defer blocking sonde script
h=h.replace('<script src="sonde-noaa.js?v=30"></script>','<script src="sonde-noaa.js?v=30" defer></script>',1)

# defer leaflet js
h=h.replace('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>',
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin="" defer></script>',1)

# fonts: non-blocking
oldf='<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Barlow+Condensed:wght@300;400;500;600;700;800&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet">'
newf='<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Barlow+Condensed:wght@300;400;500;600;700;800&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'">\n<noscript><link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Barlow+Condensed:wght@300;400;500;600;700;800&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet"></noscript>'
if oldf in h:
    h=h.replace(oldf,newf,1)
    print('fonts')
else:
    print('WARN fonts')

# hidden sections skip paint work
if 'content-visibility:auto' not in h:
    h=h.replace('.hidden{display:none;}','.hidden{display:none!important;}\n.table-wrapper:not(.hidden){content-visibility:auto;contain-intrinsic-size:1px 700px;}',1)
    print('css')

def lazify(html, marker, file):
    a=f'src="{file}"'
    if a in html and f'data-src="{file}"' not in html:
        html=html.replace(a, f'src="about:blank" data-src="{file}"',1)
        print('lazy', file)
    else:
        print('skip', file, a in html)
    return html

h=lazify(h, 'SYNOP encoder', 'encoders.html')
h=lazify(h, 'Live ATC', 'atc.html')
h=lazify(h, 'Overzicht', 'overzicht.html')

helper='''function lazyLoadIframe(root){
  if(!root) return;
  const f=root.tagName==='IFRAME'?root:root.querySelector('iframe');
  if(!f) return;
  const ds=f.getAttribute('data-src');
  if(ds && (f.getAttribute('src')==='about:blank' || !f.getAttribute('src') || f.dataset.lazy!=='1')){
    f.src=ds; f.dataset.lazy='1';
  }
}
'''
if 'function lazyLoadIframe' not in h:
    h=h.replace('function synopSub(which){', helper+'function synopSub(which){',1)
    print('helper')

old='  if(which===\'day\') loadDaySummary78988();\n}'
new='  if(which===\'day\') loadDaySummary78988();\n  if(which===\'encode\') lazyLoadIframe(enc);\n}'
if old in h:
    h=h.replace(old,new,1)
    print('synop encode lazy')

if "if(which==='ovz'){ try{ var f=ovz&&ovz.querySelector('iframe');" in h:
    h=h.replace(
        "if(which==='ovz'){ try{ var f=ovz&&ovz.querySelector('iframe'); if(f&&(!f.dataset.loaded)){ f.src=f.src; f.dataset.loaded='1'; } }catch(e){} }",
        "if(which==='ovz'){ lazyLoadIframe(ovz); }",
        1)
    print('ovz lazy')

h=h.replace("else if(name==='atc'){atcSectionEl?.classList.remove('hidden');}",
            "else if(name==='atc'){atcSectionEl?.classList.remove('hidden');lazyLoadIframe(atcSectionEl);}",1)
print('atc switch')

oldm='''function ensureMapsTabWindowsLoaded(){
  document.querySelectorAll('#mapsSection .windy-widget iframe[data-src]').forEach(function(f){
    if(!f.getAttribute('src')||f.dataset.mapsLoaded!=='1'){
      f.setAttribute('src', f.getAttribute('data-src'));
      f.dataset.mapsLoaded='1';
    }
  });
  if(!__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; }
}'''
newm='''function ensureMapsTabWindowsLoaded(){
  const frames=[].slice.call(document.querySelectorAll('#mapsSection iframe[data-src], #mapsSection iframe#ventuskyFrame'));
  frames.forEach(function(f,i){
    if(f.dataset.mapsLoaded==='1') return;
    const kick=function(){
      const ds=f.getAttribute('data-src');
      if(ds) f.setAttribute('src', ds);
      f.dataset.mapsLoaded='1';
      if(f.id==='ventuskyFrame' && !__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; }
    };
    if(i===0) kick();
    else setTimeout(kick, 280*i);
  });
  if(!__ventuskyFrameSet){ setTimeout(function(){ if(!__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; } }, 200); }
}'''
if oldm in h:
    h=h.replace(oldm,newm,1)
    print('stagger maps')
else:
    print('WARN maps')
    print(h[h.find('function ensureMapsTabWindowsLoaded'):h.find('function ensureMapsTabWindowsLoaded')+420])

hp.write_text(h,encoding='utf-8')
print('done', 'lazyLoadIframe' in h, h.count('about:blank'))
