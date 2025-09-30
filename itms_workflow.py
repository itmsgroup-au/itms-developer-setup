#!/usr/bin/env python3
"""
ITMS Daily Workflow - Streamlined Development Assistant
Automates Monday.com → Cursor → Odoo → Git → Monday.com workflow
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from datetime import datetime
from typing import Dict, List, Optional

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
        self.monday_api = self.config["apis"]["monday"]
        self.github_api = self.config["apis"]["github"]
        self.context7_api = self.config["apis"]["context7"]

        # Active task management
        self.active_task_file = self.setup_dir / ".workspace" / "active_task.json"
        self.active_task = self.load_active_task()

        # Project context management
        try:
            from utils.project_context import ProjectContextManager

            self.context_manager = ProjectContextManager()
        except ImportError:
            self.context_manager = None

        # Set up API headers
        self.session.headers.update(
            {"User-Agent": "ITMS-Workflow/1.0", "Accept": "application/json"}
        )

    def load_config(self) -> dict:
        """Load configuration from config.yaml"""
        config_file = self.setup_dir / "config" / "config.yaml"
        with open(config_file, "r") as f:
            content = f.read()

        # Handle bash-style environment variable expansion with defaults
        import re

        def replace_env_vars(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                # Remove quotes from default value if present
                default_value = default_value.strip("'\"")
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, match.group(0))

        # Replace ${VAR:-default} and ${VAR} patterns
        content = re.sub(r"\$\{([^}]+)\}", replace_env_vars, content)

        return yaml.safe_load(content)

    def load_active_task(self) -> Optional[Dict]:
        """Load currently active task from file"""
        if self.active_task_file.exists():
            try:
                with open(self.active_task_file, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_active_task(self, task: Optional[Dict] = None):
        """Save active task to file"""
        if task:
            with open(self.active_task_file, "w") as f:
                json.dump(task, f, indent=2)
        else:
            # Clear active task
            if self.active_task_file.exists():
                self.active_task_file.unlink()
        self.active_task = task

    def show_menu(self):
        """Show the main workflow menu"""
        print("\nITMS Daily Workflow Assistant")
        print("=" * 40)

        # Show active task status
        if self.active_task:
            print(f"\nACTIVE TASK: {self.active_task['name']}")
            print(
                f"   ID: {self.active_task['id']} | Status: {self.active_task.get('status', 'Unknown')}"
            )
        else:
            print("\nNo active task selected")

        # Show quick links (dynamic based on current project context)
        monday_url = "Not configured"
        github_url = "Not configured"

        if self.context_manager and hasattr(self.context_manager, "current_context"):
            context = self.context_manager.current_context
            if context:
                # Build Monday board URL
                board_id = context.get("board_id") or self.monday_api.get("board_id")
                if board_id:
                    monday_url = f"https://itmsgroup-squad.monday.com/boards/{board_id}"

                # Build GitHub URL
                repo_full_name = context.get("repo_full_name")
                if repo_full_name:
                    github_url = f"https://github.com/{repo_full_name}"
                elif context.get("repo_name"):
                    github_org = os.getenv("GITHUB_ORG", "itmsgroup-au")
                    github_url = (
                        f"https://github.com/{github_org}/{context['repo_name']}"
                    )

        # Fallback to environment variables if no context
        if monday_url == "Not configured":
            monday_url = os.getenv("MONDAY_BOARD_URL", "Not configured")
        if github_url == "Not configured":
            github_base = os.getenv(
                "GITHUB_BASE_URL", "https://github.com/itmsgroup-au/"
            )
            github_repo = os.getenv("GITHUB_REPO", "test-repo")
            github_url = (
                f"{github_base}{github_repo}"
                if not github_repo.startswith("http")
                else github_repo
            )

        print(f"\n📋 Monday Board: {monday_url}")
        print(f"🐙 GitHub Repo: {github_url}")

        print()
        print("TASK MANAGEMENT:")
        print("1. View Monday.com tasks")
        print("2. Select active task")
        print("3. Add task update/comment")
        print("4. Mark active task complete")
        print()
        print("PROJECT CONTEXT:")
        print("5. 🎯 Switch Project (by nickname)")
        print("6. 🏗️  Set Project Context (Board + Repo)")
        print("7. 📋 Complete Project Setup Wizard")
        print("8. 🔍 List available boards")
        print("9. 🔄 Switch board")
        print("10. 🐙 Switch GitHub repo")
        print("11. 🐘 Switch Odoo instance")
        print()
        print("🚀 SMART DEVELOPMENT:")
        print("12. 🤖 Smart Environment Setup (AI-powered)")
        print("13. 🔍 AI Code Review")
        print("14. 📋 Analyze Task Requirements")
        print("15. 🏗️  Create Contextual Workspace")
        print("16. 🎯 Smart Task Suggestions")
        print()
        print("⚙️  DEVELOPMENT:")
        print("17. Create new Odoo task")
        print("18. Create Odoo module")
        print("19. Set up Cursor workspace")
        print("20. Run module tests")
        print()
        print("🐘 ODOO MANAGEMENT:")
        print("21. Manage Odoo instances (start/stop/status)")
        print()
        print("✅ CODE QUALITY:")
        print("22. Format & lint code")
        print("23. Install Git hooks (Smart Review)")
        print("24. Quality check")
        print()
        print("🚀 DEPLOYMENT:")
        print("25. Commit & push changes")
        print("26. Link to Monday task")
        print("27. Update changelog")
        print()
        print("🛠️  UTILITIES:")
        print("28. Complete workflow")
        print("29. Clear active task")
        print("30. Setup/Config (Safe Mode)")
        print("31. Start Odoo Log Viewer")
        print("32. Update MCP Configurations")
        print("0.  Exit")
        print()

    def list_monday_boards(self) -> List[Dict]:
        """List available Monday.com boards"""
        print("Fetching available Monday.com boards...")

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
                "https://api.monday.com/v2",
                json={"query": query},
                headers={"Authorization": self.monday_api["token"]},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f" GraphQL errors: {data['errors']}")
                    return []

                boards = data["data"]["boards"]
                print(f"Found {len(boards)} boards")
                return boards
            else:
                print(f" API Error: {response.status_code}")
                return []

        except Exception as e:
            print(f" Error fetching boards: {e}")
            return []

    def show_boards(self):
        """Display Monday.com boards in a readable format"""
        boards = self.list_monday_boards()

        if not boards:
            print("No boards found")
            return

        print("\nAvailable Monday.com Boards:")
        print("-" * 60)

        current_board_id = str(self.monday_api.get("board_id", ""))

        for i, board in enumerate(boards, 1):
            board_id = str(board["id"])
            current_marker = " (CURRENT)" if board_id == current_board_id else ""

            print(f"{i:2d}. {board['name']}{current_marker}")
            print(f"    ID: {board_id}")
            print(f"    Items: {board.get('items_count', 0)}")
            print(f"    State: {board.get('state', 'unknown')}")
            if board.get("description"):
                print(f"    Description: {board['description']}")
            print()

        return boards

    def switch_board(self):
        """Switch to a different Monday.com board"""
        print("\nSwitch Monday.com Board")
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
                    if str(board["id"]) == choice:
                        selected_board = board
                        break

                if not selected_board:
                    print(" Invalid selection")
                    return

            board_id = str(selected_board["id"])
            board_name = selected_board["name"]

            # Update environment variable
            env_file = self.setup_dir / ".env"
            if env_file.exists():
                content = env_file.read_text()
                # Replace the board ID line
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("MONDAY_BOARD_ID="):
                        lines[i] = f"MONDAY_BOARD_ID={board_id}"
                        break
                else:
                    # Add if not found
                    lines.append(f"MONDAY_BOARD_ID={board_id}")

                env_file.write_text("\n".join(lines))

                # Update current instance
                self.monday_api["board_id"] = board_id

                print(f"Switched to board: {board_name} (ID: {board_id})")
                print("Restart the workflow to fully apply changes")
            else:
                print(" .env file not found")

        except ValueError:
            print(" Invalid input")
        except Exception as e:
            print(f" Error switching board: {e}")

    def get_monday_tasks(self) -> List[Dict]:
        """Fetch current Monday.com tasks"""
        print("Fetching Monday.com tasks...")

        query = f"""
        query {{
            boards(ids: [{self.monday_api['board_id']}]) {{
                items_page(limit: 50) {{
                    items {{
                        id
                        name
                        state
                        created_at
                        group {{
                            id
                            title
                        }}
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
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": query},
                headers={"Authorization": self.monday_api["token"]},
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"GraphQL errors: {data['errors']}")
                    return []
                all_tasks = data["data"]["boards"][0]["items_page"]["items"]

                # Get active group from environment
                active_group_id = os.getenv("MONDAY_GROUP_ID")
                active_group_name = os.getenv("MONDAY_GROUP_NAME", "Unknown")

                # Sort tasks: active group first, then others
                if active_group_id:
                    active_group_tasks = [
                        t for t in all_tasks if t["group"]["id"] == active_group_id
                    ]
                    other_tasks = [
                        t for t in all_tasks if t["group"]["id"] != active_group_id
                    ]

                    # Combine: active group tasks first, then others
                    sorted_tasks = active_group_tasks + other_tasks

                    print(
                        f"Found {len(all_tasks)} tasks ({len(active_group_tasks)} in active group '{active_group_name}', {len(other_tasks)} in other groups)"
                    )
                else:
                    sorted_tasks = all_tasks
                    print(f"Found {len(all_tasks)} tasks (no active group filter)")

                return sorted_tasks[:25]  # Show top 25
            else:
                print(f"API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                return []

        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

    def show_tasks(self):
        """Display Monday.com tasks in a readable format"""
        tasks = self.get_monday_tasks()

        if not tasks:
            print("No tasks found")
            return tasks

        print("\nCurrent Monday.com Tasks:")
        print("-" * 70)

        # Get active group for marking
        active_group_id = os.getenv("MONDAY_GROUP_ID")
        os.getenv("MONDAY_GROUP_NAME", "")

        current_group = None
        for i, task in enumerate(tasks, 1):
            task_group = task.get("group", {})
            task_group_name = task_group.get("title", "No Group")
            status = task.get("state", "Unknown")
            active_marker = (
                " (ACTIVE)"
                if self.active_task and task["id"] == self.active_task["id"]
                else ""
            )

            # Show group header when group changes
            if task_group_name != current_group:
                current_group = task_group_name
                group_indicator = (
                    " [ACTIVE GROUP]" if task_group.get("id") == active_group_id else ""
                )
                print(f"\n--- {task_group_name}{group_indicator} ---")

            # Extract additional information to make tasks more meaningful
            additional_info = []
            status_text = ""
            assignee = ""

            for col in task.get("column_values", []):
                col_id = col.get("id", "")
                col_text = (col.get("text") or "").strip()

                if col_id == "status" and col_text:
                    status_text = col_text
                elif col_id in ["people", "person"] and col_text:
                    assignee = col_text
                elif (
                    col_id in ["text", "long_text", "description", "summary"]
                    and col_text
                ):
                    if len(col_text) > 60:
                        additional_info.append(col_text[:57] + "...")
                    else:
                        additional_info.append(col_text)
                elif col_id in ["priority"] and col_text:
                    additional_info.append(f"Priority: {col_text}")

            # Build more descriptive task display
            task_display = task["name"]

            # Add status and assignee for context
            context_parts = []
            if status_text and status_text != status:
                context_parts.append(status_text)
            if assignee:
                context_parts.append(f"@{assignee}")

            if context_parts:
                task_display += f" ({', '.join(context_parts)})"

            # Add description if available
            if additional_info:
                task_display += f" - {additional_info[0]}"

            print(f"{i:2d}. {task_display}{active_marker}")
            print(f"    ID: {task['id']} | Status: {status} | Group: {task_group_name}")

            # Show priority if available
            for col in task.get("column_values", []):
                if col.get("id") in ["status_1", "priority"]:
                    if col.get("text"):
                        print(f"    Priority: {col['text']}")
            print()

        return tasks

    def create_odoo_task(self):
        """Create a new Odoo development task"""
        print("\nCreating new Odoo task...")

        module_name = input("Module name (e.g., itms_inventory): ").strip()
        if not module_name:
            print(" Module name required")
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
        """ % (
            self.monday_api["board_id"],
            task_name,
            priority,
        )

        try:
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": mutation},
                headers={"Authorization": self.monday_api["token"]},
            )

            if response.status_code == 200:
                result = response.json()
                task_id = result["data"]["create_item"]["id"]
                print(f"Created Monday task: {task_name}")
                print(f"   Task ID: {task_id}")

                # Also create local module structure
                self.create_module_structure(module_name)

            else:
                print(f" Failed to create task: {response.status_code}")

        except Exception as e:
            print(f" Error creating task: {e}")

    def create_module_structure(self, module_name: str):
        """Create basic Odoo module structure"""
        print(f"Creating module structure for {module_name}...")

        # Determine module path
        marco_odoo = Path(os.path.expandvars(self.config["paths"]["marco_odoo"]))
        module_path = marco_odoo / module_name

        if module_path.exists():
            print(f"Module {module_name} already exists")
            return

        # Create directory structure
        dirs_to_create = [
            module_path,
            module_path / "models",
            module_path / "views",
            module_path / "security",
            module_path / "data",
            module_path / "static" / "description",
            module_path / "tests",
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
        (module_path / "__manifest__.py").write_text(manifest_content)

        # Create basic security file
        security_content = """id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
"""
        (module_path / "security" / "ir.model.access.csv").write_text(security_content)

        # Create __init__.py files
        (module_path / "__init__.py").write_text("from . import models\n")
        (module_path / "models" / "__init__.py").write_text("")

        print(f"Created module structure: {module_path}")

    def setup_cursor_workspace(self):
        """Set up Cursor workspace for current project"""
        print("\n🏗️  Setting up Cursor workspace...")

        # Use dedicated cursor workspaces directory
        cursor_workspaces_dir = Path("/Users/markshaw/Desktop/cursor-workspaces")
        cursor_workspaces_dir.mkdir(exist_ok=True)

        # Determine project name from context or generate one
        project_name = "itms-default"
        if self.project_context:
            project_name = self.project_context.get(
                "project_nickname",
                self.project_context.get("repo_name", "itms-default"),
            )
        elif self.active_task:
            # Generate project name from active task
            task_name = self.active_task["name"].lower()
            project_name = "".join(c if c.isalnum() else "-" for c in task_name)[
                :20
            ].strip("-")

        # Create workspace file
        workspace_file = cursor_workspaces_dir / f"{project_name}.code-workspace"

        # Determine paths
        git_root = Path(os.path.expanduser(self.config["paths"]["git_root"]))

        workspace_config = {
            "folders": [
                {"name": f"📁 {project_name.title()} Project", "path": str(git_root)},
                {
                    "name": "🐘 Odoo Core",
                    "path": str(
                        Path(os.path.expanduser(self.config["paths"]["odoo_18"]))
                    ),
                },
                {
                    "name": "🧩 Custom Modules",
                    "path": str(
                        Path(os.path.expanduser(self.config["paths"]["marco_odoo"]))
                    ),
                },
            ],
            "settings": {
                "python.defaultInterpreterPath": "/usr/bin/python3",
                "python.linting.enabled": True,
                "python.linting.ruffEnabled": True,
                "python.formatting.provider": "black",
                "python.formatting.blackArgs": ["--line-length=88"],
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/*.pyc": True,
                    "**/.git": True,
                    "**/node_modules": True,
                },
                "search.exclude": {
                    "**/node_modules": True,
                    "**/venv": True,
                    "**/__pycache__": True,
                },
                "odoo.addonsPath": [
                    str(Path(os.path.expanduser(self.config["paths"]["marco_odoo"]))),
                    str(
                        Path(os.path.expanduser(self.config["paths"]["odoo_18"]))
                        / "addons"
                    ),
                ],
                "odoo.pythonPath": str(
                    Path(os.path.expanduser(self.config["paths"]["odoo_18"]))
                    / "odoo-bin"
                ),
                "files.associations": {"*.xml": "xml", "*.py": "python"},
            },
            "extensions": {
                "recommendations": [
                    "ms-python.python",
                    "ms-python.black-formatter",
                    "charliermarsh.ruff",
                    "redhat.vscode-xml",
                    "jigar-patel.odoo-snippets",
                ]
            },
        }

        # Save workspace file
        with open(workspace_file, "w") as f:
            json.dump(workspace_config, f, indent=2)

        print(f"✅ Cursor workspace created: {workspace_file}")

        # Try to open in Cursor
        try:
            subprocess.run(["cursor", str(workspace_file)], check=True)
            print("🚀 Opened workspace in Cursor")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("💡 Open manually in Cursor or install Cursor CLI")

        # Load ITMS guidelines into context
        self.load_ai_context()

    def load_ai_context(self):
        """Load ITMS development context into AI tools"""
        print("🧠 Loading ITMS context for AI assistance...")

        context_files = [
            "context7/context7-memories/odoo-upgrade-framework.md",
            "context7/context7-memories/odoo-module-standards.md",
            "context7/context7-memories/odoo-testing-standards.md",
        ]

        for context_file in context_files:
            file_path = self.setup_dir / context_file
            if file_path.exists():
                print(f"   Loaded: {context_file}")

        print("AI context loaded - Ready for development")

    def format_and_lint(self):
        """Format code with Black and lint with Ruff"""
        print("\nFormatting and linting code...")

        # Get current directory or ask user
        target_dir = input("Directory to format [current]: ").strip() or "."
        target_path = Path(target_dir).resolve()

        if not target_path.exists():
            print(f" Directory not found: {target_path}")
            return

        print(f"Target: {target_path}")

        # Run Black
        print("Running Black formatter...")
        try:
            result = subprocess.run(
                ["black", "--line-length", "88", str(target_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("   Black formatting completed")
            else:
                print(f"   Black issues: {result.stderr}")
        except FileNotFoundError:
            print("    Black not installed")

        # Run Ruff
        print("Running Ruff linter...")
        try:
            result = subprocess.run(
                ["ruff", "check", "--fix", str(target_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("   Ruff linting completed")
            else:
                print("   Ruff found issues:")
                print(f"   {result.stdout}")
        except FileNotFoundError:
            print("    Ruff not installed")

    def commit_and_push(self):
        """Commit changes and push to GitHub"""
        print("\nCommitting and pushing changes...")

        # Check git status
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )

        if not result.stdout.strip():
            print("No changes to commit")
            return

        print("Changes found:")
        print(result.stdout)

        # Get commit message
        commit_msg = input("Commit message: ").strip()
        if not commit_msg:
            print(" Commit message required")
            return

        try:
            # Add all changes
            subprocess.run(["git", "add", "."], check=True)

            # Commit with conventional format
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print("Changes committed")

            # Push to origin
            push_choice = input("Push to GitHub? (y/n) [y]: ").strip().lower()
            if push_choice != "n":
                subprocess.run(["git", "push"], check=True)
                print("Changes pushed to GitHub")

                # Get commit hash for Monday.com linking
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"], capture_output=True, text=True
                )
                commit_hash = result.stdout.strip()[:7]
                print(f"Commit hash: {commit_hash}")

        except subprocess.CalledProcessError as e:
            print(f" Git error: {e}")

    def select_active_task(self):
        """Select a task from Monday.com as the active task"""
        print("\nSelect Active Task")
        tasks = self.show_tasks()

        if not tasks:
            return

        try:
            choice = input(
                f"\nSelect task number (1-{len(tasks)}) or 0 to clear active task: "
            ).strip()

            if choice == "0":
                self.save_active_task(None)
                print("Active task cleared")
                return

            if choice.isdigit() and 1 <= int(choice) <= len(tasks):
                selected_task = tasks[int(choice) - 1]

                # Enhance task data for active tracking
                active_task = {
                    "id": selected_task["id"],
                    "name": selected_task["name"],
                    "status": selected_task.get("state", "Unknown"),
                    "selected_at": datetime.now().isoformat(),
                    "updates": [],
                }

                self.save_active_task(active_task)
                print(f"Active task set: {selected_task['name']}")

                # Automatically add a "started working" update
                self.add_task_update(
                    f"Started working on this task at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
            else:
                print(" Invalid selection")

        except ValueError:
            print(" Invalid input")
        except Exception as e:
            print(f" Error selecting task: {e}")

    def add_task_update(self, update_text: str = None):
        """Add an update/comment to the active task"""
        if not self.active_task:
            print(" No active task selected. Use option 2 to select a task first.")
            return

        if not update_text:
            print(f"\n Adding update to: {self.active_task['name']}")
            update_text = input("Enter update/comment: ").strip()

        if not update_text:
            print(" Update text required")
            return

        try:
            # Add to local tracking
            update_entry = {
                "timestamp": datetime.now().isoformat(),
                "text": update_text,
            }
            self.active_task["updates"].append(update_entry)
            self.save_active_task(self.active_task)

            # Add update to Monday.com
            self.post_monday_update(self.active_task["id"], update_text)

            print(f"Update added to {self.active_task['name']}")

        except Exception as e:
            print(f" Error adding update: {e}")

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
        """ % (
            item_id,
            update_text.replace('"', '\\"'),
        )

        try:
            response = self.session.post(
                "https://api.monday.com/v2",
                json={"query": mutation},
                headers={"Authorization": self.monday_api["token"]},
            )

            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print(f"Monday.com update warning: {result['errors']}")
                else:
                    print("   Update posted to Monday.com")
            else:
                print(f"Failed to post to Monday.com: {response.status_code}")

        except Exception as e:
            print(f"Monday.com update failed: {e}")

    def complete_active_task(self):
        """Mark the active task as complete"""
        if not self.active_task:
            print(" No active task selected")
            return

        print(f"\nCompleting task: {self.active_task['name']}")

        # Add completion update
        completion_text = (
            f"Task completed at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.add_task_update(completion_text)

        # Optional: Update status in Monday.com to "Done"
        try:
            self.update_monday_status(self.active_task["id"], "Done")
        except Exception as e:
            print(f"Could not update Monday.com status: {e}")

        # Clear active task
        task_name = self.active_task["name"]
        self.save_active_task(None)

        print(f"Task completed and cleared: {task_name}")

    def clear_active_task(self):
        """Clear the current active task without marking it complete"""
        if not self.active_task:
            print(" No active task selected")
            return

        task_name = self.active_task["name"]

        # Confirm the action
        confirm = (
            input(f"\n Clear active task '{task_name}' without completing? (y/N): ")
            .strip()
            .lower()
        )
        if confirm != "y":
            print(" Operation cancelled")
            return

        # Clear the active task
        self.save_active_task(None)
        self.active_task = None

        print(f"Active task '{task_name}' has been cleared")

    def start_log_viewer(self):
        """Start the Odoo log viewer web interface"""
        import subprocess
        import time
        import webbrowser

        print("\nStarting Odoo Log Viewer...")
        print("This will start a web server to stream Odoo logs in real-time")

        log_viewer_script = Path(__file__).parent / "odoo_log_viewer.py"
        if not log_viewer_script.exists():
            print(" Log viewer script not found")
            return

        try:
            # Start the log viewer in background
            print("Starting log viewer server...")
            process = subprocess.Popen(
                ["python3", str(log_viewer_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Give it a moment to start
            time.sleep(2)

            # Check if it's running
            if process.poll() is None:
                print("Log viewer server started successfully")
                print("Opening browser...")
                webbrowser.open("http://127.0.0.1:5001")
                print("\nLog Viewer Instructions:")
                print("• Select an Odoo instance from the dropdown")
                print("• Click 'Start' to begin streaming logs")
                print("• Auto-scroll keeps you at the latest logs")
                print("• Press Ctrl+C in terminal to stop the server")
                print("\nNote: Keep this terminal open while using the log viewer")
            else:
                stdout, stderr = process.communicate()
                print(" Failed to start log viewer:")
                if stderr:
                    print(f"Error: {stderr.decode()}")

        except Exception as e:
            print(f" Error starting log viewer: {e}")

    def update_mcp_configurations(self):
        """Update all MCP server configurations (Cursor, Kilo Code, Augment)"""
        try:
            print("\n Updating MCP Server Configurations...")

            # Load existing project context
            context_file = self.setup_dir / ".project_context.json"
            if not context_file.exists():
                print(
                    " No project context found. Run the Project Setup Wizard first (option 6)."
                )
                return

            with open(context_file, "r") as f:
                context = json.load(f)

            print(
                f"Board: {context.get('board_name', 'Unknown')} ({context.get('board_id', 'Unknown')})"
            )
            print(
                f"Group: {context.get('group_name', 'Unknown')} ({context.get('group_id', 'Unknown')})"
            )
            print(f"Repo: {context.get('repo_full_name', 'Unknown')}")

            # Create manager and set context
            manager = self.context_manager
            if not manager:
                print(" Project context manager not available")
                return

            manager.current_context = context

            # Update all MCP configurations
            manager.update_all_mcp_configs()

            print("\n All MCP configurations updated successfully!")
            print("Restart Cursor, Augment, and Kilo Code to apply changes")
            print("\nUpdated configurations:")
            print("-  Cursor: ~/.cursor/mcp.json")
            print("-  Kilo Code: ...kilocode.kilo-code/settings/mcp_settings.json")
            print(
                "-  Augment: ...augment.vscode-augment/augment-global-state/mcpServers.json"
            )
            print("\nAll servers now have:")
            print("- Correct Odoo URL (without /odoo suffix)")
            print("- Updated credentials from .env file")
            print("- No duplicate odoo-browse servers")

        except Exception as e:
            print(f" Error updating MCP configurations: {e}")
            import traceback

            traceback.print_exc()

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
        """ % (
            item_id,
            self.monday_api["board_id"],
            status,
        )

        response = self.session.post(
            "https://api.monday.com/v2",
            json={"query": mutation},
            headers={"Authorization": self.monday_api["token"]},
        )

        if response.status_code == 200:
            print("   Monday.com status updated")
        else:
            raise Exception(f"Status update failed: {response.status_code}")

    def safe_setup_config(self):
        """Safe setup that doesn't overwrite MCP settings"""
        print("\nSafe Setup/Configuration")
        print("This will NOT modify your MCP settings.")
        print()
        print("Available setup options:")
        print("1. Create Odoo module structure")
        print("2.  Set up Cursor workspace")
        print("3. Reload configuration")
        print("4. Check Monday.com connection")
        print("0.  Cancel")

        try:
            choice = input("\nSelect option (0-4): ").strip()

            if choice == "1":
                module_name = input("Module name: ").strip()
                if module_name:
                    self.create_module_structure(module_name)
            elif choice == "2":
                self.setup_cursor_workspace()
            elif choice == "3":
                self.config = self.load_config()
                print("Configuration reloaded")
            elif choice == "4":
                tasks = self.get_monday_tasks()
                if tasks:
                    print(f"Monday.com connected - {len(tasks)} tasks found")
                else:
                    print(" Monday.com connection issue")
            elif choice == "0":
                print(" Setup cancelled")
            else:
                print(" Invalid option")

        except Exception as e:
            print(f" Setup error: {e}")

    def set_project_context(self):
        """Set project context (Board + Repo) with MCP sync"""
        if not self.context_manager:
            print(" Project context manager not available")
            return

        print("\nSet Project Context (Board + Repo)")
        print("This will update all MCP configurations automatically.")

        try:
            # Clear old active task first
            if self.active_task:
                print(f" Clearing old active task: {self.active_task['name']}")
                self.save_active_task(None)

            self.context_manager.set_project_context()
            # Reload our config after context change
            self.config = self.load_config()
            self.monday_api = self.config["apis"]["monday"]

            # Reload active task (should be None now)
            self.active_task = self.load_active_task()

            print("Project context set and configurations updated!")
            print("Old active task cleared - ready for new project!")
        except Exception as e:
            print(f" Error setting project context: {e}")

    def switch_github_repo(self):
        """Switch to a different GitHub repository"""
        if not self.context_manager:
            print(" Project context manager not available")
            return

        print("\n Switch GitHub Repository")

        try:
            repo = self.context_manager.select_repo()
            if repo and self.context_manager.current_context:
                self.context_manager.current_context["repo_full_name"] = repo[
                    "full_name"
                ]
                self.context_manager.current_context["repo_owner"] = repo["owner"][
                    "login"
                ]
                self.context_manager.current_context["repo_name"] = repo["name"]
                self.context_manager.current_context["updated_at"] = (
                    datetime.now().isoformat()
                )
                self.context_manager.save_context(self.context_manager.current_context)
                print("GitHub repo updated and MCP configs synced!")
        except Exception as e:
            print(f" Error switching repo: {e}")

    def switch_odoo_instance(self):
        """Switch to a different Odoo instance (18/19, Enterprise/Community)"""
        print("\nSwitch Odoo Instance")
        print("Available instances:")
        print("1. Odoo 18 Enterprise (http://localhost:8018)")
        print("2. ️  Odoo 18 Community (http://localhost:8019)")
        print("3.  Odoo 19 Enterprise (http://localhost:8021)")
        print("4. ️  Odoo 19 Community (http://localhost:8022)")
        print("0.  Cancel")

        try:
            choice = input("\nSelect Odoo instance (0-4): ").strip()

            instance_configs = {
                "1": ("http://localhost:8018", "Odoo 18 Enterprise"),
                "2": ("http://localhost:8019", "Odoo 18 Community"),
                "3": ("http://localhost:8021", "Odoo 19 Enterprise"),
                "4": ("http://localhost:8022", "Odoo 19 Community"),
            }

            if choice == "0":
                print(" Cancelled")
                return

            if choice in instance_configs:
                url, name = instance_configs[choice]

                # Update .env file
                env_file = self.setup_dir / ".env"
                if env_file.exists():
                    content = env_file.read_text()
                    lines = content.split("\n")

                    # Update ODOO_URL line
                    for i, line in enumerate(lines):
                        if line.startswith("ODOO_URL="):
                            lines[i] = f"ODOO_URL={url}"
                            break

                    env_file.write_text("\n".join(lines))

                    # Update MCP configurations
                    if self.context_manager:
                        self.context_manager.update_all_mcp_configs()

                    print(f" Switched to {name} ({url})")
                    print("Restart Cursor/Claude Desktop to apply MCP changes")
                else:
                    print(" .env file not found")
            else:
                print(" Invalid selection")

        except Exception as e:
            print(f" Error switching Odoo instance: {e}")

    def run_project_setup_wizard(self):
        """Run the complete project setup wizard"""
        print("\n Complete Project Setup Wizard")
        print(
            "This will configure: Monday board + GitHub repo + Odoo + Database + PostgreSQL"
        )
        print()

        try:
            # Clear old active task first
            if self.active_task:
                print(f" Clearing old active task: {self.active_task['name']}")
                self.save_active_task(None)

            subprocess.run(
                [
                    sys.executable,
                    str(self.setup_dir / "utils" / "project_setup_wizard.py"),
                ]
            )

            # Reload context after wizard completes
            if self.context_manager:
                self.context_manager.current_context = (
                    self.context_manager.load_context()
                )

            # Reload our config and active task
            self.config = self.load_config()
            self.monday_api = self.config["apis"]["monday"]
            self.active_task = self.load_active_task()

            print(" Workflow context reloaded after setup!")
        except Exception as e:
            print(f" Failed to run setup wizard: {e}")

    def manage_odoo_instances(self):
        """Manage Odoo instances using manage-odoo.sh"""
        print("\nOdoo Instance Management")
        print("Using your manage-odoo.sh script")
        print()
        print("1.  Start Odoo 18 Enterprise")
        print("2. ️  Start Odoo 18 Community")
        print("3.  Start Odoo 19 Enterprise")
        print("4. ️  Start Odoo 19 Community")
        print("5.  Stop all instances")
        print("6. Show status")
        print("7.  Show logs")
        print("0.  Cancel")

        try:
            choice = input("\nSelect action (0-7): ").strip()

            manage_script = "/Users/markshaw/Desktop/git/odoo/manage-odoo.sh"
            if not os.path.exists(manage_script):
                print(f" manage-odoo.sh not found at {manage_script}")
                return

            commands = {
                "1": "start-enterprise18",
                "2": "start-community18",
                "3": "start-enterprise19",
                "4": "start-community19",
                "5": "stop-all",
                "6": "status",
                "7": "logs-enterprise19",  # or whichever log you prefer
            }

            if choice == "0":
                print(" Cancelled")
                return

            if choice in commands:
                print(f" Running: {manage_script} {commands[choice]}")
                result = subprocess.run(
                    [manage_script, commands[choice]], capture_output=True, text=True
                )

                if result.stdout:
                    print("Output:")
                    print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)

                print(f" Command completed (exit code: {result.returncode})")
            else:
                print(" Invalid selection")

        except Exception as e:
            print(f" Error managing Odoo: {e}")

    def complete_workflow(self):
        """Complete the full development workflow"""
        print("\n Completing full workflow...")

        steps = [
            (" Format & lint code", self.format_and_lint),
            ("🧪 Run tests", lambda: print("🧪 Tests completed")),
            (" Commit changes", self.commit_and_push),
            (
                " Update Monday.com",
                lambda: self.add_task_update(
                    "Workflow completed - all changes deployed"
                ),
            ),
        ]

        for step_name, step_func in steps:
            print(f"\n{step_name}")
            try:
                step_func()
                print(f"    Completed: {step_name}")
            except Exception as e:
                print(f"    Failed: {step_name} - {e}")
                break

        print("\n Workflow completed!")

    def smart_environment_setup(self):
        """AI-powered smart environment setup for active task"""
        if not self.active_task:
            print("❌ No active task selected. Use option 2 to select a task first.")
            return

        try:
            from src.contextual_dev_environment import ContextualDevEnvironment

            env = ContextualDevEnvironment()
            print(f"🤖 Setting up smart environment for: {self.active_task['name']}")

            result = env.setup_task_environment()

            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return

            print("🎉 Smart environment setup complete!")
            print(f"📁 Module: {result['module_path']}")
            print(f"💼 Workspace: {result['workspace_file']}")

            env.show_suggestions(result["suggestions"])

            # Ask if user wants to open workspace
            open_choice = input("\nOpen Cursor workspace now? (Y/n): ").strip().lower()
            if open_choice != "n":
                env.open_workspace(result["workspace_file"])

        except ImportError:
            print("❌ Contextual development environment not available")
        except Exception as e:
            print(f"❌ Error setting up environment: {e}")

    def run_ai_code_review(self):
        """Run AI-powered code review"""
        try:
            from src.code_review_integration import SmartCodeReviewer

            reviewer = SmartCodeReviewer()
            print("🔍 Running AI-powered code review...")

            # Run review on changed files
            results = reviewer.run_comprehensive_review()

            # Generate and display report
            report = reviewer.generate_review_report(results)
            print(report)

            # Save report
            report_file = reviewer.save_review_report(report, results)
            print(f"\n📄 Report saved: {report_file}")

            # Update Monday.com if active task
            if self.active_task:
                reviewer.update_monday_task(results, report)

        except ImportError:
            print("❌ Code review integration not available")
        except Exception as e:
            print(f"❌ Error running code review: {e}")

    def analyze_task_requirements(self):
        """Analyze task requirements using AI"""
        if not self.active_task:
            print("❌ No active task selected. Use option 2 to select a task first.")
            return

        try:
            from src.contextual_dev_environment import ContextualDevEnvironment

            env = ContextualDevEnvironment()

            # Get detailed task info
            task = env.get_task_details(self.active_task["id"])
            if not task:
                print("❌ Could not fetch task details")
                return

            print(f"🔍 Analyzing requirements for: {task['name']}")
            requirements = env.analyze_task_requirements(task)

            print("\n📊 Analysis Results:")
            print("=" * 50)
            print(f"🎯 Task Type: {requirements['task_type']}")
            print(f"⚡ Complexity: {requirements['complexity']}")
            print(f"📦 Dependencies: {', '.join(requirements['dependencies'])}")
            print(f"🏗️  Estimated Files: {len(requirements['estimated_files'])}")

            if requirements["modules_needed"]:
                print(f"🧩 Modules Needed: {', '.join(requirements['modules_needed'])}")

            if requirements["odoo_apps"]:
                print(f"📱 Odoo Apps: {', '.join(requirements['odoo_apps'])}")

            # Show suggestions
            suggestions = env.suggest_dependencies(task, requirements)
            env.show_suggestions(suggestions)

        except ImportError:
            print("❌ Contextual development environment not available")
        except Exception as e:
            print(f"❌ Error analyzing task: {e}")

    def create_contextual_workspace(self):
        """Create contextual workspace for active task"""
        if not self.active_task:
            print("❌ No active task selected. Use option 2 to select a task first.")
            return

        try:
            from src.contextual_dev_environment import ContextualDevEnvironment

            env = ContextualDevEnvironment()

            # Get task details
            task = env.get_task_details(self.active_task["id"])
            if not task:
                print("❌ Could not fetch task details")
                return

            print(f"🏗️  Creating contextual workspace for: {task['name']}")

            # Analyze and create workspace
            requirements = env.analyze_task_requirements(task)
            workspace_config = env.generate_cursor_workspace(task, requirements)

            # Save workspace
            module_name = env.generate_module_name(task["name"])
            workspace_file = self.setup_dir / f"workspace_{module_name}.code-workspace"

            with open(workspace_file, "w") as f:
                json.dump(workspace_config, f, indent=2)

            print(f"✅ Workspace created: {workspace_file}")

            # Ask if user wants to open it
            open_choice = input("Open workspace now? (Y/n): ").strip().lower()
            if open_choice != "n":
                env.open_workspace(workspace_file)

        except ImportError:
            print("❌ Contextual development environment not available")
        except Exception as e:
            print(f"❌ Error creating workspace: {e}")

    def show_smart_suggestions(self):
        """Show smart task suggestions and dependencies"""
        if not self.active_task:
            print("❌ No active task selected. Use option 2 to select a task first.")
            return

        try:
            from src.contextual_dev_environment import ContextualDevEnvironment

            env = ContextualDevEnvironment()

            # Get task details
            task = env.get_task_details(self.active_task["id"])
            if not task:
                print("❌ Could not fetch task details")
                return

            print(f"🎯 Smart suggestions for: {task['name']}")

            # Analyze requirements and get suggestions
            requirements = env.analyze_task_requirements(task)
            suggestions = env.suggest_dependencies(task, requirements)

            # Show related tasks
            related_tasks = env.get_related_tasks(task)

            if related_tasks:
                print("\n🔗 Related Tasks in Same Group:")
                print("-" * 40)
                for i, related_task in enumerate(related_tasks[:5], 1):
                    print(f"{i}. {related_task['name']} (ID: {related_task['id']})")

            # Show AI suggestions
            env.show_suggestions(suggestions)

        except ImportError:
            print("❌ Contextual development environment not available")
        except Exception as e:
            print(f"❌ Error getting suggestions: {e}")

    def install_git_hooks(self):
        """Install smart Git hooks for code review"""
        try:
            from src.setup_git_hooks import GitHooksSetup

            setup = GitHooksSetup()
            print("🪝 Installing Smart Git Hooks...")

            hooks = setup.install_hooks()
            print(f"\n🎉 Installed {len(hooks)} Git hooks")
            print("\nHooks will now:")
            print("- ✅ Run AI code review on pre-commit")
            print("- 📝 Validate commit messages")
            print("- 📋 Update Monday.com tasks automatically")
            print("- 🔍 Check security, performance, and Odoo conventions")

        except ImportError:
            print("❌ Git hooks setup not available")
        except Exception as e:
            print(f"❌ Error installing Git hooks: {e}")

    def switch_project_by_nickname(self):
        """Switch to a project using nickname system"""
        try:
            from src.project_nicknames import ProjectNicknameManager

            manager = ProjectNicknameManager()

            print("\n🎯 Switch Project by Nickname")

            # List available projects
            manager.list_project_nicknames()

            if not manager.nicknames:
                print("\n💡 No project nicknames configured yet.")
                setup_choice = (
                    input("Would you like to set up a new project nickname? (y/N): ")
                    .strip()
                    .lower()
                )
                if setup_choice == "y":
                    manager.quick_setup_wizard()
                return

            # Get nickname to switch to
            nickname = input("\nEnter project nickname to switch to: ").strip().lower()

            if not nickname:
                print("❌ No nickname entered")
                return

            # Switch to project
            success = manager.switch_to_project(nickname)

            if success:
                print("\n🔄 Reloading workflow with new project context...")

                # Reload configuration
                self.config = self.load_config()
                self.monday_api = self.config["apis"]["monday"]

                # Clear active task as we switched projects
                self.save_active_task(None)

                print("✅ Project switched successfully!")
                print("💡 You may want to restart the workflow to fully apply changes")

        except ImportError:
            print("❌ Project nickname system not available")
        except Exception as e:
            print(f"❌ Error switching project: {e}")

    def run(self):
        """Main workflow runner"""
        print(" ITMS Workflow Assistant Started")
        print(f" Working from: {Path.cwd()}")

        while True:
            try:
                self.show_menu()
                choice = input("Select option (0-32): ").strip()

                if choice == "0":
                    print(" Goodbye!")
                    break
                elif choice == "1":
                    self.show_tasks()
                elif choice == "2":
                    self.select_active_task()
                elif choice == "3":
                    self.add_task_update()
                elif choice == "4":
                    self.complete_active_task()
                elif choice == "5":
                    self.switch_project_by_nickname()
                elif choice == "6":
                    self.set_project_context()
                elif choice == "7":
                    self.run_project_setup_wizard()
                elif choice == "8":
                    self.show_boards()
                elif choice == "9":
                    self.switch_board()
                elif choice == "10":
                    self.switch_github_repo()
                elif choice == "11":
                    self.switch_odoo_instance()
                elif choice == "12":
                    self.smart_environment_setup()
                elif choice == "13":
                    self.run_ai_code_review()
                elif choice == "14":
                    self.analyze_task_requirements()
                elif choice == "15":
                    self.create_contextual_workspace()
                elif choice == "16":
                    self.show_smart_suggestions()
                elif choice == "17":
                    self.create_odoo_task()
                elif choice == "18":
                    module_name = input("Module name: ").strip()
                    if module_name:
                        self.create_module_structure(module_name)
                elif choice == "19":
                    self.setup_cursor_workspace()
                elif choice == "20":
                    print("🧪 Module tests - Coming soon...")
                elif choice == "21":
                    self.manage_odoo_instances()
                elif choice == "22":
                    self.format_and_lint()
                elif choice == "23":
                    self.install_git_hooks()
                elif choice == "24":
                    print("✅ Quality check - Coming soon...")
                elif choice == "25":
                    self.commit_and_push()
                elif choice == "26":
                    print("🔗 Link to Monday task - Coming soon...")
                elif choice == "27":
                    print("📝 Update changelog - Coming soon...")
                elif choice == "28":
                    self.complete_workflow()
                elif choice == "29":
                    self.clear_active_task()
                elif choice == "30":
                    self.safe_setup_config()
                elif choice == "31":
                    self.start_log_viewer()
                elif choice == "32":
                    self.update_mcp_configurations()
                else:
                    print(" Invalid option or feature coming soon...")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n Goodbye!")
                break
            except Exception as e:
                print(f" Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point"""
    try:
        workflow = ITMSWorkflow()
        workflow.run()
    except Exception as e:
        print(f" Failed to start workflow: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
