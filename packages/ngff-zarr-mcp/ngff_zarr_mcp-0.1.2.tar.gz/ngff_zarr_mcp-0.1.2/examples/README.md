# ngff-zarr MCP Examples

This directory contains examples and demos for the ngff-zarr Model Context Protocol (MCP) server.

## Configuration Files

- **`claude-desktop-config.json`** - Configuration for integrating with Claude Desktop
- **`sse-config.json`** - Server-sent events configuration

## Demo Scripts

- **`conversion_demo.py`** - Demonstrates the image conversion functionality of the MCP server
  - Shows supported formats and methods
  - Creates a test image and converts it to OME-Zarr
  - Demonstrates various conversion options

- **`structure_demo.py`** - Shows the project structure and available MCP tools
  - Displays the project organization
  - Lists all available MCP tools and their descriptions

## Running the Demos

```bash
# Run the conversion demo
cd mcp/
pixi run python examples/conversion_demo.py

# Run the structure demo
cd mcp/
pixi run python examples/structure_demo.py
```

These demos provide a quick way to understand the capabilities and usage of the ngff-zarr MCP server.
