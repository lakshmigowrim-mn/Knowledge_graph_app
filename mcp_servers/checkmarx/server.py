#!/usr/bin/env python3
"""
Checkmarx AST MCP Server
Provides access to Checkmarx Application Security Testing platform
"""

import os
import sys
import json
import logging
from typing import Any, Dict, List, Optional
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CheckmarxASTClient:
    """Client for interacting with Checkmarx AST API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize Checkmarx AST client
        
        Args:
            base_url: Base URL for Checkmarx AST (e.g., https://ast.checkmarx.net)
            api_key: API key for authentication (optional)
            client_id: OAuth client ID (optional)
            client_secret: OAuth client secret (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('CHECKMARX_API_KEY')
        self.client_id = client_id or os.getenv('CHECKMARX_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CHECKMARX_CLIENT_SECRET')
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with Checkmarx AST using OAuth or API key"""
        if self.api_key:
            # Use API key authentication
            self.access_token = self.api_key
            return True
        elif self.client_id and self.client_secret:
            # Use OAuth authentication
            try:
                auth_url = f"{self.base_url}/identity/connect/token"
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'scope': 'ast-api'
                }
                response = requests.post(auth_url, data=data)
                response.raise_for_status()
                self.access_token = response.json()['access_token']
                logger.info("Successfully authenticated with Checkmarx AST")
                return True
            except Exception as e:
                logger.error(f"Authentication failed: {str(e)}")
                return False
        else:
            logger.error("No authentication credentials provided")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of all projects"""
        try:
            url = f"{self.base_url}/api/projects"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    def get_project_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project details by name"""
        projects = self.get_projects()
        for project in projects:
            if project.get('name', '').lower() == project_name.lower():
                return project
        return None
    
    def get_scans(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get scans for a project"""
        try:
            url = f"{self.base_url}/api/scans"
            params = {
                'project-id': project_id,
                'limit': limit,
                'sort': '-created_at'  # Sort by newest first
            }
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json().get('scans', [])
        except Exception as e:
            logger.error(f"Failed to get scans: {str(e)}")
            return []
    
    def get_latest_scan(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get the latest scan for a project by name"""
        # Get project
        project = self.get_project_by_name(project_name)
        if not project:
            logger.error(f"Project '{project_name}' not found")
            return None
        
        project_id = project.get('id')
        if not project_id:
            logger.error(f"Project ID not found for '{project_name}'")
            return None
        
        # Get scans
        scans = self.get_scans(project_id, limit=1)
        if not scans:
            logger.error(f"No scans found for project '{project_name}'")
            return None
        
        return scans[0]
    
    def get_scan_results(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific scan"""
        try:
            url = f"{self.base_url}/api/scans/{scan_id}/results"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get scan results: {str(e)}")
            return None
    
    def get_scan_summary(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of scan results"""
        try:
            url = f"{self.base_url}/api/scans/{scan_id}/summary"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get scan summary: {str(e)}")
            return None
    
    def get_latest_scan_report(self, project_name: str) -> Dict[str, Any]:
        """
        Get comprehensive report of the latest scan for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary containing scan report with details and summary
        """
        # Get latest scan
        latest_scan = self.get_latest_scan(project_name)
        if not latest_scan:
            return {
                'success': False,
                'error': f'No scan found for project: {project_name}'
            }
        
        scan_id = latest_scan.get('id')
        scan_status = latest_scan.get('status')
        created_at = latest_scan.get('createdAt', 'Unknown')
        
        report = {
            'success': True,
            'project_name': project_name,
            'scan_id': scan_id,
            'status': scan_status,
            'created_at': created_at,
            'scan_details': latest_scan
        }
        
        # Get scan summary if scan is completed
        if scan_status == 'Completed':
            summary = self.get_scan_summary(scan_id)
            if summary:
                report['summary'] = summary
            
            # Get detailed results
            results = self.get_scan_results(scan_id)
            if results:
                report['results'] = results
        
        return report


class CheckmarxMCPServer:
    """MCP Server for Checkmarx AST"""
    
    def __init__(self):
        self.base_url = "https://ast.checkmarx.net"
        self.client = None
        
    def initialize(self) -> bool:
        """Initialize the MCP server"""
        try:
            self.client = CheckmarxASTClient(self.base_url)
            if self.client.authenticate():
                logger.info("Checkmarx MCP Server initialized successfully")
                return True
            else:
                logger.error("Failed to authenticate with Checkmarx AST")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {str(e)}")
            return False
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'get_latest_scan_report':
            project_name = params.get('project_name')
            if not project_name:
                return {
                    'success': False,
                    'error': 'project_name parameter is required'
                }
            return self.client.get_latest_scan_report(project_name)
        
        elif method == 'get_projects':
            projects = self.client.get_projects()
            return {
                'success': True,
                'projects': projects
            }
        
        elif method == 'get_project':
            project_name = params.get('project_name')
            if not project_name:
                return {
                    'success': False,
                    'error': 'project_name parameter is required'
                }
            project = self.client.get_project_by_name(project_name)
            if project:
                return {
                    'success': True,
                    'project': project
                }
            else:
                return {
                    'success': False,
                    'error': f'Project not found: {project_name}'
                }
        
        else:
            return {
                'success': False,
                'error': f'Unknown method: {method}'
            }
    
    def run(self):
        """Run the MCP server (stdio mode)"""
        if not self.initialize():
            sys.exit(1)
        
        # Read requests from stdin and write responses to stdout
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error_response = {
                    'success': False,
                    'error': 'Invalid JSON request'
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


def main():
    """Main entry point"""
    server = CheckmarxMCPServer()
    server.run()


if __name__ == '__main__':
    main()
