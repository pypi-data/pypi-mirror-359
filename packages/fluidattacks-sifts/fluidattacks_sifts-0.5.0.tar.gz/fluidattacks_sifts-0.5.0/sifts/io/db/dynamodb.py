from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, cast

import aioboto3
from asyncache import cached
from boto3.dynamodb.conditions import Attr
from cachetools import Cache
from types_aiobotocore_dynamodb import DynamoDBServiceResource
from types_aiobotocore_dynamodb.service_resource import Table as DynamoTable

from sifts.io.db.types import AnalysisFacet, SafeFacet, SnippetFacet, VulnerableFacet

SESSION = aioboto3.Session()
StartupCallable = Callable[[], Awaitable[None]]
ShutdownCallable = Callable[[], Awaitable[None]]
GetResourceCallable = Callable[[], Awaitable[DynamoDBServiceResource]]
DynamoContext = tuple[StartupCallable, ShutdownCallable, GetResourceCallable]


TABLE_RESOURCES: dict[str, DynamoTable] = {}


def create_dynamo_context() -> DynamoContext:
    context_stack = None
    resource = None

    async def _startup() -> None:
        nonlocal context_stack, resource

        context_stack = AsyncExitStack()
        resource = await context_stack.enter_async_context(
            SESSION.resource(
                service_name="dynamodb",
                use_ssl=True,
                verify=True,
            ),
        )
        if context_stack:
            await context_stack.aclose()

    async def _shutdown() -> None:
        if context_stack:
            await context_stack.aclose()

    async def _get_resource() -> DynamoDBServiceResource:
        if resource is None:
            await dynamo_startup()

        return cast(DynamoDBServiceResource, resource)

    return _startup, _shutdown, _get_resource


dynamo_startup, dynamo_shutdown, get_resource = create_dynamo_context()


async def get_table(table_name: str) -> DynamoTable:
    if table_name not in TABLE_RESOURCES:
        resource = await get_resource()
        TABLE_RESOURCES[table_name] = await resource.Table(table_name)
    return TABLE_RESOURCES[table_name]


async def insert_snippet(snippet: SnippetFacet) -> None:
    table = await get_table("sifts_state")
    pk = f"GROUP#{snippet.group_name}#ROOT#{snippet.root_id}"
    sk = f"SNIPPET#FILE#{snippet.file_path}#HASH#{snippet.snippet_hash}"
    item = snippet.model_dump()
    item["pk"] = pk
    item["sk"] = sk
    await table.put_item(Item=serialize(item))


async def insert_analysis(analysis: AnalysisFacet) -> None:
    table = await get_table("sifts_state")
    pk = f"GROUP#{analysis.group_name}#ROOT#{analysis.root_id}"
    candidates_ids = "-".join(sorted(analysis.vulnerability_id_candidates))
    sk = (
        f"ANALYSIS#VERSION#{analysis.version}#PATH#{analysis.file_path}#SNIPPET#{analysis.snippet_hash}"
        f"#VULNERABILITY#{candidates_ids}"
    )
    item = analysis.model_dump()
    item["pk"] = pk
    item["sk"] = sk
    await table.put_item(Item=serialize(item))


async def get_snippets_by_root(group_name: str, root_id: str) -> list[SnippetFacet]:
    table = await get_table("sifts_state")
    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    response = await table.query(
        KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": pk,
            ":sk_prefix": "SNIPPET#",
        },
    )
    return [SnippetFacet.model_validate(item) for item in response["Items"]]


async def get_snippets_by_file_path(
    group_name: str,
    root_id: str,
    file_path: str,
) -> list[SnippetFacet]:
    table = await get_table("sifts_state")
    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    response = await table.query(
        KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
        ExpressionAttributeValues={
            ":pk": pk,
            ":sk_prefix": f"SNIPPET#FILE#{file_path}",
        },
    )
    return [SnippetFacet.model_validate(item) for item in response["Items"]]


