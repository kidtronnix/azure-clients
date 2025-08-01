# Entra Scopes Finder

A powerful CLI tool for finding Azure first party clients with pre-consented scopes to the resources you require. Perfect for red team operations, security assessments, and Azure application analysis.

Data from: [entrascopes.com](https://entrascopes.com/firstpartyscopes.json).

Credits:
  - @f-bader for publishing entrascopes.com
  - @dirkjanm for publishing ROADtools (used heavily) and entrascopes.com contributor

```bash
# look for a public app with two seperate scopes
entra-scopes-finder https://graph.microsoft.com "Policy.Read.All" https://management.azure.com "user_impersonation" --public  
```

## Features

- **Multi-mode Search**: Search apps by scopes, lookup by app ID, or find by name
- **URL Resolution**: Use resource URLs or UUIDs interchangeably 
- **Multi-resource Support**: Search across multiple resources with resource-specific scopes
- **Flexible Sorting**: Sort results by permissions count, resource count, or matching criteria
- **Advanced Filtering**: Filter by FOCI (Family of Client IDs) or public client apps
- **Rich Output**: Detailed app information with permission counts and URL mappings

## Installation

### From PyPI (Recommended)
```bash
pip install entra-scopes-finder
```

### From Source
```bash
# Clone the repository
git clone https://github.com/kidtronnix/entra-scopes-finder.git
cd entra-scopes-finder

# Install in development mode
pip install -e .

# Or install directly
pip install .
```

### Verify Installation
```bash
# Check if the tool is installed
entra-scopes-finder --help

# Or use the short alias
esf --help
```

## Quick Start

```bash
# Find apps with User.Read permission for Microsoft Graph
esf https://graph.microsoft.com User.Read

# Find all Microsoft Teams related apps
esf --lookup-name "Teams"

# Find public client apps with specific scopes
esf https://graph.microsoft.com User.Read --public

# Use for quick searches
esf --lookup-name "PowerBI"
```

## Usage

### Basic Syntax
```bash
esf [OPTIONS] [RESOURCE_ID/URL [SCOPE]] [RESOURCE_ID/URL [SCOPE]] ...
```

## Operation Modes

### 1. Scope Search (Default Mode)
Find apps that have specific scopes for given resources.

```bash
# Find apps with User.Read scope for Microsoft Graph
esf https://graph.microsoft.com User.Read

# Find public and foci clients
esf https://graph.microsoft.com User.Read --public --foci

# Find apps with any scope for a resource (using UUID)
esf 00000003-0000-0000-c000-000000000000 

# Multi-resource search with different scopes
esf https://graph.microsoft.com User.Read https://management.azure.com user_impersonation
```

### 2. App Lookup

Look up a specific app by its application ID.

```bash
# Lookup specific app
esf --lookup-id "12345678-1234-1234-1234-123456789012"

# Lookup app and filter to specific resource
esf --lookup-id "12345678-1234-1234-1234-123456789012" https://graph.microsoft.com
```
Search for apps by name (supports partial matching).

```bash
# Partial name search
esf --lookup-name "Teams"

# Exact name match
esf --lookup-name "Microsoft Teams" --exact-name

# Name search with resource filtering
esf --lookup-name "Power" https://graph.microsoft.com
```

## Command Line Options

### Search Filtering
- `--foci`: Only include FOCI (Family of Client IDs) apps
- `--public`: Only include public client apps
- `--other-resources`: Include all resources the app has access to (not just searched ones)

### Resource-Scope Specification
- `--resource-scope RESOURCE SCOPE`: Explicitly specify resource-scope pairs
- `--scope SCOPE`: Apply single scope to all resources (legacy option)

### Sorting Options
- `--sort-by`: Sort results by various criteria
  - `highest_permissions` (default): Most API permissions first
  - `lowest_permissions`: Fewest API permissions first
  - `highest_resources`: Most resources first
  - `lowest_resources`: Fewest resources first

### Caching Control
- `--cache HOURS`: Cache age in hours (default: 24, set to 0 to disable)

### Result Limiting
- `--results NUMBER`: Limit the number of results displayed (default: show all results)

### Name Matching
- `--exact-name`: Require exact name match when using `--lookup-name`

## Examples

### Basic Examples

```bash
# Find all public client apps with any permission to graph.microsoft.com resource 
esf https://graph.microsoft.com --public

# Find FOCI apps with Mail.Read permission
esf https://graph.microsoft.com Mail.Read --foci

# Find public client apps sorted by fewest permissions
esf https://graph.microsoft.com User.Read --public --sort-by lowest_permissions
```

### Multi-Resource Examples

```bash
# Apps that have specific scopes for BOTH resources
esf https://graph.microsoft.com User.Read https://management.azure.com user_impersonation

# Using explicit resource-scope pairs
esf --resource-scope https://graph.microsoft.com User.Read --resource-scope https://management.azure.com user_impersonation

# Mixed URL and UUID with different scopes
esf https://graph.microsoft.com User.Read 00000002-0000-0000-c000-000000000000 Directory.Read.All
```

### Lookup Examples

```bash
# Look up specific app by ID
esf --lookup-id "027bb4ab-fec3-42ba-8850-9d48dc6f0060"

# Search for apps by name
esf --lookup-name "Microsoft Teams"

# Search with resource filtering
esf --lookup-name "Office" https://graph.microsoft.com --other-resources
```

### Advanced Examples

```bash
# Disable caching for fresh data
esf https://graph.microsoft.com User.Read --cache 0

# Limit results to first 5 apps found
esf --lookup-name "Microsoft" --results 5

# Show only the top 3 public client apps with least permissions
esf https://graph.microsoft.com User.Read --public --sort-by lowest_permissions --results 3
```

## Output Format

### App Information Display
Each matching app shows:
- **App ID**: Unique application identifier
- **Name**: Display name of the application
- **FOCI**: Whether it's part of a Family of Client IDs
- **Public Client**: Whether it's a public client application
- **Result**: Status indicator
- **Summary**: Resource count and total permission count

### Scope Information
For each resource, the output shows:
- Resource UUID with matching indicator
- Associated URL(s) for the resource
- List of all scopes/permissions for that resource
- Permission count for easy comparison

### Matching Indicators
- `<- MATCHING`: Resource has the searched scope
- `<- SEARCHED`: Resource was searched but scope not found
- No indicator: Additional resource (when `--other-resources` used)

## Resource URL Support

The script supports various Microsoft resource URLs and automatically resolves them to UUIDs:

- `https://graph.microsoft.com` → Microsoft Graph API
- `https://management.azure.com` → Azure Resource Manager API
- `https://vault.azure.net` → Azure Key Vault API
- And many more...

You can use either the full URL or the resource UUID interchangeably.

## Caching

The script includes intelligent caching to improve performance:

- **Default**: 24-hour cache for downloaded data
- **Location**: System temporary directory (`/tmp` on macOS/Linux, `%TEMP%` on Windows)
- **Cache Key**: MD5 hash of the data source URL
- **Validation**: Automatic cache age checking and fallback to fresh download

### Cache Control
```bash
# Use default 24-hour cache
esf https://graph.microsoft.com User.Read

# Disable caching (always download fresh)
esf https://graph.microsoft.com User.Read --cache 0

# Use 1-week cache
esf https://graph.microsoft.com User.Read --cache 168
```

## Common Use Cases

### Security Auditing
```bash
# Find all apps with high-privilege scopes
esf https://graph.microsoft.com Directory.ReadWrite.All --sort-by highest_permissions

# Find public client apps (potential security risk)
esf https://graph.microsoft.com User.Read --public
```

### App Discovery
```bash
# Find all Microsoft Teams related apps
esf --lookup-name "Teams"

# Find apps that can access both Graph and Azure Management APIs
esf https://graph.microsoft.com https://management.azure.com
```

### Permission Analysis
```bash
# Find apps with minimal permissions
esf https://graph.microsoft.com User.Read --sort-by lowest_permissions

# Analyze specific app's permissions
esf --lookup-id "your-app-id" --other-resources
```

## Error Handling

The script includes robust error handling for:
- Network connectivity issues
- Invalid JSON responses
- Cache file corruption
- Missing or invalid app IDs
- Malformed resource identifiers

## Data Source

The script fetches data from [entrascopes.com](https://entrascopes.com/firstpartyscopes.json), which provides comprehensive information about Microsoft first-party applications and their API permissions.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script's functionality.

## License

This project is provided as-is for educational and administrative purposes. Please ensure compliance with your organization's policies when analyzing application permissions.
