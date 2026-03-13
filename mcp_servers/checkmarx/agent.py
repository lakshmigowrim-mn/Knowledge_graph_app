#!/usr/bin/env python3
"""
Coding Agent for Checkmarx AST
This agent retrieves the latest scan report for the user-access-management project
"""

import json
import sys
import os
import subprocess
from typing import Dict, Any, Optional


class CheckmarxAgent:
    """Agent to interact with Checkmarx MCP Server"""
    
    def __init__(self, mcp_server_path: str):
        """
        Initialize the Checkmarx agent
        
        Args:
            mcp_server_path: Path to the MCP server script
        """
        self.mcp_server_path = mcp_server_path
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a request to the MCP server
        
        Args:
            method: The method to call on the MCP server
            params: Parameters for the method
            
        Returns:
            Response from the MCP server
        """
        request = {
            'method': method,
            'params': params or {}
        }
        
        try:
            # Start the MCP server process
            process = subprocess.Popen(
                [sys.executable, self.mcp_server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send request and get response
            stdout, stderr = process.communicate(input=json.dumps(request) + '\n', timeout=30)
            
            if stderr:
                print(f"MCP Server stderr: {stderr}", file=sys.stderr)
            
            # Parse response
            response = json.loads(stdout.strip())
            return response
        
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'success': False,
                'error': 'MCP server request timed out'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse MCP server response: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to communicate with MCP server: {str(e)}'
            }
    
    def get_latest_scan_report(self, project_name: str) -> Dict[str, Any]:
        """
        Get the latest scan report for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            Scan report data
        """
        return self.send_request('get_latest_scan_report', {'project_name': project_name})
    
    def get_projects(self) -> Dict[str, Any]:
        """Get list of all projects"""
        return self.send_request('get_projects')
    
    def get_project(self, project_name: str) -> Dict[str, Any]:
        """Get details of a specific project"""
        return self.send_request('get_project', {'project_name': project_name})
    
    def format_scan_report(self, report: Dict[str, Any]) -> str:
        """
        Format scan report for display
        
        Args:
            report: Scan report data
            
        Returns:
            Formatted report string
        """
        if not report.get('success'):
            return f"Error: {report.get('error', 'Unknown error')}"
        
        output = []
        output.append("=" * 80)
        output.append(f"CHECKMARX SCAN REPORT: {report.get('project_name', 'Unknown')}")
        output.append("=" * 80)
        output.append(f"Scan ID: {report.get('scan_id', 'Unknown')}")
        output.append(f"Status: {report.get('status', 'Unknown')}")
        output.append(f"Created At: {report.get('created_at', 'Unknown')}")
        output.append("")
        
        # Display summary if available
        summary = report.get('summary')
        if summary:
            output.append("SUMMARY:")
            output.append("-" * 80)
            if isinstance(summary, dict):
                for key, value in summary.items():
                    output.append(f"  {key}: {value}")
            else:
                output.append(f"  {summary}")
            output.append("")
        
        # Display scan details
        scan_details = report.get('scan_details')
        if scan_details:
            output.append("SCAN DETAILS:")
            output.append("-" * 80)
            if isinstance(scan_details, dict):
                for key, value in scan_details.items():
                    if key not in ['id', 'status', 'createdAt']:  # Skip already shown fields
                        output.append(f"  {key}: {value}")
            output.append("")
        
        # Display results if available
        results = report.get('results')
        if results:
            output.append("RESULTS:")
            output.append("-" * 80)
            if isinstance(results, dict):
                for key, value in results.items():
                    output.append(f"  {key}: {value}")
            elif isinstance(results, list):
                output.append(f"  Total results: {len(results)}")
                for idx, result in enumerate(results[:10], 1):  # Show first 10 results
                    output.append(f"  Result {idx}: {result}")
            output.append("")
        
        output.append("=" * 80)
        return "\n".join(output)


def main():
    """Main entry point for the agent"""
    # Determine the path to the MCP server
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_server_path = os.path.join(script_dir, 'server.py')
    
    # Create agent instance
    agent = CheckmarxAgent(mcp_server_path)
    
    print("Checkmarx Coding Agent")
    print("=" * 80)
    print()
    
    # Get latest scan report for user-access-management project
    project_name = 'user-access-management'
    print(f"Fetching latest scan report for project: {project_name}")
    print()
    
    report = agent.get_latest_scan_report(project_name)
    formatted_report = agent.format_scan_report(report)
    print(formatted_report)
    
    # Optionally save report to file
    output_file = f"{project_name}_scan_report.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to: {output_file}")


if __name__ == '__main__':
    main()
