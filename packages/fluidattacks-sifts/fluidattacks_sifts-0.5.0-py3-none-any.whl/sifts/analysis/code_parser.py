import asyncio
import fnmatch
import hashlib
import logging
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime
from os import walk
from pathlib import Path
from string import Template
from typing import Any

import aioboto3
import aiofiles
from fluidattacks_core.serializers.snippet import find_function_name
from fluidattacks_core.serializers.syntax import (
    TREE_SITTER_FUNCTION_DECLARATION_MAP,
    InvalidFileType,
    extract_imports,
    get_language_from_path,
    parse_content_tree_sitter,
    query_nodes_by_language,
)
from opensearchpy import AsyncOpenSearch
from tree_sitter import Node

import sifts
from sifts.analysis.criteria import (
    filter_candidate_codes,
    find_most_similar_finding,
    generate_candidate_text,
)
from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.analysis.tools.format_response import FORMAT_RESPONSE
from sifts.analysis.tools.search_by_id import GET_FUNCTION_BY_ID_TOOL
from sifts.analysis.tools.search_by_name import SEARCH_FUNCTION_TOOL
from sifts.analysis.types import FunctionTool, TreeExecutionContext, VulnerabilityAssessment
from sifts.common_types.snippets import (
    SnippetHit,
    num_tokens_from_string,
)
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import limited_parallel
from sifts.core.repository import get_repo_head_hash
from sifts.io.db.dynamodb import (
    get_analyses_for_snippet,
    get_analyses_for_snippet_vulnerability,
    insert_snippet,
)
from sifts.io.db.opensearch_client import (
    SearchParameters,
    search_similar_vulnerabilities_by_field_name_bm25,
    search_similar_vulnerabilities_by_knn_code,
)
from sifts.io.db.types import AnalysisFacet, SafeFacet, VulnerableFacet
from sifts.io.db.types import SnippetFacet as Snippet
from sifts.io.file_system_defaults import TEST_FILES
from sifts.llm.config_data import MODEL_PARAMETERS
from sifts.llm.propose_changes import get_functional_semantics
from sifts.llm.ranking import reciprocal_rank_fusion
from sifts.llm.router import RouterStrict

LOGGER = logging.getLogger(__name__)
SESSION = aioboto3.Session()

TOOLS: list[FunctionTool[Any]] = [
    SEARCH_FUNCTION_TOOL,
    GET_FUNCTION_BY_ID_TOOL,
    FORMAT_RESPONSE,
]

TOOLS_BY_NAME: dict[str, FunctionTool[Any]] = {tool.name: tool for tool in TOOLS}

# Maximum number of conversational turns we will allow before bailing out. Prevents
# potential infinite loops if the model repeatedly requests tools without ever
# producing a final answer.
_MAX_CONVERSE_TURNS = 10


def build_tool_config() -> dict[str, Any]:
    """Translate *TOOLS* into the format expected by the Converse API."""
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": spec.name,
                    "description": spec.description,
                    "inputSchema": {
                        "json": spec.params_json_schema,
                    },
                },
            }
            for spec in TOOLS
        ],
    }


async def _create_snippet(  # noqa: PLR0913
    *,
    root_id: str,
    group_name: str,
    where: str,
    method_node: Node,
    language: str,
    code: str,
) -> Snippet | None:
    try:
        function_name = None
        identifier_ = find_function_name([method_node], language)
        if identifier_:
            identifier_node, _ = identifier_
            text = identifier_node.text
            function_name = (
                text.decode("utf-8") if (text is not None and isinstance(text, bytes)) else text
            )

        snippet_hash = hashlib.sha3_256(code.encode()).hexdigest()
        return Snippet(
            group_name=group_name,
            root_id=root_id,
            file_path=where,
            snippet_hash=snippet_hash,
            line_start=method_node.start_point.row + 1,
            line_end=method_node.end_point.row + 1,
            column_start=method_node.start_point.column + 1,
            column_end=method_node.end_point.column + 1,
            snippet_content=code,
            hash_type="sha3_256",
            language=language,
            last_seen_at=datetime.now(UTC).isoformat(),
            byte_start=method_node.start_byte,
            byte_end=method_node.end_byte,
            name=function_name,
        )
    except ValueError:
        return None


async def _get_semantics_and_embeddings(
    snippet: Snippet,
    router: RouterStrict,
) -> tuple[str | None, str | None]:
    if not snippet.snippet_content:
        return None, None

    abstract_propose, detailed_behavior = await get_functional_semantics(
        code=snippet.snippet_content,
        router=router,
    )
    if not abstract_propose or not detailed_behavior:
        return None, None

    return abstract_propose, detailed_behavior


