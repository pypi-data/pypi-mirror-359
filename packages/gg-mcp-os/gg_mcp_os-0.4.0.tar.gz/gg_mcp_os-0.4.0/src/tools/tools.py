# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
from typing import Any, Dict, List
from opensearch.helper import (
    count_documents,
    explain_query,
    get_index_mapping,
    get_shards,
    list_indices,
    msearch_documents,
    search_index,
    cluster_health,
)
from opensearch.diagnostic import diagnose_connection
from tools.tool_params import (
    ClusterHealthArgs,
    CountArgs,
    ExplainArgs,
    GetIndexMappingArgs,
    GetShardsArgs,
    ListIndicesArgs,
    MsearchArgs,
    SearchIndexArgs,
    baseToolArgs,
)


def check_tool_compatibility(tool_name: str, args: baseToolArgs) -> None:
    """Check if the tool is compatible with the current OpenSearch version."""
    pass


async def connection_diagnostic_tool(args: ListIndicesArgs) -> list[dict]:
    """Diagnose OpenSearch connection issues and provide detailed feedback."""
    try:
        # Get connection details
        opensearch_url = os.getenv('OPENSEARCH_URL', '')
        opensearch_username = os.getenv('OPENSEARCH_USERNAME', '')
        opensearch_password = os.getenv('OPENSEARCH_PASSWORD', '')
        
        if not opensearch_url:
            return [{
                'type': 'text', 
                'text': 'Error: OPENSEARCH_URL environment variable is not set'
            }]
        
        # Run connection diagnosis
        success, message = diagnose_connection(opensearch_url, opensearch_username, opensearch_password)
        
        if success:
            # Try to actually connect and get cluster info
            try:
                from opensearch.client import initialize_client
                client = initialize_client(args)
                cluster_info = client.info()
                
                response_text = f"✅ OpenSearch Connection Successful!\n\n"
                response_text += f"🔗 URL: {opensearch_url}\n"
                response_text += f"📊 Cluster: {cluster_info.get('cluster_name', 'Unknown')}\n"
                response_text += f"🏷️  Node: {cluster_info.get('name', 'Unknown')}\n"
                response_text += f"📦 Version: {cluster_info.get('version', {}).get('number', 'Unknown')}\n"
                
                # Test basic API access
                try:
                    indices = list_indices(args)
                    response_text += f"📂 Available indices: {len(indices)}\n"
                    if indices:
                        response_text += f"   Sample indices: {', '.join(idx['index'] for idx in indices[:5])}\n"
                except Exception as e:
                    response_text += f"⚠️  Warning: Could not list indices: {str(e)}\n"
                
                return [{'type': 'text', 'text': response_text}]
                
            except Exception as e:
                return [{
                    'type': 'text', 
                    'text': f"❌ Connection diagnosis passed, but client initialization failed:\n{str(e)}"
                }]
        else:
            # Connection failed, provide diagnostic information
            response_text = f"❌ OpenSearch Connection Failed\n\n"
            response_text += f"🔗 URL: {opensearch_url}\n"
            response_text += f"👤 Username: {opensearch_username or '(not set)'}\n"
            response_text += f"🔐 Password: {'***' if opensearch_password else '(not set)'}\n\n"
            response_text += f"📋 Diagnostic Results:\n{message}\n\n"
            
            # Add troubleshooting suggestions
            response_text += "🔧 Troubleshooting Suggestions:\n"
            response_text += "1. Verify the OpenSearch URL is correct\n"
            response_text += "2. Check if the server is accessible from your network\n"
            response_text += "3. Ensure credentials are correct if authentication is required\n"
            response_text += "4. Try setting OPENSEARCH_SSL_VERIFY=false for self-signed certificates\n"
            response_text += "5. Check if the URL points to the API endpoint, not the web interface\n"
            
            return [{'type': 'text', 'text': response_text}]
            
    except Exception as e:
        return [{
            'type': 'text', 
            'text': f'Error during connection diagnosis: {str(e)}'
        }]


