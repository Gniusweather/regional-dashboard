from pathlib import Path
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

old = '''    if(isNew&&WX_NOTIFY_ICAOS.includes(icao)&&!isSpecialAlarmCondition&&!isWindAlarmCondition&&!window.__suppressAlarms){
      const sigReasons=significantConditionReasons(parsed,windSpeed,gustValue);
      if(sigReasons.length)sendWxNotification(icao,parsed,sigReasons);
    }
'''

new = '''    if(isNew&&WX_NOTIFY_ICAOS.includes(icao)&&!isSpecialAlarmCondition&&!isWindAlarmCondition&&!window.__suppressAlarms){
      const sigReasons=significantConditionReasons(parsed,windSpeed,gustValue);
      if(sigReasons.length)sendWxNotification(icao,parsed,sigReasons);
    }
    // ── SPECI issued (TNCA / TNCB / TNCC) — minute ≠ routine METAR minute
    if(isNew&&typeof SPECI_ICAOS!=='undefined'&&SPECI_ICAOS.includes(icao)&&!window.__suppressAlarms){
      const sm=(metarLine||parsed.raw||'').match(/\\b(\\d{2})(\\d{2})(\\d{2})Z\\b/);
      if(sm){
        const minute=parseInt(sm[3],10);
        const routine=(typeof SPECI_ROUTINE_MIN!=='undefined'&&SPECI_ROUTINE_MIN[icao]!=null)?SPECI_ROUTINE_MIN[icao]:0;
        if(minute!==routine){
          const tStr=sm[2]+':'+sm[3]+'Z';
          ntfyPublish('SPECI — '+icao, tStr+' — special report issued.\n'+(metarLine||parsed.raw||''), ['zap'], 4);
          if(notificationsEnabled&&'Notification' in window&&Notification.permission==='granted'){
            showAppNotification('⚡ SPECI — '+icao, {
              body: tStr+'\n'+(metarLine||parsed.raw||''),
              tag: 'speci-'+icao,
              requireInteraction: true,
              silent: false,
              icon: 'icon-192.png',
              badge: 'icon-192.png'
            });
          }
        }
      }
    }
'''

if old in h:
    h = h.replace(old, new, 1)
    print('SPECI notify inserted')
else:
    print('WARN exact miss')
    # looser: after sig reasons block
    needle = 'if(sigReasons.length)sendWxNotification(icao,parsed,sigReasons);\n    }'
    if needle in h and 'SPECI — ' not in h[h.find(needle):h.find(needle)+800]:
        h = h.replace(needle, needle + '''
    // ── SPECI issued (TNCA / TNCB / TNCC)
    if(isNew&&typeof SPECI_ICAOS!=='undefined'&&SPECI_ICAOS.includes(icao)&&!window.__suppressAlarms){
      const sm=(metarLine||parsed.raw||'').match(/\\b(\\d{2})(\\d{2})(\\d{2})Z\\b/);
      if(sm){
        const minute=parseInt(sm[3],10);
        const routine=(typeof SPECI_ROUTINE_MIN!=='undefined'&&SPECI_ROUTINE_MIN[icao]!=null)?SPECI_ROUTINE_MIN[icao]:0;
        if(minute!==routine){
          const tStr=sm[2]+':'+sm[3]+'Z';
          ntfyPublish('SPECI — '+icao, tStr+' — special report issued.\n'+(metarLine||parsed.raw||''), ['zap'], 4);
          if(notificationsEnabled&&'Notification' in window&&Notification.permission==='granted'){
            showAppNotification('⚡ SPECI — '+icao, {body:tStr+'\n'+(metarLine||parsed.raw||''),tag:'speci-'+icao,requireInteraction:true,silent:false,icon:'icon-192.png',badge:'icon-192.png'});
          }
        }
      }
    }''', 1)
        print('SPECI notify loose insert')
    else:
        print('FAIL')

hp.write_text(h, encoding='utf-8')
print('has SPECI —', 'SPECI — ' in h)
