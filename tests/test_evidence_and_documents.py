"""Citation integrity, safe report rendering, and local document-reader regressions."""
from io import BytesIO
from PIL import Image
from app.agents.critic import critique
from app.agents.evidence import bind_sources
from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, PlannedScheme
from app.schemas.research import ResearchResult, RetrievedChunk
from app.ui.report import generate_html_report
from app.tools import ocr

QUOTE='Applicants must have passed the senior secondary examination.'
def evidence():
    return ResearchResult(query='education',mode='mentor',chunks=[RetrievedChunk(
        doc_id='official',chunk_id='official__chunk_1',name='Official guidance',text=QUOTE,
        source_url='https://example.org/official.pdf',page=12,rerank_score=3,citation='Official')])
def option(**overrides):
    return PlannedScheme(**{'name':'Education pathway','scheme_id':'official__chunk_1','evidence_quote':QUOTE,**overrides})
def test_source_urls_are_bound_from_retrieval():
    plan=ActionPlan(eligible_schemes=[option(source_url='https://invented.example')])
    bound=bind_sources(plan,evidence())
    assert bound.eligible_schemes[0].source_url=='https://example.org/official.pdf'
    assert bound.eligible_schemes[0].source_page==12

def test_unknown_source_and_invented_quote_fail():
    for item in (option(scheme_id='invented'),option(evidence_quote='Guaranteed admission and a free scholarship for everyone.')):
        verdict=critique(CitizenProfile(mode='mentor'),ActionPlan(eligible_schemes=[item]),evidence())
        assert not verdict.passed and verdict.errors

def test_exact_quote_passes_but_is_not_semantic_proof():
    assert critique(CitizenProfile(mode='mentor'),ActionPlan(eligible_schemes=[option()]),evidence()).passed

def test_report_escapes_untrusted_text_and_rejects_script_url():
    plan=ActionPlan(greeting='<script>alert(1)</script>',eligible_schemes=[option(source_url='javascript:alert(2)')])
    html=generate_html_report(CitizenProfile(mode='mentor'),plan)
    assert '<script>alert(1)</script>' not in html and '&lt;script&gt;' in html
    assert 'href="javascript:' not in html

def test_bad_ocr_input_has_actionable_error():
    assert ocr.extract_text_from_image(b'not an image').startswith('OCR Error:')

def test_ocr_reads_only_confident_lines(monkeypatch):
    monkeypatch.setattr(ocr,'_engine',lambda:lambda image:([[[], 'Clear text', .98],[[], 'noise', .2]],None))
    buffer=BytesIO();Image.new('RGB',(100,100),'white').save(buffer,format='PNG')
    assert ocr.extract_text_from_image(buffer.getvalue())=='Clear text'

def test_reviewed_pathways_are_exact_excerpts_on_the_cited_page():
    import json
    from app.rag.corpus import KB_DIR
    doc=json.loads((KB_DIR/'mentor/cbse_compendium_2026.json').read_text(encoding='utf8'))
    assert len(doc['reviewed_passages'])==6
    for reviewed in doc['reviewed_passages']:
        assert any(reviewed['text'] in text for text,page in zip(doc['chunks'],doc['chunk_pages']) if page==reviewed['page'])

def test_model_list_checks_are_readable_and_schema_fragments_fail():
    item=option(eligibility_note=['Confirm subjects','Check current admissions'])
    assert item.eligibility_note=='Confirm subjects; Check current admissions'
    verdict=critique(CitizenProfile(mode='mentor'),ActionPlan(eligible_schemes=[item],next_steps=['estimated_annual_benefit',':0']),evidence())
    assert not verdict.passed

def test_career_catalogue_cannot_establish_applicant_eligibility():
    plan=ActionPlan(eligible_schemes=[option(eligibility_note='Commerce is mandatory',why_relevant='You are eligible',benefits='Guaranteed admission')])
    bound=bind_sources(plan,evidence(),CitizenProfile(mode='mentor',language='en'))
    item=bound.eligible_schemes[0]
    assert 'Commerce is mandatory' not in item.eligibility_note
    assert 'does not establish your eligibility' in item.eligibility_note
    assert item.benefits=='' and 'You are eligible' not in item.why_relevant
