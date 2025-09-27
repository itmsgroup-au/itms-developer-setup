#!/usr/bin/env python3
"""
Sync Manager for ITMS Developer Setup
Handles bidirectional synchronization between Monday.com and GitHub
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monday_integration import MondayDevIntegration
from github_integration import GitHubIntegration


class SyncManager:
    """Manages synchronization between Monday.com and GitHub"""
    
    def __init__(self):
        self.monday = MondayDevIntegration()
        self.github = GitHubIntegration()
        
    def sync_monday_to_github(self):
        """Sync Monday.com tasks to GitHub issues"""
        print("🔄 Syncing Monday.com → GitHub")
        print("=" * 35)
        
        try:
            # Get all Monday.com tasks
            tasks = self.monday.get_my_tasks(user_filter=False)
            
            if not tasks:
                print("📋 No tasks found on Monday.com board")
                return
            
            print(f"📋 Found {len(tasks)} tasks on Monday.com")
            
            # Get existing GitHub issues to avoid duplicates
            existing_issues = self.github.get_repository_issues()
            
            synced_count = 0
            for task in tasks:
                task_name = task['name']
                task_id = task['id']
                
                # Check if issue already exists (by task name or Monday ID in title)
                issue_exists = False
                for issue in existing_issues:
                    if (task_name.lower() in issue['title'].lower() or 
                        f"Monday-{task_id}" in issue['title']):
                        issue_exists = True
                        break
                
                if not issue_exists:
                    # Extract task details
                    priority = "medium"
                    status = "Under discovery"
                    area = ""
                    
                    for col_val in task["column_values"]:
                        text = col_val.get("text", "")
                        if text in ["High", "Medium", "Low"]:
                            priority = text.lower()
                        elif text in ["Under discovery", "Ready for Development", "Needs information"]:
                            status = text
                        elif text and len(text) < 50:  # Likely area/category
                            area = text
                    
                    # Create GitHub issue with enhanced information
                    issue_body = f"""**Monday.com Task**: {task_id}
**Priority**: {priority.title()}
**Status**: {status}
**Area**: {area}

## Task Details
This issue was automatically synced from Monday.com board for tracking development progress.

## Development Progress
- [ ] Initial analysis and planning
- [ ] Implementation
- [ ] Testing and validation
- [ ] Code review
- [ ] Deployment

## Commit History
*Commits linked to this task will appear here automatically*

