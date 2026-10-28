
"""Offline regressions for planning and multi-turn workflow behavior."""
import json
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from app.agents import planning, understanding
from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, CriticVerdict
from app.schemas.research import ResearchResult, RetrievedChunk
from app.workflows import graph


def fake_client(payload):
    create = Mock(return_value=SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=json.dumps(payload)))]))
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def test_planner_uses_actual_prompt_and_passes_evidence(monkeypatch):
    client = fake_client({"greeting": "Hello", "next_steps": ["Confirm eligibility"]})
    monkeypatch.setattr(planning, "_get_client", lambda: client)
    result = planning.plan(CitizenProfile(), ResearchResult(
        query="pension", mode="scheme", source="rag", num_results=1,
        chunks=[RetrievedChunk(doc_id="pension", name="Pension", text="Evidence text",
                               rerank_score=1, source_url="https://example.org/pension", citation="source")]))
    assert result.next_steps == ["Confirm eligibility"]
    message = client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert "Evidence text" in message and "Source ID: pension" in message
    assert "https://example.org/pension" in message



def test_workflow_does_not_stop_for_followup_flags(monkeypatch):
    """Legacy follow-up flags must not interrupt the single-turn workflow."""
    monkeypatch.setattr(graph, "understand_node", lambda state: {
        "profile": CitizenProfile(mode="mentor"),
        "needs_followup": True,  # Legacy field should not control routing.
        "followup_questions": ["Which state?"],
        "iterations": 0,
    })
    monkeypatch.setattr(
        graph,
        "research_node",
        lambda state: {"research": ResearchResult(
            query="career guidance",
            mode="mentor",
            source="test",
            num_results=0,
            chunks=[],
        )},
    )
    monkeypatch.setattr(
        graph,
        "plan_node",
        lambda state: {"plan": ActionPlan(next_steps=["Compare courses"])},
    )
    monkeypatch.setattr(
        graph,
        "critic_node",
        lambda state: {"verdict": CriticVerdict(passed=True), "iterations": 1},
    )
    monkeypatch.setattr(graph, "_graph", None)

    result = graph.build_graph().invoke({"raw_input": "Help me"})

    assert result["plan"].next_steps == ["Compare courses"]
    assert result["verdict"].passed




@pytest.mark.parametrize(
    "direction",
    [
        {"interests": ["math"]},
        {"strengths": ["writing"]},
        {"career_goal": "doctor"},
    ],
)
def test_mentor_direction_is_extracted_without_followups(monkeypatch, direction):
    """Mentor profile extraction works without conversational follow-ups."""
    client = fake_client({
        "mode": "mentor",
        "needs_followup": True,
        "followup_questions": ["Again?"],
        **direction,
    })
    monkeypatch.setattr(understanding, "_get_client", lambda: client)

    profile = understanding.understand(
        "After school?",
        requested_mode="mentor",
    )

    assert profile.mode == "mentor"

    for field, expected in direction.items():
        assert getattr(profile, field) == expected

    message = client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert "Selected mode (preserve this): mentor" in message
    assert "followup_answers" not in message


def test_mentor_without_direction_returns_profile(monkeypatch):
    """Mentor mode returns a profile even when direction is unknown."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({"mode": "mentor"}),
    )

    profile = understanding.understand("Finished class 12")

    assert profile.mode == "mentor"
    assert profile.interests == []
    assert profile.strengths == []
    assert profile.age is None


def test_legacy_followup_flags_are_ignored(monkeypatch):
    """Legacy follow-up fields in an LLM response do not affect the profile."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({
            "mode": "mentor",
            "user_said_enough": True,
            "needs_followup": True,
            "followup_questions": ["Another question?"],
        }),
    )

    profile = understanding.understand("Just help me")

    assert profile.mode == "mentor"
    assert not hasattr(profile, "needs_followup")
    assert not hasattr(profile, "followup_questions")
    assert not hasattr(profile, "user_said_enough")


