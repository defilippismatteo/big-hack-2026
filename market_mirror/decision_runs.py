"""Persistent, per-person Decisions cache and append-only request history."""
import json
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .contracts import digest, read, write
from .feed import build_plan
from .providers import decide, decision_preflight
from .signals import aggregate


def now():
    return datetime.now(timezone.utc).isoformat()


def analysis_key(plan, qid):
    return digest({'version': 1, 'api_version': 'v1beta', 'asset_id': plan['asset_id'],
                   'persona_id': plan['assignments'][qid]['persona_id'],
                   'model': plan['request']['model'], 'input': plan['request']['input'],
                   'question': plan['request']['questions'][qid], 'scenario': plan['scenario']})


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY, status TEXT NOT NULL, created_at TEXT NOT NULL,
                finished_at TEXT, seconds REAL, plan TEXT NOT NULL, raw_path TEXT NOT NULL,
                error_type TEXT, error_code TEXT
            );
            CREATE TABLE IF NOT EXISTS analyses (
                cache_key TEXT PRIMARY KEY, asset_id TEXT NOT NULL, persona_id TEXT NOT NULL,
                model TEXT NOT NULL, scenario TEXT NOT NULL, request_id TEXT NOT NULL,
                qid TEXT NOT NULL, status TEXT NOT NULL, answer TEXT
            );
        ''')

    def close(self):
        self.db.close()

    def get(self, key):
        return self.db.execute('SELECT * FROM analyses WHERE cache_key=?', (key,)).fetchone()

    def claim(self, plan, qids, raw_path, retry_rejected=False):
        request_id = uuid.uuid4().hex
        req = {**plan['request'], 'questions': {q: plan['request']['questions'][q] for q in qids}}
        fragment = {**plan, 'request': req, 'request_sha256': digest(req),
                    'assignments': {q: plan['assignments'][q] for q in qids}}
        try:
            self.db.execute('BEGIN IMMEDIATE')
            for qid in qids:
                row = self.get(analysis_key(plan, qid))
                if row and not (row['status'] == 'rejected' and retry_rejected):
                    raise ValueError('Analisi già registrata o in corso: nessun secondo invio')
            self.db.execute('INSERT INTO requests(id,status,created_at,plan,raw_path) VALUES(?,?,?,?,?)',
                            (request_id, 'pending', now(), json.dumps(fragment, ensure_ascii=False), str(raw_path)))
            for qid in qids:
                a = plan['assignments'][qid]
                self.db.execute('INSERT OR REPLACE INTO analyses VALUES(?,?,?,?,?,?,?,?,?)',
                                (analysis_key(plan, qid), plan['asset_id'], a['persona_id'], req['model'],
                                 plan['scenario'], request_id, qid, 'pending', None))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        return request_id, fragment

    def finish(self, request_id, fragment, raw, seconds=None):
        if raw['data_kind'] != 'simulated_decision':
            raise ValueError('Il registro live non accetta fixture')
        aggregate(fragment, raw)
        with self.db:
            self.db.execute('UPDATE requests SET status=?,finished_at=?,seconds=COALESCE(?,seconds) WHERE id=?',
                            ('completed', now(), seconds, request_id))
            for qid, answer in raw['response']['answers'].items():
                self.db.execute('UPDATE analyses SET status=?,answer=? WHERE request_id=? AND qid=?',
                                ('completed', json.dumps(answer, ensure_ascii=False), request_id, qid))

    def fail(self, request_id, status, exc, seconds):
        # Never persist exception strings: URLs/headers might include secrets.
        code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
        with self.db:
            self.db.execute('UPDATE requests SET status=?,finished_at=?,seconds=?,error_type=?,error_code=? WHERE id=?',
                            (status, now(), seconds, type(exc).__name__, str(code) if code else None, request_id))
            self.db.execute('UPDATE analyses SET status=? WHERE request_id=?', (status, request_id))

    def recover_saved_responses(self):
        rows = list(self.db.execute("SELECT * FROM requests WHERE status='pending'"))
        for row in rows:
            if Path(row['raw_path']).exists():
                try:
                    self.finish(row['id'], json.loads(row['plan']), read(row['raw_path']))
                except (ValueError, KeyError) as exc:
                    self.fail(row['id'], 'invalid_response', exc, row['seconds'] or 0)

    def export(self):
        queries = [dict(r) for r in self.db.execute('SELECT cache_key,asset_id,persona_id,model,scenario,request_id,status FROM analyses ORDER BY asset_id,persona_id')]
        requests = [dict(r) for r in self.db.execute('SELECT id,status,created_at,finished_at,seconds,raw_path,error_type,error_code FROM requests ORDER BY created_at')]
        return {'schema_version': '1.0', 'analyses': queries, 'requests': requests,
                'notice': 'A pending/ambiguous/invalid response is never automatically resubmitted.'}


def run_asset(ledger, plan, out, api, retry_rejected=False):
    out = Path(out)
    decision_preflight(plan)
    ledger.recover_saved_responses()
    missing, reused = [], 0
    for qid in plan['request']['questions']:
        cached = ledger.get(analysis_key(plan, qid))
        if cached and cached['status'] == 'completed':
            reused += 1
        elif cached and not (cached['status'] == 'rejected' and retry_rejected):
            raise ValueError(f"Analisi {cached['status']} da verificare per {cached['asset_id']}/{cached['persona_id']}; nessun reinvio automatico")
        else:
            missing.append(qid)
    source_ids = set()
    if missing:
        if api is None:
            raise ValueError('Analisi non presente nel registro: serve --live per una nuova chiamata, nessuna fixture prodotta')
        raw_path = out / 'raw' / f'{uuid.uuid4().hex}.json'
        request_id, fragment = ledger.claim(plan, missing, raw_path, retry_rejected)
        write(out / 'requests' / f'{request_id}.json', fragment)
        started = time.monotonic()
        try:
            raw = decide(fragment, api)
        except Exception as exc:
            code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
            state = 'rejected' if str(code) in {'400','401','403','404','429'} else 'ambiguous'
            ledger.fail(request_id, state, exc, time.monotonic() - started)
            raise RuntimeError(f"Decision {state}: {type(exc).__name__}, codice {code or 'non disponibile'}. Registro aggiornato; nessun retry automatico.") from None
        write(raw_path, raw)  # Preserve the actual response before validating or aggregating.
        try:
            ledger.finish(request_id, fragment, raw, time.monotonic() - started)
        except (ValueError, KeyError) as exc:
            ledger.fail(request_id, 'invalid_response', exc, time.monotonic() - started)
            raise RuntimeError('Risposta Decision salvata ma non valida: ispezionare raw senza ripetere la chiamata') from None
    answers = {}
    for qid in plan['request']['questions']:
        row = ledger.get(analysis_key(plan, qid))
        answers[qid] = json.loads(row['answer'])
        source_ids.add(row['request_id'])
    combined = {'schema_version': '1.0', 'data_kind': 'simulated_decision', 'provider': 'google',
                'model': plan['request']['model'], 'request_sha256': plan['request_sha256'],
                'source_request_ids': sorted(source_ids), 'response': {'answers': answers}}
    signal = aggregate(plan, combined)
    asset_out = out / 'assets' / plan['asset_id']
    write(asset_out / 'plan.json', plan)
    write(asset_out / 'combined_raw.json', combined)
    write(asset_out / 'signals.json', signal)
    return {'asset_id': plan['asset_id'], 'status': 'completed', 'new_questions': len(missing),
            'reused_questions': reused, 'api_requests': int(bool(missing)), 'signal': signal}


def refresh_summary(ledger, catalog, cards, out, model, seed, results=(), request_count_before=None):
    """Publish all completed results even if a later asset was rate-limited."""
    complete, states = [], []
    verticals = {p['vertical'] for p in cards['personas']}
    for asset in catalog['creatives']:
        if asset['vertical'] not in verticals:
            continue
        n = sum(p['vertical'] == asset['vertical'] for p in cards['personas'])
        plan = build_plan(catalog, cards, asset['asset_id'], n, seed, model)
        records = [ledger.get(analysis_key(plan, q)) for q in plan['request']['questions']]
        if all(r is not None and r['status'] == 'completed' for r in records):
            complete.append(run_asset(ledger, plan, out, None)['signal'])
            state = 'completed'
        else:
            state = next((r['status'] for r in records if r is not None and r['status'] != 'completed'), 'not_run')
        states.append({'asset_id': asset['asset_id'], 'status': state,
                       'completed_questions': sum(r is not None and r['status'] == 'completed' for r in records)})
    registry = ledger.export()
    token_counts, seconds = [], []
    for request in registry['requests']:
        if request['status'] == 'completed':
            raw = read(request['raw_path'])
            count = raw['response'].get('usage', {}).get('total_input_tokens')
            if isinstance(count, (int, float)):
                token_counts.append(count)
            if request['seconds'] is not None:
                seconds.append(request['seconds'])
    summary = {'schema_version': '1.0', 'data_kind': 'simulated_decision', 'calibrated_to_ctr': False,
               'assets': len(complete), 'planned_assets': len(states), 'asset_states': states,
               'persona_asset_evaluations': sum(s['n_personas'] for s in complete),
               'new_api_requests': len(registry['requests']) - request_count_before if request_count_before is not None else 0,
               'new_questions': sum(r['new_questions'] for r in results),
               'reused_questions': sum(r['reused_questions'] for r in results),
               'recorded_requests': len(registry['requests']),
               'completed_requests': sum(r['status'] == 'completed' for r in registry['requests']),
               'usage': {'reported_input_tokens': sum(token_counts) if token_counts else None,
                         'requests_with_usage': len(token_counts),
                         'mean_completed_request_seconds': sum(seconds) / len(seconds) if seconds else None},
               'usage_note': f"{sum(token_counts):,} token input dichiarati su {len(token_counts)} richieste completate; costo monetario non misurato.".replace(',', '.'),
               'ranking': sorted(complete, key=lambda s: (-s['click_intent_signal'], -s['attention_signal'], s['asset_id']))}
    write(Path(out) / 'summary.json', summary)
    return summary


def analyze(catalog, cards, out, api, asset_ids=None, model='gemini-decision-1', seed=2026, retry_rejected=False):
    out = Path(out).resolve()
    ledger = Ledger(out / 'ledger.sqlite')
    verticals = {p['vertical'] for p in cards['personas']}
    assets = [a for a in catalog['creatives'] if a['vertical'] in verticals]
    if asset_ids:
        if set(asset_ids) - {a['asset_id'] for a in assets}:
            raise ValueError('Asset richiesto assente o senza personas del settore')
        assets = [a for a in assets if a['asset_id'] in asset_ids]
    results = []
    request_count_before = len(ledger.export()['requests'])
    try:
        for asset in assets:
            people = [p for p in cards['personas'] if p['vertical'] == asset['vertical']]
            if not 1 <= len(people) <= 4:
                raise ValueError('Il primo giro live supporta da 1 a 4 persone per settore')
            plan = build_plan(catalog, cards, asset['asset_id'], len(people), seed, model)
            result = run_asset(ledger, plan, out, api, retry_rejected)
            results.append(result)
            write(out / 'ledger.json', ledger.export())
        return results
    finally:
        write(out / 'ledger.json', ledger.export())
        try:
            refresh_summary(ledger, catalog, cards, out, model, seed, results, request_count_before)
        finally:
            ledger.close()
