"""Export corpus quality measures for inspection or Power BI; no citizen data."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.rag.corpus import KB_DIR, load_chunks

OUT = KB_DIR.parent / 'eval'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks()
    rows = []
    for path in sorted(KB_DIR.glob('*/*.json')):
        doc = json.loads(path.read_text(encoding='utf8'))
        meta = doc.get('metadata', {})
        texts = list(doc.get('chunks', [])) + [r['text'] for r in doc.get('reviewed_passages', [])]
        rows.append({'document': doc['doc_id'], 'mode': 'mentor' if path.parent.name == 'mentor' else 'scheme',
            'active': meta.get('active') is not False, 'chunks': len(texts),
            'characters': sum(map(len,texts)), 'duplicate_chunks': len(texts)-len(set(texts)),
            'source_url': meta.get('source_url', ''), 'edition': meta.get('edition',''),
            'retrieved_on': meta.get('retrieved_on',''), 'sha256': meta.get('sha256',''),
            'exclusion_reason': meta.get('exclusion_reason','')})
    with (OUT/'corpus_quality.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    summary={'active_documents':len({c['doc_id'] for c in chunks}), 'active_chunks':len(chunks),
             'chunks_by_mode':dict(Counter(c['mode'] for c in chunks)),
             'chunks_missing_url':sum(not c['source_url'] for c in chunks),
             'chunks_with_page':sum(c['page']>0 for c in chunks),
             'excluded_documents':sum(not r['active'] for r in rows),
             'coverage':'Curated central and Kerala schemes; selected education and career references. Not exhaustive.'}
    (OUT/'corpus_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
