#!/usr/bin/env python3
"""
Agentic Diagnostic Layer for Checkmarx Scan Results

This module analyzes security scan results and provides intelligent upgrade guidance
by parsing changelogs, checking code reachability, and scoring migration effort.
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BreakingChange:
    """Represents a breaking change identified in release notes"""
    identifier: str  # Function, class, or variable name
    change_type: str  # 'function', 'class', 'variable', 'module'
    description: str
    version_introduced: str
    severity: str  # 'high', 'medium', 'low'


@dataclass
class CodeImpact:
    """Represents the impact of a breaking change on local code"""
    breaking_change: BreakingChange
    found_in_files: List[str]
    occurrence_count: int
    is_reachable: bool


@dataclass
class MigrationScore:
    """Migration effort score and metadata"""
    score: int  # 1-100
    version_delta: float
    code_impact_count: int
    breaking_changes_count: int
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    estimated_hours: float


@dataclass
class DiagnosticReport:
    """Complete diagnostic report for a dependency upgrade"""
    dependency_name: str
    current_version: str
    target_version: str
    breaking_changes: List[BreakingChange]
    code_impacts: List[CodeImpact]
    migration_score: MigrationScore
    recommendations: List[str]
    generated_at: str


class ChangelogIntelligence:
    """Uses LLM-like analysis to extract breaking changes from release notes"""
    
    def __init__(self):
        self.breaking_change_patterns = [
            # Common patterns for breaking changes in changelogs
            r'BREAKING[:\s]+(.+?)(?:\n|$)',
            r'Breaking Change[:\s]+(.+?)(?:\n|$)',
            r'⚠️\s*(.+?)(?:\n|$)',
            r'deprecated[:\s]+(.+?)(?:\n|$)',
            r'removed[:\s]+(.+?)(?:\n|$)',
            r'renamed[:\s]+(.+?)(?:\n|$)',
            r'no longer supported[:\s]+(.+?)(?:\n|$)',
        ]
        
        self.identifier_patterns = [
            r'`([A-Za-z_][A-Za-z0-9_\.]*)`',  # Backtick identifiers
            r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b',  # CamelCase
            r'\b([a-z_][a-z0-9_]+)\(\)',  # function calls
            r'class\s+([A-Z][A-Za-z0-9_]+)',  # class definitions
        ]
    
    def parse_changelog(self, changelog_text: str, version: str) -> List[BreakingChange]:
        """
        Parse changelog text to extract breaking changes
        
        Args:
            changelog_text: Raw changelog or release notes text
            version: Version number for these changes
            
        Returns:
            List of identified breaking changes
        """
        breaking_changes = []
        
        # Find sections that mention breaking changes
        for pattern in self.breaking_change_patterns:
            matches = re.finditer(pattern, changelog_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                description = match.group(1).strip()
                
                # Extract identifiers from the description
                identifiers = self._extract_identifiers(description)
                
                for identifier, change_type in identifiers:
                    severity = self._assess_severity(description)
                    breaking_changes.append(BreakingChange(
                        identifier=identifier,
                        change_type=change_type,
                        description=description,
                        version_introduced=version,
                        severity=severity
                    ))
        
        return breaking_changes
    
    def _extract_identifiers(self, text: str) -> List[Tuple[str, str]]:
        """Extract code identifiers from text"""
        identifiers = []
        
        for pattern in self.identifier_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                identifier = match.group(1)
                change_type = self._infer_type(identifier, text)
                identifiers.append((identifier, change_type))
        
        return identifiers
    
    def _infer_type(self, identifier: str, context: str) -> str:
        """Infer whether identifier is a function, class, or variable"""
        context_lower = context.lower()
        
        if 'class' in context_lower or identifier[0].isupper():
            return 'class'
        elif '()' in context or 'function' in context_lower or 'method' in context_lower:
            return 'function'
        elif 'module' in context_lower or 'package' in context_lower:
            return 'module'
        else:
            return 'variable'
    
    def _assess_severity(self, description: str) -> str:
        """Assess severity based on description keywords"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['critical', 'major', 'removed', 'deleted']):
            return 'high'
        elif any(word in desc_lower for word in ['deprecated', 'changed', 'modified']):
            return 'medium'
        else:
            return 'low'
    
    def analyze_dependency_changelogs(self, dependency: str, current_version: str, 
                                     target_version: str) -> List[BreakingChange]:
        """
        Analyze all changelogs between two versions
        
        In a real implementation, this would fetch release notes from:
        - GitHub releases API
        - PyPI changelog
        - npm registry
        - Package documentation
        
        For now, returns mock data for demonstration
        """
        logger.info(f"Analyzing changelogs for {dependency}: {current_version} -> {target_version}")
        
        # Mock changelog data (in production, fetch from APIs)
        mock_changelog = f"""
        ## Version {target_version}
        
        ### Breaking Changes
        - BREAKING: Removed deprecated `execute_query()` function. Use `run_query()` instead.
        - ⚠️ The `ConfigManager` class has been renamed to `Configuration`.
        - Deprecated: `parse_sql()` is no longer supported. Use `parse_statement()`.
        
        ### Features
        - Added new `QueryBuilder` class for safer SQL construction
        - Improved error handling in database connections
        
        ### Bug Fixes
        - Fixed memory leak in connection pooling
        """
        
        return self.parse_changelog(mock_changelog, target_version)


