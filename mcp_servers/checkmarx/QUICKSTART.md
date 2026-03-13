# Checkmarx MCP Server - Quick Start Guide

## Overview
This implementation provides a complete MCP (Model Context Protocol) server for Checkmarx Application Security Testing (AST) platform, specifically configured to work with the Checkmarx instance at `https://ast.checkmarx.net/applicationsAndProjects/`.

## What's Included

### 1. MCP Server (`server.py`)
A full-featured MCP server that connects to Checkmarx AST and provides:
- Project listing and retrieval
- Scan information and status
- Latest scan reports with comprehensive details
- Support for both API Key and OAuth authentication

### 2. Coding Agent (`agent.py`)
A specialized agent designed to retrieve the latest scan report for the `user-access-management` project. Simply run:

```bash
python agent.py
```

This will:
1. Authenticate with Checkmarx AST
2. Find the `user-access-management` project
3. Retrieve the most recent scan
4. Display a formatted report showing:
   - Scan status and metadata
   - Security findings summary (High/Medium/Low/Info)
   - Detailed scan results
5. Save the full report to a JSON file

## Quick Setup

### Step 1: Install Dependencies
```bash
cd mcp_servers/checkmarx
pip install -r requirements.txt
```

### Step 2: Configure Authentication

Choose ONE of the following methods:

**Option A: API Key**
```bash
export CHECKMARX_API_KEY="your-api-key-here"
```

**Option B: OAuth Credentials**
```bash
export CHECKMARX_CLIENT_ID="your-client-id"
export CHECKMARX_CLIENT_SECRET="your-client-secret"
```

### Step 3: Run the Agent
```bash
python agent.py
```

## Example Output

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

RESULTS:
--------------------------------------------------------------------------------
  [Detailed vulnerability findings...]

================================================================================

Full report saved to: user-access-management_scan_report.json
```

## Additional Usage

### Run Examples
```bash
python example.py
```

### Run Tests
```bash
python test.py
```

### Use the MCP Server Directly
```bash
echo '{"method": "get_latest_scan_report", "params": {"project_name": "user-access-management"}}' | python server.py
```

### Query Other Projects
Edit `agent.py` and change the `project_name` variable to query different projects:

```python
project_name = 'your-project-name'  # Change this line
```

## API Methods

The MCP server supports these methods:

1. **get_latest_scan_report**
   - Parameters: `project_name` (required)
   - Returns: Complete scan report with status, summary, and results

2. **get_projects**
   - Parameters: None
   - Returns: List of all available projects

3. **get_project**
   - Parameters: `project_name` (required)
   - Returns: Detailed information about a specific project

## Troubleshooting

### "Authentication failed"
- Verify your API key or OAuth credentials are correct
- Ensure the credentials have proper permissions on Checkmarx AST
- Check network connectivity to `ast.checkmarx.net`

### "Project not found"
- Verify the project name is spelled correctly
- Use `get_projects` method to see all available projects
- Check that you have access to the project

### "No scans found"
- Confirm that scans have been run for the project
- Check the Checkmarx AST web interface for scan history

## Security Notes

⚠️ **Important Security Practices:**
- Never commit API keys or secrets to version control
- Always use environment variables for credentials
- The `.gitignore` file is configured to exclude sensitive files
- Review scan results regularly for security vulnerabilities

## File Structure

```
mcp_servers/checkmarx/
├── server.py           # Main MCP server implementation
├── agent.py            # Coding agent for user-access-management
├── config.json         # Server configuration
├── example.py          # Usage examples
├── test.py            # Test suite
├── requirements.txt    # Python dependencies
├── __init__.py        # Package initialization
└── README.md          # Detailed documentation
```

## Next Steps

1. Configure your Checkmarx credentials
2. Run `python test.py` to verify the setup
3. Run `python agent.py` to get your first scan report
4. Customize the agent for your specific needs
5. Integrate with your CI/CD pipeline

## Support

For detailed API documentation, see `README.md` in the same directory.

For issues and questions, please open an issue on GitHub.
