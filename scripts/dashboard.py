#!/usr/bin/env python3
"""
Development Dashboard for ITMS Developer Setup
Board management and comprehensive project overview
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monday_integration import MondayDevIntegration


class DevelopmentDashboard:
    """Development dashboard with board management"""
    
    def __init__(self):
        self.monday = MondayDevIntegration()
        
    def list_available_boards(self, search_term=None):
        """List all available Monday.com boards, optionally filtered by search term"""
        if search_term:
            print(f"📋 Monday.com Boards - Search Results for '{search_term}'")
            print("=" * 50)
        else:
            print("📋 Available Monday.com Boards")
            print("=" * 40)
        
        try:
            # Query to get all boards the user has access to
            query = """
            query {
                boards (limit: 50) {
                    id
                    name
                    description
                    state
                    board_kind
                    items_count
                    updated_at
                    groups {
                        id
                        title
                        color
                    }
                }
            }
            """
            
            result = self.monday.make_query(query)
            boards = result["boards"]
            
            if not boards:
                print("❌ No boards found or access denied")
                return
            
            # Filter boards by search term if provided
            if search_term:
                search_lower = search_term.lower()
                filtered_boards = []
                for board in boards:
                    board_name = (board.get('name') or '').lower()
                    board_desc = (board.get('description') or '').lower()
                    
                    # Search in name and description
                    if search_lower in board_name or search_lower in board_desc:
                        filtered_boards.append(board)
                
                boards = filtered_boards
                
                if not boards:
                    print(f"❌ No boards found containing '{search_term}'")
                    print(f"\n💡 Try a different search term or use './manage-dev.sh list-boards' to see all boards")
                    return
                
                print(f"🔍 Found {len(boards)} boards matching '{search_term}':\n")
            else:
                print(f"🔍 Found {len(boards)} accessible boards:\n")
            
            for i, board in enumerate(boards, 1):
                state = board.get("state", "unknown")
                items_count = board.get("items_count", 0)
                updated = board.get("updated_at", "")[:10] if board.get("updated_at") else "Unknown"
                
                # Board status indicator
                status_icon = {
                    "active": "🟢",
                    "archived": "📦", 
                    "deleted": "🗑️"
                }.get(state, "⚪")
                
                print(f"  {i:2d}. {status_icon} {board['name']}")
                print(f"      📋 ID: {board['id']} | Items: {items_count} | Updated: {updated}")
                if board.get('description'):
                    print(f"      📄 {board['description'][:80]}...")
                
                # Show groups if available
                groups = board.get("groups", [])
                if groups:
                    group_names = [g["title"] for g in groups[:3]]
                    group_display = ", ".join(group_names)
                    if len(groups) > 3:
                        group_display += f" (+{len(groups)-3} more)"
                    print(f"      🗂️  Groups: {group_display}")
                print()
            
            print(f"📌 Current configured board: {self.monday.board_id}")
            
        except Exception as e:
            print(f"❌ Error fetching boards: {e}")
    
    def connect_to_board(self, board_id: str):
        """Connect to a specific board"""
        print(f"🔗 Connecting to Board {board_id}")
        print("=" * 35)
        
        try:
            # Temporarily set board ID to test connection
            original_board_id = self.monday.board_id
            self.monday.board_id = board_id
            
            # Test connection to new board
            board_info = self.monday.get_board_info()
            
            if not board_info.get("boards"):
                print(f"❌ Board {board_id} not found or not accessible")
                self.monday.board_id = original_board_id
                return False
            
            board = board_info["boards"][0]
            
            print(f"✅ Successfully connected to board!")
            print(f"📋 Name: {board['name']}")
            print(f"🆔 ID: {board['id']}")
            print(f"📊 Groups: {len(board.get('groups', []))}")
            print(f"📝 Items: {len(board.get('items_page', {}).get('items', []))}")
            
            # Show columns structure
            columns = board.get("columns", [])
            if columns:
                print(f"\n📋 Board Columns:")
                for col in columns:
                    print(f"  • {col['title']} ({col['type']})")
            
            # Update environment configuration suggestion
            print(f"\n💡 To make this permanent, update your .env file:")
            print(f"   MONDAY_BOARD_ID={board_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error connecting to board: {e}")
            self.monday.board_id = original_board_id
            return False
    
    def show_my_tasks(self):
        """Show tasks assigned to current user"""
        print("👤 My Assigned Tasks")
        print("=" * 25)
        
        try:
            # Get current user info first
            user_query = """
            query {
                me {
                    id
                    name
                    email
                }
            }
            """
            
            user_result = self.monday.make_query(user_query)
            current_user = user_result.get("me", {})
            user_id = current_user.get("id")
            user_name = current_user.get("name", "Unknown")
            
            print(f"👋 Hello {user_name}!")
            print(f"🆔 User ID: {user_id}\n")
            
            # Get board items with person column filtering
            board_info = self.monday.get_board_info()
            
            if not board_info.get("boards"):
                print("❌ No board information available")
                return
            
            board = board_info["boards"][0]
            items = board.get("items_page", {}).get("items", [])
            
            if not items:
                print("📝 No tasks found on this board")
                return
            
            # Filter tasks assigned to current user
            my_tasks = []
            
            for item in items:
                column_values = item.get("column_values", [])
                
                # Look for person/people columns
                for col_val in column_values:
                    if col_val.get("value"):
                        try:
                            # Parse JSON value for person columns
                            value_data = json.loads(col_val["value"])
                            
                            # Check if it's a person column with our user ID
                            if isinstance(value_data, dict) and "personsAndTeams" in value_data:
                                persons = value_data["personsAndTeams"]
                                for person in persons:
                                    if str(person.get("id")) == str(user_id):
                                        my_tasks.append(item)
                                        break
                        except (json.JSONDecodeError, KeyError):
                            # Skip invalid JSON or non-person columns
                            continue
            
            if not my_tasks:
                print(f"📋 No tasks currently assigned to {user_name}")
                print("\n💡 Tasks may be unassigned or assigned to others")
                print("   Use 'show-tasks' to see all board tasks")
                return
            
            print(f"📋 Found {len(my_tasks)} tasks assigned to you:\n")
            
            # Display my tasks
            for task in my_tasks:
                status = "Unknown"
                priority = "Medium"
                progress = "0%"
                
                # Extract status, priority, and progress
                for col_val in task["column_values"]:
                    text = col_val.get("text", "")
                    if text in ["Not Started", "In Progress", "Review", "Done", "Blocked"]:
                        status = text
                    elif text in ["High", "Medium", "Low"]:
                        priority = text
                    elif "%" in text:
                        progress = text
                
                # Status and priority icons
                status_icon = {
                    "Not Started": "⏸️",
                    "In Progress": "▶️", 
                    "Review": "🔍",
                    "Done": "✅",
                    "Blocked": "🚫"
                }.get(status, "❓")
                
                priority_icon = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢"
                }.get(priority, "⚪")
                
                created_date = task.get("created_at", "")[:10] if task.get("created_at") else "Unknown"
                
                print(f"{status_icon} {task['name']}")
                print(f"   🆔 ID: {task['id']} | {priority_icon} {priority} | 📊 {status} | 📈 {progress}")
                print(f"   📅 Created: {created_date}")
                print()
            
        except Exception as e:
            print(f"❌ Error fetching user tasks: {e}")
    
    def show_board_summary(self):
        """Show current board summary"""
        print("📊 Board Summary")
        print("=" * 20)
        
        try:
            board_info = self.monday.get_board_info()
            
            if not board_info.get("boards"):
                print("❌ No board information available")
                return
            
            board = board_info["boards"][0]
            items = board.get("items_page", {}).get("items", [])
            groups = board.get("groups", [])
            
            print(f"📋 Board: {board['name']}")
            print(f"🆔 ID: {board['id']}")
            print(f"📝 Total Items: {len(items)}")
            print(f"🗂️  Groups: {len(groups)}\n")
            
            # Status breakdown
            status_counts = {}
            priority_counts = {}
            
            for item in items:
                item_status = "Unknown"
                item_priority = "Medium"
                
                for col_val in item["column_values"]:
                    text = col_val.get("text", "")
                    if text in ["Not Started", "In Progress", "Review", "Done", "Blocked"]:
                        item_status = text
                    elif text in ["High", "Medium", "Low"]:
                        item_priority = text
                
                status_counts[item_status] = status_counts.get(item_status, 0) + 1
                priority_counts[item_priority] = priority_counts.get(item_priority, 0) + 1
            
            # Display status breakdown
            print("📊 Status Breakdown:")
            for status, count in status_counts.items():
                percentage = (count / len(items) * 100) if items else 0
                status_icon = {
                    "Not Started": "⏸️",
                    "In Progress": "▶️",
                    "Review": "🔍", 
                    "Done": "✅",
                    "Blocked": "🚫"
                }.get(status, "❓")
                print(f"   {status_icon} {status}: {count} ({percentage:.1f}%)")
            
            print(f"\n🎯 Priority Breakdown:")
            for priority, count in priority_counts.items():
                percentage = (count / len(items) * 100) if items else 0
                priority_icon = {
                    "High": "🔴",
                    "Medium": "🟡", 
                    "Low": "🟢"
                }.get(priority, "⚪")
                print(f"   {priority_icon} {priority}: {count} ({percentage:.1f}%)")
            
            # Recent activity
            recent_items = sorted(items, key=lambda x: x.get("updated_at", ""), reverse=True)[:3]
            if recent_items:
                print(f"\n🕒 Recent Activity:")
                for item in recent_items:
                    updated = item.get("updated_at", "")[:10] if item.get("updated_at") else "Unknown"
                    print(f"   • {item['name'][:40]}... (Updated: {updated})")
            
        except Exception as e:
            print(f"❌ Error fetching board summary: {e}")
    
    def show_full_dashboard(self):
        """Show complete development dashboard"""
        print("🎯 ITMS Development Dashboard")
        print("=" * 35)
        print()
        
        # Test connection first
        try:
            self.monday.test_connection()
            print()
        except:
            print("❌ Monday.com connection failed")
            return
        
        # Board summary
        self.show_board_summary()
        print("\n" + "="*50 + "\n")
        
        # My tasks
        self.show_my_tasks()
        print("\n" + "="*50 + "\n")
        
        # Quick actions
        print("🚀 Quick Actions:")
        print("  ./manage-dev.sh create-task     - Create new task")
        print("  ./manage-dev.sh show-tasks      - Show all tasks") 
        print("  ./manage-dev.sh pull-tasks      - Pull latest from Monday")
        print("  ./manage-dev.sh sync both       - Sync Monday ↔ GitHub")
        print()
        
        print("📋 Board Management:")
        print("  python3 scripts/dashboard.py list-boards    - List available boards")
        print("  python3 scripts/dashboard.py connect <id>   - Connect to different board")
        print()


def main():
    """Main function for dashboard operations"""
    if len(sys.argv) < 2:
        print("Development Dashboard for ITMS Developer Setup")
        print("Usage:")
        print("  python3 dashboard.py show-full")
        print("  python3 dashboard.py list-boards [search_term]") 
        print("  python3 dashboard.py connect <board_id>")
        print("  python3 dashboard.py my-tasks")
        print("  python3 dashboard.py board-summary")
        return
    
    command = sys.argv[1]
    dashboard = DevelopmentDashboard()
    
    try:
        if command == "show-full":
            dashboard.show_full_dashboard()
            
        elif command == "list-boards":
            search_term = sys.argv[2] if len(sys.argv) > 2 else None
            dashboard.list_available_boards(search_term)
            
        elif command == "connect":
            if len(sys.argv) < 3:
                print("Board ID required")
                return
            board_id = sys.argv[2]
            dashboard.connect_to_board(board_id)
            
        elif command == "my-tasks":
            dashboard.show_my_tasks()
            
        elif command == "board-summary":
            dashboard.show_board_summary()
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()