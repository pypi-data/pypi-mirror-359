# Devopness - MCP Server

This is the source code for the Devopness MCP Server - <https://mcp.devopness.com/mcp/>

## Quick Start - Connect to Production Server

The easiest way to get started is to connect directly to our hosted MCP server.

### AI-Powered IDEs (Cursor, VSCode, Windsurf, etc.)

Add the Devopness MCP server to your IDE's configuration file:

**Cursor (~/.cursor/mcp.json)**:

```json
{
  "devopness": {
    "url": "https://mcp.devopness.com/mcp",
    "headers": {
      "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
      "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
    }
  }
}
```

**VSCode (settings or workspace configuration)**:

```json
{
  "mcp": {
    "servers": {
      "devopness": {
        "type": "http",
        "url": "https://mcp.devopness.com/mcp/",
        "headers": {
          "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
          "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
        }
      }
    }
  }
}
```

**Other MCP Clients**:

```yaml
URL: https://mcp.devopness.com/mcp/

Headers:
  Devopness-User-Email: YOUR_DEVOPNESS_USER_EMAIL
  Devopness-User-Password: YOUR_DEVOPNESS_USER_PASSWORD
```

## Development & Testing

### Local Development (Recommended: STDIO)

#### Run from source with STDIO transport

```shell
uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --transport stdio
```

#### AI-Powered IDEs Configuration for Local Development

**Cursor (~/.cursor/mcp.json)**:

```json
{
  "devopness": {
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/full/path/to/devopness-ai/mcp-server",
      "devopness-mcp-server",
      "--transport",
      "stdio"
    ],
    "env": {
      "DEVOPNESS_USER_EMAIL": "YOUR_DEVOPNESS_USER_EMAIL",
      "DEVOPNESS_USER_PASSWORD": "YOUR_DEVOPNESS_USER_PASSWORD"
    }
  }
}
```

### Local Development (HTTP Server Mode)

For testing HTTP connections locally, you can run the server in HTTP mode:

#### Run local HTTP server

```shell
uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --host localhost --port 8000
```

Then connect using:

```yaml
URL: http://localhost:8000/

Headers:
  Devopness-User-Email: YOUR_DEVOPNESS_USER_EMAIL
  Devopness-User-Password: YOUR_DEVOPNESS_USER_PASSWORD
```

### Testing and Debugging

#### Run with MCP Inspector

```shell
npx @alpic-ai/grizzly uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --transport stdio
```

#### Run on Postman

Follow Postman guide to [create an MCP Request](https://learning.postman.com/docs/postman-ai-agent-builder/mcp-requests/create/)

* Choose `STDIO`
* Use the server command:

```shell
uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --transport stdio
```

## Transport Options Summary

* **Remote (Production)**: Use `https://mcp.devopness.com/mcp/` - easiest for end users
* **Local STDIO**: Use `--transport stdio` - recommended for development
* **Local HTTP**: Use `--host localhost --port 8000` - for testing HTTP connections locally

## Environment Variables

Set your Devopness credentials using:

* `DEVOPNESS_USER_EMAIL`: Your Devopness account email
* `DEVOPNESS_USER_PASSWORD`: Your Devopness account password
