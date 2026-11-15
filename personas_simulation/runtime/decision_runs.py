"""Persistent, per-person Decisions cache and append-only request history."""
import json
import math
import queue
import sqlite3
import threading
import time
import uuid
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path

from .contracts import digest, read, write
from .feed import build_plan
from .providers import decide, decision_preflight
from .signals import aggregate

CAMPAIGN_BY_VERTICAL = {
    'beauty_skincare': {'campaign_id': 'NDL-C1', 'campaign_name': 'NDL | Vendite | Skincare', 'inserzionista_id': 'NDL'},
    'pet_ecommerce': {'campaign_id': 'CDF-C1', 'campaign_name': 'CDF | Vendite | Cani e gatti', 'inserzionista_id': 'CDF'},
    'abbigliamento': {'campaign_id': 'FGR-C1', 'campaign_name': 'FGR | Vendite | Autunno-Inverno', 'inserzionista_id': 'FGR'},
}


def now():
    return datetime.now(timezone.utc).isoformat()


def estimate_request_tokens(input_text, questions_dict):
    """Conservative input token estimate calibrated on observed gemini-decision-1 usage (~3.77 chars/tok)."""
    if not questions_dict:
        return 0
    chars = len(str(input_text or '')) + sum(
        len(json.dumps(q, ensure_ascii=False)) for q in questions_dict.values()
    )
    return math.ceil(chars / 3.45) + 32 * len(questions_dict)


def pack_question_chunks(plan, qids, batch_size=34, max_est_tokens=41000):
    """Pack qids into chunks respecting both max question count and max estimated token budget."""
    if not 1 <= batch_size <= 1000:
        raise ValueError('Batch size Decision consentito: 1–1000')
    questions = plan['request']['questions']
    input_text = plan['request']['input']
    if not qids:
        return []
    if not max_est_tokens or max_est_tokens <= 0:
        return [qids[i:i + batch_size] for i in range(0, len(qids), batch_size)]
    chunks, current = [], []
    for qid in qids:
        candidate = current + [qid]
        est = estimate_request_tokens(input_text, {q: questions[q] for q in candidate})
        if current and (len(candidate) > batch_size or est > max_est_tokens):
            chunks.append(current)
            current = [qid]
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def analysis_key(plan, qid):
    return digest({'version': 1, 'api_version': 'v1beta', 'asset_id': plan['asset_id'],
                   'persona_id': plan['assignments'][qid]['persona_id'],
                   'model': plan['request']['model'], 'input': plan['request']['input'],
                   'question': plan['request']['questions'][qid], 'scenario': plan['scenario']})


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
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
        with self._lock:
            self.db.close()

    def get(self, key):
        with self._lock:
            return self.db.execute('SELECT * FROM analyses WHERE cache_key=?', (key,)).fetchone()

    def last_request_created_at(self):
        with self._lock:
            row = self.db.execute('SELECT created_at FROM requests ORDER BY created_at DESC LIMIT 1').fetchone()
            return row['created_at'] if row else None

    def recent_requests(self, limit=50):
        with self._lock:
            return list(self.db.execute(
                'SELECT created_at, plan, raw_path, status FROM requests ORDER BY created_at DESC LIMIT ?',
                (limit,),
            ).fetchall())

    def claim(self, plan, qids, raw_path, retry_rejected=False):
        request_id = uuid.uuid4().hex
        req = {**plan['request'], 'questions': {q: plan['request']['questions'][q] for q in qids}}
        fragment = {**plan, 'request': req, 'request_sha256': digest(req),
                    'assignments': {q: plan['assignments'][q] for q in qids}}
        with self._lock:
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
        with self._lock:
            with self.db:
                self.db.execute('UPDATE requests SET status=?,finished_at=?,seconds=COALESCE(?,seconds) WHERE id=?',
                                ('completed', now(), seconds, request_id))
                for qid, answer in raw['response']['answers'].items():
                    self.db.execute('UPDATE analyses SET status=?,answer=? WHERE request_id=? AND qid=?',
                                    ('completed', json.dumps(answer, ensure_ascii=False), request_id, qid))

    def fail(self, request_id, status, exc, seconds):
        # Never persist exception strings: URLs/headers might include secrets.
        code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
        with self._lock:
            with self.db:
                self.db.execute('UPDATE requests SET status=?,finished_at=?,seconds=?,error_type=?,error_code=? WHERE id=?',
                                (status, now(), seconds, type(exc).__name__, str(code) if code else None, request_id))
                self.db.execute('UPDATE analyses SET status=? WHERE request_id=?', (status, request_id))

    def recover_saved_responses(self):
        with self._lock:
            rows = list(self.db.execute("SELECT * FROM requests WHERE status='pending'"))
        for row in rows:
            if Path(row['raw_path']).exists():
                try:
                    self.finish(row['id'], json.loads(row['plan']), read(row['raw_path']))
                except (ValueError, KeyError) as exc:
                    self.fail(row['id'], 'invalid_response', exc, row['seconds'] or 0)

    def export(self):
        with self._lock:
            queries = [dict(r) for r in self.db.execute('SELECT cache_key,asset_id,persona_id,model,scenario,request_id,status FROM analyses ORDER BY asset_id,persona_id')]
            requests = [dict(r) for r in self.db.execute('SELECT id,status,created_at,finished_at,seconds,raw_path,error_type,error_code FROM requests ORDER BY created_at')]
        return {'schema_version': '1.0', 'analyses': queries, 'requests': requests,
                'notice': 'A pending/ambiguous/invalid response is never automatically resubmitted.'}