def test_known_pension_context_extracts_profile_without_followups(monkeypatch):
    """Known pension context is extracted without follow-up processing."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({
            "mode": "scheme",
            "state": "Kerala",
            "age": 68,
            "life_events": ["spouse_death"],
            "needs_followup": True,
            "followup_questions": ["Occupation?"],
        }),
    )

    profile = understanding.understand(
        "My grandmother is 68, a widow in Kerala.",
        requested_mode="scheme",
    )

    assert profile.mode == "scheme"
    assert profile.age == 68
    assert profile.gender == "female"
    assert profile.state == "Kerala"
    assert profile.life_events == ["spouse_death"]
    assert not hasattr(profile, "needs_followup")
    assert not hasattr(profile, "followup_questions")


def test_age_is_extracted_from_original_message(monkeypatch):
    """Deterministic age extraction uses the original user message."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({"mode": "scheme", "language": "en"}),
    )

    profile = understanding.understand(
        "I am 68 years old and need help finding a government scheme.",
        requested_mode="scheme",
    )

    assert profile.age == 68


def test_state_is_extracted_from_original_message(monkeypatch):
    """Deterministic state extraction uses the original user message."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({"mode": "scheme", "language": "en"}),
    )

    profile = understanding.understand(
        "I live in Kerala and need help finding a government scheme.",
        requested_mode="scheme",
    )

    assert profile.state == "Kerala"




def test_single_turn_pipeline_passes_mode_and_finishes(monkeypatch):
    """The selected mode reaches understanding without follow-up answers."""
    seen = {}

    def understand(state):
        seen.update(state)
        return {"profile": CitizenProfile(mode="mentor"), "iterations": 0}

    monkeypatch.setattr(graph, "understand_node", understand)
    monkeypatch.setattr(
        graph,
        "research_node",
        lambda state: {"research": ResearchResult(
            query="career guidance",
            mode="mentor",
            source="test",
            num_results=0,
            chunks=[],
        )},
    )
    monkeypatch.setattr(
        graph,
        "plan_node",
        lambda state: {"plan": ActionPlan(next_steps=["Compare courses"])},
    )
    monkeypatch.setattr(
        graph,
        "critic_node",
        lambda state: {
            "verdict": CriticVerdict(passed=True),
            "iterations": 1,
        },
    )
    monkeypatch.setattr(graph, "_graph", None)
    monkeypatch.setattr(graph, "record_run", lambda *args, **kwargs: None)

    result = graph.run_pipeline("After school?", "mentor")

    assert seen["requested_mode"] == "mentor"
    assert "followup_answers" not in seen
    assert result["plan"].next_steps == ["Compare courses"]
    assert result["verdict"].passed



def test_failed_critic_stops_at_limit(monkeypatch):
    monkeypatch.setattr(graph, "understand_node", lambda state: {"iterations": 0})
    monkeypatch.setattr(graph, "research_node", lambda state: {})
    monkeypatch.setattr(graph, "plan_node", lambda state: {"plan": ActionPlan()})
    monkeypatch.setattr(graph, "critic_node", lambda state: {
        "verdict": CriticVerdict(passed=False, errors=["Unsupported"]),
        "iterations": state["iterations"] + 1})
    replan = Mock(return_value={})
    monkeypatch.setattr(graph, "replan_node", replan)
    result = graph.build_graph().invoke({"raw_input": "Help"})
    assert result["iterations"] == 3 and not result["verdict"].passed
    assert replan.call_count == 2


def test_known_pension_context_extracts_profile_without_followups(monkeypatch):
    """Known pension context is extracted without follow-up processing."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({
            "mode": "scheme",
            "state": "kerala",
            "age": 68,
            "life_events": ["spouse_death"],
            "needs_followup": True,
            "followup_questions": ["Occupation?"],
        }),
    )

    profile = understanding.understand(
        "My grandmother is 68, a widow in Kerala.",
        requested_mode="scheme",
    )

    assert profile.mode == "scheme"
    assert profile.age == 68
    assert profile.gender == "female"
    assert profile.state.lower() == "kerala"
    assert profile.life_events == ["spouse_death"]
    assert not hasattr(profile, "needs_followup")
    assert not hasattr(profile, "followup_questions")

