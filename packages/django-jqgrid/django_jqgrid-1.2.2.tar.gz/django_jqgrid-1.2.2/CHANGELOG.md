# Changelog

All notable changes to django-jqgrid will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-01

### Added
- Comprehensive utility functions module for common operations
- Content type caching to reduce database queries
- Optimized paginator to avoid unnecessary count queries
- Utility functions for jqGrid filter parsing and response building
- Model field information helper functions
- Export value formatting utilities

### Changed
- Optimized GridFilterViewSet queryset with select_related
- Added caching for ContentType lookups in views
- Improved get_tmplgilters method to use cached content types
- Enhanced pagination with OptimizedPaginator class

### Performance
- Reduced database queries through strategic caching
- Added select_related to optimize related field lookups
- Implemented content type caching with 1-hour timeout
- Optimized queryset evaluation in bulk operations

## [1.0.0] - 2024-01-15

### Added
- Initial release of django-jqgrid
- Auto-configuration system for Django models
- Full CRUD support with REST API integration
- Advanced filtering and search capabilities
- Import/Export functionality for Excel and CSV
- Bulk actions support
- Field-level permissions
- Query optimization with automatic select_related/prefetch_related
- Configuration caching for improved performance
- Comprehensive template tag system
- Management command for model discovery
- Multi-database support
- Responsive grid layouts
- Custom formatter support
- JavaScript hooks for extensibility
- Extensive configuration options via Django settings
- Field-specific configuration methods
- Permission-based field visibility
- Dynamic model loading
- Custom bulk action handlers
- Theme support (Bootstrap 4/5, jQuery UI)
- Internationalization support

### Security
- CSRF protection enabled by default
- Field-level permission checks
- XSS prevention in formatters