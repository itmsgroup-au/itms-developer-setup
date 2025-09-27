#!/usr/bin/env python3
"""
Task Manager for ITMS Developer Setup
Clear interface for task management following manage-odoo.sh pattern
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monday_integration import MondayDevIntegration


class TaskManager:
    """Task management interface"""
    
    def __init__(self):
        self.monday = MondayDevIntegration()
        
    def show_current_tasks(self):
        """Show current development tasks in a clear format"""
        print("📋 Current Development Tasks")
        print("=" * 50)
        
        try:
            # First try to get user-assigned tasks
            tasks = self.monday.get_my_tasks(user_filter=True)
            
            # If no assigned tasks found, show all tasks
            if not tasks:
                print("📋 No tasks assigned to you. Showing all board tasks:\n")
                tasks = self.monday.get_my_tasks(user_filter=False)
                
                if not tasks:
                    print("🎉 No tasks found on this board. Use 'create-task' to add new tasks.")
                    return
            
            # Group tasks by status
            task_groups = {}
            for task in tasks:
                status = "Unknown"
                priority = "Medium"
                
                for col_val in task["column_values"]:
                    # Simple text-based detection for status and priority
                    text = col_val["text"] or ""
                    if text in ["Not Started", "In Progress", "Review", "Done", "Blocked"]:
                        status = text
                    elif text in ["High", "Medium", "Low"]:
                        priority = text
                
                if status not in task_groups:
                    task_groups[status] = []
                
                task_groups[status].append({
                    "id": task["id"],
                    "name": task["name"],
                    "priority": priority,
                    "created": task["created_at"]
                })
            
            # Display tasks by status
            status_order = ["Not Started", "In Progress", "Review", "Done", "Unknown"]
            
            for status in status_order:
                if status in task_groups:
                    print(f"\n🔸 {status} ({len(task_groups[status])})")
                    print("-" * 30)
                    
                    for task in task_groups[status]:
                        priority_icon = {
                            "High": "🔴",
                            "Medium": "🟡", 
                            "Low": "🟢"
                        }.get(task["priority"], "⚪")
                        
                        created_date = task["created"][:10] if task["created"] else "Unknown"
                        print(f"  {priority_icon} {task['name']}")
                        print(f"     ID: {task['id']} | Created: {created_date}")
            
            print(f"\n📊 Total: {len(tasks)} tasks")
            
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
    
    def pull_from_monday(self):
        """Pull latest tasks from Monday.com"""
        print("📥 Pulling Tasks from Monday.com")
        print("=" * 40)
        
        try:
            board_info = self.monday.get_board_info()
            board = board_info["boards"][0]
            items = board["items_page"]["items"]
            
            print(f"📋 Board: {board['name']}")
            print(f"🔄 Synced {len(items)} tasks")
            
            # Show recent updates
            recent_tasks = sorted(items, key=lambda x: x.get("updated_at", ""), reverse=True)[:5]
            
            print(f"\n📌 Recently Updated:")
            for task in recent_tasks:
                updated_date = task.get("updated_at", "")[:10] if task.get("updated_at") else "Unknown"
                print(f"  • {task['name']} (Updated: {updated_date})")
            
            print(f"\n✅ Sync complete! Use 'show-tasks' to view all tasks.")
            
        except Exception as e:
            print(f"❌ Error pulling tasks: {e}")
    
    def create_task_interactive(self):
        """Interactive task creation"""
        print("➕ Create New Development Task")
        print("=" * 35)
        
        try:
            # Get task details
            title = input("📝 Task title: ").strip()
            if not title:
                print("❌ Task title is required")
                return
            
            description = input("📄 Description (optional): ").strip()
            
            print("\n🎯 Priority levels:")
            print("  1. Low")
            print("  2. Medium (default)")
            print("  3. High")
            
            priority_choice = input("Priority (1-3) [2]: ").strip() or "2"
            priority_map = {"1": "low", "2": "medium", "3": "high"}
            priority = priority_map.get(priority_choice, "medium")
            
            print("\n🔧 Task types:")
            print("  1. Development (default)")
            print("  2. Bug Fix")
            print("  3. Testing")
            print("  4. Documentation")
            print("  5. Research")
            
            type_choice = input("Task type (1-5) [1]: ").strip() or "1"
            type_map = {
                "1": "development",
                "2": "bug fix", 
                "3": "testing",
                "4": "documentation",
                "5": "research"
            }
            task_type = type_map.get(type_choice, "development")
            
            # Create the task
            print(f"\n🚀 Creating task: {title}")
            result = self.monday.create_task(title, description, priority, task_type)
            
            task_id = result["create_item"]["id"]
            task_name = result["create_item"]["name"]
            
            print(f"✅ Task created successfully!")
            print(f"🆔 Task ID: {task_id}")
            print(f"📝 Task: {task_name}")
            print(f"🎯 Priority: {priority.title()}")
            print(f"🔧 Type: {task_type.title()}")
            
        except KeyboardInterrupt:
            print("\n❌ Task creation cancelled")
        except Exception as e:
            print(f"❌ Error creating task: {e}")
    
    def update_task_interactive(self):
        """Interactive task update"""
        print("📝 Update Task Progress")
        print("=" * 30)
        
        try:
            # Show current tasks for reference
            print("📋 Current tasks:")
            tasks = self.monday.get_my_tasks()
            
            if not tasks:
                print("No tasks found. Create a task first.")
                return
            
            # Show first 10 tasks
            for i, task in enumerate(tasks[:10]):
                status = "Unknown"
                for col_val in task["column_values"]:
                    if col_val["title"].lower() == "status":
                        status = col_val["text"] or "Not Set"
                        break
                
                print(f"  {i+1}. {task['name']} (ID: {task['id']}) - {status}")
            
            if len(tasks) > 10:
                print(f"  ... and {len(tasks) - 10} more tasks")
            
            # Get task selection
            task_input = input(f"\n🔍 Task ID or number (1-{min(10, len(tasks))}): ").strip()
            
            # Determine task ID
            task_id = None
            if task_input.isdigit():
                task_num = int(task_input)
                if 1 <= task_num <= len(tasks):
                    task_id = tasks[task_num - 1]["id"]
                else:
                    print("❌ Invalid task number")
                    return
            else:
                task_id = task_input
            
            # Get update details
            print(f"\n📊 Status options:")
            print("  1. Not Started")
            print("  2. In Progress") 
            print("  3. Review")
            print("  4. Done")
            print("  5. Blocked")
            
            status_choice = input("New status (1-5, or press Enter to skip): ").strip()
            status_map = {
                "1": "Not Started",
                "2": "In Progress",
                "3": "Review", 
                "4": "Done",
                "5": "Blocked"
            }
            new_status = status_map.get(status_choice) if status_choice else None
            
            # Get progress
            progress_input = input("Progress percentage (0-100, or press Enter to skip): ").strip()
            progress = int(progress_input) if progress_input.isdigit() else None
            
            # Get notes
            notes = input("Progress notes (or press Enter to skip): ").strip() or None
            
            # Update the task
            print(f"\n🔄 Updating task...")
            result = self.monday.update_task(task_id, new_status, progress, notes)
            
            print(f"✅ Task updated successfully!")
            print(f"📝 Task: {result['change_multiple_column_values']['name']}")
            if new_status:
                print(f"📊 Status: {new_status}")
            if progress is not None:
                print(f"📈 Progress: {progress}%")
            
        except KeyboardInterrupt:
            print("\n❌ Update cancelled")
        except Exception as e:
            print(f"❌ Error updating task: {e}")


def main():
    """Main function for task management"""
    if len(sys.argv) < 2:
        print("Task Manager for ITMS Developer Setup")
        print("Usage:")
        print("  python3 task_manager.py show-current")
        print("  python3 task_manager.py pull-from-monday")
        print("  python3 task_manager.py create-interactive")
        print("  python3 task_manager.py update-interactive")
        print("  python3 task_manager.py create-task \"Title\" [description] [priority]")
        print("  python3 task_manager.py update-task <task_id> [status] [progress] [notes]")
        return
    
    command = sys.argv[1]
    manager = TaskManager()
    
    try:
        if command == "show-current":
            manager.show_current_tasks()
            
        elif command == "pull-from-monday":
            manager.pull_from_monday()
            
        elif command == "create-interactive":
            manager.create_task_interactive()
            
        elif command == "update-interactive":
            manager.update_task_interactive()
            
        elif command == "create-task":
            if len(sys.argv) < 3:
                print("Task title required")
                return
            
            title = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
            
            result = manager.monday.create_task(title, description, priority)
            print(f"✅ Task created: {result['create_item']['name']}")
            print(f"🆔 Task ID: {result['create_item']['id']}")
            
        elif command == "update-task":
            if len(sys.argv) < 3:
                print("Task ID required")
                return
            
            task_id = sys.argv[2]
            status = sys.argv[3] if len(sys.argv) > 3 else None
            progress = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
            notes = sys.argv[5] if len(sys.argv) > 5 else None
            
            result = manager.monday.update_task(task_id, status, progress, notes)
            print(f"✅ Task updated: {result['change_multiple_column_values']['name']}")
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()