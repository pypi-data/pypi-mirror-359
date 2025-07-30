# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
from semver import Version
from tools.tool_params import *


# List all the helper functions, these functions perform a single rest call to opensearch
# these functions will be used in tools folder to eventually write more complex tools
def list_indices(args: ListIndicesArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    response = client.cat.indices(format='json')
    return response


def get_index_mapping(args: GetIndexMappingArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    response = client.indices.get_mapping(index=args.index)
    return response


def search_index(args: SearchIndexArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    response = client.search(index=args.index, body=args.query)
    return response


def get_shards(args: GetShardsArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    response = client.cat.shards(index=args.index, format='json')
    return response


def cluster_health(args: ClusterHealthArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    if hasattr(args, 'index') and args.index:
        response = client.cluster.health(index=args.index)
    else:
        response = client.cluster.health()
    return response


def count_documents(args: CountArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    if hasattr(args, 'index') and args.index:
        if hasattr(args, 'body') and args.body:
            response = client.count(index=args.index, body=args.body)
        else:
            response = client.count(index=args.index)
    else:
        if hasattr(args, 'body') and args.body:
            response = client.count(body=args.body)
        else:
            response = client.count()
    return response


def explain_query(args: ExplainArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    response = client.explain(index=args.index, id=args.id, body=args.body)
    return response


def msearch_documents(args: MsearchArgs) -> json:
    from .client import initialize_client

    client = initialize_client(args)
    if hasattr(args, 'index') and args.index:
        response = client.msearch(index=args.index, body=args.body)
    else:
        response = client.msearch(body=args.body)
    return response


def get_opensearch_version(args: baseToolArgs) -> Version:
    """Get the version of OpenSearch cluster.

    Returns:
        Version: The version of OpenSearch cluster (SemVer style)
    """
    from .client import initialize_client, is_serverless

    if is_serverless(args):
        # TODO: The version is placeholder with no impact on logic, we need to add serverless compatibility check for all tools
        return Version.parse('2.11.0')

    client = initialize_client(args)
    response = client.info()
    return Version.parse(response['version']['number'])
