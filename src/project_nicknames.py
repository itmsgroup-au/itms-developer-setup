#!/usr/bin/env python3
"""
Project Nickname System - Unified project switching for ITMS
Switch between projects using nicknames that configure everything automatically
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict


class ProjectNicknameManager:
    """Manage project nicknames and unified switching"""

    def __init__(self):
        self.setup_dir = Path(__file__).parent.parent
        self.nicknames_file = self.setup_dir / ".workspace" / "project_nicknames.json"
        self.nicknames = self.load_nicknames()

        # Workspace directory
        self.cursor_workspaces_dir = Path("/Users/markshaw/Desktop/cursor-workspaces")
        self.cursor_workspaces_dir.mkdir(exist_ok=True)

    def load_nicknames(self) -> Dict:
        """Load project nicknames configuration"""
        if self.nicknames_file.exists():
            try:
                with open(self.nicknames_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_nicknames(self):
        """Save project nicknames configuration"""
        with open(self.nicknames_file, "w") as f:
            json.dump(self.nicknames, f, indent=2)

    def add_project_nickname(self, nickname: str, config: Dict) -> bool:
        """Add a new project nickname with full configuration"""
        required_fields = ["monday_board_id", "github_repo", "description"]

        # Validate required fields
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field: {field}")
                return False

        # Create project configuration
        project_config = {
            "nickname": nickname,
            "description": config["description"],
            "monday_board_id": config["monday_board_id"],
            "monday_board_name": config.get("monday_board_name", ""),
            "monday_group_id": config.get("monday_group_id", ""),
            "monday_group_name": config.get("monday_group_name", ""),
            "github_repo": config["github_repo"],
            "github_owner": config.get("github_owner", "itmsgroup-au"),
            "odoo_database": config.get("odoo_database", f"odoo_{nickname}"),
            "odoo_url": config.get("odoo_url", "http://localhost:8018"),
            "workspace_path": str(
                self.cursor_workspaces_dir / f"{nickname}.code-workspace"
            ),
            "created_at": datetime.now().isoformat(),
            "last_used": None,
        }

        self.nicknames[nickname] = project_config
        self.save_nicknames()

        print(f"✅ Added project nickname: '{nickname}'")
        return True

    def remove_project_nickname(self, nickname: str) -> bool:
        """Remove a project nickname"""
        if nickname in self.nicknames:
            del self.nicknames[nickname]
            self.save_nicknames()

            # Remove workspace file if it exists
            workspace_file = self.cursor_workspaces_dir / f"{nickname}.code-workspace"
            if workspace_file.exists():
                workspace_file.unlink()

            print(f"✅ Removed project nickname: '{nickname}'")
            return True
        else:
            print(f"❌ Project nickname '{nickname}' not found")
            return False

    def list_project_nicknames(self):
        """List all available project nicknames"""
        if not self.nicknames:
            print("📋 No project nicknames configured")
            return

        print("📋 Available Project Nicknames:")
        print("=" * 50)

        for nickname, config in self.nicknames.items():
            last_used = config.get("last_used")
            last_used_str = (
                f" (Last used: {last_used[:10]})" if last_used else " (Never used)"
            )

            print(f"🎯 {nickname.upper()}{last_used_str}")
            print(f"   📝 {config['description']}")
            print(
                f"   📋 Monday: {config.get('monday_board_name', 'Unknown')} (ID: {config['monday_board_id']})"
            )
            print(f"   🐙 GitHub: {config['github_owner']}/{config['github_repo']}")
            print(f"   🐘 Database: {config['odoo_database']}")
            print()

    def switch_to_project(self, nickname: str) -> bool:
        """Switch to a project by nickname - configures everything automatically"""
        if nickname not in self.nicknames:
            print(f"❌ Project nickname '{nickname}' not found")
            print("Available projects:")
            for n in self.nicknames.keys():
                print(f"   - {n}")
            return False

        project = self.nicknames[nickname]

        print(f"🚀 Switching to project: {nickname.upper()}")
        print(f"📝 {project['description']}")

        # Update .env file
        self.update_env_file(project)

        # Update project context
        self.update_project_context(project)

        # Create/update Cursor workspace
        self.create_cursor_workspace(nickname, project)

        # Update last used timestamp
        project["last_used"] = datetime.now().isoformat()
        self.save_nicknames()

        print(f"✅ Successfully switched to project: {nickname.upper()}")
        print(f"📋 Monday Board: {project.get('monday_board_name', 'Unknown')}")
        print(f"🐙 GitHub Repo: {project['github_owner']}/{project['github_repo']}")
        print(f"🐘 Odoo Database: {project['odoo_database']}")
        print(f"💼 Workspace: {project['workspace_path']}")

        return True

    def update_env_file(self, project: Dict):
        """Update .env file with project configuration"""
        env_file = self.setup_dir / ".env"

        if not env_file.exists():
            print(f"❌ .env file not found at {env_file}")
            return

        # Read current .env
        with open(env_file, "r") as f:
            lines = f.readlines()

        # Update relevant environment variables
        env_updates = {
            "MONDAY_BOARD_ID": project["monday_board_id"],
            "MONDAY_GROUP_ID": project.get("monday_group_id", ""),
            "MONDAY_GROUP_NAME": project.get("monday_group_name", ""),
            "GITHUB_REPO": project["github_repo"],
            "GITHUB_ORG": project["github_owner"],
            "ODOO_URL": project["odoo_url"],
            "ODOO_DB": project["odoo_database"],
        }

        # Update lines
        for i, line in enumerate(lines):
            for key, value in env_updates.items():
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    break

        # Add missing variables
        existing_keys = set()
        for line in lines:
            if "=" in line and not line.startswith("#"):
                existing_keys.add(line.split("=")[0])

        for key, value in env_updates.items():
            if key not in existing_keys and value:
                lines.append(f"{key}={value}\n")

        # Write updated .env
        with open(env_file, "w") as f:
            f.writelines(lines)

        print("✅ Updated .env file")

    def update_project_context(self, project: Dict):
        """Update project context file"""
        context_file = self.setup_dir / ".workspace" / "project_context.json"

        context = {
            "project_nickname": project["nickname"],
            "board_id": project["monday_board_id"],
            "board_name": project.get("monday_board_name", ""),
            "group_id": project.get("monday_group_id", ""),
            "group_name": project.get("monday_group_name", ""),
            "repo_full_name": f"{project['github_owner']}/{project['github_repo']}",
            "repo_owner": project["github_owner"],
            "repo_name": project["github_repo"],
            "database": project["odoo_database"],
            "odoo_url": project["odoo_url"],
            "updated_at": datetime.now().isoformat(),
        }

        with open(context_file, "w") as f:
            json.dump(context, f, indent=2)

        print("✅ Updated project context")

    def create_cursor_workspace(self, nickname: str, project: Dict):
        """Create/update Cursor workspace for the project"""
        workspace_file = Path(project["workspace_path"])

        # Load configuration for paths
        try:
            from itms_workflow import ITMSWorkflow

            workflow = ITMSWorkflow()
            config = workflow.config
        except:
            print("⚠️  Could not load workflow config, using defaults")
            config = {
                "paths": {
                    "git_root": "~/Desktop/git",
                    "odoo_18": "~/Desktop/git/odoo/odoo18-server",
                    "custom_modules": "~/Desktop/git/custom_modules",
                }
            }

        # Expand paths
        git_root = Path(os.path.expanduser(config["paths"]["git_root"]))
        odoo_path = Path(os.path.expanduser(config["paths"]["odoo_18"]))
        custom_modules = Path(os.path.expanduser(config["paths"]["custom_modules"]))

        workspace_config = {
            "folders": [
                {
                    "name": f"🎯 {nickname.upper()} Project",
                    "path": str(git_root / project["github_repo"]),
                },
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
            "tasks": {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": f"Start Odoo for {nickname}",
                        "type": "shell",
                        "command": str(odoo_path / "odoo-bin"),
                        "args": [
                            "-c",
                            str(odoo_path.parent / "odoo.conf"),
                            "-d",
                            project["odoo_database"],
                            "--dev=reload,qweb,werkzeug,xml",
                        ],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "new",
                        },
                    }
                ],
            },
        }

        with open(workspace_file, "w") as f:
            json.dump(workspace_config, f, indent=2)

        print(f"✅ Created/updated Cursor workspace: {workspace_file}")

    def quick_setup_wizard(self):
        """Interactive wizard to quickly set up a new project nickname"""
        print("🪄 Project Nickname Setup Wizard")
        print("=" * 40)

        # Get nickname
        nickname = (
            input("Project nickname (e.g., 'canbrax', 'bigquery'): ").strip().lower()
        )
        if not nickname:
            print("❌ Nickname is required")
            return False

        if nickname in self.nicknames:
            print(f"❌ Nickname '{nickname}' already exists")
            return False

        # Get description
        description = input("Project description: ").strip()
        if not description:
            print("❌ Description is required")
            return False

        # Get Monday.com board
        print("\n📋 Monday.com Configuration:")
        board_id = input("Monday.com Board ID: ").strip()
        board_name = input("Monday.com Board Name (optional): ").strip()

        # Get GitHub repo
        print("\n🐙 GitHub Configuration:")
        github_repo = input("GitHub repository name: ").strip()
        github_owner = (
            input("GitHub owner (default: itmsgroup-au): ").strip() or "itmsgroup-au"
        )

        # Get Odoo config
        print("\n🐘 Odoo Configuration:")
        odoo_database = (
            input(f"Odoo database name (default: odoo_{nickname}): ").strip()
            or f"odoo_{nickname}"
        )
        odoo_url = (
            input("Odoo URL (default: http://localhost:8018): ").strip()
            or "http://localhost:8018"
        )

        # Create configuration
        config = {
            "description": description,
            "monday_board_id": board_id,
            "monday_board_name": board_name,
            "github_repo": github_repo,
            "github_owner": github_owner,
            "odoo_database": odoo_database,
            "odoo_url": odoo_url,
        }

        # Add the nickname
        success = self.add_project_nickname(nickname, config)

        if success:
            print(f"\n🎉 Project '{nickname}' set up successfully!")
            print(
                f"You can now use: './itms project {nickname}' to switch to this project"
            )

        return success


def main():
    """Main entry point for project nickname management"""
    import argparse

    parser = argparse.ArgumentParser(description="Project Nickname Management")
    parser.add_argument(
        "action",
        choices=["list", "add", "remove", "switch", "setup"],
        help="Action to perform",
    )
    parser.add_argument("nickname", nargs="?", help="Project nickname")
    parser.add_argument("--board-id", help="Monday.com board ID")
    parser.add_argument("--repo", help="GitHub repository name")
    parser.add_argument("--description", help="Project description")

    args = parser.parse_args()

    manager = ProjectNicknameManager()

    if args.action == "list":
        manager.list_project_nicknames()

    elif args.action == "setup":
        manager.quick_setup_wizard()

    elif args.action == "switch":
        if not args.nickname:
            print("❌ Nickname required for switch action")
            return
        manager.switch_to_project(args.nickname)

    elif args.action == "add":
        if not args.nickname:
            print("❌ Nickname required for add action")
            return

        config = {}
        if args.board_id:
            config["monday_board_id"] = args.board_id
        if args.repo:
            config["github_repo"] = args.repo
        if args.description:
            config["description"] = args.description

        if not all(
            k in config for k in ["monday_board_id", "github_repo", "description"]
        ):
            print("❌ Missing required arguments: --board-id, --repo, --description")
            return

        manager.add_project_nickname(args.nickname, config)

    elif args.action == "remove":
        if not args.nickname:
            print("❌ Nickname required for remove action")
            return
        manager.remove_project_nickname(args.nickname)


if __name__ == "__main__":
    main()
