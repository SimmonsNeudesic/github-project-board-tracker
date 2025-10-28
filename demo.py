#!/usr/bin/env python3
"""
Demo script showing sample output from project_board_tracker.py

This script generates sample CSV and Markdown files to demonstrate
the expected output format without requiring GitHub API access.
"""

import csv
from datetime import datetime


def generate_sample_data():
    """Generate sample issue data matching stakeholder requirements."""
    return [
        {
            'Issue ID': 'REQ-001',
            'Title': 'Add Azure AI Document Intelligence custom classifier pipeline',
            'Source': 'Issue',
            'GitHub Issue URL': 'https://github.com/org/repo/issues/123',
            'Business Need': 'Improve document routing accuracy for multi-form ingestion.',
            'Acceptance Criteria': '≥95% routing accuracy on validation set; fallback to human review when <80%.',
            'Design Artifact(s) URL': 'https://github.com/org/repo/docs/design/HLD-doc-intel-classifier.md',
            'Test Case ID(s)': 'TC-101, TC-102',
            'Test Evidence URL': 'https://github.com/org/repo/actions/runs/111',
            'Linked PR(s) URL': 'https://github.com/org/repo/pull/456',
            'Commit SHA(s)': 'a1b2c3d, e4f5g6h',
            'Status': 'In Progress',
            'Priority': 'High',
            'Risk': 'Medium',
            'Owner': 'jdoe',
            'Approvals: Product Owner': 'Pending',
            'Approvals: QA Lead': 'Pending',
            'Approvals: Exec Sponsor': 'N/A',
            'Release Version': '2025.9',
            'Created Date': '2025-09-18',
            'Updated Date': '2025-09-18',
            'Change Log': 'Initial capture from GitHub Issue #123.'
        },
        {
            'Issue ID': 'REQ-002',
            'Title': 'Add export to CSV feature',
            'Source': 'Issue',
            'GitHub Issue URL': 'https://github.com/org/repo/issues/456',
            'Business Need': 'Stakeholders need to export data for external reporting',
            'Acceptance Criteria': 'Export button in UI; All data columns included; UTF-8 encoding',
            'Design Artifact(s) URL': 'N/A',
            'Test Case ID(s)': 'TC-201',
            'Test Evidence URL': 'N/A',
            'Linked PR(s) URL': 'N/A',
            'Commit SHA(s)': 'N/A',
            'Status': 'Done',
            'Priority': 'Medium',
            'Risk': 'Low',
            'Owner': 'jsmith',
            'Approvals: Product Owner': 'Approved',
            'Approvals: QA Lead': 'Approved',
            'Approvals: Exec Sponsor': 'Approved',
            'Release Version': '2025.6',
            'Created Date': '2025-06-01',
            'Updated Date': '2025-09-18',
            'Change Log': 'Completed implementation; QA approved; Released in 2025.6'
        },
        {
            'Issue ID': 'REQ-003',
            'Title': 'OpenAI-based summarization for extracted fields',
            'Source': 'Issue',
            'GitHub Issue URL': 'https://github.com/org/repo/issues/789',
            'Business Need': 'Improve analyst throughput by generating claim-ready summaries.',
            'Acceptance Criteria': 'Summaries meet template; human accept rate ≥ 90% on sample set.',
            'Design Artifact(s) URL': 'https://github.com/org/repo/docs/design/HLD-summarization.md',
            'Test Case ID(s)': 'TC-301, TC-302',
            'Test Evidence URL': 'https://github.com/org/repo/actions/runs/333',
            'Linked PR(s) URL': 'https://github.com/org/repo/pull/790',
            'Commit SHA(s)': '99aa11b',
            'Status': 'Done',
            'Priority': 'High',
            'Risk': 'Medium',
            'Owner': 'mcollins',
            'Approvals: Product Owner': 'Approved',
            'Approvals: QA Lead': 'Approved',
            'Approvals: Exec Sponsor': 'Approved',
            'Release Version': '2025.6',
            'Created Date': '2025-06-01',
            'Updated Date': '2025-09-18',
            'Change Log': 'Approved & released 2025.6.'
        }
    ]


