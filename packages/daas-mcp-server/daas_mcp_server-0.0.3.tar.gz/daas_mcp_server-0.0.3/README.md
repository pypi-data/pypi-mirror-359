# CVAD Model Context Protocol (MCP) Server

A Model Context Protocol (MCP) server implementation for DaaS that provides AI assistants with the ability to interact with DaaS environments.

## Overview

The DaaS MCP Server extends AI capabilities to Citrix DaaS environments by providing a set of tools that allow AI assistants to interact with your DaaS site.

This server implements the Model Context Protocol (MCP), a standardized way for AI agents to interact with external systems and tools.

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager and installer
- Generate your own [Service Principle](https://developer-docs.citrix.com/en-us/citrix-cloud/citrix-cloud-api-overview/get-started-with-citrix-cloud-apis) to access DaaS API

### Setup

1. Clone the repository
2. Navigate to the project directory:

   ```bash
   cd daas-mcp
   ```

3. Install the package and its dependencies with uv sync:

   ```bash
   uv sync
   ```

## Project Structure

- `src/`: Main package directory
  - `server.py`: MCP server implementation
  - `tools.py`: Tool implementations for interacting with DaaS
  - `constants.py`: Project constants
  - `resources.py`: Resource implementations
  - `utils/`: Utility modules for authentication, logging, etc.

## Usage

### Starting the Server

To start the CVAD MCP Server using uv:

```bash
uv run .\src\server.py
```

The server uses stdio as the transport mechanism.

## Development

### Development Dependencies

Install the development dependencies with uv:

```bash
uv sync --dev
```

### Debug Mode

Navigate to the project directory:

```bash
cd daas-mcp
```

Run the server with inspector mode:

```bash
mcp dev server.py
```

### Code Quality

This project uses Ruff for linting and formatting.

To run the linter:

```bash
uv run ruff check
```

To auto-fix the lint issues:

```bash
uv run ruff check --fix
```

To format the code:

```bash
uv run ruff format
```

## Publishment

```bash
uv pip install build twine
```

```bash
python -m build
```

```bash
python -m twine upload dist/*
```

## Security Considerations

- The server identifies sensitive operations that require special permissions
- Authentication is handled through Citrix Cloud authentication mechanisms
- Token caching is implemented securely

## License

Copyright (c) 2025. Cloud Software Group, Inc. All Rights Reserved. Confidential & Proprietary.
