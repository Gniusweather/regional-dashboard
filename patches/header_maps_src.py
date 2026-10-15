from pathlib import Path
import re
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

start = h.find('windy-widget windy-widget-header')
end = h.find('<!-- Vis Widget', start)
if end < 0:
    end = h.find('class="weather-widget', start)
if start < 0 or end < 0:
    raise SystemExit('header block not found')

block = h[start:end]

def fix_iframe(m):
    tag = m.group(0)
    if re.search(r'\ssrc="https?://', tag):
        return tag
    ds = re.search(r'data-src="([^"]+)"', tag)
    if not ds:
        return tag
    url = ds.group(1)
    # inject src before data-src
    tag = tag.replace('data-src="'+url+'"', 'src="'+url+'" data-src="'+url+'"')
    if 'satellite' in tag.lower():
        if 'fetchpriority' not in tag:
            tag = tag.replace('<iframe ', '<iframe fetchpriority="high" loading="eager" ')
    else:
        if 'loading=' not in tag:
            tag = tag.replace('<iframe ', '<iframe loading="eager" ')
    return tag

new_block, n = re.subn(r'<iframe\b[^>]*>', fix_iframe, block, flags=re.S)
print('iframes fixed', n)
h = h[:start] + new_block + h[end:]
hp.write_text(h, encoding='utf-8')
# verify
b2 = h[h.find('windy-widget windy-widget-header'):h.find('windy-widget windy-widget-header')+2000]
print('src=', b2.count('src="https://embed.windy.com'))
print('data-src=', b2.count('data-src="https://embed.windy.com'))
