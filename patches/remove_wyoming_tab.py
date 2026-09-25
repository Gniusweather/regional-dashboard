from pathlib import Path
import re
hp=Path('index.html')
h=hp.read_text(encoding='utf-8')

h=h.replace('\n      <button class="tab-btn" data-tab="sounderpy" role="tab" aria-selected="false">Wyoming</button>','')

h=re.sub(
    r'\s*<div id="sounderpySection" class="table-wrapper fade-in hidden">.*?</div>\s*(?=<div id="atcSection")',
    '\n    ',
    h, count=1, flags=re.S)

h=h.replace('\nconst sounderpySectionEl=document.getElementById(\'sounderpySection\');','')
h=h.replace(',sounderpySectionEl','')
h=h.replace("\n  else if(name==='sounderpy'){sounderpySectionEl?.classList.remove('hidden');loadSounderpyPlot();}",'')

h=re.sub(r'function wyomingLatestUrl\(\)\{[\s\S]*?function loadSounderpyPlot\(\)\{[\s\S]*?\n\}\n','',h,count=1)
# leftover loader only
h=re.sub(r'function loadSounderpyPlot\(\)\{[\s\S]*?\n\}\n','',h,count=1)

hp.write_text(h,encoding='utf-8')
print('sounderpy left', h.count('sounderpy'))
print('wyoming fn', 'wyomingLatestUrl' in h)
print('wyoming btn', 'data-tab="sounderpy"' in h)
