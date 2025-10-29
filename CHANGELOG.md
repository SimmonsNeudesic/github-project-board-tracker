# Changelog

## [Unreleased] - 2025-10-29

### Added
- **Per-Project Cache Separation**: Cache files are now organized by owner and project (e.g., `.ai_cache/myorg_137_extractions.json`) to prevent cache key conflicts when tracking multiple organizations or projects
- **PR Approval Matching**: Automatically fetches PR reviews from GitHub and matches approvers to linked issues
  - PR approvers are extracted from GitHub review data (APPROVED reviews only)
  - Approvers are matched to issues via GitHub's `closingIssuesReferences` API
  - Approval information flows from PRs to issues automatically
  - Supports multiple approvers per issue (comma-separated)
- **`--include-pr` CLI Flag**: New command-line switch to control PR visibility in reports
  - Default behavior: PRs are excluded from reports but used to gather approval data
  - With `--include-pr`: PRs appear as separate rows with Source = "Pull Request"
  - Maintains flexibility while keeping reports focused on issues by default

### Changed
- **Cache Key Format**: Changed from simple issue number to composite key `owner/repo#number` to support multiple repositories
- **ExtractionCache Constructor**: Now accepts `owner` and `project` parameters for cache file separation
- **AIFieldExtractor Constructor**: Now accepts `owner` and `project` parameters and passes them to cache
- **_process_items Method**: Now performs two passes:
  1. First pass: Process PRs to extract approval data and build approval mapping
  2. Second pass: Process all items, apply approval data to issues, filter PRs based on `--include-pr` flag
- **Source Field Values**: Updated to include "Pull Request" as a valid source type (previously only "Issue" or "Discussion")
- **GraphQL Queries**: Added `closingIssuesReferences` field to PR queries to support issue-PR linking
- **Approval Fields**: Now populated with PR approver names when available, falling back to project board fields

### Fixed
- Cache conflicts when tracking issues across multiple organizations or projects with overlapping issue numbers
- Missing approval information when PRs contain review approvals but project board fields are empty

### Documentation
- Updated README with PR Approval Matching section explaining the three usage scenarios
- Added examples for all three PR handling scenarios
- Updated command-line options documentation with `--include-pr` flag
- Updated Column Descriptions to reflect PR approver integration
- Updated feature list to highlight new capabilities

## Usage Examples

### Scenario 1: Issues only (no PR data)
```bash
python project_board_tracker.py --owner myorg --project 137 \
  --filter 'milestone:"Release 1.10.5.8" is:issue' \
  --format excel --output report.xlsx
```
- Report: Issues only
- Approvals: From project board fields only

### Scenario 2: Issues with PR approval data (recommended)
```bash
python project_board_tracker.py --owner myorg --project 137 \
  --filter 'milestone:"Release 1.10.5.8"' \
  --format excel --output report.xlsx
```
- Report: Issues only
- Approvals: **Enriched with PR approver names**

### Scenario 3: Include PRs in report
```bash
python project_board_tracker.py --owner myorg --project 137 \
  --filter 'milestone:"Release 1.10.5.8"' \
  --include-pr --format excel --output report.xlsx
```
- Report: Issues AND Pull Requests
- Approvals: Full PR approval information

## Technical Details

### Cache File Structure
- Old: `.ai_cache/extractions.json` (single file for all projects)
- New: `.ai_cache/{owner}_{project}_extractions.json` (one file per project)

### Cache Entry Format
```json
{
  "owner/repo#123": {
    "fields": {
      "business_need": "...",
      "acceptance_criteria": "..."
    },
    "timestamp": "2025-10-29T10:30:00",
    "model": "gpt-4.1-mini",
    "issue_updated_at": "2025-10-28T15:45:00"
  }
}
```

### PR Approval Extraction
1. Fetch PR reviews via GitHub REST API: `/repos/{owner}/{repo}/pulls/{number}/reviews`
2. Filter for `APPROVED` state reviews
3. Track most recent review state per user
4. Extract unique approver usernames
5. Map to linked issues via `closingIssuesReferences`
6. Populate approval fields with comma-separated approver names