async def _search_candidates(
    *,
    open_client: AsyncOpenSearch,
    snippet: Snippet,
    router: RouterStrict,
    search_parameters: SearchParameters,
) -> tuple[tuple[str, ...], ...]:
    if not snippet.snippet_content:
        return ()

    code_hits = await search_similar_vulnerabilities_by_knn_code(
        open_client=open_client,
        snippet_content=snippet.snippet_content,
        search_parameters=search_parameters,
    )
    if not code_hits:
        return ()
    abstract_propose, detailed_behavior = await _get_semantics_and_embeddings(
        snippet=snippet,
        router=router,
    )
    if not abstract_propose or not detailed_behavior:
        return ()
    abstract_hits, detailed_hits = await asyncio.gather(
        *[
            search_similar_vulnerabilities_by_field_name_bm25(
                open_client=open_client,
                field_value=abstract_propose,
                field_name="abstract_propose",
                search_parameters=search_parameters,
            ),
            search_similar_vulnerabilities_by_field_name_bm25(
                open_client=open_client,
                field_value=detailed_behavior,
                field_name="detailed_behavior",
                search_parameters=search_parameters,
            ),
        ],
    )
    code_hits_ids = {x["_id"] for x in code_hits}
    abstract_hits = [x for x in abstract_hits if x["_id"] in code_hits_ids]
    detailed_hits = [x for x in detailed_hits if x["_id"] in code_hits_ids]

    candidates_hits: list[SnippetHit] = reciprocal_rank_fusion(
        top_n=100,
        hits_lists=[code_hits, abstract_hits, detailed_hits],
    )

    filtered_candidates = (await filter_candidate_codes(candidates_hits))[:10]
    return tuple(
        tuple(x["_source"]["metadata"]["criteria_code"] for x in group)
        for group in filtered_candidates
    )


async def invoke_agent(
    context: TreeExecutionContext,
    user_question: str,
) -> VulnerabilityAssessment | None:
    async with SESSION.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    ) as bedrock:
        # Initial user message
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": [{"text": user_question}]},
        ]

        tool_config = build_tool_config()

        for turn in range(_MAX_CONVERSE_TURNS):
            try:
                response = await bedrock.converse(
                    modelId=(
                        "arn:aws:bedrock:us-east-1:205810638802:application-inference-profile/ihi8eded6fcg"
                    ),
                    system=[
                        {"text": MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["system"]},
                    ],
                    messages=messages,
                    toolConfig=tool_config,
                )
            except bedrock.exceptions.ClientError:
                LOGGER.exception("Error calling Converse API (turn %s)", turn)
                return None

            stop_reason = response.get("stopReason")
            output_message = response["output"]["message"]

            # The agent should continue requesting tools until it emits FORMAT_RESPONSE.
            if stop_reason != "tool_use":
                LOGGER.warning("Unexpected stop reason '%s' received, aborting.", stop_reason)
                return None

            # `output_message["content"]` always contains a single element, so we can
            # access it directly instead of iterating.
            block = output_message["content"][0] if output_message["content"] else {}
            tool_use = block.get("toolUse")
            if not tool_use:
                LOGGER.error(
                    "Expected 'toolUse' key in response block but none was found: %s",
                    block,
                )
                continue

            name = tool_use["name"]
            raw_tool_input: dict[str, Any] = tool_use["input"]
            # Flatten JSON schema values returned by Bedrock (they wrap each actual value
            # inside a dict with a single 'value' key).
            tool_input = {
                k: (v.get("value") if isinstance(v, dict) else v) for k, v in raw_tool_input.items()
            }
            tool_use_id = tool_use["toolUseId"]

            tool = TOOLS_BY_NAME.get(name)
            if tool is None:
                LOGGER.error("Unknown tool requested by model: %s", name)
                continue

            LOGGER.info("Invoking tool '%s' with input %s", name, tool_input)

            # If the model is providing the final answer we can stop looping early.
            if tool is FORMAT_RESPONSE:
                result: VulnerabilityAssessment | None = await tool.on_invoke_tool(
                    context,
                    tool_input,
                )
                if result is None:
                    LOGGER.error(
                        "FORMAT_RESPONSE returned None - invalid input: %s",
                        tool_input,
                    )
                return result

            # Run the requested helper tool and attach its result so the model can consume it.
            tool_result = await tool.on_invoke_tool(context, tool_input)
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"text": str(tool_result)}],
                            },
                        },
                    ],
                },
            )
            # Proceed to the next turn with the augmented message history.
            continue

        LOGGER.error(
            "Reached the maximum of %s turns without obtaining a final assessment.",
            _MAX_CONVERSE_TURNS,
        )
        return None


