# Changelog

## [1.0.0] - 2025-01-31

### Added
- Initial release as a proper CLI tool
- Package structure with `entra-scopes-finder` and `esf` commands
- Proper Python packaging with setuptools
- Installation via pip
- Comprehensive documentation

### Changed
- Converted from standalone script to installable Python package
- Updated README with new installation and usage instructions

### Features
- 🔍 **Multi-mode Search**: Search apps by scopes, lookup by app ID, or find by name
- 🌐 **URL Resolution**: Use resource URLs or UUIDs interchangeably 
- 🔄 **Multi-resource Support**: Search across multiple resources with resource-specific scopes
- 📊 **Flexible Sorting**: Sort results by permissions count, resource count, or matching criteria
- 🏷️ **Advanced Filtering**: Filter by FOCI (Family of Client IDs) or public client apps
- 📋 **Rich Output**: Detailed app information with permission counts and URL mappings
