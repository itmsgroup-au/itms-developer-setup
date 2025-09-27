#!/usr/bin/env python3
"""
Monday.com Integration for ITMS Developer Setup
Handles task management with the new development board
"""

import os
import json
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class MondayDevIntegration:
    """Monday.com integration for development board"""
    
    def __init__(self):
        self.api_token = os.getenv('MONDAY_API_TOKEN')
        self.board_id = os.getenv('MONDAY_BOARD_ID', '7970370827')
        self.api_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        if not self.api_token:
            raise ValueError("MONDAY_API_TOKEN not found in environment variables")
    
    def make_query(self, query: str, variables: dict = None) -> dict:
        """Make GraphQL query to Monday.com API"""
        data = {"query": query}
        if variables:
            data["variables"] = variables
        
        response = requests.post(
            self.api_url,
            json=data,
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Monday.com API error: {response.status_code} - {response.text}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result["data"]
    
    def get_board_info(self) -> dict:
        """Get development board information and structure"""
        query = """
        query ($board_id: ID!) {
            boards (ids: [$board_id]) {
                id
                name
                description
                columns {
                    id
                    title
                    type
                    settings_str
                }
                groups {
                    id
                    title
                    color
                }
                items_page (limit: 50) {
                    items {
                        id
                        name
                        state
                        created_at
                        updated_at
                        column_values {
                            id
                            text
                            value
                        }
                        group {
                            id
                            title
                        }
                    }
                }
            }
        }
        """
        
        variables = {"board_id": self.board_id}
        return self.make_query(query, variables)
    
    def create_task(self, name: str, description: str = "", priority: str = "medium", 
                   task_type: str = "development", group_id: str = None) -> dict:
        """Create a new development task"""
        
        # Prepare column values based on board structure
        column_values = {
            "status": {"label": "Not Started"},
            "priority": {"label": priority.title()},
            "text": description,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add task type if supported
        if task_type:
            column_values["dropdown"] = {"labels": [task_type.title()]}
        
        query = """
        mutation ($board_id: ID!, $item_name: String!, $group_id: String, $column_values: JSON) {
            create_item (
                board_id: $board_id, 
                item_name: $item_name, 
                group_id: $group_id,
                column_values: $column_values
            ) {
                id
                name
                created_at
                group {
                    id
                    title
                }
            }
        }
        """
        
        variables = {
            "board_id": self.board_id,
            "item_name": name,
            "group_id": group_id,
            "column_values": json.dumps(column_values)
        }
        
        return self.make_query(query, variables)
    
    def update_task(self, item_id: str, status: str = None, progress: int = None, 
                   notes: str = None) -> dict:
        """Update an existing task"""
        column_values = {}
        
        if status:
            column_values["status"] = {"label": status}
        
        if progress is not None:
            column_values["numbers"] = progress
        
        if notes:
            column_values["long_text"] = notes
        
        query = """
        mutation ($board_id: ID!, $item_id: ID!, $column_values: JSON) {
            change_multiple_column_values (
                board_id: $board_id,
                item_id: $item_id,
                column_values: $column_values
            ) {
                id
                name
                updated_at
            }
        }
        """
        
        variables = {
            "board_id": self.board_id,
            "item_id": item_id,
            "column_values": json.dumps(column_values)
        }
        
        return self.make_query(query, variables)
    
    def get_my_tasks(self, status_filter: str = None) -> list:
        """Get current user's tasks"""
        board_data = self.get_board_info()
        items = board_data["boards"][0]["items_page"]["items"]
        
        # Filter by status if provided
        if status_filter:
            filtered_items = []
            for item in items:
                for col_val in item["column_values"]:
                    if col_val["title"].lower() == "status" and status_filter.lower() in col_val["text"].lower():
                        filtered_items.append(item)
                        break
            items = filtered_items
        
        return items
    
    def add_commit_update(self, item_id: str, commit_hash: str, commit_message: str) -> dict:
        """Add commit information to task"""
        
        # Get current notes
        current_updates = self.get_task_updates(item_id)
        
        # Add new commit update
        commit_update = f"""
**Commit {commit_hash[:8]}** - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{commit_message}

---
"""
        
        new_notes = commit_update + current_updates
        
        return self.update_task(item_id, notes=new_notes)
    
    def get_task_updates(self, item_id: str) -> str:
        """Get current task updates/notes"""
        query = """
        query ($item_id: ID!) {
            items (ids: [$item_id]) {
                id
                column_values {
                    id
                    title
                    text
                }
            }
        }
        """
        
        variables = {"item_id": item_id}
        result = self.make_query(query, variables)
        
        if result["items"]:
            for col_val in result["items"][0]["column_values"]:
                if col_val["title"].lower() in ["notes", "updates", "long text"]:
                    return col_val["text"] or ""
        
        return ""
    
    def test_connection(self) -> bool:
        """Test Monday.com API connection"""
        try:
            board_info = self.get_board_info()
            board = board_info["boards"][0]
            print(f"✅ Connected to Monday.com board: {board['name']}")
            print(f"📋 Board ID: {board['id']}")
            print(f"📊 Groups: {len(board['groups'])}")
            print(f"📝 Items: {len(board['items_page']['items'])}")
            return True
        except Exception as e:
            print(f"❌ Monday.com connection failed: {e}")
            return False


def main():
    """Main function for Monday.com operations"""
    if len(sys.argv) < 2:
        print("Monday.com Integration for ITMS Developer Setup")
        print("Usage:")
        print("  python3 monday_integration.py test-connection")
        print("  python3 monday_integration.py create-task \"Task Title\" [description] [priority]")
        print("  python3 monday_integration.py update-task <task_id> [status] [progress] [notes]")
        print("  python3 monday_integration.py show-tasks [status_filter]")
        return
    
    command = sys.argv[1]
    monday = MondayDevIntegration()
    
    try:
        if command == "test-connection":
            monday.test_connection()
            
        elif command == "create-task":
            if len(sys.argv) < 3:
                print("Task title required")
                return
            
            title = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
            
            result = monday.create_task(title, description, priority)
            print(f"✅ Task created: {result['create_item']['name']}")
            print(f"🆔 Task ID: {result['create_item']['id']}")
            
        elif command == "update-task":
            if len(sys.argv) < 3:
                print("Task ID required")
                return
            
            task_id = sys.argv[2]
            status = sys.argv[3] if len(sys.argv) > 3 else None
            progress = int(sys.argv[4]) if len(sys.argv) > 4 else None
            notes = sys.argv[5] if len(sys.argv) > 5 else None
            
            result = monday.update_task(task_id, status, progress, notes)
            print(f"✅ Task updated: {result['change_multiple_column_values']['name']}")
            
        elif command == "show-tasks":
            status_filter = sys.argv[2] if len(sys.argv) > 2 else None
            tasks = monday.get_my_tasks(status_filter)
            
            print(f"📋 Tasks ({len(tasks)}):")
            for task in tasks:
                status = "Unknown"
                # Find status column (usually the first status-type column)
                for col_val in task["column_values"]:
                    if col_val["text"] and "status" in str(col_val).lower():
                        status = col_val["text"] or "Not Set"
                        break
                
                print(f"  🔹 {task['name']} (ID: {task['id']}) - {status}")
                
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()