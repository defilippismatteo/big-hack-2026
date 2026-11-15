import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BRANDS = OUT / 'brands'
BRANDS.mkdir(exist_ok=True)
SOURCES = {
    'mistral.svg': 'https://mistral.ai/images/logos/logo-mistral.svg',
    't3-code.svg': 'https://raw.githubusercontent.com/pingdotgg/t3code/main/assets/prod/logo.svg',
    'gemini.svg': 'https://www.gstatic.com/images/branding/productlogos/gemini/v1/192px.svg',
    'claude.svg': 'https://claude.com/icon.svg',
    'chatgpt.svg': 'https://chatgpt.com/cdn/assets/favicon.6a33781f61.svg',
    'catboost.svg': 'https://yastatic.net/s3/locdoc/daas-static/catboost/71b237a322eec6f2889af0dae2a9c549.svg',
}


def download(item):
    filename, url = item
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=25) as response:
            content = response.read()
        document = ET.fromstring(content)
        if not document.tag.endswith('svg'):
            raise ValueError('La risposta non è un SVG')
        (BRANDS / filename).write_bytes(content)
        return {'file': filename, 'source': url, 'sha256': hashlib.sha256(content).hexdigest(), 'status': 'downloaded', 'treatment': 'Originale non modificato; verificare linee guida marchio prima della pubblicazione.'}
    except Exception as error:
        return {'file': filename, 'source': url, 'status': 'failed', 'error': str(error)}


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    manifest = list(pool.map(download, SOURCES.items()))
(BRANDS / 'sources.json').write_text(json.dumps(manifest, indent=2))
shutil.copy2('/Users/fede/.t3/userdata/attachments/8fbeb383-0c4d-4a5b-a591-edcfe3dc03f7-4ef3e001-cdfe-4030-a8bf-e9c11955c288.png', BRANDS / 'adera-original.png')
personas = json.loads((ROOT / 'adera-revamp/public/data/persona-library.json').read_text())['personas']
selection = [0, 25, 55, 85, 115, 205, 255, 305, 405, 505]
common = 'Illustrazione editoriale 2D, forme morbide e pulite, contorno sottile color prugna, ombre minime, palette ADERA viola #8861E8, prugna #35214F e neutri caldi. Ritratto a mezzobusto, centrato, vista frontale leggermente a tre quarti, espressione naturale. Canvas quadrato 1024x1024, margine libero del 12%, sfondo realmente trasparente. Nessun testo, lettere, logo, cornice o watermark. Persona fittizia, non imitare persone reali o celebrità. Conservare lo stesso stile e scala della testa in tutta la serie. Il mestiere non richiede uniformi o oggetti stereotipati. Non dedurre l’aspetto fisico dall’identità di genere.'
lines = ['# ADERA — inventario asset e prompt v1', '', 'Nessuna immagine AI generata. Prompt pronti per esecuzione manuale o generatore successivo. Tutti gli asset bitmap richiesti sono PNG; avatar con alpha, creatività 1080×1350. Nessun logo va generato con AI.', '', '## Loghi raccolti online', '']
for entry in manifest:
    lines.append(f"- `{entry['file']}` — {entry['status']} — {entry['source']}")
lines += ['', 'ADERA: originale allegato copiato in brands/adera-original.png. T3 e Gemini: nuova verifica delle fonti già citate dal progetto. Claude e ChatGPT: icone prodotto dai rispettivi siti ufficiali, non kit stampa completi. CatBoost: SVG identificato come Logo icon dal sito ufficiale. Origine ufficiale non equivale a licenza senza vincoli.', '', 'Timestral: nessun marchio separato verificato in questa ricerca. Usare la scritta «Timestral 28M», non il logo Mistral come se fosse quello del modello. Gemini Decision: usare il logo Gemini con etichetta HTML «Gemini Decision 1»; non inventare un marchio dedicato. Nessun logo Instagram necessario: feed simulato riconoscibile per struttura, senza rivendicare una partnership.', '', '## Dieci avatar da generare', '', 'Campione narrativo scelto dalla libreria sintetica, non rappresentativo statisticamente. I dettagli di volto/vestiti sono libertà illustrative, non informazioni inferite dal profilo. Le card riporteranno solo informazioni documentate.', '', '### Prompt comune', common, '']
for number, index in enumerate(selection, 1):
    person = personas[index]
    lines += [f"### avatar-{number:02d}.png — {person['name']}", f"Fonte: persona_id `{person['persona_id']}`; età {person['age_years']}; occupazione: {person['occupation']}.", '', f"{common} Soggetto: {person['name']}, {person['age_years']} anni. Contesto del personaggio: {person['occupation']}. Abbigliamento quotidiano semplice, non uniforme. Aspetto e silhouette distinti rispetto agli altri nove ritratti. Identità dichiarata nel profilo: {person['gender_identity']}; nessun indicatore visivo stereotipato.", '']
