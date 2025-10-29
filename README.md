# GitHub Project Board Tracker

A Python script that exports a full list of issues from a GitHub project board view and generates project status reports for stakeholders in **Markdown**, **CSV**, or **Excel** format.

## Features

- 📊 Export issues from GitHub Projects (V2)
- 🔎 **Filter by GitHub search queries** - Use full GitHub search syntax to filter results
- 🔗 **Smart PR Approval Matching** - Automatically extracts PR approvers and matches them to linked issues
- 🎯 **Flexible PR Handling** - PRs are excluded from reports by default but used to gather approval data
- 🤖 **AI-Powered Field Extraction** - Extract missing fields from issue content using Azure OpenAI
- 💾 **Per-Project Caching** - Separate cache files per organization/project to avoid conflicts
- 📝 Generate reports in multiple formats: Markdown, CSV, and Excel
- 🔍 Extract comprehensive issue information including:
  - Issue ID, Title, Source (Discussion/Issue/Pull Request)
  - GitHub Issue URL, Business Need, Acceptance Criteria
  - Design Artifact(s) URL, Test Case ID(s), Test Evidence URL
  - Linked PR(s) URL, Commit SHA(s), Status, Priority
  - Risk, Owner, **Approvals with Approver Names** (Product Owner, QA Lead, Exec Sponsor)
  - Release Version, Dates, Change Log
- 🎨 Beautiful formatted output with status summaries
- 🔄 Flexible field mapping that handles variations in custom field names (spaces, underscores, case)
- 💾 Smart caching for AI extractions (avoid re-processing and reduce costs)
- ✅ Uses "N/A" for missing fields to clearly identify incomplete data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SimmonsNeudesic/github-project-board-tracker.git
cd github-project-board-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your GitHub personal access token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the following permissions:
     - `repo` (Full control of private repositories)
     - `read:project` (Read access to projects)
     - `read:org` (Read org and team membership)
   - Set the token as an environment variable:
     ```bash
     export GITHUB_TOKEN=your_token_here
     ```

## Usage

### Basic Usage

Export entire project to CSV (default):
```bash
python project_board_tracker.py --owner myorg --project 1 --format csv
```

Export filtered by milestone to Excel:
```bash
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8" is:issue' --format excel --output report.xlsx
```

Export with PR approval data (PRs filtered from report but used for approval matching):
```bash
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8"' --format excel --output report.xlsx
```

Export including PRs in the report:
```bash
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8"' --include-pr --format excel --output report.xlsx
```

Export to Markdown:
```bash
python project_board_tracker.py --owner myorg --project 1 --format markdown --output report.md
```

### PR Approval Matching

🔗 **New Feature!** The tracker now automatically fetches PR reviews and matches approvers to linked issues.

**How it works:**

1. When you run a query that includes PRs (without `is:issue` filter), the tracker fetches all PR reviews
2. PR approvers are automatically extracted from GitHub review data
3. PRs are matched to their linked issues using GitHub's `closingIssuesReferences`
4. Approval information flows from PRs to issues automatically
5. By default, PRs are **excluded from the report** but their approval data is preserved for issues

**Usage scenarios:**

**Scenario 1: Issues only (no PR data)**
```bash
# Filter explicitly excludes PRs, so no PR approval data is available
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8" is:issue' --format excel --output report.xlsx
```
- Report contains: Issues only
- Approval data: From project board fields only

**Scenario 2: Issues with PR approval data (recommended)**
```bash
# Filter includes PRs, but they're filtered from report output
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8"' --format excel --output report.xlsx
```
- Report contains: Issues only
- Approval data: **Enriched with PR approver names**
- PRs are fetched for approval data but not included in report

**Scenario 3: Include PRs in report**
```bash
# Use --include-pr to show PRs as separate items
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8"' --include-pr --format excel --output report.xlsx
```
- Report contains: Issues AND Pull Requests
- Approval data: Full PR approval information
- PRs appear as separate rows with Source = "Pull Request"

**Benefits:**
- ✅ Automatic approval tracking from code reviews
- ✅ No manual data entry needed for approvals
- ✅ Accurate approver names from GitHub reviews
- ✅ Flexible - use PRs for data enrichment or include them in reports

### Using Filters (Recommended)

The `--filter` option supports full GitHub search query syntax, allowing you to export only the issues you care about:

