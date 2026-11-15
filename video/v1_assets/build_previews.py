import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'adera-revamp/public/data/overview.json').read_text())
values = [(row[0], row[3]) for row in data['forecast'] if row[1] == 'FGR-AD03']
if not values:
    raise ValueError('Serie FGR-AD03 assente')
low = min(value for date, value in values)
high = max(value for date, value in values)
padding = max((high - low) * .2, .01)
low -= padding
high += padding
points = [(150 + index * 1120 / (len(values) - 1), 700 - (value - low) / (high - low) * 350) for index, (date, value) in enumerate(values)]
curve = ' '.join(f'{horizontal:.2f},{vertical:.2f}' for horizontal, vertical in points)
base = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"><style>text{font-family:Inter,Arial,sans-serif;letter-spacing:-1px}.big{font-weight:750}</style>'
opening = base + '<rect width="1600" height="900" fill="#F6F5F9"/><text x="100" y="120" fill="#7046CE" font-size="30">ADERA</text><g class="big" fill="#292339" font-size="98"><text x="100" y="300">E se potessi</text><text x="100" y="415">testare una campagna</text><text x="100" y="530">prima di</text></g><rect x="92" y="565" width="665" height="130" rx="12" fill="#8861E8"/><text x="115" y="660" class="big" fill="white" font-size="100">investirci?</text><g transform="translate(1090 530) rotate(-8)"><rect width="350" height="220" rx="20" fill="white" stroke="#E7E3EE"/><text x="30" y="60" font-size="25" fill="#706A7D">La prossima campagna</text><text x="30" y="125" font-size="42" fill="#7046CE">Prima, capiscila.</text><path d="M30 175h235m-25-16 25 16-25 16" fill="none" stroke="#7046CE" stroke-width="5"/></g></svg>'
(OUT / '01-opening.svg').write_text(opening)
graph = base + '<rect width="1600" height="900" fill="#35214F"/><text x="90" y="100" fill="#C2A5FF" font-size="28">ADERA / ANALISI QUANTITATIVA</text><text x="90" y="195" class="big" fill="white" font-size="65">Il periodo vuoto prende forma.</text><text x="90" y="255" fill="#D1C2E1" font-size="27">CPM previsto · FGR-AD03 · Timestral 28M</text>'
for index in range(4):
    vertical = 350 + index * 350 / 3
    label = high - index * (high - low) / 3
    graph += f'<path d="M150 {vertical}H1270" stroke="#ffffff20"/><text x="75" y="{vertical + 8}" fill="#D1C2E1" font-size="23">{label:.2f}</text>'
graph += f'<polyline points="{curve}" fill="none" stroke="#C2A5FF" stroke-width="7" stroke-linejoin="round"/>'
for target, label, top in [('2026-11-27', 'Black Friday', 300), ('2026-11-30', 'Cyber Monday', 780)]:
    index = next(index for index, (date, value) in enumerate(values) if date == target)
    horizontal, vertical = points[index]
    graph += f'<path d="M{horizontal} 335V735" stroke="#ffffff50" stroke-dasharray="5 8"/><circle cx="{horizontal}" cy="{vertical}" r="11" fill="white"/><rect x="{horizontal-100}" y="{top-34}" width="230" height="52" rx="13" fill="#F6F5F9"/><text x="{horizontal-85}" y="{top}" fill="#35214F" font-size="27">{label}</text>'
graph += '<text x="150" y="747" fill="#D1C2E1" font-size="23">16 novembre</text><text x="90" y="850" fill="white" font-size="27">La curva usa i forecast salvati. I checkpoint non aggiungono picchi.</text></svg>'
(OUT / '02-forecast.svg').write_text(graph)
html = '<!doctype html><meta charset="utf-8"><style>body{font-family:var(--font-sans);color:var(--foreground)}section{margin-bottom:24px}img{display:block;width:100%;border-radius:16px}p{color:var(--muted-foreground);font-size:14px}</style>'
for filename, title in [('01-opening.svg', '01 · Apertura — proposta compositiva'), ('02-forecast.svg', '02 · Forecast — curva dai dati salvati')]:
    html += f'<section><h3>{title}</h3><img src="{OUT / filename}"></section>'
html += '<p>Bozze SVG, non immagini AI. Timing del riferimento e font Inter incorporato ancora da rifinire. Grafico: asse Y locale, sola previsione CPM; storico e confronto modelli non ancora inclusi. La frase sotto il grafico è esplicativa della bozza, non prevista nel video.</p>'
(OUT / 'previews.html').write_text(html)
print('Due anteprime SVG e galleria HTML prodotte.')
