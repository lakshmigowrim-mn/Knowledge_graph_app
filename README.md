# Knowledge Graph Application

This repository contains a Knowledge Graph application with Flask backend and additional MCP (Model Context Protocol) servers for various integrations.

## Components

### 1. Knowledge Graph Application (Flask)
Located in `/app` directory.

A Flask-based application for managing and visualizing knowledge graphs with support for:
- Adding relationships between entities
- Querying the graph
- Visualizing graph data
- Uploading data from CSV/JSON files

**Features:**
- RESTful API endpoints for graph operations
- Web interface for graph visualization
- Support for multiple relationship types
- File upload for bulk data import

**Running the app:**
```bash
cd app
python app.py
```

### 2. Checkmarx AST MCP Server
Located in `/mcp_servers/checkmarx` directory.

An MCP server that provides programmatic access to Checkmarx Application Security Testing (AST) platform.

**Features:**
- Get project information from Checkmarx AST
- Retrieve scan results and reports
- Query latest scan status
- Support for OAuth and API key authentication

**Quick Start:**
```bash
cd mcp_servers/checkmarx

# Install dependencies
pip install -r requirements.txt

# Set authentication credentials
export CHECKMARX_API_KEY="your-api-key"
# OR
export CHECKMARX_CLIENT_ID="your-client-id"
export CHECKMARX_CLIENT_SECRET="your-client-secret"

# Run the coding agent to get latest scan report
python agent.py
```

**Example - Get latest scan report for user-access-management project:**
```bash
cd mcp_servers/checkmarx
python agent.py
```

This will:
1. Connect to Checkmarx AST at `https://ast.checkmarx.net`
2. Authenticate using your credentials
3. Retrieve the latest scan for `user-access-management` project
4. Display a formatted report
5. Save the full report to a JSON file

**Available Methods:**
- `get_latest_scan_report` - Get comprehensive scan report for a project
- `get_projects` - List all available projects
- `get_project` - Get details of a specific project

**Running Tests:**
```bash
cd mcp_servers/checkmarx
python test.py
```

## Project Structure

```
.
├── app/                          # Flask knowledge graph application
│   ├── app.py                   # Main Flask application
│   ├── graph_utils.py           # Graph utility functions
│   ├── static/                  # Static assets
│   └── templates/               # HTML templates
├── mcp_servers/                 # MCP servers directory
│   └── checkmarx/              # Checkmarx AST MCP server
│       ├── server.py           # MCP server implementation
│       ├── agent.py            # Coding agent for scan reports
│       ├── config.json         # Server configuration
│       ├── example.py          # Usage examples
│       ├── test.py             # Test suite
│       ├── requirements.txt    # Python dependencies
│       └── README.md           # Detailed documentation
└── add/                        # Additional utilities

```

## Requirements

### Knowledge Graph App
- Python 3.7+
- Flask
- NetworkX
- Matplotlib

### Checkmarx MCP Server
- Python 3.7+
- requests library

## Setup

1. Clone the repository:
```bash
git clone https://github.com/lakshmigowrim-mn/Knowledge_graph_app.git
cd Knowledge_graph_app
```

2. Install dependencies for the component you want to use:

For Knowledge Graph App:
```bash
pip install flask networkx matplotlib
```

For Checkmarx MCP Server:
```bash
cd mcp_servers/checkmarx
pip install -r requirements.txt
```

## Usage Examples

### Knowledge Graph Application

Start the server:
```bash
cd app
python app.py
```

Access the web interface at `http://localhost:5000`

### Checkmarx MCP Server

Get the latest scan report:
```bash
cd mcp_servers/checkmarx
export CHECKMARX_API_KEY="your-api-key"
python agent.py
```

Run examples:
```bash
cd mcp_servers/checkmarx
python example.py
```

## API Documentation

### Knowledge Graph API

See `/app/app.py` for available endpoints:
- `POST /add_relationship` - Add a relationship between entities
- `GET /query?entity=<name>` - Query relationships for an entity
- `GET /query_graph_visualization?entity=<name>` - Get graph visualization
- `POST /upload` - Upload CSV/JSON data

### Checkmarx MCP Server API

See `/mcp_servers/checkmarx/README.md` for detailed API documentation.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
