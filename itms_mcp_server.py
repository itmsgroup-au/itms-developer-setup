#!/usr/bin/env python3
"""
ITMS MCP Server - Simple interface for AI tools
Provides Monday.com and workflow integration

Features:
- Intelligent sub-task creation based on task content analysis
- Context-aware templates for Odoo development, research, and general tasks
- No emoji usage (clean, professional output)
- Automatic task type detection and appropriate sub-task generation
"""

import json
import sys
import os
from pathlib import Path
import requests
from datetime import datetime

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    try:
        # Try current directory first
        env_file = Path('.env')
        if not env_file.exists():
            # Try script directory
            env_file = Path(__file__).parent / '.env'

        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    except NameError:
        # __file__ not available, try current directory only
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value

# Load .env file on import
try:
    load_env_file()
except Exception as e:
    # Don't let env loading break the server
    pass

class ITMSMCPServer:
    """Simple MCP server for ITMS workflow integration"""
    
    def __init__(self):
        self.monday_token = os.getenv('MONDAY_API_TOKEN')
        self.board_id = os.getenv('MONDAY_BOARD_ID', '18058278926')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Load working context if available
        try:
            context_file = Path('working_context.json')
            if context_file.exists():
                with open(context_file, 'r') as f:
                    context = json.load(f)
                    if 'board_id' in context:
                        self.board_id = context['board_id']
                    self.github_repo = context.get('github_repo', os.getenv('GITHUB_REPO', ''))
                    self.working_group_id = context.get('group_id', None)
                    self.working_group_name = context.get('group_name', None)
            else:
                self.github_repo = os.getenv('GITHUB_REPO', '')
                self.working_group_id = None
                self.working_group_name = None
        except Exception:
            self.github_repo = os.getenv('GITHUB_REPO', '')
            self.working_group_id = None
            self.working_group_name = None
    
    def handle_request(self, request):
        """Handle MCP requests"""
        method = request.get('method', '')
        request_id = request.get('id')

        if method == 'initialize':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "itms-workflow",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == 'notifications/initialized':
            # MCP initialization complete notification - no response needed
            return None
        
        elif method == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_monday_tasks",
                            "description": "Get current Monday.com tasks",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "create_monday_task",
                            "description": "Create a new Monday.com task",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "priority": {"type": "string", "enum": ["Low", "Medium", "High"]}
                                },
                                "required": ["name"]
                            }
                        },
                        {
                            "name": "workflow_status",
                            "description": "Get current workflow status",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "select_active_task",
                            "description": "Select a task as the active task for detailed analysis",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "Monday.com task ID"}
                                },
                                "required": ["task_id"]
                            }
                        },
                        {
                            "name": "create_subtasks",
                            "description": "Create intelligent sub-tasks for the active task using Context7 and guidelines",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "execute_subtask",
                            "description": "Execute a specific sub-task with AI guidance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "subtask_id": {"type": "string", "description": "Monday.com subtask ID"}
                                },
                                "required": ["subtask_id"]
                            }
                        },
                        {
                            "name": "complete_subtask",
                            "description": "Mark a subtask as complete with notes",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "subtask_id": {"type": "string", "description": "Monday.com subtask ID"},
                                    "completion_notes": {"type": "string", "description": "Completion notes"}
                                },
                                "required": ["subtask_id"]
                            }
                        },
                        {
                            "name": "set_working_board",
                            "description": "Set the active Monday.com board ID for operations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "board_id": {"type": "string", "description": "Monday.com board ID"}
                                },
                                "required": ["board_id"]
                            }
                        },
                        {
                            "name": "set_working_repo",
                            "description": "Set the active GitHub repository for operations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "repo": {"type": "string", "description": "GitHub repository (org/repo format)"}
                                },
                                "required": ["repo"]
                            }
                        },
                        {
                            "name": "list_board_groups",
                            "description": "List all groups available on the current working board",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "set_working_group",
                            "description": "Set the active group within the current board for task filtering",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "group_id": {"type": "string", "description": "Monday.com group ID"}
                                },
                                "required": ["group_id"]
                            }
                        },
                        {
                            "name": "clear_working_group",
                            "description": "Clear the working group filter to show tasks from all groups",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = request.get('params', {}).get('name')
            tool_args = request.get('params', {}).get('arguments', {})
            
            if tool_name == 'get_monday_tasks':
                return self.get_monday_tasks(request)
            elif tool_name == 'create_monday_task':
                return self.create_monday_task(request)
            elif tool_name == 'workflow_status':
                return self.get_workflow_status(request)
            elif tool_name == 'select_active_task':
                return self.select_active_task(request, tool_args.get('task_id'))
            elif tool_name == 'create_subtasks':
                return self.create_subtasks(request)
            elif tool_name == 'execute_subtask':
                return self.execute_subtask(request, tool_args.get('subtask_id'))
            elif tool_name == 'complete_subtask':
                return self.complete_subtask(request, tool_args.get('subtask_id'), tool_args.get('completion_notes', ''))
            elif tool_name == 'set_working_board':
                return self.set_working_board(request, tool_args.get('board_id'))
            elif tool_name == 'set_working_repo':
                return self.set_working_repo(request, tool_args.get('repo'))
            elif tool_name == 'list_board_groups':
                return self.list_board_groups(request)
            elif tool_name == 'set_working_group':
                return self.set_working_group(request, tool_args.get('group_id'))
            elif tool_name == 'clear_working_group':
                return self.clear_working_group(request)
            else:
                return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
    
    def get_monday_tasks(self, request):
        """Get Monday.com tasks"""
        if not self.monday_token:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No Monday.com token"}}
        
        # Add group filter if working group is set
        group_filter = ""
        if hasattr(self, 'working_group_id') and self.working_group_id:
            group_filter = f', group_ids: ["{self.working_group_id}"]'
        
        query = f"""
        query {{
            boards(ids: [{self.board_id}]) {{
                items_page(limit: 10{group_filter}) {{
                    items {{
                        id
                        name
                        state
                        created_at
                        updated_at
                        group {{
                            id
                            title
                        }}
                        column_values {{
                            id
                            text
                            value
                        }}
                        updates {{
                            id
                            body
                            created_at
                            creator {{
                                name
                            }}
                        }}
                        subitems {{
                            id
                            name
                            state
                        }}
                    }}
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"GraphQL errors: {data['errors']}"}}
                
                tasks = data['data']['boards'][0]['items_page']['items']
                
                # Debug: Log the actual response for troubleshooting
                debug_info = f"Debug: Found {len(tasks)} tasks in board {self.board_id}"
                if tasks:
                    debug_info += f"\\nFirst task: {tasks[0]['name']} (ID: {tasks[0]['id']})"
                
                if len(tasks) == 1:
                    # Single task - return detailed info for auto-selection
                    task = tasks[0]
                    task_details = f"""Found 1 task - Auto-selecting for workflow:

**Task:** {task['name']}
**ID:** {task['id']}
**Status:** {task['state']}
**Created:** {task['created_at']}
**Updates:** {len(task['updates'])} comments
**Sub-items:** {len(task['subitems'])} existing

**Recent Updates:**"""
                    
                    if task['updates']:
                        for update in task['updates'][:3]:  # Show last 3 updates
                            task_details += f"\\n- {update['creator']['name']}: {update['body'][:100]}..."
                    else:
                        task_details += "\\n- No updates yet"
                    
                    # Auto-store as active task for immediate workflow
                    active_task = {
                        'id': task['id'],
                        'name': task['name'],
                        'state': task['state'],
                        'created_at': task['created_at'],
                        'updated_at': task['updated_at'],
                        'column_values': task['column_values'],
                        'updates': task['updates'],
                        'selected_at': datetime.now().isoformat(),
                        'auto_selected': True
                    }
                    self.save_active_task(active_task)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": {
                            "content": [{"type": "text", "text": f"{debug_info}\\n\\n{task_details}"}]
                        }
                    }
                else:
                    # Multiple tasks - show list with IDs for selection
                    task_list = "\\n".join([f"• **{task['name']}** (ID: {task['id']}, Group: {task['group']['title']}, Status: {task['state']}, Updates: {len(task['updates'])})" for task in tasks])
                    group_filter_text = ""
                    if hasattr(self, 'working_group_name') and self.working_group_name:
                        group_filter_text = f" (filtered to group: {self.working_group_name})"
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": {
                            "content": [{"type": "text", "text": f"{debug_info}\\n\\nFound {len(tasks)} tasks{group_filter_text}:\\n{task_list}\\n\\nUse select_active_task with the task ID to begin workflow."}]
                        }
                    }
            else:
                return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"API Error: {response.status_code}"}}
        
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def create_monday_task(self, request):
        """Create Monday.com task"""
        args = request.get('params', {}).get('arguments', {})
        name = args.get('name', '')
        description = args.get('description', '')
        priority = args.get('priority', 'Medium')
        
        if not self.monday_token or not name:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing token or name"}}
        
        mutation = f"""
        mutation {{
            create_item(
                board_id: {self.board_id},
                item_name: "{name}"
            ) {{
                id
                name
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': mutation},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' in result:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"GraphQL errors: {result['errors']}"}}
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Created task: {name} (ID: {result['data']['create_item']['id']})"}]
                    }
                }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def get_workflow_status(self, request):
        """Get workflow status"""
        group_status = "All groups"
        if hasattr(self, 'working_group_name') and self.working_group_name:
            group_status = f"{self.working_group_name} (ID: {getattr(self, 'working_group_id', 'Unknown')})"
        elif hasattr(self, 'working_group_id') and self.working_group_id:
            group_status = f"Group ID: {self.working_group_id}"
            
        status_text = f"ITMS Workflow Status:\\n• Monday.com: {'Connected' if self.monday_token else 'Not Connected'}\\n• GitHub: {'Connected' if self.github_token else 'Not Connected'}\\n• Working Board: {self.board_id}\\n• Working Group: {group_status}\\n• Working Repo: {getattr(self, 'github_repo', 'Not set')}"
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": status_text}]
            }
        }
    
    def select_active_task(self, request, task_id):
        """Select and store active task for detailed analysis"""
        if not self.monday_token or not task_id:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing token or task_id"}}
        
        query = f"""
        query {{
            items(ids: ["{task_id}"]) {{
                id
                name
                state
                created_at
                updated_at
                column_values {{
                    id
                    text
                    value
                }}
                updates {{
                    id
                    body
                    created_at
                    creator {{
                        name
                    }}
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"GraphQL errors: {data['errors']}"}}
                
                if not data['data']['items']:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Task not found"}}
                
                task = data['data']['items'][0]
                
                # Save active task
                active_task = {
                    'id': task['id'],
                    'name': task['name'],
                    'state': task['state'],
                    'created_at': task['created_at'],
                    'updated_at': task['updated_at'],
                    'column_values': task['column_values'],
                    'updates': task['updates'],
                    'selected_at': datetime.now().isoformat()
                }
                
                self.save_active_task(active_task)
                
                task_details = f"""Selected active task for workflow:

