from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

# 1) Preconnect Windy embeds
if 'embed.windy.com' not in h[h.find('<head>'):h.find('</head>')]:
    h = h.replace(
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://embed.windy.com" crossorigin>\n'
        '<link rel="dns-prefetch" href="https://embed.windy.com">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        1)
    print('preconnect')
else:
    print('preconnect exists')

# 2) Give header iframes real src during HTML parse (eager)
def promote(html, title_snip):
    # find iframe with title containing snip inside header widget only - operate on full for simplicity
    import re
    def repl(m):
        tag = m.group(0)
        if 'data-src=' not in tag:
            return tag
        if 'src="http' in tag or "src='http" in tag:
            return tag
        # copy data-src to src, keep data-src, add loading/fetchpriority
        ds = re.search(r'data-src="([^"]+)"', tag)
        if not ds:
            return tag
        url = ds.group(1)
        tag = tag.replace('data-src="'+url+'"', 'src="'+url+'" data-src="'+url+'" loading="eager"')
        if 'Satellite' in tag or 'satellite' in tag:
            tag = tag.replace('loading="eager"', 'loading="eager" fetchpriority="high"')
        return tag
    # only header pair: between windy-widget-header and weather-widget
    start = html.find('windy-widget windy-widget-header')
    end = html.find('<!-- Vis Widget', start)
    if start < 0 or end < 0:
        end = html.find('weather-widget', start)
    if start < 0 or end < 0:
        print('WARN header block')
        return html
    block = html[start:end]
    new_block = re.sub(r'<iframe\b[^>]*>', repl, block)
    if new_block != block:
        html = html[:start] + new_block + html[end:]
        print('promoted src in header')
    else:
        print('no iframe change')
    return html

h = promote(h, 'Satellite')

# 3) loadHeaderMapWindows: mark already-src as loaded; kick any remaining ASAP
old_fn = '''function loadHeaderMapWindows(){
  document.querySelectorAll('.windy-widget-header iframe[data-src]').forEach(function(f){
    if(f.dataset.headerLoaded==='1') return;
    var ds=f.getAttribute('data-src');
    if(ds){ f.setAttribute('src', ds); f.dataset.headerLoaded='1'; }
  });
}'''
new_fn = '''function loadHeaderMapWindows(){
  var frames=[].slice.call(document.querySelectorAll('.windy-widget-header iframe'));
  frames.forEach(function(f,i){
    if(f.dataset.headerLoaded==='1') return;
    var ds=f.getAttribute('data-src')||f.getAttribute('src');
    if(!ds) return;
    var kick=function(){
      if(f.getAttribute('src')!==ds) f.setAttribute('src', ds);
      f.dataset.headerLoaded='1';
    };
    // already has src from HTML parse — just mark; otherwise set immediately (sat) / slight stagger (radar)
    if(f.getAttribute('src') && f.getAttribute('src')!=='about:blank'){
      f.dataset.headerLoaded='1';
      return;
    }
    if(i===0) kick();
    else setTimeout(kick, 60);
  });
}'''
if old_fn in h:
    h = h.replace(old_fn, new_fn, 1)
    print('fn updated')
else:
    print('WARN fn')

# 4) Call at START of init, not after METAR await
old_init = '''(async function init(){
  try{
    primeFromCache(); // instant paint from last-known data while fresh reports load
    await Promise.allSettled([refreshAllMetars(),loadAllTafs(),loadAllSynops(),loadKnmiData()]);'''
new_init = '''(async function init(){
  try{
    try{ loadHeaderMapWindows(); }catch(e){}
    primeFromCache(); // instant paint from last-known data while fresh reports load
    await Promise.allSettled([refreshAllMetars(),loadAllTafs(),loadAllSynops(),loadKnmiData()]);'''
if old_init in h:
    h = h.replace(old_init, new_init, 1)
    print('early init call')
else:
    print('WARN init')

# 5) Soften finally delay — still safe if already loaded
old_fin = '''(window.requestIdleCallback||function(cb){return setTimeout(cb,400);})(loadHeaderMapWindows);'''
new_fin = '''try{ loadHeaderMapWindows(); }catch(e){}'''
if old_fin in h:
    h = h.replace(old_fin, new_fin, 1)
    print('finally immediate')
else:
    print('WARN finally')

hp.write_text(h, encoding='utf-8')
print('header src count', h[h.find('windy-widget-header'):h.find('windy-widget-header')+1500].count('src="https://embed.windy.com'))