def test_age_is_extracted_from_original_message(monkeypatch):
    """Age extraction uses the original user message."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({"mode": "scheme", "language": "en"}),
    )

    profile = understanding.understand(
        "I am 68 years old and need help finding a government scheme.",
        requested_mode="scheme",
    )

    assert profile.age == 68

def test_state_is_extracted_from_original_message(monkeypatch):
    """State extraction uses the original user message."""
    monkeypatch.setattr(
        understanding,
        "_get_client",
        lambda: fake_client({"mode": "scheme", "language": "en"}),
    )

    profile = understanding.understand(
        "I live in Kerala and need help finding a government scheme.",
        requested_mode="scheme",
    )

    assert profile.state == "Kerala"


def test_build_query_includes_raw_input_when_retrieval_query_exists():
    from app.agents.research import _build_query

    profile = CitizenProfile(
        mode="scheme",
        retrieval_query="government welfare schemes",
        raw_input="I am a 68-year-old widow living in Kerala.",
    )

    query = _build_query(profile)

    assert "government welfare schemes" in query
    assert "I am a 68-year-old widow living in Kerala." in query


def test_load_chunks_uses_folder_for_missing_state(tmp_path):
    from app.rag.corpus import load_chunks

    documents = {
        "central": ("central_doc", None),
        "kerala": ("kerala_doc", None),
        "general": ("general_doc", None),
        "mentor": ("mentor_doc", None),
    }

    for folder, (doc_id, state) in documents.items():
        folder_path = tmp_path / folder
        folder_path.mkdir()
        doc = {
            "doc_id": doc_id,
            "metadata": {"state": state, "active": True},
            "chunks": [f"Sample text for {doc_id}"],
        }
        (folder_path / f"{doc_id}.json").write_text(
            json.dumps(doc), encoding="utf-8"
        )

    chunks = load_chunks(tmp_path)
    states = {chunk["doc_id"]: chunk["state"] for chunk in chunks}

    assert states["central_doc"] == "central"
    assert states["kerala_doc"] == "kerala"
    assert states["general_doc"] == ""
    assert states["mentor_doc"] == ""


def test_research_prioritizes_local_schemes_and_keeps_central(monkeypatch):
    import importlib
    import sys

    research_module = importlib.import_module("app.agents.research")

    profile = CitizenProfile(
        mode="scheme",
        state="Kerala",
        retrieval_query="widow pension",
        raw_input="I am a widow living in Kerala.",
    )

    candidates = [
        {
            "id": "central__chunk_0",
            "doc_id": "central",
            "name": "Central Widow Pension",
            "text": "Central pension details",
            "state": "central",
            "mode": "scheme",
            "source_url": "https://example.org/central",
            "page": 1,
        },
        {
            "id": "kerala__chunk_0",
            "doc_id": "kerala",
            "name": "Kerala Widow Pension",
            "text": "Kerala pension details",
            "state": "kerala",
            "mode": "scheme",
            "source_url": "https://example.org/kerala",
            "page": 1,
        },
        {
            "id": "other__chunk_0",
            "doc_id": "other",
            "name": "Other State Pension",
            "text": "Other state pension details",
            "state": "Tamil Nadu",
            "mode": "scheme",
            "source_url": "https://example.org/other",
            "page": 1,
        },
    ]

    class FakeBM25:
        def search(self, *args, **kwargs):
            return candidates

    # Mock the RAG modules before research() imports them.
    # This prevents the test from loading real embedding/vector dependencies.
    fake_embed = ModuleType("app.rag.embed")
    fake_embed.embed_text = lambda query: [0.1, 0.2]

    fake_vector = ModuleType("app.rag.vector_store")
    fake_vector.search = lambda *args, **kwargs: {
        "ids": [["central__chunk_0", "kerala__chunk_0", "other__chunk_0"]],
        "documents": [[c["text"] for c in candidates]],
        "metadatas": [[
            {
                "doc_id": c["doc_id"],
                "name": c["name"],
                "state": c["state"],
                "mode": c["mode"],
                "source_url": c["source_url"],
                "page": c["page"],
            }
            for c in candidates
        ]],
    }

    fake_bm25 = ModuleType("app.rag.bm25")
    fake_bm25.get_bm25_index = lambda: FakeBM25()

    fake_rrf = ModuleType("app.rag.rrf")
    fake_rrf.reciprocal_rank_fusion = lambda lists, id_key: candidates

    fake_rerank = ModuleType("app.rag.rerank")
    fake_rerank.rerank = lambda query, items, text_key, top_k: [
        {**c, "_rerank_score": 1.0} for c in items
    ]

    for name, module in [
        ("app.rag.embed", fake_embed),
        ("app.rag.vector_store", fake_vector),
        ("app.rag.bm25", fake_bm25),
        ("app.rag.rrf", fake_rrf),
        ("app.rag.rerank", fake_rerank),
    ]:
        monkeypatch.setitem(sys.modules, name, module)

    result = research_module.research(profile)

    result_ids = [chunk.doc_id for chunk in result.chunks]

    assert "kerala" in result_ids
    assert "central" in result_ids
    assert "other" not in result_ids
    assert result_ids.index("kerala") < result_ids.index("central")
