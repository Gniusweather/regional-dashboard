from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

fn = '''function loadHeaderMapWindows(){
  document.querySelectorAll('.windy-widget-header iframe[data-src]').forEach(function(f){
    if(f.dataset.headerLoaded==='1') return;
    var ds=f.getAttribute('data-src');
    if(ds){ f.setAttribute('src', ds); f.dataset.headerLoaded='1'; }
  });
}
'''

if 'function loadHeaderMapWindows' not in h:
    if 'function loadMapWindows' in h:
        h = h.replace('function loadMapWindows', fn + 'function loadMapWindows', 1)
        print('inserted loadHeaderMapWindows')
    else:
        h = h.replace('function ensureMapsTabWindowsLoaded', fn + 'function ensureMapsTabWindowsLoaded', 1)
        print('inserted before ensureMaps')
else:
    print('fn exists')

old = '''  }finally{
    // Maps load only when the Maps tab is opened (ensureMapsTabWindowsLoaded).
  }
'''
new = '''  }finally{
    // Header satellite/radar only (Maps-tab embeds stay tab-lazy).
    (window.requestIdleCallback||function(cb){return setTimeout(cb,400);})(loadHeaderMapWindows);
  }
'''
if old in h:
    h = h.replace(old, new, 1)
    print('boot header load')
elif 'loadHeaderMapWindows);' not in h:
    # looser: any comment-only finally from A-E
    if 'Maps load only when the Maps tab is opened' in h:
        h = h.replace(
            '// Maps load only when the Maps tab is opened (ensureMapsTabWindowsLoaded).',
            '(window.requestIdleCallback||function(cb){return setTimeout(cb,400);})(loadHeaderMapWindows);',
            1)
        print('boot loose')
    else:
        print('WARN boot site')
else:
    print('boot already')

hp.write_text(h, encoding='utf-8')
print('header fn', 'function loadHeaderMapWindows' in h)
print('boot call', 'loadHeaderMapWindows' in h[h.find('}finally{'):h.find('}finally{')+300] if '}finally{' in h else False)