async def _process_single_candidate_group(  # noqa: PLR0911, PLR0913
    candidates_group: tuple[str, ...],
    context: TreeExecutionContext,
    snippet: Snippet,
    imports: str,
    *,
    strict: bool = True,
    candidate_index: int,
) -> AnalysisFacet | None:
    candidate_id = "-".join(sorted(candidates_group))
    previous_analyses = await get_analyses_for_snippet_vulnerability(
        group_name=snippet.group_name,
        root_id=snippet.root_id,
        version=sifts.__version__,
        file_path=snippet.file_path,
        snippet_hash=snippet.snippet_hash,
        vulnerability_id=candidate_id,
    )
    if previous_analyses:
        return None

    candidate_text = generate_candidate_text(candidates_group)
    code_enumerated = "\n".join(
        (
            f"{index}| {x}"
            for index, x in enumerate(
                (snippet.snippet_content or "").split("\n"),
                start=snippet.line_start or 0,
            )
        ),
    )
    count = num_tokens_from_string(code_enumerated, "gpt-4o")
    if count > 3000:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too long to be processed: %s:%s, count: %s",
            snippet.file_path,
            snippet.line_start,
            count,
        )
        return None
    if count < 50:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too short to be processed: %s:%s, count: %s",
            snippet.file_path,
            snippet.line_start,
            count,
        )
        return None
    first_message = {
        "role": "user",
        "content": Template(
            MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["instructions"]
            if strict
            else MODEL_PARAMETERS["prompts"]["agents"]["vuln_loose"]["instructions"],
        ).safe_substitute(
            code=code_enumerated,
            functionName=snippet.name,
            vulnerability_knowledge=candidate_text,
            filePath=snippet.file_path,
            imports=imports,
        ),
    }
    trace_id = None
    try:
        result: VulnerabilityAssessment | None = await invoke_agent(
            context,
            first_message["content"],
        )
    except ValueError:
        return None
    if not result:
        return None

    cost = 0

    if result.is_vulnerable and result.vulnerability_type:
        if snippet.name is not None and result.vulnerable_function != snippet.name:
            return None
        finding_code = (
            await find_most_similar_finding(
                router=context.router,
                title=result.vulnerability_type,
                description=result.explanation,
            )
        ) or candidates_group[0]
        return VulnerableFacet(
            group_name=snippet.group_name,
            root_id=snippet.root_id,
            version=sifts.__version__,
            commit=get_repo_head_hash(context.working_dir) or "",
            snippet_hash=snippet.snippet_hash,
            analyzed_at=datetime.now(UTC),
            file_path=snippet.file_path,
            path=snippet.file_path,
            cost=cost,
            vulnerability_id_candidates=list(candidates_group),
            vulnerable_lines=result.vulnerable_lines or [],
            ranking_score=0,
            reason=result.explanation,
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            suggested_criteria_code=finding_code,
            suggested_finding_title=DEFINES_VULNERABILITIES[finding_code]["en"]["title"],
        )

    return SafeFacet(
        group_name=snippet.group_name,
        root_id=snippet.root_id,
        version=sifts.__version__,
        commit=snippet.snippet_hash,
        snippet_hash=snippet.snippet_hash,
        analyzed_at=datetime.now(UTC),
        file_path=snippet.file_path,
        path=snippet.file_path,
        cost=cost,
        candidate_index=candidate_index,
        trace_id=trace_id,
        input_tokens=0,
        output_tokens=0,
        total_tokens=0,
        reason=result.explanation,
        vulnerability_id_candidates=list(candidates_group),
    )


async def _extract_code_and_imports(
    *,
    working_dir: Path,
    where: Path,
    method_node: Node,
) -> tuple[str, str, str] | None:
    try:
        async with aiofiles.open(working_dir / where, "rb") as f:
            file_content = await f.read()

        code = (
            method_node.text.decode("utf-8")
            if method_node.text
            else file_content[method_node.start_byte : method_node.end_byte].decode("utf-8")
        )
        language = get_language_from_path(str(where))
    except FileNotFoundError:
        LOGGER.warning("File not found: %s", where)
        return None
    except UnicodeDecodeError:
        LOGGER.warning("File is not UTF-8 encoded: %s", where)
        return None
    else:
        if not language or not code:
            return None

        imports_nodes = extract_imports(file_content.decode("utf-8"), language)
        imports = "\n".join([(x.text or b"").decode() for x in imports_nodes])
        return code, imports, language


