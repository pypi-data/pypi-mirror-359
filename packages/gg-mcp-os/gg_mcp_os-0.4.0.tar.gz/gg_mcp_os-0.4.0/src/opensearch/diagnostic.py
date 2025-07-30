# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import requests
import json
from typing import Tuple
from urllib.parse import urlparse


def diagnose_connection(opensearch_url: str, username: str = None, password: str = None) -> Tuple[bool, str]:
    """Diagnose OpenSearch connection issues.
    
    Args:
        opensearch_url: The OpenSearch URL to test
        username: Optional username for basic auth
        password: Optional password for basic auth
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Basic URL validation
        if not opensearch_url:
            return False, "OpenSearch URL is not provided"
            
        parsed_url = urlparse(opensearch_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False, f"Invalid OpenSearch URL format: {opensearch_url}"
        
        # Test basic connectivity
        test_url = f"{opensearch_url.rstrip('/')}/"
        headers = {
            'User-Agent': 'OpenSearch-MCP-Server/1.0',
            'Accept': 'application/json'
        }
        
        auth = None
        if username and password:
            auth = (username, password)
            
        # Configure SSL verification
        verify_ssl = os.getenv('OPENSEARCH_SSL_VERIFY', 'true').lower() != 'false'
        
        try:
            response = requests.get(
                test_url, 
                headers=headers, 
                auth=auth, 
                timeout=10,
                verify=verify_ssl
            )
            
            # Check response content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'text/html' in content_type:
                if response.status_code == 200:
                    return False, (
                        f"Server returned HTML instead of JSON (status {response.status_code}). "
                        f"This usually indicates:\n"
                        f"1. Wrong URL - you may be hitting a web interface instead of API\n"
                        f"2. Authentication required - server redirected to login page\n"
                        f"3. Proxy or load balancer issue\n"
                        f"Response content type: {content_type}"
                    )
                else:
                    return False, (
                        f"Server returned HTML error page (status {response.status_code}). "
                        f"Check if the URL is correct and server is accessible."
                    )
            
            if 'application/json' not in content_type:
                return False, (
                    f"Server returned unexpected content type: {content_type}. "
                    f"Expected 'application/json' for OpenSearch API."
                )
                
            # Try to parse JSON response
            try:
                data = response.json()
                
                # Check if it looks like an OpenSearch response
                if isinstance(data, dict):
                    if 'version' in data and 'number' in data.get('version', {}):
                        version = data['version']['number']
                        name = data.get('name', 'Unknown')
                        return True, f"✓ Successfully connected to OpenSearch {version} (node: {name})"
                    elif 'error' in data:
                        error_info = data['error']
                        if isinstance(error_info, dict):
                            error_type = error_info.get('type', 'unknown')
                            error_reason = error_info.get('reason', 'No reason provided')
                            return False, f"OpenSearch error ({error_type}): {error_reason}"
                        else:
                            return False, f"OpenSearch error: {error_info}"
                    else:
                        return False, (
                            f"Server responded with JSON but doesn't look like OpenSearch API. "
                            f"Response keys: {list(data.keys())}"
                        )
                else:
                    return False, "Server returned non-object JSON response"
                    
            except json.JSONDecodeError as e:
                return False, f"Server returned invalid JSON: {str(e)}"
                
        except requests.exceptions.SSLError as e:
            return False, (
                f"SSL/TLS error: {str(e)}\n"
                f"Try setting OPENSEARCH_SSL_VERIFY=false for testing with self-signed certificates"
            )
        except requests.exceptions.ConnectTimeout:
            return False, f"Connection timeout to {opensearch_url}. Check if server is accessible."
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {str(e)}. Check if server is running and accessible."
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP error {e.response.status_code}: {str(e)}"
            
    except Exception as e:
        return False, f"Unexpected error during connection diagnosis: {str(e)}" 