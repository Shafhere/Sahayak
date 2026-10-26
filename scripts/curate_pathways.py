"""Reviewed extractive course passages; every excerpt must exist on its cited page."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# These are retrieval headings, not admission eligibility or independent sources.
SELECTIONS=[
 (124,'Engineering education pathways after class 12','Education Pathway After 12th Some Colleges','IITs and NITs'),
 (130,'Electronics engineering education pathways after class 12','Education Pathway After 12th Some Colleges','For B.Tech'),
 (45,'Undergraduate commerce, finance and business courses','Undergraduate Some Colleges B.Com','Education Pathway'),
 (147,'Commerce and accounting education pathways','Undergraduate Some Colleges B.Com.','Education Pathway'),
 (200,'Business administration undergraduate pathways after class 12','After 12th Some Colleges Bachelor of Business Administration','Education Pathway'),
 (32,'Computer science and web development undergraduate pathways','Undergraduate Post-Graduate Some Colleges Bachelor of Computer Application','University of Delhi'),
]
def main():
 path=ROOT/'data/knowledge_base/mentor/cbse_compendium_2026.json'
 doc=json.loads(path.read_text(encoding='utf8'))
 reviewed=[]
 for page,title,start,end in SELECTIONS:
  matches=[t for t,p in zip(doc['chunks'],doc['chunk_pages']) if p==page and start in t and end in t[t.index(start):]]
  if not matches: raise ValueError(f'Review excerpt no longer matches page {page}; inspect source before updating.')
  text=matches[0];a=text.index(start);b=text.index(end,a)
  reviewed.append({'name':doc['metadata']['name']+' — '+title,'page':page,'text':text[a:b].strip()})
 doc['reviewed_passages']=reviewed
 path.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
 print(f'Validated {len(reviewed)} extractive pathways against original page passages.')
 path=ROOT/'data/knowledge_base/mentor/nta_neet_2026.json'
 doc=json.loads(path.read_text(encoding='utf8'))
 selectors=[(9,'Medical undergraduate pathway: NEET and MBBS','NEET (UG) has been a qualifying entrance exam',' vi.'),
            (34,'Medical college admission and counselling through NEET','1. ADMISSION PROCEDURE',' A. The following')]
 reviewed=[]
 for page,title,start,end in selectors:
  matches=[t for t,p in zip(doc['chunks'],doc['chunk_pages']) if p==page and start in t and end in t[t.index(start):]]
  if not matches: raise ValueError(f'NEET excerpt on page {page} changed; review it.')
  text=matches[0];a=text.index(start);b=text.index(end,a)
  reviewed.append({'name':doc['metadata']['name']+' — '+title,'page':page,'text':text[a:b].strip()})
 doc['reviewed_passages']=reviewed
 path.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
 print('Validated 2 medical-pathway excerpts.')
if __name__=='__main__':main()
