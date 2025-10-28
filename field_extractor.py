#!/usr/bin/env python3
"""
AI Field Extractor

Extracts structured fields from GitHub issue content using Azure OpenAI.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests


class ExtractionCache:
    """Cache AI extractions to avoid reprocessing and reduce API costs."""
    
    def __init__(self, cache_dir: str = '.ai_cache'):
        """Initialize cache with directory path."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / 'extractions.json'
        self.data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save(self):
        """Save cache to disk."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, issue_number: int, issue_updated_at: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached extraction by issue number.
        
        Args:
            issue_number: GitHub issue number
            issue_updated_at: ISO timestamp of when issue was last updated
            
        Returns:
            Cached extraction if valid, None otherwise
        """
        key = str(issue_number)
        if key not in self.data:
            return None
        
        cached = self.data[key]
        
        # If re-extraction enabled and issue was updated, invalidate cache
        if issue_updated_at:
            cached_time = cached.get('issue_updated_at')
            if cached_time and issue_updated_at > cached_time:
                return None  # Issue updated since cache
        
        return cached.get('fields')
    
    def set(self, issue_number: int, extracted_fields: Dict[str, str], 
            model: str, issue_updated_at: str = None):
        """
        Cache extraction result.
        
        Args:
            issue_number: GitHub issue number
            extracted_fields: Extracted field values
            model: Model used for extraction
            issue_updated_at: ISO timestamp of when issue was last updated
        """
        self.data[str(issue_number)] = {
            'fields': extracted_fields,
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'issue_updated_at': issue_updated_at
        }
        self._save()


class AIFieldExtractor:
    """Extracts structured fields from GitHub issue content using Azure OpenAI."""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str = 'gpt-4.1-mini', 
                 cache_dir: str = '.ai_cache', github_token: str = None):
        """
        Initialize the AI field extractor.
        
        Args:
            endpoint: Azure OpenAI endpoint URL (full URL with deployment and API version)
            api_key: Azure OpenAI API key
            deployment: Deployment name (included in endpoint)
            cache_dir: Directory for caching extractions
            github_token: GitHub token for fetching issue content
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.cache = ExtractionCache(cache_dir)
        self.github_token = github_token
    
    def extract_fields(self, issue_data: Dict[str, Any], repo_owner: str, 
                      repo_name: str) -> Dict[str, str]:
        """
        Extract missing fields from issue content.
        
        Args:
            issue_data: Issue data from GitHub API (must include number, updated_at)
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Dictionary of extracted fields with [AI-Extracted] annotation
        """
        issue_number = issue_data.get('number')
        issue_updated_at = issue_data.get('updatedAt') or issue_data.get('updated_at')
        
        # Check cache first
        if cached := self.cache.get(issue_number, issue_updated_at):
            print(f"  Using cached extraction for issue #{issue_number}")
            return self._annotate_fields(cached)
        
        print(f"  Extracting fields for issue #{issue_number}...")
        
        # Fetch full issue content
        issue_content = self._fetch_issue_content(issue_number, repo_owner, repo_name)
        
        # Build extraction prompt
        prompt = self._build_extraction_prompt(
            issue_content['body'],
            issue_content['comments'],
            issue_content['labels']
        )
        
        # Call Azure OpenAI
        response = self._call_azure_openai(prompt)
        
        # Parse JSON response
        extracted = self._parse_response(response)
        
        # Cache result
        self.cache.set(issue_number, extracted, self.deployment, issue_updated_at)
        
        return self._annotate_fields(extracted)
    
    def _fetch_issue_content(self, issue_number: int, repo_owner: str, 
                            repo_name: str) -> Dict[str, Any]:
        """
        Fetch full issue content from GitHub REST API.
        
        Args:
            issue_number: Issue number
            repo_owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Dictionary with body, comments, and labels
        """
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Fetch issue details
        issue_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}'
        issue_response = requests.get(issue_url, headers=headers)
        issue_response.raise_for_status()
        issue = issue_response.json()
        
        # Fetch comments
        comments_url = issue['comments_url']
        comments_response = requests.get(comments_url, headers=headers)
        comments_response.raise_for_status()
        comments = comments_response.json()
        
        return {
            'body': issue.get('body', ''),
            'comments': comments,
            'labels': [label['name'] for label in issue.get('labels', [])]
        }
    
    def _build_extraction_prompt(self, body: str, comments: List[Dict], 
                                labels: List[str]) -> List[Dict[str, str]]:
        """
        Build a prompt that requests specific fields in JSON format.
        
        Args:
            body: Issue body (markdown)
            comments: List of comment objects
            labels: List of label names
            
        Returns:
            Messages array for chat completion
        """
        # Format comments for context
        comments_text = "\n\n".join([
            f"Comment by {c['user']['login']} on {c['created_at']}:\n{c['body']}"
            for c in comments[:10]  # Limit to 10 most recent
        ]) if comments else "No comments"
        
        system_prompt = """You are a requirements analyst extracting structured data from GitHub issues.

