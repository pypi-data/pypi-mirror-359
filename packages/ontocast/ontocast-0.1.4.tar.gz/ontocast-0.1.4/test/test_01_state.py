import pytest
from rdflib import Literal, URIRef

from ontocast.agent import check_chunks_empty, chunk_text, select_ontology
from ontocast.onto import (
    ONTOLOGY_VOID_ID,
    AgentState,
    Ontology,
)


def test_agent_state_json():
    state = AgentState()
    state.current_ontology = Ontology(short_name="ex")
    state.current_ontology.graph.add(
        (
            URIRef("http://example.com/subject"),
            URIRef("http://example.com/predicate"),
            Literal("object"),
        )
    )

    state_json = state.model_dump_json()

    loaded_state = AgentState.model_validate_json(state_json)

    assert len(loaded_state.current_ontology.graph) > 0


def test_chunks(apple_report: dict, tools, state_chunked_filename):
    state = AgentState()
    state.set_text(apple_report["text"])
    state = chunk_text(state, tools)
    assert len(state.chunks) == 10
    state.chunks = state.chunks[:2]
    state = check_chunks_empty(state)
    assert state.current_chunk is not None
    state.serialize(state_chunked_filename)


@pytest.mark.order(after="test_chunks")
def test_select_ontology_fsec(
    state_chunked: AgentState,
    tools,
    state_onto_selected_filename,
):
    state = state_chunked
    state = select_ontology(state=state, tools=tools)
    assert state.current_ontology.ontology_id == "FSEC"

    state.serialize(state_onto_selected_filename)


def test_select_ontology_null(
    random_report: dict,
    tools,
    state_onto_null_filename,
):
    state = AgentState()
    state.set_text(random_report["text"])
    state = chunk_text(state, tools)
    state = check_chunks_empty(state)
    state = select_ontology(state=state, tools=tools)
    assert state.current_ontology.ontology_id == ONTOLOGY_VOID_ID

    state.serialize(state_onto_null_filename)
