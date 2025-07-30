import logging
from typing import Any

# OpenSearch
from opensearchpy import AsyncOpenSearch
from pydantic import BaseModel, Field, ValidationError
from tinydb import Query, TinyDB
from tinydb.table import Document

from sifts.analysis.tools.fuzzy_matcher import fuzzy_match, get_search_terms
from sifts.analysis.types import FunctionTool, TreeExecutionContext
from sifts.io.db.opensearch_client import setup_opensearch_client

LOGGER = logging.getLogger(__name__)


class SearchFunctionByNameArgs(BaseModel):
    query: str = Field(
        description=(
            "Name of the code element to search for. Avoid dot notation unless referring to"
            " scoped names like 'Class.method'."
        ),
    )


def search_in_tinydb(
    db: TinyDB,
    parsed_args: SearchFunctionByNameArgs,
    exclude_scope_kinds: list[str] | None = None,
    name_threshold: int = 70,
) -> list[Document]:
    # Extract search terms
    search_name = parsed_args.query
    search_terms = get_search_terms(search_name)

    # Configure query object
    tag_accesor = Query()

    # Build query for the name using all search terms (OR logic)
    query_parts = [
        tag_accesor.name.test(
            lambda x, term=search_term: fuzzy_match(x, term, threshold=name_threshold),
        )
        for search_term in search_terms
    ]

    # Combine with OR logic
    query = query_parts[0]
    for part in query_parts[1:]:
        query = query | part

    # Add scope type filters
    if exclude_scope_kinds:
        for kind in exclude_scope_kinds:
            # Only exclude if the field exists and matches the excluded type
            query = query & ((~tag_accesor.scopeKind.exists()) | (tag_accesor.scopeKind != kind))

    # Execute the search
    results: list[Document] = db.search(query)

    # Sort results: first by path (descending) and then by line number (ascending) within the same
    # path
    results = sorted(results, key=lambda x: (x.get("path", ""), -x.get("line", 0)), reverse=True)

    # Apply results limitation if max_results is specified
    max_results = getattr(parsed_args, "max_results", 10)
    if max_results is not None:
        results = results[:max_results]

    return results


# Helper to search symbols in OpenSearch instead of TinyDB
async def search_in_opensearch(
    client: AsyncOpenSearch,
    index_name: str,
    parsed_args: "SearchFunctionByNameArgs",
    *,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Query OpenSearch for symbol metadata using fuzzy matching on the *name* field."""
    search_terms = get_search_terms(parsed_args.query)

    # Build a BM25-based query (default similarity).
    should_clauses: list[dict[str, Any]] = [
        {
            "match": {
                "name": {
                    "query": term,
                    "operator": "or",
                },
            },
        }
        for term in search_terms
    ]

    body = {
        "size": max_results * 2,  # fetch a bit more, we'll filter later
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1,
            },
        },
        "sort": [
            {"_score": "desc"},
            {"path.keyword": "asc"},
            {"line": "asc"},
        ],
        "_source": [
            "name",
            "kind",
            "scope",
            "scopeKind",
            "path",
            "line",
            "pattern",
        ],
    }

    try:
        result = await client.search(index=index_name, body=body, request_timeout=60)
    except Exception:
        LOGGER.exception("Error searching in OpenSearch")
        # In case the index does not exist or any OS error.
        return []

    hits = result.get("hits", {}).get("hits", [])
    # Return only the _source plus _id
    return [{**hit.get("_source", {}), "_id": hit.get("_id")} for hit in hits][:max_results]


async def list_symbols(ctx: TreeExecutionContext, args: dict[str, Any]) -> str:
    try:
        parsed = SearchFunctionByNameArgs.model_validate(args)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    # Buscar en OpenSearch usando el índice creado para los tags
    os_results = await search_in_opensearch(
        await setup_opensearch_client(new_index=True),
        ctx.index_name,
        parsed,
        max_results=10,
    )

    # Transform results into TinyDB-like Documents with doc_id
    transformed_results: list[Document] = []
    for hit in os_results:
        # The _id in OpenSearch was set to the numeric doc_id
        try:
            doc_id = int(hit.get("_id", 0))
        except (TypeError, ValueError):
            continue

        document = ctx.tiny_db.get(doc_id=doc_id)
        if document is None:
            # If not found in memory (should not happen), create a placeholder Document
            transformed_results.append(Document(hit, doc_id))
        else:
            transformed_results.append(document)

    results = transformed_results

    if not results:
        filter_message = ""

        return (
            f"No functions found matching '{parsed.query}'{filter_message}. "
            f"Try a different search term or adjust the filters."
        )

    # Find corresponding graph nodes for methods and functions
    formatted_results = []
    for result in results:
        # Create a detailed string representation of the result
        function_type: str = result.get("kind", "unknown")
        scope_info: str = ""
        if "scope" in result and "scopeKind" in result:
            scope_info = f" - Defined in {result['scopeKind']} '{result['scope']}'"
        elif "scope" in result:
            scope_info = f" - Defined in '{result['scope']}'"

        # Clean up pattern by removing special characters at beginning and end, then trim
        pattern: str = result.get("pattern", "")
        if pattern:
            pattern = pattern.removeprefix("/^")
            pattern = pattern.removesuffix("$/")
            pattern = pattern.strip()

        formatted_results.append(
            f"ID: {result.doc_id} | {function_type.capitalize()}: {result['name']}{scope_info} | "
            f"File: {result['path']} | Snippet: {pattern}",
        )
    return "\n".join(formatted_results)


SEARCH_FUNCTION_TOOL = FunctionTool[str](
    name="list_symbols",
    description=(
        "Search for metadata about code elements (functions, classes, interfaces, constants) "
        "across the entire codebase by name. Use this tool to locate other definitions you may "
        "want to analyze further."
        "Returns matching element names, file paths, line numbers, and unique IDs — not full"
        " source code. "
        "To retrieve the full source, use the `fetch_symbol_code` tool with the returned ID."
    ),
    params_json_schema=SearchFunctionByNameArgs.model_json_schema(),
    on_invoke_tool=list_symbols,
)
