#!/usr/bin/env python3
"""
Git Integration for ITMS Developer Setup
Handles git commits linked to Monday.com tasks
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monday_integration import MondayDevIntegration


class GitIntegration:
    """Git integration with Monday.com task linking"""
    
    def __init__(self):
        self.monday = MondayDevIntegration()
        self.repo_root = self._find_git_root()
        
    def _find_git_root(self):
        """Find the git repository root"""
        current_dir = Path.cwd()
        
        while current_dir != current_dir.parent:
            if (current_dir / '.git').exists():
                return current_dir
            current_dir = current_dir.parent
        
        return Path.cwd()  # Fallback to current directory
    
    def _run_git_command(self, command):
        """Run a git command and return the result"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git command failed: {e.stderr}")
    
    def get_git_status(self):
        """Get current git status"""
        try:
            # Check for uncommitted changes
            status_output = self._run_git_command(['git', 'status', '--porcelain'])
            
            if not status_output:
                return {"has_changes": False, "files": []}
            
            # Parse status output
            files = []
            for line in status_output.split('\n'):
                if line.strip():
                    status = line[:2]
                    filename = line[3:]
                    files.append({"status": status, "file": filename})
            
            return {"has_changes": True, "files": files}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_branch_info(self):
        """Get detailed branch information"""
        try:
            info = {}
            
            # Current branch
            info["current_branch"] = self._run_git_command(['git', 'branch', '--show-current'])
            
            # Check if we have an upstream branch
            try:
                info["upstream"] = self._run_git_command(['git', 'rev-parse', '--abbrev-ref', '@{upstream}'])
                
                # Check ahead/behind status
                ahead_behind = self._run_git_command(['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'])
                if ahead_behind:
                    parts = ahead_behind.split('\t')
                    if len(parts) == 2:
                        info["ahead"] = int(parts[0])
                        info["behind"] = int(parts[1])
            except:
                info["upstream"] = None
                info["ahead"] = 0
                info["behind"] = 0
            
            # Get recent commits
            recent_commits = self._run_git_command(['git', 'log', '--oneline', '-5'])
            info["recent_commits"] = recent_commits.split('\n') if recent_commits else []
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_commit_for_task(self, task_id: str):
        """Get commits associated with a specific task"""
        try:
            # Search for commits mentioning the task ID
            search_output = self._run_git_command([
                'git', 'log', '--grep', task_id, '--oneline', '--all'
            ])
            
            if not search_output:
                return []
            
            commits = []
            for line in search_output.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
            
            return commits
            
        except Exception as e:
            return {"error": str(e)}
    
    def commit_to_task(self, task_id: str, commit_message: str, auto_stage: bool = True):
        """Commit changes and link to Monday.com task"""
        
        print(f"💾 Committing to Task ID: {task_id}")
        print("=" * 40)
        
        try:
            # Check git status
            status = self.get_git_status()
            
            if "error" in status:
                print(f"❌ Git error: {status['error']}")
                return False
            
            if not status["has_changes"]:
                print("⚠️  No changes to commit")
                return False
            
            # Show files to be committed
            print("📁 Files to commit:")
            for file_info in status["files"]:
                status_icon = {
                    "M ": "📝",  # Modified
                    "A ": "➕",  # Added
                    "D ": "❌",  # Deleted
                    "R ": "🔄",  # Renamed
                    "??": "❓"   # Untracked
                }.get(file_info["status"], "📄")
                
                print(f"  {status_icon} {file_info['file']}")
            
            # Stage files if requested
            if auto_stage:
                print("\n📦 Staging changes...")
                self._run_git_command(['git', 'add', '.'])
                print("✅ Changes staged")
            
            # Create commit message with task reference
            enhanced_message = f"{commit_message}\n\nTask: #{task_id}\nCommitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Commit changes
            print(f"\n💾 Creating commit...")
            commit_result = self._run_git_command(['git', 'commit', '-m', enhanced_message])
            
            # Get commit hash
            commit_hash = self._run_git_command(['git', 'rev-parse', 'HEAD'])
            
            print(f"✅ Commit created: {commit_hash[:8]}")
            
            # Update Monday.com task
            print(f"\n📋 Updating Monday.com task...")
            result = self.monday.add_commit_update(task_id, commit_hash, commit_message)
            
            # Also update the corresponding GitHub issue
            print(f"🐙 Updating GitHub issue...")
            try:
                from sync_manager import SyncManager
                sync_manager = SyncManager()
                sync_manager.update_github_issue_with_commit(task_id, commit_hash, commit_message)
            except Exception as e:
                print(f"⚠️  Could not update GitHub issue: {e}")
            
            print(f"✅ Task updated with commit information")
            
            # Show summary
            print(f"\n📊 Summary:")
            print(f"  🆔 Task ID: {task_id}")
            print(f"  💾 Commit: {commit_hash[:8]}")
            print(f"  📝 Message: {commit_message}")
            print(f"  📁 Files: {len(status['files'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error committing to task: {e}")
            return False
    
    def commit_interactive(self):
        """Interactive commit to task"""
        print("💾 Commit Changes to Task")
        print("=" * 30)
        
        try:
            # Check git status
            status = self.get_git_status()
            
            if "error" in status:
                print(f"❌ Git error: {status['error']}")
                return
            
            if not status["has_changes"]:
                print("⚠️  No changes to commit")
                return
            
            # Show current changes
            print("📁 Uncommitted changes:")
            for file_info in status["files"]:
                status_icon = {
                    "M ": "📝",  # Modified
                    "A ": "➕",  # Added
                    "D ": "❌",  # Deleted
                    "R ": "🔄",  # Renamed
                    "??": "❓"   # Untracked
                }.get(file_info["status"], "📄")
                
                print(f"  {status_icon} {file_info['file']}")
            
            # Get available tasks
            print(f"\n📋 Available tasks:")
            tasks = self.monday.get_my_tasks()
            
            if not tasks:
                print("No tasks found. Create a task first.")
                return
            
            # Show first 10 active tasks
            active_tasks = [t for t in tasks if not any(
                col["title"].lower() == "status" and "done" in col["text"].lower()
                for col in t["column_values"]
            )][:10]
            
            for i, task in enumerate(active_tasks):
                status = "Unknown"
                for col_val in task["column_values"]:
                    if col_val["title"].lower() == "status":
                        status = col_val["text"] or "Not Set"
                        break
                
                print(f"  {i+1}. {task['name']} (ID: {task['id']}) - {status}")
            
            # Get task selection
            task_input = input(f"\n🔍 Task number or ID (1-{len(active_tasks)}): ").strip()
            
            # Determine task ID
            task_id = None
            if task_input.isdigit():
                task_num = int(task_input)
                if 1 <= task_num <= len(active_tasks):
                    task_id = active_tasks[task_num - 1]["id"]
                    task_name = active_tasks[task_num - 1]["name"]
                    print(f"📝 Selected: {task_name}")
                else:
                    print("❌ Invalid task number")
                    return
            else:
                task_id = task_input
                print(f"🆔 Using Task ID: {task_id}")
            
            # Get commit message
            commit_message = input("\n💬 Commit message: ").strip()
            if not commit_message:
                print("❌ Commit message is required")
                return
            
            # Ask about staging
            stage_all = input("\n📦 Stage all changes? (Y/n): ").strip().lower()
            auto_stage = stage_all != 'n'
            
            # Perform commit
            success = self.commit_to_task(task_id, commit_message, auto_stage)
            
            if success:
                # Ask about push
                push_changes = input("\n🚀 Push changes to remote? (y/N): ").strip().lower()
                if push_changes == 'y':
                    try:
                        print("🚀 Pushing to remote...")
                        self._run_git_command(['git', 'push'])
                        print("✅ Changes pushed to remote")
                    except Exception as e:
                        print(f"⚠️  Push failed: {e}")
            
        except KeyboardInterrupt:
            print("\n❌ Commit cancelled")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_commit_history(self, task_id: str = None, limit: int = 10):
        """Show recent commits, optionally filtered by task"""
        print("📜 Recent Commits")
        print("=" * 20)
        
        try:
            # Get recent commits
            commit_format = '--pretty=format:%h|%s|%an|%ad'
            command = ['git', 'log', f'--max-count={limit}', commit_format, '--date=short']
            
            commit_output = self._run_git_command(command)
            
            if not commit_output:
                print("No commits found")
                return
            
            commits = []
            for line in commit_output.split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
            
            # Filter by task if specified
            if task_id:
                commits = [c for c in commits if f"#{task_id}" in c['message']]
                print(f"🔍 Filtered by Task ID: {task_id}")
            
            if not commits:
                print(f"No commits found" + (f" for task {task_id}" if task_id else ""))
                return
            
            # Display commits
            for commit in commits:
                print(f"\n💾 {commit['hash']} - {commit['date']}")
                print(f"   📝 {commit['message']}")
                print(f"   👤 {commit['author']}")
            
            print(f"\n📊 Showing {len(commits)} commits")
            
        except Exception as e:
            print(f"❌ Error getting commit history: {e}")


