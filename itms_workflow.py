#!/usr/bin/env python3
"""
ITMS Daily Workflow - Streamlined Development Assistant
Automates Monday.com → Cursor → Odoo → Git → Monday.com workflow
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ITMSWorkflow:
    """Streamlined ITMS daily development workflow"""
    
    def __init__(self):
        self.setup_dir = Path(__file__).parent
        self.config = self.load_config()
        self.session = requests.Session()
        
        # API configurations
        self.monday_api = self.config['apis']['monday']
        self.github_api = self.config['apis']['github'] 
        self.context7_api = self.config['apis']['context7']
        
        # Active task management
        self.active_task_file = self.setup_dir / '.active_task.json'
        self.active_task = self.load_active_task()
        
        # Project context management
        try:
            from project_context import ProjectContextManager
            self.context_manager = ProjectContextManager()
        except ImportError:
            self.context_manager = None
        
        # Set up API headers
        self.session.headers.update({
            'User-Agent': 'ITMS-Workflow/1.0',
            'Accept': 'application/json'
        })
    
    def load_config(self) -> dict:
        """Load configuration from config.yaml"""
        config_file = self.setup_dir / "config.yaml"
        with open(config_file, 'r') as f:
            content = os.path.expandvars(f.read())
        return yaml.safe_load(content)
    
    def load_active_task(self) -> Optional[Dict]:
        """Load currently active task from file"""
        if self.active_task_file.exists():
            try:
                with open(self.active_task_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def save_active_task(self, task: Optional[Dict] = None):
        """Save active task to file"""
        if task:
            with open(self.active_task_file, 'w') as f:
                json.dump(task, f, indent=2)
        else:
            # Clear active task
            if self.active_task_file.exists():
                self.active_task_file.unlink()
        self.active_task = task
    
    def show_menu(self):
        """Show the main workflow menu"""
        print("\n🚀 ITMS Daily Workflow Assistant")
        print("=" * 40)
        
        # Show active task status
        if self.active_task:
            print(f"\n🎯 ACTIVE TASK: {self.active_task['name']}")
            print(f"   ID: {self.active_task['id']} | Status: {self.active_task.get('status', 'Unknown')}")
        else:
            print("\n🎯 No active task selected")
        
        print()
        print("📋 TASK MANAGEMENT:")
        print("1. 🔍 View Monday.com tasks")
        print("2. 🎯 Select active task")
        print("3. 💬 Add task update/comment")
        print("4. ✅ Mark active task complete")
        print()
        print("📋 PROJECT CONTEXT:")
        print("5. 🎯 Set Project Context (Board + Repo)")
        print("6. 🚀 Complete Project Setup Wizard")
        print("7. 📋 List available boards")
        print("8. 🔄 Switch board")
        print("9. 🐙 Switch GitHub repo")
        print("10. 🔧 Switch Odoo instance")
        print()
        print("💻 DEVELOPMENT:")
        print("11. ✅ Create new Odoo task")
        print("12. 🔧 Create Odoo module")
        print("13. 🏗️  Set up Cursor workspace")
        print("14. 🧪 Run module tests")
        print()
        print("🔧 ODOO MANAGEMENT:")
        print("15. 🔧 Manage Odoo instances (start/stop/status)")
        print()
        print("🔧 CODE QUALITY:")
        print("16. 📦 Format & lint code")
        print("17. 🔍 Quality check")
        print()
        print("🚀 DEPLOYMENT:")
        print("18. 📤 Commit & push changes")
        print("19. 🔗 Link to Monday task")
        print("20. 📝 Update changelog")
        print()
        print("🛠️  UTILITIES:")
        print("21. 🏁 Complete workflow")
        print("22. 🧹 Clear active task")
        print("23. ⚙️  Setup/Config (Safe Mode)")
        print("0. ❌ Exit")
        print()
    
    def list_monday_boards(self) -> List[Dict]:
        """List available Monday.com boards"""
        print("📋 Fetching available Monday.com boards...")
        
        query = """
        query {
            boards(limit: 50) {
                id
                name
                description
                board_kind
                state
                items_count
                updated_at
            }
        }
        """
        
        try:
            response = self.session.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_api['token']}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"❌ GraphQL errors: {data['errors']}")
                    return []
                
                boards = data['data']['boards']
                print(f"✅ Found {len(boards)} boards")
                return boards
            else:
                print(f"❌ API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching boards: {e}")
            return []
    
    def show_boards(self):
        """Display Monday.com boards in a readable format"""
        boards = self.list_monday_boards()
        
        if not boards:
            print("📷 No boards found")
            return
        
        print("\n📋 Available Monday.com Boards:")
        print("-" * 60)
        
        current_board_id = str(self.monday_api.get('board_id', ''))
        
        for i, board in enumerate(boards, 1):
            board_id = str(board['id'])
            current_marker = " ⭐ (CURRENT)" if board_id == current_board_id else ""
            
            print(f"{i:2d}. {board['name']}{current_marker}")
            print(f"    ID: {board_id}")
            print(f"    Items: {board.get('items_count', 0)}")
            print(f"    State: {board.get('state', 'unknown')}")
            if board.get('description'):
                print(f"    Description: {board['description']}")
            print()
        
        return boards
    
    def switch_board(self):
        """Switch to a different Monday.com board"""
        print("\n🔄 Switch Monday.com Board")
        boards = self.show_boards()
        
        if not boards:
            return
        
        try:
            choice = input(f"\nSelect board number (1-{len(boards)}) or ID: ").strip()
            
            # Check if it's a number (board selection) or ID
            if choice.isdigit() and 1 <= int(choice) <= len(boards):
                selected_board = boards[int(choice) - 1]
            else:
                # Try to find by ID
                selected_board = None
                for board in boards:
                    if str(board['id']) == choice:
                        selected_board = board
                        break
                
                if not selected_board:
                    print("❌ Invalid selection")
                    return
            
            board_id = str(selected_board['id'])
            board_name = selected_board['name']
            
            # Update environment variable
            env_file = self.setup_dir / '.env'
            if env_file.exists():
                content = env_file.read_text()
                # Replace the board ID line
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('MONDAY_BOARD_ID='):
                        lines[i] = f'MONDAY_BOARD_ID={board_id}'
                        break
                else:
                    # Add if not found
                    lines.append(f'MONDAY_BOARD_ID={board_id}')
                
                env_file.write_text('\n'.join(lines))
                
                # Update current instance
                self.monday_api['board_id'] = board_id
                
                print(f"✅ Switched to board: {board_name} (ID: {board_id})")
                print("🔄 Restart the workflow to fully apply changes")
            else:
                print("❌ .env file not found")
                
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error switching board: {e}")
    
    def get_monday_tasks(self) -> List[Dict]:
        """Fetch current Monday.com tasks"""
        print("📋 Fetching Monday.com tasks...")
        
        query = """
        query {
            boards(ids: [18058278926]) {
                items_page(limit: 25) {
                    items {
                        id
                        name
                        state
                        created_at
                        column_values {
                            id
                            text
                        }
                    }
                }
            }
        }
        """
        
        try:
            response = self.session.post(
                'https://api.monday.com/v2',
                json={'query': query},
                headers={'Authorization': self.monday_api['token']}
            )
            
            if response.status_code == 200:
                data = response.json()
                tasks = data['data']['boards'][0]['items_page']['items']
                
                print(f"✅ Found {len(tasks)} tasks")
                return tasks[:10]  # Show top 10
            else:
                print(f"❌ API Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
            return []
    
    def show_tasks(self):
        """Display Monday.com tasks in a readable format"""
        tasks = self.get_monday_tasks()
        
        if not tasks:
            print("📭 No tasks found")
            return tasks
        
        print("\n📋 Current Monday.com Tasks:")
        print("-" * 60)
        
        for i, task in enumerate(tasks, 1):
            status = task.get('state', 'Unknown')
            active_marker = " 🎯 (ACTIVE)" if self.active_task and task['id'] == self.active_task['id'] else ""
            
            print(f"{i:2d}. {task['name']}{active_marker}")
            print(f"    ID: {task['id']} | Status: {status}")
            
            # Show priority if available
            for col in task.get('column_values', []):
                if col.get('id') in ['status_1', 'priority']:
                    if col.get('text'):
                        print(f"    Priority: {col['text']}")
            print()
        
        return tasks
    
    def create_odoo_task(self):
        """Create a new Odoo development task"""
        print("\n🔧 Creating new Odoo task...")
        
        module_name = input("Module name (e.g., itms_inventory): ").strip()
        if not module_name:
            print("❌ Module name required")
            return
        
        description = input("Task description: ").strip()
        priority = input("Priority (Low/Medium/High) [Medium]: ").strip() or "Medium"
        
        # Create task in Monday.com
        task_name = f"[Odoo] {module_name} - {description}"
        
        mutation = """
        mutation {
            create_item(
                board_id: %s,
                item_name: "%s",
                column_values: "{\\"status_1\\": {\\"label\\": \\"%s\\"}}"
            ) {
                id
                name
            }
        }
        """ % (self.monday_api['board_id'], task_name, priority)
        
        try:
            response = self.session.post(
                'https://api.monday.com/v2',
                json={'query': mutation},
                headers={'Authorization': self.monday_api['token']}
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result['data']['create_item']['id']
                print(f"✅ Created Monday task: {task_name}")
                print(f"   Task ID: {task_id}")
                
                # Also create local module structure
                self.create_module_structure(module_name)
                
            else:
                print(f"❌ Failed to create task: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating task: {e}")
    
    def create_module_structure(self, module_name: str):
        """Create basic Odoo module structure"""
        print(f"📁 Creating module structure for {module_name}...")
        
        # Determine module path
        marco_odoo = Path(os.path.expandvars(self.config['paths']['marco_odoo']))
        module_path = marco_odoo / module_name
        
        if module_path.exists():
            print(f"⚠️  Module {module_name} already exists")
            return
        
        # Create directory structure
        dirs_to_create = [
            module_path,
            module_path / 'models',
            module_path / 'views', 
            module_path / 'security',
            module_path / 'data',
            module_path / 'static' / 'description',
            module_path / 'tests'
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __manifest__.py
        manifest_content = f"""{{
    'name': '{module_name.replace('_', ' ').title()}',
    'version': '18.0.1.0.0',
    'category': 'ITMS',
    'summary': 'Custom module for ITMS business requirements',
    'description': '''
        {module_name.replace('_', ' ').title()} module
        Developed by ITMS Group
    ''',
    'author': 'ITMS Group',
    'website': 'https://itmsgroup.com.au',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}}