lines += ['## Creatività illustrate del feed — tre annunci', '', 'Tre bitmap consentono lo swipe progressivo fra annunci. Sono reinterpretazioni per il video, NON immagini originali ricevute da Decision. Percentuali e interviste restano collegate agli asset_id originali; non dichiarare che il modello abbia visto questi nuovi bitmap.', '', '### ad-FGR-U3.png — annuncio protagonista', 'Fotografia pubblicitaria editoriale realistica per una collezione abbigliamento autunno-inverno. Persona adulta fittizia indossa un capo casual di mezza stagione; tessuto e vestibilità chiaramente visibili, luce naturale morbida, ambiente quotidiano neutro. Composizione verticale 1080x1350, lasciare il 20% superiore libero per overlay. Palette neutra calda, styling sobrio. Nessun testo, timer, logo, prezzo o watermark. Immagine illustrativa della scheda «capo indossato» del carosello FGR-U3; non inventare benefici tecnici del tessuto. Gli altri pannelli del carosello, timer/pacco/reso facile, saranno SVG/HTML.', '', '### ad-FGR-B1.png — primo swipe', 'Still life fotografico pubblicitario di capi autunno-inverno senza marchio, disposti nella parte inferiore su fondo nero uniforme. Texture realistiche di maglieria e giacca, luce da studio laterale morbida, palette beige e prugna. Formato verticale 1080x1350. Lasciare metà superiore vuota per aggiungere in HTML il testo originale «-30%». Nessun testo o logo generato, nessun prezzo o watermark. Ispirazione: visual documentato FGR-B1, non copia di un annuncio esistente.', '', '### ad-FGR-S1.png — secondo swipe', 'Still life fotografico di pochi capi casual autunno-inverno senza marchio su fondo neutro chiaro, composizione grafica con ampio spazio libero per testo HTML «ULTIME TAGLIE». Formato verticale 1080x1350, luce morbida da studio, capi raccolti nel terzo inferiore. Nessun testo, logo, prezzo, taglia o watermark incorporato. Ispirazione: visual documentato FGR-S1; non presentare il bitmap come input originale di Decision.', '', '## Asset da ricostruire, non da generare con AI', '', '| Asset | Quantità | Fonte / metodo |', '|---|---:|---|', '| Logo ADERA animabile | 1 | Originale utente; rifinire tracciato separando triangolo/barre/wordmark, senza cambiare identità |', '| Loghi provider | 5 | SVG scaricati e manifest con hash |', '| Etichette Timestral e Decision | 2 | Tipografia Inter, nessun logo fittizio |', '| Font Inter Variable | 1 famiglia | Recuperare dipendenza/font della dashboard e rispettare licenza |', '| Card personas | 10 | JSON persona-library; avatar generati separati |', '| Feed e deck annunci | 1 sistema / 3 card | SVG/HTML, swipe e azioni animate |', '| Pannelli pacco, timer e reso | 3 | SVG semplici, coerenti con FGR-U3 |', '| Percentuali Decision | 1 esempio individuale + vista aggregata | Run verificato, indicare chiaramente quale livello si mostra |', '| Notifiche azioni | 4 varianti | Solo azioni presenti nello schema; non inventare commenti probabilistici |', '| Intervista | 1 domanda / 2 risposte | Estratti registrati da product-story, verificare corrispondenza persona/asset |', '| Diagramma orchestrazione | 1 | T3 e provider; ruoli effettivi distinti |', '| Documento dei segnali | 1 | Morph da card a documento SVG |', '| Grafico forecast | 1 sistema / 2 inquadrature | Serie effettive, camera sulla punta e zoom-out |', '| Marker eventi | 3 | Black Week 20/11, Black Friday 27/11, Cyber Monday 30/11/2026 |', '| Storico + gap + previsione | 3 layer | Storico ancora da recuperare con schema verificato; nessuna interpolazione inventata |', '| Confronto modelli | 1 | model-validation; scegliere metrica e fold prima dei claim |', '| Dashboard | 3 viste proposte | Overview, analisi forecast, personas/creatività; escludere Come funziona |', '| Tipografia cinetica e chiusura | 1 sistema | Testi storyboard, frecce e transizioni SVG/HTML |', '', '## Totale immagini da generare', '**13 PNG: 10 avatar + 3 creatività.** Nessun generatore richiesto per loghi, grafici, schermate, diagrammi o testi. Sei anteprime scene verranno composte da asset e UI reali, non inventate da un modello immagini.', '']
(OUT / 'ASSET_E_PROMPT.md').write_text('\n'.join(lines))
html = '<!doctype html><meta charset="utf-8"><style>.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.tile{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px}.image{height:90px;background:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center}img{max-width:90%;max-height:70px}p{font-family:var(--font-sans);color:var(--foreground);margin-bottom:0}</style><div class="grid">'
for entry in manifest:
    if entry['status'] == 'downloaded':
        html += f'<div class="tile"><div class="image"><img src="{BRANDS / entry["file"]}"></div><p>{entry["file"].removesuffix(".svg")}</p></div>'
html += '</div><style>img{color-scheme:light}</style>'
(OUT / 'logos.html').write_text(html)
print(json.dumps(manifest, indent=2))