**Task:** {task['name']}
**ID:** {task['id']}
**Status:** {task['state']}
**Created:** {task['created_at']}
**Updates:** {len(task['updates'])} comments

**Recent Updates:**"""
                
                if task['updates']:
                    for update in task['updates'][:3]:  # Show last 3 updates
                        task_details += f"\\n- {update['creator']['name']}: {update['body'][:100]}..."
                else:
                    task_details += "\\n- No updates yet"
                    
                task_details += "\\n\\nTask is now active and ready for create_subtasks"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": task_details}]
                    }
                }
            else:
                return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"API Error: {response.status_code}"}}
        
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def create_subtasks(self, request):
        """Create intelligent sub-tasks for active task using Context7 and guidelines"""
        active_task = self.load_active_task()
        if not active_task:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No active task selected. Use get_monday_tasks or select_active_task first."}}
        
        if not self.monday_token:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No Monday.com token"}}
        
        # Analyze task content to create intelligent, context-specific sub-tasks
        task_name = active_task['name'].lower()
        task_updates = active_task.get('updates', [])
        task_description = ""
        if task_updates:
            task_description = task_updates[0].get('body', '').lower()
        
        # Determine task type and create specific sub-tasks
        if 'odoo' in task_name or 'odoo' in task_description:
            # Odoo-specific development tasks
            if 'list view' in task_description or 'column' in task_description:
                subtasks = [
                    "Analysis: Identify target Odoo app and list view requirements",
                    "Research: Locate view XML files and current column definitions", 
                    "Implementation: Update view XML with column width specifications",
                    "Testing: Verify layout changes in development environment",
                    "Code Review: Ensure changes follow Odoo development standards",
                    "Deployment: Commit changes and update module version",
                    "Documentation: Update technical specifications"
                ]
            elif 'module' in task_description or 'development' in task_description:
                subtasks = [
                    "Analysis: Define module requirements and scope",
                    "Architecture: Design module structure and dependencies",
                    "Models: Create or modify data models and fields",
                    "Views: Implement forms, lists, and kanban views", 
                    "Business Logic: Write Python methods and workflows",
                    "Testing: Create unit tests and validate functionality",
                    "Documentation: Update module documentation and user guides"
                ]
            else:
                subtasks = [
                    "Analysis: Review Odoo task requirements and affected modules",
                    "Research: Investigate existing Odoo codebase and dependencies",
                    "Implementation: Develop changes following Odoo standards",
                    "Testing: Validate changes in Odoo development environment",
                    "Review: Code review and quality assurance",
                    "Deployment: Commit to repository and update Monday status"
                ]
        elif 'research' in task_name or 'research' in task_description:
            # Research-specific tasks  
            if 'api' in task_description or 'integration' in task_description:
                subtasks = [
                    "Research: API documentation and authentication methods",
                    "Analysis: Data structures and integration requirements",
                    "Architecture: Design integration approach and data flow",
                    "Implementation: Develop scripts and connection logic", 
                    "Testing: Validate data accuracy and error handling",
                    "Documentation: Create implementation guide and troubleshooting",
                    "Review: Technical review and optimization recommendations"
                ]
            else:
                subtasks = [
                    "Research: Gather information from documentation and sources",
                    "Analysis: Evaluate options and technical requirements",
                    "Design: Create technical approach and architecture",
                    "Documentation: Compile findings into implementation guide",
                    "Validation: Review accuracy and completeness",
                    "Recommendations: Provide next steps and action items"
                ]
        else:
            # Generic development tasks
            subtasks = [
                "Analysis: Review task requirements and acceptance criteria",
                "Research: Investigate existing codebase and related components", 
                "Design: Create technical design and implementation plan",
                "Implementation: Write code following development guidelines",
                "Testing: Create and run comprehensive tests",
                "Documentation: Update relevant documentation",
                "Review: Code review and quality assurance"
            ]
        
        created_subtasks = []
        for subtask_name in subtasks:
            mutation = f"""
            mutation {{
                create_subitem(
                    parent_item_id: {active_task['id']},
                    item_name: "{subtask_name}"
                ) {{
                    id
                    name
                }}
            }}
            """
            
            try:
                response = requests.post(
                    'https://api.monday.com/v2',
                    json={'query': mutation},
                    headers={'Authorization': self.monday_token}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'errors' not in result and result.get('data', {}).get('create_subitem'):
                        created_subtasks.append(result['data']['create_subitem'])
            except Exception as e:
                continue
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": f"Created {len(created_subtasks)} sub-tasks for: {active_task['name']}\\n" + "\\n".join([f"• {st['name']}" for st in created_subtasks])}]
            }
        }
    
    def execute_subtask(self, request, subtask_id):
        """Execute specific sub-task with AI guidance"""
        if not subtask_id:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing subtask_id"}}
        
        # This would integrate with Context7 and provide AI guidance
        # For now, return a placeholder response
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": f"Executing subtask {subtask_id} with AI guidance...\\nThis would integrate with Context7 for intelligent task execution."}]
            }
        }
    
    def complete_subtask(self, request, subtask_id, completion_notes=""):
        """Mark subtask as complete with notes"""
        if not self.monday_token or not subtask_id:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing token or subtask_id"}}
        
        # Update subtask status to Done
        mutation = f"""
        mutation {{
            change_simple_column_value(
                item_id: {subtask_id},
                column_id: "status",
                value: "Done"
            ) {{
                id
                name
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': mutation},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' not in result:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id'),
                        "result": {
                            "content": [{"type": "text", "text": f"Completed subtask {subtask_id}\\nNotes: {completion_notes}"}]
                        }
                    }
            
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Failed to update subtask status"}}
        
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def load_active_task(self):
        """Load active task from storage"""
        try:
            active_task_file = Path('active_task.json')
            if active_task_file.exists():
                with open(active_task_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def save_active_task(self, task):
        """Save active task to storage"""
        try:
            active_task_file = Path('active_task.json')
            with open(active_task_file, 'w') as f:
                json.dump(task, f, indent=2)
        except Exception:
            pass
    
    def set_working_board(self, request, board_id):
        """Set the active Monday.com board ID"""
        if not board_id:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing board_id"}}
        
        # Update instance board_id
        self.board_id = board_id
        
        # Clear any existing group selection when changing boards
        self.working_group_id = None
        self.working_group_name = None
        
        # Save to working context file
        context = self.load_working_context()
        context['board_id'] = board_id
        context.pop('group_id', None)
        context.pop('group_name', None)
        self.save_working_context(context)
        
        # Automatically fetch and display groups for selection
        if self.monday_token:
            groups_response = self._fetch_board_groups(board_id)
            if groups_response:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Set working Monday.com board to: {board_id}\\n\\n{groups_response}\\n\\nUse set_working_group with a group ID to filter tasks, or proceed with get_monday_tasks to see all tasks."}]
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": f"Set working Monday.com board to: {board_id}"}]
            }
        }
    
    def set_working_repo(self, request, repo):
        """Set the active GitHub repository"""
        if not repo:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing repo"}}
        
        # Save to working context file
        context = self.load_working_context()
        context['github_repo'] = repo
        self.save_working_context(context)
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": f"Set working GitHub repository to: {repo}"}]
            }
        }
    
    def load_working_context(self):
        """Load working context from storage"""
        try:
            context_file = Path('working_context.json')
            if context_file.exists():
                with open(context_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_working_context(self, context):
        """Save working context to storage"""
        try:
            context_file = Path('working_context.json')
            with open(context_file, 'w') as f:
                json.dump(context, f, indent=2)
        except Exception:
            pass
    
    def _fetch_board_groups(self, board_id):
        """Helper method to fetch groups for a board"""
        query = f"""
        query {{
            boards(ids: [{board_id}]) {{
                groups {{
                    id
                    title
                    color
                    archived
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' not in data and data['data']['boards']:
                    groups = data['data']['boards'][0]['groups']
                    active_groups = [g for g in groups if not g['archived']]
                    
                    if active_groups:
                        group_list = "\\n".join([f"• {group['title']} (ID: {group['id']}, Color: {group['color']})" for group in active_groups])
                        return f"Available groups on this board:\\n{group_list}"
            return None
        except Exception:
            return None
    
    def list_board_groups(self, request):
        """List all groups available on the current working board"""
        if not self.monday_token:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No Monday.com token"}}
        
        query = f"""
        query {{
            boards(ids: [{self.board_id}]) {{
                groups {{
                    id
                    title
                    color
                    archived
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"GraphQL errors: {data['errors']}"}}
                
                groups = data['data']['boards'][0]['groups']
                active_groups = [g for g in groups if not g['archived']]
                
                group_list = "\\n".join([f"• {group['title']} (ID: {group['id']}, Color: {group['color']})" for group in active_groups])
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Available groups on board {self.board_id}:\\n\\n{group_list}\\n\\nUse set_working_group with the group ID to filter tasks to a specific group."}]
                    }
                }
            else:
                return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"API Error: {response.status_code}"}}
        
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def set_working_group(self, request, group_id):
        """Set the active group within the current board"""
        if not group_id:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Missing group_id"}}
        
        # First, get the group name for better UX
        if not self.monday_token:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No Monday.com token"}}
        
        query = f"""
        query {{
            boards(ids: [{self.board_id}]) {{
                groups(ids: ["{group_id}"]) {{
                    id
                    title
                }}
            }}
        }}
        """
        
        try:
            response = requests.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data or not data['data']['boards'][0]['groups']:
                    return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "Group not found"}}
                
                group = data['data']['boards'][0]['groups'][0]
                group_name = group['title']
                
                # Update instance variables
                self.working_group_id = group_id
                self.working_group_name = group_name
                
                # Save to working context file
                context = self.load_working_context()
                context['group_id'] = group_id
                context['group_name'] = group_name
                self.save_working_context(context)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Set working group to: {group_name} (ID: {group_id})\\n\\nTasks will now be filtered to this group only."}]
                    }
                }
            else:
                return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": f"API Error: {response.status_code}"}}
        
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": str(e)}}
    
    def clear_working_group(self, request):
        """Clear the working group filter to show tasks from all groups"""
        # Clear instance variables
        self.working_group_id = None
        self.working_group_name = None
        
        # Update working context file
        context = self.load_working_context()
        context.pop('group_id', None)
        context.pop('group_name', None)
        self.save_working_context(context)
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": "Cleared working group filter. Tasks will now show from all groups on the board."}]
            }
        }

def main():
    """Main MCP server loop"""
    server = ITMSMCPServer()

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = server.handle_request(request)

                # Only send response if there is one (some notifications don't need responses)
                if response is not None:
                    print(json.dumps(response))
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {e}"}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass

if __name__ == '__main__':
    main()