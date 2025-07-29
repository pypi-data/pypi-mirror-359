# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .memory_metadata_param import MemoryMetadataParam

__all__ = ["MemorySearchParams"]


class MemorySearchParams(TypedDict, total=False):
    query: Required[str]
    """Detailed search query describing what you're looking for.

    For best results, write 2-3 sentences that include specific details, context,
    and time frame. For example: 'Find recurring customer complaints about API
    performance from the last month. Focus on issues where customers specifically
    mentioned timeout errors or slow response times in their conversations.'
    """

    max_memories: int
    """Maximum number of memories to return"""

    max_nodes: int
    """Maximum number of neo nodes to return"""

    enable_agentic_graph: bool
    """Whether to enable agentic graph search.

    Default is false (graph search is skipped). Set to true to use agentic graph
    search.
    """

    external_user_id: Optional[str]
    """Optional external user ID to filter search results by a specific external user.

    If both user_id and external_user_id are provided, user_id takes precedence.
    """

    metadata: Optional[MemoryMetadataParam]
    """Metadata for memory request"""

    rank_results: bool
    """Whether to enable additional ranking of search results.

    Default is false because results are already ranked when using an LLM for search
    (recommended approach). Only enable this if you're not using an LLM in your
    search pipeline and need additional result ranking.
    """

    user_id: Optional[str]
    """Optional internal user ID to filter search results by a specific user.

    If not provided, results are not filtered by user. If both user_id and
    external_user_id are provided, user_id takes precedence.
    """

    accept_encoding: Annotated[str, PropertyInfo(alias="Accept-Encoding")]
