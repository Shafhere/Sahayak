"""Evaluate the actual research agent using synthetic, explicitly scoped cases."""
import json, os, sys, time
from pathlib import Path
os.environ['LANGSMITH_TRACING']='false'
os.environ['LANGCHAIN_TRACING_V2']='false'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.agents.research import research
from app.schemas.citizen import CitizenProfile
CASES=[
 ('doctor','mentor','What courses and entrance examinations lead to becoming a doctor after class 12 with biology?',None,['nta_neet_2026','cbse_compendium_2026']),
 ('engineering','mentor','How can I study engineering after class 12 with mathematics and physics?',None,['nta_jee_2026','cbse_compendium_2026']),
 ('commerce','mentor','What undergraduate courses and career options are available after class 12 commerce?',None,['cbse_compendium_2026']),
 ('vocational','mentor','What vocational education and skill training pathways are available after class 10?',None,['ncert_counselling','cbse_compendium_2026']),
 ('widow','scheme','What are the eligibility criteria for widow pension in Kerala?','kerala',['sevana_widow_criteria']),
 ('old_age','scheme','What are the eligibility criteria for old age pension in Kerala?','kerala',['sevana_old_age_criteria']),
 ('farmer','scheme','Who is eligible for PM KISAN farmer income support?',None,['pm_kisan_guidelines']),
 ('housing','scheme','What are the eligibility conditions for PMAY Urban 2.0 housing assistance?',None,['pmay_urban_2']),
 ('scholarship','scheme','What post matric scholarships are available for OBC students under PM YASASVI?',None,['pm_yasasvi_guidelines']),
 ('health','scheme','What assistance is available for hospital treatment under KASP in Kerala?','kerala',['kasp_kbf']),
 ('unrelated_movies','mentor','Which movies should I watch this weekend?',None,[]),
 ('unrelated_weather','mentor','Will it rain in London tomorrow?',None,[]),
 ('unrelated','mentor','How do I bake sourdough bread with rye flour?',None,[]),
]
def main():
 rows=[]
 for ident,mode,query,state,expected in CASES:
  start=time.perf_counter()
  result=research(CitizenProfile(mode=mode,raw_input=query,retrieval_query=query,state=state))
  docs=list(dict.fromkeys(c.doc_id for c in result.chunks))
  rank=next((i+1 for i,d in enumerate(docs) if d in expected),None)
  row={'id':ident,'mode':mode,'query':query,'expected_any':expected,'retrieved':docs,'rank':rank,
       'passed':bool(rank) if expected else not docs,'seconds':round(time.perf_counter()-start,2),
       'ablations':{key: bool(set(result.diagnostics.get(key,[])) & set(expected)) for key in ('dense_doc_ids','sparse_doc_ids','fused_doc_ids')} if expected else {},
       'diagnostics':result.diagnostics,'passages':[{'doc_id':c.doc_id,'page':c.page,'score':c.rerank_score,'text':c.text} for c in result.chunks]}
  rows.append(row); print(json.dumps({k:v for k,v in row.items() if k!='passages'}),flush=True)
 path=Path(__file__).resolve().parents[1]/'data/eval/live_retrieval_results.json'
 path.write_text(json.dumps({'description':'Small developer-curated smoke set; document hit rate is not factual-answer accuracy or a held-out benchmark.','passed':sum(r['passed'] for r in rows),'total':len(rows),'results':rows},ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__': main()
