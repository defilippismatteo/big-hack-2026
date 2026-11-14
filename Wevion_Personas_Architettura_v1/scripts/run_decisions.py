"""Optional live call. Run ONLY with separate Gemini API credentials; never conflates subscription quota."""
import json,argparse,os
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--request',required=True);p.add_argument('--out',required=True);p.add_argument('--live',action='store_true');args=p.parse_args()
    data=json.loads(Path(args.request).read_text(encoding='utf-8'))
    print('model:',data['model'],'questions:',len(data['questions']))
    if not args.live:
        print('Dry run: no model call. Add --live after validating credentials and schema.');return
    if not os.getenv('GEMINI_API_KEY') and not os.getenv('GOOGLE_API_KEY'):
        raise SystemExit('Set GEMINI_API_KEY or GOOGLE_API_KEY from Google AI Studio')
    try:from google import genai
    except ImportError as e:raise SystemExit('Install google-genai in a separate environment') from e
    client=genai.Client(http_options={'api_version':'v1beta'})
    resp=client.decisions.create(model=data['model'],input=data['input'],questions=data['questions'])
    # Use SDK object serialization, no invented field names.
    if hasattr(resp,'model_dump'):payload=resp.model_dump(mode='json',exclude_none=True)
    elif hasattr(resp,'to_json'):payload=json.loads(resp.to_json())
    else:raise RuntimeError('Unknown response format. Check the official API docs.')
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved raw Decision 1 response. Check schema before downstream aggregation.')
if __name__=='__main__':main()
