#!/usr/bin/env python3
"""
Test script for Checkmarx MCP Server
This script tests the MCP server with mock data
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import CheckmarxASTClient, CheckmarxMCPServer
from agent import CheckmarxAgent


def test_checkmarx_client():
    """Test CheckmarxASTClient with mock responses"""
    print("Testing CheckmarxASTClient...")
    print("-" * 80)
    
    # Create client
    client = CheckmarxASTClient(
        base_url="https://ast.checkmarx.net",
        api_key="test-api-key"
    )
    
    # Test authentication
    assert client.authenticate() == True
    print("✓ Authentication successful")
    
    # Test get_headers
    headers = client._get_headers()
    assert 'Authorization' in headers
    assert headers['Authorization'] == 'Bearer test-api-key'
    print("✓ Headers generated correctly")
    
    print()


def test_checkmarx_client_with_mock_api():
    """Test CheckmarxASTClient with mocked API responses"""
    print("Testing CheckmarxASTClient with mocked API...")
    print("-" * 80)
    
    client = CheckmarxASTClient(
        base_url="https://ast.checkmarx.net",
        api_key="test-api-key"
    )
    client.authenticate()
    
    # Mock projects response
    mock_projects = [
        {'id': 'project-1', 'name': 'user-access-management'},
        {'id': 'project-2', 'name': 'api-gateway'}
    ]
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_projects
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        projects = client.get_projects()
        assert len(projects) == 2
        assert projects[0]['name'] == 'user-access-management'
        print("✓ get_projects() works correctly")
    
    # Test get_project_by_name
    with patch.object(client, 'get_projects', return_value=mock_projects):
        project = client.get_project_by_name('user-access-management')
        assert project is not None
        assert project['id'] == 'project-1'
        print("✓ get_project_by_name() works correctly")
    
    # Test get_scans
    mock_scans = {
        'scans': [
            {
                'id': 'scan-123',
                'status': 'Completed',
                'createdAt': '2026-03-13T05:30:00Z'
            }
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_scans
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        scans = client.get_scans('project-1')
        assert len(scans) == 1
        assert scans[0]['id'] == 'scan-123'
        print("✓ get_scans() works correctly")
    
    # Test get_latest_scan_report
    mock_summary = {
        'high': 5,
        'medium': 12,
        'low': 8,
        'info': 3
    }
    
    with patch.object(client, 'get_latest_scan') as mock_latest_scan, \
         patch.object(client, 'get_scan_summary') as mock_scan_summary, \
         patch.object(client, 'get_scan_results') as mock_scan_results:
        
        mock_latest_scan.return_value = {
            'id': 'scan-123',
            'status': 'Completed',
            'createdAt': '2026-03-13T05:30:00Z'
        }
        mock_scan_summary.return_value = mock_summary
        mock_scan_results.return_value = {'vulnerabilities': []}
        
        report = client.get_latest_scan_report('user-access-management')
        assert report['success'] == True
        assert report['project_name'] == 'user-access-management'
        assert report['scan_id'] == 'scan-123'
        assert report['summary'] == mock_summary
        print("✓ get_latest_scan_report() works correctly")
    
    print()


def test_mcp_server():
    """Test CheckmarxMCPServer"""
    print("Testing CheckmarxMCPServer...")
    print("-" * 80)
    
    server = CheckmarxMCPServer()
    
    # Mock the client
    server.client = Mock()
    server.client.get_latest_scan_report = Mock(return_value={
        'success': True,
        'project_name': 'user-access-management',
        'scan_id': 'scan-123'
    })
    server.client.get_projects = Mock(return_value=[
        {'id': 'project-1', 'name': 'user-access-management'}
    ])
    server.client.get_project_by_name = Mock(return_value={
        'id': 'project-1', 
        'name': 'user-access-management'
    })
    
    # Test get_latest_scan_report method
    request = {
        'method': 'get_latest_scan_report',
        'params': {'project_name': 'user-access-management'}
    }
    response = server.handle_request(request)
    assert response['success'] == True
    assert response['project_name'] == 'user-access-management'
    print("✓ handle_request() with get_latest_scan_report works")
    
    # Test get_projects method
    request = {
        'method': 'get_projects',
        'params': {}
    }
    response = server.handle_request(request)
    assert response['success'] == True
    assert 'projects' in response
    print("✓ handle_request() with get_projects works")
    
    # Test get_project method
    request = {
        'method': 'get_project',
        'params': {'project_name': 'user-access-management'}
    }
    response = server.handle_request(request)
    assert response['success'] == True
    assert 'project' in response
    print("✓ handle_request() with get_project works")
    
    # Test unknown method
    request = {
        'method': 'unknown_method',
        'params': {}
    }
    response = server.handle_request(request)
    assert response['success'] == False
    assert 'Unknown method' in response['error']
    print("✓ handle_request() handles unknown methods correctly")
    
    print()


def test_agent():
    """Test CheckmarxAgent"""
    print("Testing CheckmarxAgent...")
    print("-" * 80)
    
    # Create a mock report
    mock_report = {
        'success': True,
        'project_name': 'user-access-management',
        'scan_id': 'scan-abc123',
        'status': 'Completed',
        'created_at': '2026-03-13T05:30:00Z',
        'summary': {
            'high': 5,
            'medium': 12,
            'low': 8,
            'info': 3
        },
        'scan_details': {
            'engine': 'SAST',
            'branch': 'main'
        }
    }
    
    # Create agent (path doesn't matter for this test)
    agent = CheckmarxAgent('/tmp/fake_server.py')
    
    # Test format_scan_report
    formatted = agent.format_scan_report(mock_report)
    assert 'user-access-management' in formatted
    assert 'scan-abc123' in formatted
    assert 'Completed' in formatted
    assert 'high: 5' in formatted or 'high' in formatted
    print("✓ format_scan_report() works correctly")
    
    # Test format_scan_report with error
    error_report = {
        'success': False,
        'error': 'Project not found'
    }
    formatted_error = agent.format_scan_report(error_report)
    assert 'Error' in formatted_error
    assert 'Project not found' in formatted_error
    print("✓ format_scan_report() handles errors correctly")
    
    print()


def run_integration_demo():
    """Run an integration demo with mock data"""
    print("\n" + "=" * 80)
    print("INTEGRATION DEMO - Simulated Checkmarx Scan Report")
    print("=" * 80)
    print()
    
    # Simulate a complete workflow
    print("Scenario: Getting latest scan report for 'user-access-management' project")
    print()
    
    # Mock report data
    report_data = {
        'success': True,
        'project_name': 'user-access-management',
        'scan_id': 'abc123-def456-ghi789',
        'status': 'Completed',
        'created_at': '2026-03-13T05:30:00Z',
        'summary': {
            'high': 5,
            'medium': 12,
            'low': 8,
            'info': 3,
            'total': 28
        },
        'scan_details': {
            'engine': 'SAST',
            'branch': 'main',
            'initiator': 'scheduled',
            'duration': '12m 34s'
        },
        'results': {
            'vulnerabilities': [
                {
                    'severity': 'High',
                    'type': 'SQL Injection',
                    'file': 'src/database/query.py',
                    'line': 45
                },
                {
                    'severity': 'High',
                    'type': 'Cross-Site Scripting (XSS)',
                    'file': 'src/web/templates.py',
                    'line': 127
                },
                {
                    'severity': 'Medium',
                    'type': 'Insecure Random',
                    'file': 'src/auth/token.py',
                    'line': 89
                }
            ]
        }
    }
    
    # Create agent and format report
    agent = CheckmarxAgent('/tmp/fake_server.py')
    formatted_report = agent.format_scan_report(report_data)
    print(formatted_report)
    
    # Save to file
    output_file = 'user-access-management_scan_report_demo.json'
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    print(f"\nDemo report saved to: {output_file}")
    
    print("\n✓ Integration demo completed successfully!")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CHECKMARX MCP SERVER TEST SUITE")
    print("=" * 80)
    print()
    
    try:
        # Run unit tests
        test_checkmarx_client()
        test_checkmarx_client_with_mock_api()
        test_mcp_server()
        test_agent()
        
        # Run integration demo
        run_integration_demo()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print()
        
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
