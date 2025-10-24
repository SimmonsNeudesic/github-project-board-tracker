#!/usr/bin/env python3
"""
GitHub Project Board Tracker

A Python script that exports a full list of issues from a GitHub project board view
and generates project status reports for stakeholders in markdown, CSV, or Excel format.
"""

import os
import sys
import argparse
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests


class GitHubProjectBoardTracker:
    """Fetch and export issues from GitHub project boards."""
    
    def __init__(self, token: str, owner: str, repo: Optional[str] = None):
        """
        Initialize the tracker.
        
        Args:
            token: GitHub personal access token
            owner: Repository owner (organization or user)
            repo: Repository name (optional, for org-level projects)
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.graphql_url = 'https://api.github.com/graphql'
        self.rest_url = 'https://api.github.com/graphql'
    
    def fetch_project_board_issues(self, project_number: int, view_number: Optional[int] = None, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch issues from a GitHub project board, optionally filtered by view or query.
        
        Args:
            project_number: The project board number
            view_number: Optional view number to filter items (deprecated - use filter_query instead)
            filter_query: Optional GitHub search query to filter items (e.g., 'milestone:"Release 1.10.5.8" -is:pr')
            
        Returns:
            List of issues with all required data
        """
        if filter_query:
            return self.fetch_filtered_project_issues(project_number, filter_query)
        elif view_number:
            return self.fetch_project_view_issues(project_number, view_number)
        else:
            return self.fetch_all_project_issues(project_number)
    
    def fetch_all_project_issues(self, project_number: int) -> List[Dict[str, Any]]:
        """
        Fetch all issues from a GitHub project board using GraphQL API.
        
        Args:
            project_number: The project board number
            
        Returns:
            List of issues with all required data
        """
        query = """
        query($owner: String!, $number: Int!, $cursor: String) {
          organization(login: $owner) {
            projectV2(number: $number) {
              title
              items(first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  id
                  type
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldNumberValue {
                        number
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        date
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                    }
                  }
                  content {
                    ... on Issue {
                      number
                      title
                      url
                      state
                      createdAt
                      updatedAt
                      body
                      labels(first: 10) {
                        nodes {
                          name
                        }
                      }
                      assignees(first: 5) {
                        nodes {
                          login
                        }
                      }
                    }
                    ... on PullRequest {
                      number
                      title
                      url
                      state
                      createdAt
                      updatedAt
                      body
                      commits(last: 1) {
                        nodes {
                          commit {
                            oid
                          }
                        }
                      }
                    }
                    ... on DraftIssue {
                      title
                      body
                      createdAt
                      updatedAt
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        all_items = []
        has_next_page = True
        cursor = None
        
        while has_next_page:
            variables = {
                'owner': self.owner,
                'number': project_number,
                'cursor': cursor
            }
            
            response = requests.post(
                self.graphql_url,
                json={'query': query, 'variables': variables},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            project_data = data['data']['organization']['projectV2']
            items = project_data['items']
            all_items.extend(items['nodes'])
            
            has_next_page = items['pageInfo']['hasNextPage']
            cursor = items['pageInfo']['endCursor']
        
        return self._process_items(all_items)
    
    def fetch_project_view_issues(self, project_number: int, view_number: int) -> List[Dict[str, Any]]:
        """
        Fetch issues from a specific view of a GitHub project board.
        Uses the updated GraphQL API to fetch items filtered by view.
        
        Args:
            project_number: The project board number
            view_number: The view number to filter items
            
        Returns:
            List of issues with all required data from the specific view
        """
        query = """
        query($owner: String!, $number: Int!, $cursor: String) {
          organization(login: $owner) {
            projectV2(number: $number) {
              title
              views(first: 50) {
                nodes {
                  id
                  name
                  number
                }
              }
              items(first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  id
                  type
                  isArchived
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldNumberValue {
                        number
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        date
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                    }
                  }
                  content {
                    ... on Issue {
                      title
                      url
                      state
                      number
                      createdAt
                      updatedAt
                      author {
                        login
                      }
                      assignees(first: 5) {
                        nodes {
                          login
                        }
                      }
                      labels(first: 10) {
                        nodes {
                          name
                        }
                      }
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                    ... on PullRequest {
                      title
                      url
                      state
                      number
                      createdAt
                      updatedAt
                      author {
                        login
                      }
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        # First, get all items and available views
        all_items = []
        has_next_page = True
        cursor = None
        views_info = None
        
        while has_next_page:
            variables = {
                'owner': self.owner,
                'number': project_number,
                'cursor': cursor
            }
            
            response = requests.post(
                self.graphql_url,
                json={'query': query, 'variables': variables},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            project_data = data['data']['organization']['projectV2']
            
            # Store views info on first iteration
            if views_info is None:
                views_info = project_data['views']['nodes']
                view_exists = any(view['number'] == view_number for view in views_info)
                if not view_exists:
                    available_views = [f"{view['number']} ({view['name']})" for view in views_info]
                    raise Exception(f"View {view_number} not found. Available views: {', '.join(available_views)}")
            
            items = project_data['items']
            all_items.extend(items['nodes'])
            
            has_next_page = items['pageInfo']['hasNextPage']
            cursor = items['pageInfo']['endCursor']
        
        # Note: Since GitHub's API doesn't provide direct view filtering in GraphQL,
        # we return all items. In a real implementation, you would need additional
        # filtering logic based on the view's configuration.
        print(f"Note: Retrieved all {len(all_items)} items from project {project_number}")
        print(f"View {view_number} filtering is not directly supported by GitHub's API")
        print("You may need to manually filter based on your view criteria.")
        
        # Filter out archived items as views typically don't show them
        active_items = [item for item in all_items if not item.get('isArchived', False)]
        print(f"Filtered to {len(active_items)} non-archived items")
        
        return self._process_items(active_items)
    
    def fetch_filtered_project_issues(self, project_number: int, filter_query: str) -> List[Dict[str, Any]]:
        """
        Fetch issues from a GitHub project board filtered by a GitHub search query.
        
        Uses GitHub Search API to evaluate the full query syntax, then intersects
        results with the project's items. This supports all GitHub search operators
        without reimplementing query parsing.
        
        Args:
            project_number: The project board number
            filter_query: GitHub search query (e.g., 'milestone:"Release 1.10.5.8" -is:pr')
            
        Returns:
            List of filtered issues with all required data
        """
        print(f"Applying filter via GitHub Search API: {filter_query}")
        
        # Use GitHub Search API to find matching issues/PRs
        search_url = 'https://api.github.com/search/issues'
        per_page = 100
        page = 1
        matched_set = set()  # Set of (owner, repo, number) tuples
        
        try:
            while True:
                params = {
                    'q': filter_query,
                    'per_page': per_page,
                    'page': page
                }
                response = requests.get(
                    search_url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                items = data.get('items', [])
                for item in items:
                    number = item.get('number')
                    # repository_url format: https://api.github.com/repos/owner/repo
                    repo_url = item.get('repository_url', '')
                    if repo_url:
                        parts = repo_url.rstrip('/').split('/')
                        if len(parts) >= 2:
                            owner = parts[-2]
                            repo_name = parts[-1]
                            matched_set.add((owner, repo_name, number))
                
                # Check if there are more pages
                if len(items) < per_page:
                    break
                
                # Protect against Search API 1000 result limit
                total_count = data.get('total_count', 0)
                if page * per_page >= min(1000, total_count):
                    if total_count > 1000:
                        print(f"Warning: Search returned {total_count} results but API limit is 1000")
                    break
                
                page += 1
                
        except requests.HTTPError as e:
            raise Exception(f"GitHub Search API error: {e}")
        
        print(f"Search API matched {len(matched_set)} issues/PRs")
        
        if not matched_set:
            print("No items matched the search query")
            return []
        
        # Fetch all project items and intersect with search results
        print(f"Fetching project {project_number} items...")
        all_project_items = self.fetch_all_project_issues_raw(project_number)
        
        # Filter project items to only those that matched the search
        filtered_items = []
        for item in all_project_items:
            content = item.get('content')
            if not content:
                continue
            
            repo_info = content.get('repository')
            number = content.get('number')
            
            if repo_info and number:
                owner = repo_info.get('owner', {}).get('login')
                repo_name = repo_info.get('name')
                if (owner, repo_name, number) in matched_set:
                    filtered_items.append(item)
        
        print(f"Filtered to {len(filtered_items)} items (from {len(all_project_items)} total project items)")
        
        # Process and return the filtered items
        return self._process_items(filtered_items)
    
    def fetch_all_project_issues_raw(self, project_number: int) -> List[Dict[str, Any]]:
        """
        Fetch all raw items from a project (before processing).
        
        Args:
            project_number: The project board number
            
        Returns:
            List of raw project items
        """
        query = """
        query($owner: String!, $number: Int!, $cursor: String) {
          organization(login: $owner) {
            projectV2(number: $number) {
              title
              items(first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  id
                  type
                  isArchived
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldNumberValue {
                        number
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        date
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                    }
                  }
                  content {
                    ... on Issue {
                      title
                      url
                      state
                      number
                      createdAt
                      updatedAt
                      author {
                        login
                      }
                      assignees(first: 5) {
                        nodes {
                          login
                        }
                      }
                      labels(first: 10) {
                        nodes {
                          name
                        }
                      }
                      milestone {
                        title
                      }
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                    ... on PullRequest {
                      title
                      url
                      state
                      number
                      createdAt
                      updatedAt
                      author {
                        login
                      }
                      milestone {
                        title
                      }
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        all_items = []
        has_next_page = True
        cursor = None
        
        while has_next_page:
            variables = {
                'owner': self.owner,
                'number': project_number,
                'cursor': cursor
            }
            
            response = requests.post(
                self.graphql_url,
                json={'query': query, 'variables': variables},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            project_data = data['data']['organization']['projectV2']
            items = project_data['items']
            all_items.extend(items['nodes'])
            
            has_next_page = items['pageInfo']['hasNextPage']
            cursor = items['pageInfo']['endCursor']
        
        return all_items
    
    def _process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw project items into structured issue data.
        
        Args:
            items: Raw items from GraphQL API
            
        Returns:
            Processed list of issues with standardized fields
        """
        processed_issues = []
        
        for item in items:
            content = item.get('content')
            if not content:
                # Draft issue
                content = {'title': 'Draft Issue', 'url': '', 'state': 'Draft'}
            
            # Extract custom field values
            field_values = {}
            for field_value in item.get('fieldValues', {}).get('nodes', []):
                if not field_value:
                    continue
                field_name = field_value.get('field', {}).get('name', '')
                if 'text' in field_value:
                    field_values[field_name] = field_value['text']
                elif 'number' in field_value:
                    field_values[field_name] = field_value['number']
                elif 'date' in field_value:
                    field_values[field_name] = field_value['date']
                elif 'name' in field_value:
                    field_values[field_name] = field_value['name']
            
            # Determine source type
            source = 'Issue'
            if item.get('type') == 'DRAFT_ISSUE':
                source = 'Draft'
            elif 'commits' in content:
                source = 'Pull Request'
            
            # Extract commit SHA for PRs
            commit_sha = ''
            if 'commits' in content and content['commits']['nodes']:
                commit_sha = content['commits']['nodes'][0]['commit']['oid']
            
            # Extract labels
            labels = []
            if 'labels' in content and content['labels']['nodes']:
                labels = [label['name'] for label in content['labels']['nodes']]
            
            # Extract assignees
            assignees = []
            if 'assignees' in content and content['assignees']['nodes']:
                assignees = [assignee['login'] for assignee in content['assignees']['nodes']]
            
            # Build the issue record
            issue_record = {
                'ReqID': field_values.get('ReqID', content.get('number', '')),
                'Title': content.get('title', ''),
                'Source': source,
                'Issue_URL': content.get('url', ''),
                'Business_Need': field_values.get('Business_Need', self._extract_section(content.get('body', ''), 'Business Need')),
                'Acceptance_Criteria': field_values.get('Acceptance_Criteria', self._extract_section(content.get('body', ''), 'Acceptance Criteria')),
                'Design_Artifact_URLs': field_values.get('Design_Artifact_URLs', ''),
                'Test_Case_ID': field_values.get('Test_Case_ID', ''),
                'Test_Evidence_URL': field_values.get('Test_Evidence_URL', ''),
                'PR_URL': content.get('url', '') if source == 'Pull Request' else '',
                'Commit_SHA': commit_sha,
                'Status': field_values.get('Status', content.get('state', '')),
                'Priority': field_values.get('Priority', self._get_priority_from_labels(labels)),
                'Risk_Owner': field_values.get('Risk_Owner', ', '.join(assignees)),
                'Approval_Product': field_values.get('Approval_Product', ''),
                'Approval_QA_Lead': field_values.get('Approval_QA_Lead', ''),
                'Approval_Sponsor': field_values.get('Approval_Sponsor', ''),
                'Release_Version': field_values.get('Release_Version', ''),
                'Created_Date': content.get('createdAt', ''),
                'Update_Date': content.get('updatedAt', ''),
                'Change_Log': field_values.get('Change_Log', '')
            }
            
            processed_issues.append(issue_record)
        
        return processed_issues
    
    def _extract_section(self, body: str, section_name: str) -> str:
        """Extract a section from issue body markdown."""
        if not body:
            return ''
        
        lines = body.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name.lower() in line.lower() and (line.startswith('#') or line.startswith('**')):
                in_section = True
                continue
            elif in_section and (line.startswith('#') or (line.startswith('**') and '**' in line[2:])):
                break
            elif in_section:
                section_content.append(line)
        
        return '\n'.join(section_content).strip()
    
    def _get_priority_from_labels(self, labels: List[str]) -> str:
        """Extract priority from labels."""
        priority_labels = [label for label in labels if 'priority' in label.lower()]
        return priority_labels[0] if priority_labels else ''
    
    def export_to_csv(self, issues: List[Dict[str, Any]], output_file: str):
        """
        Export issues to CSV format.
        
        Args:
            issues: List of issue records
            output_file: Path to output CSV file
        """
        if not issues:
            print("No issues to export.")
            return
        
        fieldnames = [
            'ReqID', 'Title', 'Source', 'Issue_URL', 'Business_Need',
            'Acceptance_Criteria', 'Design_Artifact_URLs', 'Test_Case_ID',
            'Test_Evidence_URL', 'PR_URL', 'Commit_SHA', 'Status', 'Priority',
            'Risk_Owner', 'Approval_Product', 'Approval_QA_Lead',
            'Approval_Sponsor', 'Release_Version', 'Created_Date',
            'Update_Date', 'Change_Log'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(issues)
        
        print(f"Exported {len(issues)} issues to {output_file}")
    
    def export_to_markdown(self, issues: List[Dict[str, Any]], output_file: str):
        """
        Export issues to Markdown format.
        
        Args:
            issues: List of issue records
            output_file: Path to output Markdown file
        """
        if not issues:
            print("No issues to export.")
            return
        
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
                req_id = self._escape_markdown(str(issue.get('ReqID', '')))
                title = self._escape_markdown(issue.get('Title', ''))
                source = self._escape_markdown(issue.get('Source', ''))
                status = self._escape_markdown(issue.get('Status', ''))
                priority = self._escape_markdown(issue.get('Priority', ''))
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
        
        print(f"Exported {len(issues)} issues to {output_file}")
    
    def export_to_excel(self, issues: List[Dict[str, Any]], output_file: str):
        """
        Export issues to Excel format.
        
        Args:
            issues: List of issue records
            output_file: Path to output Excel file
        """
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            print("Error: openpyxl library is required for Excel export.")
            print("Install it with: pip install openpyxl")
            return
        
        if not issues:
            print("No issues to export.")
            return
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Project Board Status"
        
        # Define headers
        headers = [
            'ReqID', 'Title', 'Source', 'Issue_URL', 'Business_Need',
            'Acceptance_Criteria', 'Design_Artifact_URLs', 'Test_Case_ID',
            'Test_Evidence_URL', 'PR_URL', 'Commit_SHA', 'Status', 'Priority',
            'Risk_Owner', 'Approval_Product', 'Approval_QA_Lead',
            'Approval_Sponsor', 'Release_Version', 'Created_Date',
            'Update_Date', 'Change_Log'
        ]
        
        # Style for header
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Write data
        for row_num, issue in enumerate(issues, 2):
            for col_num, header in enumerate(headers, 1):
                value = issue.get(header, '')
                # Sanitize value for Excel compatibility
                if isinstance(value, str):
                    # Remove or replace problematic characters
                    value = value.replace('\x00', '').replace('\x01', '').replace('\x02', '')
                    # Limit cell content length to prevent Excel issues
                    if len(value) > 32767:  # Excel cell limit
                        value = value[:32764] + "..."
                ws.cell(row=row_num, column=col_num, value=value)
        
        # Auto-adjust column widths
        for column_cells in ws.columns:
            length = max(len(str(cell.value or '')) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50)
        
        wb.save(output_file)
        print(f"Exported {len(issues)} issues to {output_file}")
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters in markdown."""
        if not text:
            return ''
        return str(text).replace('|', '\\|').replace('\n', ' ')


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Export GitHub project board issues to various formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export to CSV (entire project)
  python project_board_tracker.py --owner myorg --project 1 --format csv --output report.csv

  # Export to Excel with filter (recommended)
  python project_board_tracker.py --owner neudesic --project 137 --filter 'milestone:"Release 1.10.5.8" -is:pr' --format excel --output report.xlsx

  # Export with multiple filter criteria
  python project_board_tracker.py --owner myorg --project 1 --filter 'state:open label:bug assignee:john' --format markdown --output bugs.md

  # Export view (deprecated - use --filter instead)
  python project_board_tracker.py --owner myorg --project 1 --view 43 --format excel --output report.xlsx

Environment Variables:
  GITHUB_TOKEN: GitHub personal access token (required)
        """
    )
    
    parser.add_argument(
        '--owner',
        required=True,
        help='Repository owner (organization or user)'
    )
    parser.add_argument(
        '--repo',
        help='Repository name (optional, for org-level projects)'
    )
    parser.add_argument(
        '--project',
        type=int,
        required=True,
        help='Project board number'
    )
    parser.add_argument(
        '--view',
        type=int,
        help='Project view number (optional, deprecated - use --filter instead)'
    )
    parser.add_argument(
        '--filter',
        type=str,
        help='GitHub search query to filter items (e.g., \'milestone:"Release 1.10.5.8" -is:pr\')'
    )
    parser.add_argument(
        '--format',
        choices=['csv', 'markdown', 'excel'],
        default='csv',
        help='Output format (default: csv)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: project_board_report.[format])'
    )
    parser.add_argument(
        '--token',
        help='GitHub personal access token (or set GITHUB_TOKEN environment variable)'
    )
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token or os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token is required. Set GITHUB_TOKEN environment variable or use --token")
        sys.exit(1)
    
    # Determine output file
    if not args.output:
        extension = 'csv' if args.format == 'csv' else ('md' if args.format == 'markdown' else 'xlsx')
        args.output = f'project_board_report.{extension}'
    
    try:
        # Initialize tracker
        tracker = GitHubProjectBoardTracker(token, args.owner, args.repo)
        
        # Fetch issues
        if args.filter:
            print(f"Fetching issues from project {args.project} with filter: {args.filter}")
            issues = tracker.fetch_project_board_issues(args.project, filter_query=args.filter)
        elif args.view:
            print(f"Fetching issues from project {args.project}, view {args.view}...")
            issues = tracker.fetch_project_board_issues(args.project, view_number=args.view)
        else:
            print(f"Fetching issues from project {args.project} (all items)...")
            issues = tracker.fetch_project_board_issues(args.project)
        print(f"Found {len(issues)} issues")
        
        # Export to requested format
        if args.format == 'csv':
            tracker.export_to_csv(issues, args.output)
        elif args.format == 'markdown':
            tracker.export_to_markdown(issues, args.output)
        elif args.format == 'excel':
            tracker.export_to_excel(issues, args.output)
        
        print("Export completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
