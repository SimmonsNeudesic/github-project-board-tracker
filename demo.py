#!/usr/bin/env python3
"""
Demo script showing sample output from project_board_tracker.py

This script generates sample CSV and Markdown files to demonstrate
the expected output format without requiring GitHub API access.
"""

import csv
from datetime import datetime


def generate_sample_data():
    """Generate sample issue data."""
    return [
        {
            'ReqID': 'REQ-001',
            'Title': 'Implement user authentication',
            'Source': 'Issue',
            'Issue_URL': 'https://github.com/example/repo/issues/1',
            'Business_Need': 'Users need secure login to access the application',
            'Acceptance_Criteria': 'Users can login with email/password; Session management implemented; Password reset functionality',
            'Design_Artifact_URLs': 'https://figma.com/design-123',
            'Test_Case_ID': 'TC-001',
            'Test_Evidence_URL': 'https://testrail.com/evidence/1',
            'PR_URL': 'https://github.com/example/repo/pull/45',
            'Commit_SHA': 'a1b2c3d4e5f6',
            'Status': 'In Progress',
            'Priority': 'High',
            'Risk_Owner': 'john.doe',
            'Approval_Product': 'Approved',
            'Approval_QA_Lead': 'Pending',
            'Approval_Sponsor': 'Approved',
            'Release_Version': 'v1.2.0',
            'Created_Date': '2024-01-15T10:30:00Z',
            'Update_Date': '2024-01-20T14:22:00Z',
            'Change_Log': 'Initial creation; Updated acceptance criteria'
        },
        {
            'ReqID': 'REQ-002',
            'Title': 'Add export to CSV feature',
            'Source': 'Issue',
            'Issue_URL': 'https://github.com/example/repo/issues/2',
            'Business_Need': 'Stakeholders need to export data for external reporting',
            'Acceptance_Criteria': 'Export button in UI; All data columns included; UTF-8 encoding',
            'Design_Artifact_URLs': '',
            'Test_Case_ID': 'TC-002',
            'Test_Evidence_URL': '',
            'PR_URL': '',
            'Commit_SHA': '',
            'Status': 'Done',
            'Priority': 'Medium',
            'Risk_Owner': 'jane.smith',
            'Approval_Product': 'Approved',
            'Approval_QA_Lead': 'Approved',
            'Approval_Sponsor': 'Approved',
            'Release_Version': 'v1.1.0',
            'Created_Date': '2024-01-10T09:15:00Z',
            'Update_Date': '2024-01-18T16:45:00Z',
            'Change_Log': 'Initial creation; Completed implementation; QA approved'
        },
        {
            'ReqID': 'REQ-003',
            'Title': 'Fix performance issue in dashboard',
            'Source': 'Issue',
            'Issue_URL': 'https://github.com/example/repo/issues/3',
            'Business_Need': 'Dashboard loads too slowly affecting user experience',
            'Acceptance_Criteria': 'Dashboard loads in under 2 seconds; No console errors; Mobile responsive',
            'Design_Artifact_URLs': '',
            'Test_Case_ID': 'TC-003',
            'Test_Evidence_URL': 'https://testrail.com/evidence/3',
            'PR_URL': 'https://github.com/example/repo/pull/52',
            'Commit_SHA': 'f6e5d4c3b2a1',
            'Status': 'In Review',
            'Priority': 'Critical',
            'Risk_Owner': 'bob.johnson',
            'Approval_Product': 'Approved',
            'Approval_QA_Lead': 'In Progress',
            'Approval_Sponsor': 'Approved',
            'Release_Version': 'v1.1.1',
            'Created_Date': '2024-01-22T11:00:00Z',
            'Update_Date': '2024-01-25T13:30:00Z',
            'Change_Log': 'Initial creation; PR submitted for review'
        }
    ]


def export_sample_csv():
    """Export sample data to CSV."""
    issues = generate_sample_data()
    
    fieldnames = [
        'ReqID', 'Title', 'Source', 'Issue_URL', 'Business_Need',
        'Acceptance_Criteria', 'Design_Artifact_URLs', 'Test_Case_ID',
        'Test_Evidence_URL', 'PR_URL', 'Commit_SHA', 'Status', 'Priority',
        'Risk_Owner', 'Approval_Product', 'Approval_QA_Lead',
        'Approval_Sponsor', 'Release_Version', 'Created_Date',
        'Update_Date', 'Change_Log'
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
        mdfile.write("| ReqID | Title | Source | Status | Priority | Created | Updated |\n")
        mdfile.write("|-------|-------|--------|--------|----------|---------|----------|\n")
        
        for issue in issues:
            req_id = str(issue.get('ReqID', ''))
            title = issue.get('Title', '')
            source = issue.get('Source', '')
            status = issue.get('Status', '')
            priority = issue.get('Priority', '')
            created = issue.get('Created_Date', '')[:10] if issue.get('Created_Date') else ''
            updated = issue.get('Update_Date', '')[:10] if issue.get('Update_Date') else ''
            
            mdfile.write(f"| {req_id} | {title} | {source} | {status} | {priority} | {created} | {updated} |\n")
        
        # Detailed sections
        mdfile.write("\n## Detailed Issue Information\n\n")
        for issue in issues:
            mdfile.write(f"### {issue.get('ReqID', 'N/A')} - {issue.get('Title', 'Untitled')}\n\n")
            mdfile.write(f"**Source:** {issue.get('Source', 'N/A')}\n\n")
            mdfile.write(f"**URL:** {issue.get('Issue_URL', 'N/A')}\n\n")
            mdfile.write(f"**Status:** {issue.get('Status', 'N/A')}\n\n")
            mdfile.write(f"**Priority:** {issue.get('Priority', 'N/A')}\n\n")
            
            if issue.get('Business_Need'):
                mdfile.write(f"**Business Need:** {issue.get('Business_Need')}\n\n")
            
            if issue.get('Acceptance_Criteria'):
                mdfile.write(f"**Acceptance Criteria:** {issue.get('Acceptance_Criteria')}\n\n")
            
            if issue.get('PR_URL'):
                mdfile.write(f"**Pull Request:** {issue.get('PR_URL')}\n\n")
            
            if issue.get('Commit_SHA'):
                mdfile.write(f"**Commit SHA:** {issue.get('Commit_SHA')}\n\n")
            
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