Extract the following fields if present in the issue body or comments:

1. business_need: Why this issue matters (business value, problem being solved). Look for sections like "Business Need", "Why", "Problem Statement", "Value".

2. acceptance_criteria: What defines completion (testable conditions). Look for sections like "Acceptance Criteria", "Definition of Done", "Requirements", "Success Criteria".

3. test_case_ids: Test case references (comma-separated IDs or URLs). Look for test case numbers, QA references, or test plan links.

4. test_evidence_url: Links to test results, test reports, or QA validation. Look for URLs to test systems, test run results, or evidence of testing.

5. design_artifacts_url: Links to design documents, diagrams, architecture docs, mockups, or specifications.

6. risk: Risk level and description. Look for "Risk:" labels or sections describing security, technical, or business risks. Extract both level (High/Medium/Low) and description.

7. release_version: Target release version or milestone. Look for version numbers, release names, or milestone references.

8. change_log: Summary of what changed or will change. Look for "Changes", "What's Changed", "Modifications", or implementation details.

IMPORTANT: 
- Return "N/A" for any field not found or not clearly stated
- Return ONLY valid JSON with these exact field names
- Do not make assumptions - only extract what is explicitly stated
- Keep extracted values concise (under 200 chars per field)"""

        user_prompt = f"""Issue Content:

{body or 'No description provided'}

---

Comments:
{comments_text}

---

Labels: {', '.join(labels) if labels else 'None'}

---

Extract the structured fields as JSON."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _call_azure_openai(self, messages: List[Dict[str, str]]) -> str:
        """
        Call Azure OpenAI API.
        
        Args:
            messages: Chat messages array
            
        Returns:
            Response text (should be JSON)
        """
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
        
        payload = {
            'messages': messages,
            'temperature': 0.1,  # Low temperature for consistent extraction
            'max_tokens': 800,
            'response_format': {'type': 'json_object'}
        }
        
        response = requests.post(self.endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse JSON response from AI model.
        
        Args:
            response_text: JSON string from AI
            
        Returns:
            Dictionary of extracted fields
        """
        try:
            extracted = json.loads(response_text)
            
            # Ensure all expected fields are present
            fields = {
                'business_need': extracted.get('business_need', 'N/A'),
                'acceptance_criteria': extracted.get('acceptance_criteria', 'N/A'),
                'test_case_ids': extracted.get('test_case_ids', 'N/A'),
                'test_evidence_url': extracted.get('test_evidence_url', 'N/A'),
                'design_artifacts_url': extracted.get('design_artifacts_url', 'N/A'),
                'risk': extracted.get('risk', 'N/A'),
                'release_version': extracted.get('release_version', 'N/A'),
                'change_log': extracted.get('change_log', 'N/A')
            }
            
            return fields
            
        except json.JSONDecodeError as e:
            print(f"  Warning: Failed to parse AI response as JSON: {e}")
            return {
                'business_need': 'N/A',
                'acceptance_criteria': 'N/A',
                'test_case_ids': 'N/A',
                'test_evidence_url': 'N/A',
                'design_artifacts_url': 'N/A',
                'risk': 'N/A',
                'release_version': 'N/A',
                'change_log': 'N/A'
            }
    
    def _annotate_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        """
        Add [AI-Extracted] annotation to non-N/A fields.
        
        Args:
            fields: Extracted fields
            
        Returns:
            Fields with annotations
        """
        annotated = {}
        for key, value in fields.items():
            if value and value != 'N/A':
                annotated[key] = f"{value} [AI-Extracted]"
            else:
                annotated[key] = value
        return annotated
