"""
Agentic Diagnostic Layer for Security Scan Analysis

This package provides intelligent upgrade guidance by analyzing security scan results
and providing data-driven migration effort scoring.
"""

from .diagnostic_layer import (
    DiagnosticAgent,
    ChangelogIntelligence,
    ReachabilityMapper,
    MigrationEffortScorer,
    BreakingChange,
    CodeImpact,
    MigrationScore,
    DiagnosticReport,
    format_report_markdown,
    save_report
)

__all__ = [
    'DiagnosticAgent',
    'ChangelogIntelligence',
    'ReachabilityMapper',
    'MigrationEffortScorer',
    'BreakingChange',
    'CodeImpact',
    'MigrationScore',
    'DiagnosticReport',
    'format_report_markdown',
    'save_report'
]

__version__ = '1.0.0'
