#!/usr/bin/env python3
"""
ITMS MCP Server - Simple interface for AI tools
Provides Monday.com and workflow integration
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
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = request.get('params', {}).get('name')
            if tool_name == 'get_monday_tasks':
                return self.get_monday_tasks(request)
            elif tool_name == 'create_monday_task':
                return self.create_monday_task(request)
            elif tool_name == 'workflow_status':
                return self.get_workflow_status(request)
            else:
                return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
    
    def get_monday_tasks(self, request):
        """Get Monday.com tasks"""
        if not self.monday_token:
            return {"jsonrpc": "2.0", "id": request.get('id'), "error": {"code": -1, "message": "No Monday.com token"}}
        
        query = f"""
        query {{
            boards(ids: [{self.board_id}]) {{
                items_page(limit: 10) {{
                    items {{
                        id
                        name
                        state
                        created_at
                        updated_at
                        column_values {{
                            id
                            text
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
                task_list = "\\n".join([f"• {task['name']} ({task['state']})" for task in tasks])
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "result": {
                        "content": [{"type": "text", "text": f"Found {len(tasks)} tasks:\\n{task_list}"}]
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
        status_text = f"ITMS Workflow Status:\\n• Monday.com: {'✅' if self.monday_token else '❌'}\\n• GitHub: {'✅' if self.github_token else '❌'}\\n• Board ID: {self.board_id}"
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id'),
            "result": {
                "content": [{"type": "text", "text": status_text}]
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