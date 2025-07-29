"""Document conversion agent for OntoCast.

This module provides functionality for converting various document formats into
structured data that can be processed by the OntoCast system.
"""

import json
import logging
import pathlib

from ontocast.onto import AgentState, Status
from ontocast.toolbox import ToolBox

logger = logging.getLogger(__name__)


def convert_document(state: AgentState, tools: ToolBox) -> AgentState:
    """Convert a document into structured data.

    This function takes a document and converts it into a structured format that
    can be processed by the OntoCast system.

    Args:
        state: The current agent state containing the document to convert.
        tools: The toolbox instance providing utility functions.

    Returns:
        AgentState: Updated state with converted document data.
    """
    logger.debug("Converting documents. NB: processing only one file")

    state.status = Status.SUCCESS
    files = state.files
    for filename, file_content in files.items():
        file_extension = pathlib.Path(filename).suffix.lower()

        # if file_content is None:
        #     try:
        #         with open(filename, "rb") as f:
        #             file_content = f.read()
        #         if file_extension == ".json":
        #             file_content = json.loads(file_content)
        #     except Exception as e:
        #         logger.error(f"Failed to load file {filename}: {str(e)}")
        #         state.status = Status.FAILED
        #         return state
        logger.debug(f"file ext: {file_extension}, {filename}")
        if file_extension in tools.converter.supported_extensions:
            logger.debug("will apply convert :")
            result = tools.converter(file_content)
        elif file_extension == ".json":
            result = json.loads(file_content.decode("utf-8"))
        elif file_extension == ".txt":
            result = {"text": json.loads(file_content.decode("utf-8"))}
        else:
            state.status = Status.FAILED
            return state

        state.set_text(result["text"])
    return state
