from pathlib import Path
p=Path('index.html'); t=p.read_text()
if 'data-tab="atc"' not in t:
    t=t.replace(
        'data-tab="stations" role="tab" aria-selected="false">⊎ Stations</button>',
        'data-tab="stations" role="tab" aria-selected="false">⊎ Stations</button>\n    <button class="tab-btn" data-tab="atc" role="tab" aria-selected="false">ATC</button>',
        1)
    if 'data-tab="atc"' not in t:
        t=t.replace('</nav>', '    <button class="tab-btn" data-tab="atc" role="tab" aria-selected="false">ATC</button>\n  </nav>', 1)
p.write_text(t)
print('atc nav', 'data-tab="atc"' in t)
