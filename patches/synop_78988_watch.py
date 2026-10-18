from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

BLOCK = r'''
/* ── 78988 SYNOP watch (NOAA SI/SM) ──
   Client-only: runs while app is open or backgrounded (not fully killed).
   Synoptic hours 00/03/06/09/12/15/18/21 UTC, window T-5 .. T+15.
   ntfy only during 08:00-21:59 AST. */
const SYNOP_78988_SI='https://tgftp.nws.noaa.gov/data/raw/si/sica20.tncc..txt';
const SYNOP_78988_SM='https://tgftp.nws.noaa.gov/data/raw/sm/smca01.tncc..txt';
const SYNOP_78988_WATCH_KEY='rwc-synop-78988-watch-v1';
const SYNOP_UTC_HOURS=[0,3,6,9,12,15,18,21];

function ntfyActiveHoursAST(){
  // Curaçao AST = UTC-4 year-round
  const now=new Date();
  const astH=(now.getUTCHours()-4+24)%24;
  return astH>=8 && astH<=21; // 08:00-21:59 AST
}
function ntfyPublishActive(title,message,tags,priority){
  if(!ntfyActiveHoursAST()) return;
  ntfyPublish(title,message,tags,priority);
}
function synopWatchTarget(now){
  now=now||new Date();
  const mins=now.getUTCHours()*60+now.getUTCMinutes();
  for(let i=0;i<SYNOP_UTC_HOURS.length;i++){
    const H=SYNOP_UTC_HOURS[i];
    const t=H*60;
    if(H===0){
      // 23:55-24:00 previous day OR 00:00-00:15
      if(mins>=(24*60-5) || mins<=15) return {hour:0,inWindow:true,pastDue:mins>15&&mins<(24*60-5)?false:(mins>15)};
      continue;
    }
    const delta=mins-t;
    if(delta>=-5 && delta<=15) return {hour:H,inWindow:true,pastDue:delta>15};
  }
  return {hour:null,inWindow:false,pastDue:false};
}
function synop78988LoadState(){
  try{ return JSON.parse(localStorage.getItem(SYNOP_78988_WATCH_KEY))||{}; }catch(e){ return {}; }
}
function synop78988SaveState(st){
  try{ localStorage.setItem(SYNOP_78988_WATCH_KEY, JSON.stringify(st)); }catch(e){}
}
function synopFingerprint(text){
  const t=String(text||'').replace(/\s+/g,' ').trim();
  if(!t) return '';
  // bulletin id + first 78988 chunk
  const hdr=t.match(/\b(S[IM][A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6})\b/);
  const st=t.match(/\b78988\b[\s\S]{0,120}/);
  return ((hdr&&hdr[1])||'')+'|'+(st?st[0].slice(0,80):t.slice(0,80));
}
function assessSynop78988(text, kind){
  const raw=String(text||'').trim();
  if(!raw || raw.length<30){
    return {ok:false, issue:'no_data', detail:kind+' empty or too short', fp:''};
  }
  if(/valid API key|AuthenticationRequired|AccessDenied|<!DOCTYPE|<html/i.test(raw)){
    return {ok:false, issue:'no_data', detail:kind+' fetch returned non-SYNOP content', fp:''};
  }
  const flat=raw.replace(/\r/g,'').replace(/\n/g,' ').replace(/\s{2,}/g,' ');
  const fp=synopFingerprint(flat);
  // NIL bulletin without a station report
  if(/\bNIL\b/.test(flat) && !/\b78988\b/.test(flat)){
    return {ok:false, issue:'nil', detail:kind+' NIL (no 78988)', fp:fp||('NIL|'+kind)};
  }
  if(!/\b78988\b/.test(flat)){
    return {ok:false, issue:'missing_station', detail:kind+' has no 78988 group', fp:fp};
  }
  if(!/\bAAXX\b/.test(flat)){
    return {ok:false, issue:'incomplete', detail:kind+' missing AAXX', fp:fp};
  }
  // Extract roughly the 78988 report groups until next IIiii or end
  const m=flat.match(/\b78988\b(?:\s+\d{5}){0,2}([\s\S]{0,200})/);
  const chunk=(m?m[0]:flat);
  // Core: station + wind group (nddff) expected in almost all non-NIL land reports
  if(!/\b78988\s+\d{5}\b/.test(chunk) && !/\b78988\s+\/\/\/\/\/\b/.test(chunk)){
    // some formats use 78988 then groups without strict wind — soft check
    if(chunk.replace(/\s+/g,'').length<20){
      return {ok:false, issue:'incomplete', detail:kind+' 78988 report truncated', fp:fp};
    }
  }
  // Missing pressure group 4PPPP or 4xxxx often present at TNCC — warn if neither temp 1sTTT nor pressure 4
  const hasTemp=/\b1[01]\d{3}\b/.test(chunk) || /\b1\/\/\/\/\/\b/.test(chunk);
  const hasSlp=/\b4\d{4}\b/.test(chunk) || /\b4\/\/\/\/\/\b/.test(chunk);
  if(!hasTemp && !hasSlp){
    return {ok:false, issue:'incomplete', detail:kind+' 78988 missing temp/SLP groups', fp:fp};
  }
  return {ok:true, issue:null, detail:null, fp:fp};
}
let __synop78988Busy=false;
async function checkSynop78988Watch(force){
  if(__synop78988Busy) return;
  const tgt=synopWatchTarget(new Date());
  if(!force && !tgt.inWindow) return;
  if(!ntfyActiveHoursAST() && !force) return;
  __synop78988Busy=true;
  try{
    const st=synop78988LoadState();
    const cycleKey=(tgt.hour!=null?String(tgt.hour).padStart(2,'0'):'xx')+'Z';
    const results={};
    for(const [kind,url] of [['SI',SYNOP_78988_SI],['SM',SYNOP_78988_SM]]){
      let text='';
      try{
        const out=await fetchWithRetries(url, 2);
        if(out&&out.ok&&out.text) text=out.text;
      }catch(e){}
      results[kind]=assessSynop78988(text, kind);
      results[kind].textLen=(text||'').length;
    }
    const si=results.SI, sm=results.SM;
    const bothMissing=(!si.ok && si.issue==='no_data') && (!sm.ok && sm.issue==='no_data');
    const alerted=st.alerted&&typeof st.alerted==='object'?st.alerted:{};

    function once(key, title, msg, tags, pri){
      if(alerted[key]) return;
      ntfyPublishActive(title, msg, tags||['warning'], pri||4);
      alerted[key]=Date.now();
    }

    if(bothMissing){
      once('nodata-'+cycleKey, '78988 SYNOP missing',
        'No NOAA SI/SM data for TNCC (78988) around '+cycleKey+' UTC.',
        ['x'], 4);
    } else {
      for(const kind of ['SI','SM']){
        const r=results[kind];
        if(r.ok){
          const prev=st['fp'+kind];
          if(r.fp && r.fp!==prev){
            once('new-'+kind+'-'+r.fp.slice(0,40), 'New SYNOP 78988 — '+kind,
              (r.fp.split('|')[0]||kind)+' updated for station 78988.\nSource: NOAA raw '+kind+'.',
              ['clipboard'], 3);
            st['fp'+kind]=r.fp;
          }
        } else if(r.issue==='nil'){
          once('nil-'+kind+'-'+cycleKey, '78988 SYNOP NIL — '+kind,
            r.detail|| (kind+' NIL'), ['grey_exclamation'], 3);
        } else if(r.issue==='missing_station' || r.issue==='incomplete'){
          once('bad-'+kind+'-'+cycleKey, '78988 SYNOP data problem — '+kind,
            r.detail||'Incomplete or wrong groups', ['warning'], 4);
        } else if(r.issue==='no_data'){
          // only if the other side is ok — else bothMissing already fired
          if(results[kind==='SI'?'SM':'SI'].ok){
            once('nodata-one-'+kind+'-'+cycleKey, '78988 '+kind+' missing',
              r.detail|| (kind+' not available'), ['x'], 3);
          }
        }
      }
    }
    st.alerted=alerted;
    st.lastCheck=Date.now();
    st.lastCycle=cycleKey;
    // prune alerted keys older than 2 days
    const cut=Date.now()-2*24*3600*1000;
    Object.keys(st.alerted).forEach(function(k){ if(st.alerted[k]<cut) delete st.alerted[k]; });
    synop78988SaveState(st);
  }finally{
    __synop78988Busy=false;
  }
}
// Tick every 60s; runs while backgrounded (does not require !document.hidden).
setInterval(function(){ try{ checkSynop78988Watch(false); }catch(e){} }, 60*1000);
setTimeout(function(){ try{ checkSynop78988Watch(false); }catch(e){} }, 8000);
'''

# Insert after sendWxNotification block / before BACKGROUND PUSH comment
marker = "/* ── BACKGROUND PUSH (alerts even when the app is fully closed) ──"
if 'SYNOP_78988_WATCH_KEY' in h:
    print('already present')
elif marker in h:
    h = h.replace(marker, BLOCK + '\n' + marker, 1)
    print('inserted before BACKGROUND PUSH')
else:
    # fallback after function ntfyPublish section
    m2 = 'function sendWxNotification'
    if m2 in h:
        # find closing of sendWxNotification - after the try notificationsEnabled block
        idx = h.find("localStorage.getItem('rwc-notify-enabled')")
        if idx > 0:
            end = h.find('}catch(e){}', idx)
            if end > 0:
                end = end + len('}catch(e){}')
                h = h[:end] + '\n' + BLOCK + h[end:]
                print('inserted after notify-enabled try')
            else:
                print('FAIL end')
        else:
            print('FAIL notify-enabled')
    else:
        print('FAIL markers')

hp.write_text(h, encoding='utf-8')
print('watch key', 'SYNOP_78988_WATCH_KEY' in h)
print('checkSynop', 'function checkSynop78988Watch' in h)
print('active hours', 'ntfyActiveHoursAST' in h)
