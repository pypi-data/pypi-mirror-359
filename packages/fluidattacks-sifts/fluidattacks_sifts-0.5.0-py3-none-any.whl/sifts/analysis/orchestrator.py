import fnmatch
import logging
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

from boto3 import Session
from tree_sitter import Node

import sifts
from sifts.analysis.code_parser import (
    analyze_method_node,
    process_file_for_functions,
)
from sifts.analysis.types import TreeExecutionContext
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import merge_async_generators
from sifts.core.repository import get_repo_head_hash
from sifts.core.types import Language
from sifts.io.db.ctags_tinydb import create_tiny_db_from_ctags
from sifts.io.db.dynamodb import (
    create_dynamo_context,
    get_vulnerable_analyses_by_root,
    insert_analysis,
)
from sifts.io.db.opensearch_client import setup_opensearch_client
from sifts.io.db.types import AnalysisFacet
from sifts.io.file_system import find_projects
from sifts.llm.constants import LLM_MODELS
from sifts.llm.router import ResilientRouter

LOGGER = logging.getLogger(__name__)


async def analyze_project(
    *,
    config: SiftsConfig,
    context: TreeExecutionContext,
    exclude: list[str] | None = None,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    function_iter = (
        iter_functions_from_line_config(context, config)
        if config.analysis.lines_to_check
        else iter_functions_from_project(
            context,
            config,
            exclude,
        )
    )

    function_pairs = []
    async for where, method_node in function_iter:
        function_pairs.append((where, method_node))

    function_coroutines = [
        analyze_method_node(
            method_node=method_node,
            where=where,
            context=context,
            config=config,
        )
        for where, method_node in function_pairs
    ]

    async for result in merge_async_generators(function_coroutines, limit=100):
        try:
            if result is not None:
                yield result
        except Exception:
            LOGGER.exception("Error processing function")


async def get_valid_functions(
    file_path: Path,
    lines: list[int],
) -> list[Node]:
    result: list[Node] = []
    async for _, node in process_file_for_functions(file_path):
        if any(x for x in lines if node.start_point[0] <= x <= node.end_point[0]):
            result.append(node)
    return result


async def iter_functions_from_line_config(
    context: TreeExecutionContext,
    config: SiftsConfig,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields functions to analyze based on line configs."""
    for line_config in config.analysis.lines_to_check:
        if not (config.analysis.working_dir / line_config.file).is_relative_to(
            context.working_dir,
        ):
            continue
        functions = await get_valid_functions(
            config.analysis.working_dir / line_config.file,
            line_config.lines,
        )
        for function in functions:
            yield (
                (config.analysis.working_dir / line_config.file).relative_to(
                    config.analysis.working_dir,
                ),
                function,
            )


async def iter_functions_from_project(
    context: TreeExecutionContext,
    config: SiftsConfig,
    exclude: list[str] | None = None,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields all functions for the files present in the TinyDB.

    This eliminates the redundant evaluation of exclusion patterns during the filesystem
    walk by relying exclusively on the list of files already collected in the TinyDB
    (which was generated with the desired exclusions).
    """
    # Collect unique relative file paths stored in the tiny DB
    tiny_db_paths: set[Path] = {
        Path(doc.get("path")) for doc in context.tiny_db.all() if doc.get("path")
    }

    # Apply include/exclude patterns specified in the analysis config (these were NOT
    # necessarily applied when the TinyDB was generated).
    include_patterns = config.analysis.include_files or []
    exclude_patterns = set(config.analysis.exclude_files + (exclude or []))

    if include_patterns:
        tiny_db_paths = {
            p
            for p in tiny_db_paths
            if any(fnmatch.fnmatch(str(p), pat) for pat in include_patterns)
        }

    if exclude_patterns:
        tiny_db_paths = {
            p
            for p in tiny_db_paths
            if not any(fnmatch.fnmatch(str(p), pat) for pat in exclude_patterns)
        }

    # Iterate over each remaining path and yield its functions
    for rel_path in tiny_db_paths:
        full_path = (context.working_dir / rel_path).resolve()

        if not full_path.exists():
            LOGGER.warning("File %s does not exist", full_path)
            continue

        async for _, function_node in process_file_for_functions(
            file_path=full_path,
            working_dir=context.working_dir,
        ):
            try:
                where = full_path.relative_to(config.analysis.working_dir)
            except ValueError:
                where = rel_path
            yield (where, function_node)


LOGGER = logging.getLogger(__name__)


SESSION = Session()
dynamo_startup, dynamo_shutdown, get_resource = create_dynamo_context()


async def scan_projects(config: SiftsConfig) -> list[AnalysisFacet]:
    await dynamo_startup()
    router = ResilientRouter(
        model_list=LLM_MODELS,
        routing_strategy="simple-shuffle",
        enable_pre_call_checks=True,
        cache_responses=True,
    )

    if router.cache.redis_cache is not None:
        await router.cache.redis_cache.ping()
    projects = find_projects(config.analysis.working_dir)
    open_client = await setup_opensearch_client()

    all_results = []

    async def process_single_project(
        working_dir: Path,
        language: Language,
        exclude: list[str] | None,
    ) -> AsyncGenerator[AnalysisFacet, None]:
        """Procesa un solo proyecto y retorna sus vulnerabilidades."""
        if config.analysis.lines_to_check and not any(
            (config.analysis.working_dir / item.file).is_relative_to(working_dir)
            for item in config.analysis.lines_to_check
        ):
            return

        LOGGER.info(
            "Analyzing project %s",
            working_dir.relative_to(Path(config.analysis.working_dir)),
        )
        tiny_db, index_name = await create_tiny_db_from_ctags(
            working_dir,
            exclude,
            language,
            metadata={
                "group_name": config.context.group_name,
                "root_id": config.context.root_id,
                "version": sifts.__version__,
                "commit": get_repo_head_hash(working_dir) or "",
                "uuid": str(uuid.uuid4()),
            },
        )
        context = TreeExecutionContext(
            working_dir=working_dir,
            tiny_db=tiny_db,
            analysis_dir=Path(config.analysis.working_dir),
            open_client=open_client,
            router=router,
            index_name=index_name,
        )

        try:
            # Get results from analyze_project_tree directly as AsyncGenerator
            async for response in analyze_project(
                context=context,
                config=config,
                exclude=exclude,
            ):
                if response is not None:
                    # Process the result and add to our list
                    await insert_analysis(response)
                    yield response
        except Exception:
            LOGGER.exception(
                "Error in analysis for project %s",
                working_dir.relative_to(Path(config.analysis.working_dir)),
            )

    # Crear coroutines para cada proyecto
    project_coroutines = [
        process_single_project(working_dir, language, exclude)
        for working_dir, language, exclude in projects
    ]

    # Usar limited_as_completed para procesar proyectos con límite de concurrencia
    async for project_result in merge_async_generators(project_coroutines, limit=3):
        try:
            all_results.append(project_result)
        except Exception:
            LOGGER.exception("Error processing project")

    LOGGER.info("Total vulnerabilities found: %d", len(all_results))
    return await get_vulnerable_analyses_by_root(
        group_name=config.context.group_name or "",
        root_id=config.context.root_id or "",
        version=sifts.__version__,
        commit=get_repo_head_hash(config.analysis.working_dir) or "",
    )
