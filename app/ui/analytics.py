"""Read-only local project evidence dashboard. Run separately from the citizen app."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[2]
st.set_page_config(page_title='Sahayak project evidence',layout='wide')
st.title('Sahayak · Project evidence')
st.caption('Local development dashboard. Curated corpus coverage and measured results; no citizen prompts or profiles.')
folder=ROOT/'data/eval'
summary=folder/'corpus_summary.json'
if summary.exists():
    data=json.loads(summary.read_text(encoding='utf8'))
    cols=st.columns(3)
    for col,key,label in zip(cols,['active_documents','active_chunks','excluded_documents'],['Active documents','Search passages','Excluded legacy documents']):
        col.metric(label,data[key])
    st.info(data['coverage'])
quality=folder/'corpus_quality.csv'
if quality.exists():
    frame=pd.read_csv(quality)
    st.subheader('Corpus quality and provenance')
    st.bar_chart(frame[frame.active].groupby('mode').chunks.sum())
    st.dataframe(frame,hide_index=True)
    st.download_button('Download corpus CSV',quality.read_bytes(),'corpus_quality.csv','text/csv')
for filename,title in [('live_retrieval_results.json','Real retrieval evaluation'),('live_pipeline_results.json','Synthetic end-to-end evaluation')]:
    path=folder/filename
    if path.exists():
        st.subheader(title)
        st.json(json.loads(path.read_text(encoding='utf8')),expanded=False)
metrics=folder/'runtime_metrics.jsonl'
if metrics.exists():
    st.subheader('Local run measurements')
    rows=[json.loads(line) for line in metrics.read_text(encoding='utf8').splitlines() if line.strip()]
    frame=pd.DataFrame(rows)
    st.dataframe(frame.tail(100),hide_index=True)
    st.caption('Synthetic tests and real use may both appear. These rows are operational measurements, not an accuracy score.')
else:
    st.caption('No run measurements yet.')