**Filter by milestone (exclude PRs):**
```bash
python project_board_tracker.py --owner neudesic --project 137 --filter 'milestone:"Release 1.11.0.0" -is:pr' --format excel --output release_report.xlsx
```

**Filter by state and label:**
```bash
python project_board_tracker.py --owner myorg --project 1 --filter 'state:open label:bug' --format csv --output open_bugs.csv
```

**Filter by assignee:**
```bash
python project_board_tracker.py --owner myorg --project 1 --filter 'assignee:john state:open' --format markdown --output johns_tasks.md
```

**Complex filters:**
```bash
python project_board_tracker.py --owner myorg --project 1 --filter 'milestone:"Sprint 5" label:feature state:closed' --format excel --output completed_features.xlsx
```

### Supported Filter Syntax

The filter supports all GitHub search query operators:
- `milestone:"Release 1.10.5.8"` - Filter by milestone name
- `state:open` or `state:closed` - Filter by issue state
- `label:bug` or `label:"needs review"` - Filter by labels
- `assignee:username` - Filter by assignee
- `author:username` - Filter by author
- `is:pr` or `is:issue` - Filter by type
- `-is:pr` - Exclude pull requests
- `-is:issue` - Exclude issues
- `created:>2024-01-01` - Filter by date
- Any combination of the above using spaces

For more information on GitHub search syntax, see: [GitHub Search Documentation](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests)

### Command-Line Options

```
Options:
  --owner OWNER         Repository owner (organization or user) [required]
  --repo REPO          Repository name (optional, for org-level projects)
  --project PROJECT    Project board number [required]
  --filter FILTER      GitHub search query to filter items (e.g., 'milestone:"Release 1.10.5.8"')
  --include-pr         Include pull requests in the report output (default: PRs excluded but used for approval data)
  --view VIEW          Project view number (optional, deprecated - use --filter instead)
  --format FORMAT      Output format: csv, markdown, or excel (default: csv)
  --output OUTPUT      Output file path (default: project_board_report.[format])
  --token TOKEN        GitHub personal access token (or set GITHUB_TOKEN env variable)
  
  AI Extraction Options:
  --extract-from-body  Extract missing fields from issue content using AI (Azure OpenAI)
  --azure-openai-endpoint ENDPOINT  Azure OpenAI endpoint URL (or set AZURE_OPENAI_ENDPOINT)
  --azure-openai-key KEY            Azure OpenAI API key (or set AZURE_OPENAI_API_KEY)
  --azure-deployment NAME           Azure OpenAI deployment name (default: gpt-4.1-mini)
  --cache-dir DIR                   Directory for caching AI extractions (default: .ai_cache)
  
  -h, --help          Show help message
```

### AI-Powered Field Extraction

The tracker can intelligently extract missing Project board fields from issue bodies and comments using Azure OpenAI. This is useful when:
- Your Project board lacks custom fields for Business Need, Acceptance Criteria, etc.
- Issues contain rich content but it's not structured in Project board fields
- You want automated extraction without manually adding custom fields

**Setup:**

1. Deploy an Azure OpenAI resource with `gpt-4o-mini` or `gpt-4.1-mini`
2. Set environment variables:
   ```bash
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview"
   export AZURE_OPENAI_API_KEY="your-api-key"
   ```

**Usage:**

```bash
python project_board_tracker.py \
  --owner neudesic \
  --project 137 \
  --filter 'milestone:"Release 1.10.5.8" is:issue' \
  --format excel \
  --output report.xlsx \
  --extract-from-body
```

**What Gets Extracted:**
- Business Need - Why the issue matters
- Acceptance Criteria - Definition of done
- Test Case IDs - Test case references
- Test Evidence URL - Links to test results
- Design Artifacts URL - Links to design docs
- Risk - Risk level and description
- Release Version - Target release
- Change Log - Summary of changes

**Features:**
- 💾 **Smart Caching** - Extractions are cached in `.ai_cache/` to avoid re-processing
- 🗂️ **Per-Project Cache Separation** - Cache files are organized by owner/project (e.g., `.ai_cache/myorg_137_extractions.json`)
- ♻️ **Re-extraction** - Automatically re-extracts if issue is updated since last cache
- 🏷️ **Source Annotation** - AI-extracted fields are marked with `[AI-Extracted]`
- 💰 **Cost-Effective** - Uses gpt-4o-mini (~$0.0005 per issue, ~$0.50 for 1000 issues)
- 🚫 **No Cache Conflicts** - Multiple projects can be tracked without cache key collisions

