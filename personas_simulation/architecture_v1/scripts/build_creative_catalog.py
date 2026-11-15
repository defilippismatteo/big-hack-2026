"""Build creatives from literal supplied text/visual descriptions only, NEVER historical KPI tables."""
import csv,json,argparse
from pathlib import Path

def build(dir):
    o=[]
    for f in sorted((Path(dir)/'asset_creativi').glob('*.csv')):
        with f.open(encoding='utf-8-sig',newline='') as h:
            for a in csv.DictReader(h):
                o.append({k:a[k] for k in ['asset_id','vertical','leva','formato','durata_video_s','headline','testo_principale','call_to_action','descrizione_visual']})
    assert len(o)==36 and len({x['asset_id'] for x in o})==36
    return {'schema_version':'1.0','notice':'text descriptions only: no actual images supplied','creatives':o}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(build(a.data_dir),indent=2,ensure_ascii=False),encoding='utf-8')