class KeyRateLimiter:
    """Thread-safe sliding-window RPM + TPM limiter for one API key (or shared quota)."""

    def __init__(self, tpm_limit=45000, rpm_limit=12, min_interval_s=5.2, window_s=62.0):
        self.tpm_limit = tpm_limit
        self.rpm_limit = rpm_limit
        self.min_interval_s = min_interval_s
        self.window_s = window_s
        self._lock = threading.Lock()
        self._events = deque()  # list of [monotonic_ts, tokens]
        self._last_ts = None
        self._cooldown_until = 0.0

    def note_429(self, cooldown_s=65.0):
        with self._lock:
            self._cooldown_until = max(self._cooldown_until, time.monotonic() + cooldown_s)

    def acquire(self, est_tokens):
        while True:
            wait_s = 0.0
            with self._lock:
                now_m = time.monotonic()
                if now_m < self._cooldown_until:
                    wait_s = self._cooldown_until - now_m
                else:
                    while self._events and now_m - self._events[0][0] >= self.window_s:
                        self._events.popleft()
                    if self.min_interval_s and self._last_ts is not None:
                        elapsed = now_m - self._last_ts
                        if elapsed < self.min_interval_s:
                            wait_s = max(wait_s, self.min_interval_s - elapsed)
                    if self.rpm_limit and self.rpm_limit > 0 and len(self._events) >= self.rpm_limit:
                        wait_s = max(wait_s, self.window_s - (now_m - self._events[0][0]) + 0.25)
                    if self.tpm_limit and self.tpm_limit > 0:
                        used_tokens = sum(entry[1] for entry in self._events)
                        if self._events and used_tokens + est_tokens > self.tpm_limit:
                            # Wait until enough oldest entries expire to fit est_tokens.
                            running = used_tokens
                            for ts, tok in self._events:
                                running -= tok
                                if running + est_tokens <= self.tpm_limit:
                                    wait_s = max(wait_s, self.window_s - (now_m - ts) + 0.25)
                                    break
                            else:
                                wait_s = max(wait_s, self.window_s - (now_m - self._events[0][0]) + 0.25)
                    if wait_s <= 0.0:
                        entry = [now_m, est_tokens]
                        self._events.append(entry)
                        self._last_ts = now_m
                        return entry
            time.sleep(min(wait_s, 65.0))

    def reconcile(self, entry, actual_tokens):
        if isinstance(actual_tokens, (int, float)) and actual_tokens > 0:
            with self._lock:
                entry[1] = int(actual_tokens)


