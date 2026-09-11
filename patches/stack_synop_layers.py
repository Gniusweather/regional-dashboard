from pathlib import Path
p=Path('index.html'); t=p.read_text()
old="if(P.cloud_layers&&P.cloud_layers.length) srows.push(['LAYERS',P.cloud_layers.join(' | ')]);"
new="if(P.cloud_layers&&P.cloud_layers.length) P.cloud_layers.forEach((ln,i)=>srows.push([i===0?'LYR':'',ln]));"
print('layers line', old in t)
t=t.replace(old,new,1)
# skip emdash placeholders too
t=t.replace("P.CL!=='-'","P.CL!=='-'&&P.CL!=='\u2014'")
t=t.replace("P.CM!=='-'","P.CM!=='-'&&P.CM!=='\u2014'")
t=t.replace("P.CH!=='-'","P.CH!=='-'&&P.CH!=='\u2014'")
# clip long values to the synop box width
clip_old="ctx.fillText(r[1],px,py+10);"
clip_new="{let v=r[1]; while(ctx.measureText(v).width>pw&&v.length>4) v=v.slice(0,-2); if(v!==r[1]) v=v.replace(/[\\s\\/]+$/,'')+'\u2026'; ctx.fillText(v,px,py+10);}"
# only the SYNOP box values — first occurrence after SFC SYNOP is safest if we scope
i=t.find("'SFC SYNOP'")
print('synop header', i)
if i>0:
    k=t.find(clip_old, i)
    print('clip site', k)
    if k>0:
        t=t[:k]+clip_new+t[k+len(clip_old):]
p.write_text(t)
print('LYR forEach', 'i===0?\'LYR\'' in t or "i===0?'LYR'" in t)
