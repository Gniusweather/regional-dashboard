from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

# 1) TNCC group first, TNCA second
old_g = "const groups=[[0,1],[2,3]];"
new_g = "const groups=[[2,3],[0,1]]; // TNCC on top, TNCA below"
if old_g in h:
    h = h.replace(old_g, new_g, 1)
    print('groups reordered')
else:
    print('WARN groups')

# 2) Slightly larger fonts on synop cards / headers (second definition wins for m-lbl/m-val)
repls = [
    ('.synop-blt-header .station{font-size:var(--fs-15);',
     '.synop-blt-header .station{font-size:var(--fs-17);'),
    ('.synop-blt-time{font-size:var(--fs-13);',
     '.synop-blt-time{font-size:var(--fs-15);'),
    ('.synop-card-id{font-family:var(--mono);font-size:var(--fs-16);',
     '.synop-card-id{font-family:var(--mono);font-size:var(--fs-18);'),
    ('.synop-card-time{font-family:var(--mono);font-size:var(--fs-12);',
     '.synop-card-time{font-family:var(--mono);font-size:var(--fs-14);'),
]
for a,b in repls:
    if a in h:
        h = h.replace(a, b, 1)
        print('css', b[:50])
    else:
        print('miss', a[:40])

# Card metric labels/values — prefer the later (card) block near synop-card-id
# Replace the second occurrence of each if two exist
def replace_nth(text, old, new, n):
    parts = text.split(old)
    if len(parts) <= n:
        return text, False
    return old.join(parts[:n]) + new + old.join(parts[n:]), True

h, ok = replace_nth(
    h,
    '.synop-m-lbl{\n  font-size:var(--fs-10);letter-spacing:0.9px;font-weight:700;\n  color:rgba(200,225,255,0.32);margin-bottom:3px;text-transform:uppercase;\n}',
    '.synop-m-lbl{\n  font-size:var(--fs-11);letter-spacing:0.9px;font-weight:700;\n  color:rgba(200,225,255,0.32);margin-bottom:3px;text-transform:uppercase;\n}',
    1,
)
print('m-lbl card', ok)
h, ok = replace_nth(
    h,
    '.synop-m-val{font-size:var(--fs-15);font-weight:600;color:#d0e8ff;white-space:nowrap;overflow:hidden;}',
    '.synop-m-val{font-size:var(--fs-17);font-weight:600;color:#d0e8ff;white-space:nowrap;overflow:hidden;}',
    1,
)
print('m-val card', ok)

# Also bump first (older) m-val if still used
if '.synop-m-val{font-size:var(--fs-20);' in h:
    h = h.replace('.synop-m-val{font-size:var(--fs-20);', '.synop-m-val{font-size:var(--fs-21);', 1)
    print('m-val primary bumped')

hp.write_text(h, encoding='utf-8')
print('groups TNCC first', 'groups=[[2,3],[0,1]]' in h)
