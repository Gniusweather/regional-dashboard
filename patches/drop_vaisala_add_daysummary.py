from pathlib import Path

enc = Path('encoders.html')
t = enc.read_text(encoding='utf-8')

# Drop the Vaisala nav button (exact line from file)
lines = []
for line in t.splitlines(True):
    if 'showEnc(' in line and 'vaisala' in line and 'Vaisala' in line:
        continue
    lines.append(line)
t = ''.join(lines)

# Cut the Vaisala HTML panel
marker = 'id="synop-sub-vaisala"'
i = t.find(marker)
if i >= 0:
    start = t.rfind('<div', 0, i)
    script = t.find('<script', i)
    if start >= 0 and script > start:
        t = t[:start] + t[script:]
        print('cut panel', script - start)
else:
    print('no panel marker')

enc.write_text(t, encoding='utf-8')
print('button left', any('Vaisala</button>' in ln for ln in t.splitlines()))
print('panel left', 'synop-sub-vaisala' in t)

# Day summary already patched in index; keep idempotent
idx = Path('index.html')
h = idx.read_text(encoding='utf-8')
print('day tab', "synopSub('day')" in h and 'synop-day-wrap' in h)
