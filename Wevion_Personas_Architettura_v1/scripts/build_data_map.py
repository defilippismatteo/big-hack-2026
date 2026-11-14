"""Convenience audit of the organizer's relational data, separate from persona runtime."""
import csv, json, argparse,collections
from pathlib import Path

def read(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def build(d):
    d=Path(d)
    camps=read(d/'campagne.csv');adsets=read(d/'adset.csv');ads=read(d/'annunci.csv');hist=read(d/'storico_giornaliero.csv');fut=read(d/'da_prevedere.csv')
    ac=[]
    for f in sorted((d/'asset_creativi').glob('*.csv')):ac+=read(f)
    use=collections.defaultdict(set)
    for a in ads:use[a['asset_id']].add(a['adset_id'])
    hi={h['ad_id'] for h in hist};fu={f['ad_id'] for f in fut}
    by=[]
    for c in camps:
        xx=[]
        for s in adsets:
            if s['campaign_id']!=c['campaign_id']:continue
            ad=[a for a in ads if a['adset_id']==s['adset_id']]
            xx.append({'adset_id':s['adset_id'],'ads':[{'ad_id':a['ad_id'],'asset_id':a['asset_id'],'has_history':a['ad_id'] in hi, 'future_active':a['ad_id'] in fu} for a in ad]})
        by.append({'campaign_id':c['campaign_id'],'vertical':c['vertical'],'adsets':xx})
    return {'file_rows':{'campaigns':len(camps),'adsets':len(adsets),'ads':len(ads),'assets':len(ac),'history':len(hist),'forecast_rows':len(fut)},'new_ads_without_history':sorted(fu-hi),'new_assets_without_history':sorted({x['asset_id'] for x in fut}-{x['asset_id'] for x in hist}), 'asset_shared_across_adsets':dict(collections.Counter(map(len,use.values()))),'hierarchy':by}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(build(a.data_dir),indent=2,ensure_ascii=False),encoding='utf-8')
