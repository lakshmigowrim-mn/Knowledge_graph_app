#!/usr/bin/env python3
"""
Test suite for Agentic Diagnostic Layer
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from diagnostic_layer import (
    ChangelogIntelligence,
    ReachabilityMapper,
    MigrationEffortScorer,
    DiagnosticAgent,
    BreakingChange,
    format_report_markdown
)


def test_changelog_intelligence():
    """Test changelog parsing"""
    print("Testing Changelog Intelligence...")
    print("-" * 80)
    
    intelligence = ChangelogIntelligence()
    
    changelog = """
    ## Version 2.0.0
    
    ### Breaking Changes
    - BREAKING: Removed deprecated `old_function()` function. Use `new_function()` instead.
    - ⚠️ The `OldClass` has been renamed to `NewClass`.
    - Deprecated: `parse_data()` is no longer supported.
    """
    
    changes = intelligence.parse_changelog(changelog, "2.0.0")
    
    print(f"Found {len(changes)} breaking changes:")
    for change in changes:
        print(f"  • {change.identifier} ({change.change_type}) - {change.severity} severity")
    
    assert len(changes) > 0, "Should find breaking changes"
    print("✓ Changelog Intelligence test passed")
    print()


def test_version_delta():
    """Test version delta calculation"""
    print("Testing Version Delta Calculation...")
    print("-" * 80)
    
    scorer = MigrationEffortScorer()
    
    test_cases = [
        ("1.0.0", "1.0.1", 1),    # Patch update
        ("1.0.0", "1.1.0", 10),   # Minor update
        ("1.0.0", "2.0.0", 100),  # Major update
        ("1.2.3", "2.5.7", 134),  # Complex update
    ]
    
    for current, target, expected in test_cases:
        delta = scorer.calculate_version_delta(current, target)
        print(f"  {current} → {target}: delta = {delta} (expected ~{expected})")
        assert delta == expected, f"Version delta mismatch: {delta} != {expected}"
    
    print("✓ Version Delta test passed")
    print()


def test_migration_scoring():
    """Test migration effort scoring"""
    print("Testing Migration Effort Scoring...")
    print("-" * 80)
    
    scorer = MigrationEffortScorer()
    
    # Create mock data
    breaking_changes = [
        BreakingChange("func1", "function", "Removed function", "2.0.0", "high"),
        BreakingChange("Class1", "class", "Renamed class", "2.0.0", "medium"),
    ]
    
    from diagnostic_layer import CodeImpact
    code_impacts = [
        CodeImpact(breaking_changes[0], ["file1.py", "file2.py"], 5, True),
    ]
    
    score = scorer.calculate_score(10.0, code_impacts, breaking_changes)
    
    print(f"  Score: {score.score}/100")
    print(f"  Risk Level: {score.risk_level}")
    print(f"  Estimated Hours: {score.estimated_hours}")
    print(f"  Version Delta: {score.version_delta}")
    print(f"  Code Impacts: {score.code_impact_count}")
    
    assert 1 <= score.score <= 100, "Score should be between 1 and 100"
    assert score.risk_level in ['low', 'medium', 'high', 'critical']
    print("✓ Migration Scoring test passed")
    print()


def test_diagnostic_agent():
    """Test complete diagnostic agent workflow"""
    print("Testing Complete Diagnostic Agent...")
    print("-" * 80)
    
    # Use current directory as project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    agent = DiagnosticAgent(project_root)
    
    # Run analysis
    report = agent.analyze_dependency_upgrade(
        dependency_name="test-package",
        current_version="1.0.0",
        target_version="2.0.0"
    )
    
    print(f"  Dependency: {report.dependency_name}")
    print(f"  Version: {report.current_version} → {report.target_version}")
    print(f"  Breaking Changes: {len(report.breaking_changes)}")
    print(f"  Code Impacts: {len(report.code_impacts)}")
    print(f"  Migration Score: {report.migration_score.score}/100")
    print(f"  Risk Level: {report.migration_score.risk_level}")
    
    assert report.dependency_name == "test-package"
    assert report.migration_score.score > 0
    print("✓ Diagnostic Agent test passed")
    print()


def test_markdown_formatting():
    """Test markdown report formatting"""
    print("Testing Markdown Report Formatting...")
    print("-" * 80)
    
    # Create a mock report
    from diagnostic_layer import DiagnosticReport, MigrationScore
    
    report = DiagnosticReport(
        dependency_name="test-lib",
        current_version="1.0.0",
        target_version="2.0.0",
        breaking_changes=[],
        code_impacts=[],
        migration_score=MigrationScore(
            score=42,
            version_delta=10.0,
            code_impact_count=5,
            breaking_changes_count=2,
            risk_level='medium',
            estimated_hours=5.5
        ),
        recommendations=["Test recommendation"],
        generated_at="2026-03-13T07:00:00"
    )
    
    markdown = format_report_markdown(report)
    
    assert "test-lib" in markdown
    assert "42/100" in markdown
    assert "MEDIUM RISK" in markdown
    
    print("  Generated markdown report (first 500 chars):")
    print("  " + markdown[:500].replace("\n", "\n  "))
    print("  ...")
    
    print("✓ Markdown Formatting test passed")
    print()


def run_integration_test():
    """Run a full integration test"""
    print("\n" + "=" * 80)
    print("INTEGRATION TEST - Full Diagnostic Workflow")
    print("=" * 80)
    print()
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    agent = DiagnosticAgent(project_root)
    
    # Simulate scan results
    mock_scan = {
        'success': True,
        'results': {
            'vulnerabilities': [
                {
                    'dependency': 'flask',
                    'current_version': '1.1.2',
                    'fixed_version': '2.3.0'
                }
            ]
        }
    }
    
    print("Analyzing mock scan results...")
    reports = agent.analyze_scan_results(mock_scan)
    
    print(f"Generated {len(reports)} diagnostic report(s)")
    
    for report in reports:
        print()
        print(f"Report for: {report.dependency_name}")
        print(f"  Score: {report.migration_score.score}/100")
        print(f"  Risk: {report.migration_score.risk_level}")
        print(f"  Effort: {report.migration_score.estimated_hours} hours")
        print(f"  Recommendations: {len(report.recommendations)}")
    
    print()
    print("✓ Integration test passed")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("AGENTIC DIAGNOSTIC LAYER - TEST SUITE")
    print("=" * 80)
    print()
    
    try:
        test_changelog_intelligence()
        test_version_delta()
        test_migration_scoring()
        test_diagnostic_agent()
        test_markdown_formatting()
        run_integration_test()
        
        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print()
        
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
