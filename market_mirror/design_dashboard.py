"""Build an offline presentation dashboard from existing artifacts only.

Run: python -m market_mirror.design_dashboard
No inference, API calls or changes to delivery artifacts.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .unified_dashboard import build_unified_payload

ROOT = Path(__file__).resolve().parents[1]


def build_dashboard(root=ROOT):
    root = Path(root)
    v4 = root / 'artifacts/wevion_v4'
    catalog = root / 'artifacts/market_mirror/decision_inputs/creative_catalog.json'
    sources = []

    def load(path):
        path = root / path
        if not path.exists():
            return None
        raw = path.read_bytes()
        sources.append({'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(raw).hexdigest()})
        if path.suffix == '.json':
            return json.loads(raw)
        if path.suffix == '.csv':
            return list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
        return raw.decode('utf-8')

    runs = {}
    for label, folder in [('Pool 600', 'personas_t3_600'), ('Pilota skincare', 'personas_t3')]:
        base = root / 'artifacts' / folder
        if (base / 'analyses/summary.json').exists():
            runs[label] = build_unified_payload(v4, base / 'persona_cards.json', catalog,
                                               base / 'analyses', base / 'interviews', base / 'interviews/REPORT.md')
            for name in ['persona_cards.json', 'analyses/summary.json', 'analyses/categorization.json',
                         'interviews/frozen.json', 'interviews/interview_summary.json']:
                load(f'artifacts/{folder}/{name}')
    payload = {
        'runs': runs,
        'manifest': load('artifacts/wevion_v4/manifest.json'),
        'forecasts': load('artifacts/wevion_v4/forecasts_2026-11-16_30.csv'),
        'audiences': load('artifacts/wevion_v4/persona_adset.json'),
        'decisions': load('artifacts/wevion_v4/decisions.json'),
        'scenarios': load('artifacts/wevion_v4/seasonal_scenarios.csv'),
        'quality': load('artifacts/wevion_v4/data_quality.json'),
        'validation': load('artifacts/wevion_v4/validation_metrics.json'),
        'catalog': load(str(catalog.relative_to(root))),
        'comparison': load('artifacts/timestral_reproduction/results/method_comparison.csv'),
        'intervals': load('artifacts/timestral_reproduction/results/interval_diagnostics.csv'),
        'reports': [{'title': p.stem.replace('_', ' '), 'text': load(str(p.relative_to(root)))}
                    for p in sorted((root / 'docs/report').glob('*.md'))],
        'built_at': datetime.now(timezone.utc).isoformat(),
        'sources': sources,
    }
    template = (Path(__file__).parent / 'templates/dashboard_design.html').read_text()
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    return template.replace('__PAYLOAD__', data)


if __name__ == '__main__':
    output = ROOT / 'dashboard_design.html'
    output.write_text(build_dashboard(), encoding='utf-8')
    print(output)
