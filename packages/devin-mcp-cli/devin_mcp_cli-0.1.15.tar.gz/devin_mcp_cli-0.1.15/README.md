# mcp-cli

Model Context Protocol Command Line Interface (MCP CLI)

A CLI for interacting with Model Context Protocol (MCP) servers. Allows listing and execution of tools, reading resources, and managing server configurations.

---

## 🌟 Features

- List available MCP servers defined in a JSON configuration file.
- Inspect and list available tools on an MCP server.
- Execute tools on MCP servers with JSON-formatted inputs.
- Read resources from MCP servers by URI.
- **Automatic OAuth 2.1 authentication** - connects to OAuth-protected servers without configuration.
- Support for environment variable expansion and `.env` files.
- Rich, colored output powered by Rich and Typer.

## 📋 Prerequisites

- Python 3.11 or higher
- uv

## 🚀 Installation

### Pre-built Binaries (Recommended)

#### Automated Installation Script

The easiest way to download the correct binary for your platform:

```bash
# Install latest release (default)
./download_binary.sh

# Or install to a custom location
./download_binary.sh -o /usr/local/bin/mcp-cli

# Or get the latest development build
./download_binary.sh --main
```

**Options:**
- `--release` - Download latest release (default)
- `--main` - Download latest development build from main branch
- `-o, --output PATH` - Save binary to custom location
- `-h, --help` - Show help message

#### Manual Installation (curl)

Alternatively, download manually for your specific platform:

#### Latest Release

**Linux (x64):**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/latest/mcp-cli-linux-x64 -o mcp-cli && chmod +x mcp-cli
```

**Linux (ARM64):**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/latest/mcp-cli-linux-arm64 -o mcp-cli && chmod +x mcp-cli
```

**macOS (Intel):**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/latest/mcp-cli-macos-x64 -o mcp-cli && chmod +x mcp-cli
```

**macOS (Apple Silicon):**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/latest/mcp-cli-macos-arm64 -o mcp-cli && chmod +x mcp-cli
```

#### Main Branch (Development Builds)

For the latest development builds from the main branch:

**Linux:**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/main-latest/mcp-cli-linux -o mcp-cli && chmod +x mcp-cli
```

**macOS:**
```bash
curl -L https://cognition-public.s3.amazonaws.com/mcp-cli/main-latest/mcp-cli-macos -o mcp-cli && chmod +x mcp-cli
```

### From Source

```bash
uv sync --reinstall
```

Run the CLI:

```bash
uv run mcp-cli --help
```

## 🧰 Global Options

- `--config`, `-C` <path>: Path to the server configuration file (default: `server_config.json`).
- `--server`, `-s` <name>: Specify the server name when listing or executing tools/resources.


## 🏷️ Available Commands

### Server Commands

- `mcp-cli server list`
  Lists all configured MCP servers.

- `mcp-cli server check`
  Check connectivity to all MCP servers and list their available tools. Displays a nice terminal UI with loading indicators and status indicators.

### Tool Commands

- `mcp-cli tool list --server <server_name>`
  Lists all tools available on the specified server.

- `mcp-cli tool call <tool_name> --server <server_name> [--input '{"key": "value"}']`
  Executes a tool on the specified server. Provide inputs as a JSON string via the `--input` option.

- `mcp-cli tool read <uri> --server <server_name>`
  Reads a resource from the server by its URI.

### Auth Commands

- `mcp-cli auth login <server_name>`
  Authenticate with an OAuth-enabled MCP server.

- `mcp-cli auth logout [server_name]`
  Clear stored OAuth tokens for a specific server or all servers. If no server name is provided, you will be prompted for confirmation before clearing all tokens.

- `mcp-cli auth status`
  Show authentication status for all configured servers.

## ⚙️ Server Configuration

Create a `server_config.json` file in the project root or set the `$MCP_CLI_CONFIG_PATH` environment variable:

```json
{
  "mcpServers": {
    "example-server": {
      "command": "uv",
      "args": ["run", "example_mcp_server.py"],
      "env": {
        "EXAMPLE_API_KEY": "$EXAMPLE_API_KEY"
      }
    },
    "remote-server": {
      "url": "https://api.example.com/mcp/sse"
    }
  }
}
```

Each server entry supports:
- `command`: The command to start the server (for STDIO servers).
- `args`: List of arguments for the command.
- `env`: Environment variables (values can reference host env vars).
- `url`: Server URL for HTTP-based transports.

## ⚙️ Environment Variables

Set the `MCP_CLI_CONFIG_PATH` variable to the path where your config lives, e.g.

- `export MCP_CLI_CONFIG_PATH="$HOME/.mcp/server_config.json"`

Also supports storing environment variables in a separate file, just set `$MCP_CLI_DOTENV_PATH`

- `export MCP_CLI_DOTENV_PATH="$HOME/.mcp/.env"`

## 📚 Examples

List servers:

```bash
mcp-cli server list
```

List tools on a server:

```bash
mcp-cli tool list --server sqlite
```

Execute a tool with JSON input:

```bash
mcp-cli tool call summarize --server sqlite --input '{"text": "Hello world"}'
```

Read a resource by URI:

```bash
mcp-cli tool read https://example.com/resource.txt --server sqlite
```
