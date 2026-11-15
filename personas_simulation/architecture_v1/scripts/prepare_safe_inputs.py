"""Build a deliberately outcome-blind product context. Reads only inserzionisti/campagne."""
import csv, json, argparse
from pathlib import Path

def rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))

def build(data_dir):
    d=Path(data_dir)
    brands={r['inserzionista_id']:r for r in rows(d/'inserzionisti.csv')}
    camps=rows(d/'campagne.csv')
    assert len(brands)==3 and len(camps)==3
    allowed=[{'vertical':r['vertical'],'market':'IT', 'industry_description':brands[r['inserzionista_id']]['descrizione'], 'campaign_goal':r['obiettivo']} for r in camps]
    return {'schema_version':'1.0','basis':'advertiser sector descriptions only; no target/performance/adset/creative information','verticals':allowed}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    obj=build(a.data_dir)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
