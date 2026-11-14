"""Prepare factual Gemini Decisions API payloads. This script DOES NOT call the API.
One creative per request, one JOINT action+reason choice question per persona.
Requires persona cards separately authored by a text LLM from outcome-blind slots.
"""
import json,argparse
from pathlib import Path

# Mutually exclusive action+reason classes avoid inconsistent independent answers.
OUTCOMES={
 'scroll__irrelevant':'Ignora la pubblicità perché categoria o proposta non sono pertinenti.',
 'scroll__busy':'Scorre subito perché è distratta o non ha tempo.',
 'scroll__skeptical':'Evita la pubblicità perché diffida dei messaggi promozionali.',
 'glance__visual':'Guarda un istante, attirata dalla presentazione, poi prosegue.',
 'glance__weak_offer':'Guarda un istante ma non trova convincente la proposta.',
 'glance__low_need':'Guarda ma non ha un bisogno concreto della categoria.',
 'stop__curiosity':'Si ferma per curiosità, ma non apre il link.',
 'stop__trust_check':'Si ferma per capire affidabilità o condizioni, senza aprire.',
 'stop__interested':'Si ferma perché interessata al tema, ma non abbastanza da aprire.',
 'click__utility':'Apre il link per utilità percepita o interesse pratico.',
 'click__offer':'Apre il link perché attratta da offerta, urgenza o disponibilità.',
 'click__more_info':'Apre il link per approfondire prima di decidere.',
}

def request(asset,people,max_personas=24):
    people=[p for p in people if p['vertical']==asset['vertical']][:max_personas]
    if not people:raise ValueError('No personas matched vertical')
    text=f"Annuncio sponsorizzato Meta, obiettivo commerciale vendite. Settore: {asset['vertical']}. Formato: {asset['formato']}. Titolo: {asset['headline']}. Testo: {asset['testo_principale']}. CTA: {asset['call_to_action']}. Descrizione visual fornita dagli organizzatori (non è un'immagine originale): {asset['descrizione_visual']}"
    questions={}
    for p in people:
        name=p['persona_id']
        # Only persona-safe fields. No adset identifiers or historic outcomes.
        profile={k:p.get(k) for k in ['age_band','gender_identity','motivation','social_habit','risk_attitude','interest_in_category','occupation','economic_context','daily_routine','decision_habits','decision_routine','trust_requirements','ad_avoidance','what_persuades_them','concerns','contradiction','persona_summary'] if k in p}
        stem=f"Profilo fittizio e indipendente {json.dumps(profile,ensure_ascii=False)}. Considera la situazione di una normale esposizione nel feed. Non usare informazioni sulle risposte di altri utenti."
        questions[f'{name}__outcome']={'type':'choice','instructions':stem+' Quale combinazione di azione e motivazione è più plausibile? Scegli una sola possibilità.', 'criteria':OUTCOMES}
    return {'model':'gemini-decision-1','input':[{'type':'text','text':text}],'questions':questions}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--creatives',required=True);a.add_argument('--personas',required=True);a.add_argument('--asset-id',required=True);a.add_argument('--out',required=True);args=a.parse_args()
    creatives=json.loads(Path(args.creatives).read_text(encoding='utf-8'))['creatives']
    asset=next((a for a in creatives if a['asset_id']==args.asset_id),None)
    if asset is None:raise SystemExit(f'Unknown asset_id {args.asset_id}')
    raw=json.loads(Path(args.personas).read_text(encoding='utf-8'))
    persons=raw.get('personas') or raw.get('slots')
    obj=request(asset,persons)
    assert len(obj['questions'])<=1000
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