**Example Output:**

| Field | Value |
|-------|-------|
| Business Need | Prevent security vulnerability from overly permissive CORS policy [AI-Extracted] |
| Risk | Medium: Overly permissive cross-domain policy allows malicious sites to exploit user sessions [AI-Extracted] |
| Change Log | Removed '*' from allowed CORS domains; configured allowed domains per service [AI-Extracted] |

### Finding Your Project Number

To find your project number:
1. Go to your GitHub project board
2. Look at the URL: `https://github.com/orgs/YOUR_ORG/projects/NUMBER`
3. The number at the end is your project number

### Examples

**Export organization project to CSV:**
```bash
python project_board_tracker.py --owner mycompany --project 5 --format csv --output sprint_status.csv
```

**Export with explicit token:**
```bash
python project_board_tracker.py --owner mycompany --project 5 --format markdown --token ghp_xxxxx
```

**Export to Excel with custom filename:**
```bash
python project_board_tracker.py --owner mycompany --project 5 --format excel --output "Q4_Project_Status.xlsx"
```

## Output Formats

### CSV Format
Standard comma-separated values file with all columns defined in the requirements. Easy to import into spreadsheets and databases.

### Markdown Format
Human-readable format with:
- Status summary (count by status)
- Quick overview table
- Detailed issue information sections

### Excel Format
Formatted Excel workbook with:
- Styled headers (blue background, white text)
- Auto-adjusted column widths
- Professional appearance for stakeholder reports

## Column Descriptions

| Column | Description |
|--------|-------------|
| Issue ID | Requirement/Issue identifier (e.g., REQ-001) |
| Title | Issue title |
| Source | Type: Discussion, Issue, or Pull Request |
| GitHub Issue URL | Direct link to the GitHub issue or PR |
| Business Need | Business justification from issue body or custom field |
| Acceptance Criteria | Success criteria from issue body or custom field |
| Design Artifact(s) URL | Links to design documents |
| Test Case ID(s) | Associated test case identifiers (e.g., TC-101, TC-102) |
| Test Evidence URL | Link to test evidence or CI run |
| Linked PR(s) URL | Pull request URL(s) linked to this issue |
| Commit SHA(s) | Commit SHA(s) from linked PRs (shortened format) |
| Status | Current status from project board (e.g., In Progress, Done) |
| Priority | Priority level (High, Medium, Low, or from labels) |
| Risk | Risk level (High, Medium, Low) |
| Owner | Person responsible (from custom field or first assignee) |
| Approvals: Product Owner | Product owner approval status or PR approver names |
| Approvals: QA Lead | QA Lead approval status or PR approver names |
| Approvals: Exec Sponsor | Executive sponsor approval status or PR approver names |
| Release Version | Target release version (e.g., 2025.9) |
| Created Date | Issue creation date (YYYY-MM-DD format) |
| Updated Date | Last update date (YYYY-MM-DD format) |
| Change Log | History of changes |

**Note:** All missing fields are represented as "N/A" to clearly identify incomplete data.

## Custom Fields

The script automatically extracts custom fields from your GitHub project board. The script uses flexible field name matching that handles variations in naming:

- **Exact match**: Looks for exact field names first
- **Normalized match**: Handles spaces, underscores, hyphens, and case variations
  - "Issue ID", "Issue_ID", "issue-id", "issue id" are all recognized
  - "Business Need", "Business_Need", "business-need" are all recognized

If custom fields don't exist, the script attempts to extract information from:

- Issue body (for Business Need and Acceptance Criteria)
- Labels (for Priority - supports patterns like "priority:", "p0", "p1", "high", "medium", "low", "critical")
- Assignees (for Owner - uses first assignee if Owner field is not set)

All missing fields are represented as "N/A" to clearly identify incomplete data.

## Troubleshooting

**Error: GitHub token is required**
- Make sure you've set the `GITHUB_TOKEN` environment variable or use the `--token` flag

**Error: GraphQL errors**
- Verify your token has the correct permissions
- Check that the project number is correct
- Ensure you have access to the organization/project

**Excel export fails**
- Install openpyxl: `pip install openpyxl`

## Requirements

- Python 3.7+
- requests library
- openpyxl library (for Excel export)

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
