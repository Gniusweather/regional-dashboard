from pathlib import Path
import re
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

old = '''async function fetchMetarHistoryNOAA(icao){
  try{
    const url=`https://aviationweather.gov/api/data/metar?ids=${icao}&format=json&hours=6`;
    let data=null;
    for(let attempt=0;attempt<2&&!data;attempt++){
      try{ data=await fetchMetarHistoryJSON(url,8000); }
      catch(e){ if(attempt===0)await new Promise(r=>setTimeout(r,400)); }
    }
    if(!data)return null;
    const records=data.map(r=>{
      const rawOb=r.rawOb||r.raw_text||r.metar||'';
      let t=null;
      if(r.obsTime)t=new Date(r.obsTime*1000);
      else if(r.reportTime)t=new Date(r.reportTime);
      return rawOb?{time:t||new Date(),raw:rawOb}:null;
    }).filter(Boolean);
    if(!records.length)return null;
    records.sort((a,b)=>b.time.getTime()-a.time.getTime());
    return records;
  }catch(e){console.warn('NOAA history fetch failed',icao,e);return null;}
}'''

new = '''function parseMetarHistTime(raw){
  const m=String(raw||'').match(/\\b(\\d{2})(\\d{2})(\\d{2})Z\\b/);
  if(!m) return new Date();
  const now=new Date();
  let y=now.getUTCFullYear(), mo=now.getUTCMonth();
  const day=+m[1], hh=+m[2], mm=+m[3];
  let t=new Date(Date.UTC(y, mo, day, hh, mm, 0));
  // Month wrap: report day ahead of UTC day means previous month
  if(t.getTime()-now.getTime() > 36*3600*1000){
    mo-=1; if(mo<0){ mo=11; y-=1; }
    t=new Date(Date.UTC(y, mo, day, hh, mm, 0));
  } else if(now.getTime()-t.getTime() > 40*24*3600*1000){
    mo+=1; if(mo>11){ mo=0; y+=1; }
    t=new Date(Date.UTC(y, mo, day, hh, mm, 0));
  }
  return t;
}
function parseMetarHistRawText(icao, text){
  if(!text) return [];
  const records=[];
  const seen=new Set();
  String(text).split(/\\r?\\n/).forEach(function(line){
    let ln=line.trim();
    if(!ln) return;
    // strip jina / markdown wrappers when present
    ln=ln.replace(/^\\s*[-*`]\\s*/, '').replace(/`+$/,'');
    if(!ln.includes(icao) && !/^(METAR|SPECI)\\s+/.test(ln)) return;
    if(!/\\b\\d{6}Z\\b/.test(ln)) return;
    ln=ln.replace(/^(METAR|SPECI)\\s+/,'');
    // keep first occurrence of ICAO onward if prefixed junk
    const ix=ln.indexOf(icao);
    if(ix>0) ln=ln.slice(ix);
    if(seen.has(ln)) return;
    seen.add(ln);
    records.push({ time: parseMetarHistTime(ln), raw: ln });
  });
  records.sort(function(a,b){ return b.time.getTime()-a.time.getTime(); });
  return records;
}
async function fetchMetarHistoryNOAA(icao){
  try{
    // Prefer raw text via the same proxy race as live METARs (JSON path is
    // blocked by CORS and most public proxies return non-JSON / 401).
    const rawUrl='https://aviationweather.gov/api/data/metar?ids='+icao+'&format=raw&hours=6';
    let records=[];
    try{
      const out=await fetchWithRetries(rawUrl, 2);
      if(out&&out.ok&&out.text){
        records=parseMetarHistRawText(icao, out.text);
      }
    }catch(e){}
    if(!records.length){
      // JSON fallback — accept pure JSON or JSON embedded in a proxy wrapper
      const jsonUrl='https://aviationweather.gov/api/data/metar?ids='+icao+'&format=json&hours=6';
      try{
        const data=await fetchMetarHistoryJSON(jsonUrl, 10000);
        if(data&&data.length){
          records=data.map(function(r){
            const rawOb=r.rawOb||r.raw_text||r.metar||'';
            let t=null;
            if(r.obsTime) t=new Date(r.obsTime*1000);
            else if(r.reportTime) t=new Date(r.reportTime);
            else t=parseMetarHistTime(rawOb);
            return rawOb?{time:t||new Date(),raw:rawOb}:null;
          }).filter(Boolean);
        }
      }catch(e){}
    }
    if(!records.length){
      // Last resort: jina reader on raw endpoint
      try{
        const jurl='https://r.jina.ai/'+rawUrl;
        const r=await fetchWithTimeout(jurl, 12000);
        if(r&&r.ok){
          const t=await r.text();
          records=parseMetarHistRawText(icao, t);
        }
      }catch(e){}
    }
    if(!records.length) return null;
    records.sort(function(a,b){ return b.time.getTime()-a.time.getTime(); });
    return records;
  }catch(e){ console.warn('NOAA history fetch failed', icao, e); return null; }
}'''

if old in h:
    h = h.replace(old, new, 1)
    print('replaced fetchMetarHistoryNOAA')
else:
    print('WARN exact miss')
    start = h.find('async function fetchMetarHistoryNOAA')
    if start < 0:
        start = h.find('function fetchMetarHistoryNOAA')
    end = h.find('/* Resolve the best available history list', start)
    if start >= 0 and end > start:
        h = h[:start] + new + '\n\n' + h[end:]
        print('replaced by markers')
    else:
        print('FAIL locate', start, end)

# Also harden fetchMetarHistoryJSON to extract JSON array from proxy wrappers (jina etc.)
oldj = '''  const validated=candidates.map(fn=>fn().then(text=>{
    if(!text)throw 0;
    const data=JSON.parse(text); // throws (and thus loses the race) on non-JSON, e.g. a mangled Jina response
    if(!Array.isArray(data)||!data.length)throw 0;
    return data;
  }));'''
newj = '''  const validated=candidates.map(fn=>fn().then(text=>{
    if(!text)throw 0;
    let data=null;
    try{ data=JSON.parse(text); }
    catch(e){
      // Proxy wrappers (e.g. jina markdown) often embed the JSON array
      const a=text.indexOf('['), b=text.lastIndexOf(']');
      if(a>=0&&b>a){ try{ data=JSON.parse(text.slice(a,b+1)); }catch(e2){ throw 0; } }
      else throw 0;
    }
    if(!Array.isArray(data)||!data.length)throw 0;
    return data;
  }));'''
if oldj in h:
    h = h.replace(oldj, newj, 1)
    print('hardened JSON parse')
else:
    print('WARN json harden')

hp.write_text(h, encoding='utf-8')
print('parseMetarHistRawText', 'function parseMetarHistRawText' in h)
print('raw hours=6', "format=raw&hours=6" in h)