async def cluster_health_tool(args: ClusterHealthArgs) -> list[dict]:
    try:
        check_tool_compatibility('ClusterHealthTool', args)
        health = cluster_health(args)
        formatted_health = json.dumps(health, indent=2)

        return [{'type': 'text', 'text': f'Cluster health:\n{formatted_health}'}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting cluster health: {str(e)}'}]


async def count_tool(args: CountArgs) -> list[dict]:
    try:
        check_tool_compatibility('CountTool', args)
        result = count_documents(args)
        formatted_result = json.dumps(result, indent=2)

        return [{'type': 'text', 'text': f'Document count:\n{formatted_result}'}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error counting documents: {str(e)}'}]


async def explain_tool(args: ExplainArgs) -> list[dict]:
    try:
        check_tool_compatibility('ExplainTool', args)
        result = explain_query(args)
        formatted_result = json.dumps(result, indent=2)

        return [{'type': 'text', 'text': f'Query explanation for document {args.id}:\n{formatted_result}'}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error explaining query: {str(e)}'}]


async def msearch_tool(args: MsearchArgs) -> list[dict]:
    try:
        check_tool_compatibility('MsearchTool', args)
        result = msearch_documents(args)
        formatted_result = json.dumps(result, indent=2)

        return [{'type': 'text', 'text': f'Multi-search results:\n{formatted_result}'}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error executing multi-search: {str(e)}'}]


async def list_indices_tool(args: ListIndicesArgs) -> list[dict]:
    try:
        check_tool_compatibility('ListIndexTool', args)
        indices = list_indices(args)
        indices_text = '\n'.join(index['index'] for index in indices)

        # Return in MCP expected format
        return [{'type': 'text', 'text': indices_text}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error listing indices: {str(e)}'}]


async def get_index_mapping_tool(args: GetIndexMappingArgs) -> list[dict]:
    try:
        check_tool_compatibility('IndexMappingTool', args)
        mapping = get_index_mapping(args)
        formatted_mapping = json.dumps(mapping, indent=2)

        return [{'type': 'text', 'text': f'Mapping for {args.index}:\n{formatted_mapping}'}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting mapping: {str(e)}'}]


async def search_index_tool(args: SearchIndexArgs) -> list[dict]:
    try:
        check_tool_compatibility('SearchIndexTool', args)
        result = search_index(args)
        formatted_result = json.dumps(result, indent=2)

        return [
            {
                'type': 'text',
                'text': f'Search results from {args.index}:\n{formatted_result}',
            }
        ]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error searching index: {str(e)}'}]


async def get_shards_tool(args: GetShardsArgs) -> list[dict]:
    try:
        check_tool_compatibility('GetShardsTool', args)
        result = get_shards(args)

        if isinstance(result, dict) and 'error' in result:
            return [{'type': 'text', 'text': f'Error getting shards: {result["error"]}'}]
        formatted_text = 'index | shard | prirep | state | docs | store | ip | node\n'

        # Format each shard row
        for shard in result:
            formatted_text += f'{shard["index"]} | '
            formatted_text += f'{shard["shard"]} | '
            formatted_text += f'{shard["prirep"]} | '
            formatted_text += f'{shard["state"]} | '
            formatted_text += f'{shard["docs"]} | '
            formatted_text += f'{shard["store"]} | '
            formatted_text += f'{shard["ip"]} | '
            formatted_text += f'{shard["node"]}\n'

        return [{'type': 'text', 'text': formatted_text}]
    except Exception as e:
        return [{'type': 'text', 'text': f'Error getting shards information: {str(e)}'}]


# Registry of available OpenSearch tools with their metadata  
TOOL_REGISTRY = {
    'ListIndexTool': {
        'description': 'Lists all indices in the OpenSearch cluster',
        'input_schema': ListIndicesArgs.model_json_schema(),
        'function': list_indices_tool,
        'args_model': ListIndicesArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'IndexMappingTool': {
        'description': 'Retrieves index mapping and setting information for an index in OpenSearch',
        'input_schema': GetIndexMappingArgs.model_json_schema(),
        'function': get_index_mapping_tool,
        'args_model': GetIndexMappingArgs,
        'http_methods': 'GET',
    },
    'SearchIndexTool': {
        'description': 'Searches an index using a query written in query domain-specific language (DSL) in OpenSearch',
        'input_schema': SearchIndexArgs.model_json_schema(),
        'function': search_index_tool,
        'args_model': SearchIndexArgs,
        'http_methods': 'GET, POST',
    },
    'GetShardsTool': {
        'description': 'Gets information about shards in OpenSearch',
        'input_schema': GetShardsArgs.model_json_schema(),
        'function': get_shards_tool,
        'args_model': GetShardsArgs,
        'http_methods': 'GET',
    },
    'ClusterHealthTool': {
        'description': 'Returns basic information about the health of the cluster',
        'input_schema': ClusterHealthArgs.model_json_schema(),
        'function': cluster_health_tool,
        'args_model': ClusterHealthArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
    'CountTool': {
        'description': 'Returns number of documents matching a query',
        'input_schema': CountArgs.model_json_schema(),
        'function': count_tool,
        'args_model': CountArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET, POST',
    },
    'ExplainTool': {
        'description': 'Returns information about why a specific document matches (or doesn\'t match) a query',
        'input_schema': ExplainArgs.model_json_schema(),
        'function': explain_tool,
        'args_model': ExplainArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET, POST',
    },
    'MsearchTool': {
        'description': 'Allows to execute several search operations in one request',
        'input_schema': MsearchArgs.model_json_schema(),
        'function': msearch_tool,
        'args_model': MsearchArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET, POST',
    },
    'ConnectionDiagnosticTool': {
        'description': 'Diagnose OpenSearch connection issues and provide detailed troubleshooting information',
        'input_schema': ListIndicesArgs.model_json_schema(),
        'function': connection_diagnostic_tool,
        'args_model': ListIndicesArgs,
        'min_version': '1.0.0',
        'http_methods': 'GET',
    },
}
