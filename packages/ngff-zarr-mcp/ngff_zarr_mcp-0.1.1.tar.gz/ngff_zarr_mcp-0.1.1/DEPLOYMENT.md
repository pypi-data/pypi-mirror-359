# Deployment Guide for ngff-zarr-mcp

This guide covers how to deploy and use the ngff-zarr MCP server package.

## Package Distribution

The `ngff-zarr-mcp` package is distributed via PyPI and can be used with various installation methods.

### Built Package Contents

- **Console Script**: `ngff-zarr-mcp` (entry point: `ngff_zarr_mcp.server:main`)
- **Python Package**: `ngff_zarr_mcp` with full MCP server functionality
- **Dependencies**: Automatically manages all required dependencies including ngff-zarr

## Installation Methods

### 1. Using uvx (Recommended for End Users)

`uvx` provides the simplest way to run the MCP server without managing Python environments:

```bash
# Install uvx if not already installed
pip install uvx

# Run the MCP server directly from PyPI
uvx ngff-zarr-mcp
```

**Advantages:**
- ✅ No environment management required
- ✅ Automatic dependency isolation
- ✅ Always uses latest version from PyPI
- ✅ Perfect for production deployments

### 2. Using pip

```bash
# Install globally
pip install ngff-zarr-mcp

# Install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ngff-zarr-mcp

# Run the server
ngff-zarr-mcp
```

### 3. Using pipx

```bash
# Install with pipx for isolated environment
pipx install ngff-zarr-mcp

# Run the server
ngff-zarr-mcp
```

## MCP Client Configuration

### Claude Desktop Configuration

**Using uvx (recommended):**
```json
{
  "mcpServers": {
    "ngff-zarr": {
      "command": "uvx",
      "args": ["ngff-zarr-mcp"]
    }
  }
}
```

**Using direct installation:**
```json
{
  "mcpServers": {
    "ngff-zarr": {
      "command": "ngff-zarr-mcp",
      "args": []
    }
  }
}
```

**Using Python module (development):**
```json
{
  "mcpServers": {
    "ngff-zarr": {
      "command": "python",
      "args": ["-m", "ngff_zarr_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/development/directory"
      }
    }
  }
}
```

### Server-Sent Events (SSE) Transport

For web-based clients or when STDIO isn't suitable:

```json
{
  "mcpServers": {
    "ngff-zarr": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Start the SSE server:
```bash
uvx ngff-zarr-mcp --transport sse --host localhost --port 8000
```

## Command Line Usage

The server supports various command-line options:

```bash
# STDIO transport (default)
uvx ngff-zarr-mcp

# SSE transport
uvx ngff-zarr-mcp --transport sse --host localhost --port 8000

# Help
uvx ngff-zarr-mcp --help
```

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Installation** | `pixi install` + dev environment | `uvx ngff-zarr-mcp` |
| **Updates** | `git pull` + `pixi install` | `uvx --refresh ngff-zarr-mcp` |
| **Dependencies** | Managed by pixi/pyproject.toml | Managed by uvx/PyPI |
| **Configuration** | Local path in PYTHONPATH | Direct uvx command |
| **Isolation** | Project-specific environment | System-wide isolation |

## Publishing to PyPI

For maintainers, to publish a new version:

```bash
# Ensure you're in the development environment
cd mcp/
pixi shell -e dev

# Update version in ngff_zarr_mcp/__about__.py
# Update CHANGELOG.md if present

# Build the package
pixi run -e dev build

# Publish to PyPI (requires authentication)
hatch publish

# Tag the release
git tag v0.1.0
git push origin v0.1.0
```

## Troubleshooting

### Common Issues

1. **uvx not found**: Install with `pip install uvx`
2. **Permission denied**: Ensure uvx is in your PATH
3. **Old version running**: Use `uvx --refresh ngff-zarr-mcp` to update
4. **Dependencies conflict**: uvx automatically handles isolation

### Verification

Test that the installation works:

```bash
# Check if command is available
uvx ngff-zarr-mcp --help

# Test MCP communication (should show JSON-RPC messages)
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}' | uvx ngff-zarr-mcp
```

## Security Considerations

- **uvx isolation**: Provides automatic dependency isolation
- **PyPI trust**: Only install from trusted PyPI packages
- **Version pinning**: Consider pinning to specific versions in production
- **Network access**: Server may need internet access for remote Zarr stores

## Monitoring and Logs

The MCP server communicates via JSON-RPC and logs to stderr:

```bash
# Capture logs when debugging
uvx ngff-zarr-mcp 2>server.log

# Monitor logs in real-time
uvx ngff-zarr-mcp 2>&1 | tee server.log
```
