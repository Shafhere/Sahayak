"""Build Chroma from the active corpus, reusing unchanged compatible embeddings."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.rag.corpus import load_chunks
BATCH_SIZE=32

def collect_chunks():
    return [{'id':c['id'],'text':c['text'],'metadata':{k:v for k,v in c.items() if k not in ('id','text')}} for c in load_chunks()]

def main():
    from app.rag.embed import embed_batch, MODEL_NAME
    from app.rag.vector_store import add_chunks, reset, count, get_or_create_collection
    chunks=collect_chunks()
    if not chunks:
        raise SystemExit('No active chunks. Import sources first; existing index was preserved.')
    collection=get_or_create_collection()
    reusable={}
    if (collection.metadata or {}).get('embedding_model')==MODEL_NAME:
        old=collection.get(include=['documents','embeddings'])
        reusable={ident:(text,vector) for ident,text,vector in zip(old['ids'],old['documents'],old['embeddings'])}
    missing=[]
    for chunk in chunks:
        saved=reusable.get(chunk['id'])
        if saved is not None and saved[0]==chunk['text']:
            chunk['embedding']=list(saved[1])
        else:
            missing.append(chunk)
    print(f"Active passages: {len(chunks)}; new embeddings: {len(missing)}",flush=True)
    if missing:
        for chunk,vector in zip(missing,embed_batch([c['text'] for c in missing])):
            chunk['embedding']=vector
    # Finish all model work before replacing the index. Restart running apps after this command.
    reset()
    for i in range(0,len(chunks),BATCH_SIZE):
        add_chunks(chunks[i:i+BATCH_SIZE])
    get_or_create_collection().modify(metadata={'embedding_model':MODEL_NAME})
    print(f'Index ready: {count()} passages',flush=True)
if __name__=='__main__': main()
