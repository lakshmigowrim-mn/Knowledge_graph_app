# Agentic Diagnostic Layer

An intelligent diagnostic system that sits between security scans and developers, providing data-driven upgrade guidance.

## Overview

The Agentic Diagnostic Layer analyzes Checkmarx security scan results and transforms them into actionable intelligence by:

1. **Changelog Intelligence**: Uses LLM-like analysis to parse release notes and extract breaking changes (functions, classes, variables)
2. **Reachability Mapping**: Runs high-speed local analysis (ripgrep) to check if breaking identifiers exist in `/src`
3. **Migration Effort Scoring**: Generates a 1-100 score based on Version Delta and Local Code Impact
4. **Risk Mitigation**: Replaces "Blind Upgrades" with Auditable Upgrades
5. **Resource Optimization**: Provides accurate effort estimation for sprint planning

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Checkmarx AST Scan                         │
│            (via MCP Server @ .vscode/mcp.json)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Agentic Diagnostic Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Changelog Intelligence                          │    │
│  │     • Parse release notes                           │    │
│  │     • Extract breaking changes                      │    │
│  │     • Identify affected identifiers                 │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Reachability Mapping (ripgrep)                  │    │
│  │     • Search /src for identifiers                   │    │
│  │     • Count occurrences                             │    │
│  │     • Map to affected files                         │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Migration Effort Scoring                        │    │
│  │     • Calculate version delta                       │    │
│  │     • Weight code impacts                           │    │
│  │     • Assess breaking changes                       │    │
│  │     • Generate 1-100 score                          │    │
│  └────────────────────────────────────────────────────┘    │
│                       │                                      │
│                       ▼                                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Recommendation Engine                           │    │
│  │     • Risk assessment                               │    │
│  │     • Effort estimation (hours)                     │    │
│  │     • Testing strategy                              │    │
│  │     • Sprint point allocation                       │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             Diagnostic Reports (JSON + Markdown)            │
│  • Breaking changes with severity                           │
│  • Code impact analysis with file locations                 │
│  • Migration score (1-100) and risk level                   │
│  • Actionable recommendations                               │
│  • Resource planning guidance                               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install ripgrep for fast code searching (recommended)
# Ubuntu/Debian:
sudo apt-get install ripgrep

# macOS:
brew install ripgrep

# Windows:
choco install ripgrep
```

## Configuration

### 1. VSCode MCP Configuration

The `.vscode/mcp.json` file configures the Checkmarx MCP server:

```json
{
  "mcpServers": {
    "checkmarx-ast": {
      "command": "python",
      "args": ["mcp_servers/checkmarx/server.py"],
      "env": {
        "CHECKMARX_API_KEY": "${env:CHECKMARX_API_KEY}"
      },
      "description": "Checkmarx AST MCP Server"
    }
  }
}
```

### 2. Environment Variables

Set your Checkmarx credentials:

```bash
export CHECKMARX_API_KEY="your-api-key"
# OR
export CHECKMARX_CLIENT_ID="your-client-id"
export CHECKMARX_CLIENT_SECRET="your-client-secret"
```

## Usage

### Quick Start

```bash
cd diagnostic_agent
python run_diagnostic.py --project user-access-management
```

### Command Line Options

```bash
python run_diagnostic.py \
    --project user-access-management \
    --project-root /path/to/project \
    --output-dir diagnostic_reports
```

### Programmatic Usage

```python
from diagnostic_agent import DiagnosticAgent

# Initialize agent
agent = DiagnosticAgent(project_root='/path/to/project')

# Analyze a dependency upgrade
report = agent.analyze_dependency_upgrade(
    dependency_name='flask',
    current_version='1.1.2',
    target_version='2.3.0'
)

# Display results
print(f"Migration Score: {report.migration_score.score}/100")
print(f"Risk Level: {report.migration_score.risk_level}")
print(f"Estimated Effort: {report.migration_score.estimated_hours} hours")

