#!/usr/bin/env python3
"""
Main Orchestrator for Agentic Diagnostic Layer

This script integrates the Checkmarx MCP server with the diagnostic layer
to provide intelligent upgrade guidance for security vulnerabilities.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagnostic_layer import DiagnosticAgent, save_report, format_report_markdown
from mcp_servers.checkmarx.agent import CheckmarxAgent


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Agentic Diagnostic Layer for Checkmarx Scan Analysis'
    )
    parser.add_argument(
        '--project', 
        default='user-access-management',
        help='Checkmarx project name to analyze'
    )
    parser.add_argument(
        '--project-root',
        default=os.getcwd(),
        help='Root directory of the project to analyze'
    )
    parser.add_argument(
        '--output-dir',
        default='diagnostic_reports',
        help='Directory to save diagnostic reports'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🔍 AGENTIC DIAGNOSTIC LAYER")
    print("=" * 80)
    print()
    print("Intelligent Upgrade Guidance System")
    print("Analyzing security scan results with:")
    print("  • Changelog Intelligence (LLM-based breaking change extraction)")
    print("  • Reachability Mapping (ripgrep code impact analysis)")
    print("  • Migration Effort Scoring (1-100 data-driven scoring)")
    print("  • Risk Mitigation (Auditable upgrade recommendations)")
    print()
    print("=" * 80)
    print()
    
    # Step 1: Get latest scan report from Checkmarx
    print("Step 1: Fetching latest Checkmarx scan report...")
    print(f"Project: {args.project}")
    print()
    
    mcp_server_path = str(Path(__file__).parent.parent / 'mcp_servers' / 'checkmarx' / 'server.py')
    checkmarx_agent = CheckmarxAgent(mcp_server_path)
    
    scan_report = checkmarx_agent.get_latest_scan_report(args.project)
    
    if not scan_report.get('success'):
        print(f"❌ Error fetching scan report: {scan_report.get('error', 'Unknown error')}")
        print()
        print("Using mock data for demonstration...")
        scan_report = generate_mock_scan_data()
    else:
        print("✓ Scan report retrieved successfully")
        print()
    
    # Step 2: Initialize Diagnostic Agent
    print("Step 2: Initializing Diagnostic Agent...")
    diagnostic_agent = DiagnosticAgent(args.project_root)
    print(f"Project root: {args.project_root}")
    print(f"Source directories: {diagnostic_agent.reachability_mapper.src_dirs}")
    print()
    
    # Step 3: Analyze scan results
    print("Step 3: Running diagnostic analysis...")
    print()
    
    # Extract vulnerabilities and analyze
    reports = diagnostic_agent.analyze_scan_results(scan_report)
    
    if not reports:
        print("No vulnerabilities found or unable to extract vulnerability data.")
        print("Running sample analysis with mock dependency...")
        print()
        
        # Run sample analysis
        sample_report = diagnostic_agent.analyze_dependency_upgrade(
            dependency_name='flask',
            current_version='1.1.2',
            target_version='2.3.0'
        )
        reports = [sample_report]
    
    # Step 4: Display and save results
    print()
    print("=" * 80)
    print("📊 DIAGNOSTIC RESULTS")
    print("=" * 80)
    print()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    for i, report in enumerate(reports, 1):
        print(f"\n{'-' * 80}")
        print(f"Report {i}/{len(reports)}: {report.dependency_name}")
        print(f"{'-' * 80}\n")
        
        # Display report
        print(format_report_markdown(report))
        
        # Save report
        json_path, md_path = save_report(report, args.output_dir)
        print(f"\n💾 Report saved:")
        print(f"  • JSON: {json_path}")
        print(f"  • Markdown: {md_path}")
    
    # Summary
    print()
    print("=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Dependencies Analyzed: {len(reports)}")
    
    risk_counts = {
        'low': 0,
        'medium': 0,
        'high': 0,
        'critical': 0
    }
    
    total_hours = 0
    total_score = 0
    
    for report in reports:
        risk_level = report.migration_score.risk_level
        risk_counts[risk_level] += 1
        total_hours += report.migration_score.estimated_hours
        total_score += report.migration_score.score
    
    print(f"Risk Levels:")
    print(f"  • Critical: {risk_counts['critical']}")
    print(f"  • High: {risk_counts['high']}")
    print(f"  • Medium: {risk_counts['medium']}")
    print(f"  • Low: {risk_counts['low']}")
    print()
    print(f"Total Estimated Effort: {total_hours:.1f} hours")
    print(f"Average Migration Score: {total_score/len(reports):.1f}/100")
    print()
    
    # Resource planning recommendation
    print("💡 RESOURCE PLANNING RECOMMENDATION:")
    print()
    sprint_points = int(total_hours / 2)  # Rough conversion to story points
    print(f"Recommended Sprint Allocation: {sprint_points} story points")
    print(f"(Based on {total_hours:.1f} hours of estimated migration effort)")
    print()
    
    print("=" * 80)
    print("✅ Analysis Complete!")
    print("=" * 80)


def generate_mock_scan_data() -> dict:
    """Generate mock Checkmarx scan data for demonstration"""
    return {
        'success': True,
        'project_name': 'user-access-management',
        'scan_id': 'mock-scan-123',
        'status': 'Completed',
        'results': {
            'vulnerabilities': [
                {
                    'severity': 'High',
                    'type': 'Dependency Vulnerability',
                    'dependency': 'flask',
                    'current_version': '1.1.2',
                    'fixed_version': '2.3.0',
                    'description': 'Security vulnerability in Flask requiring upgrade'
                },
                {
                    'severity': 'Medium',
                    'type': 'Dependency Vulnerability',
                    'dependency': 'requests',
                    'current_version': '2.25.1',
                    'fixed_version': '2.31.0',
                    'description': 'Multiple security fixes in requests library'
                }
            ]
        }
    }


if __name__ == '__main__':
    main()
