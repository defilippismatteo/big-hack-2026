"""Deterministic stratified persona slots; no performance data or LLM calls."""
import json, argparse, hashlib, random
from pathlib import Path
AGE_BANDS=['18-24','25-34','35-44','45-54','55-64','65+']
GEN=[('donna',0.45),('uomo',0.45),('non_binary_or_undeclared',0.10)]
MOTIVATIONS=['curiosita','convenienza','qualita','abitudine','sostenibilita','fiducia','indifferenza','praticita']
MEDIA=['instagram','facebook','social_misto','uso_social_limitato']
RISKS=['prudente','moderato','esplorativo']

def distribute(n,labels,weights=None):
    if weights is None: weights=[1/len(labels)]*len(labels)
    exact=[n*w for w in weights]
    counts=[int(x) for x in exact]
    for i in sorted(range(len(labels)),key=lambda i:(-(exact[i]-counts[i]),i))[:n-sum(counts)]:counts[i]+=1
    return [s for s,n in zip(labels,counts) for _ in range(n)]

def generate(context,n=24,seed=2026):
    assert n>=len(AGE_BANDS)
    result=[]
    for v in context['verticals']:
        key=v['vertical'];rv=random.Random(int.from_bytes(hashlib.sha256((str(seed)+key).encode()).digest()[:8],'big'))
        ages=distribute(n,AGE_BANDS);genders=distribute(n,[g for g,w in GEN],[w for g,w in GEN]);motives=distribute(n,MOTIVATIONS);media=distribute(n,MEDIA);risks=distribute(n,RISKS)
        for x in (ages,genders,motives,media,risks): rv.shuffle(x)
        for i in range(n):
            result.append({'persona_id':f'{key}-P{i+1:03d}','vertical':key,'country':'IT','age_band':ages[i], 'gender_identity':genders[i], 'motivation':motives[i], 'social_habit':media[i], 'risk_attitude':risks[i], 'interest_in_category': ['low','medium','high'][i%3], 'sampling_weight':1.0/n, 'seed':seed})
    return {'schema_version':'1.0','source':'manual balanced design; NOT observed adset demographics','slots':result}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--context',required=True);p.add_argument('--n-per-vertical',type=int,default=24);p.add_argument('--seed',type=int,default=2026);p.add_argument('--out',required=True);a=p.parse_args()
    result=generate(json.loads(Path(a.context).read_text(encoding='utf-8')),a.n_per_vertical,a.seed)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
