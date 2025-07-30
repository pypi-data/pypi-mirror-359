# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field
from typing import Any, Optional


class baseToolArgs(BaseModel):
    """Base class for all tool arguments that contains common OpenSearch connection parameters."""

    opensearch_cluster_name: str = Field(
        default='', description='The name of the OpenSearch cluster'
    )


class ListIndicesArgs(baseToolArgs):
    pass


class GetIndexMappingArgs(baseToolArgs):
    index: str = Field(description='The name of the index to get mapping information for')


class SearchIndexArgs(baseToolArgs):
    index: str = Field(description='The name of the index to search in')
    query: Any = Field(description='The search query in OpenSearch query DSL format')


class GetShardsArgs(baseToolArgs):
    index: str = Field(description='The name of the index to get shard information for')


class ClusterHealthArgs(baseToolArgs):
    index: Optional[str] = Field(
        default=None, 
        description='Limit health reporting to a specific index'
    )


class CountArgs(baseToolArgs):
    index: Optional[str] = Field(
        default=None, 
        description='The name of the index to count documents in'
    )
    body: Optional[Any] = Field(
        default=None, 
        description='Query in JSON format to filter documents'
    )


class ExplainArgs(baseToolArgs):
    index: str = Field(description='The name of the index to retrieve the document from')
    id: str = Field(description='The document ID to explain')
    body: Any = Field(description='Query in JSON format to explain against the document')


class MsearchArgs(baseToolArgs):
    index: Optional[str] = Field(
        default=None, 
        description='Default index to search in'
    )
    body: Any = Field(description='Multi-search request body in NDJSON format')
