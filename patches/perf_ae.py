from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

# A — restore stations map when leaving Overzicht
old_a = """  if(tog) tog.style.display=which==='ovz'?'none':'inline-flex';
  if(map && which==='ovz') map.classList.add('hidden');
"""
new_a = """  if(tog) tog.style.display=which==='ovz'?'none':'inline-flex';
  if(map){
    if(which==='ovz'){
      map.dataset.wasOpen = map.classList.contains('hidden') ? '0' : '1';
      map.classList.add('hidden');
    } else if(map.dataset.wasOpen==='1'){
      map.classList.remove('hidden');
      try{ if(typeof map!=='undefined' && window.map) setTimeout(function(){ try{ window.map.invalidateSize(); }catch(e){} }, 200); }catch(e){}
    }
  }
"""
if old_a in h:
    h = h.replace(old_a, new_a, 1)
    print('A stations map restore')
else:
    print('WARN A')

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
    # looser
    if 'loadMapWindows);' in h and 'requestIdleCallback' in h:
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
    # inject before initMap if present
    if 'function initMap' in h:
        h = h.replace('function initMap', loader + 'function initMap', 1)
        print('D ensureLeafletCss fn')
    else:
        h = h.replace('function switchTab(name){', loader + 'function switchTab(name){', 1)
        print('D ensureLeafletCss before switchTab')

# call ensureLeafletCss at start of initMap
if 'function initMap' in h and 'ensureLeafletCss()' not in h[h.find('function initMap'):h.find('function initMap')+200]:
    # find initMap body start
    i = h.find('function initMap')
    brace = h.find('{', i)
    h = h[:brace+1] + '\n  ensureLeafletCss();' + h[brace+1:]
    print('D call in initMap')

# also on toggleMap open path
if "mapCard.classList.remove('hidden');initMap();" in h:
    h = h.replace(
        "mapCard.classList.remove('hidden');initMap();",
        "mapCard.classList.remove('hidden');ensureLeafletCss();initMap();",
        1)
    print('D toggleMap')

# E — IntersectionObserver for maps iframes
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
  // First frame immediately (above the fold)
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

if old_e in h:
    h = h.replace(old_e, new_e, 1)
    print('E intersection observer')
else:
    print('WARN E exact')
    # try replace function body by finding start/end
    start = h.find('function ensureMapsTabWindowsLoaded(){')
    if start >= 0:
        # find matching close at same indent level - simplistic: next\nlet __ventuskyFrameSet
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
print('boot loadMapWindows call', 'loadMapWindows);' in h and 'requestIdleCallback' in h)
print('ensureLeafletCss', 'ensureLeafletCss' in h)
print('IntersectionObserver maps', 'IntersectionObserver' in h[h.find('ensureMapsTabWindowsLoaded'):h.find('ensureMapsTabWindowsLoaded')+800] if 'ensureMapsTabWindowsLoaded' in h else False)