# Save report
from diagnostic_agent import save_report
save_report(report, output_dir='reports')
```

## Components

### 1. Changelog Intelligence

Parses release notes and changelogs to extract:
- Breaking changes with severity levels
- Affected identifiers (functions, classes, variables)
- Version information

**Patterns detected:**
- `BREAKING: ...`
- `deprecated: ...`
- `removed: ...`
- `renamed: ...`
- `⚠️ ...`

### 2. Reachability Mapper

Uses ripgrep (with grep fallback) to:
- Search source code for breaking change identifiers
- Count occurrences across the codebase
- Identify affected files
- Map impact to specific locations

**Search locations:**
- `/src`
- `/app`
- `/lib`
- `/core`

### 3. Migration Effort Scorer

Calculates a 1-100 score based on:

**Version Delta (0-30 points):**
- Major version change: 100 points per version
- Minor version change: 10 points per version
- Patch version change: 1 point per version

**Code Impact (0-40 points):**
- 2 points per occurrence of breaking change in code

**Breaking Changes (0-30 points):**
- High severity: 10 points each
- Medium severity: 5 points each
- Low severity: 2 points each

**Risk Levels:**
- 75-100: Critical
- 50-74: High
- 25-49: Medium
- 1-24: Low

## Output

### Diagnostic Report

Each analysis generates:

**JSON Report** (`dependency_timestamp_diagnostic.json`):
```json
{
  "dependency_name": "flask",
  "current_version": "1.1.2",
  "target_version": "2.3.0",
  "migration_score": {
    "score": 45,
    "risk_level": "medium",
    "estimated_hours": 6.5
  },
  "breaking_changes": [...],
  "code_impacts": [...],
  "recommendations": [...]
}
```

**Markdown Report** (`dependency_timestamp_diagnostic.md`):
- Executive summary with score and risk level
- Breaking changes with severity
- Code impact analysis with file locations
- Actionable recommendations
- Testing strategy

### Example Output

```
================================================================================
🔍 AGENTIC DIAGNOSTIC LAYER
================================================================================

Step 1: Fetching latest Checkmarx scan report...
✓ Scan report retrieved successfully

Step 2: Initializing Diagnostic Agent...
Source directories: ['/path/to/project/src', '/path/to/project/app']

Step 3: Running diagnostic analysis...
Found 3 breaking changes
Found 2 code impacts
Migration score: 45/100 (medium risk)

================================================================================
📊 DIAGNOSTIC RESULTS
================================================================================

# 🔍 Dependency Upgrade Diagnostic Report

**Dependency:** flask
**Upgrade Path:** `1.1.2` → `2.3.0`

## Migration Effort Score

**Score:** 45/100 ⚠️ MEDIUM RISK
**Estimated Effort:** 6.5 hours
**Code Impacts:** 12 occurrences
**Breaking Changes:** 3

## 💡 Recommendations

⚠️ HIGH RISK: Extensive testing recommended.
📝 Action Required: Update 2 affected code locations:
  • Replace 'execute_query' (function) in 2 file(s) - 8 occurrence(s)
  • Replace 'ConfigManager' (class) in 1 file(s) - 4 occurrence(s)
⏱️ Estimated Effort: 6.5 hours (45 migration points)

================================================================================
📈 SUMMARY
================================================================================

Total Dependencies Analyzed: 2
Risk Levels:
  • Critical: 0
  • High: 0
  • Medium: 2
  • Low: 0

Total Estimated Effort: 13.0 hours
Average Migration Score: 45.0/100

💡 RESOURCE PLANNING RECOMMENDATION:
Recommended Sprint Allocation: 6 story points
(Based on 13.0 hours of estimated migration effort)
```

## Benefits

### 1. Risk Mitigation
- Replace blind upgrades with auditable upgrades
- Understand impact before making changes
- Prevent system stability issues from security patches

### 2. Resource Optimization
- Accurate effort estimation for sprint planning
- Data-driven story point allocation
- Better capacity planning

### 3. Developer Productivity
- Clear action items with file locations
- Priority guidance based on risk levels
- Testing strategy recommendations

### 4. Security Compliance
- Systematic approach to vulnerability remediation
- Audit trail of upgrade decisions
- Balance security with stability

## Integration

### CI/CD Pipeline

Add to your CI pipeline:

```yaml
# .github/workflows/security-diagnostic.yml
name: Security Diagnostic

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  diagnostic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          sudo apt-get install ripgrep
      - name: Run Diagnostic
        env:
          CHECKMARX_API_KEY: ${{ secrets.CHECKMARX_API_KEY }}
        run: |
          python diagnostic_agent/run_diagnostic.py
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: diagnostic-reports
          path: diagnostic_reports/
```

### Sprint Planning Integration

Use the migration scores in your sprint planning:

```python
# Get all reports
reports = agent.analyze_scan_results(scan_data)

# Calculate sprint capacity needed
total_points = sum(r.migration_score.score for r in reports)
sprint_capacity_needed = total_points / 100 * average_velocity

print(f"This sprint needs {sprint_capacity_needed} points for security upgrades")
```

## Troubleshooting

### "ripgrep not found"
Install ripgrep or the system will automatically fall back to grep:
```bash
sudo apt-get install ripgrep  # Ubuntu/Debian
brew install ripgrep          # macOS
```

### No breaking changes detected
- The changelog patterns may need adjustment for your dependencies
- Check if release notes are available for the target version
- Manual changelog review may be needed

### Inaccurate scores
- Customize scoring weights in `MigrationEffortScorer`
- Adjust version delta calculations for your use case
- Fine-tune severity assessments

## License

This module is part of the Knowledge Graph Application project.
