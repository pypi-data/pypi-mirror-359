from .._client import Client
from .._client._get_json_response_body_type_adapter import (
    get_json_response_body_type_adapter,
)
from .._query_explanation import QueryExplanation
from .._typing import Duration
from ._enrich_context import enrich_context
from .context import Context


def explain_query(
    mdx: str, /, *, client: Client, context: Context, timeout: Duration
) -> QueryExplanation:
    path = f"{client.get_path_and_version_id('activeviam/pivot')[0]}/cube/query/mdx/queryplan"
    context = enrich_context(context, timeout=timeout)
    response = client._http_client.post(
        path,
        json={"context": {**context}, "mdx": mdx},
        # The timeout is part of `context` and is managed by the server.
        timeout=None,
    ).raise_for_status()
    body = response.content
    return get_json_response_body_type_adapter(
        QueryExplanation,  # type: ignore[type-abstract]
    ).validate_json(body)
