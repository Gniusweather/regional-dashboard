from pathlib import Path
import re, subprocess, sys

hp = Path("index.html")
h = hp.read_text(encoding="utf-8")

old1 = "tStr+' — special report issued." + "\n" + "'+(metarLine"
new1 = "tStr+' — special report issued.\\n'+(metarLine"
old2 = "body: tStr+'" + "\n" + "'+(metarLine"
new2 = "body: tStr+'\\n'+(metarLine"

n1 = h.count(old1)
n2 = h.count(old2)
if n1:
    h = h.replace(old1, new1)
    print("fixed ntfy string", n1)
if n2:
    h = h.replace(old2, new2)
    print("fixed body string", n2)
if not n1 and not n2:
    i = h.find("special report issued")
    print("pattern miss", repr(h[i:i+50]) if i >= 0 else "not found")

hp.write_text(h, encoding="utf-8")

scripts = re.findall(r"<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>", h)
big = max(scripts, key=len)
Path("/tmp/check_app.js").write_text(big)
r = subprocess.run(["node", "--check", "/tmp/check_app.js"], capture_output=True, text=True)
print("node", r.returncode)
if r.returncode != 0:
    print(r.stderr[:500])
    sys.exit(1)
print("OK")
