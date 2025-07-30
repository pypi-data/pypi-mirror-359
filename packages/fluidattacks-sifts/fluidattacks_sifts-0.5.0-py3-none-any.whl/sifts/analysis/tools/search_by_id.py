from pathlib import Path
from typing import Any

import aiofiles
from fluidattacks_core.serializers.syntax import (
    InvalidFileType,
    get_language_from_path,
    parse_content_tree_sitter,
)
from opensearchpy.exceptions import NotFoundError
from pydantic import BaseModel, Field
from pydantic_core import ValidationError
from tinydb.table import Document
from tree_sitter import Node

from sifts.analysis.types import FunctionTool, TreeExecutionContext
from sifts.io.db.opensearch_client import setup_opensearch_client


class GetFunctionByIdArgs(BaseModel):
    code_id: int = Field(
        description=(
            "ID of the code you want to retrieve. "
            "Code IDs can be obtained from the list_symbols tool."
        ),
    )

    class Config:  # noqa: D106
        extra = "forbid"  # This is equivalent to additionalProperties: false


async def get_function_by_in_tree(
    working_dir: Path,
    document: Document,
) -> Node | None:
    language = get_language_from_path(str(Path(working_dir, document["path"])))
    try:
        line = document["line"] - 1
    except KeyError as exc:
        msg = f"Function with ID '{document.doc_id}' has no line number."
        raise ValueError(msg) from exc
    if not language:
        msg = f"Language not found for function with ID '{document.doc_id}'."
        raise ValueError(msg)
    async with aiofiles.open((Path(working_dir, document["path"])), "rb") as f:
        content = await f.read()
    try:
        tree = parse_content_tree_sitter(content, language)
    except (OSError, InvalidFileType) as exc:
        msg = f"Error parsing tree for function with ID '{document.doc_id}'."
        raise ValueError(msg) from exc

    # Find the largest node at the specified line
    target_node = None
    node_size = 0

    def traverse_tree(node: Node) -> None:
        nonlocal target_node, node_size

        # Check if node contains the target line
        start_line = node.start_point[0]
        end_line = node.end_point[0]

        # Node must start at exactly the target line (not before)
        # and can span to multiple lines below
        if start_line == line:
            # Calculate node size (number of lines it spans)
            current_size = end_line - start_line

            # If this node is larger than the current best match, update it
            if current_size > node_size or (current_size == node_size and target_node is None):
                target_node = node
                node_size = current_size

        # Recursively process children
        for child in node.children:
            traverse_tree(child)

    # Start traversal from the root node
    traverse_tree(tree.root_node)

    return target_node


async def fetch_symbol_code(ctx: TreeExecutionContext, args: dict[str, Any]) -> str:
    try:
        parsed = GetFunctionByIdArgs.model_validate(args)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    # First, try to fetch the document directly from OpenSearch by its ID
    document: Document | None = None
    client = await setup_opensearch_client(new_index=True)
    try:
        hit = await client.get(
            index=ctx.index_name,
            id=str(parsed.code_id),
        )
        src = hit.get("_source", {})
        # Wrap in TinyDB Document so the rest of the pipeline works unchanged
        document = Document(src, parsed.code_id)
    except NotFoundError:
        # Fallback to TinyDB (should rarely happen, but keeps backward compatibility)
        tiny_db = ctx.tiny_db
        document = tiny_db.get(doc_id=parsed.code_id)

    if document is None:
        return (
            f"Function with ID '{parsed.code_id}' not found. "
            "Please run list_symbols to obtain valid IDs."
        )

    try:
        node = await get_function_by_in_tree(Path(ctx.working_dir), document)
    except ValueError as exc:
        return str(exc)
    if node is None or not node.text:
        return (
            f"Function with ID '{parsed.code_id}' not found in the database. Please use"
            " list_symbols to find valid function IDs."
        )

    code = node.text.decode("utf-8")
    # Return the function code and metadata
    return f"Lines: {node.start_point.row}-{node.end_point.row}\n\nCode:\n{code}"


GET_FUNCTION_BY_ID_TOOL = FunctionTool[str](
    name="fetch_symbol_code",
    description=(
        "Retrieves code and details using its ID from the global search. "
        "Use this after finding a relevant function with list_symbols. "
        "This will add the function to the available methods for analysis."
    ),
    params_json_schema={**GetFunctionByIdArgs.model_json_schema(), "additionalProperties": False},
    on_invoke_tool=fetch_symbol_code,
)
