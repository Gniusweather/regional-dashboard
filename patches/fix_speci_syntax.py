from pathlib import Path
import re
hp = Path('index.html')
h = hp.read_text(encoding='utf-8')

# Broken SPECI ntfyPublish / showAppNotification string literals (real newlines inside quotes)
broken = '''          ntfyPublish('SPECI — '+icao, tStr+' — special report issued.
'+(metarLine||parsed.raw||''), ['zap'], 4);
          if(notificationsEnabled&&'Notification' in window&&Notification.permission==='granted'){
            showAppNotification('⚡ SPECI — '+icao, {
              body: tStr+'
'+(metarLine||parsed.raw||''),
              tag: 'speci-'+icao,
              requireInteraction: true,
              silent: false,
              icon: 'icon-192.png',
              badge: 'icon-192.png'
            });
          }'''

fixed = '''          ntfyPublish('SPECI — '+icao, tStr+' — special report issued.\n'+(metarLine||parsed.raw||''), ['zap'], 4);
          if(notificationsEnabled&&'Notification' in window&&Notification.permission==='granted'){
            showAppNotification('⚡ SPECI — '+icao, {
              body: tStr+'\n'+(metarLine||parsed.raw||''),
              tag: 'speci-'+icao,
              requireInteraction: true,
              silent: false,
              icon: 'icon-192.png',
              badge: 'icon-192.png'
            });
          }'''

if broken in h:
    h = h.replace(broken, fixed, 1)
    print('fixed SPECI block')
else:
    # regex fallback: fix tStr+' ... newline ... '+(metarLine
    h2, n = re.subn(
        r"tStr\+' — special report issued\.\n'\+\(metarLine",
        "tStr+' — special report issued.\\n'+(metarLine",
        h,
        count=1,
    )
    # The file has REAL newline not backslash-n
    h2, n = re.subn(
        r"tStr\+' — special report issued\.\s*\n'\+\(metarLine",
        "tStr+' — special report issued.\\n'+(metarLine",
        h,
        count=1,
    )
    h2, n2 = re.subn(
        r"body: tStr\+'\s*\n'\+\(metarLine",
        "body: tStr+'\\n'+(metarLine",
        h2,
        count=1,
    )
    print('regex fixes', n, n2)
    h = h2

hp.write_text(h, encoding='utf-8')

# syntax check largest inline script
import re as _re, subprocess, sys
scripts=_re.findall(r'<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>', h)
big=max(scripts, key=len)
Path('/tmp/app_check2.js').write_text(big)
r=subprocess.run(['node','--check','/tmp/app_check2.js'], capture_output=True, text=True)
print('node check', r.returncode)
print(r.stderr[:500] if r.stderr else 'OK')
if r.returncode!=0:
    sys.exit(1)
