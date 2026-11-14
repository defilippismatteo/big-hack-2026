"""Prepare provider-neutral, outcome-blind tasks and import real T3 results."""
import json
import random
from pathlib import Path

from .contracts import DETAIL_FIELDS, SLOT_FIELDS, digest, project, validate_card, write
from .personas import writer_payload
from .starter import build_context, generate_slots


def build_jobs(context, slots, batch_size=4):
    if not 1 <= batch_size <= 24:
        raise ValueError("Batch size consentito: 1–24")
    jobs = []
    for sector in context['verticals']:
        selected = [s for s in slots['slots'] if s['vertical'] == sector['vertical']]
        for offset in range(0, len(selected), batch_size):
            records = []
            for source in selected[offset:offset + batch_size]:
                slot = project(source, SLOT_FIELDS)
                band = slot['age_band']
                low, high = (int(band[:-1]), 80) if band.endswith('+') else map(int, band.split('-'))
                rng = random.Random(int(digest([slot['seed'], slot['persona_id'], 'exact_age'])[:16], 16))
                slot['age_years'] = rng.randint(low, high)
                records.append(slot)
            job = {'schema_version': '2.0', 'job_id': f"{sector['vertical']}-{offset // batch_size + 1:02d}",
                   'sector': writer_payload(context, selected[0])['sector'], 'slots': records,
                   'output_contract': {'root': 'personas', 'records': {'persona_id': 'identico allo slot',
                                       'name': 'nome fittizio', 'interests': 'array di 3–8 interessi distinti',
                                       **{k: 'stringa italiana non vuota' for k in DETAIL_FIELDS}}},
                   'sampling_notice': 'Quote manuali; età 65+ limitata a 80 per questo disegno. Nessuna quota osservata.'}
            job['input_sha256'] = digest(job)
            jobs.append(job)
    return jobs


def task_prompt(job):
    return (
        'TASK PERSONA WRITER — esegui solo questo task di generazione.\n'
        'Usa esclusivamente i dati inline qui sotto. Non usare strumenti, non leggere file, '
        'non consultare internet, repository, cronologia del coordinatore, creatività o KPI. '
        'Non lanciare subagenti e non chiamare API. Rispondi soltanto con JSON valido.\n'
        'Crea una persona fittizia per ogni slot. Python ha già scelto settore, età esatta, '
        'genere, motivazione, uso social, rischio e interesse: non modificarli. '
        'Restituisci persona_id, nome, 3–8 interessi distinti (anche estranei alla categoria) '
        'e tutti i campi del contratto. Gli interessi devono rispettare anche un interesse '
        'basso nella categoria: non trasformare tutti in clienti ideali. '
        'Differenzia professioni, contesto economico, bisogni e occasioni d’acquisto; '
        'scrivi routine concrete, requisiti di fiducia, timori e una contraddizione plausibile. '
        'Evita stereotipi e schede uguali; non dedurre preferenze dal solo genere o età. '
        'Nessun annuncio da giudicare ora, nessuna previsione di click o CTR. '
        'I profili saranno congelati prima dei test e riutilizzati nelle varie creatività.\n'
        + json.dumps(job, ensure_ascii=False, indent=2)
    )