def _wait_for_pacing(ledger, min_interval_s, tpm_limit, next_est_tokens):
    if not 0 <= min_interval_s <= 60:
        raise ValueError('Intervallo richieste consentito: 0–60 secondi')
    if min_interval_s:
        last_ts = ledger.last_request_created_at()
        if last_ts:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_ts)).total_seconds()
            if elapsed < min_interval_s:
                time.sleep(min_interval_s - elapsed)
    if tpm_limit and tpm_limit > 0:
        while True:
            now_dt = datetime.now(timezone.utc)
            recent = ledger.recent_requests(50)
            used = 0
            oldest_in_window = None
            for row in recent:
                dt = datetime.fromisoformat(row['created_at'])
                age = (now_dt - dt).total_seconds()
                if age >= 61.0:
                    continue
                oldest_in_window = dt if oldest_in_window is None or dt < oldest_in_window else oldest_in_window
                tokens = None
                if row['status'] == 'completed' and Path(row['raw_path']).exists():
                    try:
                        tokens = read(row['raw_path'])['response'].get('usage', {}).get('total_input_tokens')
                    except Exception:
                        tokens = None
                if not isinstance(tokens, (int, float)):
                    req_obj = json.loads(row['plan']).get('request', {})
                    tokens = estimate_request_tokens(req_obj.get('input', ''), req_obj.get('questions', {}))
                used += tokens
            if used + next_est_tokens <= tpm_limit or oldest_in_window is None:
                break
            wait_s = max(1.0, 61.5 - (now_dt - oldest_in_window).total_seconds())
            time.sleep(min(wait_s, 62.0))


def _finalize_asset(ledger, plan, out):
    answers = {}
    source_ids = set()
    for qid in plan['request']['questions']:
        row = ledger.get(analysis_key(plan, qid))
        answers[qid] = json.loads(row['answer'])
        source_ids.add(row['request_id'])
    combined = {'schema_version': '1.0', 'data_kind': 'simulated_decision', 'provider': 'google',
                'model': plan['request']['model'], 'request_sha256': plan['request_sha256'],
                'source_request_ids': sorted(source_ids), 'response': {'answers': answers}}
    signal = aggregate(plan, combined)
    asset_out = Path(out) / 'assets' / plan['asset_id']
    write(asset_out / 'plan.json', plan)
    write(asset_out / 'combined_raw.json', combined)
    write(asset_out / 'signals.json', signal)
    return signal


def run_asset(ledger, plan, out, api, retry_rejected=False, min_interval_s=0, batch_size=25, tpm_limit=0):
    if not 1 <= batch_size <= 1000:
        raise ValueError('Batch size Decision consentito: 1–1000')
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
    api_requests = 0
    if missing:
        if api is None:
            raise ValueError('Analisi non presente nel registro: serve --live per una nuova chiamata, nessuna fixture prodotta')
        max_chunk_tok = max(int(tpm_limit * 0.9), 15000) if tpm_limit and tpm_limit > 0 else 0
        chunks = pack_question_chunks(plan, missing, batch_size=batch_size, max_est_tokens=max_chunk_tok)
        for chunk in chunks:
            est_tokens = estimate_request_tokens(plan['request']['input'], {q: plan['request']['questions'][q] for q in chunk})
            _wait_for_pacing(ledger, min_interval_s, tpm_limit, est_tokens)
            raw_path = out / 'raw' / f'{uuid.uuid4().hex}.json'
            request_id, fragment = ledger.claim(plan, chunk, raw_path, retry_rejected)
            write(out / 'requests' / f'{request_id}.json', fragment)
            started = time.monotonic()
            try:
                raw = decide(fragment, api)
            except Exception as exc:
                code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
                state = 'rejected' if str(code) in {'400', '401', '403', '404', '429'} else 'ambiguous'
                ledger.fail(request_id, state, exc, time.monotonic() - started)
                raise RuntimeError(f"Decision {state}: {type(exc).__name__}, codice {code or 'non disponibile'}. Registro aggiornato; nessun retry automatico.") from None
            write(raw_path, raw)  # Preserve the actual response before validating or aggregating.
            try:
                ledger.finish(request_id, fragment, raw, time.monotonic() - started)
            except (ValueError, KeyError) as exc:
                ledger.fail(request_id, 'invalid_response', exc, time.monotonic() - started)
                raise RuntimeError('Risposta Decision salvata ma non valida: ispezionare raw senza ripetere la chiamata') from None
            api_requests += 1
    signal = _finalize_asset(ledger, plan, out)
    return {'asset_id': plan['asset_id'], 'status': 'completed', 'new_questions': len(missing),
            'reused_questions': reused, 'api_requests': api_requests, 'signal': signal}


