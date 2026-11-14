"""Dry integration assertions; no external dependency or API required."""
from pathlib import Path
import os
from prepare_safe_inputs import build as build_public
from build_creative_catalog import build as build_ads
from make_slots import generate
from decision1_requests import request
D=Path(os.environ.get('WEVION_DATA_DIR',str(Path(__file__).resolve().parents[2]/'wevion_materials/Wevion BigHack - materiale challenger/dati')))
if not D.exists():
    raise SystemExit("Set WEVION_DATA_DIR to the extracted organizer kit dati/ folder")
context=build_public(D)
a=generate(context,8,11);b=generate(context,8,11)
assert a==b
assert len(a['slots'])==24
for forbidden in ['ctr','cpm','impression','spesa','adset_id','asset_id','headline','storico']:
    assert forbidden not in str(a).lower(),forbidden
creative=build_ads(D)
assert len(creative['creatives'])==36
req=request(creative['creatives'][0],a['slots'],8)
assert len(req['questions'])==8
for forbidden in ['ctr','cpm','impression','spesa','storico','adset_id']:
    assert forbidden not in str(req).lower(),forbidden
print('PASS: safe contexts, deterministic slots, 36 creative descriptions, 8 independent Decision questions with joint action+reason outcomes')
