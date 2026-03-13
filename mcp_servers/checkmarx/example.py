#!/usr/bin/env python3
"""
Example script demonstrating how to use the Checkmarx MCP Server
"""

import os
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import CheckmarxAgent


def main():
    """Example usage of the Checkmarx Agent"""
    
    print("Checkmarx MCP Server Example")
    print("=" * 80)
    print()
    
    # Get the MCP server path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(script_dir, 'server.py')
    
    # Create agent
    agent = CheckmarxAgent(mcp_server_path)
    
    # Example 1: Get all projects
    print("Example 1: Listing all projects")
    print("-" * 80)
    projects_response = agent.get_projects()
    if projects_response.get('success'):
        projects = projects_response.get('projects', [])
        print(f"Found {len(projects)} projects:")
        for project in projects[:5]:  # Show first 5
            print(f"  - {project.get('name', 'Unknown')}")
    else:
        print(f"Error: {projects_response.get('error')}")
    print()
    
    # Example 2: Get specific project details
    print("Example 2: Get project details")
    print("-" * 80)
    project_name = 'user-access-management'
    project_response = agent.get_project(project_name)
    if project_response.get('success'):
        project = project_response.get('project')
        print(f"Project: {project.get('name')}")
        print(f"ID: {project.get('id')}")
        print(f"Details: {project}")
    else:
        print(f"Error: {project_response.get('error')}")
    print()
    
    # Example 3: Get latest scan report
    print("Example 3: Get latest scan report for user-access-management")
    print("-" * 80)
    report = agent.get_latest_scan_report(project_name)
    formatted_report = agent.format_scan_report(report)
    print(formatted_report)


if __name__ == '__main__':
    # Check if authentication is configured
    if not (os.getenv('CHECKMARX_API_KEY') or 
            (os.getenv('CHECKMARX_CLIENT_ID') and os.getenv('CHECKMARX_CLIENT_SECRET'))):
        print("WARNING: No authentication credentials found!")
        print("Please set one of the following:")
        print("  - CHECKMARX_API_KEY environment variable")
        print("  - CHECKMARX_CLIENT_ID and CHECKMARX_CLIENT_SECRET environment variables")
        print()
        print("Continuing anyway (may result in authentication errors)...")
        print()
    
    main()
