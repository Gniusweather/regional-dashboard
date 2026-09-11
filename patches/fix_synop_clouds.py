#!/usr/bin/env python3
from pathlib import Path
p = Path('index.html')
t = p.read_text()
idx = t.find('r.P.CL=CL[parseInt(g[3],10)]')
print('sec1 idx', idx)
if idx > 0:
    start = t.rfind("} else if(id==='8'", 0, idx+1)
    end = t.find('\n      }', idx)
    print('sec1 start/end', start, end)
    if start > 0 and end > start:
        repl = "} else if(id==='8'&&!slash){\n        const Nh=parseInt(g[1],10), cl=parseInt(g[2],10), cm=parseInt(g[3],10), ch=parseInt(g[4],10);\n        r.P.cloud_group8=g;\n        if(!isNaN(Nh)){ r.P.low_cloud_cover=['SKC','FEW','FEW','SCT','SCT','BKN','BKN','OVC','OVC','-'][Nh]||'-'; r.P.Nh=Nh; }\n        if(!isNaN(cl)) r.P.CL=CL[cl]||'-';\n        if(!isNaN(cm)) r.P.CM=CM[cm]||'-';\n        if(!isNaN(ch)) r.P.CH=CH[ch]||'-';\n      }"
        t = t[:start] + repl + t[end+8:]
idx2 = t.find('r.P.CL=CL[parseInt(g[3],10)]')
print('sec3 leftover idx', idx2)
if idx2 > 0:
    start = t.rfind("else if(id==='8'", 0, idx2+1)
    end = t.find('\n        }', idx2)
    print('sec3 start/end', start, end)
    if start > 0 and end > start:
        repl = "else if(id==='8'&&!slash){\n          const Ns=parseInt(g[1],10), Cg=parseInt(g[2],10), hs=parseInt(g.slice(3,5),10);\n          const CGEN=['Ci','Cc','Cs','Ac','As','Ns','Sc','St','Cu','Cb'];\n          let ft=null;\n          if(!isNaN(hs)&&hs<=50) ft=Math.round(hs*30*3.28084);\n          else if(!isNaN(hs)&&hs>=56&&hs<=80) ft=Math.round((1800+(hs-56)*300)*3.28084);\n          else if(hs===81) ft=34450; else if(hs===82) ft=39370; else if(hs===83) ft=44300;\n          const amt=['SKC','FEW','FEW','SCT','SCT','BKN','BKN','OVC','OVC',''][Ns]||'';\n          const typ=CGEN[Cg]||'';\n          const hstr=ft==null?'':(ft>=1000?(ft/1000).toFixed(1)+'kft':Math.round(ft)+'ft');\n          const line=[amt,typ,hstr].filter(Boolean).join(' ');\n          if(line){ r.P.cloud_layers=r.P.cloud_layers||[]; r.P.cloud_layers.push(line); }\n        }"
        t = t[:start] + repl + t[end+10:]
i = t.find('cloudBits.push(`Mid:')
print('mid bit', i)
if i>0 and 'High: ${P.CH}' not in t:
    nl = t.find('\n', i)
    extra = "\n  if(P.CH&&P.CH!=='-') cloudBits.push(`High: ${P.CH}`);\n  if(P.cloud_layers&&P.cloud_layers.length) cloudBits.push(P.cloud_layers.join(' | '));"
    t = t[:nl] + extra + t[nl:]
j = t.find("srows.push(['CLOUD',P.cloud_cover")
print('srows', j)
if j>0 and "srows.push(['CL'" not in t:
    semi = t.find(';', j)
    extra = "\n      if(P.CL&&P.CL!=='-') srows.push(['CL',P.CL]);\n      if(P.CM&&P.CM!=='-') srows.push(['CM',P.CM]);\n      if(P.CH&&P.CH!=='-') srows.push(['CH',P.CH]);\n      if(P.cloud_layers&&P.cloud_layers.length) srows.push(['LAYERS',P.cloud_layers.join(' | ')]);"
    t = t[:semi+1] + extra + t[semi+1:]
p.write_text(t)
print('leftover g[3] CL', t.count('CL[parseInt(g[3]'))
print('cloud_group8', t.count('cloud_group8'))
print('LAYERS', t.count("['LAYERS'"))
