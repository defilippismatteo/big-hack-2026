"""Wevion BigHack 2026 - temporal backtest for CTR/CPM (no future leakage).
Self-contained validation script. Takes the extracted challenge folder as --data.
Not an official benchmark; no Timestral is run.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

FEATURE_GROUPS=['ad_id','adset_id','asset_id','vertical']
CATS=['ad_id','adset_id','asset_id','vertical','leva','formato','campaign_id']
BASE=['budget_giornaliero_adset','dow','days_from_start','days_to_bf','ad_age','asset_age','market_index_cpm','market_index_ctr','is_weekend','is_black_week','is_black_friday','is_cyber_monday']


def setup(base):
    h=pd.read_csv(base/'storico_giornaliero.csv', parse_dates=['data']).sort_values(['data','ad_id']).reset_index(drop=True)
    f=pd.read_csv(base/'da_prevedere.csv',parse_dates=['data']).sort_values(['data','ad_id']).reset_index(drop=True)
    assets=pd.concat([pd.read_csv(p) for p in sorted((base/'asset_creativi').glob('*.csv'))],ignore_index=True)
    ads=pd.read_csv(base/'annunci.csv')
    market=pd.read_csv(base/'benchmark_mercato_settimanale_2025.csv',parse_dates=['settimana_dal'])
    assets=assets[['asset_id','data_lancio']].rename(columns={'data_lancio':'asset_launch'})
    ads=ads[['ad_id','data_lancio']].rename(columns={'data_lancio':'ad_launch'})
    for df in (h,f):
        df['dow']=df.data.dt.dayofweek
        df['days_from_start']=(df.data-pd.Timestamp('2026-08-17')).dt.days
        df['days_to_bf']=(pd.Timestamp('2026-11-27')-df.data).dt.days
        df['is_weekend']=(df.dow>=5).astype(float)
        df['is_black_week']=((df.data>=pd.Timestamp('2026-11-20')) & (df.data<=pd.Timestamp('2026-11-30'))).astype(float)
        df['is_black_friday']=(df.data==pd.Timestamp('2026-11-27')).astype(float)
        df['is_cyber_monday']=(df.data==pd.Timestamp('2026-11-30')).astype(float)
        df['week_2025']=(df.data-pd.Timedelta(days=364)).dt.to_period('W-SUN').dt.start_time
    for df in (h,f):
        x=df[['ad_id','asset_id']].merge(ads,on='ad_id',how='left').merge(assets,on='asset_id',how='left')
        df['ad_age']=(df.data-pd.to_datetime(x.ad_launch)).dt.days.to_numpy()
        df['asset_age']=(df.data-pd.to_datetime(x.asset_launch)).dt.days.to_numpy()
        m=market[['settimana_dal','vertical','indice_cpm','indice_ctr']].rename(columns={'settimana_dal':'week_2025','indice_cpm':'market_index_cpm','indice_ctr':'market_index_ctr'})
        aligned=df[['week_2025','vertical']].merge(m,on=['week_2025','vertical'],how='left')
        df['market_index_cpm']=aligned.market_index_cpm.to_numpy()
        df['market_index_ctr']=aligned.market_index_ctr.to_numpy()
    return h,f


def rates_from_sum(df):
    return (100*df['click']/df['impression'],1000*df['spesa']/df['impression'])


def group_features(hist, predict):
    """Train features are strictly shifted; predict features frozen at the last history date."""
    train=hist.copy(); hold=predict.copy()
    cols=[]
    for name in FEATURE_GROUPS:
        daily=hist.groupby([name,'data'],as_index=False).agg(click=('click','sum'),impression=('impression','sum'),spesa=('spesa','sum'))
        daily['daily_ctr']=100*daily.click/daily.impression
        daily['daily_cpm']=1000*daily.spesa/daily.impression
        daily=daily.sort_values([name,'data']).reset_index(drop=True)
        for k in ('daily_ctr','daily_cpm'):
            namecol=f'{name}_{k}_l7'
            daily[namecol]=daily.groupby(name)[k].transform(lambda v: v.shift(1).rolling(window=7,min_periods=1).mean())
            cols.append(namecol)
        train=train.merge(daily[[name,'data']+cols[-2:]],on=[name,'data'],how='left',validate='many_to_one')
        # Last 7 observed daily measurements up through the forecast origin, no peek.
        latest=daily.groupby(name,sort=False).tail(7).groupby(name).agg({ 'daily_ctr':'mean','daily_cpm':'mean'}).reset_index()
        latest=latest.rename(columns={'daily_ctr':cols[-2], 'daily_cpm':cols[-1]})
        hold=hold.merge(latest,on=name,how='left',validate='many_to_one')
    for df in (train,hold):
        for col in cols:df[col]=df[col].fillna(-1.0)
    return train,hold,cols


def heuristic(hist, hold):
    p=hold.copy()
    for name in FEATURE_GROUPS:
        x=hist[hist.data>=hist.data.max()-pd.Timedelta(days=13)].groupby(name).agg(click=('click','sum'),impression=('impression','sum'),spesa=('spesa','sum'))
        x['ref_ctr']=100*x.click/x.impression
        x['ref_cpm']=1000*x.spesa/x.impression
        p=p.join(x[['ref_ctr','ref_cpm']].rename(columns={'ref_ctr':f'{name}_ref_ctr','ref_cpm':f'{name}_ref_cpm'}),on=name)
    for target in ('ctr','cpm'):
        cols=[f'{name}_ref_{target}' for name in FEATURE_GROUPS]
        p['pred_'+target]=p[cols].bfill(axis=1).iloc[:,0]
        # Fallback global weighted metric.
        overall=100*hist.click.sum()/hist.impression.sum() if target=='ctr' else 1000*hist.spesa.sum()/hist.impression.sum()
        p['pred_'+target]=p['pred_'+target].fillna(overall)
    return p[['pred_ctr','pred_cpm']]


def summarize(hold,pred):
    yctr=100*hold.click/hold.impression
    ycpm=1000*hold.spesa/hold.impression
    return {
      'n_rows':int(len(hold)),
      'ctr_mae_pp':round(float(np.mean(abs(pred.pred_ctr-yctr))),4),
      'cpm_mae_eur':round(float(np.mean(abs(pred.pred_cpm-ycpm))),4),
      'ctr_wmae_pp':round(float(np.average(abs(pred.pred_ctr-yctr),weights=hold.impression)),4),
      'cpm_wmae_eur':round(float(np.average(abs(pred.pred_cpm-ycpm),weights=hold.impression)),4)
    }


def run_fold(h,start,end):
    train=h[h.data<start].copy(); hold=h[(h.data>=start)&(h.data<=end)].copy()
    Xtr,Xva,lag_cols=group_features(train,hold)
    features=CATS+BASE+lag_cols
    for df in [Xtr,Xva]:
        for k in CATS:df[k]=df[k].astype(str).fillna('missing')
        for k in BASE+lag_cols:df[k]=pd.to_numeric(df[k],errors='coerce').fillna(-1.0)
    heur=heuristic(train,hold)
    out={'train_to':str(train.data.max().date()),'valid_from':start,'valid_to':end,'n_train':len(train),'n_validation':len(hold),'new_ad_ids_in_validation':len(set(hold.ad_id)-set(train.ad_id)),'heuristic':summarize(hold,heur)}
    preds={}
    for name,target in [('ctr','ctr'),('cpm','cpm')]:
        raw=(np.log((Xtr.click+0.5)/(Xtr.impression-Xtr.click+0.5)) if target=='ctr' else np.log(Xtr.cpm))
        model=CatBoostRegressor(iterations=550,depth=5,learning_rate=0.045,l2_leaf_reg=8,loss_function='RMSE',verbose=False,thread_count=4,random_seed=17)
        model.fit(Xtr[features],raw,cat_features=CATS)
        yhat=model.predict(Xva[features])
        preds[name]=100/(1+np.exp(-yhat)) if target=='ctr' else np.exp(yhat)
    cb=pd.DataFrame({'pred_ctr':preds['ctr'],'pred_cpm':preds['cpm']},index=hold.index)
    out['catboost']=summarize(hold,cb)
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=Path('/mnt/data/wevion_materials/Wevion BigHack - materiale challenger/dati'))
    ap.add_argument('--output',type=Path,default=Path('/mnt/data/Wevion_validazione_baseline.json'))
    args=ap.parse_args()
    h,_=setup(args.data)
    folds=[('2026-10-19','2026-11-01'),('2026-11-02','2026-11-15')]
    results={'method':'Chronological holdout per fold, per-adset/ad/asset trailing features frozen at cutoff. CatBoost models for logit CTR and log CPM; naive trailing 14-day hierarchical benchmark. No Timestral fitted.','folds':[run_fold(h,s,e) for s,e in folds]}
    args.output.write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