class ReachabilityMapper:
    """Uses ripgrep to map breaking changes to local codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.src_dirs = self._find_src_directories()
    
    def _find_src_directories(self) -> List[str]:
        """Find source code directories in the project"""
        potential_dirs = ['src', 'app', 'lib', 'core']
        found_dirs = []
        
        for dir_name in potential_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                found_dirs.append(dir_path)
        
        return found_dirs if found_dirs else [self.project_root]
    
    def check_identifier_usage(self, identifier: str) -> Tuple[List[str], int]:
        """
        Use ripgrep to find all occurrences of an identifier in source code
        
        Args:
            identifier: Code identifier to search for
            
        Returns:
            Tuple of (list of files containing identifier, total occurrence count)
        """
        files_with_identifier = []
        total_count = 0
        
        for src_dir in self.src_dirs:
            try:
                # Use ripgrep for fast searching
                result = subprocess.run(
                    ['rg', '--files-with-matches', '--word-regexp', identifier, src_dir],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
                    files_with_identifier.extend(files)
                
                # Count occurrences
                count_result = subprocess.run(
                    ['rg', '--count', '--word-regexp', identifier, src_dir],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if count_result.returncode == 0:
                    for line in count_result.stdout.split('\n'):
                        if ':' in line:
                            count = int(line.split(':')[-1])
                            total_count += count
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout searching for {identifier} in {src_dir}")
            except FileNotFoundError:
                # ripgrep not installed, fall back to grep
                logger.warning("ripgrep not found, using grep as fallback")
                return self._fallback_grep_search(identifier, src_dir)
            except Exception as e:
                logger.error(f"Error searching for {identifier}: {e}")
        
        return files_with_identifier, total_count
    
    def _fallback_grep_search(self, identifier: str, src_dir: str) -> Tuple[List[str], int]:
        """Fallback to grep if ripgrep is not available"""
        try:
            result = subprocess.run(
                ['grep', '-r', '-l', '-w', identifier, src_dir],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            count_result = subprocess.run(
                ['grep', '-r', '-o', '-w', identifier, src_dir],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            count = len(count_result.stdout.split('\n')) if count_result.stdout else 0
            
            return files, count
        except Exception as e:
            logger.error(f"Grep fallback failed: {e}")
            return [], 0
    
    def analyze_breaking_changes(self, breaking_changes: List[BreakingChange]) -> List[CodeImpact]:
        """
        Analyze which breaking changes impact local code
        
        Args:
            breaking_changes: List of breaking changes to check
            
        Returns:
            List of code impacts
        """
        code_impacts = []
        
        for change in breaking_changes:
            files, count = self.check_identifier_usage(change.identifier)
            
            if files:
                impact = CodeImpact(
                    breaking_change=change,
                    found_in_files=files,
                    occurrence_count=count,
                    is_reachable=True
                )
                code_impacts.append(impact)
                logger.info(f"Found {count} occurrences of '{change.identifier}' in {len(files)} files")
        
        return code_impacts


class MigrationEffortScorer:
    """Calculates migration effort score based on version delta and code impact"""
    
    def calculate_version_delta(self, current: str, target: str) -> float:
        """
        Calculate semantic version delta
        
        Returns:
            Float representing version distance (major.minor.patch)
        """
        try:
            # Parse semantic versions
            current_parts = [int(x) for x in current.split('.')[:3]]
            target_parts = [int(x) for x in target.split('.')[:3]]
            
            # Pad to ensure 3 parts
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(target_parts) < 3:
                target_parts.append(0)
            
            # Calculate delta with weights (major * 100, minor * 10, patch * 1)
            delta = (
                (target_parts[0] - current_parts[0]) * 100 +
                (target_parts[1] - current_parts[1]) * 10 +
                (target_parts[2] - current_parts[2])
            )
            
            return max(0, delta)
        except (ValueError, IndexError):
            # If version parsing fails, return moderate delta
            return 10.0
    
    def calculate_score(self, version_delta: float, code_impacts: List[CodeImpact],
                       breaking_changes: List[BreakingChange]) -> MigrationScore:
        """
        Calculate migration effort score (1-100)
        
        Scoring factors:
        - Version delta: larger jumps = higher score
        - Code impact count: more occurrences = higher score
        - Breaking changes: more changes = higher score
        - Severity of changes: high severity = higher score
        
        Args:
            version_delta: Numeric version distance
            code_impacts: List of code impacts
            breaking_changes: List of breaking changes
            
        Returns:
            MigrationScore object
        """
        # Base score from version delta (0-30 points)
        version_score = min(30, version_delta / 2)
        
        # Score from code impacts (0-40 points)
        impact_count = sum(impact.occurrence_count for impact in code_impacts)
        impact_score = min(40, impact_count * 2)
        
        # Score from breaking changes (0-30 points)
        breaking_score = 0
        for change in breaking_changes:
            if change.severity == 'high':
                breaking_score += 10
            elif change.severity == 'medium':
                breaking_score += 5
            else:
                breaking_score += 2
        breaking_score = min(30, breaking_score)
        
        # Total score
        total_score = int(version_score + impact_score + breaking_score)
        total_score = max(1, min(100, total_score))  # Clamp to 1-100
        
        # Determine risk level
        if total_score >= 75:
            risk_level = 'critical'
        elif total_score >= 50:
            risk_level = 'high'
        elif total_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Estimate hours (rough formula)
        estimated_hours = (total_score / 10) + (len(code_impacts) * 0.5)
        
        return MigrationScore(
            score=total_score,
            version_delta=version_delta,
            code_impact_count=impact_count,
            breaking_changes_count=len(breaking_changes),
            risk_level=risk_level,
            estimated_hours=round(estimated_hours, 1)
        )


class DiagnosticAgent:
    """Main diagnostic agent orchestrating the analysis"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.changelog_intelligence = ChangelogIntelligence()
        self.reachability_mapper = ReachabilityMapper(project_root)
        self.effort_scorer = MigrationEffortScorer()
    
    def analyze_dependency_upgrade(self, dependency_name: str, current_version: str,
                                   target_version: str) -> DiagnosticReport:
        """
        Perform complete diagnostic analysis of a dependency upgrade
        
        Args:
            dependency_name: Name of the dependency
            current_version: Current version string
            target_version: Target version string
            
        Returns:
            Complete diagnostic report
        """
        logger.info(f"Starting diagnostic analysis for {dependency_name}")
        logger.info(f"Upgrade path: {current_version} -> {target_version}")
        
        # Step 1: Changelog Intelligence
        logger.info("Step 1: Analyzing changelogs for breaking changes...")
        breaking_changes = self.changelog_intelligence.analyze_dependency_changelogs(
            dependency_name, current_version, target_version
        )
        logger.info(f"Found {len(breaking_changes)} breaking changes")
        
        # Step 2: Reachability Mapping
        logger.info("Step 2: Mapping breaking changes to local codebase...")
        code_impacts = self.reachability_mapper.analyze_breaking_changes(breaking_changes)
        logger.info(f"Found {len(code_impacts)} code impacts")
        
        # Step 3: Migration Effort Scoring
        logger.info("Step 3: Calculating migration effort score...")
        version_delta = self.effort_scorer.calculate_version_delta(current_version, target_version)
        migration_score = self.effort_scorer.calculate_score(
            version_delta, code_impacts, breaking_changes
        )
        logger.info(f"Migration score: {migration_score.score}/100 ({migration_score.risk_level} risk)")
        
        # Step 4: Generate Recommendations
        recommendations = self._generate_recommendations(
            breaking_changes, code_impacts, migration_score
        )
        
        # Create report
        report = DiagnosticReport(
            dependency_name=dependency_name,
            current_version=current_version,
            target_version=target_version,
            breaking_changes=breaking_changes,
            code_impacts=code_impacts,
            migration_score=migration_score,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        return report
    
    def _generate_recommendations(self, breaking_changes: List[BreakingChange],
                                 code_impacts: List[CodeImpact],
                                 migration_score: MigrationScore) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if migration_score.risk_level == 'critical':
            recommendations.append(
                "⚠️ CRITICAL RISK: This upgrade requires significant code changes. "
                "Consider breaking into smaller incremental upgrades."
            )
        elif migration_score.risk_level == 'high':
            recommendations.append(
                "⚠️ HIGH RISK: Extensive testing recommended. "
                "Allocate dedicated sprint for migration."
            )
        
        # Code impact recommendations
        if code_impacts:
            recommendations.append(
                f"📝 Action Required: Update {len(code_impacts)} affected code locations:"
            )
            for impact in code_impacts[:5]:  # Top 5
                change = impact.breaking_change
                recommendations.append(
                    f"  • Replace '{change.identifier}' ({change.change_type}) "
                    f"in {len(impact.found_in_files)} file(s) - {impact.occurrence_count} occurrence(s)"
                )
        
        # Effort estimation
        recommendations.append(
            f"⏱️ Estimated Effort: {migration_score.estimated_hours} hours "
            f"({migration_score.score} migration points)"
        )
        
        # Testing recommendations
        recommendations.append(
            "✅ Testing Strategy:"
        )
        recommendations.append(
            "  • Run full test suite before and after upgrade"
        )
        recommendations.append(
            "  • Add regression tests for modified code paths"
        )
        if migration_score.score > 50:
            recommendations.append(
                "  • Consider canary deployment or feature flags"
            )
        
        return recommendations
    
    def analyze_scan_results(self, scan_report: Dict[str, Any]) -> List[DiagnosticReport]:
        """
        Analyze Checkmarx scan results and generate diagnostic reports
        
        Args:
            scan_report: Checkmarx scan report data
            
        Returns:
            List of diagnostic reports for each affected dependency
        """
        reports = []
        
        # Extract vulnerabilities from scan report
        vulnerabilities = self._extract_vulnerabilities(scan_report)
        
        # Group by dependency
        dependencies = self._group_by_dependency(vulnerabilities)
        
        # Analyze each dependency
        for dep_name, vuln_list in dependencies.items():
            # Determine target version (latest secure version)
            current_version = vuln_list[0].get('current_version', '1.0.0')
            target_version = vuln_list[0].get('fixed_version', '2.0.0')
            
            report = self.analyze_dependency_upgrade(dep_name, current_version, target_version)
            reports.append(report)
        
        return reports
    
    def _extract_vulnerabilities(self, scan_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract vulnerability data from scan report"""
        vulnerabilities = []
        
        # Handle different scan report formats
        if 'results' in scan_report:
            results = scan_report['results']
            if isinstance(results, dict) and 'vulnerabilities' in results:
                vulnerabilities = results['vulnerabilities']
            elif isinstance(results, list):
                vulnerabilities = results
        
        return vulnerabilities
    
    def _group_by_dependency(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, List]:
        """Group vulnerabilities by dependency name"""
        grouped = {}
        
        for vuln in vulnerabilities:
            dep_name = vuln.get('dependency', vuln.get('package', 'unknown'))
            if dep_name not in grouped:
                grouped[dep_name] = []
            grouped[dep_name].append(vuln)
        
        return grouped


def format_report_markdown(report: DiagnosticReport) -> str:
    """Format diagnostic report as markdown"""
    lines = []
    
    lines.append("# 🔍 Dependency Upgrade Diagnostic Report")
    lines.append("")
    lines.append(f"**Dependency:** {report.dependency_name}")
    lines.append(f"**Upgrade Path:** `{report.current_version}` → `{report.target_version}`")
    lines.append(f"**Generated:** {report.generated_at}")
    lines.append("")
    
    # Migration Score
    score = report.migration_score
    risk_emoji = {'low': '✅', 'medium': '⚠️', 'high': '🔴', 'critical': '🚨'}
    lines.append("## Migration Effort Score")
    lines.append("")
    lines.append(f"**Score:** {score.score}/100 {risk_emoji.get(score.risk_level, '⚠️')} {score.risk_level.upper()} RISK")
    lines.append(f"**Estimated Effort:** {score.estimated_hours} hours")
    lines.append(f"**Version Delta:** {score.version_delta}")
    lines.append(f"**Code Impacts:** {score.code_impact_count} occurrences")
    lines.append(f"**Breaking Changes:** {score.breaking_changes_count}")
    lines.append("")
    
    # Breaking Changes
    if report.breaking_changes:
        lines.append("## 🔨 Breaking Changes")
        lines.append("")
        for change in report.breaking_changes:
            severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(change.severity, '⚪')
            lines.append(f"### {severity_icon} {change.identifier} ({change.change_type})")
            lines.append(f"**Severity:** {change.severity.upper()}")
            lines.append(f"**Version:** {change.version_introduced}")
            lines.append(f"**Description:** {change.description}")
            lines.append("")
    
    # Code Impacts
    if report.code_impacts:
        lines.append("## 📍 Code Impact Analysis")
        lines.append("")
        for impact in report.code_impacts:
            lines.append(f"### {impact.breaking_change.identifier}")
            lines.append(f"**Occurrences:** {impact.occurrence_count}")
            lines.append(f"**Affected Files:** {len(impact.found_in_files)}")
            if impact.found_in_files:
                lines.append("**Files:**")
                for file_path in impact.found_in_files[:10]:  # Show first 10
                    lines.append(f"  - `{file_path}`")
                if len(impact.found_in_files) > 10:
                    lines.append(f"  - ... and {len(impact.found_in_files) - 10} more")
            lines.append("")
    
    # Recommendations
    if report.recommendations:
        lines.append("## 💡 Recommendations")
        lines.append("")
        for rec in report.recommendations:
            lines.append(rec)
        lines.append("")
    
    return "\n".join(lines)


def save_report(report: DiagnosticReport, output_dir: str = "."):
    """Save diagnostic report to JSON and markdown files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{report.dependency_name}_{timestamp}"
    
    # Save as JSON
    json_path = os.path.join(output_dir, f"{base_name}_diagnostic.json")
    with open(json_path, 'w') as f:
        # Convert dataclasses to dict
        report_dict = asdict(report)
        json.dump(report_dict, f, indent=2)
    logger.info(f"Saved JSON report to {json_path}")
    
    # Save as markdown
    md_path = os.path.join(output_dir, f"{base_name}_diagnostic.md")
    with open(md_path, 'w') as f:
        f.write(format_report_markdown(report))
    logger.info(f"Saved Markdown report to {md_path}")
    
    return json_path, md_path
