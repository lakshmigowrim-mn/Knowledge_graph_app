# Checkmarx AST MCP Server

This directory contains the Model Context Protocol (MCP) server for Checkmarx Application Security Testing (AST) platform.

## Overview

The Checkmarx MCP Server provides programmatic access to Checkmarx AST API, allowing you to:
- Retrieve project information
- Get scan results
- Generate security reports
- Monitor application security status

## Files

- **server.py**: The MCP server implementation that interfaces with Checkmarx AST API
- **agent.py**: A coding agent that uses the MCP server to retrieve scan reports
- **config.json**: Configuration file for the MCP server
- **README.md**: This file

## Setup

### Prerequisites

- Python 3.7 or higher
- `requests` library

Install dependencies:
```bash
pip install requests
```

### Configuration

The MCP server supports two authentication methods:

#### Option 1: API Key Authentication
Set the environment variable:
```bash
export CHECKMARX_API_KEY="your-api-key-here"
```

#### Option 2: OAuth Client Credentials
Set the environment variables:
```bash
export CHECKMARX_CLIENT_ID="your-client-id"
export CHECKMARX_CLIENT_SECRET="your-client-secret"
```

## Usage

### Using the Coding Agent

To get the latest scan report for the `user-access-management` project:

```bash
python agent.py
```

The agent will:
1. Connect to the Checkmarx AST platform
2. Retrieve the latest scan for the `user-access-management` project
3. Display a formatted report
4. Save the full report to a JSON file

### Using the MCP Server Directly

The MCP server runs in stdio mode and accepts JSON requests:

```bash
echo '{"method": "get_latest_scan_report", "params": {"project_name": "user-access-management"}}' | python server.py
```

### Available Methods

#### get_latest_scan_report
Get the latest scan report for a project.

**Request:**
```json
{
  "method": "get_latest_scan_report",
  "params": {
    "project_name": "user-access-management"
  }
}
```

**Response:**
```json
{
  "success": true,
  "project_name": "user-access-management",
  "scan_id": "scan-12345",
  "status": "Completed",
  "created_at": "2026-03-13T07:30:00Z",
  "scan_details": { ... },
  "summary": { ... },
  "results": { ... }
}
```

#### get_projects
Get list of all projects.

**Request:**
```json
{
  "method": "get_projects",
  "params": {}
}
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "id": "project-1",
      "name": "user-access-management",
      ...
    }
  ]
}
```

#### get_project
Get details of a specific project.

**Request:**
```json
{
  "method": "get_project",
  "params": {
    "project_name": "user-access-management"
  }
}
```

**Response:**
```json
{
  "success": true,
  "project": {
    "id": "project-1",
    "name": "user-access-management",
    ...
  }
}
```

## API Endpoints

The MCP server connects to the following Checkmarx AST endpoints:

- **Base URL**: `https://ast.checkmarx.net`
- **Authentication**: `/identity/connect/token`
- **Projects**: `/api/projects`
- **Scans**: `/api/scans`
- **Scan Results**: `/api/scans/{scan_id}/results`
- **Scan Summary**: `/api/scans/{scan_id}/summary`

## Example Output

When you run the agent, you'll see output like:

```
Checkmarx Coding Agent
================================================================================

Fetching latest scan report for project: user-access-management

================================================================================
CHECKMARX SCAN REPORT: user-access-management
================================================================================
Scan ID: abc123-def456-ghi789
Status: Completed
Created At: 2026-03-13T05:30:00Z

SUMMARY:
--------------------------------------------------------------------------------
  High: 5
  Medium: 12
  Low: 8
  Info: 3

SCAN DETAILS:
--------------------------------------------------------------------------------
  engine: SAST
  branch: main
  initiator: scheduled

================================================================================

Full report saved to: user-access-management_scan_report.json
```

## Security Notes

- Never commit API keys or secrets to version control
- Use environment variables for sensitive credentials
- Ensure proper access controls on the Checkmarx platform
- Review scan results regularly

## Troubleshooting

### Authentication Failed
- Verify your API key or client credentials are correct
- Check that the credentials have proper permissions
- Ensure network connectivity to `ast.checkmarx.net`

### Project Not Found
- Verify the project name is correct (case-insensitive)
- Check that you have access to the project
- List all projects using the `get_projects` method

### No Scans Found
- Confirm that scans have been run for the project
- Check the scan status in the Checkmarx AST web interface

## License

This MCP server is part of the Knowledge Graph Application project.
