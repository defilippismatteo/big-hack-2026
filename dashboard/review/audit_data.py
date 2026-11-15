import csv,json,hashlib,subprocess
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'dashboard/public/data'
d=json.loads((DATA/'overview.json').read_text());p=json.loads((DATA/'pilot-forecast.json').read_text())
def daily(rows,si,ii,ci):
 out=defaultdict(lambda:[0,0,0])
 for r in rows:
  for i,k in enumerate([si,ii,ci]):out[r[0]][i]+=r[k]
 return [{'day':day,'ctr':100*c/i,'cpm':1000*s/i,'spend':s} for day,(s,i,c) in sorted(out.items())]
def compact(series):
 return {k:{'min':min(r[k] for r in series),'max':max(r[k] for r in series),'range':max(r[k] for r in series)-min(r[k] for r in series)} for k in ['ctr','cpm']}
def forecastdaily(which):
 extra={(r[0],r[1]):r[2:] for r in p['rows']};rows=[]
 for r,spend in zip(d['forecast'],d['forecastSpend']):
  day,ad,ctr,cpm=r
  if which=='pilot':cpm=extra[day,ad][0]
  if which=='enriched':ctr,cpm=extra[day,ad][1:]
  imps=1000*spend/cpm;rows.append([day,spend,imps,imps*ctr/100])
 return daily(rows,1,2,3)
series={'overview_base':daily(d['budgetScenario'],4,5,6),'overview_seasonal':daily(d['seasonalScenario']['rows'],2,3,4),'forecast_base':forecastdaily('base'),'forecast_pilot':forecastdaily('pilot'),'forecast_enriched':forecastdaily('enriched')}
# Compare actual exported snapshot with local v4 source artifacts.
forecasts=list(csv.DictReader((ROOT/'data/predictions/v4_delivery/forecasts_2026-11-16_30.csv').open()))
idx={(r['data'],r['ad_id']):r for r in forecasts}
maxdiff={m:max(abs(r[i]-float(idx[r[0],r[1]][key])) for r in d['forecast']) for m,i,key in [('ctr',2,'ctr_predetto_pct'),('cpm',3,'cpm_predetto_eur')]}
byad=defaultdict(list)
for row in d['forecast']:byad[row[1]].append(row)
constants={key:sum(len({r[i] for r in rs})==1 for rs in byad.values()) for key,i in [('ctr',2),('cpm',3)]}
commit=p['commit'];path='Prima_Analisi/Previsioni_Periodo_Vuoto/previsioni_2026-11-16_30.csv'
raw=subprocess.check_output(['git','-C',str(ROOT),'show',f'{commit}:{path}'],text=True)
rawrows=list(csv.DictReader(raw.splitlines()));rawidx={(r['data'],r['ad_id']):r for r in rawrows}
reference_mismatches={key:sum(abs(r[i]-float(rawidx[r[0],r[1]][key]))>1e-6 for r in d['forecast']) for key,i in [('ctr_baseline',2),('cpm_baseline',3)]}
pilot_actualdiff=max(abs(row[2]-float(rawidx[row[0],row[1]]['cpm_scelto_eur'])) for row in p['rows'])
result={'snapshot_matches_current_forecast_max_abs_difference':maxdiff,'rows':len(d['forecast']),'ads':len(byad),'constant_by_ad_count':constants,'summaries':{k:compact(v) for k,v in series.items()},'series':series,'pilot_reference_mismatches_against_current_overview':reference_mismatches,'pilot_cpm_matches_source_max_abs_diff':pilot_actualdiff,'source':d['source'],'pilot_commit':commit}
print(json.dumps({k:v for k,v in result.items() if k!='series'},indent=2))
Path(__file__).with_name('measurements.json').write_text(json.dumps(result,indent=2)+'\n')