def main():
    """Main function for git integration"""
    if len(sys.argv) < 2:
        print("Git Integration for ITMS Developer Setup")
        print("Usage:")
        print("  python3 git_integration.py commit-interactive")
        print("  python3 git_integration.py commit-to-task <task_id> \"commit message\"")
        print("  python3 git_integration.py status")
        print("  python3 git_integration.py history [task_id] [limit]")
        return
    
    command = sys.argv[1]
    git_integration = GitIntegration()
    
    try:
        if command == "commit-interactive":
            git_integration.commit_interactive()
            
        elif command == "commit-to-task":
            if len(sys.argv) < 4:
                print("Usage: commit-to-task <task_id> \"commit message\"")
                return
            
            task_id = sys.argv[2]
            commit_message = sys.argv[3]
            
            git_integration.commit_to_task(task_id, commit_message)
            
        elif command == "status":
            status = git_integration.get_git_status()
            
            if "error" in status:
                print(f"❌ Git error: {status['error']}")
                return
            
            if not status["has_changes"]:
                print("✅ No uncommitted changes")
                return
            
            print("📁 Uncommitted changes:")
            for file_info in status["files"]:
                print(f"  {file_info['status']} {file_info['file']}")
                
        elif command == "history":
            task_id = sys.argv[2] if len(sys.argv) > 2 else None
            limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 10
            
            git_integration.show_commit_history(task_id, limit)
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()