---
*Auto-synced from Monday.com on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Board: Product Backlog (RICE Methodology)*"""
                    
                    # Create issue with Monday ID in title for tracking
                    issue_title = f"{task_name} [Monday-{task_id}]"
                    
                    try:
                        issue = self.github.create_issue(issue_title, issue_body, priority)
                        print(f"✅ Created GitHub issue: {issue['title']}")
                        synced_count += 1
                    except Exception as e:
                        print(f"❌ Failed to create issue for '{task_name}': {e}")
                else:
                    print(f"⏭️  Skipped '{task_name}' (already exists in GitHub)")
            
            print(f"\n🎯 Sync complete: {synced_count} new issues created")
            
        except Exception as e:
            print(f"❌ Error syncing Monday → GitHub: {e}")
    
    def sync_github_to_monday(self):
        """Sync GitHub issues to Monday.com tasks"""
        print("🔄 Syncing GitHub → Monday.com")
        print("=" * 35)
        
        try:
            # Get GitHub issues
            issues = self.github.get_repository_issues()
            
            if not issues:
                print("📋 No issues found in GitHub repository")
                return
            
            print(f"📋 Found {len(issues)} issues in GitHub")
            
            # Get existing Monday tasks to avoid duplicates
            existing_tasks = self.monday.get_my_tasks(user_filter=False)
            
            synced_count = 0
            for issue in issues:
                issue_title = issue['title']
                issue_number = issue['number']
                
                # Check if task already exists (by issue title or GitHub ID)
                task_exists = False
                for task in existing_tasks:
                    if (issue_title.lower() in task['name'].lower() or 
                        f"GitHub-{issue_number}" in task['name'] or
                        f"Monday-" in issue_title):  # Skip Monday-synced issues
                        task_exists = True
                        break
                
                if not task_exists and "Monday-" not in issue_title:
                    # Extract issue details
                    labels = [label['name'] for label in issue.get('labels', [])]
                    priority = "medium"
                    
                    # Map GitHub labels to priority
                    if any(label.lower() in ['high', 'critical', 'urgent'] for label in labels):
                        priority = "high"
                    elif any(label.lower() in ['low', 'minor'] for label in labels):
                        priority = "low"
                    
                    # Create task description
                    description = f"GitHub Issue #{issue_number}: {issue.get('body', '')[:200]}..."
                    
                    # Create Monday task with GitHub ID in title
                    task_title = f"{issue_title} [GitHub-{issue_number}]"
                    
                    try:
                        task = self.monday.create_task(task_title, description, priority)
                        print(f"✅ Created Monday task: {task['create_item']['name']}")
                        synced_count += 1
                    except Exception as e:
                        print(f"❌ Failed to create task for issue #{issue_number}: {e}")
                else:
                    if "Monday-" in issue_title:
                        print(f"⏭️  Skipped GitHub issue #{issue_number} (synced from Monday)")
                    else:
                        print(f"⏭️  Skipped GitHub issue #{issue_number} (already exists in Monday)")
            
            print(f"\n🎯 Sync complete: {synced_count} new tasks created")
            
        except Exception as e:
            print(f"❌ Error syncing GitHub → Monday: {e}")
    
    def sync_bidirectional(self):
        """Perform bidirectional sync"""
        print("🔄 Bidirectional Sync: Monday.com ↔ GitHub")
        print("=" * 45)
        print()
        
        # Sync Monday → GitHub
        self.sync_monday_to_github()
        print()
        
        # Sync GitHub → Monday
        self.sync_github_to_monday()
        print()
        
        print("✅ Bidirectional sync complete!")
    
    def show_sync_status(self):
        """Show current sync status"""
        print("📊 Sync Status Report")
        print("=" * 25)
        
        try:
            # Get Monday tasks
            monday_tasks = self.monday.get_my_tasks(user_filter=False)
            github_issues = self.github.get_repository_issues()
            
            print(f"📋 Monday.com tasks: {len(monday_tasks)}")
            print(f"🐙 GitHub issues: {len(github_issues)}")
            
            # Count synced items
            monday_synced = sum(1 for task in monday_tasks if "GitHub-" in task['name'])
            github_synced = sum(1 for issue in github_issues if "Monday-" in issue['title'])
            
            print(f"🔄 Monday tasks synced from GitHub: {monday_synced}")
            print(f"🔄 GitHub issues synced from Monday: {github_synced}")
            
            # Show unsynced items
            monday_unsynced = [task for task in monday_tasks if "GitHub-" not in task['name']]
            github_unsynced = [issue for issue in github_issues if "Monday-" not in issue['title']]
            
            if monday_unsynced:
                print(f"\n📋 Unsynced Monday tasks ({len(monday_unsynced)}):")
                for task in monday_unsynced[:5]:  # Show first 5
                    print(f"  • {task['name']}")
                if len(monday_unsynced) > 5:
                    print(f"  ... and {len(monday_unsynced) - 5} more")
            
            if github_unsynced:
                print(f"\n🐙 Unsynced GitHub issues ({len(github_unsynced)}):")
                for issue in github_unsynced[:5]:  # Show first 5
                    print(f"  • #{issue['number']}: {issue['title']}")
                if len(github_unsynced) > 5:
                    print(f"  ... and {len(github_unsynced) - 5} more")
            
        except Exception as e:
            print(f"❌ Error getting sync status: {e}")
    
    def update_github_issue_with_commit(self, task_id: str, commit_hash: str, commit_message: str):
        """Update corresponding GitHub issue with commit information"""
        try:
            # Find the GitHub issue for this Monday task
            issues = self.github.get_repository_issues()
            target_issue = None
            
            for issue in issues:
                if f"Monday-{task_id}" in issue['title']:
                    target_issue = issue
                    break
            
            if not target_issue:
                print(f"⚠️  No GitHub issue found for Monday task {task_id}")
                return False
            
            # Update the issue description with commit information
            current_body = target_issue.get('body', '')
            
            # Add commit to the commit history section
            commit_entry = f"\n### Commit {commit_hash[:8]} - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            commit_entry += f"```\n{commit_message}\n```\n"
            
            # Find the commit history section and add the new commit
            if "## Commit History" in current_body:
                # Replace the placeholder text with actual commit
                updated_body = current_body.replace(
                    "*Commits linked to this task will appear here automatically*",
                    f"*Latest commits for this task:*{commit_entry}"
                )
                # If there are already commits, add to them
                if "*Latest commits for this task:*" in current_body:
                    commit_section_start = updated_body.find("*Latest commits for this task:*")
                    if commit_section_start != -1:
                        insert_point = updated_body.find("\n---", commit_section_start)
                        if insert_point != -1:
                            updated_body = updated_body[:insert_point] + commit_entry + updated_body[insert_point:]
            else:
                updated_body = current_body + f"\n\n## Commit History{commit_entry}"
            
            # Update the GitHub issue
            self.github.update_issue(target_issue['number'], body=updated_body)
            print(f"✅ Updated GitHub issue #{target_issue['number']} with commit {commit_hash[:8]}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating GitHub issue: {e}")
            return False


def main():
    """Main function for sync operations"""
    if len(sys.argv) < 2:
        print("Sync Manager for ITMS Developer Setup")
        print("Usage:")
        print("  python3 sync_manager.py sync [direction]")
        print("  python3 sync_manager.py status")
        print("")
        print("Directions:")
        print("  both         - Bidirectional sync (default)")
        print("  to-github    - Monday.com → GitHub only")
        print("  to-monday    - GitHub → Monday.com only")
        return
    
    command = sys.argv[1]
    sync_manager = SyncManager()
    
    try:
        if command == "sync":
            direction = sys.argv[2] if len(sys.argv) > 2 else "both"
            
            if direction == "both":
                sync_manager.sync_bidirectional()
            elif direction == "to-github":
                sync_manager.sync_monday_to_github()
            elif direction == "to-monday":
                sync_manager.sync_github_to_monday()
            else:
                print(f"Unknown direction: {direction}")
                
        elif command == "status":
            sync_manager.show_sync_status()
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()