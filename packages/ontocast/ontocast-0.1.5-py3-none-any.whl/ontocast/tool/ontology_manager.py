"""Ontology management tool for OntoCast.

This module provides functionality for managing multiple ontologies, including
loading, updating, and retrieving ontologies by name or IRI.
"""

import logging

from pydantic import Field

from ontocast.onto import NULL_ONTOLOGY, Ontology, RDFGraph, derive_ontology_id

from .onto import Tool


class OntologyManager(Tool):
    """Manager for handling multiple ontologies.

    This class provides functionality for managing a collection of ontologies,
    including selection and retrieval operations.

    Attributes:
        ontologies: List of managed ontologies.
    """

    ontologies: list[Ontology] = Field(default_factory=list)

    def __init__(self, **kwargs):
        """Initialize the ontology manager.

        Args:
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super().__init__(**kwargs)

    def update_ontology(self, ontology_id: str, ontology_addendum: RDFGraph):
        """Update an existing ontology with additional triples.

        Args:
            ontology_id: The short name of the ontology to update.
            ontology_addendum: The RDF graph containing additional triples to add.
        """
        current_idx = next(
            i for i, o in enumerate(self.ontologies) if o.ontology_id == ontology_id
        )
        self.ontologies[current_idx] += ontology_addendum

    def get_ontology_names(self) -> list[str]:
        """Get a list of all ontology short names.

        Returns:
            list[str]: List of ontology short names.
        """
        return [o.ontology_id for o in self.ontologies]

    def get_ontology(
        self, ontology_id: str = None, ontology_iri: str = None
    ) -> Ontology:
        """Get an ontology by its short name or IRI.

        Args:
            ontology_id: The short name of the ontology to retrieve (optional).
            ontology_iri: The IRI of the ontology to retrieve (optional).

        Returns:
            Ontology: The matching ontology if found, NULL_ONTOLOGY otherwise.
        """
        # Try by id first if provided
        if ontology_id:
            for o in self.ontologies:
                if o.ontology_id == ontology_id:
                    # If IRI is also provided, check consistency
                    if ontology_iri:
                        derived_id = derive_ontology_id(ontology_iri)
                        if ontology_id != derived_id:
                            logger = logging.getLogger(__name__)
                            logger.warning(
                                f"Ontology id '{ontology_id}' does not match id derived from IRI '{ontology_iri}': '{derived_id}'"
                            )
                    return o
        # Try by IRI if provided
        if ontology_iri:
            for o in self.ontologies:
                if o.iri == ontology_iri:
                    return o
        # Not found
        return NULL_ONTOLOGY
