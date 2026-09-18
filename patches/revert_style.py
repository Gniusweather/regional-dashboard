from pathlib import Path
p=Path('index.html')
h=p.read_text(encoding='utf-8')
# only first two T/Td strokes after tdPts
h=h.replace("const tdPts=prof.filter(r=>r.td!=null);\n    if(tdPts.length>1){\n      ctx.strokeStyle='#111';","const tdPts=prof.filter(r=>r.td!=null);\n    if(tdPts.length>1){\n      ctx.strokeStyle='#0a7a28';",1)
# temperature stroke that follows td block
# after td stroke the next #111 is T
idx=h.find("ctx.stroke();\n    }\n    ctx.strokeStyle='#111';\n    ctx.beginPath();\n    const tPts=")
print('T stroke idx', idx)
if idx>=0:
    h=h.replace("ctx.stroke();\n    }\n    ctx.strokeStyle='#111';\n    ctx.beginPath();\n    const tPts=","ctx.stroke();\n    }\n    ctx.strokeStyle='#d21f1f';\n    ctx.beginPath();\n    const tPts=",1)
h=h.replace("const label=String(Math.round(h));",
            "const ft=h*3.28084;\n    const ftStr=ft>=1000?(ft/1000).toFixed(1)+'k':String(Math.round(ft));\n    const label=ftStr+'ft';",1)
h=h.replace("'NOAA v31 · '+prof.length+' lvls · heights m'","'NOAA v32 · '+prof.length+' lvls · heights ft'",1)
p.write_text(h,encoding='utf-8')
print('green', "strokeStyle='#0a7a28'" in h)
print('red', "strokeStyle='#d21f1f'" in h)
print('feet', "ftStr+'ft'" in h)
print('v32', 'NOAA v32' in h)