def serialize(object_: object) -> Any:  # noqa: ANN401
    # Mappings
    if isinstance(object_, dict):
        return {k: serialize(v) for k, v in object_.items()}

    if isinstance(object_, (list, tuple, set)):
        return [serialize(o) for o in object_]

    # Scalars
    if isinstance(object_, datetime):
        return object_.astimezone(tz=UTC).isoformat()
    if isinstance(object_, float):
        return Decimal(str(object_))
    if isinstance(object_, Enum):
        return object_.value

    return object_


async def _query_analyses_pk_prefix(
    table: DynamoTable,
    pk: str,
    sk_prefix: str,
    filter_expression: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    kwargs: dict[str, Any] = {
        "KeyConditionExpression": "pk = :pk AND begins_with(sk, :sk_prefix)",
        "ExpressionAttributeValues": {
            ":pk": pk,
            ":sk_prefix": sk_prefix,
        },
    }
    if filter_expression:
        kwargs["FilterExpression"] = filter_expression["expression"]
        kwargs["ExpressionAttributeValues"].update(filter_expression["values"])

    response = await table.query(**kwargs)
    return response["Items"]


async def get_analyses_for_snippet(
    group_name: str,
    root_id: str,
    version: str,
    file_path: str,
    snippet_hash: str,
) -> list[AnalysisFacet]:
    """Return analyses of a snippet for a specific version (version comes first in SK)."""
    table = await get_table("sifts_state")
    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    sk_prefix = f"ANALYSIS#VERSION#{version}#PATH#{file_path}#SNIPPET#{snippet_hash}#"

    items = await _query_analyses_pk_prefix(table, pk, sk_prefix)
    return [
        (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
        for item in items
    ]


async def get_analyses_by_file_path_version(
    group_name: str,
    root_id: str,
    version: str,
    file_path: str,
) -> list[AnalysisFacet]:
    """Return all analyses for a file path within a given version."""
    table = await get_table("sifts_state")
    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    sk_prefix = f"ANALYSIS#VERSION#{version}#PATH#{file_path}#"

    items = await _query_analyses_pk_prefix(table, pk, sk_prefix)
    return [
        (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
        for item in items
    ]


async def get_analyses_for_snippet_vulnerability(  # noqa: PLR0913
    group_name: str,
    root_id: str,
    version: str,
    file_path: str,
    snippet_hash: str,
    vulnerability_id: str,
) -> list[AnalysisFacet]:
    table = await get_table("sifts_state")
    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    sk_prefix = (
        f"ANALYSIS#VERSION#{version}#PATH#{file_path}#SNIPPET#{snippet_hash}"
        f"#VULNERABILITY#{vulnerability_id}#"
    )

    items = await _query_analyses_pk_prefix(table, pk, sk_prefix)
    return [
        (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
        for item in items
    ]


@cached(cache=Cache(maxsize=1000))  # type: ignore[misc]
async def get_snippet_by_hash(
    group_name: str,
    root_id: str,
    file_path: str,
    snippet_hash: str,
) -> SnippetFacet | None:
    table = await get_table("sifts_state")

    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    sk = f"SNIPPET#FILE#{file_path}#HASH#{snippet_hash}"

    response = await table.get_item(Key={"pk": pk, "sk": sk})

    item = response.get("Item")
    if item is None:
        return None

    return SnippetFacet.model_validate(item)


async def get_vulnerable_analyses_by_root(
    group_name: str,
    root_id: str,
    version: str,
    commit: str | None = None,
) -> list[AnalysisFacet]:
    table = await get_table("sifts_state")

    pk = f"GROUP#{group_name}#ROOT#{root_id}"
    sk_prefix = f"ANALYSIS#VERSION#{version}#"
    if commit:
        filter_expression = Attr("vulnerable").eq(value=True) & Attr("commit").eq(commit)
    else:
        filter_expression = Attr("vulnerable").eq(value=True)  # type: ignore[assignment]

    response = await table.query(
        KeyConditionExpression="pk = :pk AND begins_with(sk, :sk_prefix)",
        FilterExpression=filter_expression,
        ExpressionAttributeValues={
            ":pk": pk,
            ":sk_prefix": sk_prefix,
        },
    )

    return [
        (VulnerableFacet if item["vulnerable"] else SafeFacet).model_validate(item)
        for item in response["Items"]
    ]
