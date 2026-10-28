"""Corpus and sparse-retrieval integration; dense/model calls are isolated."""
import sys
from types import SimpleNamespace
from unittest.mock import Mock

from app.agents import research as agent, planning
from app.rag.bm25 import BM25Index
from app.rag.corpus import load_chunks
from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult
from scripts.build_index import collect_chunks


def test_both_indexes_share_modes_and_provenance():
    sparse = load_chunks()
    dense = collect_chunks()
    assert {c['id'] for c in sparse} == {c['id'] for c in dense}
    mentor = [c for c in dense if c['metadata']['mode'] == 'mentor']
    assert mentor
    assert 'nta_neet_2026' in {c['metadata']['doc_id'] for c in mentor}
    assert all('source_url' in c['metadata'] for c in dense)


def test_real_sparse_search_respects_mode_before_top_k():
    index = BM25Index()
    results = index.search('biology doctor NEET', top_k=5, mode='mentor')
    assert results and all(c['mode'] == 'mentor' for c in results)
    assert any(c['doc_id'] == 'nta_neet_2026' for c in results)
    assert all(c['mode'] == 'scheme' for c in index.search('pension', mode='scheme'))


def test_query_uses_followup_profile_without_assuming_class_12():
    profile = CitizenProfile(mode='mentor', raw_input='Finished class 10',
                             interests=['biology'], strengths=['drawing'], career_goal='doctor')
    query = agent._build_query(profile)
    assert all(word in query for word in ('biology', 'drawing', 'doctor', 'class 10'))
    assert '12th' not in query


def setup_retrieval(monkeypatch, score=2):
    vector = Mock(return_value={'ids': [[]], 'documents': [[]], 'metadatas': [[]]})
    monkeypatch.setitem(sys.modules, 'app.rag.embed', SimpleNamespace(embed_text=lambda q: [0.0]))
    monkeypatch.setitem(sys.modules, 'app.rag.vector_store', SimpleNamespace(search=vector))
    monkeypatch.setitem(sys.modules, 'app.rag.rerank', SimpleNamespace(
        rerank=lambda query, candidates, **kw: [{**c, '_rerank_score': score} for c in candidates]))
    web = Mock(side_effect=AssertionError('Mentor must not use unverified web snippets'))
    monkeypatch.setitem(sys.modules, 'app.tools.web_search', SimpleNamespace(search=web))
    return vector, web


def test_mentor_research_works_with_stale_dense_index(monkeypatch):
    vector, web = setup_retrieval(monkeypatch)
    result = agent.research(CitizenProfile(mode='mentor', state='kerala',
        raw_input='I finished 12th, I am confused.', interests=['biology'], career_goal='doctor NEET'))
    assert result.chunks
    assert any(c.doc_id == 'nta_neet_2026' for c in result.chunks)
    assert any(len(c.text) > 500 for c in result.chunks)
    assert vector.call_args.kwargs['mode'] == 'mentor'
    assert vector.call_args.kwargs['state'] is None
    web.assert_not_called()
    assert all(c.source_url.startswith('https://') and c.page > 0 for c in result.chunks)


def test_irrelevant_mentor_results_stay_empty(monkeypatch):
    setup_retrieval(monkeypatch, score=-10)
    result = agent.research(CitizenProfile(mode='mentor', raw_input='biology'))
    assert result.chunks == []
    plan = planning.plan(CitizenProfile(mode='mentor'), result)
    assert 'panchayat' not in ' '.join(plan.next_steps).lower()
    assert not plan.eligible_schemes


def test_empty_mentor_message_is_localized():
    research = ResearchResult(query='career', mode='mentor')
    for language in ('en', 'ml', 'hi', 'ta'):
        result = planning.plan(CitizenProfile(mode='mentor', language=language), research)
        assert result.next_steps and 'panchayat' not in result.next_steps[0].lower()


def test_vector_filters_are_applied_before_ranking(monkeypatch):
    import importlib
    monkeypatch.setitem(sys.modules, 'chromadb', SimpleNamespace())
    module = importlib.import_module('app.rag.vector_store')
    collection = Mock()
    collection.count.return_value = 100
    monkeypatch.setattr(module, 'get_or_create_collection', lambda: collection)
    module.search([0.0], mode='mentor')
    assert collection.query.call_args.kwargs['where'] == {'mode': 'mentor'}
    module.search([0.0], mode='scheme', state='Kerala')
    assert collection.query.call_args.kwargs['where'] == {'$and': [
        {'mode': 'scheme'}, {'state': {'$in': ['kerala', 'central']}}]}

def test_entrance_bulletins_respect_explicit_career_intent():
    assert not agent._source_matches_intent('nta_neet_2026','Engineering after class 12 physics mathematics')
    assert not agent._source_matches_intent('nta_jee_2026','How to become a doctor through MBBS?')
    assert agent._source_matches_intent('nta_neet_2026','Compare engineering and medical careers')
    assert agent._source_matches_intent('nta_jee_2026','Compare engineering and medical careers')
    assert agent._source_matches_intent('nta_neet_2026','What can I study after school?')
