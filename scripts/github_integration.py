#!/usr/bin/env python3
"""
GitHub Integration for ITMS Developer Setup
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()


class GitHubIntegration:
    """GitHub integration for ITMS Developer Setup"""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME')
        self.org = os.getenv('GITHUB_ORG')
        self.repo = os.getenv('GITHUB_REPO')
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def test_connection(self):
        """Test GitHub API connection"""
        try:
            # Test authentication
            response = requests.get("https://api.github.com/user", headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Connected to GitHub as: {user_data['login']}")
                
                # Test repository access if configured
                if self.repo:
                    repo_response = requests.get(f"https://api.github.com/repos/{self.repo}", headers=self.headers)
                    if repo_response.status_code == 200:
                        repo_data = repo_response.json()
                        print(f"✅ Repository access: {repo_data['full_name']}")
                        print(f"📊 Stars: {repo_data['stargazers_count']} | Forks: {repo_data['forks_count']}")
                    else:
                        print(f"⚠️  Repository access failed: {repo_response.status_code}")
                
                return True
            else:
                print(f"❌ GitHub authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub connection error: {e}")
            return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("GitHub Integration for ITMS Developer Setup")
        print("Usage:")
        print("  python3 github_integration.py test-connection")
        return
    
    command = sys.argv[1]
    
    try:
        github = GitHubIntegration()
        
        if command == "test-connection":
            github.test_connection()
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()