from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

old = '''/* Default "significant conditions" notification — always active for these
   stations whenever notifications are enabled, independent of the
   per-station gust/wind alarm config. Fires on any ONE of:
     - sustained wind ≥ WX_NOTIFY_WIND_KT
     - any weather phenomenon reported at all (not just RA/SHRA/TS/TSRA)
     - gust ≥ WX_NOTIFY_GUST_KT (no thunderstorm required)
     - visibility ≤ WX_NOTIFY_VIS_M */
const WX_NOTIFY_ICAOS=['TNCA','TNCB','TNCC'];
const WX_NOTIFY_WIND_KT=15;
const WX_NOTIFY_GUST_KT=35;
const WX_NOTIFY_VIS_M=9000;
function hasAnyWx(wxText){
  const txt=String(wxText||'').trim();
  return !!txt&&txt!=='--';
}
function significantConditionReasons(parsed,windSpeed,gustValue){
  const reasons=[];
  if(typeof windSpeed==='number'&&windSpeed>=WX_NOTIFY_WIND_KT)reasons.push(`sustained wind ${windSpeed}kt`);
  if(hasAnyWx(parsed.wx))reasons.push(`weather ${parsed.wx}`);
  if(typeof gustValue==='number'&&gustValue>=WX_NOTIFY_GUST_KT)reasons.push(`gust ${gustValue}kt`);
  if(!isNaN(parsed.visMin)&&parsed.visMin<=WX_NOTIFY_VIS_M)reasons.push(`visibility ${parsed.visMin}m`);
  return reasons;
}'''

new = '''/* Hard-coded significant conditions — TNCC only.
   Fires on any ONE of:
     - sustained wind ≥ 15 kt
     - any weather group
     - visibility ≤ 9000 m
     - overcast (OVC) cloud group
   TNCA uses a separate hard-coded path: gust > 35 kt OR thunderstorm. */
const WX_NOTIFY_ICAOS=['TNCC'];
const WX_NOTIFY_WIND_KT=15;
const WX_NOTIFY_GUST_KT=35;
const WX_NOTIFY_VIS_M=9000;
function hasAnyWx(wxText){
  const txt=String(wxText||'').trim();
  return !!txt&&txt!=='--';
}
function hasOvercastClouds(cldText){
  return /\\bOVC\\d{3}\\b/i.test(String(cldText||''));
}
function significantConditionReasons(parsed,windSpeed,gustValue){
  const reasons=[];
  if(typeof windSpeed==='number'&&windSpeed>=WX_NOTIFY_WIND_KT)reasons.push(`sustained wind ${windSpeed}kt`);
  if(hasAnyWx(parsed.wx))reasons.push(`weather ${parsed.wx}`);
  if(!isNaN(parsed.visMin)&&parsed.visMin<=WX_NOTIFY_VIS_M)reasons.push(`visibility ${parsed.visMin}m`);
  if(hasOvercastClouds(parsed.cld))reasons.push(`overcast ${String(parsed.cld||'').trim()}`);
  return reasons;
}'''

if old in h:
    h = h.replace(old, new, 1)
    print('significant conditions updated')
else:
    print('WARN block exact')
    # try smaller replacements
    if "const WX_NOTIFY_ICAOS=['TNCA','TNCB','TNCC'];" in h:
        h = h.replace("const WX_NOTIFY_ICAOS=['TNCA','TNCB','TNCC'];", "const WX_NOTIFY_ICAOS=['TNCC'];", 1)
        print('ICAOS TNCC only')
    if 'function significantConditionReasons' in h and 'hasOvercastClouds' not in h:
        h = h.replace(
            'function hasAnyWx(wxText){\n  const txt=String(wxText||\'\').trim();\n  return !!txt&&txt!==\'--\';\n}',
            'function hasAnyWx(wxText){\n  const txt=String(wxText||\'\').trim();\n  return !!txt&&txt!==\'--\';\n}\nfunction hasOvercastClouds(cldText){\n  return /\\bOVC\\d{3}\\b/i.test(String(cldText||\'\'));\n}',
            1)
        h = h.replace(
            "if(typeof gustValue==='number'&&gustValue>=WX_NOTIFY_GUST_KT)reasons.push(`gust ${gustValue}kt`);\n  if(!isNaN(parsed.visMin)&&parsed.visMin<=WX_NOTIFY_VIS_M)reasons.push(`visibility ${parsed.visMin}m`);",
            "if(!isNaN(parsed.visMin)&&parsed.visMin<=WX_NOTIFY_VIS_M)reasons.push(`visibility ${parsed.visMin}m`);\n  if(hasOvercastClouds(parsed.cld))reasons.push(`overcast ${String(parsed.cld||'').trim()}`);",
            1)
        print('reasons patched')

# TNCA hard-coded gust > 35 OR TS — after special alarm block
old_call = '''    if(isNew&&isSpecialAlarmCondition&&!window.__suppressAlarms){playSpecialAlarm();sendAlarmNotification(icao,parsed);}
    // ── SUSTAINED WIND ALARM'''

new_call = '''    if(isNew&&isSpecialAlarmCondition&&!window.__suppressAlarms){playSpecialAlarm();sendAlarmNotification(icao,parsed);}
    // ── TNCA hard-coded: gust > 35 kt OR thunderstorm (always on)
    if(icao==='TNCA'&&isNew&&!window.__suppressAlarms&&!isSpecialAlarmCondition){
      const tncaGust=(typeof gustValue==='number'&&gustValue>WX_NOTIFY_GUST_KT);
      if(tncaGust||tsPresent){
        playSpecialAlarm();
        ntfyPublish(
          'TNCA — '+(tncaGust&&tsPresent?'gust + TS':(tncaGust?'gust > 35kt':'thunderstorm')),
          ((tncaGust?('Gust '+gustValue+'kt. '):'')+(tsPresent?('TS/wx: '+(parsed.wx||'TS')+'. '):'')+(parsed.raw||'')),
          ['cloud_with_lightning'],
          5
        );
        if(notificationsEnabled&&'Notification' in window&&Notification.permission==='granted'){
          showAppNotification('⚠ TNCA — '+(tncaGust&&tsPresent?'gust + TS':(tncaGust?'gust > 35kt':'thunderstorm')),{
            body:(parsed.raw||''),
            tag:'tnca-ts-gust',
            requireInteraction:true,
            silent:false,
            icon:'icon-192.png',
            badge:'icon-192.png'
          });
        }
      }
    }
    // ── SUSTAINED WIND ALARM'''

if old_call in h:
    h = h.replace(old_call, new_call, 1)
    print('TNCA hard-coded path')
else:
    print('WARN TNCA insert')

hp.write_text(h, encoding='utf-8')
print('WX_NOTIFY_ICAOS', "WX_NOTIFY_ICAOS=['TNCC']" in h)
print('overcast', 'hasOvercastClouds' in h)
print('TNCA path', "icao==='TNCA'&&isNew" in h)