def build_categorization(summary, cards, catalog):
    """Categorize every persona's Decision 1 profile and rank campaigns/assets/cohorts."""
    people_map = {p['persona_id']: p for p in cards['personas']}
    creatives_map = {c['asset_id']: c for c in catalog['creatives']}
    persona_rows = {}
    asset_rows = []
    campaign_buckets = {}
    lever_buckets = {}

    for sig in summary.get('ranking', []):
        aid = sig['asset_id']
        creative = creatives_map.get(aid, {})
        vertical = sig['vertical']
        camp = CAMPAIGN_BY_VERTICAL.get(vertical, {'campaign_id': vertical, 'campaign_name': vertical, 'inserzionista_id': ''})
        cid = camp['campaign_id']
        cohort_groups = {'all': [], 'unbiased': [], 'category_conditioned': []}

        for pp in sig['per_person']:
            pid = pp['persona_id']
            card = people_map.get(pid, {})
            cohort = card.get('cohort', 'unbiased')
            cohort_groups['all'].append(pp)
            cohort_groups.setdefault(cohort, []).append(pp)

            prow = persona_rows.setdefault(pid, {
                'persona_id': pid,
                'name': card.get('name', pid),
                'vertical': vertical,
                'campaign_id': cid,
                'cohort': cohort,
                'age_band': card.get('age_band'),
                'age_years': card.get('age_years'),
                'gender_identity': card.get('gender_identity'),
                'interest_in_category': card.get('interest_in_category'),
                'motivation': card.get('motivation'),
                'risk_attitude': card.get('risk_attitude'),
                'social_habit': card.get('social_habit'),
                'n_assets_evaluated': 0,
                'actions_sum': Counter(),
                'reasons_sum': Counter(),
                'top_assets': [],
                'bottom_assets': [],
            })
            prow['n_assets_evaluated'] += 1
            for act, val in pp['actions'].items():
                prow['actions_sum'][act] += val
            for pair, val in pp['probabilities'].items():
                _, reason = pair.split('__', 1)
                prow['reasons_sum'][reason] += val
            prow['top_assets'].append((pp['actions']['click'], 1 - pp['actions']['scroll'], aid))

        cohort_stats = {}
        for cname, items in cohort_groups.items():
            if not items:
                continue
            n = len(items)
            cohort_stats[cname] = {
                'n': n,
                'click_intent_signal': round(sum(x['actions']['click'] for x in items) / n, 6),
                'attention_signal': round(sum(1 - x['actions']['scroll'] for x in items) / n, 6),
                'stop_signal': round(sum(x['actions']['stop'] for x in items) / n, 6),
                'scroll_signal': round(sum(x['actions']['scroll'] for x in items) / n, 6),
            }

        arow = {
            'asset_id': aid,
            'campaign_id': cid,
            'campaign_name': camp['campaign_name'],
            'vertical': vertical,
            'leva': creative.get('leva', ''),
            'formato': creative.get('formato', ''),
            'headline': creative.get('headline', ''),
            'n_personas': sig['n_personas'],
            'click_intent_signal': round(sig['click_intent_signal'], 6),
            'attention_signal': round(sig['attention_signal'], 6),
            'actions': {k: round(v, 6) for k, v in sig['actions'].items()},
            'top_reasons': sorted(((k, round(v, 6)) for k, v in sig['reason_distribution'].items()), key=lambda x: -x[1])[:5],
            'by_cohort': cohort_stats,
        }
        asset_rows.append(arow)
        campaign_buckets.setdefault(cid, {'campaign_id': cid, 'campaign_name': camp['campaign_name'], 'vertical': vertical, 'assets': []})['assets'].append(arow)
        lever_buckets.setdefault((cid, arow['leva']), []).append(arow)

    persona_categories = []
    segment_counts = Counter()
    reason_counts = Counter()
    for pid, prow in sorted(persona_rows.items()):
        n = prow['n_assets_evaluated'] or 1
        mean_actions = {k: round(prow['actions_sum'][k] / n, 6) for k in ('scroll', 'glance', 'stop', 'click')}
        mean_reasons = {k: round(v / n, 6) for k, v in prow['reasons_sum'].most_common()}
        dom_action = max(mean_actions, key=mean_actions.get)
        dom_reason = next(iter(mean_reasons)) if mean_reasons else ''
        click_mean = mean_actions['click']
        attn_mean = round(1.0 - mean_actions['scroll'], 6)
        if click_mean >= 0.15:
            segment = 'high_intent'
        elif attn_mean >= 0.50:
            segment = 'attentive_hesitant'
        elif dom_reason in ('skeptical', 'weak_offer'):
            segment = 'skeptical_resistant'
        else:
            segment = 'low_need_scroll'
        segment_counts[segment] += 1
        reason_counts[dom_reason] += 1
        ranked_assets = sorted(prow['top_assets'], reverse=True)
        persona_categories.append({
            'persona_id': pid,
            'name': prow['name'],
            'vertical': prow['vertical'],
            'campaign_id': prow['campaign_id'],
            'cohort': prow['cohort'],
            'age_band': prow['age_band'],
            'age_years': prow['age_years'],
            'gender_identity': prow['gender_identity'],
            'interest_in_category': prow['interest_in_category'],
            'motivation': prow['motivation'],
            'risk_attitude': prow['risk_attitude'],
            'social_habit': prow['social_habit'],
            'n_assets_evaluated': prow['n_assets_evaluated'],
            'mean_actions': mean_actions,
            'mean_attention_signal': attn_mean,
            'mean_click_intent_signal': click_mean,
            'dominant_action': dom_action,
            'dominant_reason': dom_reason,
            'segment': segment,
            'top_reasons': list(mean_reasons.items())[:5],
            'top_3_assets': [{'asset_id': a, 'click': round(c, 4), 'attention': round(at, 4)} for c, at, a in ranked_assets[:3]],
            'bottom_3_assets': [{'asset_id': a, 'click': round(c, 4), 'attention': round(at, 4)} for c, at, a in ranked_assets[-3:][::-1]],
        })

    campaigns_summary = []
    for cid, bucket in sorted(campaign_buckets.items()):
        alist = bucket['assets']
        n_a = len(alist) or 1
        by_lever = {}
        for a in alist:
            by_lever.setdefault(a['leva'], []).append(a)
        lever_summary = [
            {
                'leva': lv,
                'n_assets': len(items),
                'mean_click_intent': round(sum(x['click_intent_signal'] for x in items) / len(items), 6),
                'mean_attention': round(sum(x['attention_signal'] for x in items) / len(items), 6),
            }
            for lv, items in sorted(by_lever.items())
        ]
        campaigns_summary.append({
            'campaign_id': cid,
            'campaign_name': bucket['campaign_name'],
            'vertical': bucket['vertical'],
            'n_assets': len(alist),
            'mean_click_intent_signal': round(sum(a['click_intent_signal'] for a in alist) / n_a, 6),
            'mean_attention_signal': round(sum(a['attention_signal'] for a in alist) / n_a, 6),
            'top_assets': sorted(alist, key=lambda x: (-x['click_intent_signal'], -x['attention_signal']))[:5],
            'bottom_assets': sorted(alist, key=lambda x: (x['click_intent_signal'], x['attention_signal']))[:5],
            'by_lever': sorted(lever_summary, key=lambda x: -x['mean_click_intent']),
        })
    campaigns_summary.sort(key=lambda x: -x['mean_click_intent_signal'])

    return {
        'schema_version': '1.0',
        'data_kind': 'simulated_decision',
        'calibrated_to_ctr': False,
        'n_personas_categorized': len(persona_categories),
        'n_assets': len(asset_rows),
        'segment_counts': dict(segment_counts),
        'dominant_reason_counts': dict(reason_counts),
        'campaigns': campaigns_summary,
        'assets': sorted(asset_rows, key=lambda x: (-x['click_intent_signal'], -x['attention_signal'], x['asset_id'])),
        'personas': persona_categories,
    }


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
            complete.append(_finalize_asset(ledger, plan, out))
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
               'new_questions': sum(r.get('new_questions', 0) for r in results),
               'reused_questions': sum(r.get('reused_questions', 0) for r in results),
               'recorded_requests': len(registry['requests']),
               'completed_requests': sum(r['status'] == 'completed' for r in registry['requests']),
               'usage': {'reported_input_tokens': sum(token_counts) if token_counts else None,
                         'requests_with_usage': len(token_counts),
                         'mean_completed_request_seconds': sum(seconds) / len(seconds) if seconds else None},
               'usage_note': f"{sum(token_counts):,} token input dichiarati su {len(token_counts)} richieste completate; costo monetario non misurato.".replace(',', '.'),
               'ranking': sorted(complete, key=lambda s: (-s['click_intent_signal'], -s['attention_signal'], s['asset_id']))}
    write(Path(out) / 'summary.json', summary)
    if complete:
        write(Path(out) / 'categorization.json', build_categorization(summary, cards, catalog))
    return summary


