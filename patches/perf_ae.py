from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

# A — restore stations map when leaving Overzicht (use mapCard; do not shadow Leaflet `map`)
old_a = """function stationsSub(which){
  const ovz=document.getElementById('ovz-wrap');
  const list=document.getElementById('stationsList');
  const map=document.getElementById('stationsMapCard');
  if(ovz) ovz.style.display=which==='ovz'?'block':'none';
  if(list) list.style.display=which==='ovz'?'none':'grid';
  document.querySelectorAll('#stationsSection .summary').forEach(function(el){ el.style.display=which==='ovz'?'none':'flex'; });
  const tog=document.getElementById('toggleMap');
  if(tog) tog.style.display=which==='ovz'?'none':'inline-flex';
  if(map && which==='ovz') map.classList.add('hidden');
"""
new_a = """function stationsSub(which){
  const ovz=document.getElementById('ovz-wrap');
  const list=document.getElementById('stationsList');
  const mapCard=document.getElementById('stationsMapCard');
  if(ovz) ovz.style.display=which==='ovz'?'block':'none';
  if(list) list.style.display=which==='ovz'?'none':'grid';
  document.querySelectorAll('#stationsSection .summary').forEach(function(el){ el.style.display=which==='ovz'?'none':'flex'; });
  const tog=document.getElementById('toggleMap');
  if(tog) tog.style.display=which==='ovz'?'none':'inline-flex';
  if(mapCard){
    if(which==='ovz'){
      mapCard.dataset.wasOpen = mapCard.classList.contains('hidden') ? '0' : '1';
      mapCard.classList.add('hidden');
    } else if(mapCard.dataset.wasOpen==='1'){
      mapCard.classList.remove('hidden');
      setTimeout(function(){ try{ if(typeof map!=='undefined' && map && map.invalidateSize) map.invalidateSize(); }catch(e){} }, 200);
    }
  }
"""
if old_a in h:
    h = h.replace(old_a, new_a, 1)
    print('A stations map restore')
else:
    print('WARN A')
    i = h.find('function stationsSub')
    print(repr(h[i:i+500]))

# B — remove boot-time loadMapWindows
old_b = """  }finally{
    // Load the heavy map iframes once the data has painted (idle if supported).
    (window.requestIdleCallback||function(cb){return setTimeout(cb,1200);})(loadMapWindows);
  }
"""
new_b = """  }finally{
    // Maps load only when the Maps tab is opened (ensureMapsTabWindowsLoaded).
  }
"""
if old_b in h:
    h = h.replace(old_b, new_b, 1)
    print('B remove boot maps')
else:
    print('WARN B')
    if '(window.requestIdleCallback||function(cb){return setTimeout(cb,1200);})(loadMapWindows);' in h:
        h = h.replace(
            '(window.requestIdleCallback||function(cb){return setTimeout(cb,1200);})(loadMapWindows);',
            '/* maps: tab-only load */',
            1)
        print('B loose')

# C — tickClocks skip when hidden
old_c = 'function tickClocks(){\n  try{'
new_c = 'function tickClocks(){\n  if(document.hidden) return;\n  try{'
if old_c in h:
    h = h.replace(old_c, new_c, 1)
    print('C tickClocks')
else:
    print('WARN C')

# D — Leaflet CSS on demand
old_css = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>'
if old_css in h:
    h = h.replace(old_css, '<!-- leaflet.css loaded on first Stations map open -->', 1)
    print('D remove leaflet css head')
else:
    print('WARN D css')

loader = '''function ensureLeafletCss(){
  if(document.getElementById('leaflet-css-rwc')) return;
  var l=document.createElement('link');
  l.id='leaflet-css-rwc';
  l.rel='stylesheet';
  l.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  l.crossOrigin='';
  document.head.appendChild(l);
}
'''
if 'function ensureLeafletCss' not in h:
    if 'function initMap' in h:
        h = h.replace('function initMap', loader + 'function initMap', 1)
        print('D ensureLeafletCss fn')
    else:
        h = h.replace('function switchTab(name){', loader + 'function switchTab(name){', 1)
        print('D ensureLeafletCss before switchTab')

# call ensureLeafletCss at start of initMap (after possible injection above)
i = h.find('function initMap')
if i >= 0:
    brace = h.find('{', i)
    snippet = h[brace:brace+80]
    if 'ensureLeafletCss()' not in snippet:
        h = h[:brace+1] + '\n  ensureLeafletCss();' + h[brace+1:]
        print('D call in initMap')

if "mapCard.classList.remove('hidden');initMap();" in h and "ensureLeafletCss();initMap()" not in h:
    h = h.replace(
        "mapCard.classList.remove('hidden');initMap();",
        "mapCard.classList.remove('hidden');ensureLeafletCss();initMap();",
        1)
    print('D toggleMap')

# E — IntersectionObserver for maps iframes
new_e = '''function ensureMapsTabWindowsLoaded(){
  const frames=[].slice.call(document.querySelectorAll('#mapsSection iframe[data-src], #mapsSection iframe#ventuskyFrame'));
  function kick(f){
    if(!f || f.dataset.mapsLoaded==='1') return;
    const ds=f.getAttribute('data-src');
    if(ds) f.setAttribute('src', ds);
    f.dataset.mapsLoaded='1';
    if(f.id==='ventuskyFrame' && !__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; }
  }
  if(!frames.length){
    if(!__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; }
    return;
  }
  kick(frames[0]);
  const rest=frames.slice(1);
  if(!rest.length){
    if(!__ventuskyFrameSet){ setTimeout(function(){ if(!__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; } }, 150); }
    return;
  }
  if('IntersectionObserver' in window){
    const io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(en.isIntersecting){
          kick(en.target);
          io.unobserve(en.target);
        }
      });
    }, {root:null, rootMargin:'120px 0px', threshold:0.01});
    rest.forEach(function(f){ io.observe(f); });
  } else {
    rest.forEach(function(f,i){ setTimeout(function(){ kick(f); }, 350*(i+1)); });
  }
  if(!__ventuskyFrameSet){ setTimeout(function(){ if(!__ventuskyFrameSet){ setVentuskyFrame(); __ventuskyFrameSet=true; } }, 200); }
}'''

old_e = '''function ensureMapsTabWindowsLoaded(){
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

if old_e in h:
    h = h.replace(old_e, new_e, 1)
    print('E intersection observer')
else:
    print('WARN E exact')
    start = h.find('function ensureMapsTabWindowsLoaded(){')
    if start >= 0:
        end = h.find('\nlet __ventuskyFrameSet', start)
        if end > start:
            h = h[:start] + new_e + h[end:]
            print('E replaced by marker')
        else:
            print('WARN E end')
    else:
        print('WARN E missing')

hp.write_text(h, encoding='utf-8')
print('done A-E')