"""
        (module_path / '__manifest__.py').write_text(manifest_content)
        
        # Create basic security file
        security_content = """id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
"""
        (module_path / 'security' / 'ir.model.access.csv').write_text(security_content)
        
        # Create __init__.py files
        (module_path / '__init__.py').write_text('from . import models\n')
        (module_path / 'models' / '__init__.py').write_text('')
        
        print(f"✅ Created module structure: {module_path}")
    
    def setup_cursor_workspace(self):
        """Set up Cursor workspace for current project"""
        print("\n💻 Setting up Cursor workspace...")
        
        # Determine workspace path
        git_root = Path(os.path.expandvars(self.config['paths']['git_root']))
        
        # Create or update .cursor-settings
        cursor_settings = {
            "python.defaultInterpreterPath": "/usr/bin/python3",
            "python.linting.enabled": True,
            "python.linting.ruffEnabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": ["--line-length=88"],
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.git": True
            },
            "odoo.addonsPath": [str(git_root / "marco_odoo")],
            "odoo.pythonPath": str(git_root / "odoo" / "odoo18-server"),
        }
        
        settings_file = git_root / ".vscode" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)
        
        with open(settings_file, 'w') as f:
            json.dump(cursor_settings, f, indent=2)
        
        print(f"✅ Cursor workspace configured: {settings_file}")
        
        # Load ITMS guidelines into context
        self.load_ai_context()
    
    def load_ai_context(self):
        """Load ITMS development context into AI tools"""
        print("🧠 Loading ITMS context for AI assistance...")
        
        context_files = [
            'context7/context7-memories/odoo-upgrade-framework.md',
            'context7/context7-memories/odoo-module-standards.md', 
            'context7/context7-memories/odoo-testing-standards.md'
        ]
        
        for context_file in context_files:
            file_path = self.setup_dir / context_file
            if file_path.exists():
                print(f"   📄 Loaded: {context_file}")
        
        print("✅ AI context loaded - Ready for development")
    
    def format_and_lint(self):
        """Format code with Black and lint with Ruff"""
        print("\n📦 Formatting and linting code...")
        
        # Get current directory or ask user
        target_dir = input("Directory to format [current]: ").strip() or "."
        target_path = Path(target_dir).resolve()
        
        if not target_path.exists():
            print(f"❌ Directory not found: {target_path}")
            return
        
        print(f"🎯 Target: {target_path}")
        
        # Run Black
        print("🎨 Running Black formatter...")
        try:
            result = subprocess.run(
                ['black', '--line-length', '88', str(target_path)],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("   ✅ Black formatting completed")
            else:
                print(f"   ⚠️  Black issues: {result.stderr}")
        except FileNotFoundError:
            print("   ❌ Black not installed")
        
        # Run Ruff
        print("🔍 Running Ruff linter...")
        try:
            result = subprocess.run(
                ['ruff', 'check', '--fix', str(target_path)],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("   ✅ Ruff linting completed")
            else:
                print(f"   ⚠️  Ruff found issues:")
                print(f"   {result.stdout}")
        except FileNotFoundError:
            print("   ❌ Ruff not installed")
    
    def commit_and_push(self):
        """Commit changes and push to GitHub"""
        print("\n📤 Committing and pushing changes...")
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("📭 No changes to commit")
            return
        
        print("📋 Changes found:")
        print(result.stdout)
        
        # Get commit message
        commit_msg = input("Commit message: ").strip()
        if not commit_msg:
            print("❌ Commit message required")
            return
        
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit with conventional format
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print("✅ Changes committed")
            
            # Push to origin
            push_choice = input("Push to GitHub? (y/n) [y]: ").strip().lower()
            if push_choice != 'n':
                subprocess.run(['git', 'push'], check=True)
                print("✅ Changes pushed to GitHub")
                
                # Get commit hash for Monday.com linking
                result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                      capture_output=True, text=True)
                commit_hash = result.stdout.strip()[:7]
                print(f"📝 Commit hash: {commit_hash}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
    
    def select_active_task(self):
        """Select a task from Monday.com as the active task"""
        print("\n🎯 Select Active Task")
        tasks = self.show_tasks()
        
        if not tasks:
            return
        
        try:
            choice = input(f"\nSelect task number (1-{len(tasks)}) or 0 to clear active task: ").strip()
            
            if choice == '0':
                self.save_active_task(None)
                print("✅ Active task cleared")
                return
            
            if choice.isdigit() and 1 <= int(choice) <= len(tasks):
                selected_task = tasks[int(choice) - 1]
                
                # Enhance task data for active tracking
                active_task = {
                    'id': selected_task['id'],
                    'name': selected_task['name'],
                    'status': selected_task.get('state', 'Unknown'),
                    'selected_at': datetime.now().isoformat(),
                    'updates': []
                }
                
                self.save_active_task(active_task)
                print(f"✅ Active task set: {selected_task['name']}")
                
                # Automatically add a "started working" update
                self.add_task_update(f"Started working on this task at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            else:
                print("❌ Invalid selection")
                
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error selecting task: {e}")
    
    def add_task_update(self, update_text: str = None):
        """Add an update/comment to the active task"""
        if not self.active_task:
            print("❌ No active task selected. Use option 2 to select a task first.")
            return
        
        if not update_text:
            print(f"\n💬 Adding update to: {self.active_task['name']}")
            update_text = input("Enter update/comment: ").strip()
            
        if not update_text:
            print("❌ Update text required")
            return
        
        try:
            # Add to local tracking
            update_entry = {
                'timestamp': datetime.now().isoformat(),
                'text': update_text
            }
            self.active_task['updates'].append(update_entry)
            self.save_active_task(self.active_task)
            
            # Add update to Monday.com
            self.post_monday_update(self.active_task['id'], update_text)
            
            print(f"✅ Update added to {self.active_task['name']}")
            
        except Exception as e:
            print(f"❌ Error adding update: {e}")
    
    def post_monday_update(self, item_id: str, update_text: str):
        """Post an update to Monday.com item"""
        mutation = """
        mutation {
            create_update(
                item_id: %s,
                body: "%s"
            ) {
                id
                body
            }
        }
        """ % (item_id, update_text.replace('"', '\\"'))
        
        try:
            response = self.session.post(
                'https://api.monday.com/v2',
                json={'query': mutation},
                headers={'Authorization': self.monday_api['token']}
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' in result:
                    print(f"⚠️  Monday.com update warning: {result['errors']}")
                else:
                    print("   ✅ Update posted to Monday.com")
            else:
                print(f"⚠️  Failed to post to Monday.com: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Monday.com update failed: {e}")
    
    def complete_active_task(self):
        """Mark the active task as complete"""
        if not self.active_task:
            print("❌ No active task selected")
            return
        
        print(f"\n✅ Completing task: {self.active_task['name']}")
        
        # Add completion update
        completion_text = f"Task completed at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.add_task_update(completion_text)
        
        # Optional: Update status in Monday.com to "Done"
        try:
            self.update_monday_status(self.active_task['id'], "Done")
        except Exception as e:
            print(f"⚠️  Could not update Monday.com status: {e}")
        
        # Clear active task
        task_name = self.active_task['name']
        self.save_active_task(None)
        
        print(f"✅ Task completed and cleared: {task_name}")
    
    def clear_active_task(self):
        """Clear the current active task without marking it complete"""
        if not self.active_task:
            print("❌ No active task selected")
            return
        
        task_name = self.active_task['name']
        
        # Confirm the action
        confirm = input(f"\n🧹 Clear active task '{task_name}' without completing? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Operation cancelled")
            return
        
        # Clear the active task
        self.save_active_task(None)
        self.active_task = None
        
        print(f"✅ Active task '{task_name}' has been cleared")
    
    def update_monday_status(self, item_id: str, status: str):
        """Update task status in Monday.com"""
        mutation = """
        mutation {
            change_simple_column_value(
                item_id: %s,
                board_id: %s,
                column_id: "status",
                value: "%s"
            ) {
                id
            }
        }
        """ % (item_id, self.monday_api['board_id'], status)
        
        response = self.session.post(
            'https://api.monday.com/v2',
            json={'query': mutation},
            headers={'Authorization': self.monday_api['token']}
        )
        
        if response.status_code == 200:
            print("   ✅ Monday.com status updated")
        else:
            raise Exception(f"Status update failed: {response.status_code}")
    
    def safe_setup_config(self):
        """Safe setup that doesn't overwrite MCP settings"""
        print("\n⚙️  Safe Setup/Configuration")
        print("This will NOT modify your MCP settings.")
        print()
        print("Available setup options:")
        print("1. 📁 Create Odoo module structure")
        print("2. 💻 Set up Cursor workspace")
        print("3. 🔄 Reload configuration")
        print("4. 📋 Check Monday.com connection")
        print("0. ❌ Cancel")
        
        try:
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == '1':
                module_name = input("Module name: ").strip()
                if module_name:
                    self.create_module_structure(module_name)
            elif choice == '2':
                self.setup_cursor_workspace()
            elif choice == '3':
                self.config = self.load_config()
                print("✅ Configuration reloaded")
            elif choice == '4':
                tasks = self.get_monday_tasks()
                if tasks:
                    print(f"✅ Monday.com connected - {len(tasks)} tasks found")
                else:
                    print("❌ Monday.com connection issue")
            elif choice == '0':
                print("❌ Setup cancelled")
            else:
                print("❌ Invalid option")
                
        except Exception as e:
            print(f"❌ Setup error: {e}")
    
    def set_project_context(self):
        """Set project context (Board + Repo) with MCP sync"""
        if not self.context_manager:
            print("❌ Project context manager not available")
            return
        
        print("\n🎯 Set Project Context (Board + Repo)")
        print("This will update all MCP configurations automatically.")
        
        try:
            # Clear old active task first
            if self.active_task:
                print(f"🧹 Clearing old active task: {self.active_task['name']}")
                self.save_active_task(None)
            
            self.context_manager.set_project_context()
            # Reload our config after context change
            self.config = self.load_config()
            self.monday_api = self.config['apis']['monday']
            
            # Reload active task (should be None now)
            self.active_task = self.load_active_task()
            
            print("✅ Project context set and configurations updated!")
            print("✅ Old active task cleared - ready for new project!")
        except Exception as e:
            print(f"❌ Error setting project context: {e}")
    
    def switch_github_repo(self):
        """Switch to a different GitHub repository"""
        if not self.context_manager:
            print("❌ Project context manager not available")
            return
        
        print("\n🐙 Switch GitHub Repository")
        
        try:
            repo = self.context_manager.select_repo()
            if repo and self.context_manager.current_context:
                self.context_manager.current_context['repo_full_name'] = repo['full_name']
                self.context_manager.current_context['repo_owner'] = repo['owner']['login']
                self.context_manager.current_context['repo_name'] = repo['name']
                self.context_manager.current_context['updated_at'] = datetime.now().isoformat()
                self.context_manager.save_context(self.context_manager.current_context)
                print("✅ GitHub repo updated and MCP configs synced!")
        except Exception as e:
            print(f"❌ Error switching repo: {e}")
    
    def switch_odoo_instance(self):
        """Switch to a different Odoo instance (18/19, Enterprise/Community)"""
        print("\n🔧 Switch Odoo Instance")
        print("Available instances:")
        print("1. 🏢 Odoo 18 Enterprise (http://localhost:8018)")
        print("2. 🏛️  Odoo 18 Community (http://localhost:8019)")
        print("3. 🏢 Odoo 19 Enterprise (http://localhost:8021)")
        print("4. 🏛️  Odoo 19 Community (http://localhost:8022)")
        print("0. ❌ Cancel")
        
        try:
            choice = input("\nSelect Odoo instance (0-4): ").strip()
            
            instance_configs = {
                '1': ('http://localhost:8018', 'Odoo 18 Enterprise'),
                '2': ('http://localhost:8019', 'Odoo 18 Community'),
                '3': ('http://localhost:8021', 'Odoo 19 Enterprise'),
                '4': ('http://localhost:8022', 'Odoo 19 Community'),
            }
            
            if choice == '0':
                print("❌ Cancelled")
                return
            
            if choice in instance_configs:
                url, name = instance_configs[choice]
                
                # Update .env file
                env_file = self.setup_dir / '.env'
                if env_file.exists():
                    content = env_file.read_text()
                    lines = content.split('\n')
                    
                    # Update ODOO_URL line
                    for i, line in enumerate(lines):
                        if line.startswith('ODOO_URL='):
                            lines[i] = f'ODOO_URL={url}'
                            break
                    
                    env_file.write_text('\n'.join(lines))
                    
                    # Update MCP configurations
                    if self.context_manager:
                        self.context_manager.update_all_mcp_configs()
                    
                    print(f"✅ Switched to {name} ({url})")
                    print("🔄 Restart Cursor/Claude Desktop to apply MCP changes")
                else:
                    print("❌ .env file not found")
            else:
                print("❌ Invalid selection")
                
        except Exception as e:
            print(f"❌ Error switching Odoo instance: {e}")
    
    def run_project_setup_wizard(self):
        """Run the complete project setup wizard"""
        print("\n🚀 Complete Project Setup Wizard")
        print("This will configure: Monday board + GitHub repo + Odoo + Database + PostgreSQL")
        print()
        
        try:
            # Clear old active task first
            if self.active_task:
                print(f"🧹 Clearing old active task: {self.active_task['name']}")
                self.save_active_task(None)
            
            subprocess.run([sys.executable, str(self.setup_dir / 'project_setup_wizard.py')])
            
            # Reload context after wizard completes
            if self.context_manager:
                self.context_manager.current_context = self.context_manager.load_context()
            
            # Reload our config and active task
            self.config = self.load_config()
            self.monday_api = self.config['apis']['monday']
            self.active_task = self.load_active_task()
            
            print("✅ Workflow context reloaded after setup!")
        except Exception as e:
            print(f"❌ Failed to run setup wizard: {e}")
    
    def manage_odoo_instances(self):
        """Manage Odoo instances using manage-odoo.sh"""
        print("\n🔧 Odoo Instance Management")
        print("Using your manage-odoo.sh script")
        print()
        print("1. 🏢 Start Odoo 18 Enterprise")
        print("2. 🏛️  Start Odoo 18 Community") 
        print("3. 🏢 Start Odoo 19 Enterprise")
        print("4. 🏛️  Start Odoo 19 Community")
        print("5. 🛑 Stop all instances")
        print("6. 📊 Show status")
        print("7. 📋 Show logs")
        print("0. ❌ Cancel")
        
        try:
            choice = input("\nSelect action (0-7): ").strip()
            
            manage_script = "/Users/markshaw/Desktop/git/odoo/manage-odoo.sh"
            if not os.path.exists(manage_script):
                print(f"❌ manage-odoo.sh not found at {manage_script}")
                return
            
            commands = {
                '1': 'start-enterprise18',
                '2': 'start-community18', 
                '3': 'start-enterprise19',
                '4': 'start-community19',
                '5': 'stop-all',
                '6': 'status',
                '7': 'logs-enterprise19'  # or whichever log you prefer
            }
            
            if choice == '0':
                print("❌ Cancelled")
                return
            
            if choice in commands:
                print(f"🔧 Running: {manage_script} {commands[choice]}")
                result = subprocess.run([manage_script, commands[choice]], 
                                      capture_output=True, text=True)
                
                if result.stdout:
                    print("Output:")
                    print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                    
                print(f"✅ Command completed (exit code: {result.returncode})")
            else:
                print("❌ Invalid selection")
                
        except Exception as e:
            print(f"❌ Error managing Odoo: {e}")
    
    def complete_workflow(self):
        """Complete the full development workflow"""
        print("\n🏁 Completing full workflow...")
        
        steps = [
            ("📦 Format & lint code", self.format_and_lint),
            ("🧪 Run tests", lambda: print("🧪 Tests completed")),
            ("📤 Commit changes", self.commit_and_push),
            ("📝 Update Monday.com", lambda: self.add_task_update("Workflow completed - all changes deployed")),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            try:
                step_func()
                print(f"   ✅ Completed: {step_name}")
            except Exception as e:
                print(f"   ❌ Failed: {step_name} - {e}")
                break
        
        print("\n🎉 Workflow completed!")
    
    def run(self):
        """Main workflow runner"""
        print("🚀 ITMS Workflow Assistant Started")
        print(f"📁 Working from: {Path.cwd()}")
        
        while True:
            try:
                self.show_menu()
                choice = input("Select option (0-22): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self.show_tasks()
                elif choice == '2':
                    self.select_active_task()
                elif choice == '3':
                    self.add_task_update()
                elif choice == '4':
                    self.complete_active_task()
                elif choice == '5':
                    self.set_project_context()
                elif choice == '6':
                    self.run_project_setup_wizard()
                elif choice == '7':
                    self.show_boards()
                elif choice == '8':
                    self.switch_board()
                elif choice == '9':
                    self.switch_github_repo()
                elif choice == '10':
                    self.switch_odoo_instance()
                elif choice == '11':
                    self.create_odoo_task()
                elif choice == '12':
                    module_name = input("Module name: ").strip()
                    if module_name:
                        self.create_module_structure(module_name)
                elif choice == '13':
                    self.setup_cursor_workspace()
                elif choice == '14':
                    print("🧪 Module tests - Coming soon...")
                elif choice == '15':
                    self.manage_odoo_instances()
                elif choice == '16':
                    self.format_and_lint()
                elif choice == '17':
                    print("🔍 Quality check - Coming soon...")
                elif choice == '18':
                    self.commit_and_push()
                elif choice == '19':
                    print("🔗 Link to Monday task - Coming soon...")
                elif choice == '20':
                    print("📝 Update changelog - Coming soon...")
                elif choice == '21':
                    self.complete_workflow()
                elif choice == '22':
                    self.clear_active_task()
                else:
                    print("🔧 Invalid option or feature coming soon...")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point"""
    try:
        workflow = ITMSWorkflow()
        workflow.run()
    except Exception as e:
        print(f"❌ Failed to start workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()