# Rust Minidump MCP

[![CI](https://github.com/bahamoth/rust-minidump-mcp/workflows/CI/badge.svg)](https://github.com/bahamoth/rust-minidump-mcp/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/rust-minidump-mcp.svg)](https://pypi.org/project/rust-minidump-mcp/)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![uv](https://img.shields.io/badge/uv-package%20manager-yellow)](https://github.com/astral-sh/uv)

An MCP (Model Context Protocol) server that empowers AI agents and developers to understand application crashes. By bridging powerful Rust-based crash analysis tools with AI capabilities, this project transforms cryptic crash dumps into clear, actionable insights - helping you quickly identify root causes and fix critical issues.

## 🚀 Features

- **Minidump Analysis**: Analyze Windows crash dump files (`.dmp`) to get detailed stack traces
- **Symbol Extraction**: Extract Breakpad symbols from binaries (PDB, DWARF formats)
- **Multiple Transport Support**: stdio (default), Streamable HTTP, and SSE transports
- **AI-Powered Analysis**: Built-in prompts for AI-assisted crash debugging
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Comprehensive Error Handling**: Detailed error messages with actionable suggestions

## 📋 Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (optional, for development)

## 🚀 Quick Start

### Method 1: Using uvx (Recommended)

Run directly without installation:

```bash
# Run the server (default: stdio transport)
uvx rust-minidump-mcp server

# Run with HTTP transport for web access
uvx rust-minidump-mcp server --transport streamable-http

# Run the client
uvx rust-minidump-mcp client
```

### Method 2: Using pip

Install from PyPI:

```bash
pip install rust-minidump-mcp
```

### Method 3: Using uv

Add to your project:
```bash
uv add rust-minidump-mcp
```

After installation, run:
```bash
# Server (default: stdio transport for AI agent integration)
rust-minidump-mcp server

# Or use HTTP transport for web access
rust-minidump-mcp server --transport streamable-http --port 8000

# Client
rust-minidump-mcp client
```

## 📚 Usage

### Running the Server

#### STDIO Transport (Default)
```bash
# Default configuration - for AI agent integration (Claude Desktop, VS Code, etc.)
rust-minidump-mcp server

# Explicit specification
rust-minidump-mcp server --transport stdio
```

#### Streamable HTTP Transport
```bash
# For web access and debugging
rust-minidump-mcp server --transport streamable-http

# With custom port
rust-minidump-mcp server --transport streamable-http --port 8080
```

#### SSE Transport
```bash
# For real-time streaming
rust-minidump-mcp server --transport sse --port 9000
```

### Running the Client

The client is a simple testing tool for the MCP server - you typically won't need it unless you're developing or debugging the server.

```bash
# Test the server connection
rust-minidump-mcp client

# See all available commands
rust-minidump-mcp client --help
```

## 📚 MCP Tools

### stackwalk_minidump

Analyzes minidump crash files to produce human-readable stack traces.

**Parameters:**
- `minidump_path` (str, required): Path to the minidump file
- `symbols_path` (str, optional): Path to symbol files or directories
- `output_format` (str, optional): Output format - "json" or "text" (default: "json")

### extract_symbols

Converts debug symbols from native formats (PDB, DWARF) to Breakpad format for use with stackwalk_minidump.

**Parameters:**
- `binary_path` (str, required): Path to the binary file with debug info
- `output_dir` (str, optional): Directory to save converted symbols (default: ./symbols/)

## 🎯 MCP Prompts

The server provides three specialized prompts for comprehensive crash analysis:

### analyze_crash_with_expertise
Expert-level crash analysis with role-based insights:
- Detects programming language from modules/symbols
- Provides concrete code improvement suggestions
- Identifies crash patterns and prevention strategies
- Offers tailored advice based on the technology stack

### analyze_technical_details
Deep technical analysis of crash internals:
- Register state interpretation
- Stack frame pattern analysis
- Memory corruption detection
- Symbol-less frame estimation techniques

### symbol_transformation_guide
Comprehensive guide for symbol preparation:
- Explains Breakpad format requirements
- Documents dump_syms tool usage
- Shows expected directory structure
- Common troubleshooting tips

## 🤖 AI Agent Integration

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rust-minidump-mcp": {
      "command": "uvx",
      "args": ["rust-minidump-mcp", "server"]
    }
  }
}
```

### Claude Code

Claude Code automatically detects MCP servers. After installation:

1. Open Claude Code in your project directory
2. The rust-minidump-mcp server will be available for crash analysis tasks

### VS Code with Continue.dev

Add to your Continue configuration (`~/.continue/config.json`):

```json
{
  "models": [...],
  "mcpServers": {
    "rust-minidump-mcp": {
      "command": "uvx",
      "args": ["rust-minidump-mcp", "server"]
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Server configuration
MINIDUMP_MCP_NAME=my-minidump-server
MINIDUMP_MCP_LOG_LEVEL=INFO
MINIDUMP_MCP_TRANSPORT=streamable-http
MINIDUMP_MCP_STREAMABLE_HTTP__HOST=127.0.0.1
MINIDUMP_MCP_STREAMABLE_HTTP__PORT=8000

# Client configuration
MINIDUMP_MCP_CLIENT_URL=http://localhost:8000/mcp
MINIDUMP_MCP_CLIENT_TRANSPORT=streamable-http
MINIDUMP_MCP_CLIENT_TIMEOUT=30.0
```

### Configuration Priority

1. CLI arguments (highest priority)
2. Environment variables
3. `.env` file
4. Default values (lowest priority)

## 📊 Understanding Crash Analysis

### Minidump Files

Minidump files (`.dmp`) are compact crash reports generated when a Windows application crashes. They contain:
- Thread information and stack traces
- CPU register states
- Loaded module list
- Exception information
- System information

### Symbol Files

Symbol files map memory addresses to human-readable function names and source locations:
- **PDB files**: Windows debug symbols
- **DWARF**: Linux/macOS debug information
- **Breakpad format**: Cross-platform symbol format (`.sym`)


### Symbol Directory Structure

Breakpad symbols follow a specific directory structure:
```
symbols/
└── app.exe/
    └── 1234ABCD5678EF90/  # Module ID
        └── app.exe.sym    # Symbol file
```

## 🛠️ Installation Details

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) command runner (optional)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/bahamoth/rust-minidump-mcp.git
cd rust-minidump-mcp
```

2. Install dependencies:
```bash
uv sync
```

This will automatically create a virtual environment and install all dependencies.

3. Install Rust tools (Optional):

The project includes pre-compiled Rust binaries in `minidumpmcp/tools/bin/`. They are automatically used when running the tools. 

If you need to update or reinstall them:
```bash
just install-tools
```

## 🐛 Troubleshooting

### Common Issues

1. **Binary not found error**
   ```
   Solution: Run 'just install-tools' to install required binaries
   ```

2. **Connection refused error**
   ```
   Solution: Ensure the server is running on the correct port
   Check: rust-minidump-mcp server --transport streamable-http --port 8000
   ```

3. **Invalid minidump format**
   ```
   Solution: Ensure the file is a valid Windows minidump (.dmp) file
   ```

## 🏗️ Architecture

### Project Structure

```
rust-minidump-mcp/
├── minidumpmcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP server entry point
│   ├── cli.py             # Typer-based CLI
│   ├── exceptions.py      # Custom error handling
│   ├── config/
│   │   ├── settings.py    # Server configuration
│   │   └── client_settings.py  # Client configuration
│   ├── tools/
│   │   ├── stackwalk.py   # Minidump analysis tool
│   │   ├── dump_syms.py   # Symbol extraction tool
│   │   └── bin/           # Platform-specific binaries
│   └── prompts/           # AI-assisted debugging prompts
├── tests/                 # Test suite
├── justfile              # Task automation
└── pyproject.toml        # Project configuration
```

### Transport Support

- **stdio**: Standard input/output for CLI integration
- **streamable-http**: Streamable HTTP transport for web services
- **sse**: Server-Sent Events for real-time streaming

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_stackwalk.py

# Run with coverage
pytest --cov=minidumpmcp
```

### Code Quality

```bash
# Lint code
ruff check

# Format code
ruff format

# Type checking
mypy .
```

### Available Commands

See all available commands:
```bash
just --list
```

Common commands:
- `just install-tools`: Install Rust binaries
- `just test`: Run tests
- `just lint`: Run linters
- `just format`: Format code

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [rust-minidump](https://github.com/rust-minidump/rust-minidump): The Rust library powering our analysis tools
- [FastMCP](https://github.com/jlowin/fastmcp): The MCP framework used for server/client implementation
- [Breakpad](https://chromium.googlesource.com/breakpad/breakpad/): The crash reporting system that defines the symbol format