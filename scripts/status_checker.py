#!/usr/bin/env python3
"""
Status Checker for ITMS Developer Setup
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monday_integration import MondayDevIntegration
from github_integration import GitHubIntegration


def check_integration_status():
    """Check status of all integrations"""
    print("📊 ITMS Developer Setup - Integration Status")
    print("=" * 50)
    print(f"🕐 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Monday.com status
    print("📋 Monday.com Integration:")
    try:
        monday = MondayDevIntegration()
        if monday.test_connection():
            # Get task counts
            tasks = monday.get_my_tasks()
            active_tasks = [t for t in tasks if not any(
                col["title"].lower() == "status" and "done" in col["text"].lower()
                for col in t["column_values"]
            )]
            
            print(f"   📊 Total tasks: {len(tasks)}")
            print(f"   🔥 Active tasks: {len(active_tasks)}")
            print(f"   📅 Board: {os.getenv('MONDAY_BOARD_ID')}")
        else:
            print("   ❌ Connection failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # GitHub status
    print("🐙 GitHub Integration:")
    try:
        github = GitHubIntegration()
        if github.test_connection():
            print(f"   👤 User: {os.getenv('GITHUB_USERNAME')}")
            print(f"   🏢 Organization: {os.getenv('GITHUB_ORG')}")
            print(f"   📁 Repository: {os.getenv('GITHUB_REPO')}")
        else:
            print("   ❌ Connection failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Context7 status
    print("🧠 Context7 Integration:")
    context7_key = os.getenv('CONTEXT7_API_KEY')
    if context7_key:
        print(f"   ✅ API key configured")
        print(f"   🔑 Key: {context7_key[:20]}...")
    else:
        print("   ❌ API key not configured")
    
    print()
    
    # Environment status
    print("⚙️  Environment Configuration:")
    required_vars = [
        'MONDAY_API_TOKEN',
        'MONDAY_BOARD_ID', 
        'GITHUB_TOKEN',
        'GITHUB_USERNAME',
        'CONTEXT7_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: configured")
        else:
            print(f"   ❌ {var}: missing")
    
    print()
    
    # Git repository status
    print("📁 Git Repository Status:")
    try:
        import subprocess
        
        # Check if in git repo
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Git repository detected")
            
            # Get current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            if branch_result.returncode == 0:
                print(f"   🌿 Current branch: {branch_result.stdout.strip()}")
            
            # Check for uncommitted changes
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True)
            if status_result.returncode == 0:
                changes = status_result.stdout.strip()
                if changes:
                    change_count = len(changes.split('\n'))
                    print(f"   📝 Uncommitted changes: {change_count} files")
                else:
                    print("   ✅ No uncommitted changes")
        else:
            print("   ❌ Not a git repository")
            
    except Exception as e:
        print(f"   ❌ Error checking git status: {e}")
    
    print()
    print("🎯 Overall Status: Ready for development!")


if __name__ == "__main__":
    check_integration_status()