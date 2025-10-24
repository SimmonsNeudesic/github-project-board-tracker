# GitHub Project Board Tracker

A Python script that exports a full list of issues from a GitHub project board view and generates project status reports for stakeholders in **Markdown**, **CSV**, or **Excel** format.

## Features

- 📊 Export issues from GitHub Projects (V2)
- � **Filter by GitHub search queries** - Use full GitHub search syntax to filter results
- �📝 Generate reports in multiple formats: Markdown, CSV, and Excel
- 🔍 Extract comprehensive issue information including:
  - ReqID, Title, Source (Discussion/Issue/PR)
  - Issue URL, Business Need, Acceptance Criteria
  - Design Artifact URLs, Test Case ID, Test Evidence URL
  - PR URL, Commit SHA, Status, Priority
  - Risk Owner, Approvals (Product, QA Lead, Sponsor)
  - Release Version, Dates, Change Log
- 🎨 Beautiful formatted output with status summaries

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
python project_board_tracker.py --owner myorg --project 137 --filter 'milestone:"Release 1.10.5.8" -is:pr' --format excel --output report.xlsx
```

Export to Markdown:
```bash
python project_board_tracker.py --owner myorg --project 1 --format markdown --output report.md
```

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
  --filter FILTER      GitHub search query to filter items (e.g., 'milestone:"Release 1.10.5.8" -is:pr')
  --view VIEW          Project view number (optional, deprecated - use --filter instead)
  --format FORMAT      Output format: csv, markdown, or excel (default: csv)
  --output OUTPUT      Output file path (default: project_board_report.[format])
  --token TOKEN        GitHub personal access token (or set GITHUB_TOKEN env variable)
  -h, --help          Show help message
```

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
| ReqID | Requirement/Issue ID |
| Title | Issue title |
| Source | Type: Discussion, Issue, or Pull Request |
| Issue_URL | Direct link to the issue |
| Business_Need | Business justification from issue body |
| Acceptance_Criteria | Success criteria from issue body |
| Design_Artifact_URLs | Links to design documents |
| Test_Case_ID | Associated test case identifier |
| Test_Evidence_URL | Link to test evidence |
| PR_URL | Pull request URL (if applicable) |
| Commit_SHA | Latest commit SHA (for PRs) |
| Status | Current status from project board |
| Priority | Priority level |
| Risk_Owner | Person responsible for risk management |
| Approval_Product | Product approval status |
| Approval_QA_Lead | QA Lead approval status |
| Approval_Sponsor | Sponsor approval status |
| Release_Version | Target release version |
| Created_Date | Issue creation date |
| Update_Date | Last update date |
| Change_Log | History of changes |

## Custom Fields

The script automatically extracts custom fields from your GitHub project board. If you have custom fields with names matching the column names (e.g., "Business_Need", "Test_Case_ID"), they will be automatically populated in the export.

If custom fields don't exist, the script attempts to extract information from:
- Issue body (for Business_Need and Acceptance_Criteria)
- Labels (for Priority)
- Assignees (for Risk_Owner)

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