def _is_snippet_within_token_limits(snippet: Snippet) -> bool:
    count = num_tokens_from_string(snippet.snippet_content or "", "gpt-4o")
    if count > 3000:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too long to be processed: %s:%s, count: %s",
            snippet.file_path,
            snippet.line_start,
            count,
        )
        return False
    if count < 50:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too short to be processed: %s:%s, count: %s",
            snippet.file_path,
            snippet.line_start,
            count,
        )
        return False
    return True


async def _has_existing_vulnerabilities(
    snippet: Snippet,
) -> bool:
    previous_analyses = await get_analyses_for_snippet(
        group_name=snippet.group_name,
        root_id=snippet.root_id,
        file_path=snippet.file_path,
        snippet_hash=snippet.snippet_hash,
        version=sifts.__version__,
    )

    return bool(previous_analyses)


async def analyze_method_node(
    *,
    context: TreeExecutionContext,
    where: Path,
    method_node: Node,
    config: SiftsConfig,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    extraction = await _extract_code_and_imports(
        working_dir=config.analysis.working_dir,
        where=where,
        method_node=method_node,
    )
    if extraction is None:
        return

    code, imports, language = extraction

    # Build snippet representation for the function/method
    snippet = await _create_snippet(
        root_id=config.context.root_id or "",
        group_name=config.context.group_name or "",
        where=str(where),
        method_node=method_node,
        language=language,
        code=code,
    )
    if snippet is None or not _is_snippet_within_token_limits(snippet):
        return

    # Persist snippet and skip if it was already processed
    await insert_snippet(snippet)
    if await _has_existing_vulnerabilities(snippet):
        return

    if not snippet.snippet_content:
        return

    # Retrieve candidate codes
    candidate_codes = await _search_candidates(
        open_client=context.open_client,
        search_parameters=SearchParameters(
            include_vulnerabilities=config.analysis.include_vulnerabilities,
            exclude_vulnerabilities=config.analysis.exclude_vulnerabilities,
            group_name=config.context.group_name,
        ),
        snippet=snippet,
        router=context.router,
    )

    tasks = [
        _process_single_candidate_group(
            candidates_group=candidate_group,
            snippet=snippet,
            context=context,
            imports=imports,
            candidate_index=index,
        )
        for index, candidate_group in enumerate(candidate_codes)
    ]

    async for result in limited_parallel(tasks, limit=10):
        yield result


def _is_top_level_function(node: Node, function_node_names: set[str]) -> bool:
    parent = node.parent
    while parent:
        if parent.type in function_node_names:
            return False  # It's nested
        parent = parent.parent
    return True  # It's top-level


async def _process_files_with_walk(
    working_dir: Path,
    exclude_patterns: list[str],
    dir_wide_file_trigger_patterns: list[str],
) -> AsyncGenerator[tuple[str, Node], None]:
    for root, dirs, files in walk(working_dir, topdown=True):
        root_path = Path(root)
        root_str = str(root_path)

        if _should_skip_all_files_in_dir(files, root_path, dir_wide_file_trigger_patterns):
            dirs[:] = []
            continue

        dirs[:] = [
            d_name
            for d_name in dirs
            if not any(
                fnmatch.fnmatch(str(root_path / d_name), ex_pat) for ex_pat in exclude_patterns
            )
        ]

        if any(fnmatch.fnmatch(root_str, ex_pat) for ex_pat in exclude_patterns):
            continue

        for file_name in files:
            file_path = root_path / file_name
            file_path_str = str(file_path)

            if _should_skip_file(file_path_str, exclude_patterns):
                continue

            async for result in process_file_for_functions(
                file_path=file_path,
                working_dir=working_dir,
            ):
                yield result


async def _process_included_files_directly(
    working_dir: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
    start_working_dir: Path,  # Assumed to be validated as not None by caller
) -> AsyncGenerator[tuple[str, Node], None]:
    for included_file_rel_path_str in include_patterns:
        file_to_check = (start_working_dir / included_file_rel_path_str).resolve()

        if not (
            file_to_check.exists() and file_to_check.is_file()
        ) or not file_to_check.is_relative_to(working_dir.resolve()):
            continue

        file_path_str = str(file_to_check)

        if _should_skip_file(file_path_str, exclude_patterns):
            continue

        parent_dir = file_to_check.parent
        try:
            [f.name for f in parent_dir.iterdir() if f.is_file()]

        except OSError:
            continue

        async for result in process_file_for_functions(
            file_path=file_to_check,
            working_dir=working_dir,
        ):
            yield result


def _should_skip_all_files_in_dir(
    files: list[str],
    root_path: Path,
    dir_wide_file_trigger_patterns: list[str],
) -> bool:
    if not dir_wide_file_trigger_patterns:
        return False
    for file_name in files:
        file_path_str_for_trigger_check = str(root_path / file_name)
        if any(
            fnmatch.fnmatch(file_path_str_for_trigger_check, trigger_pat)
            for trigger_pat in dir_wide_file_trigger_patterns
        ):
            return True
    return False


def _should_skip_file(file_path_str: str, exclude_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(file_path_str, ex_pat) for ex_pat in exclude_patterns)


async def iter_project_functions(
    working_dir: Path,
    exclude_patterns_param: list[str] | None,
    include_patterns_param: list[str] | None,
    start_working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    exclude_patterns = exclude_patterns_param if exclude_patterns_param is not None else []
    include_patterns = include_patterns_param if include_patterns_param is not None else []

    # Assuming TEST_FILES is defined in the global scope or imported
    dir_wide_file_trigger_patterns = [
        pat for pat in exclude_patterns if "." in pat and "*" in pat and pat not in TEST_FILES
    ]

    if include_patterns:
        if not start_working_dir:
            msg = "include_patterns were provided, but start_working_dir was not."
            raise ValueError(msg)
        # start_working_dir is confirmed to be Path here
        async for result in _process_included_files_directly(
            working_dir=working_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            start_working_dir=start_working_dir,
        ):
            yield result
    else:
        async for result in _process_files_with_walk(
            working_dir=working_dir,
            exclude_patterns=exclude_patterns,
            dir_wide_file_trigger_patterns=dir_wide_file_trigger_patterns,
        ):
            yield result


async def process_file_for_functions(
    file_path: Path,
    working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    language = get_language_from_path(str(file_path))
    if not language:
        return
    try:
        async with aiofiles.open(file=file_path, mode="rb") as f:
            content = await f.read()
            try:
                tree = parse_content_tree_sitter(content, language)
            except (OSError, InvalidFileType):
                return
    except FileNotFoundError:
        return

    function_node_names = TREE_SITTER_FUNCTION_DECLARATION_MAP[language]
    function_nodes = query_nodes_by_language(
        language,
        tree,
        TREE_SITTER_FUNCTION_DECLARATION_MAP,
    )
    if len(content.splitlines()) > 2000:  # noqa: PLR2004
        LOGGER.warning(
            "File is too long to be processed: %s, count: %s",
            file_path,
            len(content.splitlines()),
        )
        return
    # Prevent minified files
    if (
        len(function_nodes) > 1
        and len({node.start_point[0] for node in (y for x in function_nodes.values() for y in x)})
        == 1
    ):
        return
    for node in (y for x in function_nodes.values() for y in x):
        if _is_top_level_function(node, set(function_node_names)):
            # Yield relative path from working_dir
            if working_dir:
                yield (str(file_path.relative_to(working_dir)), node)
            else:
                yield (str(file_path), node)


def search_nodes_in_tree(root_node: Node, line: int, node_types: tuple[str, ...]) -> Node | None:
    # First check if the current node is of the desired type and contains the line
    if root_node.type in node_types and root_node.start_point[0] <= line <= root_node.end_point[0]:
        return root_node

    # If this node doesn't contain the line we're looking for, no need to search its children
    if line < root_node.start_point[0] or line > root_node.end_point[0]:
        return None

    # Search in the children of the current node
    for child in root_node.children:
        result = search_nodes_in_tree(child, line, node_types)
        if result:
            return result

    return None


def traverse_tree(tree: Node) -> Generator[Node, None, None]:
    cursor = tree.walk()
    cursor.goto_first_child()
    cursor.goto_parent()

    reached_root = False
    while reached_root is False:
        if not cursor.node:
            break
        yield cursor.node

        if cursor.goto_first_child():
            continue

        if cursor.goto_next_sibling():
            continue

        retracing = True
        while retracing:
            if not cursor.goto_parent():
                retracing = False
                reached_root = True

            if cursor.goto_next_sibling():
                retracing = False
