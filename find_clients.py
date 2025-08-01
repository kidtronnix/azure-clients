#!/usr/bin/env python3
"""
Script to find apps with specific scopes from https://entrascopes.com/firstpartyscopes.json
"""

import json
import requests
import argparse
import os
import tempfile
import hashlib
from datetime import datetime, timedelta

from typing import Dict, Any, List


def get_cache_file_path(url: str) -> str:
    """
    Get the cache file path for a given URL.
    
    Args:
        url: The URL to create a cache path for
        
    Returns:
        The full path to the cache file
    """
    # Create a hash of the URL to use as filename
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_dir = os.path.join(tempfile.gettempdir(), "find_foci_client_cache")
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    return os.path.join(cache_dir, f"data_{url_hash}.json")


def is_cache_valid(cache_file: str, max_age_hours: int = 24) -> bool:
    """
    Check if the cache file exists and is not too old.
    
    Args:
        cache_file: Path to the cache file
        max_age_hours: Maximum age in hours before cache is considered stale
        
    Returns:
        True if cache is valid, False otherwise
    """
    if not os.path.exists(cache_file):
        return False
    
    # Check file age
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    max_age = timedelta(hours=max_age_hours)
    
    return datetime.now() - file_time < max_age


def load_json_from_url(url: str, use_cache: bool = True, cache_max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Load JSON data from a URL with optional caching.
    
    Args:
        url (str): The URL to fetch JSON data from
        use_cache (bool): Whether to use caching
        cache_max_age_hours (int): Maximum cache age in hours
        
    Returns:
        Dict[str, Any]: The parsed JSON data
        
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails
        json.JSONDecodeError: If the response is not valid JSON
    """
    cache_file = get_cache_file_path(url) if use_cache else None
    
    # Try to load from cache first
    if use_cache and is_cache_valid(cache_file, cache_max_age_hours):
        try:
            print(f"Loading from cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Cache file corrupted, will re-download: {e}")
            # Continue to download fresh data
    
    # Download fresh data
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Save to cache if enabled
        if use_cache and cache_file:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to cache: {cache_file}")
            except IOError as e:
                print(f"Warning: Could not save to cache: {e}")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        raise


def load_json_from_url_old(url: str) -> Dict[str, Any]:
    """
    Load JSON data from a URL.
    
    Args:
        url (str): The URL to fetch JSON data from
        
    Returns:
        Dict[str, Any]: The parsed JSON data
        
    Raises:
                    # Check if next argument is a scope (not a UUID or URL)
                scope = None
                if i + 1 < len(args.args):
                    next_arg = args.args[i + 1]
                    # If next arg is not a UUID and not a URL, treat it as a scope
                    is_uuid = len(next_arg) == 36 and next_arg.count('-') == 4
                    # More specific URL detection: must have protocol or be a proper domain
                    is_url = ('://' in next_arg) or (next_arg.count('.') >= 1 and any(
                        next_arg.endswith(tld) for tld in ['.com', '.org', '.net', '.gov', '.edu', '.co.uk', '.microsoft.com']
                    )) or next_arg.startswith('http')
                    
                    if not is_uuid and not is_url:
                        scope = next_arg
                        i += 1  # Skip the scope arguments.exceptions.RequestException: If the HTTP request fails
        json.JSONDecodeError: If the response is not valid JSON
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        raise


def create_resource_url_mapping(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Create a mapping from resource UUIDs to their associated URLs.
    
    Args:
        data: The JSON data containing resourceidentifiers
        
    Returns:
        Dict mapping resource UUIDs to lists of URLs
    """
    resource_to_urls = {}
    
    if "resourceidentifiers" not in data:
        return resource_to_urls
    
    resource_identifiers = data["resourceidentifiers"]
    
    # Invert the dictionary: url -> resource_id becomes resource_id -> [urls]
    for url, resource_id in resource_identifiers.items():
        if resource_id not in resource_to_urls:
            resource_to_urls[resource_id] = []
        resource_to_urls[resource_id].append(url)
    
    return resource_to_urls


def create_url_to_resource_mapping(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create a mapping from URLs to their resource UUIDs.
    
    Args:
        data: The JSON data containing resourceidentifiers
        
    Returns:
        Dict mapping URLs to resource UUIDs
    """
    url_to_resource = {}
    
    if "resourceidentifiers" not in data:
        return url_to_resource
    
    resource_identifiers = data["resourceidentifiers"]
    
    # Direct mapping: url -> resource_id
    for url, resource_id in resource_identifiers.items():
        url_to_resource[url] = resource_id
    
    return url_to_resource


def resolve_resource_identifier(identifier: str, url_to_resource_mapping: Dict[str, str]) -> str:
    """
    Resolve a resource identifier (URL or UUID) to a resource UUID.
    
    Args:
        identifier: Either a resource UUID or URL
        url_to_resource_mapping: Mapping from URLs to resource UUIDs
        
    Returns:
        Resource UUID, or the original identifier if no mapping found
    """
    # If it's already a UUID format, return as is
    if identifier and len(identifier) == 36 and identifier.count('-') == 4:
        return identifier
    
    # Try to find exact URL match
    if identifier in url_to_resource_mapping:
        return url_to_resource_mapping[identifier]
    
    # Try to find partial URL match (case insensitive)
    identifier_lower = identifier.lower()
    for url, resource_id in url_to_resource_mapping.items():
        if identifier_lower in url.lower() or url.lower() in identifier_lower:
            return resource_id
    
    # Return original if no match found
    return identifier


def lookup_app_by_id(data: Dict[str, Any], app_id: str) -> Dict[str, Any]:
    """
    Look up an app by its ID.
    
    Args:
        data: The JSON data containing apps
        app_id: The app ID to look up
        
    Returns:
        App data with app_id added, or empty dict if not found
    """
    if "apps" not in data:
        print("Error: 'apps' key not found in JSON data")
        return {}
    
    apps = data["apps"]
    
    if app_id in apps:
        app_data = apps[app_id].copy()
        app_data["app_id"] = app_id
        return app_data
    
    return {}


def lookup_apps_by_name(data: Dict[str, Any], app_name: str, exact_match: bool = False) -> List[Dict[str, Any]]:
    """
    Look up apps by name (supports partial matching by default).
    
    Args:
        data: The JSON data containing apps
        app_name: The app name to search for
        exact_match: Whether to require exact name match
        
    Returns:
        List of matching apps with app_id added
    """
    matching_apps = []
    
    if "apps" not in data:
        print("Error: 'apps' key not found in JSON data")
        return matching_apps
    
    apps = data["apps"]
    search_name = app_name.lower()
    
    for app_id, app_data in apps.items():
        app_display_name = app_data.get("name", "").lower()
        
        if exact_match:
            if app_display_name == search_name:
                result = app_data.copy()
                result["app_id"] = app_id
                matching_apps.append(result)
        else:
            if search_name in app_display_name:
                result = app_data.copy()
                result["app_id"] = app_id
                matching_apps.append(result)
    
    return matching_apps


def find_foci_apps(data: Dict[str, Any], resource_scopes: Dict[str, str], include_other_resources: bool = False, sort_by: str = "highest_permissions", foci_only: bool = False, public_only: bool = False) -> List[Dict[str, Any]]:
    """
    Find apps that have the specified scopes for the given resource IDs.
    
    Args:
        data: The JSON data containing apps
        resource_scopes: Dict mapping resource IDs to their required scopes (None means any scope)
        include_other_resources: Whether to include other resource IDs in output
        sort_by: How to sort the results (highest_permissions, lowest_permissions, highest_resources, lowest_resources, highest_matching, lowest_matching)
        foci_only: Whether to only include FOCI apps
        public_only: Whether to only include public client apps
        
    Returns:
        List of matching app objects with their app IDs
    """
    matching_apps = []
    
    if "apps" not in data:
        print("Error: 'apps' key not found in JSON data")
        return matching_apps
    
    apps = data["apps"]
    
    for app_id, app_data in apps.items():
        # Check FOCI filter if enabled
        if foci_only and not app_data.get("foci", False):
            continue
            
        # Check public client filter if enabled
        if public_only and not app_data.get("public_client", False):
            continue
            
        # Check if app has scopes for ALL of the specified resource IDs
        app_scopes = app_data.get("scopes", {})
        matching_resource_ids = []
        
        # Check each required resource-scope pair
        all_requirements_met = True
        for resource_id, required_scope in resource_scopes.items():
            if resource_id not in app_scopes:
                all_requirements_met = False
                break
                
            # If no specific scope required for this resource, any scope is a match
            if required_scope is None:
                matching_resource_ids.append(resource_id)
            else:
                # Check if the specified scope exists for this resource
                resource_scopes_list = app_scopes[resource_id]
                if required_scope in resource_scopes_list:
                    matching_resource_ids.append(resource_id)
                else:
                    all_requirements_met = False
                    break
        
        # Skip if ALL requirements are not met
        if not all_requirements_met:
            continue
        
        # Create a copy of the app data for output
        app_output = app_data.copy()
        app_output["app_id"] = app_id
        app_output["matching_resource_ids"] = matching_resource_ids
        
        # Filter scopes based on include_other_resources flag
        if not include_other_resources:
            # Only include the matching resource IDs
            filtered_scopes = {}
            for res_id in matching_resource_ids:
                filtered_scopes[res_id] = app_scopes[res_id]
            app_output["scopes"] = filtered_scopes
        
        matching_apps.append(app_output)
    
    # Sort apps based on the sort_by parameter
    def get_sort_key(app):
        scopes_dict = app.get("scopes", {})
        if not scopes_dict:
            return (0, 0, 0)
        
        # Total resources count
        total_resources = len(scopes_dict)
        
        # Total API permissions across all resources
        total_permissions = sum(len(scope_list) for scope_list in scopes_dict.values())
        
        # API permissions for the matching resources
        matching_permissions = sum(len(scopes_dict.get(res_id, [])) for res_id in app.get("matching_resource_ids", []))
        
        return (total_resources, total_permissions, matching_permissions)
    
    # Apply sorting based on sort_by parameter
    if sort_by == "highest_permissions":
        matching_apps.sort(key=lambda app: get_sort_key(app)[1], reverse=True)
    elif sort_by == "lowest_permissions":
        matching_apps.sort(key=lambda app: get_sort_key(app)[1], reverse=False)
    elif sort_by == "highest_resources":
        matching_apps.sort(key=lambda app: get_sort_key(app)[0], reverse=True)
    elif sort_by == "lowest_resources":
        matching_apps.sort(key=lambda app: get_sort_key(app)[0], reverse=False)
    elif sort_by == "highest_matching":
        matching_apps.sort(key=lambda app: get_sort_key(app)[2], reverse=True)
    elif sort_by == "lowest_matching":
        matching_apps.sort(key=lambda app: get_sort_key(app)[2], reverse=False)
    
    return matching_apps


def print_app_info(app: Dict[str, Any], resource_ids: List[str] = None, include_other_resources: bool = True, resource_url_mapping: Dict[str, List[str]] = None, original_resource_inputs: List[str] = None) -> None:
    """Print formatted information about an app."""
    # Calculate counts for display
    scopes_dict = app.get("scopes", {})
    total_resources = len(scopes_dict)
    total_permissions = sum(len(scope_list) for scope_list in scopes_dict.values())
    
    print(f"\nApp ID: {app['app_id']}")
    print(f"Name: {app.get('name', 'N/A')}")
    print(f"FOCI: {app.get('foci', False)}")
    print(f"Public Client: {app.get('public_client', False)}")
    print(f"Result: {app.get('result', 'N/A')}")
    print(f"Summary: {total_resources} resources, {total_permissions} total permissions")
    
    print("Scopes:")
    
    # Get matching resource IDs from the app if available
    matching_resource_ids = app.get("matching_resource_ids", resource_ids or [])
    
    # Create mapping from resource ID to original input
    resource_to_original = {}
    if resource_ids and original_resource_inputs:
        for i, res_id in enumerate(resource_ids):
            if i < len(original_resource_inputs):
                original_input = original_resource_inputs[i]
                # Check if original input was a URL (not a UUID)
                is_url_input = original_input and not (len(original_input) == 36 and original_input.count('-') == 4)
                if is_url_input:
                    resource_to_original[res_id] = original_input
    
    # If specific resource_ids are provided and include_other_resources is False,
    # only show those resources
    if resource_ids and not include_other_resources:
        for res_id in resource_ids:
            if res_id in scopes_dict:
                scopes = scopes_dict[res_id]
                is_matching = res_id in matching_resource_ids
                marker = f" <- MATCHING ({len(scopes)} permissions)" if is_matching else f" ({len(scopes)} permissions)"
                print(f"  {res_id}{marker}:")
                
                # Add URL information based on input type
                if resource_url_mapping and res_id in resource_url_mapping:
                    urls = resource_url_mapping[res_id]
                    if res_id in resource_to_original:
                        # Show only the original URL that was provided
                        print(f"    URL: {resource_to_original[res_id]}")
                    else:
                        # Show all URLs for this resource (UUID input or no original input)
                        print(f"    URLs: {', '.join(urls)}")
                
                for scope in scopes:
                    print(f"    - {scope}")
            else:
                is_matching = res_id in matching_resource_ids
                marker = " <- MATCHING: No permissions found for this resource" if is_matching else ": No permissions found for this resource"
                print(f"  {res_id}{marker}")
    else:
        # Show resources based on context
        if resource_ids and include_other_resources:
            # Show all resources the app has, but mark which ones were searched for
            for res_id, scopes in app.get("scopes", {}).items():
                is_matching = res_id in matching_resource_ids
                is_searched = res_id in resource_ids
                
                if is_matching and is_searched:
                    marker = f" <- MATCHING ({len(scopes)} permissions)"
                elif is_searched:
                    marker = f" <- SEARCHED ({len(scopes)} permissions)"
                else:
                    marker = f" ({len(scopes)} permissions)"
                    
                print(f"  {res_id}{marker}:")
                
                # Add URL information
                if resource_url_mapping and res_id in resource_url_mapping:
                    urls = resource_url_mapping[res_id]
                    if resource_ids and is_searched and res_id in resource_to_original:
                        # Show only the original URL that was provided for searched resources
                        print(f"    URL: {resource_to_original[res_id]}")
                    elif len(urls) == 1:
                        print(f"    URL: {urls[0]}")
                    else:
                        print(f"    URLs: {', '.join(urls)}")
                
                for scope in scopes:
                    print(f"    - {scope}")
        else:
            # No specific resource_ids provided, or single resource mode - show all app resources
            for res_id, scopes in app.get("scopes", {}).items():
                is_matching = res_id in matching_resource_ids
                if is_matching:
                    matching_permissions = len(scopes)
                    marker = f" <- MATCHING ({matching_permissions} permissions)"
                else:
                    marker = f" ({len(scopes)} permissions)"
                print(f"  {res_id}{marker}:")
                
                # Add URL information
                if resource_url_mapping and res_id in resource_url_mapping:
                    urls = resource_url_mapping[res_id]
                    if resource_ids and is_matching and res_id in resource_to_original:
                        # Show only the original URL that was provided for the matching resource
                        print(f"    URL: {resource_to_original[res_id]}")
                    elif len(urls) == 1:
                        print(f"    URL: {urls[0]}")
                    else:
                        print(f"    URLs: {', '.join(urls)}")
                
                for scope in scopes:
                    print(f"    - {scope}")


def main():
    """Main function to process command line arguments and find FOCI apps."""
    parser = argparse.ArgumentParser(
        description="Find apps with specific scopes from entrascopes.com, or lookup apps by ID/name"
    )
    
    # Create mutually exclusive group for lookup modes only
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--lookup-id",
        help="Look up a specific app by its ID"
    )
    mode_group.add_argument(
        "--lookup-name",
        help="Look up apps by name (partial match by default)"
    )
    
    parser.add_argument(
        "args", 
        nargs="*",
        help="Resource IDs/URLs and optional scopes. Format: resource_id [scope] resource_id [scope] ... Or use --resource-scope for explicit resource-scope pairs"
    )
    parser.add_argument(
        "--scope", 
        help="Single scope to match across all resources (deprecated - use resource-scope pairs in positional args)"
    )
    parser.add_argument(
        "--resource-scope",
        nargs=2,
        action="append",
        metavar=("RESOURCE", "SCOPE"),
        help="Specify resource-scope pairs explicitly. Can be used multiple times: --resource-scope resource1 scope1 --resource-scope resource2 scope2"
    )
    parser.add_argument(
        "--other-resources", 
        action="store_true",
        help="Include other resource IDs that the app has scopes for (works with all modes)"
    )
    parser.add_argument(
        "--sort-by",
        choices=["highest_permissions", "lowest_permissions", "highest_resources", "lowest_resources", "highest_matching", "lowest_matching"],
        default="highest_permissions",
        help="Sort results by: highest_permissions (default), lowest_permissions, highest_resources, lowest_resources, highest_matching (matching resource permissions), lowest_matching"
    )
    parser.add_argument(
        "--exact-name",
        action="store_true",
        help="Require exact name match when using --lookup-name"
    )
    parser.add_argument(
        "--foci",
        action="store_true",
        help="Only include FOCI (Family of Client IDs) apps in search results"
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Only include public client apps in search results"
    )
    parser.add_argument(
        "--cache",
        type=int,
        default=24,
        help="Cache age in hours (default: 24). Set to 0 to disable caching"
    )
    
    args = parser.parse_args()
    
    url = "https://entrascopes.com/firstpartyscopes.json"
    
    try:
        print(f"Loading JSON from: {url}")
        data = load_json_from_url(url, use_cache=args.cache > 0, cache_max_age_hours=args.cache)
        
        # Create resource mappings
        resource_url_mapping = create_resource_url_mapping(data)
        url_to_resource_mapping = create_url_to_resource_mapping(data)
        
        # Parse resource-scope pairs from arguments
        resource_scopes = {}
        resolved_resource_ids = []
        original_resource_inputs = []
        
        # Handle --resource-scope flags first
        if args.resource_scope:
            for resource_input, scope in args.resource_scope:
                resolved_resource_id = resolve_resource_identifier(resource_input, url_to_resource_mapping)
                resource_scopes[resolved_resource_id] = scope
                resolved_resource_ids.append(resolved_resource_id)
                original_resource_inputs.append(resource_input)
                if resolved_resource_id != resource_input:
                    print(f"Resolved '{resource_input}' to resource ID: {resolved_resource_id}")
        
        # Handle positional arguments (resource_id [scope] resource_id [scope] ...)
        if args.args:
            i = 0
            while i < len(args.args):
                resource_input = args.args[i]
                resolved_resource_id = resolve_resource_identifier(resource_input, url_to_resource_mapping)
                
                # Check if next argument is a scope (not a UUID or URL)
                scope = None
                if i + 1 < len(args.args):
                    next_arg = args.args[i + 1]
                    # If next arg is not a UUID and not a URL, treat it as a scope
                    is_uuid = len(next_arg) == 36 and next_arg.count('-') == 4
                    # More specific URL detection: must have protocol or be a proper domain
                    is_url = ('://' in next_arg) or (next_arg.count('.') >= 1 and any(
                        next_arg.endswith(tld) for tld in ['.com', '.org', '.net', '.gov', '.edu', '.co.uk', '.microsoft.com']
                    )) or next_arg.startswith('http')
                    
                    if not is_uuid and not is_url:
                        scope = next_arg
                        i += 1  # Skip the scope argument
                
                resource_scopes[resolved_resource_id] = scope
                resolved_resource_ids.append(resolved_resource_id)
                original_resource_inputs.append(resource_input)
                
                if resolved_resource_id != resource_input:
                    print(f"Resolved '{resource_input}' to resource ID: {resolved_resource_id}")
                
                i += 1
        
        # Handle legacy --scope flag for backward compatibility
        if args.scope and resource_scopes:
            # Apply the single scope to all resources that don't have a specific scope
            for resource_id in resource_scopes:
                if resource_scopes[resource_id] is None:
                    resource_scopes[resource_id] = args.scope
        
        # Handle different modes
        if args.lookup_id:
            # App ID lookup mode
            print(f"Looking up app ID: {args.lookup_id}")
            if resolved_resource_ids:
                print(f"Filtering to show only resources: {', '.join(resolved_resource_ids)}")
            print()
            
            app = lookup_app_by_id(data, args.lookup_id)
            if not app:
                print("App not found.")
                return 0
            
            print("App found:")
            print("=" * 50)
            print_app_info(app, resolved_resource_ids, args.other_resources, resource_url_mapping, original_resource_inputs)
            
        elif args.lookup_name:
            # App name lookup mode
            print(f"Looking up apps with name: '{args.lookup_name}' ({'exact' if args.exact_name else 'partial'} match)")
            if resolved_resource_ids:
                print(f"Filtering to show only resources: {', '.join(resolved_resource_ids)}")
            print()
            
            apps = lookup_apps_by_name(data, args.lookup_name, args.exact_name)
            if not apps:
                print("No apps found.")
                return 0
            
            print(f"Found {len(apps)} app(s):")
            print("=" * 50)
            
            for app in apps:
                print_app_info(app, resolved_resource_ids, args.other_resources, resource_url_mapping, original_resource_inputs)
                print("-" * 50)
                
        else:
            # App search mode (original functionality, now supports all apps by default)
            if not resource_scopes:
                print("Error: at least one resource ID is required for app search mode")
                return 1
            
            # Build search description
            search_type = []
            if args.foci:
                search_type.append("FOCI")
            if args.public:
                search_type.append("public")
            if not search_type:
                search_type.append("all")
            
            search_desc = " ".join(search_type) + " apps"
            if len(resolved_resource_ids) == 1:
                print(f"Searching for {search_desc} with resource ID: {resolved_resource_ids[0]}")
            else:
                print(f"Searching for {search_desc} with resource IDs: {', '.join(resolved_resource_ids)}")
            
            # Show resource-scope mappings
            for resource_id, scope in resource_scopes.items():
                if scope:
                    print(f"  {resource_id}: looking for scope '{scope}'")
                else:
                    print(f"  {resource_id}: looking for any scope")
            print()
            
            matching_apps = find_foci_apps(
                data, 
                resource_scopes, 
                args.other_resources,
                args.sort_by,
                args.foci,
                args.public
            )
            
            if not matching_apps:
                print(f"No matching {search_desc} found.")
                return 0
            
            print(f"Found {len(matching_apps)} matching {search_desc}:")
            print("=" * 50)
            
            for app in matching_apps:
                print_app_info(app, resolved_resource_ids, args.other_resources, resource_url_mapping, original_resource_inputs)  # Show only matching resources unless --other-resources is specified
                print("-" * 50)
        
    except Exception as e:
        print(f"Failed to process: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())