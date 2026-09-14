from pathlib import Path
import re

enc = Path('encoders.html')
t = enc.read_text(encoding='utf-8')

# Remove Vaisala subnav button
t = t.replace(
    '<button type="button" onclick="showEnc(\'vaisala\',this)">Vaisala</button>\n',
    '',
)
t = t.replace(
    '<button type="button" onclick="showEnc(\'vaisala\',this)">Vaisala</button>',
    '',
)

# Remove Vaisala panel
start = t.find('<div class="sub-panel" id="synop-sub-vaisala">')
if start < 0:
    start = t.find('id="synop-sub-vaisala"')
    if start >= 0:
        start = t.rfind('<div', 0, start)
if start >= 0:
    # panel ends at the extra leftover sub-panel / wrap close before <script>
    script = t.find('<script', start)
    chunk = t[start:script]
    # keep a clean close of wrap if we ate it
    t = t[:start] + t[script:]
    print('removed vaisala panel bytes', script-start)
else:
    print('vaisala panel not found')

# Neutralize showEnc vaisala branch (keep function working)
t = t.replace(" if(name==='vaisala'){tplFillFromEnc('va');vaUpdate();}", '')
t = t.replace(" if(name==='vaisala'){tplFillFromEnc('va');vaUpdate();}", '')

enc.write_text(t, encoding='utf-8')
print('vaisala button left', 'showEnc(\'vaisala\'' in t or 'Vaisala</button>' in t)
print('panel left', 'synop-sub-vaisala' in t)

# SYNOP tab: Reports | Encode | Day summary
idx = Path('index.html')
h = idx.read_text(encoding='utf-8')
if "synopSub('day')" not in h:
    h = h.replace(
        "<button type=\"button\" class=\"btn-primary\" id=\"synop-sub-encode\" onclick=\"synopSub('encode')\" style=\"font-size:12px;height:28px;padding:4px 10px;opacity:.75\">Encode</button>",
        "<button type=\"button\" class=\"btn-primary\" id=\"synop-sub-encode\" onclick=\"synopSub('encode')\" style=\"font-size:12px;height:28px;padding:4px 10px;opacity:.75\">Encode</button>\n          <button type=\"button\" class=\"btn-primary\" id=\"synop-sub-day\" onclick=\"synopSub('day')\" style=\"font-size:12px;height:28px;padding:4px 10px;opacity:.75\">Day summary</button>",
        1,
    )
if 'id="synop-day-wrap"' not in h:
    h = h.replace(
        '<div id="synop-encode-wrap"',
        '<div id="synop-day-wrap" style="display:none;height:min(78vh,820px);border-radius:10px;overflow:hidden;border:1px solid var(--border);margin-bottom:10px"><iframe src="overzicht.html" title="Day summary" style="width:100%;height:100%;border:0;background:#fff"></iframe></div>\n        <div id="synop-encode-wrap"',
        1,
    )

old = '''function synopSub(which){
  const enc=document.getElementById('synop-encode-wrap');
  const tbl=document.getElementById('synop-table');
  const bar=document.getElementById('synop-updated');
  if(enc) enc.style.display=which==='encode'?'block':'none';
  if(tbl) tbl.style.display=which==='encode'?'none':'block';
  if(bar) bar.style.display=which==='encode'?'none':'block';
  const a=document.getElementById('synop-sub-encode'), b=document.getElementById('synop-sub-reports');
  if(a) a.style.opacity=which==='encode'?'1':'.75';
  if(b) b.style.opacity=which==='encode'?'.75':'1';
}'''
new = '''function synopSub(which){
  const enc=document.getElementById('synop-encode-wrap');
  const day=document.getElementById('synop-day-wrap');
  const tbl=document.getElementById('synop-table');
  const bar=document.getElementById('synop-updated');
  if(enc) enc.style.display=which==='encode'?'block':'none';
  if(day) day.style.display=which==='day'?'block':'none';
  if(tbl) tbl.style.display=(which==='encode'||which==='day')?'none':'block';
  if(bar) bar.style.display=(which==='encode'||which==='day')?'none':'block';
  const a=document.getElementById('synop-sub-encode');
  const b=document.getElementById('synop-sub-reports');
  const c=document.getElementById('synop-sub-day');
  if(a) a.style.opacity=which==='encode'?'1':'.75';
  if(b) b.style.opacity=which==='reports'?'1':'.75';
  if(c) c.style.opacity=which==='day'?'1':'.75';
}'''
if old in h:
    h = h.replace(old, new, 1)
    print('synopSub replaced')
elif "synopSub('day')" in h:
    print('synopSub already has day')
else:
    print('WARN synopSub block not matched')
    # fallback insert day handling after first enc display line
    if "const day=document.getElementById('synop-day-wrap')" not in h:
        h = h.replace(
            "const enc=document.getElementById('synop-encode-wrap');",
            "const enc=document.getElementById('synop-encode-wrap');\n  const day=document.getElementById('synop-day-wrap');",
            1,
        )

idx.write_text(h, encoding='utf-8')
print('day btn', "synopSub('day')" in h)
print('day wrap', 'synop-day-wrap' in h)
