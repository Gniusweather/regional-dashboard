from pathlib import Path

p = Path('index.html')
h = p.read_text(encoding='utf-8')

old_wrap = '<div id="synop-day-wrap" style="display:none;height:min(78vh,820px);border-radius:10px;overflow:hidden;border:1px solid var(--border);margin-bottom:10px"><iframe src="overzicht.html" title="Day summary" style="width:100%;height:100%;border:0;background:#fff"></iframe></div>'
new_wrap = '''<div id="synop-day-wrap" style="display:none;margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px">
            <div style="font-weight:700;letter-spacing:.5px">78988 TNCC Hato · day SYNOPs</div>
            <button type="button" class="btn-primary" style="font-size:12px;height:28px;padding:4px 10px" onclick="loadDaySummary78988(true)">↻ Refresh</button>
          </div>
          <div id="synop-day-body" style="color:var(--muted)">Open Day summary to load 78988 reports.</div>
        </div>'''

if old_wrap in h:
    h = h.replace(old_wrap, new_wrap, 1)
    print('replaced iframe wrap')
elif 'id="synop-day-body"' in h:
    print('day body already present')
else:
    print('WARN wrap not found; inserting before encode wrap')
    h = h.replace('<div id="synop-encode-wrap"', new_wrap + '\n        <div id="synop-encode-wrap"', 1)

# Call loader when Day summary tab opens
if "loadDaySummary78988()" not in h:
    h = h.replace(
        "if(c) c.style.opacity=which==='day'?'1':'.75';\n}",
        "if(c) c.style.opacity=which==='day'?'1':'.75';\n  if(which==='day') loadDaySummary78988();\n}",
        1,
    )
    print('hooked synopSub')

fn = r'''
function parseOgimetSynopLines(text){
  const rows=[];
  String(text||'').split(/\n+/).forEach(function(line){
    line=line.trim();
    if(!line || line[0]==='#') return;
    if(line.indexOf('78988')<0) return;
    let msg=line, y=null, mo=null, da=null, hh=null, mm='00';
    const csv=line.split(',');
    if(csv.length>=7 && csv[0].trim()==='78988'){
      y=csv[1]; mo=csv[2]; da=csv[3]; hh=csv[4]; mm=csv[5];
      msg=csv.slice(6).join(',').trim();
    }
    const aaxx=msg.match(/AAXX\s+\d{5}[\s\S]*/);
    const raw=aaxx?aaxx[0]:msg;
    const decoded=decodeSynopText(raw);
    const rep=(decoded.reports||[]).find(function(r){return r.stn==='78988';}) || (decoded.reports||[])[0];
    if(!rep) return;
    const time = (hh!=null) ? (String(hh).padStart(2,'0')+':'+String(mm||'00').padStart(2,'0')+'Z') : (decoded.bulletinTime||'—');
    rows.push({time:time, y:y, mo:mo, da:da, raw:raw, rep:rep, decoded:decoded});
  });
  rows.sort(function(a,b){ return String(a.time).localeCompare(String(b.time)); });
  return rows;
}
async function loadDaySummary78988(force){
  const host=document.getElementById('synop-day-body');
  if(!host) return;
  if(!force && host.dataset.loaded==='1') return;
  host.innerHTML='Loading 78988 SYNOPs for today…';
  const now=new Date();
  const pad=function(n){return String(n).padStart(2,'0');};
  const Y=now.getUTCFullYear(), Mo=pad(now.getUTCMonth()+1), Da=pad(now.getUTCDate());
  const url='https://www.ogimet.com/cgi-bin/getsynop?block=78988&begin='+Y+Mo+Da+'0000&end='+Y+Mo+Da+'2359';
  let text='';
  try{
    const out=await fetchWithRetries(url,2);
    if(out && out.ok && out.text) text=out.text;
  }catch(e){}
  if(!text){
    host.innerHTML='Could not load Ogimet 78988 day file.';
    return;
  }
  const rows=parseOgimetSynopLines(text);
  if(!rows.length){
    host.innerHTML='No 78988 SYNOP reports found for '+Y+'-'+Mo+'-'+Da+' UTC.';
    return;
  }
  const cards=rows.map(function(row){
    let card='';
    try{ card=makeSynopCard(row.rep, row.time); }catch(e){ card='<pre style="white-space:pre-wrap;font-size:12px">'+escapeHtml(row.raw)+'</pre>'; }
    return '<div class="synop-day-item" style="margin-bottom:12px"><div style="font-family:var(--mono);font-size:12px;color:var(--accent);margin:0 0 4px">'+row.time+' · 78988</div>'+card+'<pre style="margin:6px 0 0;font-size:11px;color:var(--muted);white-space:pre-wrap">'+escapeHtml(row.raw)+'</pre></div>';
  }).join('');
  host.innerHTML='<div style="margin-bottom:8px;font-size:13px">'+rows.length+' report(s) · '+Y+'-'+Mo+'-'+Da+' UTC</div>'+cards;
  host.dataset.loaded='1';
}
window.loadDaySummary78988=loadDaySummary78988;
'''

if 'function loadDaySummary78988' not in h:
    h = h.replace('function synopSub(which){', fn + 'function synopSub(which){', 1)
    print('inserted loader')
else:
    print('loader already in file')

p.write_text(h, encoding='utf-8')
print('day body', 'id="synop-day-body"' in h)
print('loader', 'function loadDaySummary78988' in h)
print('overzicht iframe left', 'iframe src="overzicht.html" title="Day summary"' in h)
