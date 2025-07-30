# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Nanopages is a Django package that generates pages from Markdown and HTML files. It integrates with nanodjango for simple sites and django-distill for static site generation.

**Note**: This project works with an unreleased version of nanodjango.

## Core Architecture

- **`Pages` class** (`django_nanopages/pages.py`): Main URL resolver that discovers and serves pages from a directory. Returns URL patterns for both regular Django and django-distill if available.
- **`Page` view** (`django_nanopages/views.py`): Handles rendering of individual pages, supporting both Markdown (.md) and HTML (.html) files with front matter context parsing.
- **Template system**: Uses `django_nanopages/page.html` for Markdown rendering, direct template rendering for HTML files.

### Key Features
- File discovery: Looks for `.md` and `.html` files, with preference for `.md` when both exist
- Index files: `index.md`/`index.html` serve as directory defaults
- Front matter: Supports YAML, JSON, and simple key:value context parsing
- Integration: Works with nanodjango and django-distill

## Development Commands

### Testing
```bash
pytest
```

### Code Quality
```bash
black .           # Format code
isort .           # Sort imports  
ruff check .      # Lint code
mypy .            # Type checking
```

### Coverage
```bash
pytest --cov=django_nanopages --cov-report=html
```

### Example Usage
Run the example site:
```bash
cd example/
nanodjango run website.py
```

## Package Structure

- `django_nanopages/pages.py` - Main Pages class and URL routing
- `django_nanopages/views.py` - Page view and rendering logic
- `django_nanopages/templates/` - Default page template
- `tests/` - Test suite with Django test settings
- `example/` - Example nanodjango site with sample pages

## Coding Standards

### General
- Always end files with a newline

### Python
- Add basic type hints (`x: str | bool | None`) where types are known
- Don't over-complicate typing with generics unless necessary
- Comments on separate lines before code, not at end of lines
- High-level comments explaining purpose to senior developers
- Group trivial code blocks with single comments
- Docstrings with newlines at start/end, only when adding useful information
- Use Google-style docstrings for complex functions with args/return documentation
- Run `ruff check --fix file.py` and `ruff format file.py` after changes

### JavaScript
- Write modern JS assuming latest browser versions

### CSS  
- Write modern CSS assuming latest browser versions
- Use semantic class names with nested CSS rules
- Target nested elements without extra classes (`.foo > div` vs `.foo-row`)
- Avoid utility classes unless truly necessary
- Use CSS variables for reusable values (sizes, colors)
- Never use inline `style=""` attributes