def export_sample_csv():
    """Export sample data to CSV."""
    issues = generate_sample_data()
    
    fieldnames = [
        'Issue ID', 'Title', 'Source', 'GitHub Issue URL', 'Business Need',
        'Acceptance Criteria', 'Design Artifact(s) URL', 'Test Case ID(s)',
        'Test Evidence URL', 'Linked PR(s) URL', 'Commit SHA(s)', 'Status', 'Priority',
        'Risk', 'Owner', 'Approvals: Product Owner', 'Approvals: QA Lead',
        'Approvals: Exec Sponsor', 'Release Version', 'Created Date',
        'Updated Date', 'Change Log'
    ]
    
    output_file = 'sample_report.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)
    
    print(f"✓ Sample CSV exported to {output_file}")


def export_sample_markdown():
    """Export sample data to Markdown."""
    issues = generate_sample_data()
    
    output_file = 'sample_report.md'
    with open(output_file, 'w', encoding='utf-8') as mdfile:
        mdfile.write("# Project Board Status Report\n\n")
        mdfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        mdfile.write(f"Total Issues: {len(issues)}\n\n")
        
        # Summary by status
        status_counts = {}
        for issue in issues:
            status = issue.get('Status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        mdfile.write("## Status Summary\n\n")
        for status, count in sorted(status_counts.items()):
            mdfile.write(f"- {status}: {count}\n")
        mdfile.write("\n")
        
        # Detailed table
        mdfile.write("## Detailed Issue List\n\n")
        mdfile.write("| Issue ID | Title | Source | Status | Priority | Risk | Owner | Created | Updated |\n")
        mdfile.write("|----------|-------|--------|--------|----------|------|-------|---------|----------|\n")
        
        for issue in issues:
            issue_id = str(issue.get('Issue ID', 'N/A'))
            title = issue.get('Title', 'N/A')
            source = issue.get('Source', 'N/A')
            status = issue.get('Status', 'N/A')
            priority = issue.get('Priority', 'N/A')
            risk = issue.get('Risk', 'N/A')
            owner = issue.get('Owner', 'N/A')
            created = issue.get('Created Date', 'N/A')
            updated = issue.get('Updated Date', 'N/A')
            
            mdfile.write(f"| {issue_id} | {title} | {source} | {status} | {priority} | {risk} | {owner} | {created} | {updated} |\n")
        
        # Detailed sections
        mdfile.write("\n## Detailed Issue Information\n\n")
        for issue in issues:
            mdfile.write(f"### {issue.get('Issue ID', 'N/A')} - {issue.get('Title', 'Untitled')}\n\n")
            mdfile.write(f"**Source:** {issue.get('Source', 'N/A')}\n\n")
            mdfile.write(f"**URL:** {issue.get('GitHub Issue URL', 'N/A')}\n\n")
            mdfile.write(f"**Status:** {issue.get('Status', 'N/A')}\n\n")
            mdfile.write(f"**Priority:** {issue.get('Priority', 'N/A')}\n\n")
            mdfile.write(f"**Risk:** {issue.get('Risk', 'N/A')}\n\n")
            mdfile.write(f"**Owner:** {issue.get('Owner', 'N/A')}\n\n")
            
            if issue.get('Business Need') and issue.get('Business Need') != 'N/A':
                mdfile.write(f"**Business Need:** {issue.get('Business Need')}\n\n")
            
            if issue.get('Acceptance Criteria') and issue.get('Acceptance Criteria') != 'N/A':
                mdfile.write(f"**Acceptance Criteria:** {issue.get('Acceptance Criteria')}\n\n")
            
            if issue.get('Linked PR(s) URL') and issue.get('Linked PR(s) URL') != 'N/A':
                mdfile.write(f"**Linked PR(s):** {issue.get('Linked PR(s) URL')}\n\n")
            
            if issue.get('Commit SHA(s)') and issue.get('Commit SHA(s)') != 'N/A':
                mdfile.write(f"**Commit SHA(s):** {issue.get('Commit SHA(s)')}\n\n")
            
            mdfile.write("---\n\n")
    
    print(f"✓ Sample Markdown exported to {output_file}")


def main():
    """Generate sample reports."""
    print("Generating sample output files...\n")
    export_sample_csv()
    export_sample_markdown()
    print("\n✓ Sample files generated successfully!")
    print("\nThese files demonstrate the output format of project_board_tracker.py")
    print("without requiring GitHub API access.")


if __name__ == '__main__':
    main()
