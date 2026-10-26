"""Synthetic end-to-end smoke tests. Calls Groq; never uses real citizen records."""
import os,sys,json,time,argparse
from datetime import datetime,timezone
from pathlib import Path
os.environ['LANGSMITH_TRACING']='false';os.environ['LANGCHAIN_TRACING_V2']='false'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.workflows.graph import run_pipeline
from app.ui.report import generate_html_report
ROOT=Path(__file__).resolve().parents[1]
CASES=[
 ('mentor_en','mentor','I finished 12th, I am confused.',{'Which subjects did you study and enjoy?':'Biology, chemistry and physics. I enjoy biology.','What career interests you?':'I want to become a doctor. Please proceed with this information.'},'en'),
 ('mentor_hi','mentor','मैंने बारहवीं में वाणिज्य पढ़ा है। मुझे लेखांकन और व्यापार पसंद हैं। आगे कौन से कोर्स कर सकता हूँ? उपलब्ध जानकारी से मार्गदर्शन दें।',{},'hi'),
 ('mentor_ta','mentor','நான் பன்னிரண்டாம் வகுப்பு முடித்துள்ளேன். கணிதம் மற்றும் இயற்பியல் பிடிக்கும். பொறியியல் படிக்க விரும்புகிறேன். இந்த தகவல்களைக் கொண்டு வழிகாட்டுங்கள்.',{},'ta'),
 ('scheme_ml','scheme','എന്റെ അമ്മൂമ്മയ്ക്ക് 68 വയസ്സാണ്. ഭർത്താവ് മരിച്ചു. കേരളത്തിലാണ് താമസം. വരുമാനം ഇല്ല. വിധവ പെൻഷനുള്ള യോഗ്യത അറിയണം. ഈ വിവരങ്ങൾ ഉപയോഗിച്ച് സഹായിക്കൂ.',{},'ml'),
]
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--retry-failed',action='store_true')
 parser.add_argument('--delay',type=float,default=60)
 args=parser.parse_args()
 output=ROOT/'data/eval/live_pipeline_results.json'
 history=ROOT/'data/eval/live_pipeline_attempts.jsonl'
 previous=json.loads(output.read_text(encoding='utf8')).get('results',[]) if output.exists() else []
 rows=previous if args.retry_failed else []
 if previous and not history.exists():
  with history.open('a',encoding='utf8') as handle:
   for old in previous: handle.write(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),'imported_previous_attempt':True,**old},ensure_ascii=False)+'\n')
 completed={row['id'] for row in rows if row.get('passed')}
 cases=[case for case in CASES if not args.retry_failed or case[0] not in completed]
 for number,(ident,mode,query,answers,language) in enumerate(cases):
  if number: time.sleep(max(0,args.delay))
  sample=ROOT/"data/eval"/f"{ident}_sample.html"
  if sample.exists(): sample.unlink()
  start=time.perf_counter()
  try:
   result=run_pipeline(query,mode,answers)
   profile=result.get('profile'); plan=result.get('plan'); verdict=result.get('verdict'); research=result.get('research')
   row={'id':ident,'seconds':round(time.perf_counter()-start,2),'language':profile.language,
        'followup':result.get('needs_followup'),'questions':result.get('followup_questions'),
        'retrieval_query':profile.retrieval_query,'research':research.model_dump() if research else None,
        'plan':plan.model_dump() if plan else None,'verdict':verdict.model_dump() if verdict else None,
        'passed':bool(profile.language==language and verdict and verdict.passed and plan and plan.eligible_schemes)}
   if row['passed']:
    (ROOT/'data/eval'/f'{ident}_sample.html').write_text(generate_html_report(profile,plan),encoding='utf8')
  except Exception as exc:
   row={'id':ident,'passed':False,'error_type':type(exc).__name__,'error_reason':'provider_rate_limit' if str(exc).startswith('The language service is busy') else 'pipeline_error','seconds':round(time.perf_counter()-start,2)}
  with history.open('a',encoding='utf8') as handle:
   handle.write(json.dumps({'recorded_at':datetime.now(timezone.utc).isoformat(),**row},ensure_ascii=False)+'\n')
  rows=[old for old in rows if old['id']!=ident]
  rows.append(row)
  (ROOT/'data/eval/live_pipeline_results.json').write_text(json.dumps({'description':'Four synthetic end-to-end smoke tests; passing validates flow and citation presence, not every factual claim or native-language quality.','results':rows},ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps({k:v for k,v in row.items() if k not in ('plan','research')},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
