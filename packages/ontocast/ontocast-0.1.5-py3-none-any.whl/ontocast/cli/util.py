import logging.config
import pathlib
from typing import Optional

from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)


def crawl_directories(
    input_path: pathlib.Path, suffixes=(".pdf", ".json"), prefix=None
) -> list[pathlib.Path]:
    file_paths: list[pathlib.Path] = []

    if not input_path.is_dir():
        print(f"The path {input_path} is not a valid directory.")
        return file_paths

    for file in input_path.rglob("*"):
        if (
            file.is_file()
            and file.suffix in suffixes
            and (file.stem.startswith(prefix) if prefix is not None else True)
        ):
            file_paths.append(file)
    return file_paths


def pdf2markdown(
    file_path: pathlib.Path, converter: Optional[DocumentConverter] = None
):
    if file_path.suffix == ".pdf":
        if converter is None:
            converter = DocumentConverter()
        result = converter.convert(file_path)
        doc = result.document.export_to_markdown()
        return {"text": doc}
    else:
        raise ValueError(f"Unsupported extension {str(file_path.suffix)}")