def import_response(job, response, receipt, existing=None):
    snapshot = {k: v for k, v in job.items() if k != 'input_sha256'}
    if digest(snapshot) != job['input_sha256']:
        raise ValueError('Job modificato dopo il freeze')
    if receipt.get('providerInstanceId') != 'antigravity' or not str(receipt.get('executedModel', '')).startswith('gemini-'):
        raise ValueError('Serve la ricevuta effettiva del subagente Gemini/Antigravity')
    if not receipt.get('link') or not receipt.get('taskId'):
        raise ValueError('Ricevuta T3 incompleta')
    if set(response) != {'personas'} or not isinstance(response['personas'], list):
        raise ValueError('Risposta attesa: oggetto con lista personas')
    slots = {s['persona_id']: s for s in job['slots']}
    incoming = response['personas']
    if len(incoming) != len(slots) or {p['persona_id'] for p in incoming} != set(slots):
        raise ValueError('Persone mancanti, duplicate o non previste dal job')
    result = {p['persona_id']: p for p in (existing or {}).get('personas', [])}
    for record in incoming:
        allowed = {'persona_id', 'name', 'interests', *DETAIL_FIELDS}
        if set(record) != allowed:
            raise ValueError('La risposta deve contenere solo i campi generativi del contratto')
        slot = slots[record['persona_id']]
        card = {**slot, **record, 'schema_version': '2.0', 'data_kind': 'synthetic',
                'provider': 't3:antigravity', 'model': receipt['executedModel']}
        validate_card(card)
        result[card['persona_id']] = card
    summaries = [p['persona_summary'].strip().casefold() for p in result.values()]
    if len(summaries) != len(set(summaries)):
        raise ValueError('Riassunti persona duplicati')
    receipts = (existing or {}).get('runs', []) + [{'job_id': job['job_id'],
                'input_sha256': job['input_sha256'], 'response_sha256': digest(response), 't3_receipt': receipt}]
    return {'schema_version': '2.0', 'data_kind': 'synthetic', 'personas': sorted(result.values(), key=lambda p: p['persona_id']),
            'runs': receipts, 'isolation': 'fresh T3 task with inline projected inputs; filesystem not sandboxed'}


def prepare_jobs(data_dir, out, n=24, batch_size=4, seed=2026):
    context = build_context(data_dir)
    slots = generate_slots(context, n, seed)
    jobs = build_jobs(context, slots, batch_size)
    out = Path(out)
    write(out / 'safe_inputs/public_context.json', context)
    write(out / 'safe_inputs/persona_slots.json', slots)
    for job in jobs:
        write(out / 'jobs' / f"{job['job_id']}.json", job)
        (out / 'jobs' / f"{job['job_id']}.prompt.txt").write_text(task_prompt(job), encoding='utf-8')
    summary = {'schema_version': '2.0', 'n_slots': len(slots['slots']), 'n_jobs': len(jobs),
               'batch_size': batch_size, 'seed': seed, 'generation_transport': 'T3 subagent, Antigravity subscription',
               'external_api': 'Gemini Decisions only', 'first_probe': jobs[0]['job_id']}
    write(out / 'manifest.json', summary)
    (out / 'ORCHESTRATE.md').write_text(
        '# Prompt riutilizzabile per T3 Code\n\n'
        f'Usa i job in {out / "jobs"}. Il pool previsto è {len(slots["slots"])} persone, '
        f'{n} per settore; seed {seed}. Prima esegui soltanto {jobs[0]["job_id"]}.\n\n'
        '1. Verifica le capacità T3 e il provider Antigravity/gemini-4-hydrogen, thinking low. '
        'Non sostituire il provider se indisponibile. Nessuna API generativa.\n'
        '2. Per ogni job richiesto crea un task T3 nuovo, senza storia del padre; passa '
        'come task solo il contenuto del corrispondente .prompt.txt. Non allegare repository, '
        'creatività, storico o forecast. Il figlio restituisce JSON e non usa strumenti.\n'
        '3. Salva risposta e ricevuta T3 (taskId, providerInstanceId, executedModel, link). '
        'Esegui t3-import. Ferma la pipeline su errori del contratto; non correggere '
        'silenziosamente le risposte del modello o chiamare un provider alternativo.\n'
        '4. Mostra le schede con personas-view. Solo dopo il freeze costruisci plan '
        'con le schede approvate e il catalogo creativo separato.\n'
        '5. Delega il worker Decisions con il solo piano, output e comando Python. '
        'Esegui prima il preflight senza rete. Per il live usa GEMINI_API_KEY locale '
        'solo per Decision 1, mai nel prompt. Non dichiarare disponibile Decision tramite '
        'abbonamento se non verificato: questa fase usa la sua API distinta.\n'
        '6. Salva raw, aggrega e aggiorna il viewer. Nessuna integrazione Timestral ora.\n', encoding='utf-8')
    return summary


