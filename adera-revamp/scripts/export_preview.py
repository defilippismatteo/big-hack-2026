"""Package the production build and its versioned snapshots as one offline preview."""
import base64
import json
import re
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
def data_uri(path):
    mime = 'font/woff2' if path.suffix == '.woff2' else 'image/svg+xml'
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()
css = next((dist / 'assets').glob('index-*.css')).read_text()
css = re.sub(r'url\(([^)]+)\)', lambda m: 'url(' + data_uri(dist / m[1].strip('\"\'').lstrip('/')) + ')', css)
# Embedded frames must size to content; the app's production CSS is preserved.
css = re.sub(r'\d+(?:\.\d+)?(?:d|s|l)?vh', '800px', css)
js = next((dist / 'assets').glob('index-*.js')).read_text()
js = js.replace('"/adera.svg"', json.dumps(data_uri(dist / 'adera.svg')))
snapshots = {p.name:json.loads(p.read_text()) for p in (dist / 'data').glob('*.json')}
bootstrap = 'const snapshots=' + json.dumps(snapshots,ensure_ascii=False).replace('<','\\u003c') + ';window.fetch=async(url)=>new Response(JSON.stringify(snapshots[String(url).split("/").pop()]),{status:200,headers:{"Content-Type":"application/json"}});'
route = sys.argv[2] if len(sys.argv)>2 else '#/overview'
bootstrap += 'window.location.hash=' + json.dumps(route) + ';'
html = '<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ADERA · Anteprima offline</title><style>'+css+'</style><div id="root"></div><script>'+bootstrap+'</script><script type="module">'+js.replace('</script','<\\/script')+'</script></html>'
out = Path(sys.argv[1]) if len(sys.argv)>1 else root/'preview.html'
out.write_text(html)
print(out)