def analyze(catalog, cards, out, api, asset_ids=None, model='gemini-decision-1', seed=2026,
            retry_rejected=False, min_interval_s=6.5, batch_size=25, tpm_limit=45000):
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
            if not 1 <= len(people) <= 1000:
                raise ValueError('Numero di personas per settore consentito: 1–1000')
            plan = build_plan(catalog, cards, asset['asset_id'], len(people), seed, model)
            result = run_asset(ledger, plan, out, api, retry_rejected, min_interval_s, batch_size, tpm_limit)
            results.append(result)
            write(out / 'ledger.json', ledger.export())
        return results
    finally:
        write(out / 'ledger.json', ledger.export())
        try:
            refresh_summary(ledger, catalog, cards, out, model, seed, results, request_count_before)
        finally:
            ledger.close()


def analyze_parallel(catalog, cards, out, apis, asset_ids=None, model='gemini-decision-1', seed=2026,
                     retry_rejected=False, min_interval_s=5.2, batch_size=34, tpm_limit=45000,
                     rpm_limit=12, max_tokens_per_request=41000, max_429_retries=4, progress_cb=None):
    """Run Decision 1 across multiple API keys in parallel with per-key sliding-window RPM/TPM pacing."""
    if not apis:
        raise ValueError('Serve almeno una coppia (label, api_client) per analyze_parallel')
    out = Path(out).resolve()
    ledger = Ledger(out / 'ledger.sqlite')
    ledger.recover_saved_responses()

    verticals = {p['vertical'] for p in cards['personas']}
    assets = [a for a in catalog['creatives'] if a['vertical'] in verticals]
    if asset_ids:
        if set(asset_ids) - {a['asset_id'] for a in assets}:
            raise ValueError('Asset richiesto assente o senza personas del settore')
        assets = [a for a in assets if a['asset_id'] in asset_ids]

    plans = {}
    work_q = queue.Queue()
    reused_total = 0
    total_chunks = 0
    for asset in assets:
        aid = asset['asset_id']
        people = [p for p in cards['personas'] if p['vertical'] == asset['vertical']]
        if not 1 <= len(people) <= 1000:
            raise ValueError('Numero di personas per settore consentito: 1–1000')
        plan = build_plan(catalog, cards, aid, len(people), seed, model)
        decision_preflight(plan)
        plans[aid] = plan
        missing = []
        for qid in plan['request']['questions']:
            cached = ledger.get(analysis_key(plan, qid))
            if cached and cached['status'] == 'completed':
                reused_total += 1
            elif cached and not (cached['status'] == 'rejected' and retry_rejected):
                raise ValueError(f"Analisi {cached['status']} da verificare per {cached['asset_id']}/{cached['persona_id']}; nessun reinvio automatico")
            else:
                missing.append(qid)
        chunks = pack_question_chunks(plan, missing, batch_size=batch_size, max_est_tokens=max_tokens_per_request)
        for idx, chunk in enumerate(chunks):
            est = estimate_request_tokens(plan['request']['input'], {q: plan['request']['questions'][q] for q in chunk})
            work_q.put((aid, idx + 1, len(chunks), chunk, est, 0, retry_rejected))
            total_chunks += 1

    request_count_before = len(ledger.export()['requests'])
    stats_lock = threading.Lock()
    stats = {'done_chunks': 0, 'new_questions': 0, 'api_requests': 0, 'reused_questions': reused_total,
             'total_chunks': total_chunks, 'errors': [], 'recent_429': []}
    limiters = {label: KeyRateLimiter(tpm_limit=tpm_limit, rpm_limit=rpm_limit, min_interval_s=min_interval_s)
                for label, _ in apis}
    if min_interval_s and total_chunks > 0:
        recent_rows = ledger.recent_requests(10)
        if recent_rows:
            now_dt = datetime.now(timezone.utc)
            newest_age = min((now_dt - datetime.fromisoformat(r['created_at'])).total_seconds() for r in recent_rows)
            if 0.0 <= newest_age < 62.5:
                startup_wait = 62.5 - newest_age
                for lim in limiters.values():
                    lim.note_429(startup_wait)
    shared_limiter_box = {'limiter': None}
    stop_event = threading.Event()
    started_all = time.monotonic()

    def _get_limiter(label):
        with stats_lock:
            return shared_limiter_box['limiter'] or limiters[label]

    def worker(label, api_client):
        while not stop_event.is_set():
            try:
                item = work_q.get_nowait()
            except queue.Empty:
                return
            aid, cidx, ctot, chunk, est_tokens, attempt, allow_retry_rejected = item
            plan = plans[aid]
            limiter = _get_limiter(label)
            entry = limiter.acquire(est_tokens)
            if stop_event.is_set():
                work_q.task_done()
                return
            raw_path = out / 'raw' / f'{uuid.uuid4().hex}.json'
            try:
                request_id, fragment = ledger.claim(plan, chunk, raw_path, allow_retry_rejected)
            except Exception as exc:
                with stats_lock:
                    stats['errors'].append(f'{aid}: {exc}')
                stop_event.set()
                work_q.task_done()
                return
            write(out / 'requests' / f'{request_id}.json', fragment)
            started = time.monotonic()
            try:
                raw = decide(fragment, api_client)
            except Exception as exc:
                code = getattr(exc, 'code', None) or getattr(exc, 'status_code', None)
                is_429 = str(code) == '429'
                state = 'rejected' if str(code) in {'400', '401', '403', '404', '429'} else 'ambiguous'
                ledger.fail(request_id, state, exc, time.monotonic() - started)
                if is_429 and attempt < max_429_retries:
                    cooldown = 65.0 * (attempt + 1)
                    limiter.note_429(cooldown)
                    with stats_lock:
                        now_m = time.monotonic()
                        stats['recent_429'].append((now_m, label))
                        recent_labels = {lbl for ts, lbl in stats['recent_429'] if now_m - ts < 90.0}
                        if stats['done_chunks'] >= 4 and len(recent_labels) > 1 and shared_limiter_box['limiter'] is None:
                            shared_limiter_box['limiter'] = KeyRateLimiter(
                                tpm_limit=tpm_limit, rpm_limit=rpm_limit, min_interval_s=min_interval_s
                            )
                            shared_limiter_box['limiter'].note_429(cooldown)
                    work_q.put((aid, cidx, ctot, chunk, est_tokens, attempt + 1, True))
                    if progress_cb:
                        progress_cb(f'[{label}] {aid} chunk {cidx}/{ctot}: HTTP 429 -> cooldown {int(cooldown)}s e retry #{attempt + 1}')
                    work_q.task_done()
                    continue
                with stats_lock:
                    stats['errors'].append(f'[{label}] {aid} Decision {state}: {type(exc).__name__} code={code}')
                stop_event.set()
                work_q.task_done()
                return

            write(raw_path, raw)
            try:
                ledger.finish(request_id, fragment, raw, time.monotonic() - started)
            except (ValueError, KeyError) as exc:
                ledger.fail(request_id, 'invalid_response', exc, time.monotonic() - started)
                with stats_lock:
                    stats['errors'].append(f'[{label}] {aid} invalid_response')
                stop_event.set()
                work_q.task_done()
                return

            actual_tok = raw.get('response', {}).get('usage', {}).get('total_input_tokens')
            limiter.reconcile(entry, actual_tok)
            with stats_lock:
                stats['done_chunks'] += 1
                stats['new_questions'] += len(chunk)
                stats['api_requests'] += 1
                done = stats['done_chunks']
                elapsed_all = time.monotonic() - started_all
                eta_s = (elapsed_all / done) * (total_chunks - done) if done else 0
                if progress_cb:
                    progress_cb(
                        f'[{label}] {aid} chunk {cidx}/{ctot} ({len(chunk)}q, est={est_tokens}, real={actual_tok}) '
                        f'| {done}/{total_chunks} | ETA {int(eta_s // 60)}m{int(eta_s % 60):02d}s'
                    )
            work_q.task_done()

    try:
        if total_chunks > 0:
            threads = [threading.Thread(target=worker, args=(lbl, cli), daemon=True) for lbl, cli in apis]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        if stats['errors']:
            raise RuntimeError('; '.join(stats['errors']))
        asset_results = []
        for aid, plan in plans.items():
            signal = _finalize_asset(ledger, plan, out)
            asset_results.append({'asset_id': aid, 'status': 'completed', 'signal': signal})
        return {'assets': asset_results, **stats}
    finally:
        write(out / 'ledger.json', ledger.export())
        try:
            refresh_summary(ledger, catalog, cards, out, model, seed,
                            [{'new_questions': stats['new_questions'], 'reused_questions': stats['reused_questions']}],
                            request_count_before)
        finally:
            ledger.close()