def render_cards(cards, plan=None):
    for p in cards['personas']:
        validate_card(p)
    data = json.dumps({'cards': cards, 'plan': plan}, ensure_ascii=False).replace('<', '\\u003c')
    return CARD_VIEW.replace('__DATA__', data)


CARD_VIEW = '''<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Persone generate da T3</title>
<style>:root{color-scheme:light dark;font-family:system-ui,sans-serif}*{box-sizing:border-box}body{margin:0;background:transparent;color:var(--foreground,light-dark(#222,#eee));font-size:14px;line-height:1.5}.muted{color:var(--muted-foreground,light-dark(#666,#aaa))}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.card{padding:16px;background:var(--card,light-dark(#fafafa,#222));border:1px solid var(--border,light-dark(#ddd,#444));border-radius:var(--radius,12px)}h2{font-size:18px;margin:0 0 6px}h3{font-size:14px;margin:14px 0 4px}p{margin:6px 0}.tag{color:var(--primary,#8062e3)}details{margin-top:12px}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;max-height:350px;overflow:auto}.post{border-left:2px solid var(--border,light-dark(#ddd,#555));padding:8px;margin:8px 0}@media(max-width:540px){.grid{grid-template-columns:1fr}}</style>
<body><p><b id="count"></b> · persone sintetiche scritte da Gemini attraverso T3 Code</p><p class="muted">Gli attributi di partenza sono stati assegnati da Python prima di mostrare gli annunci. Le reazioni Decision sono una fase separata.</p><div class="grid" id="cards"></div><p class="muted">Schede reali del run T3; nessuna risposta di Decision 1 è inventata. Il primo feed è controllato: tre post neutri fissi più un annuncio testuale.</p><script type="application/json" id="data">__DATA__</script><script>
const D=JSON.parse(document.getElementById('data').textContent),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
document.getElementById('count').textContent=D.cards.personas.length+' schede generate';
const labels={occupation:'Occupazione',economic_context:'Contesto economico',daily_routine:'Routine e occasioni',decision_habits:'Come decide',trust_requirements:'Requisiti di fiducia',ad_avoidance:'Rapporto con la pubblicità',concerns:'Preoccupazioni',contradiction:'Contraddizione'};
document.getElementById('cards').innerHTML=D.cards.personas.map(p=>{let feed='';if(D.plan){const a=Object.values(D.plan.assignments).find(a=>a.persona_id===p.persona_id);if(a){feed='<details><summary>Feed assegnato · '+esc(a.feed.platform)+'</summary>'+a.feed.items.map(i=>'<div class="post">'+(i.kind==='sponsored'?'<b>Sponsorizzato</b><p>'+esc(D.plan.request.input)+'</p>':'<b>'+esc(i.author)+'</b><p>'+esc(i.text)+'</p>')+'</div>').join('')+'<p class="muted">Valutazione Decision non ancora eseguita.</p></details>'}}return '<article class="card"><span class="tag">'+esc(p.persona_id)+'</span><h2>'+esc(p.name||p.persona_id)+' · '+esc(p.age_years||p.age_band)+' anni</h2><p class="muted">'+esc(p.vertical)+' · '+esc(p.gender_identity)+' · interesse categoria '+esc(p.interest_in_category)+'</p><p>'+esc((p.interests||[]).join(' · '))+'</p><p>'+esc(p.persona_summary)+'</p><details><summary>Scheda completa e provenienza</summary>'+Object.entries(labels).map(([k,l])=>'<h3>'+l+'</h3><p>'+esc(p[k])+'</p>').join('')+'<p class="muted">'+esc(p.provider)+' / '+esc(p.model)+' · seed '+esc(p.seed)+'</p><pre>'+esc(JSON.stringify(p,null,2))+'</pre></details>'+feed+'</article>'}).join('');
</script></body></html>'''
