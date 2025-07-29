import pathlib
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from ontocast.onto import Ontology, OntologyProperties, RDFGraph
from ontocast.tool import (
    ChunkerTool,
    ConverterTool,
    FilesystemTripleStoreManager,
    FusekiTripleStoreManager,
    Neo4jTripleStoreManager,
    TripleStoreManager,
)
from ontocast.tool.aggregate import ChunkRDFGraphAggregator
from ontocast.tool.llm import LLMTool
from ontocast.tool.ontology_manager import OntologyManager


def update_ontology_properties(o: Ontology, llm_tool: LLMTool):
    """Update ontology properties using LLM analysis, only if missing.

    This function uses the LLM tool to analyze and update the properties
    of a given ontology based on its graph content, but only if any key
    property is missing or empty.
    """
    # Only update if any key property is missing or empty
    if not (o.title and o.ontology_id and o.description and o.version):
        props = render_ontology_summary(o.graph, llm_tool)
        o.set_properties(**props.model_dump())


def update_ontology_manager(om: OntologyManager, llm_tool: LLMTool):
    """Update properties for all ontologies in the manager.

    This function iterates through all ontologies in the manager and updates
    their properties using the LLM tool.

    Args:
        om: The ontology manager containing ontologies to update.
        llm_tool: The LLM tool instance for analysis.
    """
    for o in om.ontologies:
        update_ontology_properties(o, llm_tool)


class ToolBox:
    """A container class for all tools used in the ontology processing workflow.

    This class initializes and manages various tools needed for document processing,
    ontology management, and LLM interactions.

    Args:
        working_directory: Path to the working directory.
        ontology_directory: Optional path to ontology directory.
        model_name: Name of the LLM model to use.
        llm_base_url: Optional base URL for LLM API.
        temperature: Temperature setting for LLM.
        llm_provider: Provider for LLM service (default: "openai").
        neo4j_uri: (optional) URI for Neo4j connection. If provided with neo4j_auth,
                    neo4j will be used as triple store (unless Fuseki is also provided).
        neo4j_auth: (optional) Auth string (user/password) for Neo4j connection.
        fuseki_uri: (optional) URI for Fuseki connection. If provided with fuseki_auth,
                    Fuseki will be used as triple store (preferred over Neo4j).
        fuseki_auth: (optional) Auth string (user/password) for Fuseki connection.
        clean: (optional, default False) If True, triple store (Neo4j or Fuseki) will be initialized as clean (all data deleted on startup).
    """

    def __init__(self, **kwargs):
        working_directory: pathlib.Path = kwargs.pop("working_directory")
        ontology_directory: Optional[pathlib.Path] = kwargs.pop("ontology_directory")
        model_name: str = kwargs.pop("model_name")
        llm_base_url: Optional[str] = kwargs.pop("llm_base_url")
        temperature: float = kwargs.pop("temperature")
        llm_provider: str = kwargs.pop("llm_provider", "openai")
        neo4j_uri: Optional[str] = kwargs.pop("neo4j_uri", None)
        neo4j_auth: Optional[str] = kwargs.pop("neo4j_auth", None)
        fuseki_uri: Optional[str] = kwargs.pop("fuseki_uri", None)
        fuseki_auth: Optional[str] = kwargs.pop("fuseki_auth", None)
        clean: bool = kwargs.pop("clean", False)

        self.llm: LLMTool = LLMTool.create(
            provider=llm_provider,
            model=model_name,
            temperature=temperature,
            base_url=llm_base_url,
        )

        # Filesystem manager for initial ontology loading (if ontology_directory provided)
        self.filesystem_manager: Optional[FilesystemTripleStoreManager] = None
        if ontology_directory:
            self.filesystem_manager = FilesystemTripleStoreManager(
                working_directory=working_directory,
                ontology_path=ontology_directory,
            )

        # Main triple store manager - prefer Fuseki over Neo4j, fallback to filesystem
        if fuseki_uri and fuseki_auth:
            # Extract dataset name from URI if not provided
            dataset = None
            if "/" in fuseki_uri:
                dataset = fuseki_uri.split("/")[-1]
            self.triple_store_manager: TripleStoreManager = FusekiTripleStoreManager(
                uri=fuseki_uri, auth=fuseki_auth, dataset=dataset, clean=clean
            )
        elif neo4j_uri and neo4j_auth:
            self.triple_store_manager: TripleStoreManager = Neo4jTripleStoreManager(
                uri=neo4j_uri, auth=neo4j_auth, clean=clean
            )
        else:
            self.triple_store_manager: TripleStoreManager = (
                FilesystemTripleStoreManager(
                    working_directory=working_directory,
                    ontology_path=ontology_directory,
                )
            )
        self.ontology_manager: OntologyManager = OntologyManager()
        self.converter: ConverterTool = ConverterTool()
        self.chunker: ChunkerTool = ChunkerTool()
        self.aggregator: ChunkRDFGraphAggregator = ChunkRDFGraphAggregator()


def init_toolbox(toolbox: ToolBox):
    """Initialize the toolbox with ontologies and their properties.

    This function fetches ontologies from the triple store and updates
    their properties using the LLM tool. If a filesystem manager is available
    for initial loading, it will be used to load ontologies from files first.

    Args:
        toolbox: The ToolBox instance to initialize.
    """
    # If we have a filesystem manager, use it to load initial ontologies
    if toolbox.filesystem_manager:
        initial_ontologies = toolbox.filesystem_manager.fetch_ontologies()
        # Store these ontologies in the main triple store manager
        for ontology in initial_ontologies:
            toolbox.triple_store_manager.serialize_ontology(ontology)

    # Now fetch ontologies from the main triple store manager
    toolbox.ontology_manager.ontologies = (
        toolbox.triple_store_manager.fetch_ontologies()
    )
    update_ontology_manager(om=toolbox.ontology_manager, llm_tool=toolbox.llm)


def render_ontology_summary(graph: RDFGraph, llm_tool) -> OntologyProperties:
    """Generate a summary of ontology properties using LLM analysis.

    This function uses the LLM tool to analyze an RDF graph and generate
    a structured summary of its properties.

    Args:
        graph: The RDF graph to analyze.
        llm_tool: The LLM tool instance for analysis.

    Returns:
        OntologyProperties: A structured summary of the ontology properties.
    """
    ontology_str = graph.serialize(format="turtle")

    # Define the output parser
    parser = PydanticOutputParser(pydantic_object=OntologyProperties)

    # Create the prompt template with format instructions
    prompt = PromptTemplate(
        template=(
            "Below is an ontology in Turtle format:\n\n"
            "```ttl\n{ontology_str}\n```\n\n"
            "{format_instructions}"
        ),
        input_variables=["ontology_str"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    response = llm_tool(prompt.format_prompt(ontology_str=ontology_str))

    return parser.parse(response.content)
