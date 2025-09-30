#!/usr/bin/env python3
"""
Contextual Development Environment - Auto-configure IDE workspace based on Monday tasks
Provides smart suggestions and one-click environment setup for task contexts
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()


class ContextualDevEnvironment:
    """Auto-configure development environment based on active Monday task"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent.parent
        self.config = self.load_config()
        self.session = requests.Session()

        # Active task and context
        self.active_task_file = self.setup_dir / ".workspace" / "active_task.json"
        self.context_file = self.setup_dir / ".workspace" / "project_context.json"
        self.workspace_config_file = (
            self.setup_dir / ".workspace" / "workspace_config.json"
        )

        self.active_task = self.load_active_task()
        self.project_context = self.load_project_context()

        # API configurations
        self.monday_api = self.config["apis"]["monday"]
        self.github_api = self.config["apis"]["github"]

    def load_config(self) -> dict:
        """Load configuration from config.yaml"""
        # Load environment variables from .env file first
        env_file = self.setup_dir / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

        config_file = self.setup_dir / "config" / "config.yaml"
        with open(config_file, "r") as f:
            content = f.read()

        # Handle environment variable expansion with proper nesting support

        def find_and_replace_env_vars(text):
            """Replace environment variables with proper nesting support"""
            result = ""
            i = 0
            while i < len(text):
                if text[i : i + 2] == "${":
                    # Find the matching closing brace
                    brace_count = 1
                    j = i + 2
                    while j < len(text) and brace_count > 0:
                        if text[j] == "{":
                            brace_count += 1
                        elif text[j] == "}":
                            brace_count -= 1
                        j += 1

                    if brace_count == 0:
                        # Extract the variable expression
                        var_expr = text[i + 2 : j - 1]
                        replacement = resolve_env_var(var_expr)
                        result += replacement
                        i = j
                    else:
                        result += text[i]
                        i += 1
                else:
                    result += text[i]
                    i += 1
            return result

        def resolve_env_var(var_expr):
            """Resolve a single environment variable expression"""
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                env_value = os.getenv(var_name)
                if env_value is not None:
                    return env_value
                else:
                    # Recursively process the default value
                    return find_and_replace_env_vars(default_value)
            else:
                return os.getenv(var_expr, f"${{{var_expr}}}")

        # Process environment variables with proper nesting
        content = find_and_replace_env_vars(content)
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

    def load_project_context(self) -> Optional[Dict]:
        """Load project context (board, repo, etc.)"""
        if self.context_file.exists():
            try:
                with open(self.context_file, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Fetch detailed task information from Monday.com"""
        query = f"""
        query {{
            items(ids: [{task_id}]) {{
                id
                name
                state
                group {{
                    id
                    title
                }}
                board {{
                    id
                    name
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

                # Check for API errors
                if "errors" in data:
                    print(f"❌ Monday.com API errors: {data['errors']}")
                    return None

                if data.get("data", {}).get("items"):
                    items = data["data"]["items"]
                    if len(items) > 0:
                        return items[0]
                    else:
                        print(f"❌ No task found with ID {task_id}")
                        return None
                else:
                    print("❌ No task data in API response")
                    return None
            else:
                print(f"   HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error fetching task details: {e}")
            return None

    def analyze_task_requirements(self, task: Dict) -> Dict:
        """Analyze task to determine development requirements"""
        if not task:
            print("❌ No task provided for analysis")
            return {
                "modules_needed": [],
                "test_data_needed": [],
                "dependencies": ["base"],
                "odoo_apps": [],
                "database_requirements": [],
                "documentation_needed": [],
                "task_type": "unknown",
                "complexity": "medium",
                "estimated_files": [],
            }

        requirements = {
            "modules_needed": [],
            "test_data_needed": [],
            "dependencies": [],
            "odoo_apps": [],
            "database_requirements": [],
            "documentation_needed": [],
            "task_type": "unknown",
            "complexity": "medium",
            "estimated_files": [],
        }

        task_name = task.get("name", "").lower()
        task_description = ""

        # Extract description from column values or updates
        for col in task.get("column_values", []):
            # Use column text if available (Monday.com API doesn't provide column titles in this query)
            if col.get("text"):
                task_description += col["text"].lower() + " "

        # Add recent updates to description
        for update in task.get("updates", [])[:3]:  # Last 3 updates
            if update.get("body"):
                task_description += update["body"].lower() + " "

        full_text = task_name + " " + task_description

        # Determine task type
        if any(
            keyword in full_text for keyword in ["report", "reporting", "dashboard"]
        ):
            requirements["task_type"] = "reporting"
            requirements["modules_needed"] = ["report_xlsx", "web"]
            requirements["odoo_apps"] = ["base", "web"]

        elif any(
            keyword in full_text for keyword in ["invoice", "billing", "accounting"]
        ):
            requirements["task_type"] = "accounting"
            requirements["modules_needed"] = ["account", "account_invoicing"]
            requirements["odoo_apps"] = ["account", "sale", "purchase"]

        elif any(
            keyword in full_text for keyword in ["inventory", "stock", "warehouse"]
        ):
            requirements["task_type"] = "inventory"
            requirements["modules_needed"] = ["stock", "stock_account"]
            requirements["odoo_apps"] = ["stock", "purchase", "sale"]

        elif any(
            keyword in full_text for keyword in ["sale", "sales", "crm", "customer"]
        ):
            requirements["task_type"] = "sales"
            requirements["modules_needed"] = ["sale", "crm"]
            requirements["odoo_apps"] = ["sale_management", "crm"]

        elif any(
            keyword in full_text for keyword in ["purchase", "vendor", "supplier"]
        ):
            requirements["task_type"] = "purchase"
            requirements["modules_needed"] = ["purchase"]
            requirements["odoo_apps"] = ["purchase"]

        elif any(keyword in full_text for keyword in ["hr", "employee", "payroll"]):
            requirements["task_type"] = "hr"
            requirements["modules_needed"] = ["hr", "hr_payroll"]
            requirements["odoo_apps"] = ["hr", "hr_payroll"]

        elif any(keyword in full_text for keyword in ["website", "portal", "web"]):
            requirements["task_type"] = "website"
            requirements["modules_needed"] = ["website", "portal"]
            requirements["odoo_apps"] = ["website"]

        # Determine complexity
        if any(
            keyword in full_text for keyword in ["simple", "small", "quick", "minor"]
        ):
            requirements["complexity"] = "low"
        elif any(
            keyword in full_text
            for keyword in ["complex", "major", "large", "integration"]
        ):
            requirements["complexity"] = "high"

        # Estimate files needed
        module_name = self.generate_module_name(task["name"])
        requirements["estimated_files"] = [
            f"{module_name}/__manifest__.py",
            f"{module_name}/models/__init__.py",
            f"{module_name}/views/{module_name}_views.xml",
            f"{module_name}/security/ir.model.access.csv",
        ]

        if requirements["task_type"] == "reporting":
            requirements["estimated_files"].extend(
                [
                    f"{module_name}/report/report_template.xml",
                    f"{module_name}/wizard/report_wizard.py",
                ]
            )

        # Add dependencies based on task type
        if requirements["task_type"] != "unknown":
            requirements["dependencies"] = ["base"] + requirements["modules_needed"]

        return requirements

    def generate_module_name(self, task_name: str) -> str:
        """Generate appropriate module name from task name"""
        # Remove common prefixes and clean up
        clean_name = task_name.lower()
        clean_name = clean_name.replace("[odoo]", "").replace("odoo", "")
        clean_name = clean_name.replace("[", "").replace("]", "")
        clean_name = clean_name.strip()

        # Convert to valid module name
        import re

        clean_name = re.sub(r"[^a-zA-Z0-9\s]", "", clean_name)
        words = clean_name.split()

        # Take first 3 meaningful words
        meaningful_words = [w for w in words if len(w) > 2][:3]

        if not meaningful_words:
            meaningful_words = ["custom", "module"]

        module_name = "itms_" + "_".join(meaningful_words)
        return module_name

    def generate_cursor_workspace(self, task: Dict, requirements: Dict) -> Dict:
        """Generate Cursor workspace configuration for the task"""
        module_name = self.generate_module_name(task["name"])

        workspace_config = {
            "folders": [
                {"name": "Current Task", "path": f"./custom_modules/{module_name}"},
                {"name": "Odoo Core", "path": self.config["paths"]["odoo_18"]},
                {
                    "name": "Custom Modules",
                    "path": self.config["paths"]["custom_modules"],
                },
            ],
            "settings": {
                "python.defaultInterpreterPath": f"{self.config['paths']['odoo_18']}/venv/bin/python",
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
                    self.config["paths"]["custom_modules"],
                    f"{self.config['paths']['odoo_18']}/addons",
                    f"{self.config['paths']['odoo_18']}/odoo/addons",
                ],
                "odoo.pythonPath": f"{self.config['paths']['odoo_18']}/odoo-bin",
                "files.associations": {
                    "*.xml": "xml",
                    "*.py": "python",
                    "*.js": "javascript",
                    "*.css": "css",
                },
            },
            "extensions": {
                "recommendations": [
                    "ms-python.python",
                    "ms-python.black-formatter",
                    "charliermarsh.ruff",
                    "redhat.vscode-xml",
                    "ms-vscode.vscode-json",
                    "jigar-patel.odoo-snippets",
                    "trinhanhngoc.vscode-odoo",
                ]
            },
            "tasks": {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": f"Start Odoo for {module_name}",
                        "type": "shell",
                        "command": f"{self.config['paths']['odoo_18']}/odoo-bin",
                        "args": [
                            "-c",
                            f"{self.config['paths']['odoo_root']}/odoo.conf",
                            "-d",
                            self.project_context.get("database", "odoo"),
                            "-u",
                            module_name,
                            "--dev=reload,qweb,werkzeug,xml",
                        ],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "new",
                            "showReuseMessage": True,
                            "clear": False,
                        },
                        "problemMatcher": [],
                    },
                    {
                        "label": f"Test {module_name}",
                        "type": "shell",
                        "command": f"{self.config['paths']['odoo_18']}/odoo-bin",
                        "args": [
                            "-c",
                            f"{self.config['paths']['odoo_root']}/odoo.conf",
                            "-d",
                            f"{self.project_context.get('database', 'odoo')}_test",
                            "-i",
                            module_name,
                            "--test-enable",
                            "--stop-after-init",
                        ],
                        "group": "test",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "new",
                        },
                    },
                    {
                        "label": "Code Review",
                        "type": "shell",
                        "command": "python3",
                        "args": [
                            f"{self.setup_dir}/code_review_integration.py",
                            "--save-report",
                            "--update-monday",
                        ],
                        "group": "build",
                        "presentation": {"echo": True, "reveal": "always"},
                    },
                ],
            },
        }

        return workspace_config

    def get_related_tasks(self, current_task: Dict) -> List[Dict]:
        """Find related tasks based on keywords and group"""
        if not current_task:
            return []

        # Get tasks from the same group
        group_id = current_task.get("group", {}).get("id")

        query = f"""
        query {{
            boards(ids: [{self.monday_api['board_id']}]) {{
                groups(ids: ["{group_id}"]) {{
                    items_page(limit: 20) {{
                        items {{
                            id
                            name
                            state
                            created_at
                            column_values {{
                                id
                                text
                            }}
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
                if "errors" not in data and data["data"]["boards"]:
                    groups = data["data"]["boards"][0]["groups"]
                    if groups:
                        items = groups[0]["items_page"]["items"]
                        # Filter out current task
                        return [
                            item for item in items if item["id"] != current_task["id"]
                        ]

            return []
        except Exception as e:
            print(f"Error fetching related tasks: {e}")
            return []

    def suggest_dependencies(self, task: Dict, requirements: Dict) -> List[Dict]:
        """Suggest related tasks and dependencies"""
        suggestions = []

        # Get related tasks
        related_tasks = self.get_related_tasks(task)

        # Analyze dependencies based on task type
        task_type = requirements["task_type"]

        if task_type == "reporting":
            suggestions.append(
                {
                    "type": "prerequisite",
                    "description": "Ensure base data models are complete",
                    "tasks": [t for t in related_tasks if "model" in t["name"].lower()],
                }
            )

        elif task_type == "inventory":
            suggestions.append(
                {
                    "type": "prerequisite",
                    "description": "Product catalog should be configured",
                    "tasks": [
                        t for t in related_tasks if "product" in t["name"].lower()
                    ],
                }
            )

        elif task_type == "accounting":
            suggestions.append(
                {
                    "type": "prerequisite",
                    "description": "Chart of accounts configuration needed",
                    "tasks": [
                        t for t in related_tasks if "account" in t["name"].lower()
                    ],
                }
            )

        # General suggestions
        if requirements["complexity"] == "high":
            suggestions.append(
                {
                    "type": "recommendation",
                    "description": "Consider breaking into smaller tasks",
                    "tasks": [],
                }
            )

        return suggestions

    def create_module_structure(self, task: Dict, requirements: Dict) -> Path:
        """Create complete module structure based on task requirements"""
        module_name = self.generate_module_name(task["name"])
        # Properly expand environment variables and user paths
        custom_modules_path = self.config["paths"]["custom_modules"]
        # Replace any ${GIT_ROOT} variables first
        if "${GIT_ROOT}" in custom_modules_path:
            git_root = os.path.expanduser(self.config["paths"]["git_root"])
            custom_modules_path = custom_modules_path.replace("${GIT_ROOT}", git_root)
        # Then expand any remaining environment variables and user paths
        custom_modules = Path(
            os.path.expanduser(os.path.expandvars(custom_modules_path))
        )
        module_path = custom_modules / module_name

        if module_path.exists():
            print(f"📁 Module {module_name} already exists")
            return module_path

        print(f"🏗️  Creating module structure for {module_name}...")

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

        # Add additional directories based on requirements
        if requirements["task_type"] == "reporting":
            dirs_to_create.extend([module_path / "report", module_path / "wizard"])
        elif requirements["task_type"] == "website":
            dirs_to_create.extend(
                [
                    module_path / "controllers",
                    module_path / "static" / "src" / "js",
                    module_path / "static" / "src" / "css",
                ]
            )

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create __manifest__.py
        self.create_manifest_file(module_path, module_name, task, requirements)

        # Create basic security file
        self.create_security_file(module_path, module_name)

        # Create __init__.py files
        self.create_init_files(module_path, requirements)

        # Create README for the task
        self.create_task_readme(module_path, task, requirements)

        print(f"✅ Created module structure: {module_path}")
        return module_path

    def create_manifest_file(
        self, module_path: Path, module_name: str, task: Dict, requirements: Dict
    ):
        """Create __manifest__.py with task-specific configuration"""
        depends = requirements.get("dependencies", ["base"])

        manifest_content = f'''{{
    'name': '{task["name"]}',
    'version': '18.0.1.0.0',
    'category': 'ITMS/{requirements["task_type"].title()}',
    'summary': 'Task: {task["name"]}',
    'description': """{task["name"]}

Monday.com Task ID: {task["id"]}
Task Type: {requirements["task_type"]}
Complexity: {requirements["complexity"]}

Auto-generated by ITMS Contextual Development Environment""",
    'author': 'ITMS Group',
    'website': 'https://itmsgroup.com.au',
    'depends': {depends},
    'data': [
        'security/ir.model.access.csv',
        'views/{module_name}_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': {str(requirements["complexity"] == "high").lower()},
}}
'''
        (module_path / "__manifest__.py").write_text(manifest_content)

    def create_security_file(self, module_path: Path, module_name: str):
        """Create basic security file"""
        security_content = """id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
"""
        (module_path / "security" / "ir.model.access.csv").write_text(security_content)

    def create_init_files(self, module_path: Path, requirements: Dict):
        """Create __init__.py files"""
        (module_path / "__init__.py").write_text("from . import models\n")
        (module_path / "models" / "__init__.py").write_text("")

        if requirements["task_type"] == "reporting":
            (module_path / "__init__.py").write_text(
                "from . import models\nfrom . import wizard\n"
            )
            (module_path / "wizard" / "__init__.py").write_text("")
        elif requirements["task_type"] == "website":
            (module_path / "__init__.py").write_text(
                "from . import models\nfrom . import controllers\n"
            )
            (module_path / "controllers" / "__init__.py").write_text("")

    def create_task_readme(self, module_path: Path, task: Dict, requirements: Dict):
        """Create README with task context"""
        readme_content = f"""# {task['name']}

## Task Information
- **Monday.com ID**: {task['id']}
- **Task Type**: {requirements['task_type']}
- **Complexity**: {requirements['complexity']}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Requirements Analysis
- **Modules Needed**: {', '.join(requirements['modules_needed'])}
- **Odoo Apps**: {', '.join(requirements['odoo_apps'])}
- **Dependencies**: {', '.join(requirements['dependencies'])}

## Estimated Files
{chr(10).join(f'- {file}' for file in requirements['estimated_files'])}

## Development Notes
This module was auto-generated by the ITMS Contextual Development Environment.
The structure and dependencies were determined by analyzing the task requirements.

## Testing
Run tests with:
```bash
python3 odoo-bin -c odoo.conf -d test_db -i {self.generate_module_name(task['name'])} --test-enable --stop-after-init
```

## Monday.com Integration
This module is linked to Monday.com task [{task['id']}]({self.monday_api.get('board_url', '')}).
Updates to this code will automatically update the task.
"""
        (module_path / "README.md").write_text(readme_content)

    def setup_task_environment(self, task_id: str = None) -> Dict:
        """Complete one-click environment setup for a task"""
        if task_id:
            # Load specific task
            task = self.get_task_details(task_id)
            if not task:
                return {"error": f"Task {task_id} not found"}
        else:
            # Use active task
            task = self.active_task
            if not task:
                return {"error": "No active task selected"}

            # Fetch full details
            task = self.get_task_details(task["id"])

        if not task:
            return {"error": "Could not fetch task details"}

        print(f"🎯 Setting up environment for: {task['name']}")

        # Analyze requirements
        requirements = self.analyze_task_requirements(task)

        # Create module structure (task creates module, not workspace)
        module_path = self.create_module_structure(task, requirements)

        # Get or create project workspace (based on Monday Board + GitHub Repo)
        project_workspace = self.get_project_workspace()

        # Get suggestions
        suggestions = self.suggest_dependencies(task, requirements)

        # Save context
        context = {
            "task": task,
            "requirements": requirements,
            "module_path": str(module_path),
            "project_workspace": project_workspace,
            "suggestions": suggestions,
            "created_at": datetime.now().isoformat(),
        }

        with open(self.workspace_config_file, "w") as f:
            json.dump(context, f, indent=2)

        return {
            "success": True,
            "task": task,
            "module_path": module_path,
            "workspace_file": project_workspace,
            "requirements": requirements,
            "suggestions": suggestions,
        }

    def get_project_workspace(self) -> str:
        """Get or create project workspace based on Monday Board + GitHub Repo"""
        # Check if we have project context with nickname
        if self.project_context and self.project_context.get("project_nickname"):
            nickname = self.project_context["project_nickname"]
            workspace_file = (
                f"/Users/markshaw/Desktop/cursor-workspaces/{nickname}.code-workspace"
            )

            if Path(workspace_file).exists():
                print(f"📁 Using existing project workspace: {nickname}")
                return workspace_file

        # Get current board and repo information
        board_id = self.monday_api.get("board_id", "unknown")
        repo_name = (
            self.project_context.get("repo_name", "unknown")
            if self.project_context
            else "unknown"
        )

        # Generate workspace name from board + repo
        workspace_name = f"{repo_name}_{board_id}"
        workspace_file = (
            f"/Users/markshaw/Desktop/cursor-workspaces/{workspace_name}.code-workspace"
        )

        # Create workspace if it doesn't exist
        if not Path(workspace_file).exists():
            print(f"🏗️  Creating project workspace: {workspace_name}")
            self.create_project_workspace(workspace_file, workspace_name)
        else:
            print(f"📁 Using existing project workspace: {workspace_name}")

        return workspace_file

    def create_project_workspace(self, workspace_file: str, workspace_name: str):
        """Create a project workspace based on current Monday Board + GitHub Repo"""
        # Expand paths properly with environment variable handling
        git_root = Path(
            os.path.expanduser(os.path.expandvars(self.config["paths"]["git_root"]))
        )
        odoo_path = Path(
            os.path.expanduser(os.path.expandvars(self.config["paths"]["odoo_18"]))
        )

        # Handle custom_modules path with potential ${GIT_ROOT} variables
        custom_modules_path = self.config["paths"]["custom_modules"]
        if "${GIT_ROOT}" in custom_modules_path:
            custom_modules_path = custom_modules_path.replace(
                "${GIT_ROOT}", str(git_root)
            )
        custom_modules = Path(
            os.path.expanduser(os.path.expandvars(custom_modules_path))
        )

        # Get repo name from project context
        repo_name = (
            self.project_context.get("repo_name", "unknown")
            if self.project_context
            else "custom_modules"
        )
        board_name = self.monday_api.get("board_name", "Unknown Board")

        workspace_config = {
            "folders": [
                {"name": f"📋 {board_name}", "path": str(git_root / repo_name)},
                {"name": "🐘 Odoo Core", "path": str(odoo_path)},
                {"name": "🧩 Custom Modules", "path": str(custom_modules)},
            ],
            "settings": {
                "python.defaultInterpreterPath": str(
                    odoo_path / "venv" / "bin" / "python"
                ),
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
                "odoo.addonsPath": [str(custom_modules), str(odoo_path / "addons")],
                "odoo.pythonPath": str(odoo_path / "odoo-bin"),
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

        with open(workspace_file, "w") as f:
            json.dump(workspace_config, f, indent=2)

        print(f"✅ Created project workspace: {workspace_file}")

    def open_workspace(self, workspace_file: Path):
        """Open Cursor workspace"""
        try:
            subprocess.run(["cursor", str(workspace_file)], check=True)
            print(f"🚀 Opened workspace: {workspace_file}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to open workspace. Open manually: {workspace_file}")
        except FileNotFoundError:
            print("❌ Cursor not found. Install Cursor or open workspace manually")

    def show_suggestions(self, suggestions: List[Dict]):
        """Display smart suggestions"""
        if not suggestions:
            print("💡 No specific suggestions for this task")
            return

        print("💡 Smart Suggestions:")
        print("=" * 50)

        for suggestion in suggestions:
            print(f"📋 {suggestion['type'].title()}: {suggestion['description']}")

            for task in suggestion.get("tasks", []):
                print(f"   - {task['name']} (ID: {task['id']})")

            print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Contextual Development Environment")
    parser.add_argument("--task-id", help="Specific Monday.com task ID")
    parser.add_argument(
        "--setup", action="store_true", help="Run full environment setup"
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze task requirements only"
    )
    parser.add_argument(
        "--open-workspace", action="store_true", help="Open generated workspace"
    )

    args = parser.parse_args()

    env = ContextualDevEnvironment()

    if args.analyze:
        # Analyze current or specific task
        task_id = args.task_id
        if task_id:
            task = env.get_task_details(task_id)
        else:
            task = env.active_task
            if task:
                task = env.get_task_details(task["id"])

        if not task:
            print("❌ No task found to analyze")
            return

        print(f"🔍 Analyzing task: {task['name']}")
        requirements = env.analyze_task_requirements(task)
        suggestions = env.suggest_dependencies(task, requirements)

        print(f"📊 Task Type: {requirements['task_type']}")
        print(f"🎯 Complexity: {requirements['complexity']}")
        print(f"📦 Dependencies: {', '.join(requirements['dependencies'])}")
        print(f"🏗️  Estimated Files: {len(requirements['estimated_files'])}")

        env.show_suggestions(suggestions)

    elif args.setup:
        # Run full environment setup
        result = env.setup_task_environment(args.task_id)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print("🎉 Environment setup complete!")
        print(f"📁 Module: {result['module_path']}")
        print(f"💼 Workspace: {result['workspace_file']}")

        env.show_suggestions(result["suggestions"])

        if args.open_workspace:
            env.open_workspace(result["workspace_file"])

    elif args.open_workspace:
        # Open existing workspace
        if env.workspace_config_file.exists():
            with open(env.workspace_config_file, "r") as f:
                context = json.load(f)

            workspace_file = Path(context["workspace_file"])
            if workspace_file.exists():
                env.open_workspace(workspace_file)
            else:
                print("❌ Workspace file not found")
        else:
            print("❌ No workspace configuration found. Run --setup first")

    else:
        print("🏗️  Contextual Development Environment")
        print("Use --help for available options")

        if env.active_task:
            print(f"📋 Active task: {env.active_task['name']}")
            print("Run with --setup to configure environment for this task")
        else:
            print(
                "💡 No active task selected. Use itms_workflow.py to select a task first"
            )


if __name__ == "__main__":
    main()
